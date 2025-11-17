# Design Tokens

## Overview

Design tokens for the Betzenstein booking & approval application. These tokens define the visual language and are implemented via Tailwind CSS configuration.

**Framework:** Tailwind CSS 3+
**Components:** Shadcn/ui (styled with these tokens)
**Target:** Mobile-first, WCAG AA compliant

---

## Color System

### Affiliation Colors

**Purpose:** Visual identification of bookings by affiliation (Ingeborg, Cornelia, Angelika).

```typescript
// tailwind.config.ts
const affiliationColors = {
  ingeborg: '#C1DBE3',  // Light blue
  cornelia: '#C7DFC5',  // Light green
  angelika: '#DFAEB4',  // Light pink
}
```

**Usage:**
- Booking card border/background
- Calendar cell indicator
- Badges/labels

**Requirements:**
- Maintain ≥4.5:1 contrast with text
- Use for visual distinction only (not semantic meaning)

---

### Core Colors (Shadcn Default)

**Primary:**
```typescript
primary: {
  DEFAULT: 'hsl(222.2 47.4% 11.2%)',       // Dark blue-gray
  foreground: 'hsl(210 40% 98%)',          // Near-white
}
```

**Secondary:**
```typescript
secondary: {
  DEFAULT: 'hsl(210 40% 96.1%)',           // Light gray
  foreground: 'hsl(222.2 47.4% 11.2%)',    // Dark blue-gray
}
```

**Accent:**
```typescript
accent: {
  DEFAULT: 'hsl(210 40% 96.1%)',
  foreground: 'hsl(222.2 47.4% 11.2%)',
}
```

**Muted:**
```typescript
muted: {
  DEFAULT: 'hsl(210 40% 96.1%)',
  foreground: 'hsl(215.4 16.3% 46.9%)',
}
```

---

### Semantic Colors

**Success (Confirmed):**
```typescript
success: {
  DEFAULT: 'hsl(142.1 76.2% 36.3%)',       // Green
  foreground: 'hsl(355.7 100% 97.3%)',     // White
}
```

**Destructive (Denied/Canceled):**
```typescript
destructive: {
  DEFAULT: 'hsl(0 84.2% 60.2%)',           // Red
  foreground: 'hsl(210 40% 98%)',          // White
}
```

**Warning (Pending):**
```typescript
warning: {
  DEFAULT: 'hsl(38 92% 50%)',              // Orange
  foreground: 'hsl(48 100% 96.1%)',        // Near-white
}
```

---

### UI Colors

**Background:**
```typescript
background: 'hsl(0 0% 100%)',              // White
foreground: 'hsl(222.2 84% 4.9%)',         // Near-black
```

**Card:**
```typescript
card: {
  DEFAULT: 'hsl(0 0% 100%)',               // White
  foreground: 'hsl(222.2 84% 4.9%)',       // Near-black
}
```

**Popover:**
```typescript
popover: {
  DEFAULT: 'hsl(0 0% 100%)',
  foreground: 'hsl(222.2 84% 4.9%)',
}
```

**Border:**
```typescript
border: 'hsl(214.3 31.8% 91.4%)',          // Light gray
input: 'hsl(214.3 31.8% 91.4%)',           // Light gray
ring: 'hsl(222.2 84% 4.9%)',               // Dark (focus ring)
```

---

## Typography

### Font Families

**Default (System Font Stack):**
```typescript
fontFamily: {
  sans: [
    'Inter',
    'system-ui',
    '-apple-system',
    'BlinkMacSystemFont',
    'Segoe UI',
    'Roboto',
    'sans-serif',
  ],
  mono: [
    'ui-monospace',
    'SFMono-Regular',
    'Menlo',
    'Monaco',
    'Consolas',
    'monospace',
  ],
}
```

**Rationale:**
- Inter: Modern, readable, good on mobile
- System fonts: Fast load, native feel

---

### Font Sizes

```typescript
fontSize: {
  xs: ['0.75rem', { lineHeight: '1rem' }],      // 12px
  sm: ['0.875rem', { lineHeight: '1.25rem' }],  // 14px
  base: ['1rem', { lineHeight: '1.5rem' }],     // 16px (default)
  lg: ['1.125rem', { lineHeight: '1.75rem' }],  // 18px
  xl: ['1.25rem', { lineHeight: '1.75rem' }],   // 20px
  '2xl': ['1.5rem', { lineHeight: '2rem' }],    // 24px
  '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
}
```

