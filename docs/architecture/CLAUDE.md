# Architecture - CLAUDE Guide

## What's in This Section

Architecture decisions and system design:
- **README.md** - System overview, architecture diagram, principles
- **technology-stack.md** - Complete tech stack with rationale
- **adr-001 to adr-008** - Architecture Decision Records (why we chose each technology)

## When to Read This

Read before implementation:
- **README.md** - Understand system architecture
- **technology-stack.md** - See all technologies and versions
- **Specific ADRs** - Understand why decisions were made

## Tech Stack Quick Reference

| Component | Technology | Why (see ADR) |
|-----------|-----------|---------------|
| API | FastAPI + Python 3.11+ | ADR-001 |
| Web | Next.js 14 (App Router) | ADR-002 |
| Database | PostgreSQL 15+ on Fly.io | ADR-003 |
| ORM | SQLAlchemy 2.0 | ADR-003 |
| Email | Resend | ADR-004 |
| UI | Shadcn/ui + Tailwind | ADR-005 |
| Type Safety | Mypy + Pydantic + TypeScript + Zod | ADR-006 |
| Deployment | Fly.io + Vercel + GitHub Actions | ADR-007 |
| Testing | Pytest + Playwright | ADR-008 |

## Architectural Principles

**1. AI-First:**
- Well-documented, popular technologies
- Standard patterns
- Strong type safety (catch errors early)

**2. Type Safety:**
- Python type hints + mypy strict
- TypeScript strict mode
- Runtime validation (Pydantic + Zod)

**3. Separation of Concerns:**
```
API Layer (FastAPI routes)
    ↓
Service Layer (business logic)
    ↓
Repository Layer (data access)
    ↓
Model Layer (ORM models)
```

**4. Stateless:**
- No sessions
- Token-based auth
- Email-first access

## Key Patterns

**API:**
- Repository pattern for data access
- Service layer for business logic
- Pydantic models for validation
- Async/await for I/O

**Web:**
- Server Components (Next.js App Router)
- Shadcn/ui components (copy-paste)
- React Query for server state
- Zod for form validation

**Testing:**
- Test-first (BDD)
- API: Pytest (unit + integration)
- Web: Playwright (E2E)

## Database Architecture

**Fly.io Postgres co-located with backend:**
- Ultra-low latency (.internal network)
- Always on (no pausing)
- Same platform as backend

**Schema:**
- 3NF normalized
- Foreign keys enforced
- Migrations with Alembic

## API Design

**RESTful:**
- `GET /bookings` - List
- `POST /bookings` - Create
- `PATCH /bookings/{id}` - Edit
- `POST /bookings/{id}/approve` - Approve

**Versioned:** `/api/v1/...`

**JSON only** with Pydantic schemas

## Deployment Architecture

```
Browser → Vercel (Next.js) → Fly.io (FastAPI) → Fly.io Postgres
                                   ↓
                            Resend (Email)
```

**Regions:**
- Fly.io: Frankfurt (backend + DB)
- Vercel: Global CDN (frontend)

---

**Next:** See [`/docs/design/`](../design/) for detailed API/DB/component design and [`/docs/implementation/`](../implementation/) to start building.
