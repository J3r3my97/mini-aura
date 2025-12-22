"""
Webhook routes - Stripe webhook event handlers
"""
from fastapi import APIRouter, Request, HTTPException, Header
import stripe
import logging
from google.cloud import firestore

from config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, CREDIT_PACKAGES
from app.utils.firestore import db

logger = logging.getLogger(__name__)

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None)
):
    """
    Handle Stripe webhook events for credit purchases

    Critical events:
    - checkout.session.completed: Payment succeeded (add credits to user)
    """
    try:
        payload = await request.body()

        # Verify webhook signature
        try:
            event = stripe.Webhook.construct_event(
                payload, stripe_signature, STRIPE_WEBHOOK_SECRET
            )
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Webhook signature verification failed: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid signature")

        event_type = event["type"]
        data = event["data"]["object"]

        logger.info(f"Processing webhook event: {event_type}")

        # Handle checkout.session.completed (credit purchase)
        if event_type == "checkout.session.completed":
            await handle_checkout_completed(data)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def handle_checkout_completed(session):
    """
    Handle successful credit purchase

    When a user completes payment, add the purchased credits to their account
    """
    try:
        firebase_uid = session["metadata"].get("firebase_uid")
        package = session["metadata"].get("package")
        credits = int(session["metadata"].get("credits", 0))

        logger.info(f"Checkout completed: session={session['id']}, user={firebase_uid}, package={package}, credits={credits}")

        if not firebase_uid:
            logger.error(f"No firebase_uid in session metadata: {session['id']}")
            return

        if not package or package not in CREDIT_PACKAGES:
            logger.error(f"Invalid package in session metadata: {package}")
            return

        # Add credits to user account
        db.collection("users").document(firebase_uid).update({
            "credits": firestore.Increment(credits)
        })

        logger.info(f"Added {credits} credits to user {firebase_uid} (package: {package})")

    except Exception as e:
        logger.error(f"Error handling checkout completed: {str(e)}", exc_info=True)
        raise
