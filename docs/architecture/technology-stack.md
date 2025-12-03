# Technology Stack

Quick reference for technologies used in this project. For architectural decisions and rationale, see the relevant ADRs.

---

## Stack Summary

| Layer | Technology | Version | ADR |
|-------|-----------|---------|-----|
| **API Framework** | FastAPI | Latest | [ADR-001](adr-001-backend-framework.md) |
| **API Language** | Python | 3.11+ | - |
| **Web Framework** | Next.js (App Router) | 14+ | [ADR-002](adr-002-frontend-framework.md) |
| **Web Language** | TypeScript | 5+ | [ADR-006](adr-006-type-safety.md) |
| **Database** | PostgreSQL | 15+ | [ADR-012](adr-012-postgresql-database.md) |
| **ORM** | SQLAlchemy | 2.0+ | [ADR-013](adr-013-sqlalchemy-orm.md) |
| **Migrations** | Alembic | Latest | [ADR-014](adr-014-alembic-migrations.md) |
| **UI Library** | Shadcn/ui | Latest | [ADR-005](adr-005-ui-framework.md) |
| **CSS Framework** | Tailwind CSS | 3+ | [ADR-005](adr-005-ui-framework.md) |
| **Email Service** | Resend | - | [ADR-004](adr-004-email-service.md) |
| **API Hosting** | Fly.io | - | [ADR-015](adr-015-flyio-backend-hosting.md) |
| **Database Hosting** | Fly.io Postgres | - | [ADR-016](adr-016-flyio-postgres-hosting.md) |
| **Web Hosting** | Vercel | - | [ADR-017](adr-017-vercel-frontend-hosting.md) |
| **CI/CD** | GitHub Actions | - | [ADR-018](adr-018-github-actions-cicd.md) |
| **Type Safety (API)** | mypy + Pydantic | Latest | [ADR-006](adr-006-type-safety.md) |
| **Type Safety (Web)** | TypeScript + Zod | 5+ / 3+ | [ADR-006](adr-006-type-safety.md) |
| **Testing (Backend)** | Pytest | Latest | [ADR-020](adr-020-backend-testing-framework.md) |
| **Testing (Frontend Unit)** | Vitest + React Testing Library | Latest | [ADR-022](adr-022-frontend-unit-component-testing.md) |
| **Testing (Frontend E2E)** | Playwright | Latest | [ADR-021](adr-021-frontend-testing-framework.md) |
| **Authentication** | Token-based (HMAC) | - | [ADR-019](adr-019-authentication-authorization.md) |

---

## Key Libraries

### API
- `uvicorn` - ASGI server
- `httpx` - Async HTTP client
- `python-jose` - JWT handling
- `pytest-asyncio` - Async test support
- `coverage.py` - Code coverage

### Web
- `react-hook-form` - Form state management
- `@tanstack/react-query` - Server state management
- `date-fns` - Date manipulation
- `lucide-react` - Icons
- `clsx` - Conditional CSS classes

---

For detailed rationale and constraints, see the relevant ADRs. For system architecture overview, see [README.md](README.md).
