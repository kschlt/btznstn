# Technology Stack

## Overview

This document provides a complete reference of all technologies, frameworks, libraries, and tools used in the Betzenstein booking & approval application.

**Last Updated:** 2025-01-17

---

## Stack Summary

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **API Framework** | FastAPI | Latest | REST API, async Python |
| **API Language** | Python | 3.11+ | Application logic |
| **Web Framework** | Next.js (App Router) | 14+ | React framework, SSR/SSG |
| **Web Language** | TypeScript | 5+ | Type-safe JavaScript |
| **Database** | PostgreSQL | 15+ | Relational database |
| **ORM** | SQLAlchemy | 2.0+ | Python ORM, migrations |
| **UI Library** | Shadcn/ui | Latest | Copy-paste React components |
| **CSS Framework** | Tailwind CSS | 3+ | Utility-first CSS |
| **Email Service** | Resend | - | Transactional email API |
| **API Hosting** | Fly.io | - | Container hosting (Frankfurt) |
| **Database Hosting** | Fly.io Postgres | - | Managed PostgreSQL (Frankfurt) |
| **Web Hosting** | Vercel | - | Next.js hosting + CDN |
| **CI/CD** | GitHub Actions | - | Automated testing + deployment |

---

## API Stack

### Core Framework

**FastAPI**
- **Version:** Latest stable
- **Purpose:** REST API framework
- **Key Features:**
  - Auto-generated OpenAPI docs
  - Pydantic validation
  - Async/await native
  - High performance
- **Documentation:** https://fastapi.tiangolo.com/
- **ADR:** [ADR-001: API Framework](adr-001-backend-framework.md)

### Language

**Python**
- **Version:** 3.11+
- **Type Hints:** PEP 484 (required)
- **Features Used:**
  - Async/await
  - Type unions (`str | None`)
  - Pattern matching (optional)
- **Style Guide:** PEP 8 + Ruff

### Database & ORM

**PostgreSQL**
- **Version:** 15+
- **Hosting:** Fly.io Postgres (Frankfurt)
- **Features Used:**
  - ACID transactions
  - Range types (`daterange`)
  - GiST indexes
  - JSON support (optional)
- **Documentation:** https://www.postgresql.org/docs/
- **ADR:** [ADR-003: Database & ORM](adr-003-database-orm.md)

**SQLAlchemy**
- **Version:** 2.0+
- **Purpose:** ORM + query builder
- **Features Used:**
  - Async support (`AsyncSession`)
  - Type-safe ORM (Mapped)
  - Relationship management
  - Connection pooling
- **Driver:** asyncpg
- **Documentation:** https://docs.sqlalchemy.org/en/20/

**Alembic**
- **Version:** Latest
- **Purpose:** Database migrations
- **Features:**
  - Auto-generate migrations
  - Reversible migrations
  - Version control
- **Documentation:** https://alembic.sqlalchemy.org/

### Type Safety

**Mypy**
- **Version:** Latest
- **Mode:** Strict
- **Purpose:** Static type checking
- **Plugins:**
  - Pydantic mypy plugin
  - SQLAlchemy mypy plugin
- **Documentation:** https://mypy.readthedocs.io/
- **ADR:** [ADR-006: Type Safety Strategy](adr-006-type-safety.md)

**Pydantic**
- **Version:** v2+
- **Purpose:** Runtime validation + serialization
- **Features:**
  - FastAPI integration
  - Strict mode
  - Email validation
  - Custom validators
- **Documentation:** https://docs.pydantic.dev/

### Linting & Formatting

**Ruff**
- **Version:** Latest
- **Purpose:** Fast Python linter + formatter
- **Rules Enabled:**
  - Flake8 (`E`, `F`)
  - Type annotations (`ANN`)
  - Security (`S`)
  - Import sorting (`I`)
- **Documentation:** https://docs.astral.sh/ruff/

### Testing

**Pytest**
- **Version:** Latest
- **Purpose:** Unit + integration testing
- **Plugins:**
  - pytest-asyncio (async tests)
  - pytest-cov (code coverage)
- **Documentation:** https://docs.pytest.org/
- **ADR:** [ADR-008: Testing Strategy](adr-008-testing-strategy.md)

**Coverage.py**
- **Purpose:** Code coverage tracking
- **Target:** >80%

**Faker**
- **Purpose:** Test data generation
- **Locale:** de_DE (German)
- **Documentation:** https://faker.readthedocs.io/

