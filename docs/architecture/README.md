# Architecture Overview

## Purpose

This directory contains Architecture Decision Records (ADRs) and system architecture documentation for the Betzenstein booking & approval application.

---

## System Overview

**Distributed web application:**
- **API** - FastAPI on Fly.io (Frankfurt)
- **Web** - Next.js 14 App Router on Vercel (Global CDN)
- **Database** - PostgreSQL 15+ on Fly.io Postgres (Frankfurt, co-located)
- **Email** - Resend (SaaS)

### Architecture Diagram

```
┌─────────────────┐
│   User Browser  │
│   (Mobile/Web)  │
└────────┬────────┘
         │ HTTPS
         ↓
┌─────────────────────────┐
│   Vercel (CDN/Edge)     │
│   Next.js 14 Web        │
│   - Calendar UI         │
│   - Forms               │
│   - Approver Views      │
└────────┬────────────────┘
         │ HTTPS/REST
         ↓
┌──────────────────────────────────────┐
│   Fly.io (Frankfurt)                 │
│  ┌────────────────────────────────┐  │
│  │   FastAPI API                 │  │
│  │   - REST API                   │  │
│  │   - Business Logic             │  │
│  │   - Token Auth                 │  │
│  └────┬───────────────────────┬───┘  │
│       │                       │      │
│       │ .internal             │      │
│       ↓                       │      │
│  ┌────────────────────────┐   │      │
│  │   Fly.io Postgres      │   │      │
│  │   - Bookings           │   │      │
│  │   - Approvals          │   │      │
│  │   - Timeline           │   │      │
│  └────────────────────────┘   │      │
│                               │      │
└───────────────────────────────┼──────┘
                                │
                                └──────────────┐
                                               ↓
                                     ┌─────────────────┐
                                     │  Resend API     │
                                     │  - Email Send   │
                                     │  - Templates    │
                                     └─────────────────┘
```

---

## Technology Stack

| Component | Technology | Hosting |
|-----------|-----------|---------|
| **API** | FastAPI + Python 3.11+ | Fly.io (Frankfurt) |
| **Web** | Next.js 14 (App Router) | Vercel (Global CDN) |
| **Database** | PostgreSQL 15+ | Fly.io Postgres (Frankfurt, co-located) |
| **ORM** | SQLAlchemy 2.0 | - |
| **UI** | Shadcn/ui + Tailwind CSS | - |
| **Email** | Resend | SaaS |
| **Type Safety** | mypy + Pydantic + TypeScript + Zod | - |
| **Testing** | Pytest (backend) + Vitest + React Testing Library (frontend unit) + Playwright (frontend E2E) | - |
| **CI/CD** | GitHub Actions | - |

See [`technology-stack.md`](technology-stack.md) for complete details.

---

## Architecture Decision Records (ADRs)

ADRs document significant architectural decisions with context, rationale, and consequences. All ADRs are located in this directory.

**Key principles:**
- ADRs are immutable constraints - once Accepted, they cannot be altered, only superseded
- One decision per ADR - allows granular evolution
- Check filename pattern first - files ending in `-SUPERSEDED.md` or `-DEPRECATED.md` are superseded/deprecated
- Check status field - only "Accepted" ADRs are binding constraints

See [`CLAUDE.md`](CLAUDE.md) for complete ADR workflow and guidelines.

---

## Key Architectural Principles

### 1. AI-First Architecture
- Well-documented, popular technologies (more training data)
- Standard patterns (reduce AI guessing)
- Strong type safety (catch AI errors early)
- Clear conventions (documented in ADRs)
- Incremental testability (validate each step)

### 2. Type Safety Throughout
- **API:** Python type hints (PEP 484), Mypy strict mode, Pydantic v2
- **Web:** TypeScript strict mode, Zod runtime validation
- **Benefit:** AI errors caught at compile time, not runtime

### 3. Separation of Concerns
**Layered Architecture:**
- **API Layer** - FastAPI routes (thin controllers)
- **Service Layer** - Business logic (stateless)
- **Repository Layer** - Data access (SQLAlchemy)
- **Model Layer** - Domain models (ORM models)

