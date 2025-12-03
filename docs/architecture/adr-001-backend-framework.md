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

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Endpoints | `async def` | `def` blocks event loop |
| Validation | Pydantic `BaseModel` | Manual JSON parsing |
| Type Hints | Required on endpoints | Missing types break OpenAPI |
| Framework | FastAPI patterns | Flask/Django patterns |
| I/O Operations | Async/await | Blocking operations (`requests`, `psycopg2`) |

---

## Rationale

**Why FastAPI:**
- FastAPI requires async-native architecture → **Constraint:** ALL endpoint functions MUST use `async def` (never `def`)
- FastAPI uses Pydantic for validation → **Constraint:** ALL request/response models MUST inherit from `pydantic.BaseModel`
- FastAPI built on Starlette (async framework) → **Constraint:** ALL I/O operations MUST use async/await pattern
- FastAPI auto-generates OpenAPI docs → **Constraint:** Type hints required on all endpoint functions

**Why NOT Flask:**
- Flask uses WSGI (synchronous) → **Violation:** WSGI-based frameworks block event loop, preventing async I/O operations
- Flask requires manual validation → **Violation:** Manual validation (Marshmallow) violates type safety requirement and increases boilerplate

---

## Consequences

### MUST (Required)

- ALL endpoint functions MUST use `async def` (never `def`) - FastAPI requires async-native architecture to prevent blocking event loop
- ALL request/response models MUST inherit from `pydantic.BaseModel` - FastAPI uses Pydantic for automatic validation at request boundary
- Type hints MUST be used on all endpoint functions - Required for OpenAPI schema generation
- MUST use FastAPI dependency injection (`Depends()`) - FastAPI's built-in dependency injection system

### MUST NOT (Forbidden)

- MUST NOT use synchronous I/O operations (blocking database drivers, `requests` library, blocking file reads) - Blocks event loop, preventing async operations
- MUST NOT use Flask/Django patterns (`@app.route`, `request.get_json()`) - Violates FastAPI decision and lacks built-in validation
- MUST NOT skip Pydantic validation - ALL inputs MUST be validated at API boundary using Pydantic models

### Trade-offs

- Many code examples use synchronous patterns - MUST use `async def` for endpoints. MUST NOT use `def` for endpoints. Check for `def` in router files.
- Code examples may use blocking I/O libraries - MUST use async libraries (async database drivers, `httpx`, `aiofiles`). MUST NOT use blocking libraries (sync database drivers, `requests`). Check for blocking library imports.

### Code Examples

```python
# ❌ WRONG: Synchronous endpoint blocks event loop
@app.post("/bookings")
def create_booking(data: BookingCreate):  # Blocks event loop!
    booking = sync_db_call()  # Blocks all other requests
    return booking

# ❌ WRONG: No Pydantic validation
@app.post("/bookings")
async def create_booking(request: Request):
    data = await request.json()  # No validation!
    # Missing type safety

# ✅ CORRECT: Async endpoint with Pydantic validation
from fastapi import FastAPI, Depends
from pydantic import BaseModel, Field

app = FastAPI()

class BookingCreate(BaseModel):
    """Request validation via Pydantic."""
    requester_email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    party_size: int = Field(ge=1, le=10)

@app.post("/api/v1/bookings")  # ✅ Versioned endpoint
async def create_booking(  # ✅ async def
    data: BookingCreate,  # ✅ Pydantic validation
    db = Depends(get_db),  # ✅ FastAPI dependency injection
) -> BookingResponse:  # ✅ Type hint return
    """Create booking with automatic validation."""
    booking = await service.create_booking(db, data)  # ✅ await
    return booking
```


### Applies To

- ALL backend API endpoints (Phase 2, 3, 4)
- File patterns: `app/routers/*.py`
- User story specifications must require `async def` pattern
- Acceptance criteria must validate Pydantic usage

### Validation Commands

- `grep -r "def.*\(.*\):" app/routers/` (should only show `async def`, not `def`)
- `grep -r "from pydantic import BaseModel" app/schemas/` (should be present in all schema files)
- `grep -r "@app\.route\|from flask\|from django" app/` (should be empty - must use FastAPI)

**Related ADRs:**
- [ADR-006](adr-006-type-safety.md) - Type safety (Pydantic validation details)

---

## References

**Related ADRs:**
- [ADR-006](adr-006-type-safety.md) - Type Safety (Pydantic + FastAPI integration)
- [ADR-008](adr-008-testing-strategy-SUPERSEDED.md) - Testing Strategy (Superseded by ADR-020, ADR-021)

**Tools:**
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pydantic](https://docs.pydantic.dev/)
- [Starlette](https://www.starlette.io/) - Underlying framework

**Implementation:**
- `app/main.py` - FastAPI application setup
- `app/routers/*.py` - API endpoints
- `app/schemas/*.py` - Pydantic models
