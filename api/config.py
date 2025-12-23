"""
Configuration for API Service
"""
import os
import json
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# GCP Configuration
PROJECT_ID = os.getenv("PROJECT_ID", "mini-aura")
REGION = os.getenv("REGION", "us-central1")

# GCS Buckets
GCS_UPLOAD_BUCKET = f"mini-me-uploads-{PROJECT_ID}"
GCS_RESULT_BUCKET = f"mini-me-results-{PROJECT_ID}"

# Firestore
FIRESTORE_DATABASE = PROJECT_ID

# Firebase Authentication
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID", PROJECT_ID)
FIREBASE_CREDENTIALS_JSON = os.getenv("FIREBASE_CREDENTIALS_JSON")  # Optional: explicit credentials

# Parse Firebase credentials if provided
FIREBASE_CREDENTIALS: Optional[dict] = None
if FIREBASE_CREDENTIALS_JSON:
    try:
        # Try parsing as JSON string
        FIREBASE_CREDENTIALS = json.loads(FIREBASE_CREDENTIALS_JSON)
    except json.JSONDecodeError:
        # Try treating it as a file path
        try:
            with open(FIREBASE_CREDENTIALS_JSON, 'r') as f:
                FIREBASE_CREDENTIALS = json.load(f)
        except Exception:
            # If both fail, leave as None (will use ADC)
            pass

# Pub/Sub
PUBSUB_TOPIC = "generation-jobs"

# API Keys
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# Stripe Price IDs for Credit Packages
STRIPE_1_CREDIT_PRICE_ID = os.getenv("STRIPE_1_CREDIT_PRICE_ID")
STRIPE_5_CREDIT_PRICE_ID = os.getenv("STRIPE_5_CREDIT_PRICE_ID")
STRIPE_10_CREDIT_PRICE_ID = os.getenv("STRIPE_10_CREDIT_PRICE_ID")

# Frontend Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
PAYMENT_SUCCESS_URL = f"{FRONTEND_URL}/payment/success"
PAYMENT_CANCEL_URL = f"{FRONTEND_URL}/payment/cancelled"
CUSTOMER_PORTAL_RETURN_URL = f"{FRONTEND_URL}/account"

# File Upload Configuration
MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25MB (modern phone cameras can produce large files)
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "heic", "webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/heic"}

# Rate Limiting
RATE_LIMIT_PER_MINUTE = 10

# Pay-as-you-go Credit System
FREE_CREDITS = 1  # Everyone gets 1 free avatar (with watermark)

CREDIT_PACKAGES = {
    "1_credit": {
        "credits": 3,
        "price_usd": 1.99,
        "stripe_price_id": STRIPE_1_CREDIT_PRICE_ID,
        "name": "Side Character Pack",
        "description": "Just $0.66 each • Perfect for trying it out"
    },
    "5_credits": {
        "credits": 12,
        "price_usd": 4.99,
        "stripe_price_id": STRIPE_5_CREDIT_PRICE_ID,
        "name": "Main Character Pack",
        "description": "Just $0.42 each • Try different photos & outfits",
        "per_avatar_price": 0.42
    },
    "10_credits": {
        "credits": 30,
        "price_usd": 9.99,
        "stripe_price_id": STRIPE_10_CREDIT_PRICE_ID,
        "name": "Villain Pack",
        "description": "Just $0.33 each • For content creators",
        "per_avatar_price": 0.33
    }
}

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Local development
    "https://mini-me.example.com",  # Production (update with actual domain)
]
