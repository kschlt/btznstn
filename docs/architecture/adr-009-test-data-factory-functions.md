# ADR-009: Test Data Factory Functions

**Status:** Accepted
**Date:** 2025-01-18
**Deciders:** Solution Architect
**Context:** After US-2.1/2.2 - 74 tests showed duplication patterns

---

## Context

After implementing first user stories (74 integration tests), observed issues:
- Duplication: Manual `Booking()` creation repeated in 17+ tests
- Boilerplate: 10-15 lines setup per test
- Inconsistency: Helper functions duplicated across files

**Need patterns for:**
- Reduce duplication (DRY)
- Improve readability (focus on test, not setup)
- Scale effectively (100+ tests coming)
- Maintain test isolation

---

## Decision

Use **Factory Functions** for test data creation.

**Pattern:**
```python
# tests/fixtures/factories.py
def make_booking(**kwargs):
    """Create booking with sensible defaults, override via kwargs."""
    defaults = {
        "requester_email": "test@example.com",
        "start_date": get_today(),
        "end_date": get_today() + timedelta(days=2),
        "party_size": 4,
        # ... all required fields
    }
    return Booking(**(defaults | kwargs))
```

**Usage:**
```python
# Test uses factory
booking = make_booking(party_size=10)  # Override one field
db_session.add(booking)
```

**Note:** Use fixtures for complex scenarios (booking + approvals), not for simple single-model cases.

---

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Test Data Creation | Factory functions (`make_booking()`, `make_approval()`) | Manual `Booking(...)` instantiation |
| Complex Scenarios | Pytest fixtures | Factory functions for complex multi-model scenarios |
| Date/Time Utilities | `get_today()`, `get_now()` from `tests/utils.py` | `datetime.now()` or hardcoded dates |

---

## Rationale

**Why Factory Functions:**
- Factory functions provide flexible overrides → **Constraint:** MUST use factory functions (`make_booking()`, `make_approval()`) for test data creation
- Factory functions centralize default logic → **Constraint:** MUST define factories in `tests/fixtures/factories.py`
- Factory functions are explicit and readable → **Constraint:** MUST use factory functions instead of manual model instantiation

**Why NOT Raw Constructors:**
- Raw constructors require passing all fields → **Violation:** Manual `Booking(...)` instantiation violates DRY principle, creates boilerplate, breaks when models change

**Why NOT Fixtures for Simple Cases:**
- Fixtures are hard to parametrize and hide data → **Violation:** Using fixtures for simple single-model cases violates explicit test data requirement. Fixtures are appropriate for complex scenarios only.

## Consequences

### MUST (Required)

- MUST use factory functions (`make_booking()`, `make_approval()`) for test data creation - Factory functions provide flexible overrides and centralize default logic
- MUST define factories in `tests/fixtures/factories.py` - Centralizes default logic for maintainability
- MUST use fixtures for complex scenarios (booking + approvals + timeline) - Fixtures are appropriate for multi-model scenarios
- MUST use `get_today()` and `get_now()` from `tests/utils.py` for date/time - Ensures consistent timezone handling (ADR-010)

### MUST NOT (Forbidden)

- MUST NOT use manual `Booking(...)` instantiation - Violates DRY principle, creates boilerplate, breaks when models change
- MUST NOT use fixtures for simple single-model cases - Fixtures hide data and are hard to parametrize
- MUST NOT use `datetime.now()` or hardcoded dates - Violates timezone consistency (ADR-010)

### Trade-offs

- Defaults are hidden in factory file - MUST check `tests/fixtures/factories.py` for default values. MUST NOT assume defaults without checking factory definition.

### Code Examples

```python
# ❌ WRONG: Manual instantiation
booking = Booking(
    requester_first_name="Test",
    requester_email="test@example.com",
    start_date=get_today(),
    end_date=get_today() + timedelta(days=2),
    party_size=4,
    affiliation=AffiliationEnum.INGEBORG,
    status=StatusEnum.PENDING,
    total_days=3,
)

# ✅ CORRECT: Factory function
booking = make_booking(party_size=10)  # Override one field
```

```python
# ❌ WRONG: Fixture for simple case
@pytest.fixture
def simple_booking():
    return Booking(...)  # Too rigid, hides data

# ✅ CORRECT: Factory function for simple case
booking = make_booking(party_size=10)  # Explicit, flexible

# ✅ CORRECT: Fixture for complex scenario
@pytest.fixture
async def booking_with_approvals(db_session):
    """Booking with 3 NoResponse approvals."""
    booking = make_booking()
    booking.approvals = [
        make_approval(party=AffiliationEnum.INGEBORG),
        make_approval(party=AffiliationEnum.CORNELIA),
        make_approval(party=AffiliationEnum.ANGELIKA),
    ]
    db_session.add(booking)
    await db_session.commit()
    return booking
```

### Decision Tree for Test Data

```
Need test data?
│
├─ API request JSON?
│  └─ Use request builder
│
├─ Simple model with 1-2 custom fields?
│  └─ Use factory function
│
├─ Complex scenario (booking + approvals + timeline)?
│  └─ Use fixture
│
├─ Current date/time?
│  └─ Use utility (get_today(), get_now())
```

### Applies To

- ALL test files in `api/tests/`
- File patterns: `api/tests/**/*.py`

### Validation Commands

- `grep -r "Booking(" api/tests/` (should be empty - must use factories)
- `grep -r "datetime.now()" api/tests/` (should be empty - must use `get_today()` or `get_now()`)

---

**Related ADRs:**
- [ADR-008](adr-008-testing-strategy-SUPERSEDED.md) - Testing Strategy (Superseded by ADR-020, ADR-021)
- [ADR-010](adr-010-datetime-timezone.md) - DateTime Timezone (date/time utilities)

---

## References

**Related ADRs:**
- [ADR-008](adr-008-testing-strategy-SUPERSEDED.md) - Testing Strategy (Superseded by ADR-020, ADR-021)
- [ADR-010](adr-010-datetime-timezone.md) - DateTime Timezone

**Implementation:**
- `api/tests/fixtures/factories.py` - Factory functions
- `api/tests/utils.py` - Date/time utilities
