# Engineering Design Document - Mini-Me MVP

**Version:** 1.0
**Date:** December 10, 2025
**Status:** Ready for Implementation

---

## Tech Stack (Final Decisions)

### Frontend
- **Framework:** Next.js 14 (App Router)
- **Styling:** Tailwind CSS
- **State:** React Query + Context API
- **Canvas:** Fabric.js (drag/resize)
- **Auth:** Firebase Auth SDK
- **Deployment:** Vercel or GCS + Cloud CDN

### Backend
- **Runtime:** Python 3.11+
- **Framework:** FastAPI
- **Task Queue:** Google Pub/Sub
- **Image Processing:** Pillow, rembg (U2Net)
- **Deployment:** Cloud Run (containerized)

### Infrastructure (GCP)
- **Compute:** Cloud Run (API + Worker)
- **Storage:** Cloud Storage (images)
- **Database:** Firestore
- **Queue:** Pub/Sub
- **Auth:** Firebase Auth

### AI Models
- **Background Removal:** rembg (U2Net model)
- **Image Analysis + Prompt:** Claude Haiku 4 (fast, cheap)
- **Pixel Art Generation:** Google Imagen 3 (standard quality)

### Third-Party
- **Payments:** Stripe
- **Email:** SendGrid

---

## System Architecture

```
┌─────────────────────────────────────────────┐
│  Next.js Frontend (Vercel/GCS)              │
│  - Landing, Upload, Result UI               │
│  - Firebase Auth SDK                        │
└──────────────────┬──────────────────────────┘
                   │ HTTPS/REST
                   ↓
┌─────────────────────────────────────────────┐
│  API Service (Cloud Run - FastAPI)          │
│  - /api/auth/* (Firebase verify)            │
│  - /api/generate (upload → Pub/Sub)         │
│  - /api/jobs/{id} (status polling)          │
│  - /api/subscription/* (Stripe)             │
└──────┬──────────┬──────────┬────────────────┘
       │          │          │
       ↓          ↓          ↓
   ┌───────┐  ┌──────┐  ┌──────────┐
   │  GCS  │  │Pub/Sub│ │Firestore │
   │Bucket │  │ Queue │ │    DB    │
   └───────┘  └───┬──┘  └──────────┘
                  │
                  ↓
┌─────────────────────────────────────────────┐
│  Worker Service (Cloud Run - Python)        │
│  1. Download image from GCS                 │
│  2. Background removal (rembg)              │
│  3. Claude Haiku: Analyze image             │
│  4. Claude Haiku: Generate Imagen prompt    │
│  5. Imagen 3: Generate pixel art            │
│  6. Composite images (Pillow)               │
│  7. Upload to GCS                           │
│  8. Update Firestore (complete)             │
└─────────────────────────────────────────────┘
```

---

## Database Schemas (Firestore)

### Collection: `users`
```python
{
    "user_id": str,           # Firebase UID
    "email": str,
    "created_at": datetime,
    "subscription_tier": str, # "free|starter|creator|pro"
    "usage_count": int,       # Total generations
    "usage_limit": int,       # Based on tier
    "stripe_customer_id": str | None,
    "last_login": datetime
}
```

### Collection: `jobs`
```python
{
    "job_id": str,            # UUID
    "user_id": str,           # Foreign key
    "status": str,            # "queued|processing|completed|failed"
    "created_at": datetime,
    "completed_at": datetime | None,
    "input_image_url": str,   # gs://bucket/uploads/{job_id}.jpg
    "output_image_url": str | None,  # gs://bucket/results/{job_id}.png
    "processing_time_ms": int | None,
    "error_message": str | None,
    "metadata": {
        "detected_colors": list[str],
        "generated_prompt": str,
        "style": str  # "lego" (only option in MVP)
    }
}
```

### Collection: `subscriptions`
```python
{
    "subscription_id": str,
    "user_id": str,
    "stripe_subscription_id": str,
    "tier": str,              # "starter|creator|pro"
    "status": str,            # "active|cancelled|past_due"
    "current_period_start": datetime,
    "current_period_end": datetime,
    "cancel_at_period_end": bool
}
```

---

## Core API Endpoints

### Authentication
```
POST /api/auth/register
  Body: { email, password }
  Returns: { user_id, token }

POST /api/auth/login
  Body: { email, password }
  Returns: { user_id, token }

GET /api/auth/me
  Headers: Authorization: Bearer {firebase_token}
  Returns: User object
```

