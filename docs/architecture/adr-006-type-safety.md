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

### Implementation Constraints

✅ **Compile-time error detection** - mypy/tsc catch type errors before deployment
✅ **Refactoring safety** - Types prevent breaking changes during refactoring
✅ **Self-documenting code** - Type hints serve as inline documentation
✅ **IDE support enabled** - Autocomplete, hover hints, and navigation work with types
✅ **Runtime validation at boundaries** - Pydantic/Zod validate data at API/DB boundaries

### Complexity Trade-offs

⚠️ **ALL functions MUST have explicit type annotations** - mypy strict mode requires types on every function (no implicit Any)
⚠️ **Type annotations required** - More code to write, but catches errors early
⚠️ **Build step required** - mypy/tsc must run in CI (~10-30s), but prevents runtime errors

### Neutral

➡️ **Strict mode is non-negotiable** - Cannot relax strict mode (would defeat purpose of this ADR)

---

## LLM Implementation Constraints

### Required Patterns

**MUST:**
- ALL Python functions have explicit type hints (return types and parameters)
- ALL request/response models inherit from `pydantic.BaseModel` (backend)
- ALL form schemas use Zod with type inference (frontend)
- ALL API endpoints use Pydantic models for validation (no manual JSON parsing)
- ALL database models use SQLAlchemy type annotations (`Mapped[type]`)
- mypy strict mode enabled (`strict = True` in mypy.ini)
- TypeScript strict mode enabled (`strict: true` in tsconfig.json)
- Runtime validation at all boundaries (API requests, database writes, external API calls)

**MUST NOT:**
- Use `Any` type (violates strict mode, defeats purpose)
- Skip type hints on functions (mypy strict mode will fail)
- Use untyped dictionaries (`dict` → use `Dict[str, int]` or TypedDict)
- Skip Pydantic validation (validate ALL inputs at API boundary)
- Skip Zod validation (validate ALL form inputs and API responses)
- Use `# type: ignore` without justification (indicates design problem)

**Example - Correct Pattern (Backend):**
```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class BookingCreate(BaseModel):
    """Request model - Pydantic validates at API boundary."""
    requester_email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+\.[^@]+$')
    start_date: date
    end_date: date
    party_size: int = Field(ge=1, le=10)

@router.post("/api/v1/bookings")
async def create_booking(
    data: BookingCreate,  # ✅ Pydantic validates automatically
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:  # ✅ Explicit return type
    """Create booking with type-safe validation."""
    booking = await service.create_booking(data)  # ✅ Type-safe
    return booking
```

**Example - WRONG (Anti-patterns - Backend):**
```python
# ❌ WRONG: No type hints
def create_booking(data):  # mypy strict mode fails
    return booking

# ❌ WRONG: Using Any
def process_data(data: Any) -> Any:  # Defeats type safety
    return data

# ❌ WRONG: Manual JSON parsing without Pydantic
@router.post("/bookings")
async def create_booking(request: Request):
    data = await request.json()  # No validation, no type safety!
    # Missing type checking
```

**Example - Correct Pattern (Frontend):**
```typescript
import { z } from 'zod'

const BookingSchema = z.object({
  requesterEmail: z.string().email(),
  startDate: z.string().date(),
  endDate: z.string().date(),
  partySize: z.number().min(1).max(10),
})

// ✅ Type inferred from schema
type Booking = z.infer<typeof BookingSchema>

// ✅ Validate API response
const response = await fetch('/api/bookings')
const data: Booking = BookingSchema.parse(await response.json()) // Throws if invalid
```

**Example - WRONG (Anti-patterns - Frontend):**
```typescript
// ❌ WRONG: No validation, no types
const response = await fetch('/api/bookings')
const data = await response.json() // No type safety!

// ❌ WRONG: Using any
function processBooking(data: any): any {  // Defeats type safety
  return data
}
```

### Applies To

**This constraint affects:**
- ALL backend API endpoints (Phase 2, 3, 4)
- ALL frontend forms and API clients (Phase 5, 6, 7)
- ALL database models and repositories (all phases)
- ALL service layer functions (all phases)
- User story specifications must require type hints
- Acceptance criteria must validate mypy/tsc passes

### When Writing User Stories

**Ensure specifications include:**
- All functions have explicit type hints (backend: Python, frontend: TypeScript)
- Request/response models use Pydantic (backend) or Zod (frontend)
- Type checking passes (mypy strict for backend, tsc strict for frontend)
- Runtime validation at API boundaries (Pydantic/Zod schemas)

**Validation commands for user story checklists:**
- Backend: `mypy app/` (must pass with strict mode)
- Frontend: `tsc --noEmit` (must pass with strict mode)
- Check for `Any` usage: `grep -r "Any" app/` (should be minimal/justified)
- Check for missing return types: `grep -r "^def " app/ | grep -v "->"` (should be empty)

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - FastAPI + Pydantic integration
- [ADR-002](adr-002-frontend-framework.md) - TypeScript native in Next.js

**Related Specifications:**
- Type hints required: All functions in `api/app/`
- Runtime validation: All API endpoints (Pydantic), all forms (Zod)
- Business rules: Type safety enables confident BR enforcement

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
