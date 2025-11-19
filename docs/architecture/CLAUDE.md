# Architecture - CLAUDE Guide

## What's in This Section

Architecture decisions and system design:
- **README.md** - System overview, architecture diagram, principles
- **technology-stack.md** - Complete tech stack with rationale
- **adr-001 to adr-009** - Architecture Decision Records (why we chose each technology)

---

## ⚠️ CRITICAL: Architecture Decision Records (ADRs) are Immutable Constraints

### ADR Lifecycle and Immutability

**ADRs are the law of this codebase. You MUST follow them.**

#### ADR Status States
- **Proposed** - Under review, not yet binding
- **Accepted** - Active constraint, MUST be followed
- **Superseded** - Replaced by newer ADR, historical record
- **Deprecated** - No longer applies, historical record

#### Immutability Rule

**Once an ADR status is "Accepted", it CANNOT be altered. It can ONLY be superseded.**

**Why this matters:**
- ADRs create a historical record of decisions
- Changing an ADR destroys the decision history
- Superseding creates a clear evolution trail

**Wrong approach:**
```markdown
❌ Edit ADR-003 to change from PostgreSQL to MySQL
```

**Correct approach:**
```markdown
✅ Create ADR-010: Supersede ADR-003, migrate to MySQL
   Status: Proposed
   Supersedes: ADR-003

✅ Update ADR-003:
   Status: Superseded by ADR-010
   (Keep original decision text unchanged)
```

### ⚠️ ONE Decision Per ADR (Fundamental Principle)

**An ADR captures exactly ONE architectural decision, not several.**

**Why this matters:**
- Allows superseding individual decisions without affecting others
- Creates granular evolution trail
- Prevents bundling unrelated choices
- Makes decision boundaries explicit

**How to identify "one decision":**
- Ask: "Can these choices be changed independently?"
- If YES → Separate ADRs
- If NO (choices are inseparable) → One ADR

**Examples:**

**❌ Wrong - Multiple Independent Decisions:**
```markdown
ADR-010: CORS Configuration
- allow_origins = frontend domain
- allow_credentials = true
- allow_methods = ["GET", "POST"]
- allow_headers = ["*"]
```
*Problem: These can be changed independently. allow_credentials is a security policy, allow_methods is an API surface decision, allow_origins is an access control decision.*

**✅ Correct - Separate ADRs:**
```markdown
ADR-010: CORS Allow Credentials (security policy)
ADR-011: CORS Allowed Methods (API surface)
ADR-012: CORS Allowed Origins (access control)
```

**✅ Correct - One Cohesive Decision:**
```markdown
ADR-010: Naive DateTime Storage with Europe/Berlin Assumption
- Store TIMESTAMP WITHOUT TIME ZONE
- All datetimes represent Europe/Berlin local time
```
*Valid: Naive storage REQUIRES a timezone assumption. These are inseparable parts of one strategy.*

**When bundling is acceptable:**
- Multiple tools that form ONE strategy (e.g., "Type Safety Strategy" = mypy + Pydantic + TypeScript + Zod work together)
- Choices that are architecturally inseparable (e.g., naive storage + timezone assumption)
- Trade-off: If one part of the bundle needs changing, the entire ADR must be superseded

**When to split:**
- Choices that could change independently
- Unrelated concerns bundled together
- Different teams/roles would make different parts of the decision

**Before creating an ADR, ask:**
1. What is the ONE architectural decision being made?
2. Could any part of this decision change without affecting the others?
3. If I need to supersede part of this decision later, would I need to supersede all of it?

If answers suggest multiple decisions, create multiple ADRs.

---

## How to Work with ADRs as an AI Agent

### Before Implementing

**ALWAYS check ADRs first:**
1. Read relevant ADRs for the feature you're implementing
2. Treat ADRs as **constraints**, not suggestions
3. Never violate an ADR without proposing a superseding ADR

**Example: Implementing email service**
```
Step 1: Read ADR-004 (Email Service)
Step 2: See decision = Resend
Step 3: Use Resend (not SendGrid, not AWS SES)
Step 4: If Resend doesn't work, propose ADR-011 to supersede ADR-004
```

### ADRs as Constraints

