# Mini-Me Frontend Setup Guide

Complete setup guide for the Mini-Me Next.js 14 frontend with Firebase auth and API integration.

## 📋 Prerequisites

- Node.js 18+ and npm 9+
- Firebase project configured (already set up in `../firebase_config.js`)
- Backend API running on `http://localhost:8000`

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Variables

The `.env.local` file is already configured with your Firebase credentials. If you need to modify:

```bash
cp .env.local.example .env.local
# Edit .env.local with your values
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Start Backend API

In another terminal:

```bash
cd ../api
source venv/bin/activate
uvicorn app.main:app --reload
```

The frontend expects the API at `http://localhost:8000`.

## 📁 Project Structure

```
frontend/
├── app/                          # Next.js 14 App Router
│   ├── layout.tsx               # Root layout with AuthProvider
│   └── page.tsx                 # Main landing page
│
├── components/                   # React components
│   ├── auth/
│   │   ├── SignInModal.tsx      # Email/Google sign-in
│   │   └── SignUpModal.tsx      # User registration
│   └── components.tsx           # Reusable Neumorphic UI components
│
├── contexts/                     # React contexts
│   └── AuthContext.tsx          # Firebase auth state management
│
├── lib/                          # Utilities and configurations
│   ├── firebase.ts              # Firebase client SDK setup
│   └── api.ts                   # API client with auth interceptors
│
├── globals.css                   # Global styles + Neumorphic design system
├── tailwind.config.ts           # Tailwind configuration
├── tsconfig.json                # TypeScript configuration
├── next.config.js               # Next.js configuration
└── package.json                 # Dependencies
```

## 🔐 Firebase Authentication

### Configured Methods

1. **Email/Password** - Standard email registration and login
2. **Google OAuth** - One-click Google sign-in

### Authentication Flow

```typescript
// Sign in with email
import { signInWithEmail } from '@/lib/firebase';
const { user, error } = await signInWithEmail(email, password);

// Sign in with Google
import { signInWithGoogle } from '@/lib/firebase';
const { user, error } = await signInWithGoogle();

// Sign out
import { logout } from '@/lib/firebase';
await logout();

// Get auth token for API calls (handled automatically)
import { getIdToken } from '@/lib/firebase';
const token = await getIdToken();
```

### Using Auth Context

```typescript
import { useAuth } from '@/contexts/AuthContext';

function MyComponent() {
  const { user, loading, logout } = useAuth();

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>Please sign in</div>;

  return <div>Welcome, {user.email}</div>;
}
```

## 🌐 API Integration

### API Client (`lib/api.ts`)

Automatically handles:
- Firebase auth token injection
- Request/response interceptors
- Error handling and redirects

### Available Methods

```typescript
import api from '@/lib/api';

// Generate avatar
const response = await api.generateAvatar(file);
// Returns: { job_id, status, message }

// Check job status
const job = await api.getJobStatus(jobId);
// Returns: { job_id, status, output_image_url, ... }

// Poll until complete
const finalJob = await api.pollJobStatus(
  jobId,
  (update) => console.log(update), // Progress callback
  60,    // Max attempts
  2000   // Interval (ms)
);

// Get user's job history
const { jobs, total } = await api.getUserJobs(10);
```

### API Flow in Action

```typescript
// 1. User uploads image
const file = event.target.files[0];

// 2. Generate avatar (requires auth)
const { job_id } = await api.generateAvatar(file);

// 3. Poll for completion
const job = await api.pollJobStatus(job_id, (update) => {
  console.log(`Status: ${update.status}`);
});

// 4. Display result
if (job.status === 'completed') {
  console.log('Avatar URL:', job.output_image_url);
}
```

## 🎨 Neumorphism Design System

### Core Components

```typescript
import {
  NeuButton,
  NeuCard,
  NeuInput,
  NeuToggle,
  NeuLoader,
  FeatureCard,
  PricingCard
} from '@/components/components';

// Usage
<NeuButton variant="accent">Click Me</NeuButton>
<NeuCard>Content here</NeuCard>
<NeuInput label="Email" placeholder="Enter email..." />
```

### Color Palette

