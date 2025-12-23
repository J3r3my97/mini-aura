# Secret Manager Setup for Pay-As-You-Go

## Required Secrets

You need to create these secrets in Google Cloud Secret Manager:

### 1. Stripe Secrets

```bash
# Get your Stripe test/live keys from:
# https://dashboard.stripe.com/test/apikeys (test mode)
# https://dashboard.stripe.com/apikeys (live mode)

# Stripe Secret Key
gcloud secrets create STRIPE_SECRET_KEY \
  --data-file=- <<< "sk_test_YOUR_SECRET_KEY_HERE"

# Stripe Webhook Secret
# Get this from: https://dashboard.stripe.com/test/webhooks
# OR use Stripe CLI: stripe listen --print-secret
gcloud secrets create STRIPE_WEBHOOK_SECRET \
  --data-file=- <<< "whsec_YOUR_WEBHOOK_SECRET_HERE"
```

### 2. Stripe Price IDs (Credit Packages)

**Important:** First create the products in Stripe Dashboard, then add the Price IDs to Secret Manager.

**Create Products in Stripe:**
1. Go to https://dashboard.stripe.com/test/products
2. Create these 3 products (One-time payments):
   - **1 Avatar** - $2.99
   - **5 Avatars** - $12.99
   - **10 Avatars** - $19.99
3. Copy each Price ID (starts with `price_...`)

**Add to Secret Manager:**

```bash
# 1 Credit Package ($2.99)
gcloud secrets create STRIPE_1_CREDIT_PRICE_ID \
  --data-file=- <<< "price_YOUR_1_CREDIT_PRICE_ID"

# 5 Credits Package ($12.99)
gcloud secrets create STRIPE_5_CREDIT_PRICE_ID \
  --data-file=- <<< "price_YOUR_5_CREDIT_PRICE_ID"

# 10 Credits Package ($19.99)
gcloud secrets create STRIPE_10_CREDIT_PRICE_ID \
  --data-file=- <<< "price_YOUR_10_CREDIT_PRICE_ID"
```

### 3. Other Required Secrets

```bash
# Claude API Key (for AI prompts - optional for testing)
gcloud secrets create CLAUDE_API_KEY \
  --data-file=- <<< "sk-ant-YOUR_CLAUDE_API_KEY"

# Storage Service Account (if not already created)
# This should already exist from your initial setup
# gcloud secrets create mini-me-storage-key \
#   --data-file=/path/to/service-account-key.json
```

## Verify Secrets

Check all secrets are created:

```bash
gcloud secrets list | grep STRIPE
```

Should output:
```
STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET
STRIPE_1_CREDIT_PRICE_ID
STRIPE_5_CREDIT_PRICE_ID
STRIPE_10_CREDIT_PRICE_ID
```

## Grant Access to Cloud Run Service Account

Make sure your Cloud Run service account can access these secrets:

```bash
# Get your service account email
SERVICE_ACCOUNT="mini-me-api@mini-aura.iam.gserviceaccount.com"

# Grant access to all Stripe secrets
for SECRET in STRIPE_SECRET_KEY STRIPE_WEBHOOK_SECRET STRIPE_1_CREDIT_PRICE_ID STRIPE_5_CREDIT_PRICE_ID STRIPE_10_CREDIT_PRICE_ID CLAUDE_API_KEY; do
  gcloud secrets add-iam-policy-binding $SECRET \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor"
done
```

## Update Secrets (if needed)

To update a secret with a new value:

```bash
# Add a new version
echo -n "new_secret_value" | gcloud secrets versions add SECRET_NAME --data-file=-

# Cloud Build automatically uses :latest version
```

## Remove Old Secrets (Cleanup)

The old subscription-based secrets can be deleted:

```bash
# Only run this after confirming new secrets work!
gcloud secrets delete STRIPE_PRO_PRICE_ID --quiet
gcloud secrets delete STRIPE_ONETIME_PRICE_ID --quiet
```

## Testing Secrets in Cloud Run

After deployment, verify secrets are loaded:

```bash
# Get logs from Cloud Run
gcloud run services logs read mini-me-api --limit=50 --region=us-central1

# Should NOT see errors about missing STRIPE_*_CREDIT_PRICE_ID
```

## Local Development

For local development, you can either:

**Option 1: Use Secret Manager (Recommended)**
```bash
# Authenticate
gcloud auth application-default login

# Secrets will be fetched automatically if config.py uses Secret Manager client
```

**Option 2: Use .env file**
```bash
# Create /api/.env with your secrets (don't commit!)
cd api
cp .env.template .env
# Edit .env with your values
```

## Common Issues

### "Permission denied" errors
```bash
# Make sure service account has secretAccessor role
gcloud secrets add-iam-policy-binding STRIPE_SECRET_KEY \
  --member="serviceAccount:mini-me-api@mini-aura.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### "Secret not found" errors
```bash
# Check secret exists
gcloud secrets describe STRIPE_1_CREDIT_PRICE_ID

# If not found, create it
gcloud secrets create STRIPE_1_CREDIT_PRICE_ID \
  --data-file=- <<< "price_YOUR_PRICE_ID"
```

### Wrong secret value
```bash
# Check current value (if you have access)
gcloud secrets versions access latest --secret=STRIPE_1_CREDIT_PRICE_ID

# Update with new value
echo -n "price_correct_value" | gcloud secrets versions add STRIPE_1_CREDIT_PRICE_ID --data-file=-
```
