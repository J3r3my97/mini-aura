"""
/api/jobs endpoints
Get job status and list user jobs
"""
from fastapi import APIRouter, HTTPException, Query, Depends
import logging

from config import GCS_RESULT_BUCKET
from app.models.schemas import JobResponse, JobListResponse, JobStatus, JobMetadata
from app.utils.firestore import get_job, get_user_jobs
from app.utils.gcs import get_signed_url
from app.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get job status by ID

    Returns:
    - Job metadata
    - Current status (queued, processing, completed, failed)
    - Signed URL for result image (if completed)

    Requires: Firebase authentication token in Authorization header
    """
    try:
        # Extract user_id from authenticated user
        user_id = current_user["user_id"]

        logger.info(f"Getting job status for: {job_id}")

        # Get job from Firestore
        job = await get_job(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Verify user owns this job
        if job.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # If completed, generate signed URL for result
        output_url = None
        if job.get("status") == "completed" and job.get("output_image_url"):
            # Extract blob name from gs:// URL
            gs_url = job["output_image_url"]
            blob_name = gs_url.replace(f"gs://{GCS_RESULT_BUCKET}/", "")

            # Generate signed URL
            output_url = await get_signed_url(GCS_RESULT_BUCKET, blob_name)

        # Parse metadata
        metadata = None
        if job.get("metadata"):
            metadata = JobMetadata(**job["metadata"])

        return JobResponse(
            job_id=job["job_id"],
            user_id=job["user_id"],
            status=JobStatus(job["status"]),
            created_at=job["created_at"],
            completed_at=job.get("completed_at"),
            input_image_url=job.get("input_image_url"),
            output_image_url=output_url,  # Signed URL
            error_message=job.get("error_message"),
            metadata=metadata
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/jobs", response_model=JobListResponse)
async def list_user_jobs(
    limit: int = Query(20, ge=1, le=100, description="Number of jobs to return"),
    offset: int = Query(0, ge=0, description="Number of jobs to skip"),
    current_user: dict = Depends(get_current_user)
):
    """
    List user's generation jobs with pagination

    Returns list of jobs ordered by created_at (newest first)

    Requires: Firebase authentication token in Authorization header
    """
    try:
        # Extract user_id from authenticated user
        user_id = current_user["user_id"]

        logger.info(f"Listing jobs for user: {user_id} (limit={limit}, offset={offset})")

        # Get jobs from Firestore
        jobs, total = await get_user_jobs(user_id, limit=limit, offset=offset)

        # Convert to response models
        job_responses = []
        for job in jobs:
            # Parse metadata
            metadata = None
            if job.get("metadata"):
                try:
                    metadata = JobMetadata(**job["metadata"])
                except:
                    pass

            # Generate signed URL if completed
            output_url = None
            if job.get("status") == "completed" and job.get("output_image_url"):
                gs_url = job["output_image_url"]
                blob_name = gs_url.replace(f"gs://{GCS_RESULT_BUCKET}/", "")
                try:
                    output_url = await get_signed_url(GCS_RESULT_BUCKET, blob_name)
                except:
                    pass

            job_responses.append(JobResponse(
                job_id=job["job_id"],
                user_id=job["user_id"],
                status=JobStatus(job["status"]),
                created_at=job["created_at"],
                completed_at=job.get("completed_at"),
                input_image_url=job.get("input_image_url"),
                output_image_url=output_url,
                error_message=job.get("error_message"),
                metadata=metadata
            ))

        return JobListResponse(
            jobs=job_responses,
            total=total,
            limit=limit,
            offset=offset
        )

    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
