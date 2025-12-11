"""
Firestore database helper functions
"""
from google.cloud import firestore
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Initialize Firestore client
db = firestore.Client()


async def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Get a job document from Firestore"""
    try:
        doc_ref = db.collection("jobs").document(job_id)
        doc = doc_ref.get()

        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {str(e)}")
        raise


async def update_job_status(
    job_id: str,
    status: str,
    output_url: Optional[str] = None,
    error_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Update job status in Firestore

    Args:
        job_id: Job ID
        status: Job status (queued, processing, completed, failed)
        output_url: GCS URL of result image (for completed jobs)
        error_message: Error message (for failed jobs)
        metadata: Additional metadata (colors, prompt, etc.)
    """
    try:
        doc_ref = db.collection("jobs").document(job_id)

        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }

        if status == "completed":
            update_data["completed_at"] = datetime.utcnow()
            if output_url:
                update_data["output_image_url"] = output_url
            if metadata:
                update_data["metadata"] = metadata

        elif status == "failed":
            update_data["completed_at"] = datetime.utcnow()
            if error_message:
                update_data["error_message"] = error_message

        doc_ref.update(update_data)
        logger.info(f"Updated job {job_id} to status: {status}")

    except Exception as e:
        logger.error(f"Error updating job {job_id}: {str(e)}")
        raise


async def get_user_for_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Get user associated with a job"""
    try:
        job = await get_job(job_id)
        if not job:
            return None

        user_id = job.get("user_id")
        if not user_id:
            return None

        user_ref = db.collection("users").document(user_id)
        user_doc = user_ref.get()

        if user_doc.exists:
            return user_doc.to_dict()
        return None

    except Exception as e:
        logger.error(f"Error getting user for job {job_id}: {str(e)}")
        raise
