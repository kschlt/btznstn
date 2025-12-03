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

**⚠️ CRITICAL: Always check status FIRST before reading constraints**

- **Proposed** - Under review, NOT binding (do not use as constraint)
- **Accepted** - Active constraint, MUST be followed (use these constraints)
- **Superseded** - Replaced by newer ADR, follow "Superseded by" link to find current decision
- **Deprecated** - No longer applies, follow "Replaced by" link to find current decision

**Status location:** Always at the top of ADR file, right after title

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

### ADR Format: LLM-Actionable but Human-Reviewable

**ADRs serve dual purpose: LLM-actionable constraints AND human-reviewable reasoning.**

**Format optimized for both audiences:**

1. **Quick Reference** table at top (LLMs scan quickly, humans see overview)
2. **Rationale** - Reasoning chain (decision → constraint → violation) for LLM understanding AND human review
3. **Consequences** written as Implementation Constraints/Complexity Trade-offs (LLM-actionable constraints, human-reviewable trade-offs)
4. **MUST/MUST NOT patterns** - Explicit constraints with code examples only when showing specific pitfalls
5. **Concrete language** - "MUST" not "should" (LLMs parse better, humans understand clearly)
6. **No redundancy** - Each section provides unique value, no duplicate code examples
7. **Human-reviewable** - Context and reasoning preserved for human architects to review decisions

**Key principle:** Constraints must be LLM-actionable, but reasoning must be human-reviewable. Both audiences matter.

**Status:** 5/17 ADRs updated (ADR-001, ADR-006, ADR-010, ADR-013, ADR-019). Remaining ADRs are being systematically updated to this format.

### Before Implementing

**ALWAYS check ADRs first - follow this workflow:**

1. **Find relevant ADRs** - Search for ADRs related to your feature
2. **Check status FIRST** - Read status field at top of each ADR
   - ✅ **"Accepted"** → Use constraints (proceed to step 3)
   - ⚠️ **"Superseded"** → Follow "Superseded by" link, check that ADR's status
   - ⚠️ **"Deprecated"** → Follow "Replaced by" link, check that ADR's status
   - ⏸️ **"Proposed"** → Skip (not yet binding)
3. **Read Quick Reference** - Determine if ADR is relevant to your work
4. **If relevant, read Constraints** - Consequences section contains MUST/MUST NOT patterns
5. **Review Rationale** - Understand decision → constraint → violation chain
6. **Follow constraints** - Treat Accepted ADRs as binding requirements
7. **Never violate** - If ADR doesn't work, propose superseding ADR first

**Code Examples in ADRs:**
- Only included when showing **specific pitfalls** LLMs might take
- Generic patterns (that LLMs already know) are omitted
- Examples use consistent naming with codebase (no made-up variables)

**Example: Implementing email service**
```
Step 1: Read Quick Reference table in ADR-004 (Email Service)
Step 2: If relevant, read Consequences section (these ARE the constraints)
Step 3: Follow MUST/MUST NOT patterns
Step 4: See decision = Resend (MUST use Resend)
Step 5: Use Resend (not SendGrid, not AWS SES)
Step 6: If Resend doesn't work, propose ADR-011 to supersede ADR-004
```

### ADRs as Constraints

**All ADRs define MUST/MUST NOT patterns - but ONLY if status is "Accepted".**

**Status Checking Workflow:**
1. **Check status FIRST** - Read status field at top of ADR
2. **If status = "Accepted"** → Use constraints as binding requirements
3. **If status = "Superseded"** → Follow "Superseded by" link to find current decision
4. **If status = "Deprecated"** → Follow "Replaced by" link to find current decision
5. **If status = "Proposed"** → Do NOT use as constraint (awaiting approval)

**Example:**
```
Step 1: Read ADR-003 (Database & ORM)
Step 2: See status = "Superseded by ADR-012, ADR-013, ADR-014, ADR-015"
Step 3: Follow links to ADR-012, ADR-013, ADR-014, ADR-015 (all Accepted)
Step 4: Use constraints from those ADRs, not ADR-003
```

**If you need to deviate from an Accepted ADR:**
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

**⚠️ CRITICAL: ADRs contain LLM-actionable constraints AND human-reviewable reasoning.**

**Dual purpose:**
- **LLM-actionable:** Constraints written so LLMs can parse and apply them
- **Human-reviewable:** Reasoning and context preserved for human architects to review decisions

**Both audiences matter:** Constraints must be actionable for LLMs, but reasoning must be reviewable by humans.

**File naming:** `adr-{number}-{title}.md`
- Number: Next available
- Title: Kebab-case, descriptive