### Email

**Resend**
- **Purpose:** Transactional email delivery
- **API:** REST (Python SDK)
- **Free Tier:** 100 emails/day
- **Documentation:** https://resend.com/docs
- **ADR:** [ADR-004: Email Service](adr-004-email-service.md)

### Key Libraries

| Library | Purpose |
|---------|---------|
| `uvicorn` | ASGI server |
| `httpx` | Async HTTP client |
| `python-jose` | JWT handling |
| `passlib` | Password hashing (if needed) |
| `python-multipart` | Form data parsing |

---

## Web Stack

### Core Framework

**Next.js**
- **Version:** 14+
- **Router:** App Router (not Pages Router)
- **Purpose:** React framework with SSR/SSG
- **Features Used:**
  - Server Components
  - App Router
  - API Routes (minimal, if needed)
  - Image optimization
- **Documentation:** https://nextjs.org/docs
- **ADR:** [ADR-002: Web Framework](adr-002-frontend-framework.md)

**React**
- **Version:** 18+ (bundled with Next.js)
- **Features Used:**
  - Hooks (useState, useEffect, etc.)
  - Server Components
  - Suspense

### Language

**TypeScript**
- **Version:** 5+
- **Mode:** Strict
- **Config:** tsconfig.json with strict flags
- **Documentation:** https://www.typescriptlang.org/

### UI Components

**Shadcn/ui**
- **Version:** Latest
- **Purpose:** Copy-paste React components
- **Base:** Radix UI primitives
- **Features:**
  - Accessible (ARIA, keyboard nav)
  - Customizable
  - Not an npm package (copy-paste)
- **Documentation:** https://ui.shadcn.com/
- **ADR:** [ADR-005: UI Framework](adr-005-ui-framework.md)

**Radix UI**
- **Version:** Latest
- **Purpose:** Unstyled accessible primitives
- **Components Used:**
  - Dialog
  - Select
  - Calendar
  - Form
- **Documentation:** https://www.radix-ui.com/

### Styling

**Tailwind CSS**
- **Version:** 3+
- **Purpose:** Utility-first CSS framework
- **Features:**
  - Mobile-first responsive design
  - Custom design tokens (affiliation colors)
  - Purge unused CSS
- **Plugins:**
  - tailwindcss-animate
- **Documentation:** https://tailwindcss.com/
- **ADR:** [ADR-005: UI Framework](adr-005-ui-framework.md)

### Validation

**Zod**
- **Version:** 3+
- **Purpose:** Runtime validation + TypeScript types
- **Usage:**
  - Form validation
  - API response validation
  - Schema-first approach
- **Integration:** React Hook Form resolver
- **Documentation:** https://zod.dev/
- **ADR:** [ADR-006: Type Safety Strategy](adr-006-type-safety.md)

### Forms

**React Hook Form**
- **Version:** Latest
- **Purpose:** Form state management
- **Features:**
  - Uncontrolled components
  - Zod integration
  - Validation
- **Documentation:** https://react-hook-form.com/

### Data Fetching

**TanStack Query (React Query)**
- **Version:** 5+
- **Purpose:** Server state management
- **Features:**
  - Caching
  - Refetching
  - Optimistic updates
- **Documentation:** https://tanstack.com/query/

### Testing

**Playwright**
- **Version:** Latest
- **Purpose:** E2E + integration testing
- **Browsers:** Chromium, Firefox, WebKit
- **Devices:** Desktop + iPhone 8
- **Documentation:** https://playwright.dev/
- **ADR:** [ADR-008: Testing Strategy](adr-008-testing-strategy.md)

**Axe-core**
- **Version:** Latest (via @axe-core/playwright)
- **Purpose:** Accessibility testing
- **Target:** WCAG AA compliance
- **Documentation:** https://github.com/dequelabs/axe-core

### Linting & Formatting

**ESLint**
- **Version:** Latest
- **Config:** Next.js + TypeScript recommended
- **Plugins:**
  - @typescript-eslint
  - eslint-plugin-react
  - eslint-plugin-jsx-a11y
- **Documentation:** https://eslint.org/

**Prettier** (Optional)
- **Version:** Latest
- **Purpose:** Code formatting
- **Integration:** ESLint plugin

### Key Libraries

| Library | Purpose |
|---------|---------|
| `clsx` | Conditional CSS classes |
| `date-fns` | Date manipulation |
| `lucide-react` | Icons |

