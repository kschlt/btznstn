# Testing Guidelines for Claude Code

**Purpose:** Standards and patterns for writing maintainable, consistent tests in the Betzenstein Booking API.

**Target Audience:** Claude Code agents and AI developers

**Related Docs:**
- [ADR-008: Testing Strategy](../../docs/architecture/adr-008-testing-strategy.md) - Overall testing philosophy
- [ADR-009: Test Data Patterns](../../docs/architecture/adr-009-test-patterns.md) - Factory functions, fixtures, parametrization
- [Test Architecture Review](../../docs/architecture/test-architecture-review-2025-01.md) - Current state analysis

---

## 🤖 Instructions for AI Agents

**CRITICAL: Read this section BEFORE writing any test.**

### Step 1: Check Existing Utilities FIRST

**Before writing ANY helper function or creating test data, ALWAYS check:**

1. **`tests/utils.py`** - Common utilities (dates, assertions)
   ```python
   from tests.utils import get_today, assert_booking_response_structure
   ```

2. **`tests/fixtures/factories.py`** - Factory functions for models
   ```python
   from tests.fixtures.factories import make_booking, make_approval
   ```

3. **`conftest.py`** - Available fixtures
   ```python
   # Available fixtures (use as function parameters):
   # - db_session: AsyncSession
   # - client: AsyncClient
   # - booking_with_approvals: Booking (with 3 NoResponse approvals)
   # - confirmed_booking: Booking (with 3 Approved approvals)
   # - denied_booking: Booking (with 1 Denied approval)
   ```

**❌ NEVER duplicate code that already exists in these files.**

### Step 2: Apply DRY Principle (Don't Repeat Yourself)

**If you need to write the same code twice:**
1. ✅ Check if a utility/factory/fixture already exists
2. ✅ If not, create it in the appropriate file
3. ✅ Then use it in your tests

**❌ NEVER copy-paste code between tests.**

### Step 3: Follow the Pattern

**Every integration test should follow this structure:**

```python
from tests.utils import get_today  # ✅ Import utilities
from tests.fixtures.factories import make_booking  # ✅ Import factories

@pytest.mark.asyncio
async def test_feature_name(db_session: AsyncSession, client: AsyncClient):
    """Test BR-XXX: Description of what's being tested."""
    # Arrange: Use factories
    booking = make_booking(requester_first_name="Anna")
    db_session.add(booking)
    await db_session.commit()

    # Act: Call API
    response = await client.post("/api/v1/endpoint", json={...})

    # Assert: Check results
    assert response.status_code == 201
```

### Step 4: Decision Tree for Test Data

```
Need test data?
│
├─ API request JSON?
│  └─ ✅ Use request builder: booking_request(party_size=6)
│     ❌ DON'T: Manually write JSON dict with all fields
│
├─ Simple model instance (direct DB)?
│  └─ ✅ Use factory: make_booking(), make_approval()
│     ❌ DON'T: Booking(...) with all fields
│
├─ Complex scenario (booking + approvals + timeline)?
│  ├─ Test needs specific attributes? → Use factory
│  └─ Test doesn't care about attributes? → Use fixture
│     Fixtures: booking_with_approvals, confirmed_booking, denied_booking
│
├─ Current date/time?
│  └─ ✅ Use utility: get_today(), get_now()
│     ❌ DON'T: datetime.now(BERLIN_TZ).date()
│
├─ Validate response structure?
│  └─ ✅ Use assertion helper: assert_booking_response_structure()
│     ❌ DON'T: Manual field checks
│
└─ Need new utility/factory?
   └─ ✅ Add to tests/utils.py or tests/fixtures/factories.py FIRST
      └─ Then use it in your test
```

### Step 4a: When to Use Fixtures vs Factories vs Request Builders

**Use REQUEST BUILDERS (`booking_request()`) when:**
- ✅ Making API POST/PUT requests
- ✅ Need to test validation logic
- ✅ Don't need data in database beforehand
- ✅ Example: Testing party size validation, first name validation