**Mobile Recommendations:**
- Body text: `text-base` (16px) - readable on small screens
- Headings: `text-lg` to `text-2xl`
- Small text: `text-sm` (14px minimum)

---

### Font Weights

```typescript
fontWeight: {
  normal: '400',
  medium: '500',
  semibold: '600',
  bold: '700',
}
```

**Usage:**
- Body: `font-normal`
- Buttons: `font-semibold`
- Headings: `font-bold`

---

## Spacing

### Base Scale

Tailwind's default spacing scale (0.25rem = 4px increments):

```typescript
spacing: {
  px: '1px',
  0: '0px',
  0.5: '0.125rem',  // 2px
  1: '0.25rem',     // 4px
  2: '0.5rem',      // 8px
  3: '0.75rem',     // 12px
  4: '1rem',        // 16px
  5: '1.25rem',     // 20px
  6: '1.5rem',      // 24px
  8: '2rem',        // 32px
  10: '2.5rem',     // 40px
  12: '3rem',       // 48px
  16: '4rem',       // 64px
  20: '5rem',       // 80px
  24: '6rem',       // 96px
}
```

---

### Custom Spacing Tokens

**Tap Target (Mobile):**
```typescript
spacing: {
  tap: '44px',  // Minimum tap target (44×44 points per Apple/Android guidelines)
}
```

**Usage:**
```tsx
<button className="min-h-tap min-w-tap">Zustimmen</button>
```

---

## Border Radius

```typescript
borderRadius: {
  none: '0px',
  sm: '0.125rem',    // 2px
  DEFAULT: '0.25rem', // 4px
  md: '0.375rem',    // 6px
  lg: '0.5rem',      // 8px
  xl: '0.75rem',     // 12px
  '2xl': '1rem',     // 16px
  '3xl': '1.5rem',   // 24px
  full: '9999px',    // Circle/pill
}
```

**Usage:**
- Cards: `rounded-lg` (8px)
- Buttons: `rounded-md` (6px)
- Inputs: `rounded-md` (6px)
- Badges: `rounded-full` (pill shape)

---

## Shadows

```typescript
boxShadow: {
  sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
  DEFAULT: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
  md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
  lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
  xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  none: '0 0 #0000',
}
```

**Usage:**
- Cards: `shadow-md`
- Dialogs/modals: `shadow-lg`
- Buttons (hover): `shadow-sm`

---

## Breakpoints

**Mobile-First (Tailwind Default):**

```typescript
screens: {
  sm: '640px',   // Small tablets
  md: '768px',   // Tablets
  lg: '1024px',  // Laptops
  xl: '1280px',  // Desktops
  '2xl': '1536px', // Large desktops
}
```

**Custom (Project-Specific):**
```typescript
screens: {
  'xs': '375px',  // iPhone 8 minimum
  'sm': '640px',
  'md': '768px',
  'lg': '1024px',
  'xl': '1280px',
}
```

**Usage:**
```tsx
<div className="w-full px-4 sm:px-6 md:px-8 lg:px-12">
  {/* Responsive padding */}
</div>
```

---

## Z-Index Layers

**Recommended Scale:**
```typescript
zIndex: {
  0: '0',
  10: '10',      // Default elevated content
  20: '20',      // Dropdowns, popovers
  30: '30',      // Sticky headers
  40: '40',      // Modals, dialogs
  50: '50',      // Toasts, notifications
  auto: 'auto',
}
```

**Usage:**
- Dialogs: `z-40`
- Toasts: `z-50`
- Dropdowns: `z-20`

---

## Transitions

**Duration:**
```typescript
transitionDuration: {
  75: '75ms',
  100: '100ms',
  150: '150ms',   // Default for most UI
  200: '200ms',
  300: '300ms',
  500: '500ms',
  700: '700ms',
  1000: '1000ms',
}
```

**Timing Functions:**
```typescript
transitionTimingFunction: {
  DEFAULT: 'cubic-bezier(0.4, 0, 0.2, 1)',  // ease-in-out
  linear: 'linear',
  in: 'cubic-bezier(0.4, 0, 1, 1)',
  out: 'cubic-bezier(0, 0, 0.2, 1)',
  'in-out': 'cubic-bezier(0.4, 0, 0.2, 1)',
}
```

**Usage:**
```tsx
<button className="transition-colors duration-150">
  {/* Smooth color transition on hover */}
</button>
```

---

## Complete Tailwind Config

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss'

