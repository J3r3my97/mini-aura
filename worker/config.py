"""
Configuration for Worker Service
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

# API Keys
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
if not CLAUDE_API_KEY:
    raise ValueError("CLAUDE_API_KEY environment variable not set")

# AI Model Configuration
CLAUDE_MODEL = "claude-haiku-4-5"
IMAGEN_MODEL = "imagen-3.0-generate-001"

# Image Processing Configuration
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FORMATS = {"jpg", "jpeg", "png", "heic"}
OUTPUT_FORMAT = "PNG"
OUTPUT_SIZE = (2000, 2000)

# Compositing Configuration
MINI_ME_SCALE = 0.3  # Mini-me is 30% of image height
MINI_ME_POSITION = "bottom-right"  # Default position
WATERMARK_TEXT = "mini-me"
WATERMARK_POSITION = "bottom-left"