```python
# ✅ GOOD: Request builder
response = await client.post(
    "/api/v1/bookings",
    json=booking_request(party_size=0),  # One line, override only what differs
)
assert response.status_code == 422

# ❌ BAD: Manual JSON
response = await client.post(
    "/api/v1/bookings",
    json={
        "requester_first_name": "Test",
        "requester_email": "test@example.com",
        "start_date": (today + timedelta(days=10)).isoformat(),
        "end_date": (today + timedelta(days=14)).isoformat(),
        "party_size": 0,  # 13 lines for 1 field difference!
        "affiliation": "Ingeborg",
    },
)
```

**Use FACTORIES (`make_booking()`) when:**
- ✅ Creating database objects directly (not via API)
- ✅ Setting up test data for GET requests
- ✅ Testing conflicts, past indicators, etc.
- ✅ Example: Creating existing booking to test conflict detection

```python
# ✅ GOOD: Factory for DB object
existing = make_booking(
    start_date=date(2025, 8, 1),
    end_date=date(2025, 8, 5),
)
db_session.add(existing)
await db_session.commit()

# Then test new booking conflicts with this one
```

**Use FIXTURES (`confirmed_booking`) when:**
- ✅ Test doesn't care about specific booking attributes
- ✅ Need pre-created complex scenarios (booking + approvals + timeline)
- ✅ Example: Testing that GET returns 200 for any confirmed booking

```python
# ✅ GOOD: Fixture (don't care about specific dates)
async def test_get_confirmed_returns_200(confirmed_booking, client):
    response = await client.get(f"/api/v1/bookings/{confirmed_booking.id}")
    assert response.status_code == 200

# ❌ DON'T use fixture if you need specific dates
async def test_is_past_yesterday(db_session, client):
    # This needs yesterday's date - use factory, not fixture
    booking = make_booking(end_date=get_today() - timedelta(days=1))
    # ...
```

### Step 5: Use Parametrized Tests for Validation

**When writing multiple tests that differ only in input values**, use `@pytest.mark.parametrize`:

**✅ GOOD: One parametrized test (6 cases)**
```python
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "party_size,expected_status,test_id",
    [
        (0, 422, "zero_rejected"),
        (1, 201, "one_accepted"),
        (10, 201, "ten_boundary_accepted"),
        (11, 422, "eleven_over_limit"),
        (-1, 422, "negative_rejected"),
        (3.5, 422, "float_rejected"),
    ],
)
async def test_party_size_validation(
    db_session: AsyncSession,
    client: AsyncClient,
    party_size: int | float,
    expected_status: int,
    test_id: str,
):
    """Test BR-017: Party size validation (1-10 accepted, others rejected)."""
    today = get_today()
    response = await client.post(
        "/api/v1/bookings",
        json=booking_request(
            start_date=today + timedelta(days=10),
            end_date=today + timedelta(days=12),
            party_size=party_size,
        ),
    )
    assert response.status_code == expected_status
```

**❌ BAD: 6 separate tests**
```python
@pytest.mark.asyncio
async def test_party_size_zero_fails(...):
    # 10 lines of setup
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_party_size_one_succeeds(...):
    # 10 lines of DUPLICATE setup
    assert response.status_code == 201
# ... 4 more nearly-identical tests
```

**When to parametrize:**
- ✅ Validation tests (boundaries, formats, types)
- ✅ Error message tests (different error scenarios)
- ✅ Permission tests (different roles)
- ✅ Tests where **only inputs/outputs differ, not logic**

**When NOT to parametrize:**
- ❌ Tests with different assertions (one checks error message, another checks response structure)
- ❌ Tests with different setup logic
- ❌ Tests where parametrization makes intent unclear

**Pro tip:** Group by expected outcome:
```python
@pytest.mark.parametrize(..., [
    ("Anna", "simple"),
    ("Marie-Claire", "hyphen"),
    # All valid names → 201
])
async def test_first_name_valid(...):
    assert response.status_code == 201

@pytest.mark.parametrize(..., [
    ("Anna 😊", "emoji"),
    ("A" * 41, "too_long"),
    # All invalid names → 422
])
async def test_first_name_invalid(...):
    assert response.status_code == 422
```

