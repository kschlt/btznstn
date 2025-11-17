# Phase 1: Data Layer

## Goal

Implement database schema, SQLAlchemy models, and repository pattern.

**Duration:** 2-3 days
**Dependencies:** Phase 0 (Foundation)
**Outputs:** Working database with CRUD operations

---

## User Stories

### US-1.1: Database Schema

**As a** developer
**I want** PostgreSQL tables for bookings, approvals, timeline
**So that** I can persist booking data

**Acceptance Criteria:**

```gherkin
Feature: Database Schema

  Scenario: Tables created via migration
    Given Alembic is configured
    When I run "alembic upgrade head"
    Then the following tables should exist:
      | table            |
      | bookings         |
      | approvals        |
      | timeline_events  |
      | approver_parties |

  Scenario: Booking table has correct columns
    Given the bookings table exists
    When I query the table schema
    Then I should see columns:
      | column              | type         | constraints           |
      | id                  | UUID         | PRIMARY KEY           |
      | start_date          | DATE         | NOT NULL              |
      | end_date            | DATE         | NOT NULL              |
      | total_days          | INTEGER      | NOT NULL              |
      | party_size          | INTEGER      | CHECK (1-10)          |
      | affiliation         | ENUM         | NOT NULL              |
      | requester_first_name| VARCHAR(40)  | NOT NULL              |
      | requester_email     | VARCHAR(254) | NOT NULL              |
      | description         | VARCHAR(500) | NULL                  |
      | status              | ENUM         | NOT NULL              |
      | created_at          | TIMESTAMPTZ  | NOT NULL              |
      | updated_at          | TIMESTAMPTZ  | NOT NULL              |
      | last_activity_at    | TIMESTAMPTZ  | NOT NULL              |

  Scenario: Indexes created for performance
    Given the bookings table exists
    When I query table indexes
    Then I should see:
      | index                     | type  |
      | idx_bookings_status       | BTREE |
      | idx_bookings_date_range   | GIST  |
      | idx_bookings_last_activity| BTREE |

  Scenario: Foreign keys enforce referential integrity
    Given bookings and approvals tables exist
    When I try to delete a booking with approvals
    Then the approvals should also be deleted (CASCADE)

  Scenario: Check constraints validate data
    Given the bookings table exists
    When I try to insert party_size = 0
    Then I should get a constraint violation error
    When I try to insert party_size = 11
    Then I should get a constraint violation error
    When I try to insert end_date < start_date
    Then I should get a constraint violation error
```

**Tasks:**
- [ ] Create enums: `affiliation_enum`, `status_enum`, `decision_enum`
- [ ] Create `bookings` table with all columns + constraints
- [ ] Create `approvals` table with foreign key to bookings
- [ ] Create `timeline_events` table
- [ ] Create `approver_parties` table with seed data
- [ ] Add indexes for performance
- [ ] Add GiST index for date range overlap detection
- [ ] Write Alembic migration

**Tests:**
```python
# tests/integration/test_schema.py
@pytest.mark.asyncio
async def test_tables_exist(db_engine):
    async with db_engine.connect() as conn:
        result = await conn.execute(text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public'"
        ))
        tables = {row[0] for row in result}

        assert 'bookings' in tables
        assert 'approvals' in tables
        assert 'timeline_events' in tables
        assert 'approver_parties' in tables

@pytest.mark.asyncio
async def test_party_size_constraint(db_session):
    booking = Booking(
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1),
        party_size=0,  # Invalid
        affiliation=AffiliationEnum.INGEBORG,
        requester_first_name="Test",
        requester_email="test@example.com",
    )

    db_session.add(booking)

    with pytest.raises(IntegrityError):
        await db_session.commit()
```

---

### US-1.2: SQLAlchemy Models

**As a** developer
**I want** type-safe ORM models
**So that** I can query the database with Python

**Acceptance Criteria:**

