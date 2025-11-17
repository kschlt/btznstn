# Database Schema

## Overview

Complete PostgreSQL database schema for the Betzenstein booking & approval application.

**Database:** PostgreSQL 15+
**Hosting:** Fly.io Postgres (Frankfurt)
**ORM:** SQLAlchemy 2.0
**Migrations:** Alembic

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────┐
│            BOOKINGS                 │
│─────────────────────────────────────│
│ id (PK, UUID)                       │
│ start_date (DATE)                   │
│ end_date (DATE)                     │
│ total_days (INT)                    │
│ party_size (INT)                    │
│ description (VARCHAR(500), null)    │
│ requester_first_name (VARCHAR(40))  │
│ requester_email (VARCHAR(254))      │
│ affiliation (ENUM)                  │
│ status (ENUM)                       │
│ created_at (TIMESTAMPTZ)            │
│ updated_at (TIMESTAMPTZ)            │
│ last_activity_at (TIMESTAMPTZ)      │
└──────────────┬──────────────────────┘
               │
               │ 1:N
               ↓
┌─────────────────────────────────────┐
│            APPROVALS                │
│─────────────────────────────────────│
│ id (PK, UUID)                       │
│ booking_id (FK → bookings.id)       │
│ party (ENUM)                        │
│ decision (ENUM)                     │
│ comment (VARCHAR(500), null)        │
│ decided_at (TIMESTAMPTZ, null)      │
└─────────────────────────────────────┘

               ┌─────────────────┐
               │    BOOKINGS     │
               └────────┬────────┘
                        │
                        │ 1:N
                        ↓
┌─────────────────────────────────────┐
│         TIMELINE_EVENTS             │
│─────────────────────────────────────│
│ id (PK, UUID)                       │
│ booking_id (FK → bookings.id)       │
│ when (TIMESTAMPTZ)                  │
│ actor (VARCHAR(50))                 │
│ event_type (VARCHAR(50))            │
│ note (TEXT, null)                   │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│        APPROVER_PARTIES             │
│─────────────────────────────────────│
│ party (PK, ENUM)                    │
│ email (VARCHAR(254), unique)        │
│ notification_enabled (BOOLEAN)      │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│            HOLIDAYS (optional)      │
│─────────────────────────────────────│
│ date (PK, DATE)                     │
│ name (VARCHAR(100))                 │
│ region (VARCHAR(10))                │
└─────────────────────────────────────┘
```

---

## Tables

### bookings

**Purpose:** Core booking/request entity.

**DDL:**
```sql
CREATE TYPE affiliation_enum AS ENUM ('Ingeborg', 'Cornelia', 'Angelika');
CREATE TYPE status_enum AS ENUM ('Pending', 'Denied', 'Confirmed', 'Canceled');

CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Dates (inclusive end date per BR-001)
    start_date DATE NOT NULL,
    end_date DATE NOT NULL CHECK (end_date >= start_date),
    total_days INT NOT NULL,  -- Computed: (end_date - start_date) + 1

    -- Party details
    party_size INT NOT NULL CHECK (party_size >= 1 AND party_size <= 10),
    affiliation affiliation_enum NOT NULL,

    -- Requester details
    requester_first_name VARCHAR(40) NOT NULL,
    requester_email VARCHAR(254) NOT NULL,  -- Not unique (can have multiple bookings)

    -- Optional description
    description VARCHAR(500),

    -- Status
    status status_enum NOT NULL DEFAULT 'Pending',

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_requester_email ON bookings(requester_email);
CREATE INDEX idx_bookings_last_activity ON bookings(last_activity_at DESC);
CREATE INDEX idx_bookings_date_range ON bookings USING GIST (daterange(start_date, end_date, '[]'));

-- Trigger: Update updated_at on row modification
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_bookings_updated_at
BEFORE UPDATE ON bookings
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

**Constraints:**
- `CHECK (end_date >= start_date)` - End cannot be before start
- `CHECK (party_size >= 1 AND party_size <= 10)` - Valid party size (BR-016)

**Notes:**
- `total_days` is computed on insert/update (not a generated column for compatibility)
- `requester_email` not unique (same person can have multiple bookings)
- `daterange` GiST index for fast overlap detection (BR-002, BR-029)

---

### approvals