### Step 6: Checklist Before Writing Test

- [ ] Read existing tests in same file to understand pattern
- [ ] Check `tests/utils.py` for existing utilities (especially `booking_request()`)
- [ ] Check `tests/fixtures/factories.py` for existing factories
- [ ] Check `conftest.py` for available fixtures
- [ ] Use `booking_request()` for ALL API POST calls (never manual JSON dicts)
- [ ] Use factories instead of `Model(...)` constructors
- [ ] Use `get_today()` instead of `datetime.now()`
- [ ] **Consider parametrization** if writing multiple similar tests
- [ ] Reference business rule in docstring (`"""Test BR-XXX: ..."""`)

---

## Quick Reference

### ✅ DO

- Use factory functions for test data (`make_booking()`, `make_approval()`)
- Use fixtures for common scenarios (`booking_with_approvals`, `confirmed_booking`)
- Reference business rules in test docstrings (`"""Test BR-001: ..."""`)
- Parametrize similar tests with different inputs
- Use shared utilities from `tests/utils.py`
- Keep test functions focused (one assertion per business rule)
- Name tests descriptively (`test_conflict_exact_match`, not `test_booking_1`)

### ❌ DON'T

- Manually create model instances with all fields
- Duplicate helper functions across test files
- Create your own AsyncClient (use `client` fixture)
- Test multiple unrelated scenarios in one function
- Forget to commit test data to database
- Use production database URLs

---

## Test Structure

### File Organization

```
tests/
├── __init__.py
├── conftest.py                   # Global fixtures (db_session, client)
├── utils.py                      # Shared utilities (get_today, assertions)
├── fixtures/
│   └── factories.py              # Factory functions (make_booking, etc.)
├── unit/                         # Fast unit tests (no database)
│   ├── test_validation.py
│   └── test_business_rules.py
└── integration/                  # API + database tests
    ├── test_create_booking.py
    ├── test_get_booking.py
    └── test_approval_flow.py
```

### Test File Template

```python
"""
Integration tests for US-X.Y: [Feature Name].

Tests all business rules and edge cases per [spec file].

Test Plan:
- Happy Path (2 tests)
- BR-XXX: [Rule description] (N tests)
- BR-YYY: [Rule description] (M tests)
- Error Cases (K tests)
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils import get_today
from tests.fixtures.factories import make_booking


# ============================================================================
# Happy Path
# ============================================================================


@pytest.mark.asyncio
async def test_feature_success(db_session: AsyncSession, client: AsyncClient):
    """Test basic success scenario."""
    # Arrange
    # ... setup test data

    # Act
    response = await client.post("/api/v1/endpoint", json={...})

    # Assert
    assert response.status_code == 201


# ============================================================================
# BR-XXX: Business Rule Description
# ============================================================================


@pytest.mark.asyncio
async def test_business_rule_validation(db_session: AsyncSession, client: AsyncClient):
    """Test BR-XXX: [Specific scenario]."""
    # ... test implementation
```

---

## Core Patterns

### Pattern 1: Using Factory Functions

**❌ Bad:**
```python
async def test_something(db_session, client):
    booking = Booking(
        requester_first_name="Anna",
        requester_email="anna@example.com",
        start_date=date(2025, 8, 1),
        end_date=date(2025, 8, 5),
        total_days=5,
        party_size=4,
        affiliation=AffiliationEnum.INGEBORG,
        description="Test",
        status=StatusEnum.PENDING,
        created_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        updated_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
        last_activity_at=datetime.now(BERLIN_TZ).replace(tzinfo=None),
    )
    db_session.add(booking)
    await db_session.commit()
    # ... 15 lines of boilerplate
```

