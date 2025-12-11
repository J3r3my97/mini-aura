"""
Mini-Me Worker Service
Processes generation jobs from Pub/Sub queue
"""

from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
import base64
import json
import os

# Import pipeline (to be created)
# from pipeline import run_pipeline

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Mini-Me Worker starting up...")
    print("📦 Loading rembg model...")
    # Pre-load rembg model here for faster processing
    yield
    # Shutdown
    print("👋 Mini-Me Worker shutting down...")

app = FastAPI(
    title="Mini-Me Worker",
    description="Background job processor for pixel art generation",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "mini-me-worker",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.post("/process")
async def process_job(request: Request):
    """
    Receives Pub/Sub push messages with job_id.
    Processes the generation pipeline.
    """
    try:
        # Parse Pub/Sub message
        envelope = await request.json()

        if not envelope:
            raise HTTPException(status_code=400, detail="No Pub/Sub message received")

        # Decode the message data
        pubsub_message = envelope.get('message', {})
        data = pubsub_message.get('data', '')

        if not data:
            raise HTTPException(status_code=400, detail="No data in Pub/Sub message")

        # Decode base64 job_id
        job_id = base64.b64decode(data).decode('utf-8')
        print(f"📨 Received job: {job_id}")

        # TODO: Process the job
        # await run_pipeline(job_id)

        # For now, just acknowledge
        print(f"✅ Job {job_id} processed (mock)")

        return {"status": "ok", "job_id": job_id}

    except Exception as e:
        print(f"❌ Error processing job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
