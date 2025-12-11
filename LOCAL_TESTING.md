# Local Testing Guide

## Prerequisites

1. **Docker Desktop** installed and running
2. **GCP credentials** set up locally
3. **Environment variables** configured

## Setup

### 1. Authenticate with GCP

```bash
# Login to GCP
gcloud auth login

# Set application default credentials
gcloud auth application-default login

# Set project
gcloud config set project mini-aura
```

### 2. Create `.env` file

Create a `.env` file in the project root:

```bash
# .env
CLAUDE_API_KEY=sk-ant-your-key-here
STRIPE_SECRET_KEY=sk_test_your-key-here
```

### 3. Build and Run with Docker Compose

```bash
# Build images
docker-compose build

# Run worker service
docker-compose up worker

# Or run in background
docker-compose up -d worker
```

The worker will be available at: http://localhost:8001

## Testing the Worker

### Option 1: Test Health Endpoint

```bash
curl http://localhost:8001/
```

Expected response:
```json
{
  "service": "mini-me-worker",
  "status": "healthy",
  "version": "1.0.0"
}
```

### Option 2: Test Full Pipeline (Manual)

You'll need to:
1. Upload a test image to GCS
2. Create a job in Firestore
3. Send a Pub/Sub message (or call `/process` directly)

**Quick test (simulate Pub/Sub message):**

```bash
# Create test job ID
JOB_ID="test-$(uuidgen | tr '[:upper:]' '[:lower:]')"
echo "Test job ID: $JOB_ID"

# TODO: Upload test image to GCS first
# gsutil cp test.jpg gs://mini-me-uploads-mini-aura/$JOB_ID.jpg

# Simulate Pub/Sub message
curl -X POST http://localhost:8001/process \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": {
      \"data\": \"$(echo -n $JOB_ID | base64)\"
    }
  }"
```

## Troubleshooting

### Permission Errors

If you see permission errors accessing GCS/Firestore:

```bash
# Make sure you're authenticated
gcloud auth application-default login

# Verify credentials file exists
ls -la ~/.config/gcloud/application_default_credentials.json
```

### Import Errors

If you see import errors, rebuild the container:

```bash
docker-compose build --no-cache worker
docker-compose up worker
```

### View Logs

```bash
# View logs
docker-compose logs worker

# Follow logs
docker-compose logs -f worker
```

### Connect to Running Container

```bash
# Get container ID
docker ps

# Connect to container
docker exec -it <container-id> /bin/bash

# Test imports
python -c "from pipeline import run_pipeline; print('OK')"
```

## Cleanup

```bash
# Stop services
docker-compose down

# Remove images
docker-compose down --rmi all

# Remove volumes
docker-compose down -v
```

## Alternative: Run Without Docker

If you prefer to run without Docker (faster iteration):

```bash
cd worker

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PROJECT_ID=mini-aura
export REGION=us-central1
export CLAUDE_API_KEY=your-key
export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcloud/application_default_credentials.json

# Run server
uvicorn main:app --reload --port 8001
```

Then test at http://localhost:8001