**✅ Good:**
```python
from tests.fixtures.factories import make_booking

async def test_something(db_session, client):
    booking = make_booking(requester_first_name="Anna")
    db_session.add(booking)
    await db_session.commit()
    # ... test logic
```

**Factory Signature:**
```python
def make_booking(
    *,
    requester_first_name: str = "Test User",
    requester_email: str = "test@example.com",
    start_date: date | None = None,  # Defaults to +10 days
    end_date: date | None = None,    # Defaults to +14 days
    party_size: int = 4,
    affiliation: AffiliationEnum = AffiliationEnum.INGEBORG,
    description: str | None = None,
    status: StatusEnum = StatusEnum.PENDING,
    **kwargs,
) -> Booking:
```

**Override defaults as needed:**
```python
# Future booking
booking = make_booking()

# Specific dates
booking = make_booking(
    start_date=date(2025, 12, 1),
    end_date=date(2025, 12, 5),
)

# Denied booking
booking = make_booking(
    status=StatusEnum.DENIED,
    requester_first_name="Denied User",
)
```

### Pattern 2: Using Fixtures for Complex Scenarios

**❌ Bad:**
```python
async def test_confirmed_booking(db_session, client):
    # Create booking
    booking = Booking(...)
    db_session.add(booking)
    await db_session.flush()

    # Create 3 approvals
    approval1 = Approval(booking_id=booking.id, party=AffiliationEnum.INGEBORG, ...)
    approval2 = Approval(booking_id=booking.id, party=AffiliationEnum.CORNELIA, ...)
    approval3 = Approval(booking_id=booking.id, party=AffiliationEnum.ANGELIKA, ...)
    db_session.add_all([approval1, approval2, approval3])

    # Create timeline events
    # ... 20 more lines

    await db_session.commit()
    # ... finally test
```

**✅ Good:**
```python
async def test_confirmed_booking(confirmed_booking, client):
    # Data already created by fixture
    response = await client.get(f"/api/v1/bookings/{confirmed_booking.id}")
    assert response.status_code == 200
```

**Available fixtures** (defined in `conftest.py`):
- `db_session` - Fresh database session with dependency override
- `client` - Async HTTP client (depends on db_session)
- `booking_with_approvals` - Booking + 3 NoResponse approvals
- `confirmed_booking` - Booking + 3 Approved approvals
- `denied_booking` - Booking + 1 Denied approval

### Pattern 3: Parametrized Tests

**Use for:** Multiple test cases with same structure, different inputs.

**❌ Bad:**
```python
async def test_party_size_zero():
    # ... test with party_size=0, expect 400

async def test_party_size_one():
    # ... test with party_size=1, expect 201

async def test_party_size_ten():
    # ... test with party_size=10, expect 201

async def test_party_size_eleven():
    # ... test with party_size=11, expect 400
```

**✅ Good:**
```python
@pytest.mark.parametrize(
    "party_size,expected_status,description",
    [
        (0, 400, "zero is below minimum"),
        (1, 201, "one is valid (minimum)"),
        (5, 201, "five is valid (middle)"),
        (10, 201, "ten is valid (maximum)"),
        (11, 400, "eleven exceeds maximum"),
        (-1, 400, "negative is invalid"),
    ],
)
async def test_party_size_validation(
    db_session: AsyncSession,
    client: AsyncClient,
    party_size: int,
    expected_status: int,
    description: str,
):
    """Test BR-017: Party size must be 1-10."""
    today = get_today()

    response = await client.post(
        "/api/v1/bookings",
        json={
            "requester_first_name": "Test",
            "requester_email": "test@example.com",
            "start_date": (today + timedelta(days=10)).isoformat(),
            "end_date": (today + timedelta(days=12)).isoformat(),
            "party_size": party_size,
            "affiliation": "Ingeborg",
        },
    )

    assert response.status_code == expected_status, description
```

**Benefits:**
- 6 tests in one function
- Easy to add new cases
- Clear test output shows which parameter failed

**When NOT to use:**
- ❌ Different assertion logic per case
- ❌ Different test setup per case
- ❌ Would make error messages unclear

