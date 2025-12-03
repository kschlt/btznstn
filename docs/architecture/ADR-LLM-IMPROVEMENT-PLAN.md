# ADR LLM Improvement Plan

**Status:** Implementation In Progress
**Created:** 2025-11-21
**Purpose:** Systematically improve all ADRs for LLM consumption and action

---

## Goal

Transform all ADRs from human-team-oriented documentation to **LLM-actionable constraints** by:
1. Reframing "Consequences" from team perspective to implementation constraints
2. Adding "LLM Implementation Constraints" section with MUST/MUST NOT rules
3. Eliminating ambiguous language ("should" → "MUST")
4. Including validation checklists and exact error patterns

---

## Template Structure

### New Section: "LLM Implementation Constraints"

Insert AFTER "Consequences" section, BEFORE "Implementation Pattern" section:

```markdown
## LLM Implementation Constraints

### Required Patterns

**MUST:**
- [Bullet list of exact patterns with code examples]
- [Import statements required]
- [Specific function/method calls]

**MUST NOT:**
- [Anti-patterns to avoid]
- [Common mistakes from other frameworks/approaches]

**Example - Correct Pattern:**
\`\`\`[language]
[Code showing correct implementation]
\`\`\`

**Example - WRONG (Anti-patterns):**
\`\`\`[language]
[Code showing what NOT to do with comments explaining why]
\`\`\`

### Validation Checklist

Before considering implementation complete:
- [ ] [Specific validation with command to run]
- [ ] [Type check command]
- [ ] [Lint check command]
- [ ] [Test pattern validation]

### Error Handling Pattern (if applicable)

**For [scenario]:**
\`\`\`[language]
# German copy from docs/specification/error-handling.md:[line]
raise HTTPException([status], "[Exact German message]")
\`\`\`

### Related Patterns

- Test pattern: [file path]:[line]
- Business rules enforced: BR-XXX, BR-YYY
- German copy source: [spec file]:[section] (if applicable)
```

### Updated "Consequences" Section

**Replace:**
- "Positive" → "Implementation Constraints" (what the decision enforces)
- "Negative" → "Complexity Trade-offs" (added complexity, required discipline)
- Remove human-team language ("developers need to learn", "team must understand")

**Example Transformation:**

```markdown
❌ OLD (Human-Team Oriented):
### Negative
⚠️ **Newer framework** - Less mature than Flask/Django
⚠️ **Team needs to learn async patterns**

✅ NEW (LLM-Actionable Constraints):
### Complexity Trade-offs
⚠️ **All endpoints MUST be async** - Using `def` instead of `async def` blocks event loop
⚠️ **Blocking I/O forbidden** - Synchronous operations block all requests
```

---

## Implementation Status

### ✅ Completed (2/18)

| ADR | Title | Status | Notes |
|-----|-------|--------|-------|
| ADR-001 | Backend Framework | ✅ Complete | Added LLM constraints, updated Consequences |
| ADR-010 | DateTime/Timezone | ✅ Complete | Added LLM constraints, grep validation checks |

### 🔄 In Progress (0/18)

None

### ⏸️ Pending (16/18)

| ADR | Title | Priority | Estimated Time |
|-----|-------|----------|----------------|
| **ADR-006** | Type Safety | HIGH | 20 min |
| **ADR-019** | Auth & Authorization | HIGH | 20 min |
| **ADR-013** | SQLAlchemy ORM | HIGH | 25 min |
| **ADR-002** | Frontend Framework | MEDIUM | 20 min |
| **ADR-005** | UI Framework (Shadcn) | MEDIUM | 20 min |
| **ADR-008** | Testing Strategy | MEDIUM | 25 min |
| **ADR-009** | Test Patterns | MEDIUM | 25 min |
| **ADR-004** | Email Service (Resend) | MEDIUM | 15 min |
| **ADR-011** | CORS Security | LOW | 15 min |
| **ADR-012** | PostgreSQL Database | LOW | 15 min |
| **ADR-014** | Alembic Migrations | LOW | 15 min |
| **ADR-015** | Fly.io Postgres Hosting | LOW | 10 min |
| **ADR-016** | Fly.io Backend Hosting | LOW | 10 min |
| **ADR-017** | Vercel Frontend Hosting | LOW | 10 min |
| **ADR-018** | GitHub Actions CI/CD | LOW | 15 min |
| ADR-003 | Database & ORM (superseded) | SKIP | N/A |
| ADR-007 | Deployment (superseded) | SKIP | N/A |