**Format Requirements (Dual Purpose):**
- **LLM-actionable constraints:** MUST/MUST NOT patterns written so LLMs can parse and apply them
- **Human-reviewable reasoning:** Rationale and context preserved for human architects to review decisions
- **Concrete language:** Use "MUST" not "should" (LLMs parse better, humans understand clearly)
- **No verbosity:** Direct, to-the-point constraints (but preserve reasoning chain)
- **No human-team language:** Remove "learning curve", "team needs to understand" (use constraint language instead)

**What to include:**
- ✅ Context (brief - why we need this decision)
- ✅ Decision (clear statement of choice)
- ✅ Rationale (why this vs alternatives)
- ✅ Consequences (reframed as Implementation Constraints/Complexity Trade-offs)
- ✅ **LLM Implementation Constraints** (MUST/MUST NOT with code examples)
- ✅ Applies To (which phases/specs this affects)
- ✅ When Writing User Stories (guidance for spec generation)
- ✅ Minimal implementation pattern (correct vs wrong examples)

**What to exclude:**
- ❌ Human-team language ("team needs to learn", "developers should understand")
- ❌ Implementation checklists (belong in user stories, not ADRs)
- ❌ Vague language ("should", "consider", "might want to")
- ❌ Detailed tutorials (minimal reference examples only)

**Template:**
```markdown
# ADR-{number}: {Title}

**Status:** Accepted
**Date:** YYYY-MM-DD
**Deciders:** Solution Architect
**Context:** {Brief trigger}

---

## Context

{2-4 paragraphs: problem, requirements, constraints}

---

## Decision

{1-2 paragraphs: clear statement of choice}

---

## Rationale

### Why {Chosen Option} vs {Alternative}?

**{Chosen Option}:**
- ✅ Pro 1
- ✅ Pro 2

**{Alternative} (Rejected):**
- ❌ Con 1
- ❌ Con 2

{Repeat for 2-3 key alternatives}

---

## Consequences

### Implementation Constraints

✅ {What this decision ENFORCES across all implementations}
✅ {Pattern that MUST always be followed}
✅ {Library/approach that is REQUIRED}

### Complexity Trade-offs

⚠️ {Added complexity from this decision with specific constraint}
⚠️ {Discipline required with exact pattern to follow}

### Neutral

➡️ {Trade-offs that aren't strictly positive or negative}

---

## LLM Implementation Constraints

**Purpose:** Absolute constraints from this architectural decision that MUST be enforced in all user stories and implementations.

### Required Patterns

**MUST:**
- {Absolute requirement - framework/library to use}
- {Pattern that MUST always be used}
- {Import/module that is REQUIRED}

**MUST NOT:**
- {Anti-pattern that violates this ADR}
- {Framework/library that conflicts with this decision}
- {Common mistake from other approaches}

**Example - Correct Pattern:**
```{language}
# Minimal example (2-5 lines) showing the constraint
{Code showing required pattern}
```

**Example - WRONG (Anti-patterns):**
```{language}
# Example of what violates this ADR (2-5 lines)
# ❌ WRONG: {Why this violates the constraint}
{Code showing forbidden pattern}
```

### Applies To

**This constraint affects:**
- {Which phases this applies to}
- {Which types of user stories need this constraint}
- {Which specification files must reflect this}

### When Writing User Stories

**Ensure specifications include:**
- {Constraint that must appear in acceptance criteria}
- {Pattern that must be referenced in implementation notes}
- {Validation command that belongs in user story checklist}

**Related ADRs:**
- [ADR-XXX](adr-xxx.md) - {How it relates}

**Related Specifications:**
- {Which spec files this decision affects}
- {Which business rules this enables/constrains}

---

## References

**Related ADRs:** ADR-XXX
**Business Rules:** BR-XXX
**Implementation:** {file paths}
```

**Example of good ADR:** ADR-001 (Backend Framework) and ADR-010 (DateTime/Timezone) - both have LLM Implementation Constraints sections

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

## Finding Relevant ADRs

**To find which ADRs apply to your work:**

1. **Check README.md** - Lists all ADRs with status
2. **Search by topic** - Look for ADRs matching your feature (e.g., "auth" → ADR-019)
3. **Check status FIRST** - Only use "Accepted" ADRs as constraints
4. **Follow superseded links** - If ADR is superseded, follow link to current decision

**Remember:** Status is at the top of each ADR file. Always check it first before reading constraints.

---

## When to Read This

Read before implementation:
- **README.md** - Understand system architecture
- **technology-stack.md** - See all technologies and versions
- **Specific ADRs** - Understand why decisions were made and what constraints apply

**Critical workflow:**
```
1. Read user story (WHAT to build)
2. Find relevant ADRs (search by topic)
3. Check ADR status FIRST (only use "Accepted" ADRs)
4. If superseded → follow link to current ADR
5. Read ADR constraints (Consequences section)
6. Read specifications (WHAT exactly - requirements)
7. Implement following ADR constraints
8. If ADR doesn't work → propose new ADR (don't violate)
```