### Pattern 4: Shared Utilities

**Import from `tests/utils.py`:**

```python
from tests.utils import (
    get_today,                          # Europe/Berlin date
    get_now,                            # Europe/Berlin datetime (naive)
    assert_booking_response_structure,  # Validates response fields
    assert_german_error,                # Validates German error message
)
```

**Example:**
```python
async def test_create_booking_success(db_session, client):
    today = get_today()  # ✅ Not datetime.now()

    response = await client.post("/api/v1/bookings", json={
        "start_date": (today + timedelta(days=10)).isoformat(),
        # ...
    })

    assert response.status_code == 201

    # ✅ Use helper instead of manual assertions
    assert_booking_response_structure(response.json())
```

### Pattern 5: Database Session Usage

**Always use fixtures, never create your own:**

**❌ Bad:**
```python
async def test_something():
    # DON'T create your own engine/session
    engine = create_async_engine("postgresql://...")
    async with async_session() as session:
        # ...
```

**✅ Good:**
```python
async def test_something(db_session: AsyncSession, client: AsyncClient):
    # Use provided fixtures
    booking = make_booking()
    db_session.add(booking)
    await db_session.commit()  # ✅ Commits to test DB

    response = await client.get(f"/api/v1/bookings/{booking.id}")
    # ✅ Client uses same session via dependency override
```

**Key points:**
- `db_session` fixture provides fresh database per test
- `client` fixture depends on `db_session` (ensures override is active)
- Never create `AsyncClient` manually
- Database automatically rolls back after each test

---

## Common Scenarios

### Scenario 1: Testing API Endpoint (POST)

```python
@pytest.mark.asyncio
async def test_create_booking_success(db_session: AsyncSession, client: AsyncClient):
    """Test basic booking creation."""
    from tests.utils import get_today

    today = get_today()

    response = await client.post(
        "/api/v1/bookings",
        json={
            "requester_first_name": "Anna",
            "requester_email": "anna@example.com",
            "start_date": (today + timedelta(days=10)).isoformat(),
            "end_date": (today + timedelta(days=14)).isoformat(),
            "party_size": 4,
            "affiliation": "Ingeborg",
        },
    )

    assert response.status_code == 201
    data = response.json()

    assert data["requester_first_name"] == "Anna"
    assert data["total_days"] == 5  # BR-001: inclusive
```

### Scenario 2: Testing API Endpoint (GET) with Pre-Created Data

```python
@pytest.mark.asyncio
async def test_get_booking(db_session: AsyncSession, client: AsyncClient):
    """Test GET booking by ID."""
    from tests.fixtures.factories import make_booking

    # Create test data
    booking = make_booking(requester_first_name="Max")
    db_session.add(booking)
    await db_session.commit()

    # Test GET endpoint
    response = await client.get(f"/api/v1/bookings/{booking.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["requester_first_name"] == "Max"
```

### Scenario 3: Testing with Token Authentication

```python
@pytest.mark.asyncio
async def test_authenticated_access(db_session: AsyncSession, client: AsyncClient):
    """Test GET with valid token."""
    from tests.fixtures.factories import make_booking
    from app.core.tokens import generate_token

    # Create booking
    booking = make_booking()
    db_session.add(booking)
    await db_session.commit()

    # Generate token
    token = generate_token({
        "email": booking.requester_email,
        "role": "requester",
        "booking_id": str(booking.id),
    })

    # Request with token
    response = await client.get(
        f"/api/v1/bookings/{booking.id}",
        params={"token": token},
    )

    assert response.status_code == 200
```

### Scenario 4: Testing Conflict Detection (BR-002)

