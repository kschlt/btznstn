# ADR-010: DateTime Storage and Timezone Strategy

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)

---

## Context

We need to establish how datetime values are stored in the database and how timezone conversions are handled throughout the application. This decision affects:

- Data integrity (consistent timezone handling)
- Business rule enforcement (BR-014: past date determination, BR-026: future horizon)
- Query correctness (date range comparisons)
- Auto-cleanup jobs (BR-028: daily at 00:01 Europe/Berlin)

### Requirements from Specifications

**Business Rules:**
- **BR-014:** Past dates not allowed - "past" determined relative to "today" in Europe/Berlin timezone
- **BR-026:** Future horizon ≤18 months from "today" in Europe/Berlin
- **BR-028:** Auto-cleanup runs daily at 00:01 Europe/Berlin time
- **BR-009:** Weekly digest on Sunday 09:00 Europe/Berlin

**Technical Constraints:**
- All date/time business logic happens in Europe/Berlin timezone
- Database must handle date comparisons reliably
- Application timezone must be explicit (not dependent on server timezone)

---

## Decision

We will use **naive datetimes (TIMESTAMP WITHOUT TIME ZONE)** for database storage with the following strategy:

1. **Database Storage:** PostgreSQL `TIMESTAMP WITHOUT TIME ZONE` (no timezone info stored)
2. **Timezone Assumption:** All stored datetimes represent Europe/Berlin local time
3. **Application Layer:** Python's `pytz` library for timezone-aware calculations
4. **Conversion Pattern:**
   - Input: Convert user dates to Europe/Berlin → strip timezone → store naive
   - Business logic: Use timezone-aware Europe/Berlin datetimes
   - Output: Interpret stored datetimes as Europe/Berlin → format for display

---

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Database Storage | `TIMESTAMP WITHOUT TIME ZONE` | `TIMESTAMP WITH TIME ZONE` |
| Datetime Operations | `pytz.timezone('Europe/Berlin')` | `datetime.now()`, `datetime.utcnow()` |
| Background Jobs | `AsyncIOScheduler(timezone=berlin_tz)` | Scheduler without timezone |
| Date Fields | `Mapped[date]` for booking dates | `Mapped[datetime]` for date-only fields |

---

## Rationale

**Why Naive Datetimes:**
- Business logic is geographically fixed to Germany → **Constraint:** MUST use naive datetimes (`TIMESTAMP WITHOUT TIME ZONE`) with Europe/Berlin assumption
- Simpler date comparisons without timezone conversion → **Constraint:** MUST use `TIMESTAMP WITHOUT TIME ZONE` for all datetime fields
- Explicit timezone handling in application layer → **Constraint:** MUST use `pytz.timezone('Europe/Berlin')` for all datetime operations

**Why NOT TIMESTAMP WITH TIME ZONE:**
- TIMESTAMP WITH TIME ZONE stores UTC internally → **Violation:** Adds conversion complexity for no benefit in single-timezone app, UTC conversions confusing for German business logic

**Why NOT Store UTC and Convert:**
- Extra conversion logic required → **Violation:** No benefit for single-timezone business logic, "past" determination requires timezone lookup

## Consequences

### MUST (Required)

- MUST use `TIMESTAMP WITHOUT TIME ZONE` for all datetime fields - Business logic is geographically fixed to Germany, simpler date comparisons
- MUST use `pytz.timezone('Europe/Berlin')` for all datetime operations - Explicit timezone handling in application layer
- MUST use `Mapped[date]` for date-only fields (booking dates) - No time component needed for date-only fields
- MUST use `AsyncIOScheduler(timezone=berlin_tz)` for background jobs - Background jobs scheduled in Berlin timezone (BR-028, BR-009)
- MUST use `get_today()` and `get_now()` utilities from `tests/utils.py` - Ensures consistent timezone handling

### MUST NOT (Forbidden)

