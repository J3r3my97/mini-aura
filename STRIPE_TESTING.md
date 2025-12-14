# Stripe Integration Testing Guide

## Prerequisites

### 1. Stripe Test Mode Setup

```bash
# Get your Stripe test keys from: https://dashboard.stripe.com/test/apikeys
# You need:
# - Publishable key (starts with pk_test_)
# - Secret key (starts with sk_test_)
# - Webhook signing secret (starts with whsec_)
```

### 2. Create Test Products in Stripe Dashboard

Go to https://dashboard.stripe.com/test/products

**Product 1: Mini-Me Pro**
- Name: Mini-Me Pro
- Description: Unlimited pixel art avatars
- Pricing:
  - Price: $9.00 USD
  - Billing: Recurring monthly
  - Free trial: 7 days
- Copy the Price ID (starts with `price_`)

**Product 2: Mini-Me One-Time**
- Name: Mini-Me One-Time Avatar
- Description: Single high-quality pixel art avatar
- Pricing:
  - Price: $3.00 USD
  - Billing: One time
- Copy the Price ID (starts with `price_`)

### 3. Set Environment Variables

**Backend (Cloud Run or local):**
```bash
# Add to Secret Manager or .env
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...  # Get this after webhook setup
STRIPE_PRO_PRICE_ID=price_...    # From Product 1
STRIPE_ONETIME_PRICE_ID=price_... # From Product 2
```

**Frontend (Vercel or local):**
```bash
# Add to .env.local
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_API_URL=http://localhost:8000  # or your deployed API URL
```

### 4. Configure Webhook Endpoint

**Option A: Local Testing (with Stripe CLI)**
```bash
# Install Stripe CLI: https://stripe.com/docs/stripe-cli
stripe login

# Forward webhooks to local API
stripe listen --forward-to http://localhost:8000/api/webhooks/stripe

# Copy the webhook signing secret (whsec_...) to STRIPE_WEBHOOK_SECRET
```

**Option B: Production (Cloud Run)**
```bash
# Get your API URL
API_URL=$(gcloud run services describe mini-me-api --region=us-central1 --format='value(status.url)')

# Create webhook in Stripe Dashboard
# Go to: https://dashboard.stripe.com/test/webhooks/create
# Endpoint URL: $API_URL/api/webhooks/stripe
# Events to listen:
#   - checkout.session.completed
#   - customer.subscription.created
#   - customer.subscription.updated
#   - customer.subscription.deleted
#   - invoice.payment_failed

# Copy the webhook signing secret to Secret Manager
echo "whsec_..." | gcloud secrets create STRIPE_WEBHOOK_SECRET --data-file=-
```

---

## Test Scenarios

### Test 1: Free Tier (No Payment)

**Steps:**
1. Sign up with a new email
2. Upload an image
3. Verify avatar generates successfully
4. Upload 4 more images (should work - 5 total)
5. Try to upload 6th image
   - **Expected**: Error message "Usage limit exceeded. Please upgrade."

**Verify:**
- [ ] Firestore user has `usage_count: 5`, `usage_limit: 5`, `subscription_tier: "free"`
- [ ] Watermark appears on all generated images
- [ ] Upgrade prompt appears after 3rd generation

---

### Test 2: Pro Subscription ($9/month with 7-day trial)

**Steps:**
1. Sign up or use existing free tier account
2. Click "Upgrade to Pro" or "Get Started" on Pro plan
3. Complete Stripe checkout (use test card: `4242 4242 4242 4242`)
4. Verify redirect to success page
5. Check account page shows:
   - Subscription status: "Pro"
   - Trial ends: [7 days from now]
   - Usage: Unlimited
6. Generate multiple images (>5)
   - **Expected**: All work, no watermark
7. Wait for webhook processing (check logs)

**Verify in Firestore:**
```
users/{userId}:
  subscription_tier: "pro"
  subscription_status: "trialing"
  stripe_customer_id: "cus_..."
  stripe_subscription_id: "sub_..."
  trial_end: [Timestamp 7 days ahead]
  usage_count: [number]
  usage_limit: -1  # unlimited
```

**Verify in Stripe Dashboard:**
- [ ] Customer created
- [ ] Subscription created with 7-day trial
- [ ] Status: Trialing
- [ ] Next invoice scheduled for trial end date

---

### Test 3: One-Time Payment ($3)

**Steps:**
1. Sign up or use account that's at free tier limit
2. Click "Get Started" on One-Time plan
3. Complete Stripe checkout (test card: `4242 4242 4242 4242`)
4. Verify redirect to success page with `session_id` in URL
5. Upload an image immediately (should use the session_id)
   - **Expected**: Generation works even if free tier exhausted
6. Try to upload another image without new payment
   - **Expected**: Error if free tier limit reached

**Verify:**
- [ ] Session payment status: "paid"
- [ ] Session metadata has `payment_type: "onetime"`
- [ ] Generation works with session_id parameter
- [ ] User's tier remains "free" (one-time doesn't change tier)
- [ ] No watermark on the paid generation

---

### Test 4: Customer Portal (Subscription Management)