### Generation
```
POST /api/generate
  Headers: Authorization: Bearer {token}
  Body: multipart/form-data { image: File }
  Returns: { job_id, status: "queued" }

  Logic:
  1. Verify user auth
  2. Check usage limit (user.usage_count < user.usage_limit)
  3. Upload image to GCS: gs://mini-me-uploads/{job_id}.jpg
  4. Create job in Firestore (status=queued)
  5. Publish to Pub/Sub topic "generation-jobs"
  6. Increment user.usage_count
  7. Return job_id

GET /api/jobs/{job_id}
  Headers: Authorization: Bearer {token}
  Returns: { job_id, status, output_image_url?, error_message? }

  Logic:
  1. Verify user owns job (job.user_id == user.user_id)
  2. Return job document from Firestore
  3. If status=completed, return signed URL (15min expiry)

GET /api/jobs
  Headers: Authorization: Bearer {token}
  Query: ?limit=20&offset=0
  Returns: { jobs: [...], total: int }
```

### Subscription
```
POST /api/subscription/create-checkout
  Headers: Authorization: Bearer {token}
  Body: { tier: "starter|creator|pro" }
  Returns: { checkout_url: str }

  Logic:
  1. Get or create Stripe customer
  2. Create Stripe Checkout Session
  3. Return checkout URL

POST /api/webhooks/stripe
  Headers: stripe-signature
  Body: Stripe webhook event
  Returns: { received: true }

  Events to handle:
  - checkout.session.completed → Create subscription in DB
  - customer.subscription.updated → Update subscription status
  - customer.subscription.deleted → Mark as cancelled
```

---

## Worker Pipeline (Detailed)

### Worker Service Entry Point
```python
# worker/main.py

@app.post("/process")  # Cloud Run receives Pub/Sub push
async def process_generation(request: Request):
    """
    Receives Pub/Sub message with job_id.
    Processes generation end-to-end.
    """
    # 1. Parse Pub/Sub message
    envelope = await request.json()
    job_id = base64.b64decode(envelope['message']['data']).decode()

    # 2. Update job status
    await update_job_status(job_id, "processing")

    try:
        # 3. Execute pipeline
        result = await run_pipeline(job_id)

        # 4. Mark complete
        await update_job_status(
            job_id,
            "completed",
            output_url=result['output_url'],
            metadata=result['metadata']
        )
    except Exception as e:
        # 5. Mark failed
        await update_job_status(job_id, "failed", error=str(e))
        raise

    return {"status": "ok"}
```

### Pipeline Steps

```python
async def run_pipeline(job_id: str) -> dict:
    """Main processing pipeline"""
    start_time = time.time()

    # STEP 1: Download input image
    input_path = await download_from_gcs(
        bucket="mini-me-uploads",
        blob_name=f"{job_id}.jpg",
        local_path=f"/tmp/{job_id}_input.jpg"
    )

    # STEP 2: Remove background (rembg)
    # Takes ~2-3s, output has transparent background
    no_bg_path = await remove_background(input_path)

    # STEP 3: Analyze image with Claude Haiku
    # Detect: clothing colors, pose, accessories, hair color, etc.
    analysis = await analyze_with_claude(no_bg_path)
    # Returns: {
    #   "primary_colors": ["#FF6600", "#000000"],
    #   "pose": "standing front-facing",
    #   "clothing": "orange hoodie",
    #   "accessories": ["glasses"],
    #   "hair_color": "brown"
    # }

    # STEP 4: Generate Imagen prompt with Claude Haiku
    # Convert analysis into detailed Imagen prompt
    prompt = await generate_imagen_prompt(analysis)
    # Returns: "isometric pixel art voxel style character,
    #           orange hoodie, black pants, brown hair, glasses,
    #           standing pose, LEGO minifigure aesthetic,
    #           clean simple design, white background"

    # STEP 5: Generate pixel art with Imagen 3
    # Takes ~10-15s for standard quality
    pixel_art_path = await generate_with_imagen(prompt)

    # STEP 6: Composite images
    # Place mini-me on bottom-right of original (default position)
    composite_path = await composite_images(
        background=input_path,
        foreground=pixel_art_path,
        position="bottom-right",  # x=80%, y=80%
        scale=0.3  # Mini-me is 30% of image height
    )

    # STEP 7: Add watermark (if free tier)
    user = await get_user_for_job(job_id)
    if user['subscription_tier'] == 'free':
        composite_path = await add_watermark(
            composite_path,
            text="mini-me",
            position="bottom-left"
        )

    # STEP 8: Upload result to GCS
    output_url = await upload_to_gcs(
        local_path=composite_path,
        bucket="mini-me-results",
        blob_name=f"{job_id}.png"
    )

    processing_time = int((time.time() - start_time) * 1000)

    return {
        "output_url": output_url,
        "metadata": {
            "detected_colors": analysis['primary_colors'],
            "generated_prompt": prompt,
            "style": "lego",
            "processing_time_ms": processing_time
        }
    }
```

