# ADR-003: Database & ORM - PostgreSQL + SQLAlchemy on Fly.io

**Status:** Accepted
**Date:** 2025-01-17
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)

---

## Context

We need to choose a database and ORM for the Betzenstein booking & approval application. The system must support:

- Relational data (bookings, approvals, timeline)
- ACID transactions (conflict detection, first-write-wins)
- Concurrent access (multiple users, race conditions)
- PostgreSQL-specific features (if beneficial)
- Type-safe ORM for Python
- Easy hosting and management
- Co-located with backend (low latency)

### Requirements from Specifications

From `docs/specification/data-model.md` and `docs/foundation/business-rules.md`:

- **BR-002:** No overlaps - requires conflict detection
- **BR-029:** First-write-wins - requires transactions with proper isolation
- **BR-024:** First-action-wins - requires atomic updates
- **Type safety:** ORM must work with mypy
- **Async support:** FastAPI is async, ORM should be too
- **AI implementation:** Standard, well-documented ORM

---

## Decision

We will use:
- **PostgreSQL 15+** as the database
- **SQLAlchemy 2.0** as the ORM
- **Alembic** for migrations
- **Fly.io Postgres** as the hosting provider

---

## Rationale

### 1. PostgreSQL (Database)

**Why PostgreSQL:**

#### a) ACID Guarantees (Critical)

**Requirements:** BR-002 (no overlaps), BR-029 (first-write-wins).

**PostgreSQL:**
- ✅ **Strong ACID compliance** - Guaranteed consistency
- ✅ **Transaction isolation levels** - Can use SERIALIZABLE for strictest conflict detection
- ✅ **Row-level locking** - Prevent concurrent modifications

**Example (first-write-wins):**
```sql
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Check for conflicts
SELECT * FROM bookings
WHERE status IN ('Pending', 'Confirmed')
  AND daterange(start_date, end_date, '[]') && daterange('2025-01-15', '2025-01-20', '[]');

-- If no conflicts, insert
INSERT INTO bookings (...) VALUES (...);

COMMIT;  -- Fails if another transaction modified overlapping dates
```

#### b) Advanced Features

- ✅ **Range types** - `daterange` perfect for booking dates
- ✅ **Indexes on ranges** - GiST indexes for fast overlap detection
- ✅ **JSON support** - For flexible data (if needed)
- ✅ **Full-text search** - For description search (if needed later)

#### c) Mature & Proven

- ✅ **30+ years old** - Rock-solid
- ✅ **Wide adoption** - Massive community
- ✅ **Well-documented** - Excellent docs, AI knows it well

#### d) Open Source & Free

- ✅ **No licensing costs**
- ✅ **No vendor lock-in**
- ✅ **Standard SQL** - Portable

### 2. SQLAlchemy 2.0 (ORM)

**Why SQLAlchemy:**

#### a) AI-Friendly

- ✅ **Most popular Python ORM** - Extensive training data
- ✅ **Well-documented** - Official docs excellent
- ✅ **Standard patterns** - Clear conventions
- ✅ **Type hints support** - Works with mypy

**Evidence:** SQLAlchemy is the de facto Python ORM. AI consistently generates correct SQLAlchemy code.

#### b) Type Safety

**Requirement:** Catch AI errors at type-check time.

**SQLAlchemy 2.0:**
- ✅ **Fully typed** - All APIs have type hints
- ✅ **Mypy plugin** - Validates ORM usage
- ✅ **Compile-time checks** - Wrong queries caught before runtime

**Example:**
```python
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    requester_email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    start_date: Mapped[date]
    end_date: Mapped[date]
    party_size: Mapped[int]
    description: Mapped[Optional[str]] = mapped_column(String(500))
    status: Mapped[Status]  # Enum

# Mypy catches:
booking.party_size = "invalid"  # Error: str not int
booking.start_date = None       # Error: date required
```

#### c) Async Support

**Requirement:** FastAPI is async, ORM should be too.

**SQLAlchemy 2.0:**
- ✅ **Native async** - `async_session`, `await` queries
- ✅ **Asyncpg driver** - Fast PostgreSQL async driver
- ✅ **Non-blocking** - Doesn't block FastAPI event loop

**Example:**
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

engine = create_async_engine("postgresql+asyncpg://...")

async def get_booking(db: AsyncSession, booking_id: UUID) -> Booking:
    result = await db.execute(
        select(Booking).where(Booking.id == booking_id)
    )
    return result.scalar_one_or_none()
```

#### d) Migrations (Alembic)

**Requirement:** Version-controlled schema changes.

**Alembic:**
- ✅ **Standard for SQLAlchemy** - Official migration tool
- ✅ **Auto-generate migrations** - From model changes
- ✅ **Reversible** - Can rollback
- ✅ **AI-friendly** - Clear patterns

**Example:**
```bash
# AI can generate migrations
alembic revision --autogenerate -m "Add party_size column"
alembic upgrade head
```

#### e) Repository Pattern

**Benefit:** Separates data access from business logic.

**SQLAlchemy:**
- ✅ **Clean abstraction** - Repository layer wraps DB operations
- ✅ **Testable** - Can mock repository in tests
- ✅ **AI-friendly** - Clear separation of concerns

**Example:**
```python
class BookingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, booking_data: BookingCreate) -> Booking:
        booking = Booking(**booking_data.dict())
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def get(self, booking_id: UUID) -> Booking | None:
        result = await self.db.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        return result.scalar_one_or_none()
