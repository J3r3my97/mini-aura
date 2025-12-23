# Mini-Aura: AI Pixel Art Avatar Generator

Turn yourself into pixel art—instantly.

**Live Site:** https://miniaura.aurafarmer.co

---

## 🎮 What is Mini-Aura?

Mini-Aura transforms your photos into stunning isometric pixel art avatars using AI. Upload a selfie, get a custom LEGO/voxel-style character, and customize it with our retro GBA-style editor.

### Features

- ✅ **AI-Powered Generation** - Claude Haiku analyzes your photo, Google Imagen 3 creates pixel art
- ✅ **Interactive Customization** - Position, scale, and rotate your avatar on your photo
- ✅ **Pay-As-You-Go Credits** - No subscriptions, just buy credits when needed
- ✅ **Free Tier** - Everyone gets 1 free avatar (with watermark)
- ✅ **High Quality Downloads** - Full-resolution PNG exports
- ✅ **Firebase Authentication** - Secure email/password and Google OAuth

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │─────▶│   API (GCR)  │─────▶│   Worker    │
│  (Vercel)   │      │   FastAPI    │      │  (Cloud Run)│
└─────────────┘      └──────────────┘      └─────────────┘
                             │                     │
                             ▼                     ▼
                     ┌──────────────┐      ┌─────────────┐
                     │  Firestore   │      │ GCS Buckets │
                     │   (Users)    │      │  (Images)   │
                     └──────────────┘      └─────────────┘
                             │
                             ▼
                     ┌──────────────┐
                     │    Stripe    │
                     │  (Payments)  │
                     └──────────────┘
```

### Tech Stack

- **Frontend:** Next.js 14, React, TypeScript, Tailwind CSS
- **Backend:** Python 3.11, FastAPI
- **Worker:** Python 3.11, Cloud Run Jobs
- **AI:** Claude Haiku 4 (vision), Google Imagen 3 (generation)
- **Auth:** Firebase Authentication
- **Storage:** GCS (images), Firestore (users)
- **Payments:** Stripe (one-time checkout)
- **Infrastructure:** Google Cloud Platform + Vercel

---

## 📁 Project Structure

```
mini-aura/
├── api/                        # FastAPI backend (Cloud Run)
│   ├── app/
│   │   ├── main.py            # Main API application
│   │   ├── routes/            # API endpoints (generate, webhooks)
│   │   └── utils/             # Firestore, payments
│   ├── cloudbuild.yaml        # CI/CD configuration
│   └── Dockerfile
│
├── worker/                     # Background job processor (Cloud Run)
│   ├── main.py                # Worker service
│   ├── pipeline.py            # AI generation pipeline
│   ├── utils/                 # Claude vision, Imagen
│   └── Dockerfile
│
├── frontend/                   # Next.js web app (Vercel)
│   ├── app/                   # Next.js 14 app directory
│   ├── components/            # React components
│   │   └── AvatarEditor.tsx   # GBA-style customization UI
│   └── lib/                   # API client, utils
│
├── docs/                       # Documentation
│   ├── setup/                 # Production setup guides
│   ├── development/           # Development & testing docs
│   └── archive/               # Historical documents
│
└── README.md                  # This file
```

---

## 🚀 Quick Start (Development)

### Prerequisites

- Node.js 18+
- Python 3.11+
- Google Cloud CLI
- Firebase project

### 1. Frontend (Local)

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your Firebase config and API URL
npm run dev
# Open http://localhost:3000
```

### 2. API (Local)

```bash
cd api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env with your credentials
uvicorn app.main:app --reload
# API runs on http://localhost:8000
```

### 3. Worker (Local)

```bash
cd worker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
# Edit .env with your credentials
python main.py
# Worker runs on http://localhost:8001
```

**For detailed testing instructions, see:** [`docs/development/TESTING_GUIDE.md`](docs/development/TESTING_GUIDE.md)

---

## 📦 Production Deployment

### Infrastructure Setup

1. **GCP Setup**
   - Enable Cloud Build, Cloud Run, Secret Manager, Firestore, Storage
   - See: [`docs/setup/CLOUD_BUILD_SETUP.md`](docs/setup/CLOUD_BUILD_SETUP.md)

2. **Secrets Configuration**
   - Add Stripe keys, API keys to Secret Manager
   - See: [`docs/setup/SECRET_MANAGER_SETUP.md`](docs/setup/SECRET_MANAGER_SETUP.md)

