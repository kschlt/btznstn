# ADR-001: API Framework - FastAPI

**Status:** Accepted
**Date:** 2025-01-17
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)

---

## Context

We need to choose a backend framework for the Betzenstein booking & approval application. The framework must support:

- RESTful API development
- Type safety (Python type hints)
- Auto-generated API documentation
- Async I/O for email sending
- Easy integration with PostgreSQL
- Well-documented for AI implementation

### Requirements from Specifications

From `docs/foundation/business-rules.md` and `docs/constraints/technical-constraints.md`:

- **BR-010:** Stateless token-based authentication (no sessions)
- **BR-012:** Rate limiting (configurable)
- **BR-022:** Email retries with backoff
- **Type safety:** Python type hints with mypy
- **Mobile-first:** Fast API responses (< 500ms target)
- **AI implementation:** Framework AI agents know well

---

## Decision

We will use **FastAPI** with **Python 3.11+** as the backend framework.

---

## Rationale

### 1. AI-Friendly (Critical)

**Why this matters:** All implementation will be done by Claude Code.

**FastAPI benefits:**
- ✅ **Extensive training data** - AI knows FastAPI extremely well
- ✅ **Clear documentation** - Official docs are excellent, AI can reference
- ✅ **Standard patterns** - Convention over configuration
- ✅ **Auto-generated examples** - OpenAPI docs help AI understand API

**Evidence:** FastAPI is one of the most well-documented Python frameworks. AI agents consistently generate correct FastAPI code.

### 2. Built-in Type Safety

**Requirement:** Catch AI errors at compile/validation time.

**FastAPI benefits:**
- ✅ **Pydantic v2 integration** - Runtime validation on all inputs/outputs
- ✅ **Type hints required** - Forces explicit types
- ✅ **Mypy compatible** - Static type checking
- ✅ **Auto-validation** - Rejects invalid requests before business logic

**Example:**
```python
class BookingCreate(BaseModel):
    requester_first_name: str = Field(max_length=40, pattern=r'^[a-zA-ZäöüÄÖÜß\s\-\']+$')
    requester_email: EmailStr
    start_date: date
    end_date: date
    party_size: int = Field(ge=1, le=10)
    affiliation: Literal["Ingeborg", "Cornelia", "Angelika"]
    description: str | None = Field(None, max_length=500)

@app.post("/bookings")
async def create_booking(booking: BookingCreate):
    # Pydantic already validated everything
    # AI can't make validation mistakes
    ...
```

### 3. Auto-Generated OpenAPI Documentation

**Benefit:** API docs generated automatically from code.

**FastAPI:**
- ✅ Swagger UI at `/docs` (interactive API explorer)
- ✅ ReDoc at `/redoc` (detailed documentation)
- ✅ OpenAPI 3.0 spec (machine-readable)
- ✅ TypeScript client generation (for frontend)

**AI benefit:** AI can reference the auto-generated docs to understand API contracts.

### 4. Async/Await Native

**Requirement:** Send emails without blocking API responses.

**FastAPI:**
- ✅ Built on Starlette (async-first)
- ✅ Native async/await support
- ✅ Can use `asyncio` and `httpx` for Resend API calls
- ✅ Non-blocking I/O for database (async SQLAlchemy)

**Example:**
```python
@app.post("/bookings/{id}/approve")
async def approve_booking(id: UUID, token: str):
    # Non-blocking database queries
    booking = await booking_repo.get(id)
    await approval_service.approve(booking, token)

    # Non-blocking email sending
    await email_service.send_approval_notification(booking)

    return {"status": "approved"}
```

### 5. Performance

**Requirement:** API response < 500ms (p95).

**FastAPI:**
- ✅ One of fastest Python frameworks (benchmark: ~20k req/s)
- ✅ Uvicorn/Gunicorn deployment (production-ready ASGI)
- ✅ Efficient request parsing (Pydantic Rust core)

**Good enough:** For small-scale app (~100 req/day), FastAPI is overkill performance-wise. But no downside.

### 6. Database Integration

**Requirement:** PostgreSQL + SQLAlchemy 2.0.

**FastAPI:**
- ✅ Excellent SQLAlchemy integration
- ✅ Async SQLAlchemy support
- ✅ Alembic migrations standard
- ✅ Dependency injection for DB sessions

**Example:**
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session

@app.get("/bookings")
async def list_bookings(db: AsyncSession = Depends(get_db)):
    bookings = await booking_repo.list(db)
    return bookings