### Helper Functions

```python
# Background Removal
async def remove_background(input_path: str) -> str:
    """Remove background using rembg (U2Net model)"""
    from rembg import remove
    from PIL import Image

    input_img = Image.open(input_path)
    output_img = remove(input_img)  # ~2-3 seconds

    output_path = input_path.replace("_input", "_nobg")
    output_img.save(output_path)
    return output_path

# Claude Analysis
async def analyze_with_claude(image_path: str) -> dict:
    """Analyze image with Claude Haiku (vision)"""
    import anthropic
    import base64

    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    # Read image as base64
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode()

    response = client.messages.create(
        model="claude-haiku-4-20250514",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_b64
                    }
                },
                {
                    "type": "text",
                    "text": """Analyze this person's appearance for creating a pixel art avatar.

                    Return JSON with:
                    - primary_colors: array of 2-3 hex colors from clothing
                    - pose: describe their pose (e.g. "standing", "sitting")
                    - clothing: brief description
                    - accessories: array (glasses, hat, etc.)
                    - hair_color: color name

                    Only JSON, no explanation."""
                }
            ]
        }]
    )

    # Parse JSON from response
    import json
    return json.loads(response.content[0].text)

# Imagen Prompt Generation
async def generate_imagen_prompt(analysis: dict) -> str:
    """Generate Imagen prompt from Claude analysis"""
    import anthropic

    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    response = client.messages.create(
        model="claude-haiku-4-20250514",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"""Convert this analysis into a Google Imagen prompt for pixel art:

{json.dumps(analysis, indent=2)}

Create a prompt for: isometric voxel/LEGO style pixel art character.
Keep it concise, focused on visual details.
Format: single paragraph, no line breaks.
Only the prompt, no explanation."""
        }]
    )

    return response.content[0].text.strip()

# Imagen Generation
async def generate_with_imagen(prompt: str) -> str:
    """Generate pixel art with Google Imagen 3"""
    from google.cloud import aiplatform
    from vertexai.preview.vision_models import ImageGenerationModel

    model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")

    response = model.generate_images(
        prompt=prompt,
        number_of_images=1,
        aspect_ratio="1:1",
        safety_filter_level="block_some",
        person_generation="allow_adult"
    )

    # Save first image
    output_path = f"/tmp/{uuid.uuid4()}_pixel.png"
    response.images[0].save(output_path)
    return output_path

# Image Compositing
async def composite_images(
    background: str,
    foreground: str,
    position: str = "bottom-right",
    scale: float = 0.3
) -> str:
    """Composite mini-me onto original photo"""
    from PIL import Image

    bg = Image.open(background).convert("RGBA")
    fg = Image.open(foreground).convert("RGBA")

    # Resize foreground (mini-me) to 30% of background height
    new_height = int(bg.height * scale)
    aspect = fg.width / fg.height
    new_width = int(new_height * aspect)
    fg = fg.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Calculate position (default: bottom-right with 5% margin)
    if position == "bottom-right":
        x = int(bg.width * 0.95 - fg.width)
        y = int(bg.height * 0.95 - fg.height)

    # Paste with alpha channel
    bg.paste(fg, (x, y), fg)

    output_path = background.replace("_input", "_composite")
    bg.save(output_path)
    return output_path
```

---

## Frontend Key Components

### Upload Page
```typescript
// app/generate/page.tsx

export default function GeneratePage() {
  const [uploading, setUploading] = useState(false);
  const [jobId, setJobId] = useState<string | null>(null);

  const handleUpload = async (file: File) => {
    setUploading(true);

    const formData = new FormData();
    formData.append('image', file);

    const response = await fetch('/api/generate', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${await getAuthToken()}`
      },
      body: formData
    });

    const data = await response.json();
    setJobId(data.job_id);

    // Redirect to polling page
    router.push(`/generate/${data.job_id}`);
  };

  return (
    <Dropzone onDrop={handleUpload}>
      {/* Upload UI */}
    </Dropzone>
  );
}
```

### Status Polling Page
```typescript
// app/generate/[jobId]/page.tsx

