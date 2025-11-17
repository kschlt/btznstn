# ADR-006: Type Safety Strategy

**Status:** Accepted
**Date:** 2025-01-17
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)

---

## Context

We need a comprehensive type safety strategy for both backend (Python/FastAPI) and frontend (TypeScript/Next.js). The system must:

- **Catch errors at compile time, not runtime** - Critical for AI-generated code
- **Validate data at boundaries** - API requests, database queries, external services
- **Enable confident refactoring** - AI can change code without breaking things
- **Self-document code** - Type annotations serve as inline documentation
- **Support IDE tooling** - Autocomplete, hover hints, go-to-definition

### Why Type Safety Matters for AI Development

**AI code generation challenges:**
- AI can introduce subtle type mismatches
- Refactoring AI code without types is dangerous
- Runtime errors are expensive (require debugging, redeployment)
- Type hints guide AI toward correct implementations

**Example (without types - risky):**
```python
def create_booking(data):
    # What's in data? What does this return?
    booking = db.save(data)
    return booking
```

**Example (with types - safe):**
```python
def create_booking(data: BookingCreate) -> Booking:
    # Clear contract. AI knows exactly what to pass and expect.
    booking = db.save(data)
    return booking
```

---

## Decision

We will enforce strict type safety across the entire stack:

### API (Python)
- **Mypy** in strict mode for static type checking
- **Pydantic v2** for runtime validation and serialization
- **Type hints** on all functions, methods, and variables
- **Ruff** for linting and enforcing type annotation coverage

### Web (TypeScript)
- **TypeScript strict mode** for static type checking
- **Zod** for runtime validation of API responses and form data
- **ESLint** with TypeScript rules
- **Type-safe API client** (generated from OpenAPI schema)

---

## Rationale

### 1. Mypy - Static Type Checking for Python

**Why Mypy:**

#### a) Industry Standard

- ✅ **Most mature** Python type checker
- ✅ **Gradual typing** - Can adopt incrementally (but we start strict)
- ✅ **PEP 484 compliant** - Follows official Python typing spec
- ✅ **IDE support** - Works with VS Code, PyCharm, etc.

#### b) Strict Mode Benefits

**Strict mode flags:**
```ini
# mypy.ini
[mypy]
strict = True
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_any_generics = True
disallow_subclassing_any = True
disallow_untyped_calls = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True
```

**What this catches:**
- Missing return type annotations
- Missing parameter type annotations
- Implicit `Any` types
- Invalid type operations (e.g., `str + int`)
- Unreachable code

**Example (Mypy catches error):**
```python
# booking.py
def calculate_days(start: date, end: date) -> int:
    return (end - start).days  # OK

def foo():
    # Mypy error: Argument 1 to "calculate_days" has incompatible type "str"; expected "date"
    days = calculate_days("2025-01-01", date.today())
```

**AI benefit:** AI gets immediate feedback if it generates invalid code.

#### c) Catch AI Mistakes Early

**Common AI mistakes Mypy catches:**
- Returning wrong type from function
- Passing wrong type to function
- Forgetting to handle `None` (Optional types)
- Using `Any` escape hatch incorrectly

**Example (AI forgets Optional handling):**
```python
def get_booking(id: UUID) -> Booking:
    # Mypy error: Incompatible return value type (got "Booking | None", expected "Booking")
    return db.query(Booking).filter_by(id=id).first()  # .first() can return None!

# Fix:
def get_booking(id: UUID) -> Booking | None:
    return db.query(Booking).filter_by(id=id).first()
```

### 2. Pydantic v2 - Runtime Validation

**Why Pydantic:**

#### a) Runtime Guarantees

**Mypy checks types at *edit time*. Pydantic validates at *runtime*.**

**Critical for:**
- API request validation
- Database query results
- External API responses
- Configuration loading

**Example:**
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Literal