---

## Tech Stack Overview

**For complete tech stack details, see:** [`technology-stack.md`](technology-stack.md)

**For specific constraints, read the relevant ADR:**
- Backend: ADR-001 (FastAPI)
- Frontend: ADR-002 (Next.js)
- Database: ADR-012 (PostgreSQL), ADR-013 (SQLAlchemy)
- Testing: ADR-008 (Pytest/Playwright), ADR-009 (Test patterns)
- Type Safety: ADR-006 (Mypy/Pydantic/TypeScript/Zod)
- Auth: ADR-019 (FastAPI dependencies)

**Always check ADR status before using constraints.**

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

## 🔐 Authentication & Authorization Pattern (ADR-019)

**⚠️ CRITICAL: Always use the established auth pattern. Never implement custom token validation or authorization logic.**

### Where to Find Auth Components

**Token utilities** (already implemented):
- **Location:** [`api/app/core/tokens.py`](../../api/app/core/tokens.py:1)
- **Functions:**
  - `generate_token(payload)` - Create HMAC-SHA256 signed token
  - `verify_token(token)` - Validate signature, extract payload
- **Use when:** Generating tokens for emails, validating tokens manually

**Auth dependencies** (Phase 3+):
- **Location:** [`api/app/core/auth.py`](../../api/app/core/auth.py:1)
- **Dependencies:**
  - `get_current_token` - Validates token, extracts payload
  - `require_approver` - Ensures approver role
  - `require_requester` - Ensures requester role
- **Use when:** Implementing authenticated endpoints

### How to Use Auth in Endpoints

**Pattern (from ADR-019):**

```python
from typing import Annotated
from fastapi import APIRouter, Depends
from app.core.auth import require_approver, TokenPayload

@router.post("/api/v1/bookings/{id}/approve")
async def approve_booking(
    id: UUID,
    token_data: Annotated[TokenPayload, Depends(require_approver)],
    db: AsyncSession = Depends(get_db),
) -> ApprovalResponse:
    """Approve a booking (Approver only)."""
    service = BookingService(db)
    return await service.approve_booking(
        booking_id=id,
        approver_party=token_data.party,  # Already validated
    )
```

**Key points:**
- ✅ Token validation automatic (handled by dependency)
- ✅ Role check automatic (handled by dependency)
- ✅ Type-safe (`token_data.party` is `AffiliationEnum`)
- ✅ German error messages (401/403) from specification

### Common Mistakes to Avoid

❌ **Don't:** Manually validate tokens in endpoints
```python
# WRONG
token = request.query_params.get("token")
payload = verify_token(token)
if not payload:
    raise HTTPException(401, "Invalid token")
```

✅ **Do:** Use auth dependencies
```python
# CORRECT
token_data: Annotated[TokenPayload, Depends(require_approver)]
```

---

❌ **Don't:** Implement custom role checks
```python
# WRONG
if token_data.role != "approver":
    raise HTTPException(403, "Not allowed")
```

✅ **Do:** Use role-specific dependencies
```python
# CORRECT
token_data: Annotated[TokenPayload, Depends(require_approver)]
```

---

❌ **Don't:** Put tokens in headers
```python
# WRONG - Not email-friendly
Authorization: Bearer xxx
```

✅ **Do:** Use query parameter
```python
# CORRECT - Works in email links
GET /api/v1/bookings/{id}/approve?token=xxx
```

### Quick Reference

**Read this ADR for full details:** [ADR-019: Authentication & Authorization](adr-019-authentication-authorization.md)

**Token structure:**
```python
{
  "email": "user@example.com",
  "role": "requester" | "approver",
  "booking_id": "uuid",  # Optional
  "party": "Ingeborg" | "Cornelia" | "Angelika",  # For approvers
  "iat": 1234567890  # Issued-at timestamp
}
```

**Error messages (German, from specification):**
- Invalid token: `"Ungültiger Zugangslink."` (401)
- Wrong role: `"Diese Aktion ist für deine Rolle nicht verfügbar."` (403)
- No access: `"Du hast keinen Zugriff auf diesen Eintrag."` (403)

---

## Summary: ADRs are Law

**Critical reminders:**
1. ⚠️ **ADRs are constraints, not suggestions**
2. ⚠️ **Never violate an accepted ADR**
3. ⚠️ **Never alter an accepted ADR**
4. ⚠️ **Supersede with new ADR if needed**
5. ⚠️ **Propose before creating new ADR**
6. ⚠️ **Always use auth pattern from ADR-019**

**If you violate an ADR, the implementation is wrong. Full stop.**

---

**Next:** See [`/docs/design/`](../design/) for detailed API/DB/component design and [`/docs/implementation/`](../implementation/) to start building.
