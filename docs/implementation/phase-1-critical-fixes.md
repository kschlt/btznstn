# Phase 1: Critical Issues Fixed (9 Issues)

## Purpose

This document captures the 9 critical/major issues found during Phase 1 code review and how they were fixed. These learnings **must** be incorporated into the Phase 1 documentation to prevent them from happening again.

---

## Issue #1: Booking Model - Missing String Constraints (CRITICAL)

**Problem:** Schema drift between migration and model

**Migration had:**
```sql
sa.Column("requester_first_name", sa.String(length=40), nullable=False),
sa.Column("requester_email", sa.String(length=254), nullable=False),
sa.Column("description", sa.String(length=500), nullable=True),
```

**Model had (WRONG):**
```python
requester_first_name: Mapped[str] = mapped_column(nullable=False)
requester_email: Mapped[str] = mapped_column(nullable=False)
description: Mapped[str | None] = mapped_column(nullable=True)
```

**Fixed to:**
```python
requester_first_name: Mapped[str] = mapped_column(String(40), nullable=False)
requester_email: Mapped[str] = mapped_column(String(254), nullable=False)
description: Mapped[str | None] = mapped_column(String(500), nullable=True)
```

**Why Critical:** Schema drift causes production issues when length constraints are enforced in DB but not in ORM.

**Test Required:**
```python
def test_booking_model_string_constraints():
    """Verify Booking model has correct String length constraints."""
    assert str(Booking.requester_first_name.type) == "VARCHAR(40)"
    assert str(Booking.requester_email.type) == "VARCHAR(254)"
    assert str(Booking.description.type) == "VARCHAR(500)"
```

---

## Issue #2: Approval Model - Missing String Constraint (CRITICAL)

**Problem:** Comment field had no length constraint

**Migration had:**
```sql
sa.Column("comment", sa.String(length=500), nullable=True),
```

**Model had (WRONG):**
```python
comment: Mapped[str | None] = mapped_column(nullable=True)
```

**Fixed to:**
```python
comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
```

**Test Required:**
```python
def test_approval_model_string_constraints():
    """Verify Approval model has correct String length constraints."""
    assert str(Approval.comment.type) == "VARCHAR(500)"
```

---

## Issue #3: TimelineEvent Model - Missing String Constraints (CRITICAL)

**Problem:** Multiple fields missing constraints

**Migration had:**
```sql
sa.Column("actor", sa.String(length=50), nullable=False),
sa.Column("event_type", sa.String(length=50), nullable=False),
sa.Column("note", sa.Text(), nullable=True),
```

**Model had (WRONG):**
```python
actor: Mapped[str] = mapped_column(nullable=False)
event_type: Mapped[str] = mapped_column(nullable=False)
note: Mapped[str | None] = mapped_column(nullable=True)
```

**Fixed to:**
```python
actor: Mapped[str] = mapped_column(String(50), nullable=False)
event_type: Mapped[str] = mapped_column(String(50), nullable=False)
note: Mapped[str | None] = mapped_column(Text(), nullable=True)  # Unlimited
```

**Test Required:**
```python
def test_timeline_model_string_constraints():
    """Verify TimelineEvent model has correct String length constraints."""
    assert str(TimelineEvent.actor.type) == "VARCHAR(50)"
    assert str(TimelineEvent.event_type.type) == "VARCHAR(50)"
    assert isinstance(TimelineEvent.note.type, Text)
```

---

## Issue #4: Calendar Filtering - Multi-Month Overlap Bug (CRITICAL)

**Problem:** Only showed bookings STARTING in month, not all overlapping bookings

**WRONG Implementation:**
```python
async def list_for_calendar(self, month: int, year: int) -> Sequence[Booking]:
    result = await self.session.execute(
        select(Booking)
        .where(
            extract("month", Booking.start_date) == month,
            extract("year", Booking.start_date) == year,
        )
    )
    return result.scalars().all()
```

**Example that breaks:**
- Booking: Jan 15 - Mar 15 (spans 3 months)
- Query: list_for_calendar(month=2, year=2025)  # February
- Result: NOT SHOWN ❌ (starts in Jan, not Feb)
- Expected: SHOULD BE SHOWN ✅ (overlaps with Feb)

