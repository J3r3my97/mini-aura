# ⚡ Mini-Me Frontend — Quick Start

## ✅ Installation Complete!

All dependencies installed successfully. TypeScript checks passed. Ready to run!

---

## 🚀 Start Development Server

```bash
cd frontend
npm run dev
```

Open **http://localhost:3000** in your browser.

---

## 🔧 Prerequisites Checklist

Before starting the frontend, ensure:

- [ ] **Backend API is running** on `http://localhost:8000`
  ```bash
  # In another terminal
  cd api
  source venv/bin/activate
  uvicorn app.main:app --reload
  ```

- [ ] **Environment variables are set** (already configured in `.env.local`)

- [ ] **Node.js 18+** is installed
  ```bash
  node --version  # Should show v18+ or v20+
  ```

---

## 🎯 Test the Complete Flow

1. **Start backend API** (Terminal 1)
   ```bash
   cd api
   uvicorn app.main:app --reload
   ```

2. **Start frontend** (Terminal 2)
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open browser** → http://localhost:3000

4. **Test authentication:**
   - Click "Sign In"
   - Sign up with email or Google
   - Verify you're signed in (email shown in header)

5. **Test avatar generation:**
   - Upload an image (drag-drop or click)
   - Wait ~5-10 seconds
   - Download result

---

## 📦 Available Scripts

```bash
npm run dev        # Start dev server (port 3000)
npm run build      # Build for production
npm run start      # Start production server
npm run lint       # Run ESLint
npm run type-check # Run TypeScript checks
```

---

## 🔥 Quick Troubleshooting

### Issue: "Failed to generate avatar"
**Fix:** Make sure backend API is running on port 8000
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok"}
```

### Issue: "Authorization required"
**Fix:** Sign out and sign in again. Check Firebase config in `.env.local`

### Issue: Port 3000 already in use
**Fix:**
```bash
# Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use a different port
npm run dev -- -p 3001
```

### Issue: Type errors or missing modules
**Fix:**
```bash
rm -rf node_modules package-lock.json .next
npm install
```

---

## 🌐 API Endpoints Being Used

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/generate` | Upload image, create job | Requires auth token |
| `GET /api/jobs/{job_id}` | Get job status & result | Requires auth token |
| `GET /health` | Health check | Public |

---

## 🎨 Design System Quick Reference

### Color Variables (globals.css)
```css
--bg-primary: #e6e7f0     /* Soft lavender background */
--accent: #8b7fc7         /* Purple accent */
--shadow-dark: #c8c9d4    /* Shadow for depth */
--shadow-light: #ffffff   /* Shadow for highlights */
```

### Component Classes
```html
<button class="neu-button">Button</button>
<button class="neu-button-accent">Accent Button</button>
<div class="neu-card">Card</div>
<input class="neu-input" />
```

### Component Library (`components.tsx`)
```typescript
import { NeuButton, NeuCard, NeuInput, NeuLoader } from '@/components/components';

<NeuButton variant="accent">Click Me</NeuButton>
<NeuCard>Content</NeuCard>
<NeuLoader text="Processing..." />
```

---

## 📖 Full Documentation

- **Complete Setup:** [`SETUP.md`](./SETUP.md)
- **Implementation Details:** [`PROJECT_SUMMARY.md`](./PROJECT_SUMMARY.md)
- **Design System:** [`README.md`](./README.md)

---

## 🎉 You're Ready!

Everything is installed and configured. Just run:

```bash
npm run dev
```

And start generating pixel art avatars! 🚀

**Need help?** Check the troubleshooting section above or see `SETUP.md`.
