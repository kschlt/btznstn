# ADR-014: Alembic Migrations

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)
**Split from:** [ADR-003: Database & ORM](adr-003-database-orm.md)

---

## Context

We need a database migration tool to manage schema changes for PostgreSQL. The tool must:

- Track schema changes over time (version control for database)
- Support forward migrations (apply changes)
- Support backward migrations (rollback changes)
- Auto-generate migrations from ORM models
- Be AI-friendly (clear patterns, well-documented)
- Integrate with SQLAlchemy

### Requirements

**From development workflow:**
- Migrations run before deployment (CI/CD)
- Migrations are reversible (rollback on failure)
- Migrations are version-controlled (Git)
- Schema changes are incremental

---

## Decision

We will use **Alembic** for database migrations.

---

## Rationale

### 1. SQLAlchemy Integration (Perfect Match)

**Alembic is built by SQLAlchemy team** - Native integration.

**Key benefits:**
- ✅ **Auto-generation** - Compare ORM models to database, generate migration script
- ✅ **Type-safe** - Uses SQLAlchemy operations (`op.create_table()`, etc.)
- ✅ **Metadata awareness** - Knows about SQLAlchemy models

**Example (auto-generate migration):**
```bash
# Change ORM model
class Booking(Base):
    # Add new field
    notes: Mapped[Optional[str]] = mapped_column(Text)

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

**AI benefit:** AI changes ORM model → Alembic generates migration → AI reviews.

### 2. Reversible Migrations (Critical for Safety)

**Every migration has `upgrade()` and `downgrade()`.**

**Example (add index):**
```python
def upgrade():
    op.create_index('ix_bookings_status', 'bookings', ['status'])

def downgrade():
    op.drop_index('ix_bookings_status', table_name='bookings')
```

**Why reversibility matters:**
- ✅ **Rollback on failure** - If migration breaks, rollback
- ✅ **Test in staging** - Apply → test → rollback if issues
- ✅ **Safe deployments** - Can undo changes

**Best practice:** Always test `downgrade()` before production.

### 3. Version Control (Git-Tracked)

**Migrations are Python files** - Committed to Git.

**Benefits:**
- ✅ **History** - See schema changes over time
- ✅ **Code review** - Migrations reviewed in PRs
- ✅ **Reproducible** - Same migrations on all environments

**Example structure:**
```
alembic/
├── versions/
│   ├── 001_create_bookings_table.py
│   ├── 002_create_approvals_table.py
│   ├── 003_add_timeline_events.py
│   └── 004_add_gist_index.py
├── env.py  # Alembic environment config
└── script.py.mako  # Migration template
```

**AI benefit:** AI can see migration history, understand schema evolution.

### 4. Incremental Migrations (Safe Schema Changes)

**Alembic applies migrations sequentially.**

**Example (current schema version):**
```bash
alembic current
# Output: 003_add_timeline_events (head)
```

**Apply pending migrations:**
```bash
alembic upgrade head
# Applies: 004_add_gist_index
```

**Incremental benefits:**
- ✅ **Small changes** - Each migration is focused
- ✅ **Easy to reason about** - One change at a time
- ✅ **Test incrementally** - Apply one, test, apply next

### 5. Branching Support (Parallel Development)

**Multiple developers can create migrations** - Alembic merges.

**Scenario:**
- Developer A: Creates migration 004 (adds field)
- Developer B: Creates migration 004 (adds index)
- **Conflict:** Two migrations with same revision number

**Alembic solution:**
```bash
# Detect branch
alembic heads
# Output: 004a, 004b (two heads)

# Merge branches
alembic merge -m "Merge parallel migrations"
# Creates: 005_merge_004a_004b
```

**AI benefit:** AI can detect and resolve migration conflicts.

### 6. Offline SQL Generation (Review Before Apply)

**Generate SQL without applying:**
```bash
alembic upgrade head --sql > migration.sql
```

**Use cases:**
- ✅ **Review SQL** - See exactly what will run
- ✅ **Manual execution** - DBA applies manually (if needed)
- ✅ **Audit trail** - Record of SQL executed

**Example output:**
```sql
-- Running upgrade -> 004
CREATE INDEX ix_bookings_status ON bookings (status);
```

---

## Alternatives Considered

### Django Migrations

**Pros:**
- Mature
- Good tooling
- Auto-detection

**Cons:**
- ❌ **Requires Django** - We're using FastAPI
- ❌ **Tightly coupled** - Hard to use without Django
- ❌ **No SQLAlchemy integration**

**Decision:** Alembic is FastAPI/SQLAlchemy-native.

---

### Flyway

**Pros:**
- Simple (SQL files)
- Language-agnostic
- Versioned SQL

**Cons:**
- ❌ **No auto-generation** - Must write SQL manually
- ❌ **No ORM awareness** - Doesn't know about SQLAlchemy models
- ❌ **Java-based** - Extra dependency

**Decision:** Alembic auto-generates from ORM models (less manual work).

---

### Liquibase

**Pros:**
- XML/JSON/SQL formats
- Database-agnostic
- Enterprise features

**Cons:**
- ❌ **Complex** - XML configuration
- ❌ **No Python integration**
- ❌ **Overkill** - Enterprise features not needed

**Decision:** Alembic simpler, Python-native.

---

### Manual SQL Scripts

**Approach:**
```
migrations/
├── 001_create_tables.sql
├── 002_add_indexes.sql
└── 003_add_column.sql
```

**Pros:**
- Simple
- No tool needed
- Full SQL control

**Cons:**
- ❌ **No versioning** - Must track manually
- ❌ **No rollback** - Must write down migrations separately
- ❌ **Error-prone** - Manual schema tracking

**Decision:** Alembic handles versioning, rollback automatically.

---

## Consequences

### Positive

✅ **Auto-generation** - Compare ORM → database, generate migration
✅ **Reversible** - Every migration has downgrade()
✅ **Version-controlled** - Migrations in Git
✅ **SQLAlchemy integration** - Uses SQLAlchemy operations
✅ **Incremental** - Apply one migration at a time
✅ **Branching support** - Merge parallel migrations
✅ **SQL generation** - Review before apply

### Negative

⚠️ **Manual review required** - Auto-generated migrations may need tweaks
⚠️ **Downgrade not always safe** - Dropping columns loses data
⚠️ **Learning curve** - Must understand migration patterns

### Neutral

➡️ **Python files** - Migrations are Python scripts (pro: flexible, con: can be complex)
➡️ **Sequential versions** - Must apply in order (can't skip)

---

## Implementation Notes

### Installation

```bash
pip install alembic>=1.13.0
```

### Initialize Alembic

```bash
# Create alembic directory structure
alembic init alembic
```

**Creates:**
```
alembic/
├── versions/  # Migration scripts go here
├── env.py  # Environment configuration
└── script.py.mako  # Migration template

