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

### Implementation Constraints

✅ **SQLAlchemy 2.0 REQUIRED** - Type hints (`Mapped[]`) only available in 2.0+
✅ **Async operations REQUIRED** - ALL database operations use `AsyncSession` (not sync sessions)
✅ **Type annotations REQUIRED** - ALL model columns use `Mapped[type]` annotations
✅ **Mypy plugin REQUIRED** - Static type checking enabled for queries
✅ **asyncpg driver REQUIRED** - PostgreSQL async driver (not psycopg2)
✅ **Pydantic integration** - ORM models convert to/from Pydantic models

### Complexity Trade-offs

⚠️ **ALL database operations MUST be async** - Using sync sessions blocks FastAPI event loop
⚠️ **Type annotations required** - All columns must use `Mapped[type]` (more verbose than untyped)
⚠️ **SQLAlchemy 2.0+ required** - Cannot use older versions (type hints only in 2.0+)

### Neutral

➡️ **asyncpg dependency** - Required for async PostgreSQL operations (not part of SQLAlchemy core)

---

## LLM Implementation Constraints

### Required Patterns

**MUST:**
- ALL database models inherit from `DeclarativeBase` (SQLAlchemy 2.0 style)
- ALL model columns use `Mapped[type]` annotations (not untyped columns)
- ALL database sessions use `AsyncSession` (not sync `Session`)
- ALL database operations use `await` (queries, commits, rollbacks)
- ALL database engines use `create_async_engine` (not `create_engine`)
- ALL database URLs use `postgresql+asyncpg://` (not `postgresql://`)
- ALL repositories use `AsyncSession` parameter (not sync session)
- Mypy plugin enabled (`plugins = sqlalchemy.ext.mypy.plugin` in mypy.ini)
- Pydantic models use `from_attributes=True` for ORM conversion

**MUST NOT:**
- Use sync `Session` (blocks FastAPI event loop)
- Use sync `create_engine` (violates async requirement)
- Use `postgresql://` URL (requires asyncpg driver)
- Skip `Mapped[]` annotations (defeats type safety)
- Use SQLAlchemy 1.x patterns (violates ADR-013 decision)
- Mix sync and async sessions (causes blocking)

**Example - Correct Pattern:**
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

# ✅ CORRECT: Base model
class Base(DeclarativeBase):
    pass

# ✅ CORRECT: Type-annotated model
class Booking(Base):
    __tablename__ = "bookings"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    requester_first_name: Mapped[str] = mapped_column(String(40))
    start_date: Mapped[date]
    description: Mapped[str | None]  # ✅ Nullable

# ✅ CORRECT: Async engine
engine = create_async_engine("postgresql+asyncpg://...")

# ✅ CORRECT: Async session
async with AsyncSession(engine) as session:
    result = await session.execute(
        select(Booking).where(Booking.status == StatusEnum.PENDING)
    )
    bookings = result.scalars().all()
```

**Example - WRONG (Anti-patterns):**
```python
# ❌ WRONG: Sync session (blocks event loop)
from sqlalchemy.orm import Session, sessionmaker

SessionLocal = sessionmaker(bind=engine)  # Sync!
with SessionLocal() as session:  # Blocks FastAPI!
    bookings = session.query(Booking).all()

# ❌ WRONG: Sync engine
from sqlalchemy import create_engine

engine = create_engine("postgresql://...")  # Sync!

# ❌ WRONG: Wrong database URL
engine = create_async_engine("postgresql://...")  # Missing +asyncpg!

# ❌ WRONG: Untyped columns
class Booking(Base):
    id = Column(Integer, primary_key=True)  # No Mapped[] annotation!

# ❌ WRONG: Mixing sync/async
async def get_booking(session: AsyncSession):
    sync_session = Session(bind=engine)  # Mixing sync/async!
    return sync_session.query(Booking).first()
```

### Applies To

**This constraint affects:**
- ALL database models (all phases)
- ALL repositories (all phases)
- ALL database operations (all phases)
- User story specifications must require async patterns
- Acceptance criteria must validate async session usage

### When Writing User Stories

**Ensure specifications include:**
- Models use `Mapped[type]` annotations for all columns
- Database operations use `AsyncSession` (not sync `Session`)
- Database URLs use `postgresql+asyncpg://` protocol
- All queries use `await session.execute()` pattern
- Mypy plugin enabled for type checking

**Validation commands for user story checklists:**
- No sync sessions: `grep -r "from sqlalchemy.orm import Session" app/` (should be empty)
- All async: `grep -r "AsyncSession" app/repositories/` (should be present)
- Type annotations: `grep -r "Mapped\[" app/models/` (all columns should have)
- Correct URL: `grep -r "postgresql+asyncpg" app/core/` (should be present)
- Mypy plugin: `grep -r "sqlalchemy.ext.mypy.plugin" mypy.ini` (should be present)

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - FastAPI async requirement
- [ADR-006](adr-006-type-safety.md) - Type hints required
- [ADR-012](adr-012-postgresql-database.md) - PostgreSQL database choice
- [ADR-014](adr-014-alembic-migrations.md) - Alembic migrations

**Related Specifications:**
- Database models: `api/app/models/`
- Repositories: `api/app/repositories/`
- Database config: `api/app/core/database.py`

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