```gherkin
Feature: SQLAlchemy Models

  Scenario: Booking model defined
    Given I import the Booking model
    When I inspect its attributes
    Then I should see type-safe mapped columns:
      | attribute            | type                     |
      | id                   | Mapped[UUID]             |
      | start_date           | Mapped[date]             |
      | end_date             | Mapped[date]             |
      | party_size           | Mapped[int]              |
      | status               | Mapped[StatusEnum]       |
      | approvals            | Mapped[list[Approval]]   |
      | timeline_events      | Mapped[list[TimelineEvent]] |

  Scenario: Booking created and persisted
    Given a database session
    When I create a Booking instance:
      """
      booking = Booking(
          start_date=date(2025, 8, 1),
          end_date=date(2025, 8, 5),
          party_size=4,
          affiliation=AffiliationEnum.INGEBORG,
          requester_first_name="Anna",
          requester_email="anna@example.com",
      )
      """
    And I add it to the session and commit
    Then the booking should have an ID
    And I can query it back from the database

  Scenario: Relationships work correctly
    Given a booking exists
    When I create 3 approval records for it
    Then booking.approvals should have 3 items
    And each approval should reference the booking

  Scenario: Total days computed correctly
    Given a booking with:
      | start_date | end_date   |
      | 2025-08-01 | 2025-08-05 |
    When I call booking.compute_total_days()
    Then it should return 5 (inclusive end date per BR-001)
```

**Tasks:**
- [ ] Create `app/models/base.py` with Base class
- [ ] Create `app/models/booking.py` with Booking model
- [ ] Create `app/models/approval.py` with Approval model
- [ ] Create `app/models/timeline_event.py`
- [ ] Define enums (StatusEnum, AffiliationEnum, DecisionEnum)
- [ ] Add relationships (booking ↔ approvals, timeline)
- [ ] Add `compute_total_days()` method

**Tests:**
```python
# tests/unit/test_models.py
def test_booking_model_attributes():
    """Test Booking model has correct type annotations."""
    assert hasattr(Booking, 'id')
    assert hasattr(Booking, 'start_date')
    assert hasattr(Booking, 'approvals')

@pytest.mark.asyncio
async def test_create_booking(db_session):
    """Test creating and persisting a booking."""
    booking = Booking(
        start_date=date(2025, 8, 1),
        end_date=date(2025, 8, 5),
        total_days=5,
        party_size=4,
        affiliation=AffiliationEnum.INGEBORG,
        requester_first_name="Anna",
        requester_email="anna@example.com",
        status=StatusEnum.PENDING,
    )

    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    assert booking.id is not None
    assert booking.total_days == 5

def test_total_days_calculation():
    """Test BR-001: Inclusive end date."""
    booking = Booking(
        start_date=date(2025, 8, 1),
        end_date=date(2025, 8, 5),
    )

    assert booking.compute_total_days() == 5  # 1,2,3,4,5 = 5 days
```

---

### US-1.3: Repository Pattern

**As a** developer
**I want** a repository layer for data access
**So that** business logic is separated from database queries

**Acceptance Criteria:**

```gherkin
Feature: Booking Repository

  Scenario: Create booking
    Given a BookingRepository instance
    When I call repository.create(booking_data)
    Then a new booking should be inserted
    And it should return the created booking with ID

  Scenario: Get booking by ID
    Given a booking exists with ID "abc-123"
    When I call repository.get("abc-123")
    Then it should return the booking

  Scenario: Get booking with approvals (eager load)
    Given a booking exists with 3 approvals
    When I call repository.get_with_approvals(booking_id)
    Then the returned booking should have approvals loaded
    And no additional queries should be made

  Scenario: List bookings for calendar
    Given 10 bookings exist in August 2025
    When I call repository.list_for_calendar(month=8, year=2025)
    Then it should return only Pending and Confirmed bookings
    And they should be ordered by start_date

  Scenario: Check for conflicts
    Given a booking exists from 2025-08-01 to 2025-08-05
    When I call repository.check_conflicts(start=2025-08-03, end=2025-08-08)
    Then it should return the conflicting booking
```