```python
@pytest.mark.asyncio
async def test_conflict_detection(db_session: AsyncSession, client: AsyncClient):
    """Test BR-002: No overlaps with existing bookings."""
    from tests.fixtures.factories import make_booking
    from tests.utils import get_today

    today = get_today()

    # Create first booking
    existing = make_booking(
        start_date=today + timedelta(days=10),
        end_date=today + timedelta(days=14),
    )
    db_session.add(existing)
    await db_session.commit()

    # Try to create conflicting booking
    response = await client.post(
        "/api/v1/bookings",
        json={
            "requester_first_name": "Conflict",
            "requester_email": "conflict@example.com",
            "start_date": (today + timedelta(days=12)).isoformat(),  # Overlaps
            "end_date": (today + timedelta(days=16)).isoformat(),
            "party_size": 2,
            "affiliation": "Cornelia",
        },
    )

    assert response.status_code == 409  # Conflict
    assert "überschneidet" in response.json()["detail"]
```

### Scenario 5: Testing German Error Messages

```python
@pytest.mark.asyncio
async def test_german_404_message(db_session: AsyncSession, client: AsyncClient):
    """Test BR-011: German error messages."""
    from tests.utils import assert_german_error
    from uuid import uuid4

    # Request non-existent booking
    response = await client.get(f"/api/v1/bookings/{uuid4()}")

    assert response.status_code == 404

    # Validate German error message
    assert_german_error(
        response.json(),
        expected_phrase="konnte leider nicht gefunden werden",
    )
```

### Scenario 6: Testing with Approvals and Timeline

```python
@pytest.mark.asyncio
async def test_self_approval(db_session: AsyncSession, client: AsyncClient):
    """Test BR-015: Self-approval if requester is approver."""
    from tests.utils import get_today
    from sqlalchemy import select
    from app.models.approval import Approval
    from app.models.enums import DecisionEnum

    today = get_today()

    # Requester is Ingeborg (one of the approvers)
    response = await client.post(
        "/api/v1/bookings",
        json={
            "requester_first_name": "Ingeborg",
            "requester_email": "ingeborg@example.com",
            "start_date": (today + timedelta(days=10)).isoformat(),
            "end_date": (today + timedelta(days=14)).isoformat(),
            "party_size": 4,
            "affiliation": "Ingeborg",
        },
    )

    assert response.status_code == 201
    booking_id = response.json()["id"]

    # Check approvals in database
    result = await db_session.execute(
        select(Approval).where(Approval.booking_id == booking_id)
    )
    approvals = result.scalars().all()

    # Should have 3 approvals
    assert len(approvals) == 3

    # Ingeborg's approval should be APPROVED (self-approval)
    ingeborg_approval = next(
        a for a in approvals if a.party.value == "Ingeborg"
    )
    assert ingeborg_approval.decision == DecisionEnum.APPROVED
    assert ingeborg_approval.decided_at is not None

    # Others should be NO_RESPONSE
    other_approvals = [a for a in approvals if a.party.value != "Ingeborg"]
    for approval in other_approvals:
        assert approval.decision == DecisionEnum.NO_RESPONSE
        assert approval.decided_at is None
```

---

## Anti-Patterns

### ❌ Anti-Pattern 1: Creating Your Own Client

**Problem:**
```python
async def test_something(db_session):
    # ❌ DON'T: Creates client without dependency override
    async with AsyncClient(transport=ASGITransport(app=app)) as client:
        response = await client.post(...)
```

**Why it's bad:**
- Client doesn't use `db_session` fixture
- Dependency override not active
- Test data won't be visible to API

**Fix:**
```python
async def test_something(db_session, client):
    # ✅ Use fixture
    response = await client.post(...)
```

### ❌ Anti-Pattern 2: Forgetting to Commit

**Problem:**
```python
async def test_something(db_session, client):
    booking = make_booking()
    db_session.add(booking)
    # ❌ Forgot to commit!

    response = await client.get(f"/api/v1/bookings/{booking.id}")
    # Returns 404 because booking not committed
```

**Fix:**
```python
async def test_something(db_session, client):
    booking = make_booking()
    db_session.add(booking)
    await db_session.commit()  # ✅ Commit before API call

    response = await client.get(f"/api/v1/bookings/{booking.id}")
```

### ❌ Anti-Pattern 3: Testing Multiple Things in One Test

