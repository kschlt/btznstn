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

### Positive

✅ **Type safety** - Pydantic catches errors at request time
✅ **Fast development** - Less boilerplate than Flask/Django
✅ **Great DX** - Auto-reload, interactive docs, clear errors
✅ **Performance** - Async handles I/O efficiently

### Negative

⚠️ **Newer framework** - Less mature than Flask/Django (but stable since 2018)
⚠️ **Async-only** - All endpoints must use `async def` (blocking I/O will block event loop)

### Neutral

➡️ **Opinionated** - FastAPI has "the FastAPI way" (good for consistency)

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