```

### 3. Fly.io Postgres (Database Hosting)

**Why Fly.io Postgres:**

#### a) Co-Located with API

- ✅ **Same platform** - API and database on Fly.io
- ✅ **Low latency** - Private network connection (no internet hop)
- ✅ **Simple management** - One platform, one CLI, one dashboard
- ✅ **Frankfurt region** - Same region as backend (even lower latency)

**AI benefit:** Simpler mental model - everything on Fly.io.

#### b) No Shutdown on Inactivity

**Unlike Supabase:**
- ✅ **Always on** - Doesn't pause/shutdown when idle
- ✅ **No cold starts** - Instant connections
- ✅ **Predictable** - No surprise "database is sleeping" errors

**User experience:** This was the key requirement - avoid Supabase shutdown issue.

#### c) Simple Connection Strings

**Fly.io provides:**
```env
DATABASE_URL=postgres://user:pass@appname-db.internal:5432/dbname
```

**Internal networking:**
- API connects via `.internal` hostname (private network)
- No public internet, lower latency
- AI can use standard `DATABASE_URL` environment variable

#### d) Managed PostgreSQL

- ✅ **Automatic backups** - Snapshots included
- ✅ **Monitoring** - Fly.io dashboard shows metrics
- ✅ **Scaling** - Can increase storage/RAM as needed
- ✅ **Updates** - Fly.io handles Postgres version updates

#### e) Good Pricing

**Fly.io free allowance:**
- 3GB storage included in free tier
- Shared CPU (sufficient for MVP)
- No additional cost for small database

**Later scaling:**
- ~$1-2/month for dedicated resources
- Pay-as-you-go, predictable

---

## Alternatives Considered

### Supabase (Database Hosting)

**Pros:**
- Managed PostgreSQL
- Good UI
- Generous free tier

**Cons:**
- ❌ **Shuts down when idle** - Pauses after ~7 days inactivity
- ❌ **Cold starts** - Slow to wake up (user annoyance)
- ❌ **Extra features we don't need** - Auth, Realtime, Storage, etc.
- ❌ **More expensive for always-on** - $25/month for no-pause
- ❌ **Vendor-specific patterns** - RLS, Supabase client, etc.

**Decision:** Shutdown behavior is unacceptable. Fly.io Postgres stays always-on.

---

### Railway (Database Hosting)

**Pros:**
- Excellent PostgreSQL management
- Beautiful UI/dashboard
- Good free tier ($5 credit/month)
- Simple connection strings

**Cons:**
- ⚠️ **Separate platform** - API on Fly.io, DB on Railway
- ⚠️ **Public internet connection** - Slight latency overhead
- ⚠️ **One more service** - More accounts, more management

**Decision:** Keeping everything on Fly.io is simpler. Single platform preferred.

---

### MySQL/MariaDB

**Pros:**
- Mature, widely used
- Good performance

**Cons:**
- ❌ **Weaker ACID** - Less strict than PostgreSQL
- ❌ **No range types** - Can't use `daterange` for conflicts
- ❌ **Less advanced features** - No GiST indexes, etc.

**Decision:** PostgreSQL is better for this use case (transactions, ranges).

---

### Django ORM

**Pros:**
- Simple, batteries-included
- AI knows it well

**Cons:**
- ❌ **Requires Django** - We're using FastAPI
- ❌ **Less flexible** - More opinionated
- ❌ **Sync-only** - No async support

**Decision:** SQLAlchemy is better for FastAPI + async.

---

### Prisma (ORM)

**Pros:**
- Type-safe (TypeScript-first)
- Auto-generates migrations
- Modern

**Cons:**
- ❌ **Node.js-first** - Python support experimental
- ❌ **Less Python training data** - AI knows SQLAlchemy better
- ❌ **Extra tooling** - Prisma CLI, schema files, etc.

**Decision:** SQLAlchemy is standard for Python.

---

## Consequences

### Positive

✅ **Strong ACID guarantees** - Conflict detection works correctly
✅ **Type-safe ORM** - Mypy catches errors
✅ **Async support** - Non-blocking FastAPI
✅ **AI-friendly** - SQLAlchemy is standard, well-documented
✅ **Co-located with backend** - Same platform, lower latency
✅ **Always on** - No shutdown/pause on inactivity
✅ **Simple management** - One platform (Fly.io) for everything
✅ **Cost-effective** - Included in Fly.io free tier
✅ **Advanced features** - Date ranges, GiST indexes

### Negative

⚠️ **Learning curve** (minor) - SQLAlchemy 2.0 syntax (but AI handles)
⚠️ **Async complexity** (minor) - Need to use `await` everywhere

### Neutral

➡️ **Alembic migrations** - Standard, but requires discipline
➡️ **Connection management** - Need to handle session lifecycle
➡️ **Index optimization** - Need to add indexes for performance (but documented)

---

## Implementation Notes

### Database Schema

**Key tables from `docs/specification/data-model.md`:**

```sql
CREATE TABLE bookings (
    id UUID PRIMARY KEY,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days INT NOT NULL,
    party_size INT NOT NULL CHECK (party_size >= 1 AND party_size <= 10),
    description VARCHAR(500),
    requester_first_name VARCHAR(40) NOT NULL,
    requester_email VARCHAR(254) NOT NULL UNIQUE,
    affiliation VARCHAR(20) NOT NULL CHECK (affiliation IN ('Ingeborg', 'Cornelia', 'Angelika')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('Pending', 'Denied', 'Confirmed', 'Canceled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bookings_date_range ON bookings USING GIST (daterange(start_date, end_date, '[]'));
CREATE INDEX idx_bookings_status ON bookings(status);
CREATE INDEX idx_bookings_last_activity ON bookings(last_activity_at DESC);

CREATE TABLE approvals (
    id UUID PRIMARY KEY,
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    party VARCHAR(20) NOT NULL CHECK (party IN ('Ingeborg', 'Cornelia', 'Angelika')),
    decision VARCHAR(20) NOT NULL CHECK (decision IN ('NoResponse', 'Approved', 'Denied')),
    comment VARCHAR(500),
    decided_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(booking_id, party)
);

CREATE INDEX idx_approvals_booking ON approvals(booking_id);
CREATE INDEX idx_approvals_decision ON approvals(decision);

CREATE TABLE timeline_events (
    id UUID PRIMARY KEY,
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    when TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    actor VARCHAR(20) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    note TEXT
);

CREATE INDEX idx_timeline_booking ON timeline_events(booking_id);
CREATE INDEX idx_timeline_when ON timeline_events(when DESC);
```

### SQLAlchemy Models

```python
# app/models/booking.py
from sqlalchemy import String, Integer, Date, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
import enum

class StatusEnum(enum.Enum):
    PENDING = "Pending"
    DENIED = "Denied"
    CONFIRMED = "Confirmed"
    CANCELED = "Canceled"

class AffiliationEnum(enum.Enum):
    INGEBORG = "Ingeborg"
    CORNELIA = "Cornelia"
    ANGELIKA = "Angelika"

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    start_date: Mapped[date]
    end_date: Mapped[date]
    total_days: Mapped[int]
    party_size: Mapped[int]
    description: Mapped[Optional[str]] = mapped_column(String(500))
    requester_first_name: Mapped[str] = mapped_column(String(40))
    requester_email: Mapped[str] = mapped_column(String(254), unique=True, index=True)
    affiliation: Mapped[AffiliationEnum]
    status: Mapped[StatusEnum]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    approvals: Mapped[list["Approval"]] = relationship(back_populates="booking", cascade="all, delete-orphan")
    timeline_events: Mapped[list["TimelineEvent"]] = relationship(back_populates="booking", cascade="all, delete-orphan")
```

### Database Connection

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
```

### Conflict Detection (BR-029)

```python
# app/repositories/booking_repository.py
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError

class BookingRepository:
    async def check_conflicts(
        self,
        start_date: date,
        end_date: date,
        exclude_id: UUID | None = None
    ) -> list[Booking]:
        """Check for overlapping Pending or Confirmed bookings."""
        query = select(Booking).where(
            and_(
                Booking.status.in_([StatusEnum.PENDING, StatusEnum.CONFIRMED]),
                or_(
                    # New booking overlaps existing
                    and_(Booking.start_date <= end_date, Booking.end_date >= start_date),
                ),
            )
        )
        if exclude_id:
            query = query.where(Booking.id != exclude_id)

        result = await self.db.execute(query)
        return result.scalars().all()
```

---

## Validation

### Connection Test

```python
# Test database connection
async with engine.begin() as conn:
    result = await conn.execute(text("SELECT 1"))
    print(result.scalar())  # Should print: 1
```

### Migration Test

```bash
alembic revision --autogenerate -m "Initial schema"
alembic upgrade head
```

**Expected:** Tables created successfully.

### Type Check

```bash
mypy app/models/
```

**Expected:** Zero type errors.

---

## References

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Asyncpg Driver](https://github.com/MagicStack/asyncpg)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Fly.io Postgres Documentation](https://fly.io/docs/postgres/)
- [PostgreSQL Range Types](https://www.postgresql.org/docs/current/rangetypes.html)
- Data Model: `docs/specification/data-model.md`
- Business Rules: `docs/foundation/business-rules.md`

---

## Related ADRs

- [ADR-001: API Framework](adr-001-backend-framework.md) - FastAPI integration
- [ADR-006: Type Safety Strategy](adr-006-type-safety.md) - Mypy validation
- [ADR-007: Deployment Strategy](adr-007-deployment.md) - Fly.io deployment

---

## Changelog

- **2025-01-17:** Initial decision - PostgreSQL + SQLAlchemy 2.0 on Fly.io Postgres