**Tasks:**
- [ ] Create `app/repositories/booking_repository.py`
- [ ] Implement `create()`, `get()`, `update()`, `delete()`
- [ ] Implement `get_with_approvals()` (eager loading)
- [ ] Implement `list_for_calendar()`
- [ ] Implement `check_conflicts()` (date range overlap using GiST index)
- [ ] Create `app/repositories/approval_repository.py`
- [ ] Create `app/repositories/timeline_repository.py`

**Tests:**
```python
# tests/unit/test_booking_repository.py
@pytest.mark.asyncio
async def test_create_booking(booking_repo, booking_create_data):
    """Test creating a booking via repository."""
    booking = await booking_repo.create(booking_create_data)

    assert booking.id is not None
    assert booking.status == StatusEnum.PENDING

@pytest.mark.asyncio
async def test_get_booking(booking_repo, sample_booking):
    """Test retrieving a booking by ID."""
    booking = await booking_repo.get(sample_booking.id)

    assert booking is not None
    assert booking.id == sample_booking.id

@pytest.mark.asyncio
async def test_check_conflicts(booking_repo):
    """Test BR-002: Conflict detection."""
    # Create booking 2025-08-01 to 2025-08-05
    await booking_repo.create(BookingCreate(
        start_date=date(2025, 8, 1),
        end_date=date(2025, 8, 5),
        ...
    ))

    # Check for overlapping date range
    conflicts = await booking_repo.check_conflicts(
        start_date=date(2025, 8, 3),
        end_date=date(2025, 8, 8),
    )

    assert len(conflicts) == 1  # Should find conflict

    # Check non-overlapping range
    conflicts = await booking_repo.check_conflicts(
        start_date=date(2025, 8, 10),
        end_date=date(2025, 8, 15),
    )

    assert len(conflicts) == 0  # No conflict
```

---

### US-1.4: Seed Data

**As a** developer
**I want** seed data for approver parties
**So that** the three approvers are pre-configured

**Acceptance Criteria:**

```gherkin
Feature: Seed Data

  Scenario: Approver parties seeded
    Given the database is migrated
    When I query the approver_parties table
    Then I should see 3 rows:
      | party     | email                   |
      | Ingeborg  | ingeborg@example.com    |
      | Cornelia  | cornelia@example.com    |
      | Angelika  | angelika@example.com    |

  Scenario: Seed data is idempotent
    Given approver parties already exist
    When I run the seed script again
    Then no duplicates should be created
    And the count should still be 3
```

**Tasks:**
- [ ] Create `app/db/seed.py` with seed data
- [ ] Add seed data to migration or separate script
- [ ] Make seed idempotent (`ON CONFLICT DO NOTHING`)

**Tests:**
```python
@pytest.mark.asyncio
async def test_approver_parties_seeded(db_session):
    """Test approver parties are seeded."""
    result = await db_session.execute(
        select(ApproverParty).order_by(ApproverParty.party)
    )
    parties = result.scalars().all()

    assert len(parties) == 3
    assert parties[0].party == AffiliationEnum.INGEBORG
    assert parties[1].party == AffiliationEnum.CORNELIA
    assert parties[2].party == AffiliationEnum.ANGELIKA
```

---

## Definition of Done

- [ ] All migrations run successfully: `alembic upgrade head`
- [ ] All models have type hints (mypy passes)
- [ ] Repository pattern implemented for all entities
- [ ] Unit tests pass (≥90% coverage for models/repositories)
- [ ] Integration tests pass (actual PostgreSQL)
- [ ] Seed data created
- [ ] Documentation updated

---

## Testing Commands

```bash
# Run migrations
alembic upgrade head

# Check schema
psql $DATABASE_URL -c "\dt"  # List tables
psql $DATABASE_URL -c "\d bookings"  # Describe bookings table

# Run unit tests
pytest tests/unit/test_models.py -v
pytest tests/unit/test_booking_repository.py -v

# Run integration tests (requires PostgreSQL)
pytest tests/integration/test_schema.py -v

# Check coverage
pytest --cov=app.models --cov=app.repositories --cov-report=html
```

---

## Next Phase

✅ Data Layer complete → [Phase 2: Booking API](phase-2-booking-api.md)
