# ADR-009: Test Data Patterns and Organization

**Status:** Accepted
**Date:** 2025-01-18
**Deciders:** Solution Architect
**Context:** After implementing US-2.1 and US-2.2 (74 tests, 2,403 lines)
**Supersedes:** Partially extends [ADR-008: Testing Strategy](adr-008-testing-strategy.md)

---

## Context

After implementing the first two user stories (US-2.1: Create Booking, US-2.2: Get Booking), we have 74 passing integration tests with 76.57% code coverage. The test infrastructure from ADR-008 is working well, but we've identified patterns that will help us scale testing for the remaining 6+ user stories.

### Current State (January 2025)

**Test Metrics:**
- 74 integration tests (all passing)
- 2,403 lines of test code
- 76.57% code coverage
- ~8 seconds execution time

**Observed Issues:**
1. **Duplication**: Manual `Booking()` instance creation repeated in 17+ tests
2. **Boilerplate**: 10-15 lines of setup code per test for creating related data
3. **Inconsistency**: Helper functions (`get_today()`) duplicated across files
4. **Parametrization opportunity**: 6 similar tests could be 1 parametrized test
5. **Performance**: Drop/create tables on every test (74 × ~100ms = 7+ seconds overhead)

**What's Working:**
- ✅ Test-first approach caught real bugs (is_past field, token parsing)
- ✅ Business rule traceability (every test references BR-XXX)
- ✅ Proper test isolation via fixtures
- ✅ Clear test organization by business rule

### Problem Statement

We need patterns that:
1. **Reduce duplication** - Don't repeat booking creation logic
2. **Improve readability** - Focus on what's being tested, not setup
3. **Scale effectively** - 6+ more user stories will add 100+ tests
4. **Maintain consistency** - New contributors should follow same patterns
5. **Preserve test isolation** - Each test must remain independent

See [Test Architecture Review](test-architecture-review-2025-01.md) for detailed analysis.

---

## Decision

We will adopt the following patterns for API test data management:

### 1. Factory Functions (Test Data Builders)

**Location:** `tests/fixtures/factories.py`

**Pattern:**
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
    """Create a Booking instance with sensible defaults."""
    # Implementation provides smart defaults
    # All fields can be overridden
```

**Usage:**
```python
# Default booking (10-14 days from now, 4 people, Pending)
booking = make_booking()

# Override specific fields
booking = make_booking(
    requester_first_name="Anna",
    party_size=6,
)
```

**Benefit:** 80% less code compared to manual `Booking(...)` creation.

### 2. Shared Test Utilities

**Location:** `tests/utils.py`

**Utilities:**
- `get_today() -> date` - Europe/Berlin timezone
- `get_now() -> datetime` - Europe/Berlin datetime (naive)
- `assert_booking_response_structure(data)` - Validates response fields
- `assert_german_error(data, phrase)` - Validates German error messages

**Benefit:** Single source of truth for common operations.

### 3. Scenario Fixtures

**Location:** `conftest.py`

**Pattern:**
```python
@pytest_asyncio.fixture
async def booking_with_approvals(db_session: AsyncSession) -> Booking:
    """Create a booking with 3 NoResponse approvals."""
    booking = make_booking()
    db_session.add(booking)
    await db_session.flush()

    # Create 3 approvals
    approvals = [
        make_approval(booking_id=booking.id, party=party)
        for party in [INGEBORG, CORNELIA, ANGELIKA]
    ]
    db_session.add_all(approvals)
    await db_session.commit()

    return booking
```

**Usage:**
```python
async def test_something(booking_with_approvals, client):
    # Booking + approvals already created
    response = await client.get(f"/api/v1/bookings/{booking_with_approvals.id}")
```

**Benefit:** Complex scenarios reusable across tests.

### 4. Parametrized Tests

**Pattern:**
```python
@pytest.mark.parametrize(
    "party_size,expected_status,description",
    [
        (0, 400, "zero is invalid"),
        (1, 201, "one is valid (minimum)"),
        (10, 201, "ten is valid (maximum)"),
        (11, 400, "eleven exceeds maximum"),
    ],
)
async def test_party_size_validation(party_size, expected_status, description):
    # Single test function, multiple scenarios
```

**When to use:**
- Multiple test cases with same structure, different inputs
- Boundary testing (min, max, invalid values)
- Validation rules

**When NOT to use:**
- Different assertion logic per case
- Different test setup required
- Would make error messages unclear

### 5. Documentation Standard

**Location:** `tests/CLAUDE.md`

**Content:**
- DO/DON'T quick reference
- Pattern examples with good/bad comparisons
- Common scenarios (POST, GET, conflicts, errors)
- Anti-patterns to avoid
- Checklist for new tests

**Benefit:** Ensures consistency across all future tests.

---

## Rationale

### Why Factory Functions?

**Alternative considered:** Builder pattern
```python
booking = BookingBuilder()
    .with_requester("Anna")
    .with_dates(start, end)
    .with_status(CONFIRMED)
    .build()
