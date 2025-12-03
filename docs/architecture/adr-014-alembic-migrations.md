# ADR-014: Alembic Migrations

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** Need database migration tool for version-controlled schema changes
**Split from:** ADR-003: Database & ORM

---

## Context

Need database migration tool for PostgreSQL that:
- Tracks schema changes (version control for database)
- Supports forward migrations (apply changes)
- Supports backward migrations (rollback changes)
- Auto-generates from ORM models
- AI-friendly (clear patterns, well-documented)
- Integrates with SQLAlchemy

---

## Decision

Use **Alembic** for database migrations.

---

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Migration Tool | Alembic | Flyway, Django Migrations |
| Migration Generation | Auto-generate from ORM models | Manual SQL writing |
| Migration Reversibility | All migrations have `downgrade()` | Migrations without rollback |
| Migration Version Control | Python files in Git | Database-only tracking |

---

## Rationale

**Why Alembic:**
- Alembic integrates with SQLAlchemy → **Constraint:** MUST use Alembic for database migrations
- Alembic auto-generates migrations from ORM models → **Constraint:** MUST use `alembic revision --autogenerate` for schema changes
- Alembic provides reversible migrations → **Constraint:** MUST include `downgrade()` function in all migrations

**Why NOT Flyway:**
- Flyway requires manual SQL writing → **Violation:** No auto-generation, no ORM awareness, violates AI-friendly requirement

**Why NOT Django Migrations:**
- Django Migrations require Django framework → **Violation:** We use FastAPI, not Django

## Consequences

### MUST (Required)

- MUST use Alembic for database migrations - SQLAlchemy integration, auto-generation from ORM models
- MUST use `alembic revision --autogenerate` for schema changes - Auto-generate migrations from ORM model changes
- MUST include `downgrade()` function in all migrations - Reversible migrations for rollback safety
- MUST review auto-generated migrations before applying - Auto-generated migrations may need manual tweaks

### MUST NOT (Forbidden)

- MUST NOT use Flyway or Django Migrations - Violates SQLAlchemy integration requirement
- MUST NOT skip `downgrade()` function - Violates reversibility requirement
- MUST NOT apply migrations without review - Auto-generated migrations may be incorrect

### Trade-offs

- Auto-generated migrations require review - MUST review generated migration file before applying. MUST check for: column renames (should use `op.alter_column`, not drop+add), data migrations (may need manual `op.execute`), index changes (verify correctness). MUST NOT apply migration if it looks incorrect.
- Downgrade may cause data loss - MUST include `downgrade()` function in all migrations. MUST NOT assume downgrade is safe. MUST check if downgrade drops columns or deletes data.

### Code Examples

```python
# ✅ CORRECT: Auto-generate migration
# Change ORM model
class Booking(Base):
    notes: Mapped[Optional[str]] = mapped_column(Text)  # New field

# Generate migration
# alembic revision --autogenerate -m "Add notes field to bookings"

def upgrade():
    op.add_column('bookings', sa.Column('notes', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('bookings', 'notes')

# ❌ WRONG: Missing downgrade function
def upgrade():
    op.add_column('bookings', sa.Column('notes', sa.Text(), nullable=True))
# No downgrade() - violates reversibility requirement
```

```python
# ✅ CORRECT: Rename column (manual edit required)
def upgrade():
    op.alter_column('bookings', 'party_size', new_column_name='num_guests')

def downgrade():
    op.alter_column('bookings', 'num_guests', new_column_name='party_size')

# ❌ WRONG: Auto-generated rename (loses data)
def upgrade():
    op.drop_column('bookings', 'party_size')
    op.add_column('bookings', sa.Column('num_guests', sa.Integer()))
```

### Applies To

- ALL database schema changes (all phases)
- File patterns: `alembic/versions/*.py`, `alembic/env.py`

### Validation Commands

- `grep -r "def downgrade" alembic/versions/` (all migrations should have downgrade function)
- `grep -r "alembic revision --autogenerate"` (should use auto-generation for schema changes)
- `grep -r "from app.models.base import Base" alembic/env.py` (should import all models for auto-generation)

---

**Related ADRs:**
- [ADR-012](adr-012-postgresql-database.md) - PostgreSQL Database
- [ADR-013](adr-013-sqlalchemy-orm.md) - SQLAlchemy ORM
- [ADR-018](adr-018-github-actions-cicd.md) - GitHub Actions CI/CD

---

## References

**Related ADRs:**
- [ADR-012](adr-012-postgresql-database.md) - PostgreSQL Database
- [ADR-013](adr-013-sqlalchemy-orm.md) - SQLAlchemy ORM
- [ADR-018](adr-018-github-actions-cicd.md) - GitHub Actions CI/CD

**Tools:**
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)

**Implementation:**
- `alembic/env.py` - Alembic configuration
- `alembic/versions/` - Migration files
