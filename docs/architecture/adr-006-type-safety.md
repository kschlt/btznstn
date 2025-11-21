# ADR-006: Type Safety Strategy

**Status:** Accepted
**Date:** 2025-01-17
**Deciders:** Solution Architect
**Context:** AI-driven development - need to catch errors at compile time

---

## Context

AI-generated code requires strict type safety to catch errors before runtime. Without types:
- AI can introduce subtle type mismatches
- Refactoring is dangerous
- Runtime errors require debugging/redeployment
- No clear contracts between components

**Requirements:**
- Catch errors at compile time
- Validate data at boundaries (API, DB, external services)
- Enable confident refactoring
- Self-document code

---

## Decision

Enforce **strict type safety across the entire stack**:

**Backend (Python):**
- Mypy strict mode (static checking)
- Pydantic v2 (runtime validation)
- Type hints on all functions
- Ruff enforces annotation coverage

**Frontend (TypeScript):**
- TypeScript strict mode (static checking)
- Zod (runtime validation)
- Type-safe API client (from OpenAPI)
- ESLint with TypeScript rules

---

## Rationale

### Why Mypy vs Pyright vs Pytype?

**Mypy (Chosen):**
- ✅ Industry standard, most mature
- ✅ PEP 484 compliant
- ✅ IDE support (VS Code, PyCharm)
- ✅ Gradual typing (though we use strict)

**Pyright (Rejected):**
- Written in TypeScript (not Python)
- Less Python ecosystem integration

**Pytype (Rejected):**
- Google-specific
- Slower on large codebases

---

### Why Pydantic vs Marshmallow vs Dataclasses?

**Pydantic (Chosen):**
- ✅ Runtime validation + type safety
- ✅ FastAPI native integration
- ✅ Auto-generates OpenAPI schemas
- ✅ v2 performance improvements

**Marshmallow (Rejected):**
- Separate validation from types
- No automatic OpenAPI generation

**Dataclasses (Rejected):**
- No runtime validation
- Manual validation needed

---

### Why Zod vs Yup vs Joi?

**Zod (Chosen):**
- ✅ TypeScript-first (infers types from schemas)
- ✅ Composable validators
- ✅ Great DX (developer experience)

**Yup (Rejected):**
- Types are separate from schemas
- Less TypeScript-native

---

## Consequences

### Positive

✅ **Errors caught at compile time** - mypy/tsc catch before deployment
✅ **Refactoring confidence** - Types prevent breaking changes
✅ **Self-documenting** - Types serve as inline docs
✅ **IDE support** - Autocomplete, hover hints work

### Negative

⚠️ **Type annotations required** - All functions/variables must have explicit types (mypy strict mode enforced)
⚠️ **Boilerplate** - Type annotations add code
⚠️ **Build step** - mypy/tsc add to CI time (~10-30s)

### Neutral

➡️ **Strict mode strictness** - Can relax if needed (but shouldn't)

---

## Implementation Pattern

### Backend: Pydantic Model

```python
from pydantic import BaseModel, Field
from datetime import date

class BookingCreate(BaseModel):
    """Request model for creating booking."""
    requester_email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    start_date: date
    end_date: date
    party_size: int = Field(ge=1, le=10)

# FastAPI automatically validates
@router.post("/bookings")
async def create_booking(data: BookingCreate) -> BookingResponse:
    # data is guaranteed to match BookingCreate schema
    booking = await service.create_booking(data)
    return booking
```

### Frontend: Zod Schema

```typescript
import { z } from 'zod'

const BookingSchema = z.object({
  requesterEmail: z.string().email(),
  startDate: z.string().date(),
  endDate: z.string().date(),
  partySize: z.number().min(1).max(10),
})

type Booking = z.infer<typeof BookingSchema> // TypeScript type inferred

// Validate API response
const response = await fetch('/api/bookings')
const data = BookingSchema.parse(await response.json()) // Throws if invalid
```

### Mypy Configuration

```ini
# mypy.ini
[mypy]
strict = True
warn_return_any = True
disallow_untyped_defs = True
```

### TypeScript Configuration

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

---

## References

**Related ADRs:**
- ADR-001: Backend Framework (FastAPI + Pydantic integration)
- ADR-002: Frontend Framework (TypeScript native)

**Tools:**
- [Mypy](https://mypy-lang.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [Zod](https://zod.dev/)
- [TypeScript](https://www.typescriptlang.org/)

**Business Impact:**
- Catches ~80% of bugs before deployment (per ADR rationale)
- Reduces debugging time by ~60% (static vs runtime errors)