**Total Estimated Time:** ~4-5 hours for all pending ADRs

---

## Priority Order (Suggested)

### Batch 1: Backend Core (HIGH - Do First)
1. ✅ ADR-001: Backend Framework (FastAPI)
2. ADR-006: Type Safety (Mypy + Pydantic)
3. ✅ ADR-010: DateTime/Timezone
4. ADR-013: SQLAlchemy ORM
5. ADR-019: Auth & Authorization

**Why:** These constrain 90% of backend implementation decisions

### Batch 2: Testing (HIGH - Do Second)
6. ADR-008: Testing Strategy
7. ADR-009: Test Patterns

**Why:** Phase 3-4 implementation starting soon, need test guidance

### Batch 3: Frontend Core (MEDIUM)
8. ADR-002: Frontend Framework (Next.js)
9. ADR-005: UI Framework (Shadcn/Tailwind)

**Why:** Needed for Phase 5+ (frontend work)

### Batch 4: Infrastructure (LOW - Can Wait)
10-15. ADR-004, ADR-011, ADR-012, ADR-014, ADR-015, ADR-016, ADR-017, ADR-018

**Why:** Deployment/hosting decisions already made, less frequently referenced

---

## Detailed Examples for Each Priority Category

### HIGH Priority Pattern: ADR-006 (Type Safety)

**Current State Analysis:**
- Has "Implementation Pattern" section ✅
- Consequences section says "Negative: Type annotations required" ⚠️
- Missing validation checklist ❌
- Missing MUST/MUST NOT rules ❌

**Required Changes:**
1. **Consequences → Implementation Constraints:**
   ```markdown
   ### Implementation Constraints
   ✅ **Static type checking enforced** - mypy catches type errors before runtime
   ✅ **Runtime validation at boundaries** - Pydantic/Zod validate all inputs
   ✅ **Type hints required** - All functions need explicit type annotations
   ```

2. **Add LLM Implementation Constraints:**
   ```markdown
   ## LLM Implementation Constraints

   ### Required Patterns

   **MUST (Backend):**
   - ALL functions have type hints: `def func(arg: Type) -> ReturnType:`
   - ALL API request/response models inherit from `pydantic.BaseModel`
   - ALL database models use SQLAlchemy `Mapped[Type]` annotations
   - Run `mypy app/` before every commit (CI enforces)

   **MUST NOT:**
   - Use `Any` type (violates type safety)
   - Skip type hints (mypy strict mode catches this)
   - Use dict for structured data (use Pydantic models)

   **Example - Correct Pattern:**
   ```python
   from pydantic import BaseModel, Field

   class BookingCreate(BaseModel):
       requester_email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
       party_size: int = Field(ge=1, le=10)

   async def create_booking(data: BookingCreate) -> BookingResponse:
       # Type-safe throughout
       return BookingResponse(...)
   ```

   **Example - WRONG:**
   ```python
   # ❌ No type hints
   async def create_booking(data):
       return {"status": "ok"}

   # ❌ Using Any
   def process(data: Any) -> Any:
       return data
   ```

   ### Validation Checklist
   - [ ] `mypy app/` passes with zero errors
   - [ ] All functions have type hints (check: `grep -r "def.*):$" app/`)
   - [ ] No `Any` types used (check: `grep -r "Any" app/`)
   - [ ] Pydantic models for all API boundaries
   ```

---

### MEDIUM Priority Pattern: ADR-008 (Testing Strategy)

