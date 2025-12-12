# Mini-Me Frontend — Neumorphism UI

A **premium Neumorphism-style** frontend interface for the Mini-Me AI Pixel Art Avatar Generator.

## 🎨 Design System

### Aesthetic: Neumorphism (Soft UI)
Complete commitment to the soft, tactile, embossed aesthetic that feels like physical materials.

### Color Palette
**Monochromatic Soft Lavender**
- Primary Background: `#e6e7f0` (Soft lavender-gray)
- Secondary Background: `#f0f1f7` (Lighter lavender)
- Light Shadow: `#ffffff` (Pure white highlights)
- Dark Shadow: `#c8c9d4` (Soft shadow)
- Accent: `#8b7fc7` (Muted purple)
- Deep Accent: `#6b5eb0` (Rich purple)
- Text Primary: `#4a4a5e` (Dark slate)
- Text Secondary: `#7a7a8e` (Medium slate)

### Typography
**Font:** Plus Jakarta Sans (Google Fonts)
- Modern, rounded sans-serif perfect for soft UI
- Weight range: 300-800 for hierarchy
- No default system fonts

### Neumorphic Shadow System

#### Convex (Raised Elements)
```css
box-shadow: 8px 8px 16px #c8c9d4,
           -8px -8px 16px #ffffff;
```
Used for: Cards, buttons at rest, prominent elements

#### Concave (Pressed/Inset Elements)
```css
box-shadow: inset 6px 6px 12px #c8c9d4,
           inset -6px -6px 12px #ffffff;
```
Used for: Input fields, pressed states, recessed areas

#### Flat (Subtle Elevation)
```css
box-shadow: 4px 4px 8px #c8c9d4,
           -4px -4px 8px #ffffff;
```
Used for: Hover states, subtle elevation changes

## ✨ Signature Details

### 1. Multi-Layer Soft Shadows
Every interactive element uses dual-direction shadows (light from top-left, shadow from bottom-right) creating the illusion of depth from a single light source.

### 2. Press/Release Animations
Buttons transform from convex → flat (hover) → concave (active) with smooth cubic-bezier easing.

### 3. No Hard Borders
Zero use of border properties. All separation achieved through shadow depth.

### 4. Gradient Accents
Accent buttons use subtle gradients (`135deg, #8b7fc7, #6b5eb0`) with colored shadows for visual richness.

### 5. Floating Hero Animation
Hero title has a gentle floating animation (3s ease-in-out) adding life to the static design.

### 6. Parallax Scroll Effect
Hero section has subtle parallax movement and fade on scroll for depth.

## 🧩 Component Library

### Buttons
```html
<!-- Primary Neumorphic Button -->
<button class="neu-button">Click Me</button>

<!-- Accent Button (Gradient) -->
<button class="neu-button neu-button-accent">Get Started</button>
```

### Cards
```html
<div class="neu-card">
  <!-- Content -->
</div>
```

### Input Fields
```html
<input type="text" class="neu-input" placeholder="Enter text...">
```

### Upload Zone
The signature interactive element featuring:
- Concave inset shadow
- Hover scale animation
- Gradient border reveal on hover
- Drag-and-drop visual feedback

## 📸 Image Strategy

### Real Photography (Unsplash)
Gallery section uses **real** Unsplash photos with direct URLs:
- Portrait examples showing transformation potential
- High-quality (1920w, 80% quality)
- Proper semantic alt text for accessibility

### No Fake URLs
Zero placeholder or invented image paths. All images are production-ready direct links.

## 🚀 Features

### Hero Section
- Eye-catching floating headline
- Interactive drag-and-drop upload zone
- Loading state with custom spinner
- Result preview with action buttons

### Features Grid
- 3-column responsive layout
- Icon + title + description cards
- Hover animations with lift effect

### Gallery
- 4-column responsive grid
- Real portrait examples
- Neumorphic card containers

### Pricing
- 3-tier pricing (Free, Pro, One-Time)
- Featured card highlighting
- Clean feature lists with checkmarks

### Footer
- 4-column link grid
- Company, product, resources, legal
- Responsive collapse

## 🎯 Interactions

### Upload Flow (Demo)
1. Click or drag-drop to upload
2. 3-second simulated processing with loader
3. Preview result with download/share actions

**Note:** Currently shows uploaded image as demo. Connect to `/api/generate` endpoint for real pixel art generation.

## 📱 Responsive Design

- **Desktop:** Full 1200px container, multi-column grids
- **Tablet:** Responsive grids collapse to 2 columns
- **Mobile:** Single column, reduced padding, smaller typography

Breakpoint: `768px`

## ♿ Accessibility

- Semantic HTML5 elements
- WCAG AA compliant color contrast (4.5:1 minimum)
- Focus states on all interactive elements
- Alt text on all images
- Keyboard navigation support

## 🔗 Integration Points

### API Endpoints (to be connected)
```javascript
// Upload and generate
POST /api/generate
Body: FormData with image file
Response: { image_url: string, job_id: string }

// Check status
GET /api/status/:jobId
Response: { status: 'processing' | 'complete', result_url?: string }
```

### Firebase Auth (configured)
Connect sign-in button to Firebase authentication flow from `firebase_config.js`.

## 🎨 Design Philosophy

**Tactile Over Flat**
Every element feels like a physical button you can press. The depth is subtle but consistent.

**Monochrome Mastery**
Single color family with surgical accent use creates cohesion and prevents visual noise.

**Motion with Purpose**
Animations serve functional feedback (hover, press, scroll) not decoration.

**Typography-First Hierarchy**
Font weight (300-800 range) and size create clear information hierarchy without color dependence.

## 🏗️ File Structure

```
frontend/
├── index.html          # Complete single-page application
└── README.md          # This file
```

**Production Note:** Convert to Next.js 14 with:
- Component extraction (`components/`)
- Route handlers for API (`app/api/`)
- Server-side rendering for SEO
- Image optimization with `next/image`

## 🎯 Next Steps

1. **Connect API:** Replace demo upload with real `/api/generate` endpoint
2. **Add Auth:** Implement Firebase sign-in flow
3. **State Management:** Add React Context or Zustand for user state
4. **Analytics:** Integrate PostHog/Mixpanel for conversion tracking
5. **SEO:** Add meta tags, OG images, structured data
6. **Performance:** Lazy load images, code splitting, CDN assets

---

**Built with Neumorphism aesthetics** — Soft, tactile, premium. Zero AI slop.
