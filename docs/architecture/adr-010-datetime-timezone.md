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

## Rationale

### Why Naive Datetimes (Not TIMESTAMP WITH TIME ZONE)?

**1. Business Logic is Geographically Fixed**
- All bookings happen in Betzenstein, Germany (Europe/Berlin timezone)
- All approvers are in Germany
- All date business rules reference "today" in German local time
- No need to support multiple timezones

**2. Simpler Date Comparisons**
- Date-only comparisons (e.g., "is booking in past?") don't require timezone conversion
- Query filters like `start_date >= current_date` work directly
- No ambiguity about "which timezone's midnight?"

**3. Avoids UTC Conversion Confusion**
- TIMESTAMP WITH TIME ZONE stores UTC internally, displays in session timezone
- This adds conversion complexity for no benefit (single timezone app)
- Auto-cleanup at "00:01 Berlin time" is clearer than "23:01 UTC (or 22:01 during DST)"

**4. Explicit Timezone Handling in Application**
- Forces developers to be explicit about timezone in Python code
- Uses `pytz.timezone('Europe/Berlin')` consistently
- Catches timezone bugs at application layer (not silently in database)

### Alternatives Considered

| Alternative | Pros | Cons | Why Rejected |
|-------------|------|------|--------------|
| **TIMESTAMP WITH TIME ZONE** | Standard practice for global apps | Adds complexity for single-timezone app; UTC conversions confusing | App is geographically fixed to Germany |
| **Store UTC, convert on read/write** | Universal time standard | Extra conversion logic; "past" determination requires timezone lookup | No benefit for single-timezone business logic |
| **String dates (YYYY-MM-DD)** | Simple for date-only fields | Loses time information; hard to query ranges; no DST handling | Need time for timeline events, audit logs |
| **Unix timestamps (integers)** | Compact storage | Loses readability; hard to query; no database date functions | Not human-readable in DB queries |

---

## Consequences

### Implementation Constraints

✅ **Date calculations simplified** - No timezone conversion in SQL queries
✅ **Background job scheduling explicit** - Cron expressions use Berlin timezone directly
✅ **Business rule evaluation clear** - "Today" always means Europe/Berlin date
✅ **Database schema simple** - `TIMESTAMP WITHOUT TIME ZONE` for all datetime fields

### Complexity Trade-offs

⚠️ **Explicit timezone REQUIRED everywhere** - Every datetime operation must use `pytz.timezone('Europe/Berlin')`
⚠️ **Convention not enforced** - Database doesn't prevent storing non-Berlin datetimes (mitigation: code review + utility functions)
⚠️ **Multi-timezone not supported** - Extending to other locations requires schema migration

---

## LLM Implementation Constraints

### Required Patterns

**MUST:**
- ALL datetime operations use `pytz.timezone('Europe/Berlin')` explicitly
- Database columns use `TIMESTAMP WITHOUT TIME ZONE` (SQLAlchemy: `Mapped[datetime]` without timezone)
- Background jobs use `AsyncIOScheduler(timezone=berlin_tz)`
- Date fields use `Mapped[date]` (no time component for booking dates)

**MUST NOT:**
- Use `datetime.now()` or `datetime.utcnow()` (wrong timezone)
- Use `TIMESTAMP WITH TIME ZONE` in migrations
- Mix timezone-aware and naive datetimes in same function
- Store UTC and convert on read/write (violates single-timezone assumption)

**Example - Correct Pattern:**
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

# ✅ CORRECT: Business logic
today = get_today()
if booking.end_date < today:
    # German copy from docs/specification/error-handling.md:XX
    raise HTTPException(400, "Das Enddatum liegt in der Vergangenheit.")
```

**Example - WRONG (Anti-patterns):**
```python
# ❌ WRONG: Server timezone undefined
today = datetime.now().date()

# ❌ WRONG: UTC instead of Berlin
today = datetime.utcnow().date()

# ❌ WRONG: Hardcoded timezone offset
now = datetime.now() + timedelta(hours=1)  # Breaks during DST!

# ❌ WRONG: Timezone-aware stored in DB
created_at = datetime.now(BERLIN_TZ)  # Has tzinfo, should be naive
```

### Background Job Pattern (BR-028, BR-009)

**For scheduled tasks (BR-028, BR-009):**
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
    CronTrigger(hour=0, minute=1, timezone=berlin_tz),  # ✅ Explicit timezone
    id='auto_cleanup'
)

# BR-009: Weekly digest Sunday 09:00 Europe/Berlin
scheduler.add_job(
    send_weekly_digest,
    CronTrigger(day_of_week='sun', hour=9, minute=0, timezone=berlin_tz),
    id='weekly_digest'
)
```

### Database Schema Pattern

**Alembic Migration:**
```python
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'bookings',
        # ✅ CORRECT: TIMESTAMP WITHOUT TIME ZONE
        sa.Column('created_at', sa.TIMESTAMP(timezone=False), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=False), nullable=False),
        # ✅ CORRECT: DATE for booking dates (no time component)
        sa.Column('start_date', sa.DATE(), nullable=False),
        sa.Column('end_date', sa.DATE(), nullable=False),
    )

# ❌ WRONG: Don't use TIMESTAMP WITH TIME ZONE
# sa.Column('created_at', sa.TIMESTAMP(timezone=True), ...)
```

