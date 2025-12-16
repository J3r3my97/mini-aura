"""
Main image processing pipeline
Orchestrates: download → bg removal (input) → Claude analysis → prompt generation → DALL-E 3 → bg removal (pixel art) → compositing → upload
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
from utils.ai import analyze_image_with_claude, generate_dalle_prompt, generate_pixel_art_with_dalle

logger = logging.getLogger(__name__)


async def run_pipeline(job_id: str) -> Dict[str, Any]:
    """
    Execute the full image processing pipeline

    Pipeline steps:
    1. Download input image from GCS
    2. Remove background from input photo (rembg)
    3. Analyze image with Claude Haiku (vision)
    4. Generate DALL-E 3 prompt with Claude Haiku
    5. Generate pixel art with OpenAI DALL-E 3
    6. Remove background from generated pixel art (rembg)
    7. Composite images (place mini-me on original)
    8. Add watermark if free tier
    9. Upload result to GCS

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
        logger.info(f"📥 Step 1/9: Downloading input image")
        input_blob_name = f"{job_id}.jpg"  # Assuming uploaded as JPG
        input_path = f"/tmp/{job_id}_input.jpg"

        await download_from_gcs(
            bucket_name=GCS_UPLOAD_BUCKET,
            blob_name=input_blob_name,
            local_path=input_path
        )

        # STEP 2: Remove background from input photo
        logger.info(f"🎨 Step 2/9: Removing background from input photo")
        no_bg_path = await remove_background(input_path)

        # STEP 3: Analyze image with Claude
        logger.info(f"🔍 Step 3/9: Analyzing image with Claude")
        analysis = await analyze_image_with_claude(no_bg_path)

        # STEP 4: Generate DALL-E 3 prompt
        logger.info(f"✍️  Step 4/9: Generating DALL-E 3 prompt")
        prompt = await generate_dalle_prompt(analysis)

        # STEP 5: Generate pixel art with DALL-E 3
        logger.info(f"🎨 Step 5/9: Generating pixel art with DALL-E 3")
        pixel_art_path = f"/tmp/{job_id}_pixel.png"
        await generate_pixel_art_with_dalle(prompt, pixel_art_path)

        # STEP 6: Isolate largest character (removes duplicates + background)
        logger.info(f"✂️  Step 6/9: Isolating largest character (removes duplicates)")
        pixel_art_isolated_path = await isolate_largest_character(pixel_art_path)

        # STEP 7: Composite images
        logger.info(f"🖼️  Step 7/9: Compositing images")
        composite_path = await composite_images(
            background_path=input_path,
            foreground_path=pixel_art_isolated_path,
            position=MINI_ME_POSITION,
            scale=MINI_ME_SCALE
        )

        # STEP 8: Add watermark if free tier
        logger.info(f"💧 Step 8/9: Checking watermark requirement")
        user = await get_user_for_job(job_id)

        if user and user.get("subscription_tier") == "free":
            logger.info("Adding watermark (free tier)")
            composite_path = await add_watermark(composite_path)
        else:
            logger.info("Skipping watermark (paid tier)")

        # STEP 9: Upload result to GCS
        logger.info(f"📤 Step 9/9: Uploading result to GCS")
        result_blob_name = f"{job_id}.png"
        output_url = await upload_to_gcs(
            local_path=composite_path,
            bucket_name=GCS_RESULT_BUCKET,
            blob_name=result_blob_name
        )

        # Calculate processing time
        processing_time = int((time.time() - start_time) * 1000)

        # Prepare metadata
        metadata = {
            "detected_colors": analysis.get("primary_colors", []),
            "generated_prompt": prompt,
            "style": "jrpg-pixel-art",
            "processing_time_ms": processing_time
        }

        logger.info(f"✅ Pipeline complete! Processing time: {processing_time}ms")

        return {
            "output_url": output_url,
            "metadata": metadata
        }

    except Exception as e:
        logger.error(f"❌ Pipeline failed for job {job_id}: {str(e)}")
        raise