const config: Config = {
  darkMode: ['class'],  // Optional dark mode (not used initially)
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
  ],
  theme: {
    container: {
      center: true,
      padding: '2rem',
      screens: {
        '2xl': '1400px',
      },
    },
    extend: {
      // Affiliation colors
      colors: {
        affiliation: {
          ingeborg: '#C1DBE3',
          cornelia: '#C7DFC5',
          angelika: '#DFAEB4',
        },
        // Shadcn colors (CSS variables)
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },
      },
      // Custom spacing
      spacing: {
        tap: '44px',  // Minimum tap target
      },
      // Responsive breakpoints
      screens: {
        xs: '375px',  // iPhone 8 minimum
      },
      // Border radius
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },
      // Animations (from Shadcn)
      keyframes: {
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
      },
      animation: {
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}

export default config
```

---

## CSS Variables (Shadcn)

### app/globals.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;

    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;

    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;

    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;

    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;

    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;

    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;

    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;

    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;

    --radius: 0.5rem;
  }

  /* Dark mode (optional, not used initially)
  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    ...
  }
  */
}
```

---

## Usage Examples

### Booking Card with Affiliation Color

```tsx
<Card className={cn(
  'min-h-tap',  // Minimum tap target
  'border-l-4',
  affiliation === 'Ingeborg' && 'border-l-affiliation-ingeborg',
  affiliation === 'Cornelia' && 'border-l-affiliation-cornelia',
  affiliation === 'Angelika' && 'border-l-affiliation-angelika',
)}>
  <CardHeader>
    <CardTitle className="text-base sm:text-lg">Anna</CardTitle>
  </CardHeader>
  <CardContent>
    <p className="text-sm text-muted-foreground">4 Personen</p>
  </CardContent>
</Card>
```

---

### Status Badge

```tsx
<Badge variant={
  status === 'Confirmed' ? 'success' :
  status === 'Denied' ? 'destructive' :
  'secondary'
}>
  {status === 'Pending' && 'Ausstehend'}
  {status === 'Confirmed' && 'Bestätigt'}
  {status === 'Denied' && 'Abgelehnt'}
</Badge>
```

---

### Responsive Padding

```tsx
<div className="w-full px-4 sm:px-6 md:px-8 lg:px-12">
  {/* Mobile: 16px, Tablet: 24px, Desktop: 32-48px */}
</div>
```

---

### Button with Transition

```tsx
<Button className="transition-colors duration-150 hover:bg-primary/90">
  Zustimmen
</Button>
```

---

## Accessibility

### Color Contrast

**WCAG AA Requirements:**
- Normal text: ≥4.5:1
- Large text (≥18pt or ≥14pt bold): ≥3:1
- UI components: ≥3:1

**Affiliation Colors (on white background):**
- Ingeborg `#C1DBE3`: Use dark text (e.g., `text-foreground`)
- Cornelia `#C7DFC5`: Use dark text
- Angelika `#DFAEB4`: Use dark text

**Check:** https://webaim.org/resources/contrastchecker/

---

### Focus Indicators

**Default focus ring:**
```tsx
<button className="focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2">
  {/* Clear focus indicator */}
</button>
```

**Required:** Visible focus indicator for keyboard navigation.

---

## Implementation Checklist

- [ ] Add `tailwind.config.ts` with affiliation colors
- [ ] Add `globals.css` with CSS variables
- [ ] Install `tailwindcss-animate` plugin
- [ ] Test affiliation colors on booking cards
- [ ] Test responsive breakpoints (375px minimum)
- [ ] Test focus indicators (keyboard navigation)
- [ ] Verify WCAG AA contrast ratios
- [ ] Test tap targets on mobile (≥44px)

---

## Related Documentation

- [UI Screens](../specification/ui-screens.md) - UI components that use these tokens
- [ADR-005: UI Framework](../architecture/adr-005-ui-framework.md) - Shadcn/ui + Tailwind decision
- [Component Guidelines](component-guidelines.md) - How to use Shadcn components

---

## Summary

These design tokens provide:

- ✅ **Affiliation colors** - Visual distinction (Ingeborg, Cornelia, Angelika)
- ✅ **Mobile-first** - 44px tap targets, responsive spacing
- ✅ **WCAG AA compliant** - Sufficient contrast ratios
- ✅ **Consistent spacing** - Tailwind scale (4px increments)
- ✅ **Semantic colors** - Success/warning/destructive states
- ✅ **AI-friendly** - Standard Tailwind classes

**Next:** Implement Shadcn components using these tokens.
