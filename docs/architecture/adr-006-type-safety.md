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

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Type Hints | Explicit on all functions | Missing type hints, implicit Any |
| Backend Validation | Pydantic BaseModel | Manual JSON parsing, Marshmallow |
| Frontend Validation | Zod schemas | Manual validation, Yup/Joi |
| Static Checking | Mypy strict (backend), TypeScript strict (frontend) | Relaxed strict mode, Any types |
| Runtime Validation | Pydantic/Zod at boundaries | Skipped validation, untyped data |

---

## Rationale

**Why Mypy + Pydantic + TypeScript + Zod:**
- Mypy provides static type checking → **Constraint:** MUST use mypy strict mode, MUST have type hints on all functions
- Pydantic provides runtime validation → **Constraint:** MUST use Pydantic BaseModel for all request/response models
- TypeScript provides static type checking → **Constraint:** MUST use TypeScript strict mode, MUST have types on all functions
- Zod provides runtime validation → **Constraint:** MUST use Zod schemas for all form inputs and API responses

**Why NOT Marshmallow (Backend):**
- Marshmallow separates validation from types → **Violation:** Separate validation violates type safety requirement, no automatic OpenAPI generation

**Why NOT Yup (Frontend):**
- Yup has types separate from schemas → **Violation:** Separate types violates TypeScript-first requirement, less type-safe

---

## Consequences

### MUST (Required)

- ALL Python functions MUST have explicit type hints (return types and parameters) - Mypy strict mode requires types on every function
- ALL request/response models MUST inherit from `pydantic.BaseModel` - Pydantic provides runtime validation and type safety
- ALL form schemas MUST use Zod with type inference - Zod provides TypeScript-first runtime validation
- ALL API endpoints MUST use Pydantic models for validation - No manual JSON parsing, Pydantic validates automatically
- ALL database models MUST use SQLAlchemy type annotations (`Mapped[type]`) - Type-safe database models
- mypy strict mode MUST be enabled (`strict = True` in mypy.ini) - Strict mode catches type errors at compile time
- TypeScript strict mode MUST be enabled (`strict: true` in tsconfig.json) - Strict mode catches type errors at compile time
- Runtime validation MUST occur at all boundaries - API requests, database writes, external API calls must be validated

### MUST NOT (Forbidden)

- MUST NOT use `Any` type - Violates strict mode, defeats purpose of type safety
- MUST NOT skip type hints on functions - Mypy strict mode will fail
- MUST NOT use untyped dictionaries - Use `Dict[str, int]` or TypedDict instead of `dict`
- MUST NOT skip Pydantic validation - ALL inputs MUST be validated at API boundary
- MUST NOT skip Zod validation - ALL form inputs and API responses MUST be validated
- MUST NOT use `# type: ignore` without justification - Indicates design problem that should be fixed

### Trade-offs

- Many code examples skip type hints - MUST use explicit type hints on all functions. MUST NOT skip type annotations. Check for missing return types in function definitions.
- Code examples may use `Any` type - MUST use specific types. MUST NOT use `Any` type. Check for `Any` usage in codebase.
- Code examples may skip runtime validation - MUST use Pydantic/Zod at boundaries. MUST NOT skip validation. Check for manual JSON parsing or unvalidated API responses.

### Code Examples

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

# ✅ CORRECT: Type hints and Pydantic validation
from pydantic import BaseModel, Field
from datetime import date

class BookingCreate(BaseModel):
    requester_email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    start_date: date
    end_date: date
    party_size: int = Field(ge=1, le=10)

@router.post("/api/v1/bookings")
async def create_booking(
    data: BookingCreate,  # ✅ Pydantic validates automatically
    db: AsyncSession = Depends(get_db),
) -> BookingResponse:  # ✅ Explicit return type
    booking = await service.create_booking(data)
    return booking
```

```typescript
// ❌ WRONG: No validation, no types
const response = await fetch('/api/bookings')
const data = await response.json() // No type safety!

// ❌ WRONG: Using any
function processBooking(data: any): any {  // Defeats type safety
  return data
}

// ✅ CORRECT: Zod schema with type inference
import { z } from 'zod'

const BookingSchema = z.object({
  requesterEmail: z.string().email(),
  startDate: z.string().date(),
  endDate: z.string().date(),
  partySize: z.number().min(1).max(10),
})

type Booking = z.infer<typeof BookingSchema> // ✅ Type inferred

const response = await fetch('/api/bookings')
const data: Booking = BookingSchema.parse(await response.json()) // ✅ Validated
```

### Applies To

- ALL backend API endpoints (Phase 2, 3, 4)
- ALL frontend forms and API clients (Phase 5, 6, 7)
- ALL database models and repositories (all phases)
- ALL service layer functions (all phases)
- File patterns: `api/app/**/*.py`, `web/**/*.ts`, `web/**/*.tsx`

### Validation Commands

- Backend: `mypy app/` (must pass with strict mode)
- Frontend: `tsc --noEmit` (must pass with strict mode)
- Check for `Any` usage: `grep -r "Any" app/` (should be minimal/justified)
- Check for missing return types: `grep -r "^def " app/ | grep -v "->"` (should be empty)

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - Backend Framework (FastAPI + Pydantic integration)
- [ADR-002](adr-002-frontend-framework.md) - Frontend Framework (TypeScript native in Next.js)

---

## References

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - Backend Framework (FastAPI + Pydantic integration)
- [ADR-002](adr-002-frontend-framework.md) - Frontend Framework (TypeScript native)

**Tools:**
- [Mypy](https://mypy-lang.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [Zod](https://zod.dev/)
- [TypeScript](https://www.typescriptlang.org/)

**Implementation:**
- `api/mypy.ini` - Mypy strict mode configuration
- `web/tsconfig.json` - TypeScript strict mode configuration
- `api/app/schemas/` - Pydantic models
- `web/app/` - TypeScript files with Zod schemas
