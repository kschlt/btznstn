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

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Framework | Next.js 14+ App Router | Create React App, Vite, Pages Router |
| Routing | File-based routing | Manual routing (`react-router`) |
| TypeScript | Zero-config TypeScript | JavaScript without types |
| Components | Server/Client Components | All client-side components |

---

## Rationale

**Why Next.js:**
- Next.js requires App Router (not Pages Router) → **Constraint:** MUST use App Router with Server Components
- Next.js provides file-based routing → **Constraint:** MUST use file-based routing (no `react-router`)
- Next.js supports zero-config TypeScript → **Constraint:** MUST use TypeScript (`.tsx` files)

**Why NOT Create React App:**
- Create React App is deprecated (unmaintained since 2022) → **Violation:** Using deprecated framework violates maintenance requirement
- Create React App requires manual routing → **Violation:** Manual routing (`react-router`) violates file-based routing constraint

---

## Consequences

### MUST (Required)

- MUST use Next.js 14+ with App Router - Next.js provides file-based routing and Server Components
- MUST use file-based routing - File structure in `app/` directory defines routes (no `react-router`)
- MUST use TypeScript - Zero-config TypeScript support, all files use `.tsx` extension

### MUST NOT (Forbidden)

- MUST NOT use Create React App - Deprecated framework (unmaintained since 2022)
- MUST NOT use manual routing (`react-router`) - Violates file-based routing constraint
- MUST NOT use Pages Router - Must use App Router (Next.js 14+ requirement)

### Trade-offs

- Many code examples use Pages Router - MUST use App Router patterns (`app/` directory). MUST NOT use Pages Router patterns (`pages/` directory). Check for `pages/` directory usage.
- Code examples may mix Server and Client Components incorrectly - MUST use `"use client"` directive only when component uses browser APIs or React hooks. MUST NOT use `"use client"` unnecessarily. Verify `"use client"` usage.

### Applies To

- ALL frontend pages and components (Phase 5, 6, 7, 8)
- File patterns: `web/app/**/*.tsx`
- Routing structure in `web/app/` directory

### Validation Commands

- `grep -r "react-router" web/` (should be empty)
- `grep -r "from 'next/router'" web/` (should be empty - use App Router, not Pages Router)
- `grep -r "\.jsx" web/app/` (should be empty - use `.tsx` files)

**Related ADRs:**
- [ADR-005](adr-005-ui-framework.md) - UI Framework (Shadcn/ui + Tailwind)
- [ADR-006](adr-006-type-safety.md) - Type Safety (TypeScript strict)
- [ADR-017](adr-017-vercel-frontend-hosting.md) - Vercel Hosting (deployment)

---

## References

**Related ADRs:**
- [ADR-005](adr-005-ui-framework.md) - UI Framework (Shadcn/ui + Tailwind)
- [ADR-006](adr-006-type-safety.md) - Type Safety (TypeScript strict)
- [ADR-017](adr-017-vercel-frontend-hosting.md) - Vercel Hosting (deployment)

**Tools:**
- [Next.js](https://nextjs.org/)
- [App Router Docs](https://nextjs.org/docs/app)
- [Vercel](https://vercel.com/)

**Implementation:**
- `web/app/` - Next.js App Router pages
- `web/components/` - React components
- `web/tsconfig.json` - TypeScript configuration