export default function JobStatusPage({ params }: { params: { jobId: string } }) {
  const { data, isLoading } = useQuery({
    queryKey: ['job', params.jobId],
    queryFn: () => fetchJobStatus(params.jobId),
    refetchInterval: (data) => {
      // Poll every 2 seconds if still processing
      return data?.status === 'completed' ? false : 2000;
    }
  });

  if (data?.status === 'completed') {
    return <ResultDisplay jobId={params.jobId} imageUrl={data.output_image_url} />;
  }

  return <ProgressAnimation status={data?.status} />;
}
```

---

## Deployment Configuration

### API Service (Cloud Run)
```yaml
# api/cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/mini-me/api:$SHORT_SHA', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/mini-me/api:$SHORT_SHA']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'mini-me-api'
      - '--image=gcr.io/mini-me/api:$SHORT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--memory=512Mi'
      - '--cpu=1'
      - '--min-instances=0'
      - '--max-instances=10'
      - '--concurrency=80'
      - '--allow-unauthenticated'
```

### Worker Service (Cloud Run)
```yaml
# worker/cloudbuild.yaml
# Similar structure but:
# --memory=2Gi (for rembg model)
# --cpu=2
# --timeout=300s (5 min max)
# --no-allow-unauthenticated (internal only)
```

### Environment Variables
```bash
# API Service
FIREBASE_PROJECT_ID=mini-me-prod
STRIPE_SECRET_KEY=sk_live_xxx
PUBSUB_TOPIC=generation-jobs
GCS_UPLOAD_BUCKET=mini-me-uploads
GCS_RESULT_BUCKET=mini-me-results

# Worker Service
CLAUDE_API_KEY=sk-ant-xxx
GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json
FIRESTORE_DATABASE=mini-me-prod
```

---

## Cost Estimates (Per Generation)

```
Background Removal (rembg): $0.00 (self-hosted)
Claude Haiku (2 calls):     $0.002 (~1K tokens each)
Imagen 3 (standard):        $0.04 (per image)
Cloud Run (API):            $0.0001
Cloud Run (Worker):         $0.001 (2GB mem, 20s)
GCS Storage:                $0.0001
Pub/Sub:                    $0.00001
--------------------------------------------------
Total per generation:       ~$0.043

With 20% margin:            $0.052 per generation

Pricing strategy:
- Free tier: 5 images = $0.26 cost → Acquire users
- Starter: 20 images for $4.99 = $0.25/image revenue → $4.99 - $1.04 = $3.95 profit (79% margin)
- Creator: 100 images for $9.99 = $0.10/image revenue → $9.99 - $5.20 = $4.79 profit (48% margin)
```

---

## Implementation Order

### Week 1: Backend Foundation
1. GCP project setup (Cloud Run, Firestore, GCS, Pub/Sub)
2. API service skeleton (FastAPI + auth middleware)
3. Firestore schemas + helper functions
4. Firebase Auth integration
5. `/api/generate` endpoint (upload → Pub/Sub)
6. `/api/jobs/{id}` endpoint (status polling)

### Week 2: Worker Pipeline
1. Worker service skeleton (FastAPI receiver)
2. Pub/Sub subscription → Worker endpoint
3. Background removal integration (rembg)
4. Claude Haiku integration (analysis + prompt)
5. Imagen 3 integration
6. Image compositing (Pillow)
7. End-to-end pipeline test

### Week 3: Frontend
1. Next.js project setup + Tailwind
2. Landing page (static)
3. Upload interface (drag & drop + camera)
4. Progress polling page (React Query)
5. Result display (canvas with drag/resize)
6. Export functionality

### Week 4: Monetization + Polish
1. Stripe integration (checkout + webhooks)
2. Usage tracking + limits
3. Watermark on free tier
4. Upgrade prompts
5. Error handling + retry logic
6. Deploy to production
7. Testing + bug fixes

---

## Next Steps

1. Create GitHub repo
2. Setup GCP project
3. Start with API service (Week 1)
4. Create `/api/generate` endpoint
5. Test image upload → GCS flow

Ready to start coding?
