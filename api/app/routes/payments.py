"""
Payment routes - Stripe checkout and customer portal
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
import stripe
import logging
from typing import Literal

from config import (
    STRIPE_SECRET_KEY,
    STRIPE_PRO_PRICE_ID,
    STRIPE_ONETIME_PRICE_ID,
    FRONTEND_URL,
    PAYMENT_SUCCESS_URL,
    PAYMENT_CANCEL_URL,
    CUSTOMER_PORTAL_RETURN_URL
)
from app.models.schemas import CheckoutSessionRequest, CheckoutSessionResponse
from app.utils.firestore import get_user
from app.auth import get_current_user

logger = logging.getLogger(__name__)

# Initialize Stripe
stripe.api_key = STRIPE_SECRET_KEY

router = APIRouter()


@router.post("/create-checkout-session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: CheckoutSessionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a Stripe Checkout Session for Pro subscription or one-time payment

    Flow:
    1. Get or create Stripe customer
    2. Create checkout session with appropriate price
    3. Return session URL for redirect
    """
    try:
        user_id = current_user["user_id"]
        email = current_user["email"]

        logger.info(f"Creating checkout session for user {user_id}, type: {request.payment_type}")

        # Get or create Stripe customer
        stripe_customer_id = current_user.get("stripe_customer_id")

        if not stripe_customer_id:
            # Create new Stripe customer
            customer = stripe.Customer.create(
                email=email,
                metadata={
                    "firebase_uid": user_id
                }
            )
            stripe_customer_id = customer.id

            # Update user in Firestore
            from app.utils.firestore import db
            db.collection("users").document(user_id).update({
                "stripe_customer_id": stripe_customer_id
            })
            logger.info(f"Created Stripe customer: {stripe_customer_id}")

        # Determine price ID and mode based on payment type
        if request.payment_type == "pro":
            price_id = STRIPE_PRO_PRICE_ID
            mode = "subscription"
            # Use custom success URL if provided, otherwise use config default
            base_success_url = request.success_url or PAYMENT_SUCCESS_URL
            success_url = f"{base_success_url}?session_id={{CHECKOUT_SESSION_ID}}"
        elif request.payment_type == "onetime":
            price_id = STRIPE_ONETIME_PRICE_ID
            mode = "payment"
            # For one-time, redirect directly to generation flow
            base_frontend_url = request.success_url or FRONTEND_URL
            success_url = f"{base_frontend_url}?session_id={{CHECKOUT_SESSION_ID}}&onetime=true"
        else:
            raise HTTPException(status_code=400, detail="Invalid payment type")

        # Use custom cancel URL if provided, otherwise use config default
        cancel_url = request.cancel_url or PAYMENT_CANCEL_URL

        # Create checkout session
        session_params = {
            "customer": stripe_customer_id,
            "payment_method_types": ["card"],
            "line_items": [{
                "price": price_id,
                "quantity": 1
            }],
            "mode": mode,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "metadata": {
                "firebase_uid": user_id,
                "payment_type": request.payment_type
            }
        }

        # For subscriptions, enable free trial
        if mode == "subscription":
            session_params["subscription_data"] = {
                "trial_period_days": 7,
                "metadata": {
                    "firebase_uid": user_id
                }
            }

        session = stripe.checkout.Session.create(**session_params)

        logger.info(f"Created checkout session: {session.id}")

        return CheckoutSessionResponse(
            session_id=session.id,
            url=session.url
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating checkout session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create checkout session")


@router.post("/create-portal-session")
async def create_portal_session(
    current_user: dict = Depends(get_current_user)
):
    """
    Create a Stripe Customer Portal session for managing subscription

    Allows users to:
    - Update payment method
    - Cancel subscription
    - View billing history
    """
    try:
        user_id = current_user["user_id"]
        stripe_customer_id = current_user.get("stripe_customer_id")

        if not stripe_customer_id:
            raise HTTPException(
                status_code=400,
                detail="No active subscription found"
            )

        # Create portal session
        session = stripe.billing_portal.Session.create(
            customer=stripe_customer_id,
            return_url=CUSTOMER_PORTAL_RETURN_URL
        )

        logger.info(f"Created portal session for user {user_id}")

        return {"url": session.url}

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating portal session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create portal session")


@router.get("/subscription-status")
async def get_subscription_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current user's subscription status

    Returns:
    - Current tier
    - Usage count and limit
    - Subscription status (active, trialing, cancelled)
    - Trial end date
    - Next billing date
    """
    try:
        user_id = current_user["user_id"]

        return {
            "user_id": user_id,
            "subscription_tier": current_user.get("subscription_tier", "free"),
            "subscription_status": current_user.get("stripe_subscription_status"),
            "usage_count": current_user.get("usage_count", 0),
            "usage_limit": current_user.get("usage_limit", 5),
            "trial_end": current_user.get("trial_end"),
            "current_period_end": current_user.get("subscription_current_period_end"),
            "has_payment_method": current_user.get("payment_method_added", False)
        }

    except Exception as e:
        logger.error(f"Error getting subscription status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get subscription status")
