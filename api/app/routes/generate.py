"""
/api/generate endpoint
Upload image and create generation job
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
import logging
import uuid
from slowapi import Limiter
from slowapi.util import get_remote_address

from config import (
    PROJECT_ID,
    GCS_UPLOAD_BUCKET,
    PUBSUB_TOPIC,
    MAX_UPLOAD_SIZE,
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    FREE_CREDITS
)
from app.models.schemas import GenerateResponse, JobStatus
from app.utils.firestore import get_user, create_job, increment_user_usage
from app.utils.gcs import upload_to_gcs
from app.utils.pubsub import publish_job
from app.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file"""

    # Check file size
    if file.size and file.size > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_UPLOAD_SIZE / 1024 / 1024}MB"
        )

    # Check file extension
    if file.filename:
        ext = file.filename.split(".")[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_MIME_TYPES)}"
        )


async def check_and_deduct_credit(user_id: str) -> dict:
    """
    Check if user has available credits and deduct one

    Args:
        user_id: Firebase user ID

    Returns:
        dict with "has_watermark" boolean (True if using free credit)

    Raises:
        HTTPException if no credits available
    """
    user = await get_user(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    credits = user.get("credits", 0)
    free_credits_used = user.get("free_credits_used", 0)

    # Check if user has paid credits
    if credits > 0:
        # Deduct paid credit (no watermark)
        from app.utils.firestore import db
        db.collection("users").document(user_id).update({
            "credits": credits - 1,
            "total_generated": user.get("total_generated", 0) + 1
        })
        logger.info(f"Deducted 1 paid credit from user {user_id}. Remaining: {credits - 1}")
        return {"has_watermark": False}

    # Check if user has free credits available
    elif free_credits_used < FREE_CREDITS:
        # Use free credit (with watermark)
        from app.utils.firestore import db
        db.collection("users").document(user_id).update({
            "free_credits_used": free_credits_used + 1,
            "total_generated": user.get("total_generated", 0) + 1
        })
        logger.info(f"Used 1 free credit for user {user_id}. Used: {free_credits_used + 1}/{FREE_CREDITS}")
        return {"has_watermark": True}

    # No credits available
    else:
        raise HTTPException(
            status_code=402,  # Payment Required
            detail="No credits available. Please purchase credits to generate avatars."
        )


@router.post("/generate", response_model=GenerateResponse, status_code=201)
@limiter.limit("10/minute")
async def generate(
    request: Request,
    file: UploadFile = File(..., description="Image file to process"),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload image and create generation job

    - Validates image file
    - Checks user usage limits
    - Uploads to GCS
    - Creates job in Firestore
    - Publishes to Pub/Sub for processing
    - Returns job ID for status polling

    Requires: Firebase authentication token in Authorization header
    """
    try:
        # Extract user_id from authenticated user
        user_id = current_user["user_id"]

        logger.info(f"Received generate request from user: {user_id}")

        # Validate file
        validate_image_file(file)

        # Check and deduct credit (also determines if watermark needed)
        credit_result = await check_and_deduct_credit(user_id)

        # Generate job ID
        job_id = str(uuid.uuid4())
        logger.info(f"Generated job ID: {job_id}")

        # Upload to GCS
        blob_name = f"{job_id}.jpg"
        input_url = await upload_to_gcs(
            file=file.file,
            bucket_name=GCS_UPLOAD_BUCKET,
            blob_name=blob_name,
            content_type=file.content_type or "image/jpeg"
        )

        # Create job in Firestore with watermark flag
        await create_job(job_id, user_id, input_url, credit_result["has_watermark"])

        # Publish to Pub/Sub
        message_id = await publish_job(PROJECT_ID, PUBSUB_TOPIC, job_id)
        logger.info(f"Published job {job_id} to Pub/Sub: {message_id}")

        return GenerateResponse(
            job_id=job_id,
            status=JobStatus.QUEUED,
            message="Job created successfully. Use job_id to check status."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
