# ADR-009: Test Data Patterns

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

**Also use:**
- **Fixtures** for complex scenarios (booking + approvals)
- **Request builders** for API JSON payloads
- **Utility functions** for dates (`get_today()`, `get_now()`)

---

## Rationale

### Why Factory Functions vs Fixtures vs Raw Constructors?

**Factory Functions (Chosen for models):**
- ✅ Flexible (override any field)
- ✅ Sensible defaults (less boilerplate)
- ✅ Explicit (you see what's being created)
- ✅ DRY (centralizes default logic)

**Fixtures (Use for complex scenarios):**
- ✅ Good for "booking with 3 approvals"
- ❌ Too rigid for simple cases
- ❌ Harder to customize

**Raw Constructors (Rejected):**
- ❌ Repetitive (must pass all fields every time)
- ❌ Brittle (breaks when model changes)

---

### Why Not Fixtures for Everything?

**Fixtures (pytest built-in):**
- ✅ Great for dependencies (db_session, client)
- ✅ Good for complex scenarios
- ❌ **Hard to parametrize** (can't easily override fields)
- ❌ **Hidden** (test doesn't show what data is used)

**Factory functions:**
- ✅ **Explicit** - test shows exactly what's created
- ✅ **Flexible** - easy to override any field
- ✅ **Simple** - just a Python function

---

## Consequences

### Positive

✅ **Reduced boilerplate** - 15 lines → 1 line per test
✅ **DRY** - Default logic in one place
✅ **Readable** - Tests show intent, not setup
✅ **Maintainable** - Model changes update factory, not 70+ tests

### Negative

⚠️ **Pattern choice** - Must use factories for test data creation (not manual `Booking(...)` instantiation)
⚠️ **Indirection** - Defaults hidden in factory file (check `tests/fixtures/factories.py` for values)

### Neutral

➡️ **Hybrid approach** - Use both factories and fixtures where appropriate

---

## Implementation Pattern

### Factory Function

```python
# tests/fixtures/factories.py
from datetime import timedelta
from app.models import Booking, Approval
from app.models.enums import StatusEnum, AffiliationEnum
from tests.utils import get_today

def make_booking(**overrides):
    """Create Booking with defaults."""
    today = get_today()
    defaults = {
        "requester_first_name": "Test",
        "requester_email": "test@example.com",
        "start_date": today,
        "end_date": today + timedelta(days=2),
        "party_size": 4,
        "affiliation": AffiliationEnum.INGEBORG,
        "status": StatusEnum.PENDING,
        "total_days": 3,
    }
    return Booking(**(defaults | overrides))

def make_approval(**overrides):
    """Create Approval with defaults."""
    defaults = {
        "party": AffiliationEnum.INGEBORG,
        "decision": DecisionEnum.NO_RESPONSE,
    }
    return Approval(**(defaults | overrides))
```

### Usage in Tests

```python
@pytest.mark.asyncio
async def test_create_booking_max_party_size(client, db_session):
    """Test BR-017: Party size max validation."""
    # Factory - one line, explicit override
    booking = make_booking(party_size=10)
    db_session.add(booking)
    await db_session.commit()

    # Test focuses on what matters
    assert booking.party_size == 10
```

### Fixture for Complex Scenarios

```python
# conftest.py
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

---

## Decision Tree for Test Data

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

---

## References

**Related ADRs:**
- ADR-008: Testing Strategy (Pytest foundation)

**Implementation:**
- [`api/tests/CLAUDE.md`](../../api/tests/CLAUDE.md) - Detailed patterns
- [`api/tests/fixtures/factories.py`](../../api/tests/fixtures/factories.py) - Factory functions
- [`api/tests/utils.py`](../../api/tests/utils.py) - Utilities

**Rationale:**
- [Test Architecture Review](test-architecture-review-2025-01.md) - Full analysis