class BookingCreate(BaseModel):
    requester_first_name: str = Field(
        min_length=1,
        max_length=40,
        pattern=r'^[a-zA-ZäöüÄÖÜß\s\-\']+$'
    )
    requester_email: EmailStr  # Validates email format at runtime
    start_date: date
    end_date: date
    party_size: int = Field(ge=1, le=10)
    affiliation: Literal["Ingeborg", "Cornelia", "Angelika"]
    description: str | None = Field(None, max_length=500)

# Usage:
try:
    booking_data = BookingCreate(**request.json())
except ValidationError as e:
    # AI doesn't need to write validation logic - Pydantic does it
    return {"error": e.errors()}
```

**AI benefit:** AI doesn't write validation code. Pydantic does it automatically.

#### b) FastAPI Integration (Zero-Cost)

**FastAPI uses Pydantic natively:**
```python
@app.post("/bookings", response_model=Booking)
def create_booking(data: BookingCreate):
    # FastAPI automatically:
    # 1. Validates request body against BookingCreate
    # 2. Converts JSON → Pydantic model
    # 3. Validates response against Booking
    # 4. Converts Pydantic model → JSON
    # 5. Generates OpenAPI schema

    booking = booking_service.create(data)
    return booking
```

**AI benefit:** One model definition = validation + serialization + docs.

#### c) V2 Performance

**Pydantic v2 rewrite (Rust core):**
- ✅ **5-50x faster** validation than v1
- ✅ **Strict mode** - No implicit coercion
- ✅ **Better error messages** - Easier to debug

**Example (strict mode):**
```python
class BookingCreate(BaseModel):
    model_config = {"strict": True}

    party_size: int  # Must be int, won't coerce "5" → 5

# Fails:
BookingCreate(party_size="5")  # ValidationError: Input should be a valid integer

# Passes:
BookingCreate(party_size=5)
```

### 3. TypeScript Strict Mode

**Why TypeScript Strict:**

#### a) Catch Errors Before Runtime

**Strict mode enables:**
```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

**What this catches:**
- Implicit `any` types
- Possible `null`/`undefined` access
- Type mismatches in function calls
- Uninitialized class properties
- Unused variables

**Example (strict catches error):**
```typescript
// TypeScript error: Object is possibly 'undefined'
function getBookingName(booking: Booking | undefined): string {
  return booking.requester_first_name  // Error!
}

// Fix:
function getBookingName(booking: Booking | undefined): string {
  if (!booking) return "Unknown"
  return booking.requester_first_name  // OK
}
```

#### b) AI-Friendly Autocomplete

**Type inference = Better AI code generation:**

```typescript
// API response type
type BookingResponse = {
  id: string
  requester_first_name: string
  start_date: string  // ISO date
  end_date: string
  party_size: number
  status: "Pending" | "Confirmed" | "Denied"
  affiliation: "Ingeborg" | "Cornelia" | "Angelika"
}

// AI knows exactly what properties exist:
function BookingCard({ booking }: { booking: BookingResponse }) {
  // AI gets autocomplete on booking.
  return (
    <div>
      <h2>{booking.requester_first_name}</h2>
      <p>{booking.party_size} Personen</p>
      <Badge status={booking.status} />
    </div>
  )
}
```

### 4. Zod - Runtime Validation for TypeScript

**Why Zod:**

#### a) TypeScript ↔ Runtime Validation Bridge

**Problem:** TypeScript types disappear at runtime.

**Example (unsafe):**
```typescript
type Booking = {
  id: string
  party_size: number
}

// TypeScript thinks this is safe:
const booking: Booking = await fetch("/api/bookings/123").then(r => r.json())

// But what if API returns:
// { "id": "abc", "party_size": "five" }  ← Wrong type!
// Runtime error when you use booking.party_size
```

**Solution:** Zod validates at runtime AND generates TypeScript types.