```

### 7. Ecosystem Maturity

**FastAPI ecosystem:**
- ✅ Mature (5+ years, stable)
- ✅ Large community (65k+ GitHub stars)
- ✅ Well-maintained (frequent updates)
- ✅ Production-proven (Netflix, Uber, etc.)

---

## Alternatives Considered

### Django REST Framework

**Pros:**
- Very mature
- Batteries-included (ORM, admin, auth)
- Large ecosystem

**Cons:**
- ❌ **Sync-first** (async support still experimental)
- ❌ **Heavy** (too much for this app)
- ❌ **Opinionated** (we don't need Django's batteries)
- ❌ **Less AI-friendly** (more boilerplate, less clear patterns)

**Decision:** Too heavy for needs, async not first-class.

---

### Flask

**Pros:**
- Lightweight
- Flexible
- AI knows it well

**Cons:**
- ❌ **No built-in validation** (need Flask-Pydantic or similar)
- ❌ **No auto-docs** (need Flask-RESTX or similar)
- ❌ **Sync-only** (Flask 2.0 has async, but not as mature)
- ❌ **More boilerplate** (more for AI to get wrong)

**Decision:** FastAPI is Flask's successor for APIs (same creator).

---

### Node.js (Express/NestJS)

**Pros:**
- Very mature (Express)
- TypeScript native (NestJS)
- Fast

**Cons:**
- ❌ **Not requester's preference** (wants Python)
- ❌ **Less type-safe than FastAPI+Pydantic** (TypeScript is less strict than Pydantic)
- ❌ **Additional ecosystem** (Python for scripts, Node for backend = split)

**Decision:** Python preferred, FastAPI is better choice.

---

## Consequences

### Positive

✅ **AI can implement quickly** - FastAPI is AI-friendly
✅ **Type-safe API** - Pydantic validates everything
✅ **Auto-generated docs** - Web team (AI) can reference
✅ **Fast development** - Less boilerplate than alternatives
✅ **Modern async** - Non-blocking email/DB operations
✅ **Production-ready** - Mature, proven framework

### Negative

⚠️ **Learning curve** (minor) - Async/await concepts (but AI handles this)
⚠️ **Less batteries** than Django (but we don't need them)
⚠️ **Python typing strictness** - Good for AI, but requires discipline

### Neutral

➡️ **Requires Uvicorn/Gunicorn** for production (standard, easy)
➡️ **Separate ORM** (SQLAlchemy, but that's a feature)
➡️ **Dependency injection** pattern (clean, but different from Flask)

---

## Implementation Notes

### Project Structure

```
/api/
├── app/
│   ├── main.py              # FastAPI app creation
│   ├── api/
│   │   └── v1/
│   │       ├── bookings.py  # Booking endpoints
│   │       ├── approvals.py # Approval endpoints
│   │       └── auth.py      # Token validation
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── repositories/        # Data access
│   └── core/
│       ├── config.py        # Settings (Pydantic BaseSettings)
│       ├── database.py      # DB session management
│       └── security.py      # Token signing/validation
├── tests/
├── alembic/                 # Migrations
├── requirements.txt
└── pyproject.toml           # Ruff, mypy config
```

### Key Dependencies

```txt
fastapi[all]==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy[asyncio]==2.0.25
alembic==1.13.1
pydantic[email]==2.5.0
pydantic-settings==2.1.0
asyncpg==0.29.0              # PostgreSQL async driver
httpx==0.26.0                # Async HTTP (for Resend)
python-jose[cryptography]==3.3.0  # JWT token signing
```

### Deployment

**Development:**
```bash
uvicorn app.main:app --reload
```

**Production (Fly.io):**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## Validation

### Type Safety Check

```bash
mypy app/
```

**Expected:** Zero type errors.

### Linting Check

```bash
ruff check app/
```

**Expected:** Zero linting errors.

### Auto-Generated Docs

After running:
```bash
uvicorn app.main:app
```

Visit: `http://localhost:8000/docs`

**Expected:** Interactive Swagger UI with all endpoints.

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- Business Rules: `docs/foundation/business-rules.md`
- Technical Constraints: `docs/constraints/technical-constraints.md`

---

## Related ADRs

- [ADR-003: Database & ORM](adr-003-database-orm.md) - SQLAlchemy integration
- [ADR-006: Type Safety Strategy](adr-006-type-safety.md) - Mypy + Pydantic
- [ADR-007: Deployment Strategy](adr-007-deployment.md) - Fly.io deployment

---

## Changelog

- **2025-01-17:** Initial decision - FastAPI chosen for backend framework