3. **Custom Domain**
   - Configure Cloudflare DNS + Vercel
   - See: [`docs/setup/CUSTOM_DOMAIN_SETUP.md`](docs/setup/CUSTOM_DOMAIN_SETUP.md)

4. **GitHub Protection** (Optional)
   - Branch protection, CODEOWNERS
   - See: [`docs/setup/GITHUB_PROTECTION_SETUP.md`](docs/setup/GITHUB_PROTECTION_SETUP.md)

### Deploy Workflow

```bash
# 1. Push to main → triggers Cloud Build for API + Worker
git push origin main

# 2. Frontend deploys automatically via Vercel
# (connected to GitHub repo)

# 3. Verify deployment
gcloud run services list
```

---

## 💳 Stripe Configuration

### Test Mode (Development)
- Use test API keys (sk_test_...)
- Test card: 4242 4242 4242 4242

### Production Mode
- Switch to live keys (sk_live_...)
- Create products: $2.99 (1 credit), $12.99 (5 credits), $19.99 (10 credits)
- Configure webhook: `https://[API_URL]/api/webhooks/stripe`
- Listen for: `checkout.session.completed`

See: [`docs/development/STRIPE_TESTING.md`](docs/development/STRIPE_TESTING.md)

---

## 🧪 Testing

### End-to-End Test Flow

1. Visit https://miniaura.aurafarmer.co
2. Sign up with email or Google
3. Upload a photo
4. Generate avatar (uses 1 free credit)
5. Customize position/size/rotation
6. Download high-res PNG
7. Purchase credits via Stripe
8. Generate premium avatar (no watermark)

### Test Files

- **Local API tests:** `api/test_credit_system.py`
- **Worker AI tests:** `worker/test_ai_integration.py`

---

## 📚 Documentation Index

### Setup & Deployment
- [Cloud Build Setup](docs/setup/CLOUD_BUILD_SETUP.md) - CI/CD pipeline configuration
- [Secret Manager Setup](docs/setup/SECRET_MANAGER_SETUP.md) - Managing API keys & secrets
- [Custom Domain Setup](docs/setup/CUSTOM_DOMAIN_SETUP.md) - Cloudflare + Vercel DNS
- [GitHub Protection](docs/setup/GITHUB_PROTECTION_SETUP.md) - Branch protection rules

### Development & Testing
- [Testing Guide](docs/development/TESTING_GUIDE.md) - Comprehensive testing instructions
- [Local Testing](docs/development/LOCAL_TESTING.md) - Run services locally
- [Quick Start Testing](docs/development/QUICK_START_TESTING.md) - Fast setup for testing
- [Stripe Testing](docs/development/STRIPE_TESTING.md) - Payment flow testing

### Component Documentation
- [Frontend README](frontend/README.md) - Next.js app structure
- [Worker AI Testing](worker/LOCAL_TESTING_AI.md) - Test AI pipeline locally

---

## 🔒 Security

- Firebase Auth tokens required for all API endpoints
- Rate limiting: 10 requests/minute on `/api/generate`
- Stripe webhook signature verification
- GCS CORS restricted to production domains
- Secrets stored in GCP Secret Manager (never in code)

---

## 📊 Monitoring

- **API Logs:** Cloud Run → Logs
- **Payments:** Stripe Dashboard → Payments
- **Storage:** GCS Console → Buckets
- **Users:** Firebase Console → Authentication

---

## 🐛 Troubleshooting

### Common Issues

**"CORS error on image download"**
```bash
# Apply CORS config to GCS buckets
./setup-gcs-cors.sh
```

**"Payment completed but credits not added"**
- Check Cloud Run logs for webhook errors
- Verify webhook secret in Secret Manager
- Check Stripe webhook delivery attempts

**"Avatar generation fails"**
- Check Claude API key quota
- Verify Imagen API is enabled
- Check worker logs in Cloud Run

---

## 📝 License

MIT License - see LICENSE file

---

## 🤝 Contributing

This is a personal project, but issues and PRs are welcome!

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Submit a PR

---

## 🔗 Links

- **Live Site:** https://miniaura.aurafarmer.co
- **Stripe Dashboard:** https://dashboard.stripe.com
- **GCP Console:** https://console.cloud.google.com
- **Firebase Console:** https://console.firebase.google.com
- **Vercel Dashboard:** https://vercel.com/dashboard

---

Built with ❤️ by J3r3my97
