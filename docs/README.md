# Documentation

This directory contains all documentation for Mini-Aura.

## 📁 Directory Structure

```
docs/
├── setup/          # Production deployment & configuration guides
├── development/    # Local development & testing documentation
├── archive/        # Historical/deprecated documents
└── README.md       # This file
```

---

## 🚀 Setup & Deployment

**Start here for production deployment:**

- **[Cloud Build Setup](setup/CLOUD_BUILD_SETUP.md)** - Configure CI/CD pipeline with Google Cloud Build
- **[Secret Manager Setup](setup/SECRET_MANAGER_SETUP.md)** - Store API keys and secrets securely in GCP
- **[Custom Domain Setup](setup/CUSTOM_DOMAIN_SETUP.md)** - Connect your domain (Cloudflare + Vercel)
- **[GitHub Protection](setup/GITHUB_PROTECTION_SETUP.md)** - Set up branch protection and code review

---

## 🛠️ Development & Testing

**Guides for local development:**

- **[Testing Guide](development/TESTING_GUIDE.md)** - Comprehensive testing instructions (end-to-end)
- **[Local Testing](development/LOCAL_TESTING.md)** - Run API and worker services locally
- **[Quick Start Testing](development/QUICK_START_TESTING.md)** - Fast setup for testing credit system
- **[Stripe Testing](development/STRIPE_TESTING.md)** - Test payment flows (test mode)

---

## 📦 Component-Specific Docs

- **Frontend:** See [frontend/README.md](../frontend/README.md)
- **Worker AI:** See [worker/LOCAL_TESTING_AI.md](../worker/LOCAL_TESTING_AI.md)

---

## 🗂️ Archive

The `archive/` folder contains outdated or historical documents that are kept for reference:
- Engineering design docs
- Old product requirements (Mini-Me → Mini-Aura rebrand)
- Deprecated setup guides

---

## 🔗 Quick Links

- **Main README:** [../README.md](../README.md)
- **Live Site:** https://miniaura.aurafarmer.co
- **API Docs:** (Auto-generated at `/docs` endpoint when API is running)

---

**Need help?** Check the main [README](../README.md) or the troubleshooting section.