- MUST NOT use `TIMESTAMP WITH TIME ZONE` in migrations - Violates naive datetime strategy, adds conversion complexity
- MUST NOT use `datetime.now()` or `datetime.utcnow()` - Wrong timezone, violates Europe/Berlin requirement
- MUST NOT mix timezone-aware and naive datetimes in same function - Causes confusion and bugs
- MUST NOT store UTC and convert on read/write - Violates single-timezone assumption

### Trade-offs

- Convention not enforced by database - MUST use `pytz.timezone('Europe/Berlin')` explicitly. MUST NOT assume server timezone. Check code for timezone usage.
- Multi-timezone not supported - MUST use Europe/Berlin only. MUST NOT extend to other timezones without schema migration.

### Code Examples

```python
import pytz
from datetime import datetime, date

BERLIN_TZ = pytz.timezone('Europe/Berlin')

# ✅ CORRECT: Get current date
def get_today() -> date:
    """Current date in Europe/Berlin timezone."""
    return datetime.now(BERLIN_TZ).date()

# ✅ CORRECT: Get naive datetime for DB storage
def get_now() -> datetime:
    """Current datetime in Europe/Berlin, naive for DB."""
    return datetime.now(BERLIN_TZ).replace(tzinfo=None)

# ❌ WRONG: Server timezone undefined
today = datetime.now().date()

# ❌ WRONG: UTC instead of Berlin
today = datetime.utcnow().date()

# ❌ WRONG: Timezone-aware stored in DB
created_at = datetime.now(BERLIN_TZ)  # Has tzinfo, should be naive
```

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

berlin_tz = pytz.timezone('Europe/Berlin')

# ✅ CORRECT: Scheduler with Berlin timezone
scheduler = AsyncIOScheduler(timezone=berlin_tz)

# BR-028: Auto-cleanup at 00:01 Europe/Berlin
scheduler.add_job(
    auto_cleanup_past_pending,
    CronTrigger(hour=0, minute=1, timezone=berlin_tz),
    id='auto_cleanup'
)
```

```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'bookings',
        # ✅ CORRECT: TIMESTAMP WITHOUT TIME ZONE
        sa.Column('created_at', sa.TIMESTAMP(timezone=False), nullable=False),
        # ✅ CORRECT: DATE for booking dates
        sa.Column('start_date', sa.DATE(), nullable=False),
    )

# ❌ WRONG: Don't use TIMESTAMP WITH TIME ZONE
# sa.Column('created_at', sa.TIMESTAMP(timezone=True), ...)
```

### Applies To

- ALL datetime operations (all phases)
- Database schema migrations (Phase 1)
- Background jobs (Phase 8)
- Business rule validation (BR-014, BR-026, BR-028, BR-009)
- File patterns: `app/models/**/*.py`, `alembic/versions/*.py`, `app/services/**/*.py`

### Validation Commands

- `grep -r "datetime.now()" app/` (should be empty - must use `get_today()` or `get_now()`)
- `grep -r "datetime.utcnow()" app/` (should be empty - must use Berlin timezone)
- `grep -r "TIMESTAMP(timezone=True)" alembic/versions/` (should be empty - must use `timezone=False`)
- `grep -r "pytz.timezone" app/` (should show Europe/Berlin usage)

---

## References

**Related ADRs:**
- [ADR-013](adr-013-sqlalchemy-orm.md) - SQLAlchemy ORM
- [ADR-006](adr-006-type-safety.md) - Type Safety

**Business Rules:**
- BR-014: Past date determination
- BR-026: Future horizon (18 months)
- BR-028: Auto-cleanup timing
- BR-009: Weekly digest timing

**Implementation:**
- `tests/utils.py` - `get_today()`, `get_now()`, `BERLIN_TZ`
- `app/schemas/booking.py` - Future horizon validation
- `app/models/` - All datetime fields

**Tools:**
- [PostgreSQL: Date/Time Types](https://www.postgresql.org/docs/current/datatype-datetime.html)
- [pytz documentation](https://pythonhosted.org/pytz/)
