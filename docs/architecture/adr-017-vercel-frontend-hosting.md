# ADR-017: Vercel Frontend Hosting

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)
**Split from:** [ADR-007: Deployment Strategy](adr-007-deployment.md)

---

## Context

We need to choose a hosting platform for the Next.js frontend. The hosting must:

- Deploy Next.js 14 (App Router) seamlessly
- Provide global CDN (fast page loads worldwide)
- Support preview deployments (test PRs before merge)
- Enable edge caching for static assets
- Be AI-friendly (simple deployment, clear errors)
- Fit within budget (free or cheap for MVP)

### Requirements

**From architecture:**
- Frontend is Next.js 14 with App Router (ADR-002)
- Backend API on Fly.io (ADR-016)
- Different origin requires CORS (ADR-011)
- Mobile-first (fast load times critical)

---

## Decision

We will deploy the Next.js frontend to **Vercel** with global CDN distribution.

---

## Rationale

### 1. Zero-Config Next.js Deployment (Perfect Match)

**Vercel is made by Next.js creators** - Native integration.

**Key benefits:**
- ✅ **Push to deploy** - Connect GitHub repo, auto-deploys on push
- ✅ **No configuration** - Detects Next.js, builds, deploys automatically
- ✅ **Optimal build settings** - Vercel knows best Next.js config
- ✅ **Instant rollbacks** - One-click rollback to previous deploy

**Example workflow:**
```bash
# 1. Connect GitHub repo to Vercel (one-time setup via UI)
# 2. Push to main branch
git push origin main
# 3. Vercel automatically:
#    - Detects changes
#    - Builds Next.js app
#    - Deploys to production
#    - Updates DNS
```

**AI benefit:** Zero config = nothing to get wrong.

### 2. Global CDN (Fast Worldwide)

**Vercel CDN:**
- ✅ **Cloudflare-backed** - Global edge network
- ✅ **100+ locations** - <100ms latency worldwide
- ✅ **Automatic caching** - Static assets cached at edge
- ✅ **Smart routing** - Users routed to nearest edge node

**Performance benefits:**
- Germany: ~20ms (primary users)
- Rest of EU: ~30-50ms
- Worldwide: <100ms

**Example (cache headers):**
```typescript
// Next.js automatically sets cache headers
// Static assets: Cache-Control: public, max-age=31536000, immutable
// HTML: Cache-Control: s-maxage=1, stale-while-revalidate
```

### 3. Preview Deployments (Test PRs Before Merge)

**Every pull request gets unique URL:**

**Workflow:**
1. Create PR with changes
2. Vercel automatically deploys to `https://betzenstein-pr-123.vercel.app`
3. Review feature on preview URL
4. Merge PR → deploys to production

**Benefits:**
- ✅ **Test in production-like environment** - Real deployment, real performance
- ✅ **Share with stakeholders** - Send preview URL for feedback
- ✅ **No local setup required** - Anyone can test via URL
- ✅ **Isolated testing** - Each PR gets own URL, no conflicts

**AI benefit:** AI creates PR → Vercel deploys → user reviews → merge.

### 4. Edge Caching + ISR

**Next.js Incremental Static Regeneration (ISR):**
```typescript
// app/calendar/page.tsx
export const revalidate = 60  // Revalidate every 60 seconds

export default async function CalendarPage() {
  const bookings = await fetchBookings()  // Fetch from API
  return <Calendar bookings={bookings} />
}
```

**How it works:**
1. First user: Fetches from API → Generates page → Caches at edge
2. Next 59 seconds: All users get cached page (instant load, no API calls)
3. After 60s: Next request regenerates in background, updates cache

**Benefits:**
- ✅ **Fast for users** - Cached pages load instantly
- ✅ **Low API load** - Backend not hit on every page load
- ✅ **Always fresh-ish** - Data updates every 60s (configurable)

### 5. Environment Variables (Per-Environment Config)

