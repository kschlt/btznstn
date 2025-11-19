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

### Positive

**✅ Simpler Business Logic:**
- "Today" in business rules = `datetime.now(BERLIN_TZ).date()`
- Past determination: Compare naive dates directly
- No timezone conversion bugs in date comparisons

**✅ Clearer Scheduling:**
- "00:01 Berlin time" stored as 00:01, not 23:01 UTC
- Background jobs scheduled in Berlin timezone directly
- No confusion during daylight saving time transitions

**✅ Explicit Timezone Handling:**
- Application code must use `pytz.timezone('Europe/Berlin')` explicitly
- Type system enforces timezone awareness in Python
- Harder to accidentally use wrong timezone

**✅ Database Queries Stay Simple:**
```sql
-- No timezone conversion needed
SELECT * FROM bookings WHERE start_date >= CURRENT_DATE;
```

### Negative

**⚠️ Implicit Assumption:**
- Database doesn't enforce Europe/Berlin - it's a convention
- Future developers must know to use Berlin timezone
- Could cause bugs if assumption is violated

**⚠️ No Multi-Timezone Support:**
- Hard to extend to other locations later
- Would require migration to TIMESTAMP WITH TIME ZONE

### Neutral

**Requires Discipline:**
- All Python code must use `pytz.timezone('Europe/Berlin')`
- Tests must use `get_today()` and `get_now()` utilities
- Documentation must explain the assumption

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
