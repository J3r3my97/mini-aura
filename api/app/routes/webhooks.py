"""
Webhook routes - Stripe webhook event handlers
"""
from fastapi import APIRouter, Request, HTTPException, Header
import stripe
import logging
from datetime import datetime

from config import STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
from app.utils.firestore import (
    get_user_by_stripe_customer_id,
    update_user_subscription,
    cancel_user_subscription
)

logger = logging.getLogger(__name__)

stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None)
):
    """
    Handle Stripe webhook events

    Critical events:
    - checkout.session.completed: Payment succeeded (upgrade user)
    - customer.subscription.created: New subscription created
    - customer.subscription.updated: Subscription changed (trial ended, renewed)
    - customer.subscription.deleted: Subscription cancelled (downgrade user)
    - invoice.payment_failed: Payment failed (notify user)
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

        # Handle checkout.session.completed
        if event_type == "checkout.session.completed":
            await handle_checkout_completed(data)

        # Handle subscription created
        elif event_type == "customer.subscription.created":
            await handle_subscription_created(data)

        # Handle subscription updated (e.g., trial ended, renewed)
        elif event_type == "customer.subscription.updated":
            await handle_subscription_updated(data)

        # Handle subscription deleted (cancelled or expired)
        elif event_type == "customer.subscription.deleted":
            await handle_subscription_deleted(data)

        # Handle payment failure
        elif event_type == "invoice.payment_failed":
            await handle_payment_failed(data)

        # Handle trial ending soon
        elif event_type == "customer.subscription.trial_will_end":
            await handle_trial_ending(data)

        return {"status": "success"}

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def handle_checkout_completed(session):
    """Handle successful checkout"""
    try:
        customer_id = session.get("customer")
        payment_type = session["metadata"].get("payment_type")
        firebase_uid = session["metadata"].get("firebase_uid")

        logger.info(f"Checkout completed: {session['id']}, type: {payment_type}")

        # For one-time payments, no subscription upgrade needed
        # User just gets redirected to generation flow
        if payment_type == "onetime":
            logger.info(f"One-time payment completed for user {firebase_uid}")
            # No database update needed - payment allows immediate generation
            return

        # For subscriptions, upgrade will be handled by subscription.created event
        logger.info(f"Subscription checkout completed for customer {customer_id}")

    except Exception as e:
        logger.error(f"Error handling checkout completed: {str(e)}")
        raise


async def handle_subscription_created(subscription):
    """Handle new subscription creation"""
    try:
        customer_id = subscription["customer"]
        subscription_id = subscription["id"]
        status = subscription["status"]  # trialing or active
        firebase_uid = subscription["metadata"].get("firebase_uid")

        # Get trial end timestamp
        trial_end = None
        if subscription.get("trial_end"):
            trial_end = datetime.fromtimestamp(subscription["trial_end"])

        # Get current period end
        current_period_end = datetime.fromtimestamp(subscription["current_period_end"])

        # Find user by customer ID
        if firebase_uid:
            user_id = firebase_uid
        else:
            user = await get_user_by_stripe_customer_id(customer_id)
            if not user:
                logger.error(f"User not found for customer {customer_id}")
                return
            user_id = user["user_id"]

        # Update user to Pro tier
        await update_user_subscription(
            user_id=user_id,
            tier="pro",
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_id,
            stripe_subscription_status=status,
            trial_end=trial_end,
            current_period_end=current_period_end
        )

        logger.info(f"Upgraded user {user_id} to Pro (status: {status})")

    except Exception as e:
        logger.error(f"Error handling subscription created: {str(e)}")
        raise


async def handle_subscription_updated(subscription):
    """Handle subscription updates (renewals, trial ended, etc.)"""
    try:
        customer_id = subscription["customer"]
        subscription_id = subscription["id"]
        status = subscription["status"]

        # Find user
        user = await get_user_by_stripe_customer_id(customer_id)
        if not user:
            logger.error(f"User not found for customer {customer_id}")
            return

        user_id = user["user_id"]

        # Update subscription status
        current_period_end = datetime.fromtimestamp(subscription["current_period_end"])

        # Determine tier based on status
        tier = "pro" if status in ["active", "trialing"] else "free"

        await update_user_subscription(
            user_id=user_id,
            tier=tier,
            stripe_subscription_id=subscription_id,
            stripe_subscription_status=status,
            current_period_end=current_period_end
        )

        logger.info(f"Updated subscription for user {user_id}: {status}")

    except Exception as e:
        logger.error(f"Error handling subscription updated: {str(e)}")
        raise


async def handle_subscription_deleted(subscription):
    """Handle subscription cancellation"""
    try:
        customer_id = subscription["customer"]

        # Find user
        user = await get_user_by_stripe_customer_id(customer_id)
        if not user:
            logger.error(f"User not found for customer {customer_id}")
            return

        user_id = user["user_id"]

        # Downgrade to free tier
        await cancel_user_subscription(user_id)

        logger.info(f"Downgraded user {user_id} to free tier (subscription cancelled)")

    except Exception as e:
        logger.error(f"Error handling subscription deleted: {str(e)}")
        raise


async def handle_payment_failed(invoice):
    """Handle failed payment"""
    try:
        customer_id = invoice["customer"]

        # Find user
        user = await get_user_by_stripe_customer_id(customer_id)
        if not user:
            logger.error(f"User not found for customer {customer_id}")
            return

        user_id = user["user_id"]

        # Log payment failure (could send email notification here)
        logger.warning(f"Payment failed for user {user_id}")

        # Stripe will retry automatically
        # After max retries, subscription will be cancelled automatically

    except Exception as e:
        logger.error(f"Error handling payment failed: {str(e)}")
        raise


async def handle_trial_ending(subscription):
    """Handle trial ending notification (3 days before)"""
    try:
        customer_id = subscription["customer"]

        # Find user
        user = await get_user_by_stripe_customer_id(customer_id)
        if not user:
            logger.error(f"User not found for customer {customer_id}")
            return

        user_id = user["user_id"]

        # Log trial ending (could send email notification here)
        logger.info(f"Trial ending soon for user {user_id}")

        # TODO: Send email notification to user

    except Exception as e:
        logger.error(f"Error handling trial ending: {str(e)}")
        raise
