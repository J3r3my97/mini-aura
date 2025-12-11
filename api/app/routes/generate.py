"""
/api/generate endpoint
Upload image and create generation job
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
import uuid

from config import (
    PROJECT_ID,
    GCS_UPLOAD_BUCKET,
    PUBSUB_TOPIC,
    MAX_UPLOAD_SIZE,
    ALLOWED_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    USAGE_LIMITS
)
from app.models.schemas import GenerateResponse, JobStatus
from app.utils.firestore import get_user, create_job, increment_user_usage
from app.utils.gcs import upload_to_gcs
from app.utils.pubsub import publish_job

logger = logging.getLogger(__name__)

router = APIRouter()


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


async def check_user_usage(user_id: str) -> None:
    """Check if user has available usage"""
    user = await get_user(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tier = user.get("subscription_tier", "free")
    usage_count = user.get("usage_count", 0)
    usage_limit = USAGE_LIMITS.get(tier, 5)

    # Check if unlimited (pro tier)
    if usage_limit == -1:
        return

    # Check if user has exceeded limit
    if usage_count >= usage_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Usage limit exceeded. You've used {usage_count}/{usage_limit} images. Please upgrade your plan."
        )


@router.post("/generate", response_model=GenerateResponse, status_code=201)
async def generate(
    file: UploadFile = File(..., description="Image file to process"),
    # TODO: Add user_id from Firebase auth token
    user_id: str = "test-user"  # Temporary - will come from auth
):
    """
    Upload image and create generation job

    - Validates image file
    - Checks user usage limits
    - Uploads to GCS
    - Creates job in Firestore
    - Publishes to Pub/Sub for processing
    - Returns job ID for status polling
    """
    try:
        logger.info(f"Received generate request from user: {user_id}")

        # Validate file
        validate_image_file(file)

        # Check usage limits
        await check_user_usage(user_id)

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

        # Create job in Firestore
        await create_job(job_id, user_id, input_url)

        # Increment user usage
        await increment_user_usage(user_id)

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
