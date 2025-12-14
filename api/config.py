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
STRIPE_PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID")
STRIPE_ONETIME_PRICE_ID = os.getenv("STRIPE_ONETIME_PRICE_ID")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

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

# Usage Limits by Tier
USAGE_LIMITS = {
    "free": 5,
    "starter": 20,
    "creator": 100,
    "pro": -1  # Unlimited
}

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Local development
    "https://mini-me.example.com",  # Production (update with actual domain)
]
