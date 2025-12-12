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
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# File Upload Configuration
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "heic"}
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