**Example (safe with Zod):**
```typescript
import { z } from "zod"

// Define schema (single source of truth)
const BookingSchema = z.object({
  id: z.string().uuid(),
  requester_first_name: z.string().min(1).max(40),
  party_size: z.number().int().min(1).max(10),
  status: z.enum(["Pending", "Confirmed", "Denied"]),
  affiliation: z.enum(["Ingeborg", "Cornelia", "Angelika"]),
})

// Extract TypeScript type
type Booking = z.infer<typeof BookingSchema>

// Validate API response
const response = await fetch("/api/bookings/123").then(r => r.json())
const booking = BookingSchema.parse(response)  // Throws if invalid

// Now booking is guaranteed to match Booking type
console.log(booking.party_size * 2)  // Safe!
```

**AI benefit:** One schema = runtime validation + TypeScript types.

#### b) Form Validation

**Integrate with React Hook Form:**
```typescript
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"

const BookingFormSchema = z.object({
  requester_first_name: z.string().min(1, "Dieses Feld wird benötigt.").max(40),
  requester_email: z.string().email("Bitte gib eine gültige E-Mail-Adresse an."),
  start_date: z.date(),
  end_date: z.date(),
  party_size: z.number().int().min(1).max(10),
  affiliation: z.enum(["Ingeborg", "Cornelia", "Angelika"]),
  description: z.string().max(500).optional(),
})

type BookingFormData = z.infer<typeof BookingFormSchema>

function BookingForm() {
  const form = useForm<BookingFormData>({
    resolver: zodResolver(BookingFormSchema),
  })

  // Form is fully type-safe and validated
}
```

**AI benefit:** Zod handles validation logic. AI just defines schema.

### 5. Ruff - Fast Python Linter

**Why Ruff:**

#### a) Enforce Type Annotation Coverage

**Ruff rule: `ANN` (flake8-annotations)**
```toml
# pyproject.toml
[tool.ruff]
select = ["ANN"]

# Enforces:
# ANN001: Missing type annotation for function argument
# ANN201: Missing return type annotation for public function
# ANN202: Missing return type annotation for private function
```

**Example (Ruff flags missing types):**
```python
# Ruff error: ANN001 Missing type annotation for function argument `data`
def create_booking(data):  # ← Missing type
    pass

# Fix:
def create_booking(data: BookingCreate) -> Booking:
    pass
```

#### b) 10-100x Faster Than Flake8

**Ruff is written in Rust:**
- ✅ **Instant feedback** - Runs in milliseconds
- ✅ **Replaces many tools** - Flake8 + isort + pyupgrade + etc.
- ✅ **Auto-fix** - Ruff can fix many issues automatically

**Example:**
```bash
# Run Ruff
ruff check .  # Check all files
ruff check --fix .  # Auto-fix issues

# Typical runtime: 50ms for entire codebase
# (Flake8 would take 5+ seconds)
```

### 6. ESLint - TypeScript Linting

**Why ESLint:**

#### a) Enforce TypeScript Best Practices

**Config:**
```json
// .eslintrc.json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/strict-boolean-expressions": "warn"
  }
}
```

**What this catches:**
- `any` escape hatches
- Unused variables
- Implicit boolean coercion
- Missing `await` on Promises

**Example:**
```typescript
// ESLint error: Unsafe assignment of an `any` value
const booking: Booking = await fetch(...).then(r => r.json())  // ← json() returns any

// Fix (with Zod):
const raw = await fetch(...).then(r => r.json())
const booking = BookingSchema.parse(raw)  // ← Validated
```

### 7. Type-Safe API Client (Generated)

**Why Generated Client:**

#### a) OpenAPI → TypeScript Types

**FastAPI generates OpenAPI schema:**
```bash
# Generate TypeScript client from OpenAPI
npx openapi-typescript http://localhost:8000/openapi.json --output ./types/api.ts
```

**Generated types:**
```typescript
// types/api.ts (auto-generated)
export interface paths {
  "/bookings": {
    post: {
      requestBody: {
        content: {
          "application/json": components["schemas"]["BookingCreate"]
        }
      }
      responses: {
        200: {
          content: {
            "application/json": components["schemas"]["Booking"]
          }
        }
      }
    }
  }
}
```