**Problem:**
```python
async def test_booking_lifecycle(db_session, client):
    # Create booking
    response1 = await client.post(...)
    assert response1.status_code == 201

    # Get booking
    response2 = await client.get(...)
    assert response2.status_code == 200

    # Update booking
    response3 = await client.put(...)
    assert response3.status_code == 200

    # Delete booking
    response4 = await client.delete(...)
    assert response4.status_code == 204
```

**Why it's bad:**
- If create fails, you don't know if get/update/delete work
- Hard to debug failures
- Violates single responsibility

**Fix:**
```python
async def test_create_booking(db_session, client):
    response = await client.post(...)
    assert response.status_code == 201

async def test_get_booking(db_session, client):
    # Use fixture for pre-created booking
    response = await client.get(...)
    assert response.status_code == 200

# Separate test for each operation
```

### ❌ Anti-Pattern 4: Hardcoded Dates

**Problem:**
```python
async def test_future_booking(db_session, client):
    response = await client.post(
        "/api/v1/bookings",
        json={
            "start_date": "2025-08-01",  # ❌ Hardcoded, will become past date
            # ...
        }
    )
```

**Why it's bad:**
- Test will fail after 2025-08-01
- Violates BR-014 (no past dates)

**Fix:**
```python
from tests.utils import get_today

async def test_future_booking(db_session, client):
    today = get_today()

    response = await client.post(
        "/api/v1/bookings",
        json={
            "start_date": (today + timedelta(days=30)).isoformat(),  # ✅ Relative
            # ...
        }
    )
```

### ❌ Anti-Pattern 5: Not Using Parametrize for Similar Tests

**Problem:**
```python
async def test_party_size_1(): ...
async def test_party_size_2(): ...
async def test_party_size_3(): ...
# ... 10 nearly identical functions
```

**Fix:**
```python
@pytest.mark.parametrize("party_size", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
async def test_party_size_valid(db_session, client, party_size):
    # One test, 10 cases
```

---

## Checklist for New Tests

Before submitting a PR with new tests, verify:

- [ ] Test references business rule in docstring (`"""Test BR-XXX: ..."""`)
- [ ] Uses factory functions (`make_booking()`, not `Booking(...)`)
- [ ] Uses fixtures (`db_session`, `client`, not custom instances)
- [ ] Uses shared utilities (`get_today()`, not `datetime.now()`)
- [ ] Relative dates, not hardcoded (`today + timedelta(days=10)`)
- [ ] Commits test data before API calls (`await db_session.commit()`)
- [ ] Tests one thing (not multiple operations in one test)
- [ ] Descriptive test name (`test_conflict_exact_match`, not `test_1`)
- [ ] Parametrized if 3+ similar tests (`@pytest.mark.parametrize`)
- [ ] German error message validated if testing errors

---

## Running Tests

### All Tests
```bash
pytest
```

### Specific File
```bash
pytest tests/integration/test_create_booking.py
```

### Specific Test
```bash
pytest tests/integration/test_create_booking.py::test_create_booking_success
```

### With Coverage
```bash
pytest --cov=app --cov-report=html
```

### Fast Tests Only (Unit)
```bash
pytest tests/unit/
```

### Slow Tests Only (Integration)
```bash
pytest tests/integration/
```

### Show Output
```bash
pytest -v -s
```

### Show Slowest Tests
```bash
pytest --durations=10
```

---

## Summary

**Remember:**
1. ✅ **Use factories** for test data (less boilerplate)
2. ✅ **Use fixtures** for complex scenarios (reusability)
3. ✅ **Parametrize** similar tests (DRY)
4. ✅ **Reference business rules** (traceability)
5. ✅ **Use relative dates** (avoid future failures)

**When in doubt:**
- Check existing tests in `tests/integration/`
- Read [Test Architecture Review](../../docs/architecture/test-architecture-review-2025-01.md)
- Ask for review before implementing 10+ similar tests

---

**Happy testing! 🧪**