**Steps:**
1. Log in with Pro subscription account
2. Go to Account page
3. Click "Manage Subscription"
4. Verify redirects to Stripe Customer Portal
5. Test actions:
   - Update payment method
   - Cancel subscription
   - View invoices
   - Reactivate subscription

**Verify after cancellation:**
- [ ] Webhook `customer.subscription.deleted` received
- [ ] Firestore user updated:
  - `subscription_tier: "free"`
  - `subscription_status: "canceled"`
  - `usage_limit: 5`
- [ ] User can no longer generate unlimited images
- [ ] Watermark appears on new generations

---

### Test 5: Webhook Processing

**Monitor webhook events:**
```bash
# Watch Cloud Run logs
gcloud run services logs tail mini-me-api --region=us-central1

# Or local logs if using Stripe CLI
stripe listen --forward-to http://localhost:8000/api/webhooks/stripe
```

**Trigger each webhook event:**

**A. `checkout.session.completed`**
- Action: Complete a payment
- Expected log: "✅ Checkout session completed for user: [user_id]"
- Verify: User data updated in Firestore

**B. `customer.subscription.created`**
- Action: Subscribe to Pro
- Expected log: "✅ Subscription created for user: [user_id]"
- Verify: `subscription_tier: "pro"`, `usage_limit: -1`

**C. `customer.subscription.updated`**
- Action: Trial ends → active subscription
- Expected log: "✅ Subscription updated for user: [user_id]"
- Verify: `subscription_status: "active"` (no longer "trialing")

**D. `customer.subscription.deleted`**
- Action: Cancel subscription
- Expected log: "✅ Subscription canceled for user: [user_id]"
- Verify: Downgraded to free tier

**E. `invoice.payment_failed`**
- Action: Use test card `4000 0000 0000 0341` (card declined)
- Expected log: "⚠️  Payment failed for user: [user_id]"
- Verify: Email sent (if configured), subscription marked at risk

---

### Test 6: Edge Cases

**A. Multiple Subscriptions**
- Try to subscribe to Pro while already subscribed
- **Expected**: Should update existing subscription, not create duplicate

**B. Session Expiry**
- Complete one-time payment but wait 30+ minutes before generating
- **Expected**: Session expired, should prompt for new payment

**C. Webhook Replay Attack**
- Resend same webhook event twice
- **Expected**: Idempotent processing, no duplicate updates

**D. Invalid Payment Method**
- Use test card `4000 0000 0000 0002` (card declined)
- **Expected**: Payment fails, user not upgraded

**E. Free → Pro → Cancel → Free**
- Full lifecycle test
- **Expected**: Smooth transitions, correct tier at each stage

---

## Test Cards

```
Success: 4242 4242 4242 4242
Decline: 4000 0000 0000 0002
3D Secure: 4000 0025 0000 3155
Insufficient funds: 4000 0000 0000 9995
```

More: https://stripe.com/docs/testing

---

## Verification Checklist

After all tests:

- [ ] All webhook events process correctly
- [ ] Firestore data updates accurately
- [ ] Usage limits enforced properly
- [ ] Watermarks appear/disappear correctly
- [ ] Customer Portal works
- [ ] Trial period works (7 days)
- [ ] One-time payments work
- [ ] Subscription cancellation works
- [ ] No orphaned data (customers without users, etc.)
- [ ] Error handling graceful (friendly messages to users)

---

## Debugging Tips

**Check webhook delivery:**
```bash
# Stripe Dashboard
https://dashboard.stripe.com/test/webhooks
# Look for failed deliveries, retry manually
```

**Check Firestore data:**
```bash
# Firebase Console
https://console.firebase.google.com/project/mini-aura/firestore

# Or using gcloud
gcloud firestore export gs://mini-aura-backups/$(date +%Y%m%d)
```

**Check Cloud Run logs:**
```bash
gcloud run services logs read mini-me-api \
  --region=us-central1 \
  --limit=100
```

**Common Issues:**
- Webhook signature verification fails → Check `STRIPE_WEBHOOK_SECRET` is correct
- Payment succeeds but user not upgraded → Check webhook event reached server
- One-time payment doesn't work → Check `session_id` passed in generate request
- Subscription shows but no images generate → Check `usage_limit` set to -1

---

## Production Checklist

Before going live:

- [ ] Switch to live Stripe keys (`sk_live_`, `pk_live_`)
- [ ] Create live products with same prices
- [ ] Configure live webhook endpoint
- [ ] Update `ALLOWED_ORIGINS` in backend config
- [ ] Test with real card (then refund)
- [ ] Set up Stripe email notifications
- [ ] Configure tax settings (if applicable)
- [ ] Set up invoice emails
- [ ] Configure business details in Stripe

---

## Support Resources

- Stripe Dashboard: https://dashboard.stripe.com/test
- Stripe Logs: https://dashboard.stripe.com/test/logs
- Stripe Docs: https://stripe.com/docs
- Test Cards: https://stripe.com/docs/testing
- Webhook Testing: https://stripe.com/docs/webhooks/test