```css
--bg-primary: #e6e7f0      /* Soft lavender */
--bg-secondary: #f0f1f7     /* Lighter lavender */
--shadow-light: #ffffff     /* Highlight shadow */
--shadow-dark: #c8c9d4      /* Depth shadow */
--accent: #8b7fc7           /* Purple accent */
--accent-deep: #6b5eb0      /* Deep purple */
```

### CSS Classes

```html
<!-- Buttons -->
<button class="neu-button">Default</button>
<button class="neu-button-accent">Accent</button>

<!-- Cards -->
<div class="neu-card">Card content</div>

<!-- Inputs -->
<input class="neu-input" placeholder="Text..." />

<!-- Upload Zone -->
<div class="upload-zone">Drop files here</div>
```

## 🧪 Testing Locally

### 1. Test Authentication

1. Click "Sign In" button
2. Create account with email/password or Google
3. Verify you're signed in (email shown in header)

### 2. Test Avatar Generation

1. Sign in first
2. Drag-drop or click upload zone
3. Select an image (JPG/PNG, < 10MB)
4. Wait for processing (5-10 seconds)
5. Download result

### 3. Check API Connection

```bash
# Terminal 1: API should be running
curl http://localhost:8000/health
# Should return: {"status":"ok"}

# Terminal 2: Frontend dev server
npm run dev
# Open http://localhost:3000
```

## 🚀 Production Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel

# Add environment variables in Vercel dashboard:
# - NEXT_PUBLIC_FIREBASE_* (all Firebase config)
# - NEXT_PUBLIC_API_URL=https://your-api-domain.com
```

### Build Locally

```bash
npm run build
npm start
```

## 🐛 Troubleshooting

### "Failed to generate avatar"

**Cause:** Backend API not running or CORS issue

**Fix:**
```bash
# Check API is running
curl http://localhost:8000/health

# Check API logs
cd ../api
tail -f logs/api.log
```

### "Authorization required"

**Cause:** Firebase auth token not being sent

**Fix:**
1. Sign out and sign in again
2. Check browser console for errors
3. Verify `.env.local` has correct Firebase config

### Images not loading

**Cause:** Next.js image optimization requires domains to be whitelisted

**Fix:** Check `next.config.js` has:
```javascript
images: {
  remotePatterns: [
    { hostname: 'images.unsplash.com' },
    { hostname: 'storage.googleapis.com' }
  ]
}
```

### "Module not found" errors

**Cause:** Missing dependencies or wrong import paths

**Fix:**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Verify TypeScript paths
npm run type-check
```

## 📊 Key Features Implemented

✅ **Firebase Authentication**
- Email/password registration and login
- Google OAuth sign-in
- Persistent auth state
- Auto token refresh

✅ **API Integration**
- Automatic auth token injection
- File upload with FormData
- Job status polling
- Error handling

✅ **Upload Flow**
- Drag-and-drop support
- File validation (type, size)
- Real-time status updates
- Result preview and download

✅ **Neumorphic UI**
- Soft shadows and depth
- Smooth animations
- Responsive design
- Accessible components

✅ **User Experience**
- Auth-gated generation
- Loading states
- Error messages
- Success feedback

## 🔗 API Endpoints Used

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/api/generate` | POST | ✅ | Upload image and create generation job |
| `/api/jobs/{job_id}` | GET | ✅ | Get job status and result URL |
| `/api/jobs` | GET | ✅ | List user's job history |
| `/health` | GET | ❌ | Health check |

## 📝 Environment Variables Reference

```bash
# Firebase (required)
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-bucket
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=app-id

# API (required)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Environment (optional)
NEXT_PUBLIC_ENV=development
```

## 🎯 Next Steps

1. **Add Payment Integration** - Stripe for Pro subscriptions
2. **Job History Page** - View past generations
3. **Social Sharing** - Share directly to Twitter, Instagram
4. **Download Options** - Multiple formats (PNG, SVG, animated GIF)
5. **Advanced Customization** - Style selection, color adjustments

## 📚 Additional Resources

- [Next.js 14 Documentation](https://nextjs.org/docs)
- [Firebase Auth Guide](https://firebase.google.com/docs/auth/web/start)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [React Hooks](https://react.dev/reference/react)

---

**Built with Neumorphism aesthetics** — Soft, tactile, premium. 🎨