---

## Hosting & Deployment

### API Hosting

**Fly.io**
- **Region:** Frankfurt (FRA)
- **Purpose:** Container hosting for FastAPI
- **Features:**
  - Docker-based deployment
  - Zero-downtime deploys
  - Health checks
  - Auto-scaling (future)
  - Private networking (`.internal`)
- **Free Tier:** 3 shared-cpu VMs, 3GB storage
- **Documentation:** https://fly.io/docs/
- **ADR:** [ADR-007: Deployment Strategy](adr-007-deployment.md)

### Database Hosting

**Fly.io Postgres**
- **Region:** Frankfurt (FRA, co-located with backend)
- **Version:** PostgreSQL 15+
- **Purpose:** Managed PostgreSQL database
- **Features:**
  - Automatic backups
  - Monitoring dashboard
  - Scaling options
  - Private network (`.internal` hostname)
  - Always on (no shutdown/pause)
- **Free Tier:** 3GB storage (included in Fly.io free tier)
- **Documentation:** https://fly.io/docs/postgres/
- **ADR:** [ADR-003: Database & ORM](adr-003-database-orm.md)

### Web Hosting

**Vercel**
- **Purpose:** Next.js hosting + global CDN
- **Features:**
  - Zero-config deployment
  - Preview deployments (per PR)
  - Edge caching
  - Automatic HTTPS
  - Global CDN (Cloudflare-backed)
- **Free Tier:** Unlimited deployments, 100GB bandwidth/month
- **Documentation:** https://vercel.com/docs
- **ADR:** [ADR-007: Deployment Strategy](adr-007-deployment.md)

### CI/CD

**GitHub Actions**
- **Purpose:** Automated testing + deployment
- **Workflows:**
  - Type checking (Mypy + TSC)
  - Linting (Ruff + ESLint)
  - Testing (Pytest + Playwright)
  - Deployment (Fly.io + Vercel)
- **Free Tier:** 2000 minutes/month (private repos)
- **Documentation:** https://docs.github.com/en/actions
- **ADR:** [ADR-007: Deployment Strategy](adr-007-deployment.md)

---

## Development Tools

### Local Development

**Docker** (Optional)
- **Purpose:** Local Postgres (if not using Fly.io dev DB)
- **Compose:** docker-compose.yml for services

**Fly.io CLI (flyctl)**
- **Purpose:** Deploy backend, manage Postgres
- **Installation:** https://fly.io/docs/hands-on/install-flyctl/

**Vercel CLI**
- **Purpose:** Deploy frontend, manage env vars
- **Installation:** `npm install -g vercel`

### Code Editors

**VS Code** (Recommended)
- **Extensions:**
  - Python (Microsoft)
  - Pylance (type checking)
  - Ruff (linting)
  - ESLint
  - Prettier
  - Tailwind CSS IntelliSense

**PyCharm** (Alternative)
- **Features:**
  - Built-in type checking
  - Database tools
  - Better refactoring

### Version Control

**Git**
- **Hosting:** GitHub
- **Branch Strategy:**
  - `main` - production
  - `claude/*` - feature branches (AI development)
- **Protected Branches:** `main` (later: require tests)

---

## Environment Variables

### API (FastAPI)

| Variable | Purpose | Example |
|----------|---------|---------|
| `DATABASE_URL` | Postgres connection string | `postgres://user:pass@app-db.internal:5432/db` |
| `SECRET_KEY` | JWT signing key | (generated, 32+ chars) |
| `RESEND_API_KEY` | Resend email API key | `re_...` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `https://betzenstein.app` |
| `PYTHON_ENV` | Environment | `development` / `production` |
| `LOG_LEVEL` | Logging level | `INFO` / `DEBUG` |

### Web (Next.js)

| Variable | Purpose | Example |
|----------|---------|---------|
| `NEXT_PUBLIC_API_URL` | API API URL | `https://api.betzenstein.app` |

**Note:** `NEXT_PUBLIC_*` variables are exposed to browser.

---

## Package Management

### API (Python)

**pip + requirements.txt**
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies (pytest, mypy, ruff)

**Installation:**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Web (Node.js)

**npm + package.json**
- `dependencies` - Production packages
- `devDependencies` - Development packages

**Installation:**
```bash
npm ci  # CI (clean install)
npm install  # Local development
```

---

## Versioning Strategy

**API:**
- API versioned via URL: `/api/v1/...`
- Breaking changes = new version (`/api/v2/...`)

