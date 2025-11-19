# ADR-002: Web Framework - Next.js App Router

**Status:** Accepted
**Date:** 2025-01-17
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)

---

## Context

We need to choose a frontend framework for the Betzenstein booking & approval application. The framework must support:

- React-based UI development
- TypeScript support
- Mobile-first responsive design (iPhone 8 class minimum)
- Integration with Shadcn/ui components
- Easy deployment to Vercel
- Well-documented for AI implementation

### Requirements from Specifications

From `docs/constraints/technical-constraints.md`:

- **Mobile-first:** Works on iPhone 8 class (375×667px minimum)
- **No SSR needed:** Private app, no SEO requirements
- **TypeScript strict:** All code type-safe
- **AI implementation:** Framework AI knows extremely well
- **German UI:** All copy hardcoded (no i18n initially)

---

## Decision

We will use **Next.js 14+ with App Router** as the frontend framework.

---

## Rationale

### 1. AI-Friendly (Critical)

**Why this matters:** All implementation will be done by Claude Code.

**Next.js benefits:**
- ✅ **Massive training data** - AI knows Next.js better than any other React framework
- ✅ **Official Vercel docs** - Excellent documentation AI can reference
- ✅ **Standard patterns** - Clear conventions (App Router structure)
- ✅ **Large ecosystem** - Most tutorials, examples, Stack Overflow answers

**Evidence:** Next.js is the most popular React framework. AI consistently generates correct Next.js code.

### 2. App Router (vs Pages Router)

**Choice:** App Router (newer, current standard)

**Why App Router:**
- ✅ **Current recommendation** - Vercel's official guidance
- ✅ **Better TypeScript** - Stricter types
- ✅ **Server Components** - Even though we don't need SSR, it's the standard pattern
- ✅ **More training data** - AI's recent training includes App Router heavily
- ✅ **Better structure** - File-based routing clearer

**Why not Pages Router:**
- ⚠️ Being phased out (maintenance mode)
- ⚠️ AI might mix patterns (older training data)

### 3. Vercel Deployment (Zero Config)

**Requirement:** Easy deployment to Vercel.

**Next.js on Vercel:**
- ✅ **Zero configuration** - Push to GitHub, Vercel deploys
- ✅ **Automatic optimization** - Image optimization, CDN, etc.
- ✅ **Preview deployments** - Every PR gets preview URL
- ✅ **Environment variables** - Simple secret management

**AI benefit:** AI doesn't need to configure deployment. Just works.

### 4. Shadcn/ui Integration

**Requirement:** Use Shadcn/ui components.

**Next.js + Shadcn:**
- ✅ **Perfect match** - Shadcn built for Next.js App Router
- ✅ **Copy-paste components** - AI can add components easily
- ✅ **Tailwind integration** - Shadcn uses Tailwind (AI knows Tailwind very well)

**Example:**
```bash
npx shadcn-ui@latest add button
```

AI can run this command and immediately use the Button component.

### 5. TypeScript Native

**Requirement:** TypeScript strict mode.

**Next.js:**
- ✅ **First-class TypeScript** - Built-in support
- ✅ **Automatic types** - Page props, route params auto-typed
- ✅ **Strict by default** - Config includes strict mode

**Example:**
```typescript
// app/bookings/[id]/page.tsx
type PageProps = {
  params: { id: string }
  searchParams: { [key: string]: string | string[] | undefined }
}

export default async function BookingDetailPage({ params }: PageProps) {
  const booking = await fetchBooking(params.id)
  return <BookingDetail booking={booking} />
}
```

TypeScript catches errors before AI code runs.

### 6. Mobile-First Support

**Requirement:** iPhone 8 class (375px minimum).

**Next.js:**
- ✅ **Responsive by default** - Viewport meta tags
- ✅ **Tailwind integration** - Responsive utilities (`sm:`, `md:`, `lg:`)
- ✅ **Image optimization** - Automatic srcset for different sizes

**Example:**
```tsx
<div className="w-full px-4 sm:px-6 lg:px-8">
  {/* Responsive padding */}
</div>
```

AI knows Tailwind responsive patterns well.

### 7. API Integration

**Benefit:** Can add API routes if needed (though we have separate FastAPI backend).

**Next.js:**
- ✅ **API routes** - `/app/api/` directory
- ✅ **Route handlers** - For webhooks, etc.
- ✅ **Middleware** - For auth checks (though we use backend tokens)

**Use case:** Could add API routes for client-side operations if needed later.

### 8. Performance

**Requirement:** Fast load times (< 1s for calendar).

**Next.js:**
- ✅ **Automatic code splitting** - Only load what's needed
- ✅ **Image optimization** - WebP, lazy loading
- ✅ **CDN delivery** - Vercel's global CDN

---

## Alternatives Considered

### Vite + React (SPA)

**Pros:**
- Lighter than Next.js
- Faster dev server
- Simpler (just React)

**Cons:**
- ❌ **Less training data** - AI knows Next.js better
- ❌ **Manual routing** - Need React Router (more config)
- ❌ **No conventions** - More decisions for AI to make
- ❌ **Manual optimization** - Image optimization, code splitting

**Decision:** Simplicity not worth the trade-off. Next.js benefits (AI familiarity, Vercel integration) outweigh.

---

### Next.js Pages Router

