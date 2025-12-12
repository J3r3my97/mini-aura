# 🚀 Deployment Guide — Mini-Me Frontend

Complete guide to deploy the Next.js frontend to Vercel and connect it to your Google Cloud API.

---

## 📋 Overview

**Architecture:**
```
User Browser
    ↓
Vercel (Frontend - Next.js)
    ↓
Google Cloud Run (Backend - FastAPI API)
    ↓
Google Cloud (Firestore, GCS, Pub/Sub, etc.)
```

**What you'll deploy:**
1. ✅ **Backend API** → Google Cloud Run (already set up)
2. ✅ **Frontend** → Vercel (this guide)

---

## Part 1: Deploy Backend API to Google Cloud

### Step 1: Get Your API URL

Your backend API will be deployed to Cloud Run. The URL format is:
```
https://mini-me-api-<random-hash>-uc.a.run.app
```

**To find it:**

```bash
# After deploying your API to Cloud Run
gcloud run services describe mini-me-api \
  --region=us-central1 \
  --format='value(status.url)'
```

Or check in Google Cloud Console:
- Go to **Cloud Run** → Select `mini-me-api` → Copy the URL

**Example:** `https://mini-me-api-abc123-uc.a.run.app`

### Step 2: Update Backend CORS Settings

Your backend needs to allow requests from Vercel. Edit `api/app/main.py`:

```python
# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",           # Local development
        "https://mini-me.vercel.app",      # Your Vercel production URL
        "https://*.vercel.app"             # All Vercel preview deployments
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Then redeploy the API:
```bash
cd api
git add .
git commit -m "Update CORS for Vercel"
git push origin main
# Cloud Build will auto-deploy
```

---

## Part 2: Deploy Frontend to Vercel

### Option A: Deploy via Vercel Dashboard (Recommended)

#### Step 1: Push Code to GitHub

```bash
# From project root
git add .
git commit -m "Complete frontend implementation"
git push origin main
```

#### Step 2: Import Project in Vercel

1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"Add New Project"**
3. Import your GitHub repository
4. Configure project:
   - **Framework Preset:** Next.js
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `.next`

#### Step 3: Add Environment Variables

In Vercel project settings → **Environment Variables**, add:

```bash
# Firebase Configuration (all from your .env.local)
NEXT_PUBLIC_FIREBASE_API_KEY=AIzaSyBI7eWzKwpTVpPgbnofu2YuBLvlucEa_nA
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=mini-aura.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=mini-aura
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=mini-aura.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=37275206280
NEXT_PUBLIC_FIREBASE_APP_ID=1:37275206280:web:55daf67011274bff19d53d

# API URL (IMPORTANT: Use your Cloud Run URL from Part 1)
NEXT_PUBLIC_API_URL=https://mini-me-api-abc123-uc.a.run.app

# Environment
NEXT_PUBLIC_ENV=production
```

**⚠️ CRITICAL:** Replace `https://mini-me-api-abc123-uc.a.run.app` with your actual Cloud Run URL!

#### Step 4: Deploy

Click **"Deploy"** — Vercel will:
1. Install dependencies
2. Build your Next.js app
3. Deploy to global CDN
4. Give you a URL like `https://mini-me.vercel.app`

**Done!** Your frontend is live. 🎉

---

### Option B: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy from frontend directory
cd frontend
vercel

# Follow prompts:
# - Link to existing project? No
# - Project name: mini-me
# - Directory: ./ (current directory is already frontend)
# - Override settings? No

# Add environment variables
vercel env add NEXT_PUBLIC_API_URL
# Enter your Cloud Run URL when prompted

vercel env add NEXT_PUBLIC_FIREBASE_API_KEY
# Enter value...
# Repeat for all Firebase env vars

# Deploy to production
vercel --prod
```

---

## Part 3: Verify Deployment

### Step 1: Check Frontend

Visit your Vercel URL (e.g., `https://mini-me.vercel.app`)

**Test:**
- [ ] Page loads without errors
- [ ] Design looks correct (Neumorphic style)
- [ ] Firebase auth works (sign in with Google)
- [ ] Can upload image

### Step 2: Check API Connection

Open browser console (F12) and try uploading an image.

**Success:** You should see API requests to your Cloud Run URL:
```
POST https://mini-me-api-abc123-uc.a.run.app/api/generate
GET https://mini-me-api-abc123-uc.a.run.app/api/jobs/{job_id}
```

**If errors:**
- Check CORS settings in backend
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check API logs in Google Cloud Console

---

## 🔧 Configuration Checklist

### Backend (Google Cloud Run)

- [x] API deployed to Cloud Run
- [ ] CORS allows Vercel domain (`https://*.vercel.app`)
- [ ] Firebase Admin SDK initialized
- [ ] Firestore, GCS, Pub/Sub configured
- [ ] Environment variables set (in Cloud Run console)

