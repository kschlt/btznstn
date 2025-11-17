# ADR-005: UI Framework - Shadcn/ui + Tailwind CSS

**Status:** Accepted
**Date:** 2025-01-17
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)

---

## Context

We need to choose a UI component library and styling approach for the Betzenstein booking & approval application. The system must provide:

- React components (for Next.js)
- Mobile-first responsive design
- German UI copy
- Accessibility (WCAG AA target)
- Easy customization (affiliation colors, etc.)
- Well-documented for AI implementation

### Requirements from Specifications

From `docs/constraints/technical-constraints.md` and `docs/specification/ui-screens.md`:

- **Mobile-first:** iPhone 8 class minimum (375px)
- **Large tap targets:** 44×44 points minimum
- **High contrast:** Readable in sunlight
- **No hover:** Touch-only interactions
- **Affiliation colors:** Ingeborg (#C1DBE3), Cornelia (#C7DFC5), Angelika (#DFAEB4)
- **AI implementation:** Components AI can use easily

---

## Decision

We will use:
- **Shadcn/ui** for component library
- **Tailwind CSS** for styling
- **Radix UI** (via Shadcn) for accessibility primitives

---

## Rationale

### 1. Shadcn/ui - Copy-Paste Components (Critical for AI)

**Why this matters:** AI needs to add components without complex configuration.

**Shadcn/ui approach:**
- ✅ **Copy-paste, not npm install** - Components added to your codebase
- ✅ **Full control** - Can modify components directly
- ✅ **No black box** - AI can see and understand all component code
- ✅ **AI-friendly** - Simple command: `npx shadcn-ui add button`

**Example (AI workflow):**
```bash
# AI adds Button component
npx shadcn-ui add button

# Creates: components/ui/button.tsx
# AI can now use: <Button>...</Button>
# AI can modify component if needed
```

**Contrast with Material-UI (more complex):**
```bash
npm install @mui/material @emotion/react @emotion/styled
# + ThemeProvider setup
# + Complex theme customization
# + Black box components (can't easily modify)
```

**AI benefit:** Shadcn is simpler, more transparent, easier for AI to work with.

### 2. Tailwind CSS - Utility-First (AI Knows It Extremely Well)

**Why Tailwind:**

#### a) Massive AI Training Data

- ✅ **Most popular CSS framework** - AI knows Tailwind better than any other styling approach
- ✅ **Clear patterns** - `className` strings are self-documenting
- ✅ **No context switching** - CSS-in-markup, no separate stylesheets

**Example:**
```tsx
<button className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded">
  Zustimmen
</button>
```

AI can read and understand this instantly. No separate CSS file to track.

#### b) Mobile-First Built-In

**Requirement:** Works on 375px minimum.

**Tailwind:**
- ✅ **Mobile-first breakpoints** - `sm:`, `md:`, `lg:` prefixes
- ✅ **Responsive utilities** - Everything responsive out-of-box

**Example:**
```tsx
<div className="w-full px-4 sm:px-6 md:px-8 lg:px-12">
  {/* Responsive padding: 16px mobile, 24px tablet, 32px desktop */}
</div>
```

AI knows these patterns well.

#### c) Design Tokens Support

**Requirement:** Custom colors (affiliation colors).

**Tailwind:**
- ✅ **Config-based tokens** - Define once, use everywhere
- ✅ **Custom colors** - Easy to add affiliation colors

**Example (`tailwind.config.ts`):**
```typescript
module.exports = {
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
}

// Usage:
<div className="bg-affiliation-ingeborg">...</div>
```

#### d) Performance

- ✅ **Purge unused CSS** - Only ships CSS actually used
- ✅ **Small bundle** - ~10-20KB after purge
- ✅ **No runtime** - Pure CSS, no JavaScript overhead

### 3. Radix UI - Accessibility Primitives

**Why Radix (via Shadcn):**

#### a) WCAG AA Compliance

**Requirement:** Accessible to all users.

**Radix:**
- ✅ **Keyboard navigation** - Tab, Enter, Esc work correctly
- ✅ **Screen reader support** - ARIA attributes automatic
- ✅ **Focus management** - Trapped focus in modals, etc.

**Example (Dialog):**
```tsx
<Dialog>
  <DialogTrigger>Neue Anfrage</DialogTrigger>
  <DialogContent>
    {/* Radix handles: focus trap, Esc to close, screen reader announcements */}
    <DialogTitle>Buchung erstellen</DialogTitle>
    <DialogDescription>Wähle einen Zeitraum...</DialogDescription>
    {/* Form */}
  </DialogContent>
</Dialog>
```

AI doesn't need to implement accessibility manually - Radix handles it.

#### b) Unstyled Primitives

- ✅ **No default styles** - Shadcn adds Tailwind styles
- ✅ **Composable** - Build complex components from primitives
- ✅ **Flexible** - Can customize everything

### 4. Shadcn/ui Built for Next.js

**Perfect integration:**
- ✅ **App Router compatible** - Server Components work
- ✅ **TypeScript native** - All components typed
- ✅ **Dark mode ready** - (optional, not needed initially)

### 5. No Runtime JavaScript (Mostly)

**Benefit:** Fast, lightweight.

**Tailwind:**
- Pure CSS, no JS (except for components that need it)
- No CSS-in-JS runtime (Emotion, styled-components)
- Faster than component libraries with heavy JS

---

## Alternatives Considered

### Material-UI (MUI)

**Pros:**
- Very mature
- Large ecosystem
- Good docs

**Cons:**
- ❌ **Heavy** - Large bundle size (~300KB)
- ❌ **Complex theming** - ThemeProvider, createTheme, etc.
- ❌ **Black box** - Can't easily modify components
- ❌ **CSS-in-JS runtime** - Emotion adds overhead
- ❌ **More for AI to configure** - Higher error chance

**Decision:** Too heavy, too complex for this app.

---

### Chakra UI

**Pros:**
- Modern, good DX
- Accessibility built-in
- Theming system

**Cons:**
- ❌ **Black box** - npm install, can't modify easily
- ❌ **CSS-in-JS runtime** - Adds overhead
- ❌ **Less AI training data** - Newer than Tailwind/Shadcn

**Decision:** Shadcn gives more control, better AI knowledge.

---

### Ant Design

**Pros:**
- Comprehensive
- Good for admin UIs

**Cons:**
- ❌ **Heavy** - Large bundle
- ❌ **Not mobile-first** - Desktop-focused
- ❌ **Less customizable** - Opinionated design
- ❌ **Less Western** - Chinese-first design patterns

**Decision:** Not mobile-first, too heavy.

---

### Plain Tailwind (No Component Library)

**Pros:**
- Minimal
- Full control

**Cons:**
- ❌ **Build everything** - Buttons, modals, dropdowns from scratch
- ❌ **No accessibility** - Must implement ARIA manually
- ❌ **More work for AI** - Higher error chance

**Decision:** Shadcn gives components + Tailwind styling. Best of both.

---

## Consequences

### Positive

✅ **AI can add components easily** - `npx shadcn-ui add ...`
✅ **AI knows Tailwind extremely well** - Massive training data
✅ **Mobile-first built-in** - Responsive by default
✅ **Full control** - Components in codebase, can modify
✅ **Accessible** - Radix handles ARIA, keyboard, focus
✅ **Fast** - Small bundle, no runtime overhead
✅ **Type-safe** - All components TypeScript

### Negative

⚠️ **Verbose classes** - `className` strings can be long (but readable)
⚠️ **Copy-paste model** - Need to update components manually (vs npm update)

### Neutral

➡️ **Design system** - Need to define tokens (colors, spacing) in Tailwind config
➡️ **Component variants** - Need to define in code (but AI can generate)

---

## Implementation Notes

### Setup

```bash
# Install Tailwind
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# Install Shadcn CLI
npx shadcn-ui@latest init

# Add components as needed
npx shadcn-ui add button
npx shadcn-ui add dialog
npx shadcn-ui add calendar
npx shadcn-ui add form
npx shadcn-ui add select
# etc.
```

### Tailwind Config

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        affiliation: {
          ingeborg: '#C1DBE3',
          cornelia: '#C7DFC5',
          angelika: '#DFAEB4',
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        // etc. (Shadcn adds these)
      },
      spacing: {
        // 44pt minimum tap target (mobile)
        'tap': '44px',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}

export default config
```

### Component Example

```tsx
// components/booking/BookingCard.tsx
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface BookingCardProps {
  firstName: string
  partySize: number
  status: 'Pending' | 'Confirmed' | 'Denied'
  affiliation: 'Ingeborg' | 'Cornelia' | 'Angelika'
}

export function BookingCard({ firstName, partySize, status, affiliation }: BookingCardProps) {
  return (
    <Card className={cn(
      'min-h-tap', // 44px minimum (mobile tap target)
      affiliation === 'Ingeborg' && 'border-l-4 border-l-affiliation-ingeborg',
      affiliation === 'Cornelia' && 'border-l-4 border-l-affiliation-cornelia',
      affiliation === 'Angelika' && 'border-l-4 border-l-affiliation-angelika',
    )}>
      <CardHeader>
        <CardTitle className="text-base sm:text-lg">{firstName}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-1 text-sm">
          <p>{partySize} Personen</p>
          <Badge variant={status === 'Confirmed' ? 'success' : 'default'}>
            {status === 'Pending' && 'Ausstehend'}
            {status === 'Confirmed' && 'Bestätigt'}
            {status === 'Denied' && 'Abgelehnt'}
          </Badge>
        </div>
      </CardContent>
    </Card>
  )
}
```

### German Copy Integration

```tsx
// lib/copy.ts - German UI copy
export const copy = {
  booking: {
    create: 'Neue Anfrage',
    edit: 'Bearbeiten',
    cancel: 'Stornieren',
    approve: 'Zustimmen',
    deny: 'Ablehnen',
    status: {
      pending: 'Ausstehend',
      confirmed: 'Bestätigt',
      denied: 'Abgelehnt',
    },
  },
  // etc. from specs/error-handling.md and specs/notifications.md
}

// Usage:
<Button>{copy.booking.approve}</Button>
```

### Mobile-First Example

```tsx
// components/calendar/CalendarGrid.tsx
export function CalendarGrid() {
  return (
    <div className={cn(
      // Mobile: full width, small padding
      'w-full px-4 py-2',
      // Tablet: more padding
      'sm:px-6 sm:py-4',
      // Desktop: max width, centered
      'lg:max-w-7xl lg:mx-auto lg:px-8'
    )}>
      {/* Calendar cells */}
      <div className="grid grid-cols-7 gap-1 sm:gap-2">
        {days.map(day => (
          <button
            key={day}
            className={cn(
              // Minimum tap target
              'min-h-tap min-w-tap',
              // Responsive text
              'text-xs sm:text-sm',
              // Touch-friendly
              'rounded-md transition-colors',
              'hover:bg-gray-100 active:bg-gray-200'
            )}
          >
            {day}
          </button>
        ))}
      </div>
    </div>
  )
}
```

---

## Validation

### Component Check

```bash
# List installed Shadcn components
ls components/ui/
```

**Expected:** button.tsx, dialog.tsx, etc.

### Tailwind Build

```bash
npm run build
```

**Expected:** CSS purged, small bundle size.

### Accessibility Check

```bash
npm install -D @axe-core/react
# Add to app/layout.tsx in dev mode
```

**Expected:** Zero accessibility errors.

### Mobile Test

Open DevTools → Responsive mode → 375px width.

**Expected:** All elements visible, tap targets ≥44px.

---

## References

- [Shadcn/ui Documentation](https://ui.shadcn.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [Radix UI Documentation](https://www.radix-ui.com/)
- [Tailwind Mobile-First](https://tailwindcss.com/docs/responsive-design)
- UI Screens Spec: `docs/specification/ui-screens.md`
- Design Tokens: `docs/design/design-tokens.md` (to be created)

---

## Related ADRs

- [ADR-002: Frontend Framework](adr-002-frontend-framework.md) - Next.js integration
- [ADR-006: Type Safety Strategy](adr-006-type-safety.md) - TypeScript strict mode

---

## Changelog

- **2025-01-17:** Initial decision - Shadcn/ui + Tailwind CSS chosen for UI framework