alembic.ini  # Alembic configuration
```

### Configure Alembic

**Edit `alembic/env.py`:**
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

**Auto-generate from ORM changes:**
```bash
alembic revision --autogenerate -m "Create bookings table"
```

**Manual migration:**
```bash
alembic revision -m "Add custom index"
```

**Generated file:**
```python
# alembic/versions/001_create_bookings_table.py
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('requester_first_name', sa.String(length=40), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        # ...
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_bookings_status', 'bookings', ['status'])

def downgrade():
    op.drop_index('ix_bookings_status', table_name='bookings')
    op.drop_table('bookings')
```

### Apply Migrations

**Upgrade to latest:**
```bash
alembic upgrade head
```

**Upgrade to specific version:**
```bash
alembic upgrade 003
```

**Downgrade one version:**
```bash
alembic downgrade -1
```

**Downgrade to specific version:**
```bash
alembic downgrade 002
```

### Check Current Version

```bash
alembic current
# Output: 003_add_timeline_events (head)
```

### View Migration History

```bash
alembic history
# Output:
# 003_add_timeline_events (head)
# 002_create_approvals_table
# 001_create_bookings_table
```

---

## Migration Patterns

### Pattern 1: Add Nullable Column

**Safe (backward-compatible):**
```python
def upgrade():
    op.add_column('bookings', sa.Column('notes', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('bookings', 'notes')
```

### Pattern 2: Add Non-Nullable Column (Unsafe)

**Unsafe (breaks existing rows):**
```python
def upgrade():
    # WRONG: Existing rows have no value for new field
    op.add_column('bookings', sa.Column('priority', sa.Integer(), nullable=False))
```

**Safe (two migrations):**
```python
# Migration 1: Add nullable
def upgrade():
    op.add_column('bookings', sa.Column('priority', sa.Integer(), nullable=True))

# Migration 2: Populate + make non-nullable
def upgrade():
    op.execute("UPDATE bookings SET priority = 1 WHERE priority IS NULL")
    op.alter_column('bookings', 'priority', nullable=False, server_default='1')
```

### Pattern 3: Rename Column

**Auto-generated (incorrect):**
```python
# Alembic sees: old column dropped, new column added
def upgrade():
    op.drop_column('bookings', 'party_size')
    op.add_column('bookings', sa.Column('num_guests', sa.Integer()))
    # DATA LOSS!
```

**Correct (manual edit):**
```python
def upgrade():
    op.alter_column('bookings', 'party_size', new_column_name='num_guests')

def downgrade():
    op.alter_column('bookings', 'num_guests', new_column_name='party_size')
```

---

## CI/CD Integration

**Run migrations before deployment:**
```yaml
# .github/workflows/deploy-backend.yml
- name: Run migrations
  run: alembic upgrade head
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

**Verify migrations:**
```bash
# Check pending migrations
alembic current
alembic heads

# If pending, apply
alembic upgrade head
```

---

## Validation

### Verify Installation

```bash
alembic --version
# Expected: alembic 1.13.0
```

### Verify Configuration

```bash
# Check database URL
alembic current
# Should connect successfully
```

### Test Migration

```bash
# Create test migration
alembic revision -m "Test migration"

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1

# Verify rollback worked
alembic current
```

---

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQLAlchemy Migrations](https://docs.sqlalchemy.org/en/20/core/metadata.html#alembic-integration)

**Related ADRs:**
- [ADR-012: PostgreSQL Database](adr-012-postgresql-database.md) - Database choice
- [ADR-013: SQLAlchemy ORM](adr-013-sqlalchemy-orm.md) - ORM integration
- [ADR-007: Deployment Strategy](adr-007-deployment.md) - CI/CD integration

---

## Changelog

- **2025-01-19:** Split from ADR-003 - Alembic migrations as independent decision
