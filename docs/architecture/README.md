# Architecture Overview

## Purpose

This directory contains Architecture Decision Records (ADRs) and system architecture documentation for the Betzenstein booking & approval application.

---

## System Overview

The Betzenstein application is a **distributed web application** with:

- **API API** (FastAPI on Fly.io)
- **Web SPA** (Next.js on Vercel)
- **Database** (PostgreSQL on Fly.io, co-located with backend)
- **Email Service** (Resend)

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
│   Next.js 14 Web   │
│   - Calendar UI         │
│   - Forms               │
│   - Approver Views      │
└────────┬────────────────┘
         │ HTTPS/REST
         ↓
┌──────────────────────────────────────┐
│   Fly.io (Frankfurt)                 │
│  ┌────────────────────────────────┐  │
│  │   FastAPI API              │  │
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
                                     │                 │
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
| **Testing** | Pytest + Playwright | - |
| **CI/CD** | GitHub Actions | - |

See [`technology-stack.md`](technology-stack.md) for complete details.

---

## Architecture Decision Records (ADRs)

ADRs document significant architectural decisions with context, rationale, and consequences.

### Core Stack Decisions

- [ADR-001: API Framework](adr-001-backend-framework.md) - Why FastAPI
- [ADR-002: Web Framework](adr-002-frontend-framework.md) - Why Next.js App Router
- [ADR-003: Database & ORM](adr-003-database-orm.md) - **SUPERSEDED** (split into 012-015)
- [ADR-004: Email Service](adr-004-email-service.md) - Why Resend
- [ADR-005: UI Framework](adr-005-ui-framework.md) - Why Shadcn/ui + Tailwind
- [ADR-006: Type Safety Strategy](adr-006-type-safety.md) - Mypy + Pydantic + Zod + TypeScript
- [ADR-007: Deployment Strategy](adr-007-deployment.md) - **SUPERSEDED** (split into 015-018)
- [ADR-008: Testing Strategy](adr-008-testing-strategy.md) - Pytest + Playwright
- [ADR-009: Test Patterns](adr-009-test-patterns.md) - Repository pattern + factories
- [ADR-010: DateTime & Timezone](adr-010-datetime-timezone.md) - Naive storage + Europe/Berlin
- [ADR-011: CORS Security Policy](adr-011-cors-security-policy.md) - Permissive CORS for trusted SPA
- [ADR-012: PostgreSQL Database](adr-012-postgresql-database.md) - Why PostgreSQL
- [ADR-013: SQLAlchemy ORM](adr-013-sqlalchemy-orm.md) - Why SQLAlchemy
- [ADR-014: Alembic Migrations](adr-014-alembic-migrations.md) - Why Alembic
- [ADR-015: Fly.io Postgres Hosting](adr-015-flyio-postgres-hosting.md) - Database hosting
- [ADR-016: Fly.io Backend Hosting](adr-016-flyio-backend-hosting.md) - Backend hosting
- [ADR-017: Vercel Frontend Hosting](adr-017-vercel-frontend-hosting.md) - Frontend hosting
- [ADR-018: GitHub Actions CI/CD](adr-018-github-actions-cicd.md) - CI/CD automation

---

## Key Architectural Principles

### 1. AI-First Architecture

**Context:** All implementation will be done by AI agents (Claude Code).

**Principles:**
- Use **well-documented, popular technologies** (more training data)
- Follow **standard patterns** (reduce AI guessing)
- Enforce **strong type safety** (catch AI errors early)
- Create **clear conventions** (documented in ADRs)
- Enable **incremental testability** (validate each step)

### 2. Type Safety Throughout

**API:**
- Python type hints (PEP 484)
- Mypy strict mode
- Pydantic v2 for runtime validation

**Web:**
- TypeScript strict mode
- Zod for runtime validation
- Type-safe API client

**Benefit:** AI errors caught at compile time, not runtime.

### 3. Separation of Concerns

**Layered Architecture:**
- **API Layer** - FastAPI routes (thin controllers)
- **Service Layer** - Business logic (stateless)
- **Repository Layer** - Data access (SQLAlchemy)
- **Model Layer** - Domain models (ORM models)

**Benefit:** Clear responsibilities, easier for AI to implement incrementally.

### 4. Email-First, Zero-Login

**Architecture Constraint:**
- No user authentication system
- Role determined by signed token in URL
- Stateless (no sessions)

**Implementation:**
- Token signing in backend (HMAC)
- Token validation middleware
- No password storage

### 5. Mobile-First UI