**Web:**
- Versioned with backend API
- Semantic versioning (later)

**Database:**
- Migrations tracked by Alembic
- Backward-compatible migrations (add nullable columns first)

---

## Monitoring & Observability (Future)

**Logging:**
- API: Python `logging` module (structured JSON logs)
- Web: Vercel Analytics

**Monitoring:**
- Fly.io metrics (CPU, memory, requests)
- Vercel Analytics (page views, performance)

**Error Tracking:**
- Sentry (future)

**Alerting:**
- Email or Slack (future)

---

## Security

### Authentication

**Token-based (signed URLs)**
- HMAC-SHA256 signed tokens
- No expiry (per BR-010)
- Role-by-link (no login)

### Rate Limiting

**Implemented in FastAPI middleware:**
- 10 bookings/day/email (BR-012)
- 30 requests/hour/IP
- 5 recovery requests/hour/email

### CORS

**FastAPI CORS middleware:**
- `ALLOWED_ORIGINS` environment variable
- Credentials allowed (cookies, if needed)

### HTTPS

**Enforced:**
- Fly.io: `force_https: true`
- Vercel: Automatic HTTPS

---

## Performance Targets

| Metric | Target |
|--------|--------|
| API response time (p95) | < 500ms |
| Calendar load time | < 1s |
| Email delivery time | < 5s |
| Lighthouse Performance | > 90 |
| Lighthouse Accessibility | 100 |

---

## Browser Support

**Target:** Browsers released 2023+

**Specific:**
- Chrome 115+
- Safari 16+ (iOS 16+)
- Firefox 115+
- Edge 115+

**Mobile:**
- iPhone 8 class minimum (375×667px)
- Android 10+ (Chrome)

---

## Accessibility

**Target:** WCAG AA

**Tools:**
- Axe-core (automated testing)
- Manual keyboard navigation testing
- Screen reader testing (NVDA, VoiceOver)

**Requirements:**
- Semantic HTML
- ARIA labels where needed
- Focus indicators
- Sufficient color contrast (4.5:1 minimum)
- 44×44pt minimum tap targets (mobile)

---

## Documentation

**Code Documentation:**
- Python: Docstrings (Google style)
- TypeScript: JSDoc comments

**Architecture:**
- ADRs (Architecture Decision Records)
- This document (technology-stack.md)

**API:**
- Auto-generated OpenAPI docs (FastAPI `/docs`)

**User:**
- German UI copy in-app
- No separate user manual (intuitive UI)

---

## Cost Estimate (MVP)

| Service | Tier | Monthly Cost |
|---------|------|--------------|
| Fly.io (backend + DB) | Free tier | $0 (within limits) |
| Vercel (frontend) | Hobby | $0 |
| Resend (email) | Free tier | $0 (100/day) |
| GitHub (repo + Actions) | Free | $0 |
| **Total** | | **$0** |

**Scaling Costs (estimate):**
- Fly.io: ~$1-5/month for dedicated resources
- Vercel: ~$20/month for Pro (if exceed free tier)
- Resend: ~$20/month for 10,000 emails

---

## Related Documentation

- [Architecture Overview](README.md)
- [ADR-001: API Framework](adr-001-backend-framework.md)
- [ADR-002: Web Framework](adr-002-frontend-framework.md)
- [ADR-003: Database & ORM](adr-003-database-orm.md)
- [ADR-004: Email Service](adr-004-email-service.md)
- [ADR-005: UI Framework](adr-005-ui-framework.md)
- [ADR-006: Type Safety Strategy](adr-006-type-safety.md)
- [ADR-007: Deployment Strategy](adr-007-deployment.md)
- [ADR-008: Testing Strategy](adr-008-testing-strategy.md)

---

## Summary

This stack is optimized for:

- ✅ **AI-driven development** - Well-documented, popular technologies
- ✅ **Type safety** - Mypy + Pydantic + TypeScript + Zod
- ✅ **Mobile-first** - Tailwind responsive + Playwright mobile testing
- ✅ **Developer experience** - Fast feedback loops, auto-generated docs
- ✅ **Cost-effective** - Free tier for MVP, affordable scaling
- ✅ **Performance** - Async Python + Next.js SSR + global CDN
- ✅ **Accessibility** - WCAG AA target, automated testing

**Next Steps:** Proceed to design documentation for detailed API specs, database schema, and component guidelines.