**These are NOT optional:**
- ADR-001: Use FastAPI (not Flask, not Django)
- ADR-002: Use Next.js App Router (not Pages Router, not Remix)
- ADR-004: Use Resend for email (not SendGrid, not AWS SES)
- ADR-005: Use Shadcn/ui + Tailwind (not Material UI, not Bootstrap)
- ADR-006: Type safety with mypy + Pydantic + TypeScript + Zod
- ADR-008: Test with Pytest + Playwright (not Jest, not Vitest)
- ADR-009: Test patterns (repository pattern, factories, fixtures)
- ADR-010: Naive datetime storage with Europe/Berlin timezone (not UTC, not timezone-aware)
- ADR-011: Permissive CORS policy (allow_credentials, all methods/headers for trusted SPA)
- ADR-012: Use PostgreSQL (not MySQL, not MongoDB)
- ADR-013: Use SQLAlchemy (not Django ORM, not Tortoise ORM)
- ADR-014: Use Alembic for migrations (not raw SQL, not other tools)
- ADR-015: Database hosted on Fly.io Postgres (not Supabase, not RDS)
- ADR-016: Backend hosted on Fly.io (not Heroku, not Railway)
- ADR-017: Frontend hosted on Vercel (not Netlify, not Cloudflare Pages)
- ADR-018: CI/CD via GitHub Actions (not GitLab CI, not CircleCI)

**If you need to deviate:**
1. STOP implementation
2. Document WHY current ADR doesn't work
3. Propose new ADR with clear rationale
4. Get user approval BEFORE proceeding
5. Create new ADR that supersedes old one

---

## When to Propose a New ADR

### Situations Requiring New ADR

**1. Technology Choice Not Covered**
- Example: Need a background job scheduler (no existing ADR)
- Action: Create ADR-011: Background Job Scheduler (Celery vs APScheduler)

**2. Current ADR Doesn't Work**
- Example: Resend API limits hit, need different provider
- Action: Create ADR-012: Supersede ADR-004, migrate to SendGrid

**3. New Architectural Pattern Needed**
- Example: Need caching strategy (Redis, in-memory, etc.)
- Action: Create ADR-013: Caching Strategy

**4. Significant Change to Existing Decision**
- Example: Move from SQLAlchemy to Prisma
- Action: Create ADR-014: Supersede ADR-003, switch ORM

### Situations NOT Requiring ADR

**Implementation details covered by existing ADRs:**
- Using a specific Pydantic field type (covered by ADR-006)
- Choosing a Shadcn component (covered by ADR-005)
- Writing a specific SQL query (covered by ADR-003)
- Structuring a test file (covered by ADR-009)

**Business logic:**
- How to calculate TotalDays (covered by business rules, not architecture)
- When to reset approvals (BR-005, not architecture)

---

## How to Create a New ADR

### Step 1: Check If ADR Needed

Ask yourself:
- Is this a **technology choice**? (Yes → ADR)
- Is this a **structural pattern**? (Yes → ADR)
- Is this an **implementation detail** within existing ADRs? (No → No ADR)
- Is this **business logic**? (No → Business Rule, not ADR)

### Step 2: Use ADR Template

**File naming:** `adr-{number}-{title}.md`
- Number: Next available (currently ADR-012)
- Title: Kebab-case, descriptive

**Template:**
```markdown
# ADR-{number}: {Title}

**Status:** Proposed | Accepted | Superseded | Deprecated
**Date:** YYYY-MM-DD
**Deciders:** {Who made this decision}
**Context:** {What triggered this decision}
**Supersedes:** ADR-XXX (if applicable)

---

## Context

{Describe the situation requiring a decision. Include:}
- What problem are we solving?
- What requirements drive this?
- What constraints exist?

### Requirements from Specifications

{Reference relevant BRs, user stories, constraints}

---

## Decision

{State the decision clearly and concisely}

---

## Rationale

{Explain WHY this decision makes sense. Include:}
1. How it solves the problem
2. Why it's better than alternatives
3. How it aligns with project goals (AI-first, type safety, etc.)

### Alternatives Considered

{List alternatives and why they were rejected}

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| Option A    | ... | ... | ... |
| Option B    | ... | ... | ... |

---

## Consequences

**Positive:**
- {List benefits}

**Negative:**
- {List drawbacks}

**Neutral:**
- {List trade-offs}

---

## Implementation Notes

{How to implement this decision:}
- Key patterns to follow
- Files/folders affected
- Migration steps (if superseding)

---

## References

{Links to:}
- Related ADRs
- External documentation
- Business rules
- Specifications
```

### Step 3: Propose to User

**Don't create ADR file yet. Propose first:**
```
I need to make an architectural decision that isn't covered by existing ADRs:

Decision needed: {Topic}
Current situation: {Context}
Proposed solution: {Your recommendation}
Rationale: {Why}

Should I create ADR-012: {Title}?
```

### Step 4: Create ADR After Approval

Only after user approves, create the ADR file.

---

## Current ADRs (Active Constraints)

### Core Stack Decisions