**Constraint:** Must work on iPhone 8 class devices (375×667px).

**Implementation:**
- Responsive Tailwind classes
- Touch-friendly (44×44pt tap targets)
- No hover dependencies
- Single-tap navigation

### 6. Privacy by Design

**Requirements:**
- Emails never displayed in UI
- Denied bookings hidden from public
- Comments visible only to relevant parties

**Implementation:**
- Email fields excluded from API responses
- Separate public/private endpoints
- Role-based filtering in queries

---

## System Components

### API (FastAPI on Fly.io)

**Responsibilities:**
- REST API endpoints
- Business logic enforcement (BR-001 to BR-029)
- Database operations (CRUD)
- Token generation/validation
- Email sending (via Resend)
- State machine enforcement

**Key Features:**
- Auto-generated OpenAPI docs
- Async/await for I/O operations
- Pydantic validation on all inputs
- SQLAlchemy ORM with migrations (Alembic)

### Web (Next.js on Vercel)

**Responsibilities:**
- Calendar UI (Month/Year views)
- Booking forms (Create/Edit)
- Approver interface (Outstanding/History)
- German UI copy rendering
- Client-side validation (Zod)

**Key Features:**
- Server Components (App Router)
- Shadcn/ui components (copy-paste)
- Tailwind CSS (utility-first)
- Type-safe API client (generated from OpenAPI)

### Database (PostgreSQL on Fly.io)

**Responsibilities:**
- Data persistence
- Transactional consistency
- Conflict detection (first-write-wins)

**Key Tables:**
- bookings
- approvals
- timeline_events
- approver_parties (seed data)
- holidays (optional)

**Why Fly.io Postgres:**
- Co-located with backend (ultra-low latency)
- Always on (no shutdown/pause like Supabase)
- Simple connection strings (`.internal` hostname)
- Same platform as backend (simpler management)
- Included in Fly.io free tier

### Email Service (Resend)

**Responsibilities:**
- Transactional email delivery
- Template rendering
- Bounce tracking

**Integration:**
- FastAPI service calls Resend API
- Templates stored in backend
- German copy from specifications

---

## Data Flow

### 1. Create Booking Flow

```
User (Browser)
  → Web: Fill create form
  → Web: Validate with Zod
  → API API: POST /bookings
  → API: Validate with Pydantic
  → API: Check conflicts (BR-002, BR-029)
  → API: Create booking + approvals
  → Database: INSERT transactions
  → API: Send notification emails
  → Resend: Deliver emails
  → API: Return booking data
  → Web: Show success + redirect
```

### 2. Approve Booking Flow

```
Approver (Email)
  → Click action link with token
  → API API: POST /bookings/{id}/approve?token=xxx
  → API: Validate token
  → API: Check current state
  → API: Update approval record
  → API: Check if final approval
  → API: Send notification emails
  → Resend: Deliver emails
  → API: Redirect to result page
  → Web: Show result
```

---

## Security Architecture

### Authentication

**No traditional auth** - Role-by-link with signed tokens.

**Token Structure:**
```python
{
  "email": "user@example.com",
  "role": "requester" | "approver",
  "booking_id": "uuid" (optional),
  "iat": timestamp
}
```

Signed with HMAC-SHA256, no expiry (per BR-010).

### Authorization

**Enforcement:**
- Middleware validates token signature
- Extracts email + role
- Service layer checks permissions
- Per-endpoint authorization rules

**Example:**
```python
# Only requester who created booking can cancel
if booking.requester_email != token.email:
    raise HTTPException(403, "Not authorized")
```

### Rate Limiting

**Implemented in FastAPI middleware:**
- 10 bookings/day/email (BR-012)
- 30 requests/hour/IP
- 5 recovery requests/hour/email
- 60-second soft cooldown on recovery (BR-021)

**Storage:** In-memory or Redis (TBD in implementation).

---

## Deployment Architecture

### Environments

1. **Development** (Local)
   - API: `localhost:8000`
   - Web: `localhost:3000`
   - Database: Local PostgreSQL or Fly.io dev DB

2. **Staging** (Optional, TBD)
   - API: `staging-api.betzenstein.app` (Fly.io)
   - Web: `staging.betzenstein.app` (Vercel)
   - Database: Fly.io Postgres staging DB

3. **Production**
   - API: `api.betzenstein.app` (Fly.io, Frankfurt region)
   - Web: `betzenstein.app` (Vercel, global CDN)
   - Database: Fly.io Postgres (Frankfurt region, co-located)

### CI/CD Pipeline

