#!/bin/bash
# Setup CORS for GCS buckets to allow frontend downloads

set -e

PROJECT_ID="mini-aura"
UPLOAD_BUCKET="mini-me-uploads-${PROJECT_ID}"
RESULTS_BUCKET="mini-me-results-${PROJECT_ID}"

echo "Setting up CORS for GCS buckets..."
echo ""

# Apply CORS to results bucket (where generated images are stored)
echo "📦 Applying CORS to results bucket: gs://${RESULTS_BUCKET}"
gsutil cors set gcs-cors-config.json gs://${RESULTS_BUCKET}
echo "✅ CORS applied to results bucket"
echo ""

# Apply CORS to uploads bucket (where input images are stored)
echo "📦 Applying CORS to uploads bucket: gs://${UPLOAD_BUCKET}"
gsutil cors set gcs-cors-config.json gs://${UPLOAD_BUCKET}
echo "✅ CORS applied to uploads bucket"
echo ""

# Verify CORS configuration
echo "🔍 Verifying CORS configuration..."
echo ""
echo "Results bucket CORS:"
gsutil cors get gs://${RESULTS_BUCKET}
echo ""
echo "Uploads bucket CORS:"
gsutil cors get gs://${UPLOAD_BUCKET}
echo ""

echo "✅ All done! CORS is now configured for both buckets."
echo ""
echo "The frontend can now download images from:"
echo "  - http://localhost:3000"
echo "  - https://mini-aura.vercel.app"
echo "  - https://*.vercel.app (all Vercel preview deployments)"
