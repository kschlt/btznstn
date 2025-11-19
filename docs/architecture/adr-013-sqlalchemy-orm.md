# ADR-013: SQLAlchemy ORM

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)
**Split from:** [ADR-003: Database & ORM](adr-003-database-orm.md)

---

## Context

We need to choose an Object-Relational Mapping (ORM) tool for Python to interact with PostgreSQL. The ORM must:

- Map Python classes to database tables
- Support async/await (FastAPI is async)
- Provide type hints (for mypy validation)
- Be AI-friendly (well-documented, popular)
- Support complex queries (joins, filtering, sorting)

### Requirements

**From ADR-006 (Type Safety):**
- Python type hints on all models
- Mypy strict mode compatibility
- Pydantic integration for validation

**From ADR-001 (FastAPI):**
- Async support (FastAPI uses async/await)
- Integration with FastAPI dependency injection

---

## Decision

We will use **SQLAlchemy 2.0** as the ORM, specifically:
- **SQLAlchemy Core 2.0** for async engine/sessions
- **SQLAlchemy ORM 2.0** for declarative models
- **Type hints** with `Mapped[]` annotations

---

## Rationale

### 1. SQLAlchemy 2.0 (Modern, Type-Safe)

**Why 2.0 matters:** Complete rewrite with type hints, async-first.

**Key features:**
- ✅ **Type hints** - `Mapped[int]`, `Mapped[str | None]` for all columns
- ✅ **Async/await** - Native async support (`AsyncEngine`, `AsyncSession`)
- ✅ **Mypy plugin** - Static type checking for ORM queries
- ✅ **Pydantic integration** - Convert ORM models ↔ Pydantic models

**Example (type-safe model):**
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from typing import Optional
from datetime import date

class Base(DeclarativeBase):
    pass

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    requester_first_name: Mapped[str] = mapped_column(String(40))
    start_date: Mapped[date]
    end_date: Mapped[date]
    party_size: Mapped[int]
    description: Mapped[Optional[str]]  # Nullable

    # Mypy knows:
    # - id is int
    # - requester_first_name is str
    # - description is str | None
```

**AI benefit:** Type hints guide AI toward correct implementations.

### 2. Async Support (Critical for FastAPI)

**FastAPI is async** - ORM must be async-compatible.

**SQLAlchemy 2.0 async:**
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

# Create async engine
engine = create_async_engine("postgresql+asyncpg://...")

# Use async session
async with AsyncSession(engine) as session:
    result = await session.execute(
        select(Booking).where(Booking.status == "Pending")
    )
    bookings = result.scalars().all()
```

**Why async matters:**
- ✅ **Non-blocking I/O** - FastAPI can handle multiple requests concurrently
- ✅ **Better performance** - Doesn't block event loop
- ✅ **Standard pattern** - Matches FastAPI request handlers

**Alternative (sync SQLAlchemy in async FastAPI):**
```python
# BAD: Blocks event loop
def get_bookings():  # Sync function
    session = Session(engine)  # Sync session
    return session.query(Booking).all()  # Blocks!
```

**AI benefit:** Async/await is standard Python pattern, AI knows it well.

### 3. Declarative Models (AI-Friendly)

**Declarative style:**
```python
class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    start_date: Mapped[date]
    end_date: Mapped[date]
```

**Why declarative:**
- ✅ **Clear structure** - Class defines table schema
- ✅ **Type hints** - Mapped[] shows types
- ✅ **Relationships** - `relationship()` for foreign keys
- ✅ **AI-friendly** - Standard ORM pattern

**Alternative (imperative style - old SQLAlchemy):**
```python
# OLD WAY (pre-2.0)
bookings = Table('bookings', metadata,
    Column('id', Integer, primary_key=True),
    Column('start_date', Date),
    Column('end_date', Date),
)
# Harder for AI to work with
```

### 4. Pydantic Integration

**Convert ORM ↔ Pydantic:**
```python
# ORM model
class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(primary_key=True)
    requester_first_name: Mapped[str]
    # ...

# Pydantic model (for API responses)
class BookingResponse(BaseModel):
    id: int
    requester_first_name: str
    # ...

    model_config = ConfigDict(from_attributes=True)

# Convert ORM → Pydantic
booking_orm = await session.get(Booking, booking_id)
booking_response = BookingResponse.from_orm(booking_orm)
```

**AI benefit:** Single source of truth for data structure.

### 5. Complex Query Support

**SQLAlchemy query capabilities:**
- ✅ **Joins** - Foreign key relationships
- ✅ **Filtering** - `where()`, `filter()`
- ✅ **Sorting** - `order_by()`
- ✅ **Pagination** - `limit()`, `offset()`
- ✅ **Aggregation** - `count()`, `group_by()`
- ✅ **Raw SQL** - When needed (e.g., GiST index queries)

**Example (complex query):**
```python
# Get outstanding approvals for approver
result = await session.execute(
    select(Approval)
    .join(Booking)
    .where(Approval.party_id == party_id)
    .where(Approval.response == "NoResponse")
    .where(Booking.status == "Pending")
    .order_by(Booking.created_at.desc())
)
approvals = result.scalars().all()
```

**AI benefit:** Composable queries, AI can build complex filters incrementally.

### 6. Mypy Plugin (Type Safety)

**SQLAlchemy mypy plugin:**
```ini
# mypy.ini
[mypy]
plugins = sqlalchemy.ext.mypy.plugin
```

**What it catches:**
```python
# Mypy error: "Booking" has no attribute "invalid_field"
booking.invalid_field = "value"

# Mypy error: Incompatible type (str vs int)
booking.party_size = "five"  # party_size is Mapped[int]
```