### Applies To

**This constraint affects:**
- ALL datetime operations (all phases)
- Database schema migrations (Phase 1)
- Background jobs (Phase 8)
- Business rule validation (BR-014, BR-026, BR-028, BR-009)

### When Writing User Stories

**Ensure specifications include:**
- Date validation uses `get_today()` utility from `tests/utils.py`
- SQLAlchemy models use `Mapped[datetime]` without timezone
- Background job specs reference Europe/Berlin timezone explicitly
- Migration specs use `TIMESTAMP(timezone=False)`

**Validation commands for user story checklists:**
- No `datetime.now()` without timezone: `grep -r "datetime.now()" app/`
- All migrations use naive timestamps: Review `alembic/versions/*.py`

**Related ADRs:**
- [ADR-013](adr-013-sqlalchemy-orm.md) - SQLAlchemy datetime patterns
- [ADR-006](adr-006-type-safety.md) - Type hints for datetime fields

**Related Specifications:**
- Utility functions: `tests/utils.py`
- German error messages for date validation: `docs/specification/error-handling.md`
- Business rules: BR-014 (past dates), BR-026 (future horizon), BR-028 (auto-cleanup), BR-009 (digest)

---

## Implementation Notes

### Pattern: Database Storage

**SQLAlchemy Model:**
```python
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from datetime import datetime

class Booking(Base):
    # Store naive datetime (TIMESTAMP WITHOUT TIME ZONE)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=func.now()  # PostgreSQL NOW() returns Berlin time if server configured
    )

    # Date fields
    start_date: Mapped[date] = mapped_column(nullable=False)
    end_date: Mapped[date] = mapped_column(nullable=False)
```

### Pattern: Timezone-Aware Business Logic

**Utilities (tests/utils.py):**
```python
import pytz
from datetime import datetime, date

BERLIN_TZ = pytz.timezone('Europe/Berlin')

def get_today() -> date:
    """Get current date in Europe/Berlin timezone."""
    return datetime.now(BERLIN_TZ).date()

def get_now() -> datetime:
    """Get current datetime in Europe/Berlin, returned as naive."""
    return datetime.now(BERLIN_TZ).replace(tzinfo=None)
```

**Usage in Business Logic:**
```python
from tests.utils import get_today, BERLIN_TZ
from dateutil.relativedelta import relativedelta

# Check if date is in the past (BR-014)
today = get_today()
if booking.start_date < today:
    raise ValueError("Startdatum liegt in der Vergangenheit.")

# Check future horizon (BR-026)
future_limit = today + relativedelta(months=18)
if booking.end_date > future_limit:
    raise ValueError("Buchungen sind nur bis zu 18 Monate im Voraus möglich.")
```

### Pattern: Background Jobs

**APScheduler Configuration:**
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

berlin_tz = pytz.timezone('Europe/Berlin')
scheduler = AsyncIOScheduler(timezone=berlin_tz)

# Auto-cleanup: Daily at 00:01 Europe/Berlin
scheduler.add_job(
    auto_cleanup_past_pending,
    CronTrigger(hour=0, minute=1, timezone=berlin_tz),
    id='auto_cleanup'
)
```

### Migration Notes

**If moving to multi-timezone support later:**
1. Create migration to add timezone column (default 'Europe/Berlin')
2. Convert TIMESTAMP WITHOUT TIME ZONE → TIMESTAMP WITH TIME ZONE
3. Update application code to handle timezone per booking
4. Maintain backward compatibility with Berlin-only bookings

---

## Verification Checklist

- [x] All datetime fields use naive datetime (no tzinfo)
- [x] `get_today()` and `get_now()` utilities use Europe/Berlin
- [x] Business rules reference Berlin timezone explicitly
- [x] Background jobs scheduled in Berlin timezone
- [x] Tests use `get_today()` and `get_now()` (not `datetime.now()`)
- [x] Database migrations specify TIMESTAMP WITHOUT TIME ZONE
- [x] No mixing of timezone-aware and naive datetimes

---

## References

**Related ADRs:**
- ADR-013: SQLAlchemy ORM (SQLAlchemy patterns)
- ADR-006: Type Safety (mypy catches timezone issues)

**Business Rules:**
- BR-014: Past date determination
- BR-026: Future horizon (18 months)
- BR-028: Auto-cleanup timing
- BR-009: Weekly digest timing

**Implementation:**
- `tests/utils.py` - `get_today()`, `get_now()`, `BERLIN_TZ`
- `app/schemas/booking.py` - Future horizon validation
- `app/models/` - All datetime fields

**External Documentation:**
- [PostgreSQL: Date/Time Types](https://www.postgresql.org/docs/current/datatype-datetime.html)
- [pytz documentation](https://pythonhosted.org/pytz/)
- [python-dateutil relativedelta](https://dateutil.readthedocs.io/en/stable/relativedelta.html)