**Purpose:** Tracks approval decisions for each booking.

**DDL:**
```sql
CREATE TYPE decision_enum AS ENUM ('NoResponse', 'Approved', 'Denied');

CREATE TABLE approvals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    party affiliation_enum NOT NULL,  -- Ingeborg, Cornelia, Angelika

    decision decision_enum NOT NULL DEFAULT 'NoResponse',
    comment VARCHAR(500),  -- Required if decision = 'Denied'
    decided_at TIMESTAMPTZ,  -- Set when decision changes from NoResponse

    UNIQUE(booking_id, party)  -- Each party can only approve once per booking
);

-- Indexes
CREATE INDEX idx_approvals_booking ON approvals(booking_id);
CREATE INDEX idx_approvals_decision ON approvals(decision);
CREATE INDEX idx_approvals_party_decision ON approvals(party, decision);
```

**Constraints:**
- `UNIQUE(booking_id, party)` - Each party approves once per booking
- `ON DELETE CASCADE` - Delete approvals when booking deleted

**Notes:**
- Always 3 approval records per booking (created on booking insert)
- `comment` required if `decision = 'Denied'` (validated in app layer)

---

### timeline_events

**Purpose:** Audit log of all actions on a booking.

**DDL:**
```sql
CREATE TABLE timeline_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,

    when TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    actor VARCHAR(50) NOT NULL,  -- "Requester", "Ingeborg", "Cornelia", "Angelika", "System"
    event_type VARCHAR(50) NOT NULL,  -- "Submitted", "Approved", "Denied", "Confirmed", etc.
    note TEXT  -- Optional context (e.g., old→new dates for edits)
);

-- Indexes
CREATE INDEX idx_timeline_booking ON timeline_events(booking_id);
CREATE INDEX idx_timeline_when ON timeline_events(when DESC);
```

**Event Types:**
- `Submitted` - Booking created
- `Approved` - Party approved
- `Denied` - Party denied (note = comment)
- `Confirmed` - All parties approved
- `Canceled` - Requester canceled
- `Reopened` - Requester reopened denied booking
- `DateEdited` - Dates changed (note = "01.–05.08. → 03.–08.08.")

**Notes:**
- `note` stores context (e.g., date diffs, comments)
- Visible to relevant parties based on role (specs/ui-screens.md §Timeline Display)

---

### approver_parties

**Purpose:** Seed data for the three fixed approvers.

**DDL:**
```sql
CREATE TABLE approver_parties (
    party affiliation_enum PRIMARY KEY,
    email VARCHAR(254) NOT NULL UNIQUE,
    notification_enabled BOOLEAN NOT NULL DEFAULT TRUE
);

-- Seed data
INSERT INTO approver_parties (party, email, notification_enabled) VALUES
('Ingeborg', 'ingeborg@example.com', TRUE),
('Cornelia', 'cornelia@example.com', TRUE),
('Angelika', 'angelika@example.com', TRUE);
```

**Notes:**
- Read-only in application (seeded via migration)
- `notification_enabled` allows disabling emails per party (future feature)

---

### holidays (Optional)

**Purpose:** Display holidays in calendar (visual only, no business logic impact).

**DDL:**
```sql
CREATE TABLE holidays (
    date DATE PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    region VARCHAR(10) NOT NULL DEFAULT 'DE'  -- e.g., 'DE', 'DE-NRW'
);

-- Example seed data
INSERT INTO holidays (date, name, region) VALUES
('2025-01-01', 'Neujahr', 'DE'),
('2025-04-18', 'Karfreitag', 'DE'),
('2025-12-25', 'Weihnachten', 'DE');
```

**Notes:**
- Optional feature (specs say "if unavailable, hide")
- No foreign keys (standalone table)
- Can populate via external API or manual insert

---

## Enums

### affiliation_enum

```sql
CREATE TYPE affiliation_enum AS ENUM ('Ingeborg', 'Cornelia', 'Angelika');
```

**Usage:**
- `bookings.affiliation`
- `approvals.party`
- `approver_parties.party`

---

### status_enum

```sql
CREATE TYPE status_enum AS ENUM ('Pending', 'Denied', 'Confirmed', 'Canceled');
```

**Usage:**
- `bookings.status`

