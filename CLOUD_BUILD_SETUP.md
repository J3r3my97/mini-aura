# Cloud Build Setup Guide

This guide will set up automatic deployments from GitHub to Google Cloud Run.

## Overview

When you push to the `main` branch:
- **API changes** → Automatically builds and deploys `mini-me-api`
- **Worker changes** → Automatically builds and deploys `mini-me-worker`

## Prerequisites

1. ✅ GCP project created
2. ✅ Infrastructure set up (run `setup-gcp.sh` first)
3. ✅ Code pushed to GitHub repository

## Setup Steps

### Step 1: Run in Cloud Shell

Open Cloud Shell (https://console.cloud.google.com) and run:

```bash
# Set your project ID
PROJECT_ID="your-project-id"  # Replace with your actual project ID
gcloud config set project $PROJECT_ID

# Enable Cloud Build API
gcloud services enable cloudbuild.googleapis.com

# Grant Cloud Build permissions to deploy to Cloud Run
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

echo "✅ Cloud Build permissions configured"
```

### Step 2: Connect GitHub Repository

#### Option A: Using Cloud Console (Easier)

1. Go to Cloud Build Triggers: https://console.cloud.google.com/cloud-build/triggers
2. Click **"Connect Repository"**
3. Select **GitHub** as the source
4. Authenticate with GitHub
5. Select your **mini-aura** repository
6. Click **"Connect"**

#### Option B: Using gcloud CLI

```bash
# This will open a browser to authenticate with GitHub
gcloud alpha builds connections create github mini-aura-connection \
  --region=us-central1

# Follow the prompts to authorize GitHub access
```

### Step 3: Create Build Triggers

Run these commands in Cloud Shell:

```bash
# Trigger for API service (builds when api/ changes)
gcloud builds triggers create github \
  --name="mini-me-api-deploy" \
  --repo-name="mini-aura" \
  --repo-owner="YOUR_GITHUB_USERNAME" \
  --branch-pattern="^main$" \
  --build-config="api/cloudbuild.yaml" \
  --included-files="api/**" \
  --description="Deploy API service on push to main"

# Trigger for Worker service (builds when worker/ changes)
gcloud builds triggers create github \
  --name="mini-me-worker-deploy" \
  --repo-name="mini-aura" \
  --repo-owner="YOUR_GITHUB_USERNAME" \
  --branch-pattern="^main$" \
  --build-config="worker/cloudbuild.yaml" \
  --included-files="worker/**" \
  --description="Deploy Worker service on push to main"

echo "✅ Build triggers created!"
```

**Replace `YOUR_GITHUB_USERNAME`** with your actual GitHub username.

### Step 4: Add API Keys to Secret Manager

Before the first deployment, add your API keys:

```bash
# Add Claude API key
echo -n "sk-ant-your-actual-key-here" | \
  gcloud secrets create claude-api-key \
  --data-file=- \
  --replication-policy="automatic"

# Add Stripe secret key
echo -n "sk_test_your-actual-key-here" | \
  gcloud secrets create stripe-secret-key \
  --data-file=- \
  --replication-policy="automatic"

# Grant Cloud Run access to secrets
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

gcloud secrets add-iam-policy-binding claude-api-key \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding stripe-secret-key \
  --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

echo "✅ Secrets configured!"
```

### Step 5: Test the Setup

Push to GitHub to trigger your first build:

```bash
# On your local machine
git add .
git commit -m "Initial deployment setup"
git push origin main
```

**Watch the build:**
- Go to: https://console.cloud.google.com/cloud-build/builds
- You'll see your builds running!
- Takes ~5-10 minutes for first build

### Step 6: Update Pub/Sub Subscription

After the worker deploys, update Pub/Sub to push to the worker:

```bash
# Get the worker URL
WORKER_URL=$(gcloud run services describe mini-me-worker \
  --region=us-central1 \
  --format='value(status.url)')

# Update the subscription
gcloud pubsub subscriptions update generation-jobs-sub \
  --push-endpoint="$WORKER_URL/process"

echo "✅ Pub/Sub connected to worker!"
echo "Worker URL: $WORKER_URL"
```

## Workflow After Setup

From now on, your deployment workflow is simply:

```bash
# Make changes to code
git add .
git commit -m "Add new feature"
git push origin main

# Cloud Build automatically:
# 1. Detects changes
# 2. Builds Docker images
# 3. Deploys to Cloud Run
# 4. Done! ✨
```

## Monitoring Builds

**View build history:**
```bash
gcloud builds list --limit=10
```

**View build logs:**
```bash
gcloud builds log <BUILD_ID>
```

**Or use the Console:**
https://console.cloud.google.com/cloud-build/builds

## Troubleshooting

### Build fails with "permission denied"

Grant additional permissions:
```bash
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$PROJECT_NUMBER@cloudbuild.gserviceaccount.com" \
  --role="roles/storage.admin"
```

### Secret not found

Make sure secrets are created with the exact names:
- `claude-api-key`
- `stripe-secret-key`

List secrets:
```bash
gcloud secrets list
```

### Worker deployment fails

Check that the service account exists:
```bash
gcloud iam service-accounts list | grep mini-me-worker
```

## Next Steps

1. ✅ Run `setup-gcp.sh` in Cloud Shell
2. ✅ Follow this guide to set up Cloud Build
3. ✅ Push to GitHub and watch the magic happen!
4. 🚀 Start building features!
