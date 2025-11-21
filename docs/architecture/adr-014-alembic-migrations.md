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

## Rationale

### Why Alembic vs Flyway vs Django Migrations?

**Alembic (Chosen):**
- ✅ **SQLAlchemy integration** - Built by SQLAlchemy team
- ✅ **Auto-generation** - Compare ORM models to database, generate migration
- ✅ **Reversible** - Every migration has `upgrade()` and `downgrade()`
- ✅ **Version-controlled** - Python files in Git
- ✅ **Incremental** - Apply one migration at a time
- ✅ **SQL generation** - Review SQL before apply (`--sql` flag)

**Flyway (Rejected):**
- ❌ No auto-generation (must write SQL manually)
- ❌ No ORM awareness
- ❌ Java-based (extra dependency)

**Django Migrations (Rejected):**
- ❌ Requires Django (we're using FastAPI)
- ❌ Tightly coupled to Django

---

## Key Alembic Features

### 1. Auto-Generation from ORM

```bash
# Change ORM model
class Booking(Base):
    notes: Mapped[Optional[str]] = mapped_column(Text)  # New field

# Auto-generate migration
alembic revision --autogenerate -m "Add notes field to bookings"
```

**Generated migration:**
```python
# alembic/versions/001_add_notes_field.py
def upgrade():
    op.add_column('bookings', sa.Column('notes', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('bookings', 'notes')
```

AI changes ORM model → Alembic generates migration → AI reviews.

### 2. Reversible Migrations (Rollback Safety)

**Every migration has both directions:**
```python
def upgrade():
    op.create_index('ix_bookings_status', 'bookings', ['status'])

def downgrade():
    op.drop_index('ix_bookings_status', table_name='bookings')
```

**Why reversibility:**
- Rollback on failure
- Test in staging (apply → test → rollback)
- Safe deployments

### 3. Version Control (Git-Tracked)

**Migrations are Python files:**
```
alembic/
├── versions/
│   ├── 001_create_bookings_table.py
│   ├── 002_create_approvals_table.py
│   ├── 003_add_timeline_events.py
│   └── 004_add_gist_index.py
├── env.py
└── script.py.mako
```

**Benefits:**
- See schema changes over time
- Code review migrations in PRs
- Reproducible across environments

### 4. Incremental Application

```bash
# Check current version
alembic current
# Output: 003_add_timeline_events (head)

# Apply pending migrations
alembic upgrade head
# Applies: 004_add_gist_index
```

Small, focused changes. Test incrementally.

---

## Common Migration Patterns

### Safe: Add Nullable Column

```python
def upgrade():
    op.add_column('bookings', sa.Column('notes', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('bookings', 'notes')
```

### Unsafe: Add Non-Nullable (Two Migrations Required)

```python
# Migration 1: Add nullable
def upgrade():
    op.add_column('bookings', sa.Column('priority', sa.Integer(), nullable=True))

# Migration 2: Populate + make non-nullable
def upgrade():
    op.execute("UPDATE bookings SET priority = 1 WHERE priority IS NULL")
    op.alter_column('bookings', 'priority', nullable=False)
```

### Rename Column (Manual Edit Required)

```python
# Auto-generated (WRONG - loses data):
def upgrade():
    op.drop_column('bookings', 'party_size')
    op.add_column('bookings', sa.Column('num_guests', sa.Integer()))

# Correct (manual edit):
def upgrade():
    op.alter_column('bookings', 'party_size', new_column_name='num_guests')
```

---

## Consequences

### Positive

✅ **Auto-generation** - Compare ORM → database, generate migration
✅ **Reversible** - Every migration has downgrade()
✅ **Version-controlled** - Migrations in Git
✅ **SQLAlchemy integration** - Uses SQLAlchemy operations
✅ **Incremental** - Apply one migration at a time
✅ **SQL generation** - Review before apply (`--sql`)

### Negative

⚠️ **Manual review required** - Auto-generated migrations may need tweaks
⚠️ **Downgrade not always safe** - Dropping columns loses data
⚠️ **Learning curve** - Must understand migration patterns

### Neutral

➡️ **Python files** - Migrations are Python scripts (flexible but can be complex)
➡️ **Sequential** - Must apply in order (can't skip)

---

## Implementation Pattern

### Installation

```bash
pip install alembic>=1.13.0

# Initialize
alembic init alembic
```

### Configure Alembic

```python
# alembic/env.py
from app.models.base import Base  # Import all models
from app.core.config import settings

# Set SQLAlchemy metadata
target_metadata = Base.metadata

# Set database URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

### Create Migration

```bash
# Auto-generate from ORM changes
alembic revision --autogenerate -m "Create bookings table"

# Manual migration
alembic revision -m "Add custom index"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Check current version
alembic current
```

### CI/CD Integration

```yaml
# .github/workflows/deploy-backend.yml
- name: Run migrations
  run: alembic upgrade head
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

---

## References

**Related ADRs:**
- ADR-012: PostgreSQL Database (database choice)
- ADR-013: SQLAlchemy ORM (ORM integration)
- ADR-018: GitHub Actions CI/CD (deployment integration)

**Tools:**
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
