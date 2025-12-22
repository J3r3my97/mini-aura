# Pay-As-You-Go Testing Guide

## Pre-Testing Setup

### 1. Stripe Products Setup

Go to [Stripe Dashboard](https://dashboard.stripe.com/test/products) (Test Mode)

**Create 3 Products:**

1. **Product: "1 Avatar"**
   - Pricing Model: One-time
   - Price: $2.99 USD
   - Copy the Price ID (starts with `price_...`)

2. **Product: "5 Avatars"**
   - Pricing Model: One-time
   - Price: $12.99 USD
   - Copy the Price ID

3. **Product: "10 Avatars"**
   - Pricing Model: One-time
   - Price: $19.99 USD
   - Copy the Price ID

### 2. Stripe Webhook Setup

1. Go to [Stripe Webhooks](https://dashboard.stripe.com/test/webhooks)
2. Click "Add endpoint"
3. Endpoint URL: `https://your-api-url/api/webhooks/stripe`
   - For local testing, use: `http://localhost:8000/api/webhooks/stripe`
   - Note: For local testing, you'll need Stripe CLI to forward webhooks
4. Select events to listen to:
   - `checkout.session.completed`
5. Copy the Webhook Signing Secret (starts with `whsec_...`)

### 3. Environment Variables

**API Service** (`/api/.env`):
```bash
# Create this file in /api directory
STRIPE_SECRET_KEY=sk_test_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
STRIPE_1_CREDIT_PRICE_ID=price_your_1_credit_id
STRIPE_5_CREDIT_PRICE_ID=price_your_5_credit_id
STRIPE_10_CREDIT_PRICE_ID=price_your_10_credit_id

# Other required vars
PROJECT_ID=mini-aura
FIREBASE_PROJECT_ID=mini-aura
FRONTEND_URL=http://localhost:3000
```

### 4. Local Testing with Stripe CLI (Optional but Recommended)

Install Stripe CLI:
```bash
# macOS
brew install stripe/stripe-cli/stripe

# Login
stripe login

# Forward webhooks to local API
stripe listen --forward-to localhost:8000/api/webhooks/stripe
```

This will give you a webhook signing secret to use in your `.env` file.

---

## Testing Checklist

### Test 1: New User Flow (Free Credit)

**Expected Behavior:**
- ✅ New user gets 1 free credit
- ✅ Free credit generates avatar WITH watermark
- ✅ `free_credits_used` increments from 0 to 1

**Steps:**
1. Sign up with a new email
2. Check Firestore `users` collection:
   ```json
   {
     "credits": 0,
     "free_credits_used": 0,
     "total_generated": 0
   }
   ```
3. Upload a photo and generate avatar
4. Verify generated avatar has "mini-aura" watermark in bottom-right
5. Check Firestore again:
   ```json
   {
     "credits": 0,
     "free_credits_used": 1,
     "total_generated": 1
   }
   ```

### Test 2: Out of Credits Error

**Expected Behavior:**
- ✅ User with 0 credits and free credit used gets error
- ✅ Error message: "No credits available. Please purchase credits to generate avatars."

**Steps:**
1. Try to generate another avatar with same user
2. Should receive HTTP 402 error
3. Error should prompt user to purchase credits

### Test 3: Purchase Credits (1 Credit Package)

**Expected Behavior:**
- ✅ Stripe checkout opens correctly
- ✅ After payment, webhook adds credits
- ✅ User redirected to success page

**Steps:**
1. Click "Purchase Credits" on "1 Avatar" package
2. Use Stripe test card: `4242 4242 4242 4242`
   - Expiry: Any future date
   - CVC: Any 3 digits
3. Complete payment
4. Check Firestore:
   ```json
   {
     "credits": 1,
     "free_credits_used": 1,
     "total_generated": 1
   }
   ```
5. Check API logs for webhook: "Added 1 credits to user..."

### Test 4: Generate with Paid Credit (No Watermark)

**Expected Behavior:**
- ✅ Avatar generated WITHOUT watermark
- ✅ Paid credit deducted
- ✅ `total_generated` increments

**Steps:**
1. Upload photo and generate avatar
2. Verify generated avatar has NO watermark
3. Check Firestore:
   ```json
   {
     "credits": 0,
     "free_credits_used": 1,
     "total_generated": 2
   }
   ```

### Test 5: Purchase 5 Credits Package

**Expected Behavior:**
- ✅ Checkout shows $12.99
- ✅ 5 credits added after payment

**Steps:**
1. Click "5 Avatars" package
2. Complete payment with test card
3. Check Firestore:
   ```json
   {
     "credits": 5,
     "free_credits_used": 1,
     "total_generated": 2
   }
   ```

### Test 6: Purchase 10 Credits Package

**Expected Behavior:**
- ✅ Checkout shows $19.99
- ✅ 10 credits added after payment

**Steps:**
1. Click "10 Avatars" package
2. Complete payment
3. Check Firestore:
   ```json
   {
     "credits": 15,  // 5 + 10
     "free_credits_used": 1,
     "total_generated": 2
   }
   ```

### Test 7: Multiple Generations

**Expected Behavior:**
- ✅ Credits deduct one at a time
- ✅ All avatars have no watermark

**Steps:**
1. Generate 5 avatars in a row
2. Each should deduct 1 credit
3. Check Firestore:
   ```json
   {
     "credits": 10,  // 15 - 5
     "free_credits_used": 1,
     "total_generated": 7  // 2 + 5
   }
   ```

### Test 8: Subscription Status Endpoint

**Expected Behavior:**
- ✅ API returns correct credit balance
- ✅ `has_watermark` flag is correct

**Steps:**
1. Call: `GET /api/payments/subscription-status`
2. Should return:
   ```json
   {
     "user_id": "...",
     "credits": 10,
     "free_credits_used": 1,
     "total_generated": 7,
     "has_watermark": false  // false because user has paid credits
   }
   ```

### Test 9: Webhook Failure Handling

**Expected Behavior:**
- ✅ Invalid signatures rejected
- ✅ Missing metadata logged

**Steps:**
1. Send webhook with invalid signature
2. Should get 400 error: "Invalid signature"
3. Check logs for error message

### Test 10: Payment Cancel Flow

**Expected Behavior:**
- ✅ User can cancel checkout
- ✅ No credits added
- ✅ Redirected to cancel page

**Steps:**
1. Start checkout
2. Click back/cancel in Stripe
3. Should redirect to `/payment/cancelled`
4. Credits should remain unchanged

---

## Stripe Test Cards

**Successful Payment:**
- `4242 4242 4242 4242` - Standard success

**Failed Payment:**
- `4000 0000 0000 0002` - Card declined

**3D Secure Required:**
- `4000 0025 0000 3155` - Requires authentication

---

## Debug Checklist

If something doesn't work:

### Credits Not Added After Payment
1. Check Stripe webhook logs (Dashboard → Webhooks)
2. Check API logs for webhook receipt
3. Verify webhook secret matches
4. Verify price IDs match in both Stripe and config

### Watermark Issues
1. Check job document in Firestore for `has_watermark` field
2. Check worker logs for "Applying watermark" message
3. Verify image has alpha channel (PNG)

### Checkout Session Fails
1. Verify Stripe price IDs are correct
2. Check API logs for error details
3. Verify user is authenticated
4. Check package name matches: "1_credit", "5_credits", "10_credits"

---

## Production Deployment Notes

Before deploying to production:

1. **Switch to Live Mode in Stripe**
   - Create live products with live prices
   - Update environment variables with live keys

2. **Update Environment Variables**
   - Set production Stripe keys (starts with `pk_live_` and `sk_live_`)
   - Set production webhook secret
   - Set production price IDs
   - Update `FRONTEND_URL` to production URL

3. **Configure Webhook Endpoint**
   - Add production webhook endpoint in Stripe
   - Use production API URL: `https://your-api.com/api/webhooks/stripe`

4. **Test in Production**
   - Run through all test cases with real money (small amounts)
   - Verify webhooks working in production

5. **Monitor**
   - Set up alerts for webhook failures
   - Monitor credit addition in Firestore
   - Track successful payments vs failures
