# Betzenstein Booking - Web

Next.js web application for the Betzenstein booking and approval system.

## Quick Start

### Prerequisites

- Node.js 20+
- npm or yarn

### Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   # Create .env.local
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

Application will be available at http://localhost:3000

### Development Commands

```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm run start

# Type checking
npm run type-check

# Linting
npm run lint

# E2E tests (Phase 5+)
npx playwright test
```

## Project Structure

```
web/
├── app/
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Home page
│   └── globals.css       # Global styles
├── components/
│   └── ui/               # Shadcn/ui components
├── lib/
│   └── utils.ts          # Utility functions
├── public/               # Static assets
├── tailwind.config.ts    # Tailwind configuration
├── tsconfig.json         # TypeScript configuration
└── package.json          # Dependencies
```

## Design System

**UI Components:** Shadcn/ui (copy-paste components)
**Styling:** Tailwind CSS with custom design tokens

**Affiliation Colors:**
- Ingeborg: `#C1DBE3` (light blue)
- Cornelia: `#C7DFC5` (light green)
- Angelika: `#DFAEB4` (light pink)

**Mobile-First:**
- iPhone 8 minimum (375px width)
- 44×44pt minimum tap targets

## Development

**Code Style:**
- TypeScript strict mode
- ESLint configuration (Next.js + TypeScript)
- Functional components with hooks

**State Management:**
- React Hook Form for forms
- TanStack Query for server state
- Zod for validation

**Accessibility:**
- WCAG AA compliance target
- Semantic HTML
- ARIA labels where needed
- Keyboard navigation support

## Testing

**E2E Tests (Phase 5+):**
```bash
# Run all tests
npx playwright test

# Run specific test
npx playwright test tests/calendar.spec.ts

# Run in headed mode
npx playwright test --headed

# Run on specific device
npx playwright test --project="iPhone 8"
```

## Deployment

See [Vercel Deployment](../docs/deployment/vercel-setup.md) (to be created in Phase 8)

**Environment Variables:**
- `NEXT_PUBLIC_API_URL` - API URL (e.g., `https://api.betzenstein.app`)

## Documentation

- [Project Overview](../CLAUDE.md)
- [UI Screens](../docs/specification/ui-screens.md)
- [Design Tokens](../docs/design/design-tokens.md)
- [Component Guidelines](../docs/design/component-guidelines.md)
