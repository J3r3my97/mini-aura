"""
Mini-Me Worker Service
Processes generation jobs from Pub/Sub queue
"""

from fastapi import FastAPI, Request, HTTPException
from contextlib import asynccontextmanager
import base64
import json
import os
import logging

# Import pipeline
from pipeline import run_pipeline
from utils.firestore import update_job_status, get_job
from rembg import new_session

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
    logger.info("🚀 Mini-Me Worker starting up...")
    logger.info("📦 Pre-loading rembg model (U2Net)...")

    # Pre-load rembg model into memory (faster processing)
    try:
        new_session("u2net")
        logger.info("✅ rembg model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load rembg model: {str(e)}")

    yield

    # Shutdown
    logger.info("👋 Mini-Me Worker shutting down...")

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
    job_id = None

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
        logger.info(f"📨 Received job: {job_id}")

        # Get current job status for idempotency check
        job = await get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        # Skip if already processing or completed (idempotency protection)
        current_status = job.get("status")
        if current_status in ["processing", "completed"]:
            logger.info(f"⏭️  Job {job_id} already {current_status}, skipping (Pub/Sub retry detected)")
            return {
                "status": "ok",
                "job_id": job_id,
                "message": f"Job already {current_status}, skipped duplicate processing"
            }

        # Update job status to "processing"
        await update_job_status(job_id, "processing")

        # Run the pipeline
        result = await run_pipeline(job_id)

        # Update job status to "completed"
        await update_job_status(
            job_id,
            "completed",
            output_url=result['output_url'],
            metadata=result['metadata']
        )

        logger.info(f"✅ Job {job_id} completed successfully")

        return {
            "status": "ok",
            "job_id": job_id,
            "output_url": result['output_url']
        }

    except Exception as e:
        logger.error(f"❌ Error processing job {job_id}: {str(e)}", exc_info=True)

        # Update job status to "failed"
        if job_id:
            try:
                await update_job_status(
                    job_id,
                    "failed",
                    error_message=str(e)
                )
            except Exception as db_error:
                logger.error(f"Failed to update job status: {str(db_error)}")

        raise HTTPException(status_code=500, detail=str(e))
