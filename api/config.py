"""
Configuration for API Service
"""
import os
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
