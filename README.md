# Mini-Me: AI Pixel Art Avatar Generator

Turn yourself into pixel art—instantly.

## Project Structure

```
mini-aura/
├── api/                 # FastAPI backend service
│   ├── app/
│   │   ├── main.py     # Main API application
│   │   ├── routes/     # API route handlers
│   │   ├── models/     # Pydantic models
│   │   └── utils/      # Helper functions
│   ├── Dockerfile
│   └── requirements.txt
│
├── worker/              # Background job processor
│   ├── main.py         # Worker service
│   ├── pipeline.py     # Image processing pipeline
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/            # Next.js web application
│   └── (to be created)
│
└── README.md
```

## Tech Stack

- **Backend:** Python 3.11, FastAPI
- **Frontend:** Next.js 14, React, TypeScript, Tailwind CSS (Neumorphism design)
- **Authentication:** Firebase Auth (Email/Password + Google OAuth)
- **Infrastructure:** Google Cloud Platform
- **AI:** Claude Haiku 4, Google Imagen 3

## Local Development

### Backend Services

```bash
# API Service
cd api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Worker Service
cd worker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### Frontend (Next.js)

```bash
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev
# Open http://localhost:3000
```

**Full setup guide:** See [`frontend/SETUP.md`](frontend/SETUP.md) for detailed instructions on Firebase auth, API integration, and deployment.

## Features

✅ **AI Avatar Generation** - Transform photos into pixel art with Google Imagen 3
✅ **Firebase Authentication** - Email/password and Google OAuth sign-in
✅ **Neumorphic UI** - Premium soft UI design with tactile interactions
✅ **Real-time Processing** - Job status polling with progress updates
✅ **Responsive Design** - Works on desktop, tablet, and mobile
✅ **Secure API** - Firebase token authentication on all endpoints
✅ **Usage Limits** - Tiered access (Free, Pro, One-time)
