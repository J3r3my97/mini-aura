"""
Main image processing pipeline
Orchestrates: download → GPT-image-1 with reference → isolation → compositing → upload
"""
import time
import uuid
import logging
from typing import Dict, Any

from config import (
    GCS_UPLOAD_BUCKET,
    GCS_RESULT_BUCKET,
    MINI_ME_SCALE,
    MINI_ME_POSITION
)
from utils.firestore import update_job_status, get_job, get_user_for_job
from utils.gcs import download_from_gcs, upload_to_gcs
from utils.image_processing import remove_background, isolate_largest_character, composite_images, add_watermark
from utils.ai import generate_pixel_art_with_gpt_reference

logger = logging.getLogger(__name__)


async def run_pipeline(job_id: str) -> Dict[str, Any]:
    """
    Execute the full image processing pipeline

    Pipeline steps:
    1. Download input image from GCS
    2. Generate pixel art with GPT-image-1 (uses source as reference)
    3. Isolate largest character (removes duplicates + background)
    4. Composite images (place mini-me on original)
    5. Add watermark if free tier
    6. Upload result to GCS

    Args:
        job_id: Job ID (UUID)

    Returns:
        Dictionary with output_url and metadata
    """
    start_time = time.time()
    logger.info(f"🚀 Starting pipeline for job {job_id}")

    try:
        # Get job details
        job = await get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found in Firestore")

        # STEP 1: Download input image from GCS
        logger.info(f"📥 Step 1/6: Downloading input image")
        input_blob_name = f"{job_id}.jpg"  # Assuming uploaded as JPG
        input_path = f"/tmp/{job_id}_input.jpg"

        await download_from_gcs(
            bucket_name=GCS_UPLOAD_BUCKET,
            blob_name=input_blob_name,
            local_path=input_path
        )

        # STEP 2: Generate pixel art with GPT-image-1 (uses source as reference)
        # GPT-image-1 sees the actual image, so no need for Claude analysis/prompt generation
        logger.info(f"🎨 Step 2/6: Generating pixel art with GPT-image-1")
        pixel_art_path = f"/tmp/{job_id}_pixel.png"
        await generate_pixel_art_with_gpt_reference(input_path, pixel_art_path)

        # STEP 3: Isolate largest character (removes duplicates + background)
        logger.info(f"✂️  Step 3/6: Isolating largest character")
        pixel_art_isolated_path = await isolate_largest_character(pixel_art_path)

        # STEP 4: Composite images
        logger.info(f"🖼️  Step 4/6: Compositing images")
        composite_path = await composite_images(
            background_path=input_path,
            foreground_path=pixel_art_isolated_path,
            position=MINI_ME_POSITION,
            scale=MINI_ME_SCALE
        )

        # STEP 5: Add watermark if free tier
        logger.info(f"💧 Step 5/6: Checking watermark requirement")
        user = await get_user_for_job(job_id)

        if user and user.get("subscription_tier") == "free":
            logger.info("Adding watermark (free tier)")
            composite_path = await add_watermark(composite_path)
        else:
            logger.info("Skipping watermark (paid tier)")

        # STEP 6: Upload results to GCS
        logger.info(f"📤 Step 6/6: Uploading results to GCS")

        # Upload composite image
        result_blob_name = f"{job_id}.png"
        output_url = await upload_to_gcs(
            local_path=composite_path,
            bucket_name=GCS_RESULT_BUCKET,
            blob_name=result_blob_name
        )

        # Upload isolated avatar (for customization)
        avatar_blob_name = f"{job_id}_avatar.png"
        avatar_url = await upload_to_gcs(
            local_path=pixel_art_isolated_path,
            bucket_name=GCS_RESULT_BUCKET,
            blob_name=avatar_blob_name
        )

        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)

        # Prepare metadata
        metadata = {
            "style": "everskies-pixel-art",
            "model": "gpt-image-1",
            "processing_time_ms": processing_time,
            "avatar_url": avatar_url  # Isolated avatar for customization
        }

        logger.info(f"✅ Pipeline complete! Processing time: {processing_time}ms")

        return {
            "output_url": output_url,
            "metadata": metadata
        }

    except Exception as e:
        logger.error(f"❌ Pipeline failed for job {job_id}: {str(e)}")
        raise
