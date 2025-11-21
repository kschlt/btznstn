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

## Rationale

### Why Shadcn/ui vs Material-UI vs Chakra UI?

**Shadcn/ui (Chosen):**
- ✅ **Copy-paste model** - Components added to your codebase (not npm install)
- ✅ **Full control** - Can modify components directly
- ✅ **AI-friendly** - Simple: `npx shadcn-ui add button`
- ✅ **Transparent** - AI can see all component code
- ✅ **Accessibility built-in** - Uses Radix UI primitives

**Material-UI (Rejected):**
- ❌ Heavy bundle (~300KB)
- ❌ Complex theming (ThemeProvider, createTheme)
- ❌ Black box (can't easily modify)
- ❌ CSS-in-JS runtime overhead

**Chakra UI (Rejected):**
- ❌ Black box (npm install, harder to modify)
- ❌ CSS-in-JS runtime overhead
- ❌ Less AI training data

### Why Tailwind CSS?

**Tailwind CSS (Chosen):**
- ✅ **Massive AI training data** - Most popular CSS framework
- ✅ **Utility-first** - Self-documenting classNames
- ✅ **Mobile-first** - Built-in responsive breakpoints (`sm:`, `md:`, `lg:`)
- ✅ **Design tokens** - Custom colors in config
- ✅ **Performance** - Purges unused CSS (~10-20KB final)
- ✅ **No runtime** - Pure CSS, no JavaScript overhead

**Example:**
```tsx
<button className="bg-blue-500 hover:bg-blue-600 text-white py-2 px-4 rounded">
  Zustimmen
</button>
```

AI reads this instantly - no separate CSS files.

**Custom colors:**
```typescript
// tailwind.config.ts
theme: {
  extend: {
    colors: {
      affiliation: {
        ingeborg: '#C1DBE3',
        cornelia: '#C7DFC5',
        angelika: '#DFAEB4',
      }
    }
  }
}

// Usage: <div className="bg-affiliation-ingeborg">
```

### Why Radix UI?

**Radix UI (via Shadcn):**
- ✅ **WCAG AA compliance** - Keyboard nav, screen readers, focus management
- ✅ **Unstyled primitives** - Shadcn adds Tailwind styles
- ✅ **Composable** - Build complex components
- ✅ **Next.js compatible** - Works with App Router

**Example:**
```tsx
<Dialog>
  <DialogTrigger>Neue Anfrage</DialogTrigger>
  <DialogContent>
    {/* Radix handles: focus trap, Esc, ARIA */}
    <DialogTitle>Buchung erstellen</DialogTitle>
    {/* Form */}
  </DialogContent>
</Dialog>
```

AI doesn't implement accessibility manually - Radix handles it.

---

## Consequences

### Positive

✅ **AI can add components easily** - Simple CLI commands
✅ **AI knows Tailwind extremely well** - Massive training data
✅ **Mobile-first built-in** - Responsive by default
✅ **Full control** - Components in codebase, modifiable
✅ **Accessible** - Radix handles ARIA, keyboard, focus
✅ **Fast** - Small bundle, no runtime overhead
✅ **Type-safe** - All components TypeScript

### Negative

⚠️ **Verbose classes** - `className` strings can be long (but readable)
⚠️ **Copy-paste updates** - Must update components manually (vs npm update)

### Neutral

➡️ **Design system** - Define tokens in Tailwind config
➡️ **Component variants** - Define in code (AI can generate)

---

## Implementation Pattern

### Setup

```bash
# Install Tailwind + Shadcn
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npx shadcn-ui@latest init

# Add components as needed
npx shadcn-ui add button dialog calendar form select
```

### Component Example

```tsx
// components/booking/BookingCard.tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

export function BookingCard({ firstName, status, affiliation }) {
  return (
    <Card className="min-h-[44px]"> {/* Mobile tap target */}
      <CardHeader>
        <CardTitle className="text-base sm:text-lg">{firstName}</CardTitle>
      </CardHeader>
      <CardContent>
        <Badge variant={status === 'Confirmed' ? 'success' : 'default'}>
          {status === 'Pending' && 'Ausstehend'}
          {status === 'Confirmed' && 'Bestätigt'}
        </Badge>
      </CardContent>
    </Card>
  )
}
```

### Mobile-First Pattern

```tsx
<div className={cn(
  'w-full px-4 py-2',        // Mobile: full width, small padding
  'sm:px-6 sm:py-4',         // Tablet: more padding
  'lg:max-w-7xl lg:mx-auto'  // Desktop: max width, centered
)}>
  {/* Content */}
</div>
```

---

## References

**Related ADRs:**
- ADR-002: Frontend Framework (Next.js integration)
- ADR-006: Type Safety Strategy (TypeScript strict mode)

**Tools:**
- [Shadcn/ui](https://ui.shadcn.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Radix UI](https://www.radix-ui.com/)

**Specifications:**
- [`docs/specification/ui-screens.md`](../../specification/ui-screens.md) - UI requirements
- [`docs/design/design-tokens.md`](../../design/design-tokens.md) - Color tokens
