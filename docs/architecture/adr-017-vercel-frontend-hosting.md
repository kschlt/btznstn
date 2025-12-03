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

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Hosting Platform | Vercel | Netlify, Cloudflare Pages, AWS S3+CloudFront |
| CDN | Global edge network | Single region hosting |
| Preview Deployments | Vercel preview deployments | Manual preview setup |
| Edge Caching | ISR (Incremental Static Regeneration) | No caching, full SSR every request |

---

## Rationale

**Why Vercel:**
- Vercel is Next.js-native (made by Next.js creators) → **Constraint:** MUST use Vercel for Next.js hosting (optimized for Next.js)
- Vercel provides global CDN → **Constraint:** MUST use Vercel's global edge network (<100ms worldwide, ~20ms in Germany)
- Vercel supports preview deployments → **Constraint:** MUST use Vercel preview deployments (every PR gets unique URL for testing)
- Vercel supports ISR (Incremental Static Regeneration) → **Constraint:** MUST use ISR for edge caching (fast page loads, low API load)

**Why NOT Netlify:**
- Netlify requires more configuration for Next.js → **Violation:** Not Next.js-native, violates zero-config requirement

**Why NOT Cloudflare Pages:**
- Cloudflare Pages uses edge runtime (different from Node.js) → **Violation:** Compatibility issues, build limitations, violates Next.js requirement

---

## Consequences

### MUST (Required)

- MUST use Vercel for Next.js hosting - Next.js-native, optimized for Next.js
- MUST use Vercel's global CDN - Fast page loads worldwide (<100ms, ~20ms in Germany)
- MUST use Vercel preview deployments - Every PR gets unique URL for testing
- MUST use ISR (Incremental Static Regeneration) for edge caching - Fast page loads, low API load

### MUST NOT (Forbidden)

- MUST NOT use Netlify or Cloudflare Pages - Violates Next.js-native requirement, requires more configuration
- MUST NOT use AWS S3 + CloudFront - Violates simplicity requirement, complex setup, expensive
- MUST NOT skip preview deployments - Violates testing requirement, harder to review changes

### Trade-offs

- Vendor lock-in - MUST use Vercel. MUST NOT use other platforms. Some Vercel-specific features, but Next.js is portable.
- Free tier limits - MUST use free tier initially. MUST NOT exceed 100GB bandwidth/month without upgrading. Monitor usage before scaling.

### Code Examples

```typescript
// ✅ CORRECT: ISR for edge caching
// app/calendar/page.tsx
export const revalidate = 60  // Revalidate every 60 seconds

export default async function CalendarPage() {
  const bookings = await fetchBookings()
  return <Calendar bookings={bookings} />
}
```

### Applies To

- ALL frontend hosting (Phase 1, 5, 6, 7, 8)
- File patterns: `web/`
- Vercel configuration: `vercel.json` (if needed)

### Validation Commands

- `grep -r "export const revalidate" web/app/` (should be present for ISR usage)

---

## References

**Related ADRs:**
- [ADR-002](adr-002-frontend-framework.md) - Frontend Framework (Next.js App Router)
- [ADR-011](adr-011-cors-security-policy.md) - CORS Security Policy (Frontend ↔ Backend)
- [ADR-015](adr-015-flyio-backend-hosting.md) - Fly.io Backend Hosting (backend API)
- [ADR-018](adr-018-github-actions-cicd.md) - GitHub Actions CI/CD (automated deployment)

**Tools:**
- [Vercel Documentation](https://vercel.com/docs)
- [Next.js ISR](https://nextjs.org/docs/app/building-your-application/data-fetching/incremental-static-regeneration)

**Implementation:**
- `web/` - Next.js frontend application
- `vercel.json` - Vercel configuration (if needed)
