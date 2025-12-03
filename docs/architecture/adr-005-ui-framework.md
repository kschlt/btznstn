# ADR-005: UI Framework

**Status:** Accepted
**Date:** 2025-01-17
**Deciders:** Solution Architect
**Context:** AI-driven development - need AI-friendly component library

---

## Context

Need UI component library and styling for booking calendar that:
- React components for Next.js
- Mobile-first (iPhone 8: 375px minimum)
- German UI copy
- Accessibility (WCAG AA)
- Easy customization (affiliation colors)
- Well-documented for AI

---

## Decision

Use **Shadcn/ui + Tailwind CSS + Radix UI** for the UI framework.

---

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Component Library | Shadcn/ui (copy-paste) | Material-UI, Chakra UI (npm install) |
| Styling | Tailwind CSS utility classes | CSS-in-JS, separate CSS files |
| Accessibility | Radix UI primitives | Manual ARIA/keyboard implementation |
| Mobile-First | Tailwind responsive breakpoints | Fixed-width layouts |
| Configuration | Tailwind config for colors | Hardcoded colors |

---

## Rationale

**Why Shadcn/ui + Tailwind CSS + Radix UI:**
- Shadcn/ui uses copy-paste model → **Constraint:** MUST add components to codebase (not npm install), MUST use `npx shadcn-ui add` command
- Shadcn/ui built on Radix UI → **Constraint:** MUST use Radix UI primitives for accessibility (WCAG AA compliance)
- Tailwind CSS provides utility-first classes → **Constraint:** MUST use Tailwind utility classes (no CSS-in-JS, no separate CSS files)
- Tailwind CSS mobile-first → **Constraint:** MUST use responsive breakpoints (`sm:`, `md:`, `lg:`) for mobile-first design
- Tailwind CSS supports design tokens → **Constraint:** MUST define custom colors in `tailwind.config.ts`

**Why NOT Material-UI:**
- Material-UI uses CSS-in-JS runtime → **Violation:** CSS-in-JS runtime overhead violates performance requirement
- Material-UI is black box (npm install) → **Violation:** Cannot modify components directly, violates transparency requirement for AI

---

## Consequences

### MUST (Required)

- MUST use Shadcn/ui components (copy-paste model) - Components added to codebase via `npx shadcn-ui add`, not npm install
- MUST use Tailwind CSS utility classes - No CSS-in-JS, no separate CSS files, use utility classes only
- MUST use Radix UI primitives via Shadcn - Radix UI provides WCAG AA accessibility (keyboard nav, screen readers, focus management)
- MUST use mobile-first responsive breakpoints - Use Tailwind breakpoints (`sm:`, `md:`, `lg:`) starting from mobile (375px)
- MUST define custom colors in `tailwind.config.ts` - Tailwind configuration must be used for design tokens
- MUST use TypeScript for all components - All components must be `.tsx` files with type safety

### MUST NOT (Forbidden)

- MUST NOT use Material-UI/Chakra UI - Violates copy-paste model and transparency requirement
- MUST NOT use CSS-in-JS - Violates performance requirement (runtime overhead)
- MUST NOT use separate CSS files - Violates utility-first constraint
- MUST NOT hardcode colors - Must use Tailwind config for design tokens
- MUST NOT skip accessibility - Must use Radix UI primitives (don't implement ARIA manually)

### Trade-offs

- Many code examples use CSS-in-JS or separate CSS files - MUST use Tailwind utility classes only. MUST NOT use CSS-in-JS or separate CSS files. Check for CSS-in-JS imports or `.css` files in components.
- Code examples may use Material-UI or Chakra UI - MUST use Shadcn/ui components (copy-paste model). MUST NOT use Material-UI or Chakra UI (npm-installed libraries). Check for Material-UI/Chakra imports.

### Applies To

- ALL UI components (Phase 5, 6, 7, 8)
- File patterns: `web/components/**/*.tsx`, `web/app/**/*.tsx`
- Tailwind configuration: `web/tailwind.config.ts`

### Validation Commands

- `grep -r "@mui\|@chakra-ui" web/` (should be empty - must use Shadcn/ui)
- `grep -r "styled\|emotion\|@emotion" web/` (should be empty - no CSS-in-JS)
- `grep -r "\.css" web/components/` (should be empty - use Tailwind classes)
- `grep -r "npx shadcn-ui" web/` (should reference Shadcn CLI)

**Related ADRs:**
- [ADR-002](adr-002-frontend-framework.md) - Frontend Framework (Next.js integration)
- [ADR-006](adr-006-type-safety.md) - Type Safety Strategy (TypeScript strict mode)

---

## References

**Related ADRs:**
- [ADR-002](adr-002-frontend-framework.md) - Frontend Framework (Next.js integration)
- [ADR-006](adr-006-type-safety.md) - Type Safety Strategy (TypeScript strict mode)

**Tools:**
- [Shadcn/ui](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Radix UI](https://www.radix-ui.com/)

**Implementation:**
- `web/components/ui/` - Shadcn/ui components
- `web/tailwind.config.ts` - Tailwind configuration
- `web/components.json` - Shadcn/ui configuration
