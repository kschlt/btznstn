# ADR-013: SQLAlchemy ORM

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** Need async-compatible ORM with type safety for AI-driven development
**Split from:** ADR-003: Database & ORM

---

## Context

Need Object-Relational Mapping (ORM) tool for Python + PostgreSQL that:
- Maps Python classes to database tables
- Supports async/await (FastAPI is async)
- Provides type hints (mypy validation)
- AI-friendly (well-documented, popular)
- Pydantic integration (API models)

---

## Decision

Use **SQLAlchemy 2.0** with:
- Async engine/sessions (`AsyncEngine`, `AsyncSession`)
- Type-safe declarative models (`Mapped[]` annotations)
- Mypy plugin for static type checking

---

## Rationale

### Why SQLAlchemy 2.0 vs Django ORM vs Tortoise ORM?

**SQLAlchemy 2.0 (Chosen):**
- ✅ **Type hints** - `Mapped[int]`, `Mapped[str | None]` for all columns
- ✅ **Async/await** - Native async (`AsyncEngine`, `AsyncSession`)
- ✅ **Mypy plugin** - Static type checking for queries
- ✅ **Pydantic integration** - Convert ORM ↔ Pydantic models
- ✅ **FastAPI-native** - Standard for FastAPI apps
- ✅ **Massive AI training data** - Industry standard, AI knows it well

**Django ORM (Rejected):**
- ❌ Requires Django (we're using FastAPI)
- ❌ Sync only (no async)
- ❌ No `Mapped[]` type hints

**Tortoise ORM (Rejected):**
- ❌ Less mature
- ❌ Smaller community (less AI training data)
- ❌ Fewer features (no range types, limited query builder)

---

## Key SQLAlchemy 2.0 Features

### 1. Type-Safe Models

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    requester_first_name: Mapped[str] = mapped_column(String(40))
    start_date: Mapped[date]
    description: Mapped[Optional[str]]  # Nullable

    # Mypy knows:
    # - id is int
    # - requester_first_name is str
    # - description is str | None
```

### 2. Async Support (FastAPI Compatibility)

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
- Non-blocking I/O (FastAPI can handle concurrent requests)
- Better performance
- Standard Python pattern (AI knows it well)

### 3. Pydantic Integration

```python
# ORM model
class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(primary_key=True)
    requester_first_name: Mapped[str]

# Pydantic model (API response)
class BookingResponse(BaseModel):
    id: int
    requester_first_name: str

    model_config = ConfigDict(from_attributes=True)

# Convert ORM → Pydantic
booking_orm = await session.get(Booking, booking_id)
booking_response = BookingResponse.from_orm(booking_orm)
```

### 4. Mypy Plugin (Type Safety)

```ini
# mypy.ini
[mypy]
plugins = sqlalchemy.ext.mypy.plugin
```

**Catches errors:**
```python
# Mypy error: "Booking" has no attribute "invalid_field"
booking.invalid_field = "value"

# Mypy error: Incompatible type (str vs int)
booking.party_size = "five"  # party_size is Mapped[int]
```

---

## Consequences

### Positive

✅ **Type-safe** - Mapped[] type hints + mypy plugin
✅ **Async/await** - Native async for FastAPI
✅ **AI-friendly** - Industry standard, massive training data
✅ **Pydantic integration** - Single source of truth
✅ **Complex queries** - Composable query builder (joins, filtering, sorting)
✅ **Mature** - 15+ years, v2.0 is modern rewrite
✅ **Migration tooling** - Alembic (see ADR-014)

### Negative

⚠️ **Learning curve** - Powerful but complex
⚠️ **Verbose** - More code than ActiveRecord-style ORMs

### Neutral

➡️ **Version 2.0 required** - Type hints only in 2.0+
➡️ **Async driver** - Requires asyncpg (PostgreSQL async driver)

---

## Implementation Pattern

### Base Model

```python
# app/models/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

### Async Engine & Session

```python
# app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

async def get_db():
    """Dependency for FastAPI endpoints."""
    async with AsyncSessionLocal() as session:
        yield session
```

### Repository Pattern

```python
# app/repositories/booking_repository.py
from sqlalchemy import select

class BookingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, booking_id: int) -> Booking | None:
        result = await self.session.execute(
            select(Booking).where(Booking.id == booking_id)
        )
        return result.scalar_one_or_none()
```

### FastAPI Endpoint

```python
# app/routes/bookings.py
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

## References

**Related ADRs:**
- ADR-001: Backend Framework (FastAPI async integration)
- ADR-006: Type Safety Strategy (Mypy + type hints)
- ADR-012: PostgreSQL Database (database choice)
- ADR-014: Alembic Migrations (schema migrations)

**Tools:**
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Mypy Plugin](https://docs.sqlalchemy.org/en/20/orm/extensions/mypy.html)