**Type-safe fetch:**
```typescript
import type { paths } from "./types/api"

async function createBooking(data: paths["/bookings"]["post"]["requestBody"]["content"]["application/json"]) {
  const response = await fetch("/api/bookings", {
    method: "POST",
    body: JSON.stringify(data),
  })

  const booking: paths["/bookings"]["post"]["responses"][200]["content"]["application/json"] = await response.json()
  return booking
}
```

**AI benefit:** API changes → Web types update automatically.

---

## Alternatives Considered

### Pyright (instead of Mypy)

**Pros:**
- Faster than Mypy
- Better IDE integration (VS Code)
- More strict by default

**Cons:**
- ❌ **Newer, less mature**
- ❌ **Smaller ecosystem**
- ❌ **Less AI training data** - Mypy is industry standard

**Decision:** Mypy has more AI training data. Widely adopted.

---

### TypeScript Loose Mode

**Pros:**
- Easier to get started
- More forgiving

**Cons:**
- ❌ **Defeats the purpose** - Type safety is the goal
- ❌ **AI mistakes slip through** - Errors caught at runtime
- ❌ **Tech debt** - Harder to fix later

**Decision:** Strict mode from day 1. No shortcuts.

---

### Joi (instead of Zod for TypeScript)

**Pros:**
- Mature, widely used
- Good error messages

**Cons:**
- ❌ **No TypeScript inference** - Can't generate types from schema
- ❌ **Separate type definitions** - DRY violation
- ❌ **More verbose**

**Decision:** Zod's TypeScript integration is unbeatable.

---

### No Runtime Validation (TypeScript only)

**Pros:**
- Simpler
- Less code

**Cons:**
- ❌ **Dangerous** - API responses are untrusted
- ❌ **Runtime errors** - Wrong types crash app
- ❌ **No form validation** - Have to write manually

**Decision:** Runtime validation is non-negotiable for production.

---

## Consequences

### Positive

✅ **AI errors caught early** - Compile-time, not runtime
✅ **Confident refactoring** - Type checker guides changes
✅ **Self-documenting code** - Types serve as inline docs
✅ **Better IDE support** - Autocomplete, hover hints
✅ **Fewer bugs** - Invalid states unrepresentable
✅ **Faster feedback loops** - Instant type errors in editor
✅ **Generated API types** - API ↔ Web sync
✅ **Form validation free** - Zod + Pydantic handle it

### Negative

⚠️ **More verbose** - Type annotations add lines of code
⚠️ **Learning curve** - Team needs to understand typing
⚠️ **Strictness friction** - Mypy/TSC can be pedantic

### Neutral

➡️ **CI/CD checks** - Must run Mypy + TSC + Ruff + ESLint in CI
➡️ **Type stub dependencies** - Need type stubs for third-party libraries
➡️ **Gradual adoption possible** - But we start strict

---

## Implementation Notes

### API Setup

#### 1. Install Dependencies
```bash
pip install mypy ruff pydantic[email] sqlalchemy[mypy]
```

#### 2. Mypy Config
```ini
# mypy.ini
[mypy]
python_version = 3.11
strict = True
plugins = pydantic.mypy, sqlalchemy.ext.mypy.plugin

[mypy-tests.*]
disallow_untyped_defs = False  # Relax for tests
```

#### 3. Ruff Config
```toml
# pyproject.toml
[tool.ruff]
select = ["E", "F", "I", "N", "UP", "ANN", "S", "B", "A", "C4", "T20", "RET", "SIM", "ARG"]
ignore = ["ANN101", "ANN102"]  # Ignore self/cls annotations
line-length = 100

[tool.ruff.per-file-ignores]
"tests/*" = ["S101"]  # Allow assert in tests
```

#### 4. Run Checks
```bash
# Type check
mypy src/

# Lint
ruff check src/

# Auto-fix
ruff check --fix src/
```

### Web Setup

#### 1. Install Dependencies
```bash
npm install zod @hookform/resolvers
npm install -D @typescript-eslint/eslint-plugin @typescript-eslint/parser
npm install -D openapi-typescript
```

#### 2. TypeScript Config
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM"],
    "jsx": "preserve",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "incremental": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