**Vercel dashboard:**
- Production env vars: `NEXT_PUBLIC_API_URL=https://api.betzenstein.app`
- Preview env vars: `NEXT_PUBLIC_API_URL=https://betzenstein-api-staging.fly.dev`
- Development: Uses local `.env.local`

**Next.js reads:**
```typescript
// lib/config.ts
export const API_URL = process.env.NEXT_PUBLIC_API_URL
```

**Benefits:**
- ✅ **Same code** works in dev, preview, production
- ✅ **Secure secrets** - Not committed to Git
- ✅ **Per-environment** - Different API URLs for each

### 6. Automatic HTTPS (Free TLS Certificates)

**Vercel provides:**
- ✅ **Automatic TLS** - Free SSL certificates
- ✅ **Custom domains** - Connect `betzenstein.app`
- ✅ **Auto-renewal** - Certificates renewed automatically
- ✅ **HTTPS redirect** - HTTP → HTTPS automatic

**Setup:**
```bash
# Add custom domain via Vercel dashboard
# Configure DNS:
# A record: 76.76.21.21
# AAAA record: 2606:4700:4700::1111

# Vercel handles TLS automatically
```

### 7. Free Tier (Generous for MVP)

**Vercel free (Hobby plan):**
- Unlimited deployments
- 100GB bandwidth/month
- Preview deployments included
- Custom domains included
- Automatic HTTPS
- Global CDN

**Sufficient for MVP:**
- Small user base (~10-20 users)
- Static assets cached (low bandwidth)
- Limited dynamic page loads

**Later:** ~$20/month for Pro (if traffic grows).

---

## Alternatives Considered

### Netlify

**Pros:**
- Similar to Vercel
- Good CDN
- Free tier

**Cons:**
- ❌ **Not Next.js-native** - Vercel optimized for Next.js
- ❌ **Less seamless** - Requires more configuration
- ❌ **Smaller edge network**
- ❌ **Less AI training data** - Vercel more prevalent

**Decision:** Vercel is optimal for Next.js (same team).

---

### Cloudflare Pages

**Pros:**
- Fast CDN
- Free tier
- Modern platform

**Cons:**
- ❌ **Edge runtime** - Different from Node.js (compatibility issues)
- ❌ **Build limitations** - Some Next.js features not supported
- ❌ **Less Next.js-specific** - Generic static site hosting

**Decision:** Vercel better Next.js support.

---

### AWS (S3 + CloudFront)

**Pros:**
- Full control
- Scalable
- Enterprise-grade

**Cons:**
- ❌ **Complex setup** - S3 buckets, CloudFront distributions, Lambda@Edge
- ❌ **Manual config** - Build scripts, cache headers, etc.
- ❌ **Expensive** - CloudFront + Lambda ~$10-50/month
- ❌ **Not AI-friendly** - Too many moving parts

**Decision:** Vercel simpler, cheaper for MVP.

---

### Fly.io (Same as Backend)

**Pros:**
- Same platform as backend
- Container-based
- Global deployment

**Cons:**
- ❌ **Not optimized for Next.js** - Generic containers, not Next.js-specific
- ❌ **No automatic CDN** - Would need manual CDN setup
- ❌ **No preview deployments** - Manual setup required
- ❌ **More ops work** - Manage build, deploy, caching manually

**Decision:** Vercel optimized for Next.js, less ops overhead.

---

### Self-Hosted (VPS)

**Pros:**
- Full control
- Cheap ($5/month)

**Cons:**
- ❌ **No CDN** - Slow for users far from server
- ❌ **Manual ops** - Updates, security, monitoring
- ❌ **Single point of failure**
- ❌ **No preview deployments**

**Decision:** Vercel CDN + automation worth more than $5/month saved.

---

## Consequences

### Positive

