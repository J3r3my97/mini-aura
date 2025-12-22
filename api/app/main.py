"""
Mini-Me API Service
FastAPI backend for handling uploads, auth, and job management
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Import routers
from app.routes import generate, jobs, payments, webhooks
from app.auth import initialize_firebase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("🚀 Mini-Me API starting up...")

    # Initialize Firebase Admin SDK
    try:
        initialize_firebase()
        logger.info("✅ Firebase Admin SDK initialized")
    except Exception as e:
        logger.error(f"❌ Firebase initialization failed: {str(e)}")
        # Don't raise - allow app to start for debugging

    yield

    # Shutdown
    logger.info("👋 Mini-Me API shutting down...")

app = FastAPI(
    title="Mini-Me API",
    description="AI Pixel Art Avatar Generator",
    version="1.0.0",
    lifespan=lifespan
)

# Attach rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration - allow all origins for now (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily for debugging
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "mini-me-api",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Kubernetes health check"""
    return {"status": "ok"}

# Include routers
app.include_router(generate.router, prefix="/api", tags=["generate"])
app.include_router(jobs.router, prefix="/api", tags=["jobs"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