#### 3. ESLint Config
```json
// .eslintrc.json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": "error"
  }
}
```

#### 4. Generate API Types
```json
// package.json
{
  "scripts": {
    "generate-api-types": "openapi-typescript http://localhost:8000/openapi.json -o ./src/types/api.ts"
  }
}
```

```bash
npm run generate-api-types
```

### Example: End-to-End Type Safety

**API (FastAPI + Pydantic):**
```python
# models/booking.py
from pydantic import BaseModel, EmailStr, Field
from typing import Literal
from datetime import date
from uuid import UUID

class BookingCreate(BaseModel):
    requester_first_name: str = Field(min_length=1, max_length=40)
    requester_email: EmailStr
    start_date: date
    end_date: date
    party_size: int = Field(ge=1, le=10)
    affiliation: Literal["Ingeborg", "Cornelia", "Angelika"]
    description: str | None = Field(None, max_length=500)

class Booking(BookingCreate):
    id: UUID
    status: Literal["Pending", "Confirmed", "Denied"]
    created_at: datetime

# routes/bookings.py
@app.post("/bookings", response_model=Booking)
def create_booking(data: BookingCreate) -> Booking:
    # Mypy checks types. Pydantic validates runtime.
    booking = booking_service.create(data)
    return booking
```

**Web (TypeScript + Zod):**
```typescript
// schemas/booking.ts
import { z } from "zod"

export const BookingCreateSchema = z.object({
  requester_first_name: z.string().min(1).max(40),
  requester_email: z.string().email(),
  start_date: z.date(),
  end_date: z.date(),
  party_size: z.number().int().min(1).max(10),
  affiliation: z.enum(["Ingeborg", "Cornelia", "Angelika"]),
  description: z.string().max(500).optional(),
})

export type BookingCreate = z.infer<typeof BookingCreateSchema>

// api/bookings.ts
export async function createBooking(data: BookingCreate): Promise<Booking> {
  const response = await fetch("/api/bookings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  })

  const raw = await response.json()
  return BookingSchema.parse(raw)  // Runtime validation
}

// components/BookingForm.tsx
function BookingForm() {
  const form = useForm<BookingCreate>({
    resolver: zodResolver(BookingCreateSchema),
  })

  const onSubmit = async (data: BookingCreate) => {
    await createBooking(data)  // Fully type-safe
  }

  return <form onSubmit={form.handleSubmit(onSubmit)}>...</form>
}
```

**Result:**
- API validates with Pydantic, type-checks with Mypy
- Web validates with Zod, type-checks with TypeScript
- OpenAPI schema generated from Pydantic models
- Web types generated from OpenAPI schema
- End-to-end type safety from database to UI

---

## Validation

### CI/CD Checks

**GitHub Actions workflow:**
```yaml
# .github/workflows/type-check.yml
name: Type Check

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: mypy src/
      - run: ruff check src/

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: "20"
      - run: npm ci
      - run: npm run type-check
      - run: npm run lint
```

**Expected:** All checks pass on every commit.

### Local Pre-Commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
set -e

echo "Running Mypy..."
mypy src/

echo "Running Ruff..."
ruff check src/

echo "Running TypeScript..."
npm run type-check

echo "Running ESLint..."
npm run lint

echo "✅ All type checks passed!"
```

---

## References

- [Mypy Documentation](https://mypy.readthedocs.io/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Zod Documentation](https://zod.dev/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [OpenAPI TypeScript Generator](https://github.com/drwpow/openapi-typescript)

---

## Related ADRs

- [ADR-001: API Framework](adr-001-backend-framework.md) - FastAPI + Pydantic integration
- [ADR-002: Web Framework](adr-002-frontend-framework.md) - Next.js + TypeScript strict mode
- [ADR-008: Testing Strategy](adr-008-testing-strategy.md) - Type-safe test fixtures

---

## Changelog

- **2025-01-17:** Initial decision - Mypy + Pydantic + TypeScript strict + Zod chosen for comprehensive type safety