**CORRECT Implementation:**
```python
async def list_for_calendar(self, month: int, year: int) -> Sequence[Booking]:
    # Get first and last day of month
    month_start = date(year, month, 1)
    _, last_day = monthrange(year, month)
    month_end = date(year, month, last_day)

    result = await self.session.execute(
        select(Booking)
        .where(
            and_(
                Booking.status.in_([StatusEnum.PENDING, StatusEnum.CONFIRMED]),
                Booking.start_date <= month_end,  # Starts on or before month end
                Booking.end_date >= month_start,  # Ends on or after month start
            )
        )
        .options(selectinload(Booking.approvals))  # Avoid N+1 queries
        .order_by(Booking.start_date)
    )
    return result.scalars().all()
```

**Why Critical:** BR-001 says bookings span multiple months must appear in ALL relevant calendars.

**Tests Required:**
```python
@pytest.mark.asyncio
async def test_calendar_single_month_booking(booking_repo):
    """Test booking within single month appears correctly."""
    # Feb 10-15
    booking = await booking_repo.create(Booking(
        start_date=date(2025, 2, 10),
        end_date=date(2025, 2, 15),
        ...
    ))

    feb_bookings = await booking_repo.list_for_calendar(month=2, year=2025)
    assert booking in feb_bookings

    jan_bookings = await booking_repo.list_for_calendar(month=1, year=2025)
    assert booking not in jan_bookings

@pytest.mark.asyncio
async def test_calendar_multi_month_booking(booking_repo):
    """Test booking spanning multiple months appears in ALL months."""
    # Jan 15 - Mar 15
    booking = await booking_repo.create(Booking(
        start_date=date(2025, 1, 15),
        end_date=date(2025, 3, 15),
        ...
    ))

    # Should appear in Jan, Feb, AND Mar
    jan_bookings = await booking_repo.list_for_calendar(month=1, year=2025)
    assert booking in jan_bookings

    feb_bookings = await booking_repo.list_for_calendar(month=2, year=2025)
    assert booking in feb_bookings

    mar_bookings = await booking_repo.list_for_calendar(month=3, year=2025)
    assert booking in mar_bookings

    # Should NOT appear in Apr
    apr_bookings = await booking_repo.list_for_calendar(month=4, year=2025)
    assert booking not in apr_bookings

@pytest.mark.asyncio
async def test_calendar_month_boundary(booking_repo):
    """Test booking on exact month boundaries."""
    # Jan 31 - Feb 1 (crosses month boundary)
    booking = await booking_repo.create(Booking(
        start_date=date(2025, 1, 31),
        end_date=date(2025, 2, 1),
        ...
    ))

    jan_bookings = await booking_repo.list_for_calendar(month=1, year=2025)
    assert booking in jan_bookings

    feb_bookings = await booking_repo.list_for_calendar(month=2, year=2025)
    assert booking in feb_bookings
```

---

## Issue #5: Wrong Ordering - created_at vs last_activity_at (MAJOR)

**Problem:** Used created_at instead of last_activity_at per BR-023

**WRONG Implementation:**
```python
.order_by(Booking.created_at.desc())
```

**CORRECT Implementation:**
```python
.order_by(Booking.last_activity_at.desc())
```

**Why Major:** BR-023 explicitly requires sorting by LastActivityAt DESC for all list views. This ensures most recently updated items appear first, not oldest created items.

**Test Required:**
```python
@pytest.mark.asyncio
async def test_list_ordered_by_last_activity(booking_repo):
    """Test BR-023: Lists ordered by last_activity_at DESC."""
    # Create booking 1 (older)
    booking1 = await booking_repo.create(Booking(...))
    await asyncio.sleep(0.1)

    # Create booking 2 (newer)
    booking2 = await booking_repo.create(Booking(...))
    await asyncio.sleep(0.1)

    # Update booking 1 (now has most recent activity)
    booking1.status = StatusEnum.CONFIRMED
    booking1.last_activity_at = datetime.now(timezone.utc)
    await booking_repo.update(booking1)

    # List should show booking1 first (most recent activity)
    bookings = await booking_repo.list_by_requester_email("test@example.com")
    assert bookings[0].id == booking1.id
    assert bookings[1].id == booking2.id
```

---

## Issue #6: Pending List Query - Wrong Return Type (MAJOR)

**Problem:** Query returned Approval instead of Booking, and didn't filter by status

**WRONG Implementation:**
```python
async def list_pending_for_party(
    self, party: AffiliationEnum, limit: int = 50
) -> Sequence[Approval]:
    result = await self.session.execute(
        select(Approval)
        .where(
            Approval.party == party,
            Approval.decision == DecisionEnum.NO_RESPONSE,
        )
        .order_by(Approval.id.desc())
        .limit(limit)
    )
    return result.scalars().all()
```