| ADR | Decision | Status | Summary |
|-----|----------|--------|---------|
| **ADR-001** | FastAPI + Python 3.11+ | Accepted | Backend framework |
| **ADR-002** | Next.js 14 App Router | Accepted | Frontend framework |
| **ADR-003** | PostgreSQL + SQLAlchemy on Fly.io | Superseded | Database & ORM (split into 012-015) |
| **ADR-004** | Resend | Accepted | Email service |
| **ADR-005** | Shadcn/ui + Tailwind CSS | Accepted | UI framework |
| **ADR-006** | Mypy + Pydantic + TypeScript + Zod | Accepted | Type safety strategy |
| **ADR-007** | Fly.io + Vercel + GitHub Actions | Superseded | Deployment (split into 015-018) |
| **ADR-008** | Pytest + Playwright | Accepted | Testing frameworks |
| **ADR-009** | Repository pattern + factories | Accepted | Test patterns |
| **ADR-010** | Naive DateTime Storage (Europe/Berlin) | Accepted | DateTime/timezone strategy |
| **ADR-011** | CORS Security Policy | Accepted | Permissive CORS for trusted SPA |
| **ADR-012** | PostgreSQL Database | Accepted | Database choice |
| **ADR-013** | SQLAlchemy ORM | Accepted | Python ORM |
| **ADR-014** | Alembic Migrations | Accepted | Database migrations |
| **ADR-015** | Fly.io Postgres Hosting | Accepted | Database hosting |
| **ADR-016** | Fly.io Backend Hosting | Accepted | Backend hosting |
| **ADR-017** | Vercel Frontend Hosting | Accepted | Frontend hosting |
| **ADR-018** | GitHub Actions CI/CD | Accepted | CI/CD automation |

**All accepted ADRs are constraints. Follow them. Superseded ADRs are historical only.**

---

## When to Read This

Read before implementation:
- **README.md** - Understand system architecture
- **technology-stack.md** - See all technologies and versions
- **Specific ADRs** - Understand why decisions were made and what constraints apply

**Critical workflow:**
```
1. Read user story (WHAT to build)
2. Read relevant ADRs (HOW to build - constraints)
3. Read specifications (WHAT exactly - requirements)
4. Implement following ADR constraints
5. If ADR doesn't work → propose new ADR (don't violate)
```

---

## Tech Stack Quick Reference

| Component | Technology | ADR | Constraint |
|-----------|-----------|-----|------------|
| API | FastAPI + Python 3.11+ | ADR-001 | MUST use FastAPI |
| Web | Next.js 14 (App Router) | ADR-002 | MUST use App Router (not Pages) |
| Database | PostgreSQL 15+ | ADR-012 | MUST use PostgreSQL |
| DB Hosting | Fly.io Postgres | ADR-015 | MUST use Fly.io Postgres |
| ORM | SQLAlchemy 2.0 | ADR-013 | MUST use SQLAlchemy |
| Migrations | Alembic | ADR-014 | MUST use Alembic |
| Email | Resend | ADR-004 | MUST use Resend |
| UI | Shadcn/ui + Tailwind | ADR-005 | MUST use Shadcn/ui |
| Type Safety | Mypy + Pydantic + TypeScript + Zod | ADR-006 | MUST enforce types |
| Backend Hosting | Fly.io | ADR-016 | MUST deploy backend to Fly.io |
| Frontend Hosting | Vercel | ADR-017 | MUST deploy frontend to Vercel |
| CI/CD | GitHub Actions | ADR-018 | MUST use GitHub Actions |
| Testing | Pytest + Playwright | ADR-008 | MUST use these frameworks |

---

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
- Repository pattern for data access (ADR-009)
- Service layer for business logic
- Pydantic models for validation (ADR-006)
- Async/await for I/O

**Web:**
- Server Components (Next.js App Router - ADR-002)
- Shadcn/ui components copy-paste (ADR-005)
- React Query for server state
- Zod for form validation (ADR-006)

**Testing:**
- Test-first (BDD - ADR-008)
- API: Pytest (unit + integration - ADR-008)
- Web: Playwright (E2E - ADR-008)
- Repository pattern + factories (ADR-009)

## Database Architecture

**Fly.io Postgres co-located with backend (ADR-015, ADR-016):**
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

**JSON only** with Pydantic schemas (ADR-006)

## Deployment Architecture

```
Browser → Vercel (Next.js) → Fly.io (FastAPI) → Fly.io Postgres
                                   ↓
                            Resend (Email)
```

**Regions (ADR-015, ADR-016, ADR-017):**
- Fly.io: Frankfurt (backend + DB)
- Vercel: Global CDN (frontend)

---

## Summary: ADRs are Law

**Critical reminders:**
1. ⚠️ **ADRs are constraints, not suggestions**
2. ⚠️ **Never violate an accepted ADR**
3. ⚠️ **Never alter an accepted ADR**
4. ⚠️ **Supersede with new ADR if needed**
5. ⚠️ **Propose before creating new ADR**

**If you violate an ADR, the implementation is wrong. Full stop.**

---

**Next:** See [`/docs/design/`](../design/) for detailed API/DB/component design and [`/docs/implementation/`](../implementation/) to start building.