**State Transitions:**
- `Pending` → `Confirmed` (all approved)
- `Pending` → `Denied` (one denied)
- `Pending` → `Canceled` (requester canceled)
- `Confirmed` → `Denied` (post-confirm deny)
- `Confirmed` → `Canceled` (requester canceled)
- `Denied` → `Pending` (reopened)

---

### decision_enum

```sql
CREATE TYPE decision_enum AS ENUM ('NoResponse', 'Approved', 'Denied');
```

**Usage:**
- `approvals.decision`

---

## Indexes

### Performance Indexes

| Table | Index | Type | Purpose |
|-------|-------|------|---------|
| `bookings` | `idx_bookings_status` | B-tree | Filter by status |
| `bookings` | `idx_bookings_requester_email` | B-tree | Find bookings by email |
| `bookings` | `idx_bookings_last_activity` | B-tree (DESC) | Sort by recent activity |
| `bookings` | `idx_bookings_date_range` | GiST | Overlap detection (BR-002) |
| `approvals` | `idx_approvals_booking` | B-tree | Join bookings ↔ approvals |
| `approvals` | `idx_approvals_decision` | B-tree | Filter by decision |
| `approvals` | `idx_approvals_party_decision` | B-tree | Approver outstanding list |
| `timeline_events` | `idx_timeline_booking` | B-tree | Join bookings ↔ timeline |
| `timeline_events` | `idx_timeline_when` | B-tree (DESC) | Sort timeline chronologically |

---

## Constraints

### Primary Keys

All tables use `UUID` primary keys (generated via `gen_random_uuid()`).