### 4. Email-First, Zero-Login
- No user authentication system
- Role determined by signed token in URL
- Stateless (no sessions)
- Token signing in backend (HMAC)

### 5. Mobile-First UI
- Must work on iPhone 8 class devices (375×667px)
- Responsive Tailwind classes
- Touch-friendly (44×44pt tap targets)
- No hover dependencies

### 6. Privacy by Design
- Emails never displayed in UI
- Denied bookings hidden from public
- Comments visible only to relevant parties
- Email fields excluded from API responses

---

## System Components

### API (FastAPI on Fly.io)
**Responsibilities:** REST API endpoints, business logic enforcement, database operations, token generation/validation, email sending (via Resend), state machine enforcement.

**Key Features:** Auto-generated OpenAPI docs, async/await for I/O, Pydantic validation, SQLAlchemy ORM with Alembic migrations.

### Web (Next.js on Vercel)
**Responsibilities:** Calendar UI (Month/Year views), booking forms (Create/Edit), approver interface (Outstanding/History), German UI copy rendering, client-side validation (Zod).

**Key Features:** Server Components (App Router), Shadcn/ui components, Tailwind CSS, type-safe API client.

### Database (PostgreSQL on Fly.io)
**Responsibilities:** Data persistence, transactional consistency, conflict detection (first-write-wins).

**Key Tables:** bookings, approvals, timeline_events, approver_parties (seed data), holidays (optional).

**Why Fly.io Postgres:** Co-located with backend (ultra-low latency), always on (no shutdown/pause), simple connection strings (`.internal` hostname), same platform as backend.

### Email Service (Resend)
**Responsibilities:** Transactional email delivery, template rendering, bounce tracking.

**Integration:** FastAPI service calls Resend API, templates stored in backend, German copy from specifications.

---

## Security Architecture

### Authentication
**No traditional auth** - Role-by-link with signed tokens (HMAC-SHA256, no expiry per BR-010).

### Authorization
**Enforcement:** Middleware validates token signature, extracts email + role, service layer checks permissions, per-endpoint authorization rules.

### Rate Limiting
**FastAPI middleware:** 10 bookings/day/email (BR-012), 30 requests/hour/IP, 5 recovery requests/hour/email, 60-second soft cooldown on recovery (BR-021).

---

## Deployment Architecture

### Environments
1. **Development** (Local) - API: `localhost:8000`, Web: `localhost:3000`
2. **Production** - API: `api.betzenstein.app` (Fly.io, Frankfurt), Web: `betzenstein.app` (Vercel, global CDN)

### CI/CD Pipeline
**GitHub Actions workflows:** Build → Lint → Type check → Test → Deploy (Fly.io + Vercel).

**Branch Strategy:** Feature branches → PR to `main` → auto-deploy to production.

---

## Related Documentation

**Requirements:**
- [Business Rules](../foundation/business-rules.md) - BR-001 to BR-029
- [User Journeys](../requirements/user-journeys.md) - Flows
- [State Machine](../requirements/states-and-transitions.md) - States

**Specifications:**
- [API Specification](../design/api-specification.md) - Endpoints
- [Database Schema](../design/database-schema.md) - DDL
- [Design Tokens](../design/design-tokens.md) - UI tokens

**Implementation:**
- [Phase 0](../implementation/phase-0-foundation.md) - Setup
- [Development Workflow](../implementation/test-first-workflow.md) - Test-first workflow

---

## Summary

This architecture is optimized for:
- ✅ **AI implementation** (Claude Code)
- ✅ **Type safety** (catch errors early)
- ✅ **Incremental development** (testable phases)
- ✅ **Mobile-first** (responsive, touch-friendly)
- ✅ **Privacy** (email-first, no login)
- ✅ **Simplicity** (monolithic, standard stack)

**Next Steps:** Read the ADRs for detailed rationale, then proceed to Design and Implementation docs.
