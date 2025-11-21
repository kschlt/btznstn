# ADR-017: Vercel Frontend Hosting

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** Need globally-distributed hosting optimized for Next.js
**Split from:** ADR-007: Deployment Strategy

---

## Context

Need hosting platform for Next.js frontend that:
- Deploys Next.js 14 (App Router) seamlessly
- Global CDN (fast page loads worldwide)
- Preview deployments (test PRs before merge)
- Edge caching for static assets
- AI-friendly (simple deployment, clear errors)
- Budget-friendly (free or cheap for MVP)

---

## Decision

Deploy Next.js frontend to **Vercel** with global CDN distribution.

---

## Rationale

### Why Vercel vs Netlify vs Cloudflare Pages vs AWS?

**Vercel (Chosen):**
- ✅ **Next.js-native** - Made by Next.js creators, zero-config
- ✅ **Push to deploy** - Connect GitHub repo, auto-deploys
- ✅ **Global CDN** - <100ms worldwide, ~20ms in Germany
- ✅ **Preview deployments** - Every PR gets unique URL
- ✅ **Edge caching** - ISR (Incremental Static Regeneration)
- ✅ **Free tier** - Generous (unlimited deployments, 100GB bandwidth)
- ✅ **Automatic HTTPS** - Free TLS certificates

**Netlify (Rejected):**
- ❌ Not Next.js-native (requires more config)
- ❌ Smaller edge network

**Cloudflare Pages (Rejected):**
- ❌ Edge runtime (different from Node.js, compatibility issues)
- ❌ Build limitations (some Next.js features unsupported)

**AWS S3 + CloudFront (Rejected):**
- ❌ Complex setup (buckets, distributions, Lambda@Edge)
- ❌ Expensive ($10-50/month)
- ❌ Not AI-friendly

---

## Key Benefits

### 1. Zero-Config Next.js Deployment

```bash
# Connect GitHub repo to Vercel (one-time via UI)
# Push to main branch
git push origin main

# Vercel automatically:
# - Detects changes
# - Builds Next.js app
# - Deploys to production
# - Updates DNS
```

Zero config = nothing to get wrong.

### 2. Global CDN (Fast Worldwide)

**Vercel CDN:**
- Cloudflare-backed global edge network
- 100+ locations
- Automatic caching
- Smart routing

**Performance:**
- Germany: ~20ms (primary users)
- Rest of EU: ~30-50ms
- Worldwide: <100ms

### 3. Preview Deployments (Test PRs Before Merge)

**Workflow:**
1. Create PR with changes
2. Vercel auto-deploys to `https://betzenstein-pr-123.vercel.app`
3. Review feature on preview URL
4. Merge PR → deploys to production

**Benefits:**
- Test in production-like environment
- Share with stakeholders
- No local setup required
- Isolated testing

### 4. Edge Caching + ISR

```typescript
// app/calendar/page.tsx
export const revalidate = 60  // Revalidate every 60 seconds

export default async function CalendarPage() {
  const bookings = await fetchBookings()
  return <Calendar bookings={bookings} />
}
```

**How it works:**
1. First user: Fetches from API → Generates page → Caches at edge
2. Next 59s: All users get cached page (instant load)
3. After 60s: Next request regenerates in background

Fast for users, low API load, always fresh-ish.

---

## Consequences

### Positive

✅ **Zero-config** - Push to GitHub, auto-deploys
✅ **Global CDN** - <100ms worldwide, ~20ms in Germany
✅ **Preview deployments** - Every PR gets unique URL
✅ **Edge caching** - ISR for fast page loads
✅ **Free tier** - Generous for MVP
✅ **Automatic HTTPS** - Free TLS certificates
✅ **Next.js-optimized** - Made by same team

### Negative

⚠️ **Vendor lock-in** - Some Vercel-specific features (but Next.js is portable)
⚠️ **Free tier limits** - 100GB bandwidth/month
⚠️ **Less control** - Can't customize build as much as self-hosted

### Neutral

➡️ **Stateless** - No persistent storage (appropriate for frontend)
➡️ **Serverless** - Edge functions available (not required initially)

---

## Implementation Pattern

### Connect GitHub Repo

**Via Vercel dashboard:**
1. Sign in to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import GitHub repository
4. Vercel auto-detects Next.js
5. Deploy

**Build settings (auto-detected):**
```
Framework: Next.js
Build Command: npm run build
Output Directory: .next
```

### Set Environment Variables

```
NEXT_PUBLIC_API_URL=https://api.betzenstein.app  (Production)
NEXT_PUBLIC_API_URL=https://staging-api.fly.dev  (Preview)
```

### Deploy

**Automatic:**
```bash
git push origin main  # Auto-deploys to production
git push origin feature  # Auto-deploys preview
```

**Manual (CLI):**
```bash
npm install -g vercel
vercel  # Preview
vercel --prod  # Production
```

### Custom Domain

**Via dashboard:**
1. Project settings → Add domain
2. Configure DNS:
   - A: `76.76.21.21`
   - CNAME www: `cname.vercel-dns.com`
3. Vercel auto-provisions TLS certificate

---

## References

**Related ADRs:**
- ADR-002: Frontend Framework (Next.js App Router)
- ADR-011: CORS Security Policy (Frontend ↔ Backend)
- ADR-016: Fly.io Backend Hosting (backend API)
- ADR-018: GitHub Actions CI/CD (automated deployment)

**Tools:**
- [Vercel Documentation](https://vercel.com/docs)
- [Next.js ISR](https://nextjs.org/docs/app/building-your-application/data-fetching/incremental-static-regeneration)
