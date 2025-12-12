"""
Mini-Me API Service
FastAPI backend for handling uploads, auth, and job management
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging

# Import routers
from app.routes import generate, jobs
from app.auth import initialize_firebase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.vercel\.app",  # Allow all Vercel deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Also allow localhost for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
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
# TODO: Add auth and subscription routers later
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(subscription.router, prefix="/api/subscription", tags=["subscription"])