**Pros:**
- Mature, stable
- Lots of examples

**Cons:**
- ❌ **Being phased out** - Vercel recommends App Router
- ❌ **Mixed AI training** - AI might confuse patterns
- ❌ **Less modern** - Missing latest features

**Decision:** App Router is the future, use it.

---

### Remix

**Pros:**
- Modern, similar to Next.js App Router
- Great TypeScript support

**Cons:**
- ❌ **Less training data** - Newer, less common
- ❌ **Not Vercel-native** - Deployment more complex
- ❌ **Smaller ecosystem** - Fewer Shadcn examples

**Decision:** Next.js has more AI training data.

---

## Consequences

### Positive

✅ **AI can implement quickly** - Massive Next.js knowledge
✅ **Zero deployment config** - Vercel auto-deploys
✅ **Shadcn perfect fit** - Components work out-of-box
✅ **TypeScript strict** - Catch errors early
✅ **Mobile-ready** - Responsive by default
✅ **Fast performance** - Automatic optimization

### Negative

⚠️ **Heavier than needed** - We don't need SSR, but it's fine
⚠️ **Vercel lock-in** (minor) - But we chose Vercel anyway
⚠️ **Learning curve** (minor) - App Router concepts (but AI handles)

### Neutral

➡️ **React ecosystem** - Standard React patterns
➡️ **Node.js dependency** - Dev environment needs Node
➡️ **Build step required** - But automated on Vercel

---

## Implementation Notes

### Project Structure

```
/web/
├── app/
│   ├── layout.tsx           # Root layout (German, metadata)
│   ├── page.tsx             # Landing page (redirect to calendar)
│   ├── calendar/
│   │   └── page.tsx         # Public calendar view
│   ├── bookings/
│   │   ├── new/
│   │   │   └── page.tsx     # Create booking form
│   │   └── [id]/
│   │       └── page.tsx     # Booking details
│   └── approver/
│       └── page.tsx         # Approver overview (Outstanding/History)
├── components/
│   ├── ui/                  # Shadcn components
│   ├── calendar/            # Calendar components
│   │   ├── CalendarGrid.tsx
│   │   ├── BookingCell.tsx
│   │   └── MonthView.tsx
│   ├── booking/             # Booking components
│   │   ├── BookingForm.tsx
│   │   ├── BookingDetail.tsx
│   │   └── CancelDialog.tsx
│   └── approver/            # Approver components
│       ├── OutstandingList.tsx
│       └── HistoryList.tsx
├── lib/
│   ├── api/                 # API client (fetch calls to FastAPI)
│   │   ├── client.ts
│   │   ├── bookings.ts
│   │   └── approvals.ts
│   ├── validations/         # Zod schemas
│   │   └── booking.ts
│   └── utils/
│       ├── dates.ts         # Date formatting (German)
│       └── tokens.ts        # Token parsing
├── types/
│   ├── booking.ts           # TypeScript types (from API)
│   ├── approval.ts
│   └── api.ts
├── public/
│   └── ...                  # Static assets
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── package.json
```

### Key Dependencies

```json
{
  "dependencies": {
    "next": "^14.1.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@radix-ui/react-*": "^1.0.0",  // Shadcn dependencies
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0",
    "zod": "^3.22.0",
    "date-fns": "^3.0.0"              // Date handling
  },
  "devDependencies": {
    "typescript": "^5.3.0",
    "@types/node": "^20.10.0",
    "@types/react": "^18.2.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "eslint": "^8.56.0",
    "eslint-config-next": "^14.1.0",
    "prettier": "^3.1.0",
    "@playwright/test": "^1.40.0"    // E2E testing
  }
}
```

### Configuration

**next.config.js:**
```javascript
/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },
}

module.exports = nextConfig
```

**tsconfig.json:**
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### Deployment (Vercel)

**Automatic:**
1. Connect GitHub repo to Vercel
2. Set environment variables:
   - `NEXT_PUBLIC_API_URL=https://api.betzenstein.app`
3. Push to `main` branch
4. Vercel auto-deploys

**Manual:**
```bash
vercel --prod
```

---

## Validation

### Type Check

```bash
npm run build
```

**Expected:** Zero TypeScript errors.

### Lint Check

```bash
npm run lint
```

**Expected:** Zero ESLint errors.

### Dev Server

```bash
npm run dev
```

**Expected:** Runs on `http://localhost:3000`, hot reload works.

---

## References

- [Next.js Documentation](https://nextjs.org/docs)
- [App Router Guide](https://nextjs.org/docs/app)
- [Vercel Deployment Docs](https://vercel.com/docs)
- [Shadcn/ui](https://ui.shadcn.com/)
- Technical Constraints: `docs/constraints/technical-constraints.md`

---

## Related ADRs

- [ADR-001: API Framework](adr-001-backend-framework.md) - FastAPI integration
- [ADR-005: UI Framework](adr-005-ui-framework.md) - Shadcn/ui + Tailwind
- [ADR-006: Type Safety Strategy](adr-006-type-safety.md) - TypeScript + Zod
- [ADR-017: Vercel Frontend Hosting](adr-017-vercel-frontend-hosting.md) - Vercel deployment

---

## Changelog

- **2025-01-17:** Initial decision - Next.js 14 App Router chosen for frontend framework
