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

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| ORM Version | SQLAlchemy 2.0+ | SQLAlchemy 1.x |
| Database Sessions | `AsyncSession` | Sync `Session` |
| Model Columns | `Mapped[type]` annotations | Untyped columns |
| Database URL | `postgresql+asyncpg://` | `postgresql://` |
| Database Engine | `create_async_engine` | `create_engine` |

---

## Rationale

**Why SQLAlchemy 2.0:**
- SQLAlchemy 2.0 provides type hints (`Mapped[]`) → **Constraint:** MUST use SQLAlchemy 2.0+ with `Mapped[type]` annotations for all columns
- SQLAlchemy 2.0 provides native async support → **Constraint:** MUST use `AsyncSession` and `create_async_engine` for all database operations
- SQLAlchemy 2.0 integrates with FastAPI → **Constraint:** MUST use async patterns compatible with FastAPI

**Why NOT Django ORM:**
- Django ORM requires Django framework → **Violation:** We use FastAPI, not Django
- Django ORM is sync-only → **Violation:** Violates async requirement, blocks FastAPI event loop

**Why NOT Tortoise ORM:**
- Tortoise ORM has less AI training data → **Violation:** Smaller community, less AI support, fewer features

## Consequences

### MUST (Required)

- MUST use SQLAlchemy 2.0+ - Type hints (`Mapped[]`) only available in 2.0+
- MUST use `AsyncSession` for all database operations - Async operations required for FastAPI compatibility
- MUST use `Mapped[type]` annotations for all model columns - Type safety requirement
- MUST use `create_async_engine` for database engines - Async requirement
- MUST use `postgresql+asyncpg://` database URL - Requires asyncpg driver for async PostgreSQL
- MUST enable Mypy plugin (`sqlalchemy.ext.mypy.plugin`) - Static type checking for queries
- MUST use `from_attributes=True` in Pydantic models - ORM to Pydantic conversion

### MUST NOT (Forbidden)

- MUST NOT use sync `Session` - Blocks FastAPI event loop
- MUST NOT use sync `create_engine` - Violates async requirement
- MUST NOT use `postgresql://` URL - Missing asyncpg driver
- MUST NOT skip `Mapped[]` annotations - Defeats type safety
- MUST NOT use SQLAlchemy 1.x patterns - Violates SQLAlchemy 2.0 decision
- MUST NOT mix sync and async sessions - Causes blocking

### Trade-offs

- All database operations must be async - MUST use `AsyncSession`. MUST NOT use sync sessions. Check for sync session usage.
- Type annotations required - MUST use `Mapped[type]` for all columns. MUST NOT use untyped columns. More verbose but provides type safety.

### Code Examples

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import select

# ✅ CORRECT: Base model
class Base(DeclarativeBase):
    pass

# ✅ CORRECT: Type-annotated model
class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(primary_key=True)
    requester_first_name: Mapped[str] = mapped_column(String(40))
    description: Mapped[str | None]  # Nullable

# ✅ CORRECT: Async engine
engine = create_async_engine("postgresql+asyncpg://...")

# ✅ CORRECT: Async session
async with AsyncSession(engine) as session:
    result = await session.execute(
        select(Booking).where(Booking.status == StatusEnum.PENDING)
    )
    bookings = result.scalars().all()

# ❌ WRONG: Sync session (blocks event loop)
from sqlalchemy.orm import Session
with Session(bind=engine) as session:  # Blocks FastAPI!
    bookings = session.query(Booking).all()

# ❌ WRONG: Wrong database URL
engine = create_async_engine("postgresql://...")  # Missing +asyncpg!

# ❌ WRONG: Untyped columns
class Booking(Base):
    id = Column(Integer, primary_key=True)  # No Mapped[] annotation!
```

### Applies To

- ALL database models (all phases)
- ALL repositories (all phases)
- ALL database operations (all phases)
- File patterns: `app/models/**/*.py`, `app/repositories/**/*.py`, `app/core/database.py`

### Validation Commands

- `grep -r "from sqlalchemy.orm import Session" app/` (should be empty - must use AsyncSession)
- `grep -r "AsyncSession" app/repositories/` (should be present - all repositories use async)
- `grep -r "Mapped\[" app/models/` (all columns should have - type annotations required)
- `grep -r "postgresql+asyncpg" app/core/` (should be present - correct URL format)
- `grep -r "sqlalchemy.ext.mypy.plugin" mypy.ini` (should be present - Mypy plugin enabled)

---

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - Backend Framework
- [ADR-006](adr-006-type-safety.md) - Type Safety Strategy
- [ADR-012](adr-012-postgresql-database.md) - PostgreSQL Database
- [ADR-014](adr-014-alembic-migrations.md) - Alembic Migrations

---

## References

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - Backend Framework
- [ADR-006](adr-006-type-safety.md) - Type Safety Strategy
- [ADR-012](adr-012-postgresql-database.md) - PostgreSQL Database
- [ADR-014](adr-014-alembic-migrations.md) - Alembic Migrations

**Tools:**
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Mypy Plugin](https://docs.sqlalchemy.org/en/20/orm/extensions/mypy.html)

**Implementation:**
- `app/models/base.py` - Base model
- `app/core/database.py` - Async engine and session
- `app/repositories/` - Repository pattern