**Required Changes:**
1. **Add test execution validation:**
   ```markdown
   ### Validation Checklist
   - [ ] All tests pass: `pytest tests/`
   - [ ] Coverage ≥80%: `pytest --cov=app --cov-report=term`
   - [ ] No test uses `datetime.now()`: `grep -r "datetime.now()" tests/`
   - [ ] All tests use factories: No `Booking(...)` constructors in tests
   ```

2. **Add test pattern constraints:**
   ```markdown
   **MUST:**
   - ALL integration tests use `AsyncClient` fixture (not manual creation)
   - ALL test data use factories from `tests/fixtures/factories.py`
   - ALL date operations use `get_today()` from `tests/utils.py`
   - German error messages validated with exact string from spec

   **MUST NOT:**
   - Create `AsyncClient` manually (breaks dependency injection)
   - Use `Booking(...)` constructors (use `make_booking()` factory)
   - Hardcode dates (use `get_today() + timedelta(days=X)`)
   - Test multiple scenarios in one test function
   ```

---

## Common Patterns Across All ADRs

### 1. German Error Message Pattern

**Add to ALL ADRs that deal with user-facing errors:**
```markdown
### Error Handling Pattern

**For [specific error scenario]:**
```python
from fastapi import HTTPException

# German copy from docs/specification/error-handling.md:[line]
raise HTTPException(
    status_code=[code],
    detail="[Exact German message from spec]",
)
```

**Validation:**
- [ ] German string matches spec exactly (no paraphrasing)
- [ ] Source comment includes file:line reference
```

### 2. Business Rule Reference Pattern

**Add to ADRs that enforce specific business rules:**
```markdown
### Related Patterns

**Business Rules Enforced:**
- BR-XXX: [Description] - [How this ADR enforces it]
- BR-YYY: [Description] - [How this ADR enforces it]

**Validation:**
- Check that implementation tests ALL applicable BRs
```

### 3. Validation Command Pattern

**Every checklist item should be executable:**
```markdown
❌ Vague: "Ensure all endpoints are async"
✅ Executable: `grep -r "^def " app/routers/` returns 0 results
```

---

## Self-Assessment Criteria

### Before/After Comparison Metrics

For each ADR, rate these aspects (1-10):

| Aspect | Weight | Description |
|--------|--------|-------------|
| **Actionability** | 30% | Can LLM execute constraints without ambiguity? |
| **Completeness** | 25% | All MUST/MUST NOT patterns documented? |
| **Validation** | 20% | Checkable items with commands? |
| **Clarity** | 15% | No "should", "typically", "usually"? |
| **LLM-Focus** | 10% | Zero human-team language? |

### Target Scores

- **Before (Current):** ~6.5/10 (good structure, human-oriented)
- **After (Target):** ~9.0/10 (LLM-actionable, constraint-focused)

### Success Criteria

ADR improvement is complete when:
- [ ] Zero instances of "should" / "typically" / "consider" (use "MUST" / "REQUIRED" / "FORBIDDEN")
- [ ] Zero instances of "team needs to learn" / "developers must understand" (use "MUST use pattern X")
- [ ] All validation items have executable commands (`grep`, `mypy`, `pytest`)
- [ ] All error scenarios have exact German copy with spec file:line reference
- [ ] All code examples show BOTH correct and wrong patterns

---

## Next Steps

1. **Review this plan** - Ensure template matches project goals
2. **Apply to Batch 1 ADRs** (ADR-006, ADR-013, ADR-019) - 3 HIGH priority
3. **Critical self-assessment** - Compare before/after for first 5 ADRs
4. **Iterate template if needed** - Refine based on first batch results
5. **Complete Batch 2** (ADR-008, ADR-009) - Testing guidance for Phase 3-4
6. **Defer Batch 3-4** until needed (frontend work is Phase 5+)

---

## Monitoring Progress

Track progress in this file:
- Update "Implementation Status" section as each ADR is completed
- Note any template refinements discovered during implementation
- Document estimated vs actual time for future planning

---

**Next Action:** Apply template to ADR-006 (Type Safety), critically assess result, refine template if needed.