✅ **Zero-config** - Push to GitHub, auto-deploys
✅ **Global CDN** - <100ms worldwide, ~20ms in Germany
✅ **Preview deployments** - Every PR gets unique URL
✅ **Edge caching** - ISR for fast page loads
✅ **Free tier** - Generous for MVP
✅ **Automatic HTTPS** - Free TLS certificates
✅ **Next.js-optimized** - Made by same team, perfect integration

### Negative

⚠️ **Vendor lock-in** - Some Vercel-specific features (but Next.js is portable)
⚠️ **Free tier limits** - 100GB bandwidth/month (need to upgrade if exceeded)
⚠️ **Less control** - Can't customize build process as much as self-hosted

### Neutral

➡️ **Stateless** - No persistent storage (appropriate for frontend)
➡️ **Serverless** - Edge functions available if needed (not required initially)

---

## Implementation Notes

### Connect GitHub Repo

**Via Vercel dashboard:**
1. Sign in to Vercel (https://vercel.com)
2. Click "New Project"
3. Import GitHub repository
4. Vercel auto-detects Next.js, sets build settings
5. Deploy

**Build settings (auto-detected):**
```
Framework Preset: Next.js
Build Command: npm run build
Output Directory: .next
Install Command: npm install
```

### Set Environment Variables

**Via Vercel dashboard:**
```
NEXT_PUBLIC_API_URL=https://api.betzenstein.app  (Production)
NEXT_PUBLIC_API_URL=https://betzenstein-api-staging.fly.dev  (Preview)
```

**Or via CLI:**
```bash
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://api.betzenstein.app
```

### Deploy

**Automatic (on git push):**
```bash
git push origin main  # Auto-deploys to production
git push origin feature-branch  # Auto-deploys preview
```

**Manual (via CLI):**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel  # Deploy to preview
vercel --prod  # Deploy to production
```

### Custom Domain

**Via Vercel dashboard:**
1. Go to project settings
2. Add domain: `betzenstein.app`
3. Configure DNS records (Vercel provides values)
4. Wait for DNS propagation (~5-60 minutes)
5. Vercel automatically provisions TLS certificate

**DNS records:**
```
A     @  76.76.21.21  # Root domain
CNAME www  cname.vercel-dns.com  # www subdomain
```

---

## Validation

### Verify Deployment

**Check deployment status:**
- Visit Vercel dashboard
- See "Deployment Status: Ready"
- Click "Visit" to open site

**Expected:** Site loads, no errors.

### Verify CDN

**Check response headers:**
```bash
curl -I https://betzenstein.app
```

**Expected headers:**
```
x-vercel-cache: HIT  # Served from CDN
cache-control: public, max-age=0, must-revalidate
```

### Verify Preview Deployment

**Create PR:**
```bash
git checkout -b test-feature
git push origin test-feature
# Create PR on GitHub
```

**Expected:** Vercel comment on PR with preview URL.

### Verify Environment Variables

**Check API URL:**
```typescript
// In browser console on https://betzenstein.app
console.log(process.env.NEXT_PUBLIC_API_URL)
// Expected: https://api.betzenstein.app
```

---

## References

- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Next.js Deployment](https://vercel.com/docs/frameworks/nextjs)
- [Vercel Preview Deployments](https://vercel.com/docs/deployments/preview-deployments)
- [Next.js ISR](https://nextjs.org/docs/app/building-your-application/data-fetching/incremental-static-regeneration)

**Related ADRs:**
- [ADR-002: Web Framework](adr-002-frontend-framework.md) - Next.js App Router
- [ADR-011: CORS Security Policy](adr-011-cors-security-policy.md) - Frontend ↔ Backend communication
- [ADR-016: Fly.io Backend Hosting](adr-016-flyio-backend-hosting.md) - Backend API
- [ADR-018: GitHub Actions CI/CD](adr-018-github-actions-cicd.md) - Automated deployment

---

## Changelog

- **2025-01-19:** Split from ADR-007 - Vercel frontend hosting as independent decision
