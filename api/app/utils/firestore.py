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
            "last_login": datetime.utcnow(),
            # Credit system
            "credits": 0,  # Paid credits
            "free_credits_used": 0,  # Track free credit usage
            "total_generated": 0,  # Total avatars generated
            # Stripe fields
            "stripe_customer_id": None
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


async def create_job(job_id: str, user_id: str, input_image_url: str, has_watermark: bool = False) -> str:
    """
    Create a new job in Firestore

    Args:
        job_id: Job ID (provided by caller)
        user_id: User ID
        input_image_url: GCS URL of uploaded image
        has_watermark: Whether to apply watermark (free tier)

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
            "has_watermark": has_watermark,  # Flag for worker
            "metadata": {}
        }

        db.collection("jobs").document(job_id).set(job_data)
        logger.info(f"Created job: {job_id} for user: {user_id} (watermark: {has_watermark})")

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


# Stripe-related functions

async def update_user_subscription(
    user_id: str,
    tier: str,
    stripe_customer_id: str = None,
    stripe_subscription_id: str = None,
    stripe_subscription_status: str = None,
    trial_end: datetime = None,
    current_period_end: datetime = None
) -> None:
    """
    Update user's subscription information after Stripe webhook

    Args:
        user_id: Firebase user ID
        tier: Subscription tier (free, starter, creator, pro)
        stripe_customer_id: Stripe customer ID (optional)
        stripe_subscription_id: Stripe subscription ID (optional)
        stripe_subscription_status: Stripe subscription status (optional)
        trial_end: Trial end timestamp (optional)
        current_period_end: Current billing period end (optional)
    """
    try:
        from config import USAGE_LIMITS

        user_ref = db.collection("users").document(user_id)

        update_data = {
            "subscription_tier": tier,
            "subscription_status": stripe_subscription_status or "active",
            "usage_limit": USAGE_LIMITS.get(tier, 5)
        }

        if stripe_customer_id:
            update_data["stripe_customer_id"] = stripe_customer_id
        if stripe_subscription_id:
            update_data["stripe_subscription_id"] = stripe_subscription_id
        if stripe_subscription_status:
            update_data["stripe_subscription_status"] = stripe_subscription_status
        if trial_end:
            update_data["trial_end"] = trial_end
        if current_period_end:
            update_data["subscription_current_period_end"] = current_period_end

        user_ref.update(update_data)
        logger.info(f"Updated subscription for user {user_id}: {tier}")

    except Exception as e:
        logger.error(f"Error updating user subscription: {str(e)}")
        raise


async def get_user_by_stripe_customer_id(customer_id: str) -> Optional[Dict[str, Any]]:
    """
    Find user by Stripe customer ID

    Args:
        customer_id: Stripe customer ID

    Returns:
        User document or None if not found
    """
    try:
        users_ref = db.collection("users")
        query = users_ref.where("stripe_customer_id", "==", customer_id).limit(1)
        docs = list(query.stream())

        if docs:
            return docs[0].to_dict()
        return None

    except Exception as e:
        logger.error(f"Error getting user by customer ID: {str(e)}")
        raise


async def cancel_user_subscription(user_id: str) -> None:
    """
    Downgrade user to free tier when subscription cancelled

    Args:
        user_id: Firebase user ID
    """
    try:
        user_ref = db.collection("users").document(user_id)
        user_ref.update({
            "subscription_tier": "free",
            "subscription_status": "cancelled",
            "stripe_subscription_id": None,
            "stripe_subscription_status": "canceled",
            "usage_limit": 5  # Reset to free tier limit
        })
        logger.info(f"Cancelled subscription for user: {user_id}")

    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        raise
