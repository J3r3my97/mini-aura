"""
Mini-Me API Service
FastAPI backend for handling uploads, auth, and job management
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

# Import routers (to be created)
# from app.routes import auth, generate, jobs, subscription

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Mini-Me API starting up...")
    # Initialize Firebase, Firestore connections here
    yield
    # Shutdown
    print("👋 Mini-Me API shutting down...")

app = FastAPI(
    title="Mini-Me API",
    description="AI Pixel Art Avatar Generator",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict in production
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

# TODO: Include routers
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(generate.router, prefix="/api", tags=["generate"])
# app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
# app.include_router(subscription.router, prefix="/api/subscription", tags=["subscription"])
