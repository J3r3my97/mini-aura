"""
Firestore database helper functions for API
"""
from google.cloud import firestore
from datetime import datetime
from typing import Optional, Dict, Any, List
import logging
import uuid

logger = logging.getLogger(__name__)

# Initialize Firestore client
db = firestore.Client()


async def create_user(user_id: str, email: str) -> Dict[str, Any]:
    """
    Create a new user in Firestore

    Args:
        user_id: Firebase user ID
        email: User email

    Returns:
        User document
    """
    try:
        user_data = {
            "user_id": user_id,
            "email": email,
            "created_at": datetime.utcnow(),
            "subscription_tier": "free",
            "subscription_status": "active",
            "usage_count": 0,
            "usage_limit": 5,  # Free tier
            "last_login": datetime.utcnow()
        }

        db.collection("users").document(user_id).set(user_data)
        logger.info(f"Created user: {user_id}")

        return user_data

    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise


async def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user from Firestore"""
    try:
        doc_ref = db.collection("users").document(user_id)
        doc = doc_ref.get()

        if doc.exists:
            return doc.to_dict()
        return None

    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        raise


async def get_or_create_user(user_id: str, email: str) -> Dict[str, Any]:
    """Get user or create if doesn't exist"""
    user = await get_user(user_id)

    if not user:
        user = await create_user(user_id, email)

    # Update last login
    db.collection("users").document(user_id).update({
        "last_login": datetime.utcnow()
    })

    return user


async def increment_user_usage(user_id: str) -> None:
    """Increment user's usage count"""
    try:
        user_ref = db.collection("users").document(user_id)
        user_ref.update({
            "usage_count": firestore.Increment(1)
        })
        logger.info(f"Incremented usage for user: {user_id}")

    except Exception as e:
        logger.error(f"Error incrementing usage: {str(e)}")
        raise


async def create_job(job_id: str, user_id: str, input_image_url: str) -> str:
    """
    Create a new job in Firestore

    Args:
        job_id: Job ID (provided by caller)
        user_id: User ID
        input_image_url: GCS URL of uploaded image

    Returns:
        Job ID
    """
    try:

        job_data = {
            "job_id": job_id,
            "user_id": user_id,
            "status": "queued",
            "created_at": datetime.utcnow(),
            "input_image_url": input_image_url,
            "output_image_url": None,
            "error_message": None,
            "metadata": {}
        }

        db.collection("jobs").document(job_id).set(job_data)
        logger.info(f"Created job: {job_id} for user: {user_id}")

        return job_id

    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise


async def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """Get job from Firestore"""
    try:
        doc_ref = db.collection("jobs").document(job_id)
        doc = doc_ref.get()

        if doc.exists:
            return doc.to_dict()
        return None

    except Exception as e:
        logger.error(f"Error getting job {job_id}: {str(e)}")
        raise


async def get_user_jobs(
    user_id: str,
    limit: int = 20,
    offset: int = 0
) -> tuple[List[Dict[str, Any]], int]:
    """
    Get user's jobs with pagination

    Args:
        user_id: User ID
        limit: Number of jobs to return
        offset: Number of jobs to skip

    Returns:
        Tuple of (jobs list, total count)
    """
    try:
        # Query jobs for user, ordered by created_at descending
        jobs_ref = db.collection("jobs") \
            .where("user_id", "==", user_id) \
            .order_by("created_at", direction=firestore.Query.DESCENDING)

        # Get total count
        total = len(list(jobs_ref.stream()))

        # Get paginated results
        jobs_query = jobs_ref.limit(limit).offset(offset)
        jobs = [doc.to_dict() for doc in jobs_query.stream()]

        return jobs, total

    except Exception as e:
        logger.error(f"Error getting user jobs: {str(e)}")
        raise
