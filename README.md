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
- **Frontend:** Next.js 14, Tailwind CSS
- **Infrastructure:** Google Cloud Platform
- **AI:** Claude Haiku 4, Google Imagen 3

## Local Development

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
