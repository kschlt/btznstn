# ADR-002: Frontend Framework

**Status:** Accepted
**Date:** 2025-01-17
**Deciders:** Solution Architect
**Context:** AI-driven development - need AI-friendly React framework

---

## Context

Need frontend framework for booking calendar that:
- React-based with TypeScript
- Mobile-first (iPhone 8: 375×667px minimum)
- Easy Vercel deployment
- Shadcn/ui compatible
- Well-documented for AI

---

## Decision

Use **Next.js 14+ with App Router** as the frontend framework.

---

## Rationale

### Why Next.js vs Create React App vs Vite?

**Next.js (Chosen):**
- ✅ **AI-friendly** - Most popular React framework, in Claude's training data
- ✅ **App Router** - Modern React patterns (Server Components)
- ✅ **Zero-config TypeScript** - Just rename .js → .tsx
- ✅ **Vercel deployment** - One-click deploy, automatic
- ✅ **Built-in routing** - File-based, no react-router needed

**Create React App (Rejected):**
- ❌ Deprecated (unmaintained since 2022)
- ❌ No built-in routing
- ❌ Manual deployment setup

**Vite (Rejected):**
- ❌ Less AI training data than Next.js
- ❌ Manual routing (react-router)
- ❌ More configuration needed

---

## Consequences

### Positive

✅ **Fast development** - File-based routing, hot reload
✅ **TypeScript native** - No configuration needed
✅ **Vercel optimized** - Automatic deployment, edge caching
✅ **Modern React** - Server Components, Suspense, etc.

### Negative

⚠️ **App Router learning curve** - Newer than Pages Router
⚠️ **Server Components** - Must understand client vs server

### Neutral

➡️ **Next.js conventions** - Opinionated structure (good for consistency)

---

## Implementation Pattern

### File Structure

```
web/
  app/
    layout.tsx          # Root layout
    page.tsx            # Home page (calendar)
    bookings/
      [id]/
        page.tsx        # Booking details
    approver/
      page.tsx          # Approver overview
  components/
    ui/                 # Shadcn/ui components
    calendar/           # Custom calendar components
```

### Basic Page

```typescript
// app/calendar/page.tsx
export default function CalendarPage() {
  return (
    <div className="container">
      <h1>Kalender</h1>
      {/* Calendar component */}
    </div>
  )
}
```

### TypeScript Config

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

---

## References

**Related ADRs:**
- ADR-005: UI Framework (Shadcn/ui + Tailwind)
- ADR-006: Type Safety (TypeScript strict)
- ADR-017: Vercel Hosting (deployment)

**Tools:**
- [Next.js](https://nextjs.org/)
- [App Router Docs](https://nextjs.org/docs/app)
- [Vercel](https://vercel.com/)