**Problems:**
1. Returns Approval, not Booking (frontend needs booking info)
2. No status filter (should only show status=Pending)
3. Wrong ordering (id instead of last_activity_at)
4. No eager loading (N+1 query problem)

**CORRECT Implementation:**
```python
async def list_pending_for_party(
    self, party: AffiliationEnum, limit: int = 50
) -> Sequence[Booking]:
    """
    List pending bookings where this party has NoResponse decision.

    Per BR-023: Outstanding items are:
    - Items where this approver = NoResponse
    - Status = Pending
    - Sorted by LastActivityAt desc (most recent activity first)
    """
    result = await self.session.execute(
        select(Booking)
        .join(Approval)
        .where(
            and_(
                Approval.party == party,
                Approval.decision == DecisionEnum.NO_RESPONSE,
                Booking.status == StatusEnum.PENDING,
            )
        )
        .options(selectinload(Booking.approvals))  # Eager load approvals
        .order_by(Booking.last_activity_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
```

**Test Required:**
```python
@pytest.mark.asyncio
async def test_pending_list_returns_bookings_not_approvals(approval_repo):
    """Test pending list returns Booking instances, not Approval."""
    booking = await create_test_booking()

    pending = await approval_repo.list_pending_for_party(AffiliationEnum.INGEBORG)

    assert len(pending) == 1
    assert isinstance(pending[0], Booking)  # Not Approval!
    assert pending[0].id == booking.id

@pytest.mark.asyncio
async def test_pending_list_filters_by_status(approval_repo):
    """Test pending list only shows Pending status bookings."""
    # Create Pending booking
    booking1 = await create_test_booking(status=StatusEnum.PENDING)

    # Create Confirmed booking (still has NoResponse for some approvers)
    booking2 = await create_test_booking(status=StatusEnum.CONFIRMED)

    pending = await approval_repo.list_pending_for_party(AffiliationEnum.INGEBORG)

    # Should only include Pending booking
    assert len(pending) == 1
    assert pending[0].id == booking1.id
```

---

## Issue #7: Missing History Query Method (MAJOR)

**Problem:** No method to retrieve history view for approvers

**Per BR-023:** Approvers need two views:
1. **Outstanding**: NoResponse + Pending only
2. **History**: ALL items they're involved in, all statuses

**Implementation was missing:**
```python
async def list_history_for_party(
    self, party: AffiliationEnum, limit: int = 100
) -> Sequence[Booking]:
    """
    List all bookings involving this party (history view).

    Per BR-023: History includes:
    - All items involving this approver
    - All statuses (Pending, Confirmed, Denied, Canceled)
    - Sorted by LastActivityAt desc
    - Read-only view
    """
    result = await self.session.execute(
        select(Booking)
        .join(Approval)
        .where(Approval.party == party)
        .options(selectinload(Booking.approvals))  # Eager load approvals
        .order_by(Booking.last_activity_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
```

**Test Required:**
```python
@pytest.mark.asyncio
async def test_history_includes_all_statuses(approval_repo):
    """Test history view includes all statuses."""
    # Create bookings with different statuses
    pending = await create_test_booking(status=StatusEnum.PENDING)
    confirmed = await create_test_booking(status=StatusEnum.CONFIRMED)
    denied = await create_test_booking(status=StatusEnum.DENIED)
    canceled = await create_test_booking(status=StatusEnum.CANCELED)

    history = await approval_repo.list_history_for_party(AffiliationEnum.INGEBORG)

    # All should be included
    assert len(history) == 4
    statuses = {b.status for b in history}
    assert statuses == {
        StatusEnum.PENDING,
        StatusEnum.CONFIRMED,
        StatusEnum.DENIED,
        StatusEnum.CANCELED,
    }
```

---

## Issue #8: N+1 Query Problem (MAJOR)

**Problem:** Missing eager loading in repository methods

**WRONG Implementation:**
```python
result = await self.session.execute(
    select(Booking).where(...)
)
return result.scalars().all()
```

**Result:** For each booking, a separate query fetches approvals (1 + N queries)

**CORRECT Implementation:**
```python
result = await self.session.execute(
    select(Booking)
    .where(...)
    .options(selectinload(Booking.approvals))  # Eager load!
)
return result.scalars().all()
```

**Result:** Single query with join (1 query total)