**GitHub Actions workflows:**
- API: Build → Lint (Ruff) → Type check (mypy) → Test (pytest) → Deploy (Fly.io)
- Web: Build → Lint (ESLint) → Type check (tsc) → Test (Playwright) → Deploy (Vercel)

**Branch Strategy:**
- Feature branches → PR to `main`
- `main` → auto-deploy to production (later: staging first)
- Protected `main` branch (later: require tests to pass)

---

## Non-Functional Architecture

### Performance

**Targets:**
- API response time: < 500ms (p95)
- Calendar load: < 1s
- Email delivery: < 5s

**Optimizations:**
- Database indexes on common queries
- Async I/O (FastAPI + httpx)
- Fly.io edge (low latency)
- Vercel CDN (global)

### Scalability

**Current Scale:**
- Small trusted group (~10-20 users)
- Low traffic (< 100 requests/day)
- Single Fly.io machine sufficient

**Future Scaling:**
- Horizontal: Add Fly.io machines
- Database: Read replicas if needed
- Email: Resend handles scaling

### Reliability

**Strategies:**
- Email retries (3 attempts, exponential backoff, BR-022)
- Idempotent actions (BR-010)
- Database transactions (ACID guarantees)
- Graceful error handling

**No formal SLA** (per constraints) - best effort for small group.

### Observability

**Logging:**
- Structured JSON logs (Python logging)
- Correlation IDs on all requests
- Fly.io log aggregation

**Monitoring:**
- Fly.io metrics (CPU, memory, requests)
- Vercel analytics (page views, performance)
- Resend delivery tracking

**Alerting (Future):**
- Error rate > 1%
- Email delivery failure > 5%
- API response time > 2s

---

## API Design Principles

### RESTful

**Resource-based URLs:**
- `GET /bookings` - List bookings
- `GET /bookings/{id}` - Get booking details
- `POST /bookings` - Create booking
- `PATCH /bookings/{id}` - Edit booking
- `DELETE /bookings/{id}` - Cancel booking
- `POST /bookings/{id}/approve` - Approve
- `POST /bookings/{id}/deny` - Deny

### Versioning

**Strategy:** URL versioning (`/api/v1/...`)

**Rationale:** Clear, explicit, easy for AI to implement.

### Request/Response Format

**JSON only:**
- `Content-Type: application/json`
- Pydantic schemas define contracts
- OpenAPI spec auto-generated

**Error Format:**
```json
{
  "detail": "Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung (Anna – Ausstehend).",
  "error_code": "BOOKING_CONFLICT",
  "correlation_id": "uuid"
}
```

---

## Database Design Principles

### Normalization

**3NF (Third Normal Form):**
- No redundant data
- Foreign keys enforce relationships
- Migrations track schema changes

### Indexing Strategy

**Indexes for:**
- Primary keys (automatic)
- Foreign keys (explicit)
- Query filters (status, date ranges)
- Sorts (LastActivityAt, CreatedAt)

### Migrations

**Alembic:**
- Version-controlled schema changes
- Reversible migrations
- Seeded data (approver_parties, holidays)

---

## Web Architecture Principles

### Component Structure

**Atomic Design (loosely):**
- `/components/ui/` - Shadcn base components
- `/components/calendar/` - Calendar-specific
- `/components/booking/` - Booking forms/details
- `/components/approver/` - Approver views

### State Management

**Server State:** React Query (TanStack Query)
- API data fetching
- Caching
- Optimistic updates

**Client State:** React hooks (useState, useReducer)
- Form state
- UI state (modals, etc.)

**No global state** (Redux, Zustand) - not needed for this app.

### Routing

**Next.js App Router:**
- `/app/calendar/page.tsx` - Public calendar
- `/app/bookings/[id]/page.tsx` - Booking details
- `/app/approver/page.tsx` - Approver overview

---

## Future Architecture Considerations

### Not Implemented Initially (But Architected For)

**Week View:**
- Calendar component supports it
- Add toggle in UI

**Advanced Filtering:**
- API supports query params
- Add UI filters

**Push Notifications:**
- Email-only initially
- Could add web push later

**Mobile Apps:**
- PWA-ready (Next.js)
- Native apps not planned

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
- [Development Workflow](../implementation/development-workflow.md) - Git flow

---

## Questions & Decisions

All architectural decisions are documented in ADRs. If you need to understand why a choice was made, read the relevant ADR.

**For new decisions:**
1. Create new ADR (next number)
2. Use ADR template (Context, Decision, Consequences)
3. Reference in this README

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
