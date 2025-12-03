# ADR-001: Backend Framework

**Status:** Accepted
**Date:** 2025-01-17
**Deciders:** Solution Architect
**Context:** AI-driven development - need AI-friendly backend framework

---

## Context

Need backend framework for booking API that:
- Works well with AI code generation (Claude Code)
- Built-in type safety and validation
- Auto-generates API documentation
- Supports async/await for I/O operations
- Has strong ecosystem and community

---

## Decision

Use **FastAPI with Python 3.11+** as the backend framework.

---

## Rationale

### Why FastAPI vs Flask vs Django?

**FastAPI (Chosen):**
- ✅ **AI-friendly** - Standard patterns, well-documented, in Claude's training data
- ✅ **Built-in type safety** - Pydantic validation on all inputs
- ✅ **Auto-generated docs** - OpenAPI/Swagger UI for free
- ✅ **Async native** - FastAPI built on Starlette (async framework)
- ✅ **Modern Python** - Uses type hints, async/await

**Flask (Rejected):**
- ❌ No built-in validation (manual with Marshmallow)
- ❌ No automatic API docs
- ❌ WSGI-based (not async native)
- ❌ More boilerplate for REST APIs

**Django (Rejected):**
- ❌ Overkill (admin panel, ORM, templates not needed)
- ❌ Heavier (slower startup)
- ❌ Less async support
- ❌ More opinionated (harder for AI to navigate)

---

## Consequences

### Implementation Constraints

✅ **Validation handled by Pydantic** - Input validation automatic at request boundary
✅ **Async operations required** - I/O operations must use async/await pattern
✅ **Type hints required** - All endpoint functions need type annotations
✅ **OpenAPI schema generated** - API documentation auto-generated from types

### Complexity Trade-offs

⚠️ **All endpoints MUST be async** - Using `def` instead of `async def` blocks event loop
⚠️ **Blocking I/O forbidden** - Synchronous database/file/network operations will block all requests

### Neutral

➡️ **FastAPI patterns enforced** - Dependency injection, router structure are framework conventions

---

## LLM Implementation Constraints

### Required Patterns

**MUST:**
- ALL endpoint functions use `async def` (never `def`)
- ALL request/response models inherit from `pydantic.BaseModel`
- ALL database operations use async SQLAlchemy (`AsyncSession`)
- German error messages via `HTTPException(status_code, detail="German message")`

**MUST NOT:**
- Use synchronous I/O operations (`psycopg2`, `requests` library, blocking file reads)
- Use Flask/Django patterns (`@app.route`, `request.get_json()`)
- Skip Pydantic validation (validate ALL inputs at API boundary)

**Example - Correct Pattern:**
```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

class BookingCreate(BaseModel):
    """Request validation via Pydantic."""
    requester_email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    party_size: int = Field(ge=1, le=10)

@app.post("/api/v1/bookings")  # ✅ Versioned endpoint
async def create_booking(  # ✅ async def
    data: BookingCreate,  # ✅ Pydantic validation
    db: AsyncSession = Depends(get_db),  # ✅ Async DB
) -> BookingResponse:  # ✅ Type hint return
    """Create booking with automatic validation."""
    # German error message from spec
    if some_business_rule_violated:
        raise HTTPException(400, "Dieser Zeitraum ist ungültig.")

    booking = await service.create_booking(db, data)  # ✅ await
    return booking
```

**Example - WRONG (Anti-patterns):**
```python
# ❌ WRONG: Synchronous endpoint
@app.post("/bookings")
def create_booking(data: BookingCreate):  # Blocks event loop!
    booking = sync_db_call()  # Blocks all other requests
    return booking

# ❌ WRONG: No Pydantic validation
@app.post("/bookings")
async def create_booking(request: Request):
    data = await request.json()  # No validation!
    # Missing type safety
```

### Applies To

**This constraint affects:**
- ALL backend API endpoints (Phase 2, 3, 4)
- User story specifications must require `async def` pattern
- Acceptance criteria must validate Pydantic usage

### When Writing User Stories

**Ensure specifications include:**
- Endpoint uses `async def` signature
- Request/response models inherit from `pydantic.BaseModel`
- German error messages reference `docs/specification/error-handling.md`
- Database operations use async SQLAlchemy (`AsyncSession`)

**Related ADRs:**
- [ADR-006](adr-006-type-safety.md) - Type safety (Pydantic validation details)
- [ADR-013](adr-013-sqlalchemy-orm.md) - SQLAlchemy (async pattern details)

**Related Specifications:**
- German error messages: `docs/specification/error-handling.md`
- Business rules enforced: All BRs from `docs/foundation/business-rules.md` apply to endpoints

---

## Implementation Pattern

### Basic Endpoint

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class BookingCreate(BaseModel):
    """Pydantic auto-validates requests."""
    requester_email: str
    party_size: int

@app.post("/bookings")
async def create_booking(data: BookingCreate):
    """FastAPI auto-validates 'data' against BookingCreate schema."""
    if data.party_size > 10:
        raise HTTPException(400, "Party size too large")
    return {"status": "created"}
```

**What FastAPI gives us:**
- Auto-validation (Pydantic)
- Auto-docs (OpenAPI UI at `/docs`)
- Type hints everywhere
- Async support

---

## References

**Related ADRs:**
- ADR-006: Type Safety (Pydantic + FastAPI integration)
- ADR-008: Testing Strategy (Pytest + FastAPI testing)

**Tools:**
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [Starlette](https://www.starlette.io/) (underlying framework)

**Why FastAPI:**
- Modern Python (3.6+ type hints)
- Performance comparable to Node.js/Go
- Used by Microsoft, Uber, Netflix
