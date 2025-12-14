#!/bin/bash

# Mini-Me GCP Infrastructure Setup Script
# Run this in Google Cloud Shell

set -e  # Exit on error

echo "🚀 Mini-Me GCP Setup"
echo "===================="
echo ""

# Configuration variables
read -p "Enter GCP Project ID (e.g., mini-me-prod): " PROJECT_ID
read -p "Enter GCP Region (default: us-central1): " REGION
REGION=${REGION:-us-central1}

echo ""
echo "📋 Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Set the project
echo "🔧 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo ""
echo "📦 Enabling required Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    firestore.googleapis.com \
    storage.googleapis.com \
    pubsub.googleapis.com \
    aiplatform.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com

echo "✅ APIs enabled"

# Create GCS buckets
echo ""
echo "🪣 Creating Cloud Storage buckets..."

# Uploads bucket
gcloud storage buckets create gs://mini-me-uploads-$PROJECT_ID \
    --location=$REGION \
    --uniform-bucket-level-access

# Results bucket
gcloud storage buckets create gs://mini-me-results-$PROJECT_ID \
    --location=$REGION \
    --uniform-bucket-level-access

# Set CORS on uploads bucket (for direct upload from frontend)
echo '[
  {
    "origin": ["*"],
    "method": ["GET", "POST", "PUT"],
    "responseHeader": ["Content-Type"],
    "maxAgeSeconds": 3600
  }
]' > cors-config.json

gcloud storage buckets update gs://mini-me-uploads-$PROJECT_ID --cors-file=cors-config.json
rm cors-config.json

# Set lifecycle policy (delete after 30 days)
echo '{
  "lifecycle": {
    "rule": [{
      "action": {"type": "Delete"},
      "condition": {"age": 30}
    }]
  }
}' > lifecycle.json

gcloud storage buckets update gs://mini-me-uploads-$PROJECT_ID --lifecycle-file=lifecycle.json
gcloud storage buckets update gs://mini-me-results-$PROJECT_ID --lifecycle-file=lifecycle.json
rm lifecycle.json

echo "✅ Buckets created"

# Create Firestore database
echo ""
echo "🔥 Creating Firestore database..."
gcloud firestore databases create \
    --location=$REGION \
    --type=firestore-native \
    || echo "⚠️  Firestore database may already exist"

echo "✅ Firestore configured"

# Create Pub/Sub topic and subscription
echo ""
echo "📬 Creating Pub/Sub topic and subscription..."

# Create main topic
gcloud pubsub topics create generation-jobs

# Create dead letter topic for failed jobs
gcloud pubsub topics create generation-jobs-dlq

# Create dead letter subscription
gcloud pubsub subscriptions create generation-jobs-dlq-sub \
    --topic=generation-jobs-dlq

# Create main subscription (push to worker service)
# Note: We'll update the push endpoint after deploying the worker
gcloud pubsub subscriptions create generation-jobs-sub \
    --topic=generation-jobs \
    --ack-deadline=300 \
    --message-retention-duration=7d \
    --max-delivery-attempts=5 \
    --dead-letter-topic=generation-jobs-dlq

# Grant Pub/Sub service account permissions for DLQ
echo "🔑 Granting DLQ permissions..."

# Get the Pub/Sub service account number
PUBSUB_SA="service-$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')@gcp-sa-pubsub.iam.gserviceaccount.com"

# Grant publisher role on DLQ topic
gcloud pubsub topics add-iam-policy-binding generation-jobs-dlq \
    --member="serviceAccount:$PUBSUB_SA" \
    --role="roles/pubsub.publisher"

# Grant subscriber role on main subscription
gcloud pubsub subscriptions add-iam-policy-binding generation-jobs-sub \
    --member="serviceAccount:$PUBSUB_SA" \
    --role="roles/pubsub.subscriber"

echo "✅ Pub/Sub configured with dead letter queue (max 5 retries)"

# Create service account for the application
echo ""
echo "🔐 Creating service account..."

SA_NAME="mini-me-worker"
SA_EMAIL="$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

gcloud iam service-accounts create $SA_NAME \
    --display-name="Mini-Me Worker Service Account" \
    || echo "⚠️  Service account may already exist"

# Grant necessary permissions
echo "🔑 Granting IAM permissions..."

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.objectAdmin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/pubsub.publisher"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/aiplatform.user"

echo "✅ Service account configured"

# Create Secret Manager secrets for API keys
echo ""
echo "🔒 Setting up Secret Manager..."

echo "⚠️  You'll need to add these secrets manually:"
echo "  1. CLAUDE_API_KEY"
echo "  2. STRIPE_SECRET_KEY"
echo ""
echo "Run these commands with your actual keys:"
echo "  echo -n 'your-claude-key' | gcloud secrets create CLAUDE_API_KEY --data-file=-"
echo "  echo -n 'your-stripe-key' | gcloud secrets create STRIPE_SECRET_KEY --data-file=-"

# Summary
echo ""
echo "✨ Setup complete!"
echo "===================="
echo ""
echo "📝 Summary:"
echo "  Project ID: $PROJECT_ID"
echo "  Region: $REGION"
echo "  Upload Bucket: gs://mini-me-uploads-$PROJECT_ID"
echo "  Results Bucket: gs://mini-me-results-$PROJECT_ID"
echo "  Pub/Sub Topic: generation-jobs"
echo "  Service Account: $SA_EMAIL"
echo ""
echo "📋 Next steps:"
echo "  1. Add API keys to Secret Manager (see commands above)"
echo "  2. Set up Firebase Auth project at: https://console.firebase.google.com"
echo "  3. Deploy API service: cd api && gcloud run deploy mini-me-api --source ."
echo "  4. Deploy Worker service: cd worker && gcloud run deploy mini-me-worker --source ."
echo "  5. Update Pub/Sub subscription with Worker URL"
echo ""
echo "🎉 You're ready to build!"