### Frontend (Vercel)

- [ ] Project linked to GitHub
- [ ] Root directory set to `frontend`
- [ ] All Firebase env vars added
- [ ] `NEXT_PUBLIC_API_URL` points to Cloud Run
- [ ] Production deployment successful

---

## 🌍 Custom Domain (Optional)

### Add Custom Domain to Vercel

1. Go to Vercel project → **Settings** → **Domains**
2. Add your domain (e.g., `mini-me.app`)
3. Update DNS records as instructed
4. Vercel auto-provisions SSL certificate

### Update Backend CORS

Add your custom domain to CORS whitelist:

```python
allow_origins=[
    "http://localhost:3000",
    "https://mini-me.vercel.app",
    "https://*.vercel.app",
    "https://mini-me.app",          # Add your custom domain
    "https://www.mini-me.app"       # And www subdomain
],
```

---

## 🔍 Troubleshooting

### Issue: "Failed to fetch" errors

**Cause:** CORS not configured correctly

**Fix:**
1. Check backend CORS settings include Vercel domain
2. Redeploy backend after CORS changes
3. Clear browser cache and try again

### Issue: "Authorization required" in production

**Cause:** Firebase env vars not set in Vercel

**Fix:**
1. Go to Vercel → Settings → Environment Variables
2. Verify all `NEXT_PUBLIC_FIREBASE_*` vars are present
3. Redeploy: Vercel → Deployments → Click "..." → Redeploy

### Issue: Images not loading

**Cause:** Image optimization domains not configured

**Fix:** Already configured in `next.config.js`:
```javascript
images: {
  remotePatterns: [
    { hostname: 'images.unsplash.com' },
    { hostname: 'storage.googleapis.com' }
  ]
}
```

### Issue: API calls timing out

**Cause:** Cloud Run cold start or usage limits exceeded

**Fix:**
1. Check Cloud Run logs in GCP Console
2. Increase Cloud Run timeout (default: 60s)
3. Check Firestore usage limits

---

## 💰 Cost Estimates

### Vercel (Frontend)

**Free Tier includes:**
- 100 GB bandwidth/month
- Unlimited deployments
- Automatic HTTPS
- Global CDN

**Hobby Plan ($20/month):**
- 1 TB bandwidth
- Priority support
- Advanced analytics

### Google Cloud (Backend)

Estimated for ~1,000 users/month:
- **Cloud Run:** ~$5-10/month
- **Firestore:** ~$2-5/month
- **Cloud Storage:** ~$1-3/month
- **Pub/Sub:** ~$1/month
- **Imagen API:** Pay per image generated

**Total:** ~$10-20/month + image generation costs

---

## 📊 Monitoring

### Vercel Analytics

Enable in Vercel dashboard:
- Pageviews
- User sessions
- Performance metrics
- Error tracking

### Google Cloud Monitoring

Check in GCP Console:
- **Cloud Run:** Request count, latency, errors
- **Cloud Logging:** API logs, error traces
- **Cloud Trace:** Request tracing
- **Firestore:** Read/write operations

---

## 🚀 Deployment Workflow

### For Future Updates

**Backend changes:**
```bash
cd api
# Make changes
git add .
git commit -m "Update backend"
git push origin main
# Cloud Build auto-deploys to Cloud Run
```

**Frontend changes:**
```bash
cd frontend
# Make changes
git add .
git commit -m "Update frontend"
git push origin main
# Vercel auto-deploys from GitHub
```

Both deploy automatically on push to `main` branch! 🎉

---

## 🎯 Post-Deployment Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed to Cloud Run
- [ ] Custom domain configured (optional)
- [ ] CORS allows Vercel domain
- [ ] Environment variables set correctly
- [ ] Firebase auth tested in production
- [ ] Image upload and generation tested
- [ ] Download functionality tested
- [ ] Mobile responsive design verified
- [ ] Analytics/monitoring enabled

---

## 📚 Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Google Cloud Run Docs](https://cloud.google.com/run/docs)
- [Next.js Deployment](https://nextjs.org/docs/deployment)
- [Firebase Hosting Alternative](https://firebase.google.com/docs/hosting)

---

## ✅ Quick Answer to Your Questions

### "To deploy I'd just need to get it on Vercel?"

**Yes!** Steps:
1. Push code to GitHub
2. Import in Vercel
3. Set environment variables (especially `NEXT_PUBLIC_API_URL`)
4. Deploy

### "Will it hit the API deployed in Google Cloud?"

**Yes!** As long as you:
1. Set `NEXT_PUBLIC_API_URL` to your Cloud Run API URL
2. Update backend CORS to allow Vercel domain
3. Both are using the same Firebase project

**Flow:** User → Vercel (Frontend) → Cloud Run (API) → Firestore/GCS

---

**Ready to deploy!** Just need your Cloud Run API URL to add to Vercel environment variables. 🚀
