# Custom Domain Setup: miniaura.aurafarmer.co

## Overview
This guide will help you set up `miniaura.aurafarmer.co` as a subdomain for Mini-Aura.

This allows you to host multiple projects under your main domain:
- `aurafarmer.co` - Your main site/portfolio
- `miniaura.aurafarmer.co` - Mini-Aura app
- `[other-project].aurafarmer.co` - Future projects

---

## 1. Vercel Domain Configuration

### A. Add Subdomain to Vercel Project

1. Go to your Vercel dashboard: https://vercel.com/dashboard
2. Select your `mini-aura` project
3. Go to **Settings** → **Domains**
4. Click **Add Domain**
5. Enter: `miniaura.aurafarmer.co`

### B. Get DNS Record from Vercel

Vercel will provide you with a CNAME record. Typically:

**For Subdomain (miniaura.aurafarmer.co):**
```
Type: CNAME
Name: miniaura
Value: cname.vercel-dns.com
```

---

## 2. Configure DNS at Your Domain Registrar

Go to your domain registrar (where you bought aurafarmer.co) and add this DNS record:

### Record to Add:

```
Type: CNAME
Host: miniaura
Value: cname.vercel-dns.com
TTL: 3600 (or Auto)
```

**Note:** This is much simpler than root domain setup! Just one CNAME record.

### Common Registrars:

**GoDaddy:**
1. Login → My Products → DNS
2. Click "Add" for each record

**Namecheap:**
1. Login → Domain List → Manage → Advanced DNS
2. Add Record

**Google Domains:**
1. Login → DNS
2. Custom resource records → Add

**Cloudflare:**
1. Login → DNS → Records
2. Add Record

---

## 3. Update Environment Variables

### Vercel Environment Variables

1. Go to Vercel → Your Project → Settings → Environment Variables
2. Update or add:

```
NEXT_PUBLIC_API_URL = https://mini-me-api-[hash].a.run.app
```

Replace `[hash]` with your actual Cloud Run URL.

---

## 4. Apply Updated CORS Configuration

Since we updated the CORS config to include aurafarmer.co, run:

```bash
./setup-gcs-cors.sh
```

Or manually:

```bash
gsutil cors set gcs-cors-config.json gs://mini-me-results-mini-aura
gsutil cors set gcs-cors-config.json gs://mini-me-uploads-mini-aura
```

---

## 5. SSL Certificate

Vercel automatically provides SSL certificates for custom domains.

**After adding the domain:**
- SSL certificate is issued automatically (takes 1-2 minutes)
- Your site will be available at:
  - https://aurafarmer.co
  - https://www.aurafarmer.co

**To verify:**
- Check for the green padlock in browser
- Or visit: https://www.ssllabs.com/ssltest/analyze.html?d=aurafarmer.co

---

## 6. Root Domain Setup (Optional)

If you want `aurafarmer.co` to redirect to `miniaura.aurafarmer.co`:

1. Add `aurafarmer.co` as a domain in Vercel
2. Set it to redirect to `miniaura.aurafarmer.co`

**Or** keep `aurafarmer.co` for your main portfolio/landing page!

---

## 7. Verify Setup

After DNS propagates (can take up to 48 hours, usually < 15 minutes for subdomains):

### Test Checklist:

- [ ] https://miniaura.aurafarmer.co loads correctly
- [ ] SSL certificate shows as valid (auto-configured by Vercel)
- [ ] Images download without CORS errors
- [ ] Stripe payments work
- [ ] Account creation works
- [ ] Avatar generation works

---

## 8. Update Stripe Webhook

Once your custom domain is live:

1. Go to Stripe Dashboard → Webhooks
2. Update webhook endpoint URL:
   - Old: `https://mini-aura.vercel.app/...`
   - New: Use your Cloud Run API URL directly (not Vercel)

Your webhook should point to:
```
https://mini-me-api-[hash].a.run.app/api/webhooks/stripe
```

---

## 9. Analytics & Monitoring (Optional)

### Google Analytics

Add to `frontend/app/layout.tsx`:

```tsx
// Add Google Analytics
<Script
  src="https://www.googletagmanager.com/gtag/js?id=G-YOUR-ID"
  strategy="afterInteractive"
/>
```

### Vercel Analytics

Enable in Vercel dashboard:
1. Settings → Analytics
2. Enable Web Analytics

---

## Troubleshooting

### "Domain not found" or "This site can't be reached"

**Cause:** DNS not propagated yet
**Solution:** Wait up to 48 hours. Check DNS propagation: https://dnschecker.org/

### SSL Certificate Error

**Cause:** Certificate not issued yet
**Solution:** Wait 5-10 minutes after adding domain. Vercel auto-issues certificates.

### CORS Errors on Image Download

**Cause:** CORS not updated
**Solution:** Run `./setup-gcs-cors.sh` again

### Payments Not Working

**Cause:** Stripe webhook pointing to wrong URL
**Solution:** Update webhook in Stripe Dashboard to use Cloud Run URL

---

## DNS Propagation Check

Check if DNS is propagated globally:

```bash
# Check CNAME record
dig miniaura.aurafarmer.co +short

# Should return: cname.vercel-dns.com (or similar Vercel CNAME)
```

Or use online tool: https://dnschecker.org/#CNAME/miniaura.aurafarmer.co

---

## Production Deployment Flow

1. **Push to GitHub** → Triggers Vercel build
2. **Vercel builds frontend** → Deploys to miniaura.aurafarmer.co
3. **Users visit** → https://miniaura.aurafarmer.co
4. **API calls go to** → Cloud Run (mini-aura-api)
5. **Images stored in** → GCS buckets

---

## Final Production URLs

**Frontend:** https://miniaura.aurafarmer.co
**API:** https://mini-me-api-[hash].a.run.app
**Stripe Webhook:** https://mini-me-api-[hash].a.run.app/api/webhooks/stripe

---

## Benefits of Using a Subdomain

✅ **Cleaner architecture** - Separate projects under one domain
✅ **Easier DNS** - Just one CNAME record vs A + CNAME
✅ **Faster propagation** - Subdomains typically propagate in < 15 minutes
✅ **Flexible** - Easy to add more projects (blog.aurafarmer.co, etc.)
✅ **Main domain free** - Keep aurafarmer.co for your portfolio/landing page

---

## Support

If you encounter issues:
1. Check Vercel deployment logs
2. Check DNS propagation status
3. Verify SSL certificate status
4. Test API endpoint directly
