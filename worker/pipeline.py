"""
Main image processing pipeline
Orchestrates: download → GPT-image-1 with reference → isolation → upload
Note: Compositing now happens on frontend
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
from utils.firestore import update_job_status, get_job
from utils.gcs import download_from_gcs, upload_to_gcs
from utils.image_processing import isolate_largest_character
from utils.ai import generate_pixel_art_with_gpt_reference

logger = logging.getLogger(__name__)


async def run_pipeline(job_id: str) -> Dict[str, Any]:
    """
    Execute the full image processing pipeline

    Pipeline steps:
    1. Download input image from GCS
    2. Generate pixel art with GPT-image-1 (uses source as reference)
    3. Isolate largest character (removes duplicates + background)
    4. Upload isolated avatar to GCS

    Note: Compositing now happens on frontend for better UX and cost efficiency

    Args:
        job_id: Job ID (UUID)

    Returns:
        Dictionary with output_url (None) and metadata containing avatar_url
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
        logger.info(f"✂️  Step 3/4: Isolating largest character")
        pixel_art_isolated_path = await isolate_largest_character(pixel_art_path)

        # STEP 4: Upload isolated avatar to GCS
        # Note: Compositing now happens on frontend for better UX and lower costs
        logger.info(f"📤 Step 4/4: Uploading isolated avatar to GCS")
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
            "avatar_url": avatar_url  # Isolated avatar for frontend compositing
        }

        logger.info(f"✅ Pipeline complete! Processing time: {processing_time}ms")
        logger.info(f"📦 Avatar URL: {avatar_url}")

        return {
            "output_url": None,  # No longer generating composite on backend
            "metadata": metadata
        }

    except Exception as e:
        logger.error(f"❌ Pipeline failed for job {job_id}: {str(e)}")
        raise