```

**Rejected because:**
- ❌ More complex (requires Builder class)
- ❌ More verbose for simple cases
- ❌ Less familiar to Python developers

**Factory function wins:**
- ✅ Simple keyword arguments
- ✅ Pythonic (similar to dataclass defaults)
- ✅ Easy to override any field
- ✅ AI-friendly (Claude knows this pattern well)

### Why Shared Fixtures for Scenarios?

**Alternative considered:** Helper functions that return data
```python
async def create_confirmed_booking(db_session):
    # ... create and return booking
```

**Rejected because:**
- ❌ Must manually call in every test
- ❌ No pytest fixture benefits (caching, dependency injection)
- ❌ Harder to compose

**Fixtures win:**
- ✅ Declarative (test parameters show dependencies)
- ✅ Pytest manages lifecycle
- ✅ Can depend on other fixtures
- ✅ Standard pytest pattern

### Why Parametrize?

**Evidence from current tests:**

`test_create_booking.py` has 6 party size tests:
```python
async def test_party_size_zero_fails(): ...       # 20 lines
async def test_party_size_one_succeeds(): ...     # 20 lines
async def test_party_size_ten_succeeds(): ...     # 20 lines
async def test_party_size_eleven_fails(): ...     # 20 lines
async def test_party_size_negative_fails(): ...   # 20 lines
async def test_party_size_non_integer_fails(): ...# 20 lines
```

**Total:** 120 lines with 90% duplication

**With parametrize:**
```python
@pytest.mark.parametrize("party_size,expected", [
    (0, 400), (1, 201), (10, 201), (11, 400), (-1, 400)
])
async def test_party_size_validation(party_size, expected): ...
```

**Total:** 20 lines (83% reduction)

**Benefits:**
- ✅ Easier to add new test cases (just add tuple)
- ✅ Clear which parameter failed in test output
- ✅ Less maintenance (logic in one place)

---

## Consequences

### Positive

✅ **Less code to maintain**
- 50% reduction in test code (2,403 → ~1,200 lines estimated)
- 70% less boilerplate per test

✅ **Easier to write tests**
- Copy existing pattern
- Override only what's different
- Clear examples in `tests/CLAUDE.md`

✅ **More consistent**
- All tests use same factories
- All dates use `get_today()`
- All error assertions use helpers

✅ **Faster execution** (when transaction rollback pattern added)
- Session-scoped table creation: 8s → ~2s (4x faster)

✅ **Better for AI**
- Factories are simple functions (Claude knows them)
- Clear patterns to follow
- Documented in CLAUDE.md

### Negative

⚠️ **Initial refactoring effort**
- ~6 hours to refactor existing 74 tests
- Must update tests incrementally

⚠️ **Learning curve**
- New contributors must read `tests/CLAUDE.md`
- Must understand factory pattern

⚠️ **Abstraction risk**
- Too much abstraction can hide what's being tested
- Must balance convenience vs. clarity

### Mitigation

**For refactoring effort:**
- Refactor incrementally (Priority 1 → 2 → 3)
- Start with new tests (US-2.3+) using new patterns
- Refactor old tests in next sprint

**For learning curve:**
- Document patterns in `tests/CLAUDE.md`
- Include good/bad examples
- Review checklist for new tests

**For abstraction risk:**
- Factories are simple (just keyword args)
- Avoid complex builders
- Keep test logic visible

---

## Implementation Plan

### Priority 1: Immediate (Before US-2.3)

**Estimated time:** 2.5 hours

1. **Create `tests/utils.py`** (30 min)
   ```python
   def get_today() -> date: ...
   def get_now() -> datetime: ...
   def assert_booking_response_structure(data): ...
   def assert_german_error(data, phrase): ...
   ```

2. **Create `tests/fixtures/factories.py`** (1 hour)
   ```python
   def make_booking(**kwargs) -> Booking: ...
   def make_approval(**kwargs) -> Approval: ...
   def make_timeline_event(**kwargs) -> TimelineEvent: ...
   ```

3. **Create `tests/CLAUDE.md`** (1 hour) ✅ DONE
   - Patterns with examples
   - Anti-patterns
   - Checklist

### Priority 2: Next Sprint

**Estimated time:** 7 hours

4. **Add scenario fixtures to `conftest.py`** (2 hours)
   ```python
   @pytest_asyncio.fixture
   async def booking_with_approvals(): ...

   @pytest_asyncio.fixture
   async def confirmed_booking(): ...

   @pytest_asyncio.fixture
   async def denied_booking(): ...
   ```

5. **Refactor `test_get_booking.py`** (2 hours)
   - 17 tests currently
   - Use `make_booking()` instead of manual creation
   - Use assertion helpers

6. **Refactor `test_create_booking.py`** (3 hours)
   - 57 tests currently
   - Parametrize party size tests (6 → 1)
   - Parametrize first name tests (11 → 2-3)
   - Use factories

### Priority 3: Future Optimization

**Estimated time:** 4 hours

7. **Transaction rollback pattern** (2 hours)
   - Session-scoped engine
   - Function-scoped transaction
   - Benchmark improvement

8. **Split large test files** (2 hours)
   - `test_create_booking.py` → 3 files
   - By feature area (validation, conflicts, approvals)

---

## Validation Criteria

**Success metrics after Priority 1+2:**

- [ ] New tests (US-2.3+) use factories (not manual `Booking()`)
- [ ] All tests use `get_today()` from utils (no duplication)
- [ ] Similar tests parametrized (party size: 6 → 1)
- [ ] Test code reduced by ~40% (2,403 → ~1,400 lines)
- [ ] PR reviews reference `tests/CLAUDE.md` checklist
- [ ] No new tests create `AsyncClient` manually

**Quality metrics:**
- [ ] 100% tests still passing
- [ ] Coverage maintained at ≥76%
- [ ] Test execution time ≤8 seconds (same or better)

---

## Related Documents

- [ADR-008: Testing Strategy](adr-008-testing-strategy.md) - Overall strategy (Pytest, Playwright)
- [Test Architecture Review](test-architecture-review-2025-01.md) - Detailed analysis
- [Testing Guidelines](../../api/tests/CLAUDE.md) - Practical patterns for developers

---

## Examples

### Example 1: Before/After Factory

**Before (20 lines):**
```python
booking = Booking(
    requester_first_name="Anna",
    requester_email="anna@example.com",
    start_date=today + timedelta(days=10),
    end_date=today + timedelta(days=14),
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
await db_session.refresh(booking)
```

**After (3 lines):**
```python
booking = make_booking(requester_first_name="Anna")
db_session.add(booking)
await db_session.commit()
```

### Example 2: Before/After Fixture

**Before (35 lines):**
```python
async def test_confirmed_booking(db_session, client):
    # Create booking
    booking = Booking(...)
    db_session.add(booking)
    await db_session.flush()

    # Create 3 approvals
    approval1 = Approval(booking_id=booking.id, ...)
    approval2 = Approval(booking_id=booking.id, ...)
    approval3 = Approval(booking_id=booking.id, ...)
    db_session.add_all([approval1, approval2, approval3])

    # Create timeline
    timeline = TimelineEvent(booking_id=booking.id, ...)
    db_session.add(timeline)

    await db_session.commit()

    # Finally, test
    response = await client.get(f"/api/v1/bookings/{booking.id}")
    assert response.status_code == 200
```

**After (5 lines):**
```python
async def test_confirmed_booking(confirmed_booking, client):
    # Test immediately
    response = await client.get(f"/api/v1/bookings/{confirmed_booking.id}")
    assert response.status_code == 200
```

### Example 3: Before/After Parametrize

**Before (120 lines, 6 functions):**
```python
async def test_party_size_zero_fails(db_session, client):
    today = get_today()
    response = await client.post("/api/v1/bookings", json={
        "requester_first_name": "Test",
        "requester_email": "test@example.com",
        "start_date": (today + timedelta(days=10)).isoformat(),
        "end_date": (today + timedelta(days=12)).isoformat(),
        "party_size": 0,
        "affiliation": "Ingeborg",
    })
    assert response.status_code == 400

async def test_party_size_one_succeeds(db_session, client):
    # ... same as above but party_size=1, expect 201

# ... 4 more similar functions
```

**After (30 lines, 1 function):**
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
    db_session, client, party_size, expected_status, description
):
    """Test BR-017: Party size must be 1-10."""
    today = get_today()

    response = await client.post("/api/v1/bookings", json={
        "requester_first_name": "Test",
        "requester_email": "test@example.com",
        "start_date": (today + timedelta(days=10)).isoformat(),
        "end_date": (today + timedelta(days=12)).isoformat(),
        "party_size": party_size,
        "affiliation": "Ingeborg",
    })

    assert response.status_code == expected_status, description
```

---

## Changelog

- **2025-01-18:** Initial decision - Factory functions, scenario fixtures, parametrized tests, and documentation patterns adopted for scalable test data management

---

## Notes

This ADR **extends** (not replaces) ADR-008. ADR-008 defines the overall strategy (Pytest, Playwright, coverage targets). This ADR defines specific patterns for test data management within that strategy.

The patterns in this ADR are based on real experience from implementing US-2.1 and US-2.2, not theoretical best practices. All recommendations have concrete examples from actual tests.
