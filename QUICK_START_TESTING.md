# Quick Start: Testing Pay-As-You-Go

## Step 1: Set Up Stripe (5 minutes)

### A. Get Your Stripe Test Keys

1. Go to: https://dashboard.stripe.com/test/apikeys
2. Copy your **Secret key** (starts with `sk_test_`)

### B. Create Products

1. Go to: https://dashboard.stripe.com/test/products
2. Click **"+ Add product"**

**Create these 3 products:**

| Name | Price | Type | Description |
|------|-------|------|-------------|
| 1 Avatar | $2.99 | One-time | Perfect for trying it out |
| 5 Avatars | $12.99 | One-time | Save $2 • Great for friends |
| 10 Avatars | $19.99 | One-time | Save $10 • Best Value! |

3. After creating each product, **copy the Price ID** (starts with `price_`)

### C. Set Up Webhook (for local testing)

**Option 1: Stripe CLI (Recommended)**
```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login to Stripe
stripe login

# Forward webhooks to your local API
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

This will output a webhook signing secret like: `whsec_...`

**Option 2: Skip for now**
- You can test credit deduction without webhooks
- Webhooks only needed for actual Stripe payments

---

## Step 2: Configure Environment Variables

Create `/api/.env` file:

```bash
cd /Users/null/Workspace/mini-aura/api
cp .env.template .env
```

Edit the `.env` file and add your Stripe keys:

```bash
# Required
PROJECT_ID=mini-aura
FIREBASE_PROJECT_ID=mini-aura
FRONTEND_URL=http://localhost:3000

# Stripe (from Step 1)
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
STRIPE_1_CREDIT_PRICE_ID=price_YOUR_1_CREDIT_ID
STRIPE_5_CREDIT_PRICE_ID=price_YOUR_5_CREDIT_ID
STRIPE_10_CREDIT_PRICE_ID=price_YOUR_10_CREDIT_ID
```

---

## Step 3: Test Credit Logic (No Stripe Required)

This tests the credit system without needing to make actual payments:

```bash
cd /Users/null/Workspace/mini-aura/api

# Run the test script
python test_credit_system.py
```

**Expected Output:**
```
✅ User created: credits=0, free_credits_used=0
✅ Free credit used: has_watermark=True
✅ Correctly rejected: No credits available
✅ Credits added: credits=5
✅ Paid credit used: has_watermark=False
✅ Final state: credits=0, free_credits_used=1, total_generated=6
```

---

## Step 4: Test Full Payment Flow

### Start Services

**Terminal 1: API**
```bash
cd /Users/null/Workspace/mini-aura/api
uvicorn app.main:app --reload
```

**Terminal 2: Worker**
```bash
cd /Users/null/Workspace/mini-aura/worker
python main.py
```

**Terminal 3: Frontend**
```bash
cd /Users/null/Workspace/mini-aura/frontend
npm run dev
```

**Terminal 4: Stripe Webhook Forwarding (if using Stripe CLI)**
```bash
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

### Test Flow

1. **Open browser:** http://localhost:3000

2. **Sign up with new account**

3. **Check Firestore Console:**
   - Go to: https://console.firebase.google.com/project/mini-aura/firestore
   - Find your user document
   - Should see: `credits: 0, free_credits_used: 0`

4. **Generate first avatar (free with watermark):**
   - Upload a photo
   - Wait for generation
   - Download and verify watermark appears in bottom-right

5. **Check Firestore again:**
   - Should see: `credits: 0, free_credits_used: 1, total_generated: 1`

6. **Try generating again:**
   - Should get error: "No credits available"

7. **Purchase credits:**
   - Click "Purchase Credits" on any package
   - Use test card: `4242 4242 4242 4242`
   - Expiry: Any future date (e.g., 12/25)
   - CVC: Any 3 digits (e.g., 123)
   - Complete payment

8. **Check webhook received:**
   - Look at API logs
   - Should see: "Added X credits to user..."

9. **Check Firestore:**
   - Should see credits increased (e.g., `credits: 1` or `credits: 5`)

10. **Generate with paid credit:**
    - Upload photo and generate
    - Download and verify NO watermark

11. **Check Firestore final state:**
    - `credits` should decrease by 1
    - `total_generated` should increase

---

## Step 5: Test Stripe Test Cards

Try different scenarios:

**Success:**
- `4242 4242 4242 4242` - Instant success

**Decline:**
- `4000 0000 0000 0002` - Card declined

**3D Secure:**
- `4000 0025 0000 3155` - Requires authentication

---

## Troubleshooting

### "No credits available" even after payment

1. Check API logs for webhook receipt
2. Check Stripe webhook logs: https://dashboard.stripe.com/test/webhooks
3. Verify webhook secret matches in `.env`
4. Verify price IDs match in Stripe Dashboard

### Watermark not appearing

1. Check job document in Firestore for `has_watermark: true`
2. Check worker logs for "Applying watermark" message
3. Verify image is PNG format

### Checkout fails

1. Check API logs for detailed error
2. Verify Stripe secret key is correct
3. Verify user is authenticated (signed in)
4. Check price IDs are correct

---

## Quick Test Checklist

- [ ] Stripe test keys configured in `.env`
- [ ] 3 products created in Stripe Dashboard
- [ ] Price IDs copied to `.env`
- [ ] `python test_credit_system.py` passes all tests
- [ ] New user gets 1 free credit
- [ ] Free credit generates avatar WITH watermark
- [ ] Out of credits error shows correctly
- [ ] Purchase credits adds to account
- [ ] Paid credit generates avatar WITHOUT watermark
- [ ] Webhook logs show successful credit addition

---

## Need Help?

See the full testing guide: `TESTING_GUIDE.md`