**Test Required:**
```python
@pytest.mark.asyncio
async def test_no_n_plus_1_queries(booking_repo, db_session):
    """Test BR-023: No N+1 query problems with eager loading."""
    # Create 10 bookings with approvals
    for _ in range(10):
        booking = await create_test_booking()
        await create_approvals_for_booking(booking)

    # Track queries
    from sqlalchemy import event
    queries = []

    def receive_after_cursor_execute(conn, cursor, statement, *args):
        queries.append(statement)

    event.listen(db_session.bind, "after_cursor_execute", receive_after_cursor_execute)

    # Fetch bookings and access approvals
    bookings = await booking_repo.list_for_calendar(month=1, year=2025)
    for booking in bookings:
        _ = booking.approvals  # Access relationship

    # Should be 1 query (or 2 max with eager loading), not 11 (1 + 10)
    assert len(queries) <= 2, f"N+1 query problem: {len(queries)} queries"
```

---

## Issue #9: Index Creation Inconsistency (MINOR)

**Problem:** Inconsistent DESC index creation pattern

**Migration had (OLD pattern):**
```python
op.create_index(
    "idx_bookings_last_activity",
    "bookings",
    [sa.text("last_activity_at DESC")],
)
```

**Model had (CORRECT pattern):**
```python
Index(
    "idx_bookings_last_activity",
    "last_activity_at",
    postgresql_ops={"last_activity_at": "DESC"},
)
```

**Fixed migration to match:**
```python
op.create_index(
    "idx_bookings_last_activity",
    "bookings",
    ["last_activity_at"],
    postgresql_ops={"last_activity_at": "DESC"},
)
```

**Why Important:** Consistency between migration and model prevents confusion and ensures both are maintainable.

**Test Required:**
```python
@pytest.mark.asyncio
async def test_desc_index_exists(db_engine):
    """Verify DESC index created correctly."""
    async with db_engine.connect() as conn:
        result = await conn.execute(text(
            """
            SELECT indexdef FROM pg_indexes
            WHERE indexname = 'idx_bookings_last_activity'
            """
        ))
        index_def = result.scalar()
        assert "DESC" in index_def
```

---

## Summary: Test-First Would Have Prevented All 9 Issues

**If tests were written FIRST:**

1. **Issues #1-3 (String constraints)**: Tests comparing migration schema to model would catch drift immediately
2. **Issue #4 (Calendar filtering)**: Test with multi-month booking would fail until fixed
3. **Issue #5 (Ordering)**: Test verifying last_activity_at order would fail with created_at
4. **Issue #6 (Return type)**: Type assertion `isinstance(result[0], Booking)` would fail
5. **Issue #7 (Missing method)**: Test calling the method would fail (method doesn't exist)
6. **Issue #8 (N+1)**: Query count test would fail with 11 queries instead of 1-2
7. **Issue #9 (Index)**: Index inspection test would catch inconsistency

**Conclusion:** These 9 issues exist because implementation came before tests. **TDD with test review prevents all of them.**

---

## Tests to Add to Phase 1 Documentation

### US-1.1: Schema Tests (Issues #1-3, #9)
- [ ] Test String length constraints match migration
- [ ] Test Booking model has String(40) for requester_first_name
- [ ] Test Booking model has String(254) for requester_email
- [ ] Test Booking model has String(500) for description
- [ ] Test Approval model has String(500) for comment
- [ ] Test TimelineEvent model has String(50) for actor
- [ ] Test TimelineEvent model has String(50) for event_type
- [ ] Test TimelineEvent model has Text() for note
- [ ] Test DESC index created correctly for last_activity_at

### US-1.2: Model Tests (Issue #5)
- [ ] Test compute_total_days() returns correct value
- [ ] Test relationships load correctly
- [ ] Test ordering uses last_activity_at not created_at

### US-1.3: Repository Tests (Issues #4, #6, #7, #8)
- [ ] Test calendar filtering with single-month booking
- [ ] Test calendar filtering with multi-month booking (Jan 15 - Mar 15)
- [ ] Test calendar filtering with month boundary (Jan 31 - Feb 1)
- [ ] Test pending list returns Booking instances
- [ ] Test pending list filters by status=Pending
- [ ] Test pending list orders by last_activity_at DESC
- [ ] Test history method exists and returns all statuses
- [ ] Test no N+1 queries with eager loading
- [ ] Test eager loading with selectinload()

**Total new tests:** 25 tests specifically targeting the 9 issues