**Rationale:**
- No enumeration (can't guess IDs)
- Distributed-friendly (no central ID generator)
- Privacy-friendly (opaque)

---

### Foreign Keys

| Child Table | Column | Parent Table | On Delete |
|-------------|--------|--------------|-----------|
| `approvals` | `booking_id` | `bookings.id` | CASCADE |
| `timeline_events` | `booking_id` | `bookings.id` | CASCADE |

**CASCADE:** Delete approvals + timeline when booking deleted.

---

### Unique Constraints

| Table | Columns | Purpose |
|-------|---------|---------|
| `approvals` | `(booking_id, party)` | Each party approves once per booking |
| `approver_parties` | `email` | Email unique across approvers |
| `holidays` | `date` (PK) | One holiday per date |

---

### Check Constraints

| Table | Constraint | Purpose |
|-------|-----------|---------|
| `bookings` | `end_date >= start_date` | Valid date range |
| `bookings` | `party_size >= 1 AND party_size <= 10` | Valid party size (BR-016) |

---

## Triggers

### update_updated_at_column

**Purpose:** Auto-update `updated_at` on row modification.

**Applied To:** `bookings`

**Implementation:**
```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_bookings_updated_at
BEFORE UPDATE ON bookings
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();
```

---

## SQLAlchemy Models

### Booking Model

```python
from sqlalchemy import String, Integer, Date, Enum, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from uuid import UUID, uuid4
from datetime import date, datetime
import enum

class AffiliationEnum(enum.Enum):
    INGEBORG = "Ingeborg"
    CORNELIA = "Cornelia"
    ANGELIKA = "Angelika"

class StatusEnum(enum.Enum):
    PENDING = "Pending"
    DENIED = "Denied"
    CONFIRMED = "Confirmed"
    CANCELED = "Canceled"

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    start_date: Mapped[date]
    end_date: Mapped[date]
    total_days: Mapped[int]

    party_size: Mapped[int]
    affiliation: Mapped[AffiliationEnum]

    requester_first_name: Mapped[str] = mapped_column(String(40))
    requester_email: Mapped[str] = mapped_column(String(254), index=True)

    description: Mapped[Optional[str]] = mapped_column(String(500))

    status: Mapped[StatusEnum] = mapped_column(default=StatusEnum.PENDING)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)

    # Relationships
    approvals: Mapped[list["Approval"]] = relationship(back_populates="booking", cascade="all, delete-orphan")
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(back_populates="booking", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="check_end_after_start"),
        CheckConstraint("party_size >= 1 AND party_size <= 10", name="check_party_size_range"),
    )

    def compute_total_days(self) -> int:
        """Compute total days (inclusive end date per BR-001)."""
        return (self.end_date - self.start_date).days + 1
```

### Approval Model

```python
class DecisionEnum(enum.Enum):
    NO_RESPONSE = "NoResponse"
    APPROVED = "Approved"
    DENIED = "Denied"

class Approval(Base):
    __tablename__ = "approvals"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    booking_id: Mapped[UUID] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), index=True)
    party: Mapped[AffiliationEnum]

    decision: Mapped[DecisionEnum] = mapped_column(default=DecisionEnum.NO_RESPONSE, index=True)
    comment: Mapped[Optional[str]] = mapped_column(String(500))
    decided_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Relationships
    booking: Mapped["Booking"] = relationship(back_populates="approvals")

    __table_args__ = (
        UniqueConstraint("booking_id", "party", name="unique_booking_party"),
    )
```

### TimelineEvent Model

```python
class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    booking_id: Mapped[UUID] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), index=True)

    when: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    actor: Mapped[str] = mapped_column(String(50))
    event_type: Mapped[str] = mapped_column(String(50))
    note: Mapped[Optional[str]]

    # Relationships
    booking: Mapped["Booking"] = relationship(back_populates="timeline_events")
```

---

## Migrations

### Alembic Setup

```bash
# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial schema: bookings, approvals, timeline"

# Apply migrations
alembic upgrade head
```

### Example Migration

```python
# alembic/versions/001_initial_schema.py

def upgrade():
    # Create enums
    op.execute("CREATE TYPE affiliation_enum AS ENUM ('Ingeborg', 'Cornelia', 'Angelika')")
    op.execute("CREATE TYPE status_enum AS ENUM ('Pending', 'Denied', 'Confirmed', 'Canceled')")
    op.execute("CREATE TYPE decision_enum AS ENUM ('NoResponse', 'Approved', 'Denied')")

    # Create bookings table
    op.create_table(
        'bookings',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('total_days', sa.Integer(), nullable=False),
        sa.Column('party_size', sa.Integer(), nullable=False),
        sa.Column('affiliation', sa.Enum('Ingeborg', 'Cornelia', 'Angelika', name='affiliation_enum'), nullable=False),
        sa.Column('requester_first_name', sa.String(40), nullable=False),
        sa.Column('requester_email', sa.String(254), nullable=False),
        sa.Column('description', sa.String(500)),
        sa.Column('status', sa.Enum('Pending', 'Denied', 'Confirmed', 'Canceled', name='status_enum'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_activity_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint('end_date >= start_date'),
        sa.CheckConstraint('party_size >= 1 AND party_size <= 10'),
    )

    # Create indexes
    op.create_index('idx_bookings_status', 'bookings', ['status'])
    op.create_index('idx_bookings_requester_email', 'bookings', ['requester_email'])
    op.create_index('idx_bookings_last_activity', 'bookings', ['last_activity_at'], postgresql_using='btree', postgresql_ops={'last_activity_at': 'DESC'})
    op.execute("CREATE INDEX idx_bookings_date_range ON bookings USING GIST (daterange(start_date, end_date, '[]'))")

    # ... (approvals, timeline_events, approver_parties, triggers)

def downgrade():
    op.drop_table('timeline_events')
    op.drop_table('approvals')
    op.drop_table('bookings')
    op.drop_table('approver_parties')
    op.execute("DROP TYPE decision_enum")
    op.execute("DROP TYPE status_enum")
    op.execute("DROP TYPE affiliation_enum")
```

---

## Seed Data

### Approver Parties

```sql
INSERT INTO approver_parties (party, email, notification_enabled) VALUES
('Ingeborg', 'ingeborg@example.com', TRUE),
('Cornelia', 'cornelia@example.com', TRUE),
('Angelika', 'angelika@example.com', TRUE)
ON CONFLICT (party) DO NOTHING;
```

**Run in migration or separate seed script.**

---

## Queries

### Conflict Detection (BR-002, BR-029)

```sql
-- Check if date range conflicts with existing Pending/Confirmed bookings
SELECT * FROM bookings
WHERE status IN ('Pending', 'Confirmed')
  AND daterange(start_date, end_date, '[]') && daterange('2025-08-01', '2025-08-05', '[]');
```

**GiST index `idx_bookings_date_range` makes this fast.**

---

### Approver Outstanding List

```sql
-- Get bookings where party 'Ingeborg' has NoResponse decision
SELECT b.*
FROM bookings b
JOIN approvals a ON b.id = a.booking_id
WHERE a.party = 'Ingeborg'
  AND a.decision = 'NoResponse'
  AND b.status = 'Pending'
ORDER BY b.last_activity_at DESC
LIMIT 20;
```

**Uses:** `idx_approvals_party_decision`, `idx_bookings_last_activity`

---

### Booking with Full Details

```sql
-- Get booking + approvals + timeline (for details page)
SELECT
    b.*,
    json_agg(
        json_build_object(
            'party', a.party,
            'decision', a.decision,
            'comment', a.comment,
            'decided_at', a.decided_at
        )
    ) AS approvals,
    (
        SELECT json_agg(
            json_build_object(
                'when', t.when,
                'actor', t.actor,
                'event_type', t.event_type,
                'note', t.note
            )
            ORDER BY t.when ASC
        )
        FROM timeline_events t
        WHERE t.booking_id = b.id
    ) AS timeline
FROM bookings b
LEFT JOIN approvals a ON b.id = a.booking_id
WHERE b.id = 'uuid-here'
GROUP BY b.id;
```

**ORM equivalent:** Eager load relationships (`selectinload`)

---

## Database Connection

### Connection String

```
postgresql+asyncpg://user:pass@betzenstein-db.internal:5432/betzenstein
```

**Environment Variable:**
```bash
DATABASE_URL=postgresql+asyncpg://user:pass@betzenstein-db.internal:5432/betzenstein
```

---

### Connection Pooling

**SQLAlchemy config:**
```python
engine = create_async_engine(
    DATABASE_URL,
    pool_size=10,        # Max connections in pool
    max_overflow=20,     # Extra connections if pool exhausted
    pool_pre_ping=True,  # Verify connections before use
)
```

---

## Backup & Recovery

### Fly.io Postgres Backups

**Automatic:**
- Daily snapshots included
- Retention: 7 days (default)

**Manual Backup:**
```bash
flyctl postgres db dump betzenstein-db > backup.sql
```

**Restore:**
```bash
psql $DATABASE_URL < backup.sql
```

---

## Performance Optimization

### Query Optimization

**Use EXPLAIN ANALYZE:**
```sql
EXPLAIN ANALYZE
SELECT * FROM bookings
WHERE status IN ('Pending', 'Confirmed')
  AND daterange(start_date, end_date, '[]') && daterange('2025-08-01', '2025-08-05', '[]');
```

**Expected:** Index scan on `idx_bookings_date_range`

---

### Connection Pooling

**Problem:** Opening new connections is slow.

**Solution:** SQLAlchemy connection pool reuses connections.

---

### N+1 Query Problem

**Problem:**
```python
# Bad: N+1 queries
bookings = await session.execute(select(Booking))
for booking in bookings.scalars():
    print(booking.approvals)  # Triggers separate query per booking
```

**Solution:**
```python
# Good: Eager loading
bookings = await session.execute(
    select(Booking).options(selectinload(Booking.approvals))
)
for booking in bookings.scalars():
    print(booking.approvals)  # Already loaded
```

---

## Testing

### Test Database

**Option 1:** SQLite in-memory (fast unit tests)
```python
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
```

**Option 2:** PostgreSQL test database (realistic integration tests)
```python
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/test_db"
```

**Setup/Teardown:**
```python
@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()
```

---

## Related Documentation

- [Data Model (Entities)](../specification/data-model.md) - High-level entity descriptions
- [Business Rules](../foundation/business-rules.md) - BR-001 to BR-029
- [API Specification](api-specification.md) - Endpoints that use this schema
- [ADR-003: Database & ORM](../architecture/adr-003-database-orm.md) - PostgreSQL + SQLAlchemy decision

---

## Summary

This schema is designed for:

- ✅ **ACID compliance** - Conflict detection via transactions
- ✅ **Fast overlap detection** - GiST index on date ranges
- ✅ **Type safety** - Enums + SQLAlchemy 2.0 Mapped types
- ✅ **Audit trail** - Timeline events log all actions
- ✅ **Privacy** - Emails indexed but never exposed in responses
- ✅ **Scalability** - Indexes on all query paths

**Next:** Implement SQLAlchemy models + Alembic migrations from this spec.