**AI benefit:** AI errors caught at type-check time.

---

## Alternatives Considered

### Django ORM

**Pros:**
- Mature
- Good documentation
- Active Record pattern

**Cons:**
- ❌ **Requires Django** - We're using FastAPI, not Django
- ❌ **Sync only** - No native async support
- ❌ **Less type-safe** - No Mapped[] type hints
- ❌ **Tightly coupled** - Hard to use outside Django

**Decision:** SQLAlchemy is FastAPI-native, async-first.

---

### Tortoise ORM

**Pros:**
- Async-first
- FastAPI examples
- Simple API

**Cons:**
- ❌ **Less mature** - Newer project
- ❌ **Smaller community** - Less AI training data
- ❌ **Fewer features** - No range types, limited query builder
- ❌ **Less migration tooling** - Aerich less mature than Alembic

**Decision:** SQLAlchemy more mature, better AI knowledge.

---

### Peewee

**Pros:**
- Simple
- Lightweight
- Easy to learn

**Cons:**
- ❌ **Sync only** - No async support
- ❌ **No type hints** - Not mypy-compatible
- ❌ **Smaller community** - Less AI training data

**Decision:** SQLAlchemy async + type hints critical for project.

---

### Raw SQL (No ORM)

**Pros:**
- Full control
- No abstraction
- Fastest

**Cons:**
- ❌ **Manual mapping** - Dict → Python class
- ❌ **SQL injection risk** - Must sanitize manually
- ❌ **Boilerplate** - Write CRUD for every model
- ❌ **No type safety** - Mypy can't check SQL strings

**Decision:** ORM reduces boilerplate, AI can generate ORM code easily.

---

## Consequences

### Positive

✅ **Type-safe** - Mapped[] type hints + mypy plugin
✅ **Async/await** - Native async support for FastAPI
✅ **AI-friendly** - SQLAlchemy is industry standard
✅ **Pydantic integration** - ORM ↔ API models
✅ **Complex queries** - Composable query builder
✅ **Mature** - 15+ years, v2.0 is modern rewrite
✅ **Migration tooling** - Alembic (see ADR-014)

### Negative

⚠️ **Learning curve** - SQLAlchemy is powerful but complex
⚠️ **Verbose** - More code than ActiveRecord-style ORMs
⚠️ **Magic** - Declarative models use metaclasses (but AI handles this well)

### Neutral

➡️ **Version 2.0 required** - Type hints only in 2.0+
➡️ **Async driver** - Requires asyncpg (PostgreSQL async driver)

---

## Implementation Notes

### Installation

```bash
pip install sqlalchemy[asyncio]>=2.0.25
pip install asyncpg>=0.29.0  # PostgreSQL async driver
```

### Base Model

```python
# app/models/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

### Example Model

```python
# app/models/booking.py
from sqlalchemy import String, Integer, Date, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import date
from typing import Optional
from app.models.base import Base
from app.models.enums import StatusEnum, AffiliationEnum

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    requester_first_name: Mapped[str] = mapped_column(String(40))
    requester_email: Mapped[str] = mapped_column(String(255))
    start_date: Mapped[date]
    end_date: Mapped[date]
    total_days: Mapped[int]
    party_size: Mapped[int]
    affiliation: Mapped[AffiliationEnum] = mapped_column(Enum(AffiliationEnum))
    description: Mapped[Optional[str]]
    status: Mapped[StatusEnum] = mapped_column(Enum(StatusEnum), default=StatusEnum.PENDING)

    # Relationships
    approvals: Mapped[list["Approval"]] = relationship(back_populates="booking")
```

### Async Engine & Session

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncSession:
    """Dependency for FastAPI endpoints."""
    async with AsyncSessionLocal() as session:
        yield session
```

### Repository Pattern

```python
# app/repositories/booking_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.booking import Booking

class BookingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, booking_id: int) -> Booking | None:
        result = await self.session.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        return result.scalar_one_or_none()

    async def create(self, booking: Booking) -> Booking:
        self.session.add(booking)
        await self.session.flush()
        await self.session.refresh(booking)
        return booking
```

### FastAPI Endpoint

```python
# app/routes/bookings.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.repositories.booking_repository import BookingRepository
from app.schemas.booking import BookingResponse

router = APIRouter()

@router.get("/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
):
    repo = BookingRepository(db)
    booking = await repo.get_by_id(booking_id)
    if not booking:
        raise HTTPException(404, "Booking not found")
    return booking
```

---

## Validation

### Verify Type Hints

```bash
# Run mypy with SQLAlchemy plugin
mypy app/
# Expected: No errors if types correct
```

### Verify Async Works

```python
# Test async session
async def test():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Booking))
        bookings = result.scalars().all()
        print(f"Found {len(bookings)} bookings")

import asyncio
asyncio.run(test())
```

---

## References

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [SQLAlchemy Mypy Plugin](https://docs.sqlalchemy.org/en/20/orm/extensions/mypy.html)
- [FastAPI with SQLAlchemy](https://fastapi.tiangolo.com/tutorial/sql-databases/)

**Related ADRs:**
- [ADR-001: API Framework](adr-001-backend-framework.md) - FastAPI async integration
- [ADR-006: Type Safety Strategy](adr-006-type-safety.md) - Mypy + type hints
- [ADR-012: PostgreSQL Database](adr-012-postgresql-database.md) - Database choice
- [ADR-014: Alembic Migrations](adr-014-alembic-migrations.md) - Schema migrations

---

## Changelog

- **2025-01-19:** Split from ADR-003 - SQLAlchemy ORM choice as independent decision
