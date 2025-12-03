# ADR Template for LLM Consumption

**Purpose:** This template ensures ADRs provide **immutable architectural constraints** that LLMs must follow when generating user stories and implementing features.

---

## Key Principle

**ADRs are GUARDRAILS, not implementation guides:**
- ✅ "We chose FastAPI" (immutable decision)
- ✅ "MUST use async, MUST NOT use Flask" (universal constraint)
- ❌ NOT "Validate party_size 1-10" (that's user story/BR level)
- ❌ NOT implementation checklists (those belong in user stories)

**ADRs constrain the HOW (framework/approach), user stories define the WHAT (specific feature).**

---

## Template Structure

### 1. Context (Keep Existing)

Brief explanation of WHAT problem this decision solves and WHY it matters.

---

### 2. Decision (Keep Existing)

Clear statement of WHAT was decided.

---

### 3. Rationale (Keep Existing)

Comparison of alternatives (Chosen vs Rejected).

---

### 4. Consequences (**MODIFY THIS**)

**Replace human-team language with LLM-actionable constraints:**

```markdown
## Consequences

### Implementation Constraints

✅ [What this decision ENFORCES across all implementations]
✅ [Pattern that MUST always be followed]
✅ [Library/approach that is REQUIRED]

### Complexity Trade-offs

⚠️ [Added complexity from this decision with specific constraint]
⚠️ [Discipline required with exact pattern to follow]

### Neutral

➡️ [Trade-offs that aren't strictly positive or negative]
```

**Example Transformation:**

```markdown
❌ OLD (Human-Team):
### Negative
⚠️ Team needs to learn async patterns

✅ NEW (LLM-Constraint):
### Complexity Trade-offs
⚠️ **All endpoints MUST be async** - Using `def` instead of `async def` blocks event loop
```

---

### 5. LLM Implementation Constraints (**ADD THIS NEW SECTION**)

**Insert AFTER "Consequences", BEFORE any "Implementation Pattern" section:**

```markdown
## LLM Implementation Constraints

**Purpose:** Absolute constraints from this architectural decision that MUST be enforced in all user stories and implementations.

### MUST (Required)

- [Absolute requirement - framework/library to use]
- [Pattern that MUST always be used]
- [Import/module that is REQUIRED]

### MUST NOT (Forbidden)

- [Anti-pattern that violates this ADR]
- [Framework/library that conflicts with this decision]
- [Common mistake from other approaches]

### Pattern Example

**This decision requires:**
\```[language]
# Minimal example (2-5 lines) showing the constraint
[Code showing required pattern]
\```

**This decision forbids:**
\```[language]
# Example of what violates this ADR (2-5 lines)
# ❌ WRONG: [Why this violates the constraint]
[Code showing forbidden pattern]
\```

### Applies To

**This constraint affects:**
- [Which phases this applies to]
- [Which types of user stories need this constraint]
- [Which specification files must reflect this]

### When Writing User Stories

**Ensure specifications include:**
- [Constraint that must appear in acceptance criteria]
- [Pattern that must be referenced in implementation notes]
- [Validation command that belongs in user story checklist]

**Related ADRs:**
- [ADR-XXX](adr-xxx.md) - [How it relates]

**Related Specifications:**
- [Which spec files this decision affects]
- [Which business rules this enables/constrains]
```

---

### 6. Implementation Pattern (Keep if Exists, Optional)

Minimal reference example (not a tutorial).

---

### 7. References (Keep Existing)

Links to related ADRs, tools, business rules.

---

## What NOT to Include in ADRs

❌ **Implementation checklists** → Belong in user stories
❌ **Specific validation rules** (e.g., "party_size 1-10") → Belong in BRs + user stories
❌ **Step-by-step implementation guides** → Belong in phase docs
❌ **Test writing instructions** → Belong in user story acceptance criteria
❌ **"Before considering complete..."** language → Belongs in user story DoD

---

## What TO Include in ADRs

✅ **Framework/library decisions** (FastAPI, not Flask)
✅ **Universal patterns** (async everywhere, not sync)
✅ **Forbidden anti-patterns** (don't use Flask patterns)
✅ **Which phases/specs this affects**
✅ **Validation commands for user story checklists** (not in ADR, but ADR tells user stories what to check)

---

## Example: ADR-001 (Backend Framework)

### LLM Implementation Constraints

**MUST:**
- ALL backend endpoints use FastAPI framework
- ALL endpoints use `async def` (not `def`)
- ALL request/response validation via Pydantic `BaseModel`

**MUST NOT:**
- Use Flask or Django (violates ADR-001 decision)
- Use synchronous `def` endpoints (blocks event loop)
- Use manual JSON parsing (use Pydantic validation)

**Pattern Example:**

**Required:**
\```python
from fastapi import FastAPI
from pydantic import BaseModel

@app.post("/api/v1/bookings")
async def create_booking(data: BookingCreate) -> BookingResponse:
    # FastAPI + Pydantic + async
\```

**Forbidden:**
\```python
# ❌ WRONG: Flask pattern
@app.route("/bookings", methods=["POST"])
def create_booking():
    data = request.get_json()  # Violates ADR-001
\```

**Applies To:**
- ALL backend API endpoints (Phase 2, 3, 4)
- User stories must specify `async def` + Pydantic models

**When Writing User Stories:**
- Acceptance criteria MUST include: "Endpoint uses `async def`"
- Implementation notes MUST reference: Pydantic model for validation
- User story checklist SHOULD include: `grep -r "^def " app/routers/` returns 0

---

## Key Differences from Previous Template

**REMOVED:**
- ❌ Validation checklists in ADR (moved to user stories)
- ❌ "Before considering implementation complete" (implementation happens in user stories)
- ❌ Step-by-step guides (ADRs are constraints, not tutorials)

**KEPT:**
- ✅ MUST/MUST NOT (absolute constraints)
- ✅ Pattern examples (minimal reference, not tutorial)
- ✅ "Applies To" (helps LLM know which specs need this)

**ADDED:**
- ✅ "When Writing User Stories" (guidance for spec generation)
- ✅ "Validation commands for user story checklists" (tells user stories what to validate, but doesn't do validation in ADR)

---

## Usage

When updating an ADR:
1. Read existing ADR fully
2. Update "Consequences" section (remove human-team language)
3. Add "LLM Implementation Constraints" section
4. Keep examples minimal (reference, not tutorial)
5. Remove any checklists (move to user story template if needed)
6. Focus on UNIVERSAL constraints (not spec-level details)
