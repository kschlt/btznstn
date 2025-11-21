# ADR-012: PostgreSQL Database

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** Need ACID database for booking system with concurrency safety
**Split from:** ADR-003: Database & ORM

---

## Context

Need relational database for booking & approval application that:
- Stores structured data (bookings, approvals, timeline)
- Supports ACID transactions (booking conflicts, concurrent approvals)
- Handles complex queries (date range overlaps)
- AI-friendly (well-documented, popular)
- Scales for small application (~10-20 users)

**Critical requirements:**
- **BR-002:** Conflict detection (overlapping date ranges)
- **BR-024:** First-action-wins (concurrent approval/denial)
- **BR-029:** First-write-wins (concurrent booking creation)

---

## Decision

Use **PostgreSQL 15+** as the relational database.

---

## Rationale

### Why PostgreSQL vs MySQL vs SQLite vs MongoDB?

**PostgreSQL (Chosen):**
- ✅ **ACID compliance** - Atomicity, Consistency, Isolation, Durability
- ✅ **Row-level locking** - `SELECT FOR UPDATE` prevents race conditions
- ✅ **Date range types** - Native overlap detection (`daterange`, `&&` operator)
- ✅ **GiST indexes** - Fast range queries
- ✅ **Massive AI training data** - AI knows PostgreSQL extremely well
- ✅ **Mature** - 30+ years, stable
- ✅ **Open source** - No vendor lock-in

**MySQL (Rejected):**
- ❌ No date range types (custom conflict detection required)
- ❌ Weaker transaction isolation
- ❌ Less AI training data

**SQLite (Rejected):**
- ❌ No concurrent writes (file-level locking)
- ❌ No range types
- ❌ Not production-suitable

**MongoDB (Rejected):**
- ❌ No ACID across documents
- ❌ No relational integrity
- ❌ Overkill for structured data

---

## Key PostgreSQL Features for Booking System

### 1. Date Range Types (Killer Feature)

**Native overlap detection:**
```sql
-- Create GiST index for fast overlap queries
CREATE INDEX bookings_date_range_gist
ON bookings USING GIST (daterange(start_date, end_date, '[]'));

-- Check for overlaps (fast!)
SELECT * FROM bookings
WHERE daterange(start_date, end_date, '[]') && daterange('2025-08-01', '2025-08-05', '[]')
  AND status IN ('Pending', 'Confirmed');
```

**Why this is powerful:**
- `'[]'` = inclusive range (matches BR-001: inclusive end date)
- `&&` = overlap operator (optimized by GiST index)
- Index scan, not table scan
- PostgreSQL handles edge cases correctly

**Alternative (MySQL/SQLite - slower, complex):**
```sql
SELECT * FROM bookings
WHERE (start_date <= '2025-08-05' AND end_date >= '2025-08-01')
  AND status IN ('Pending', 'Confirmed');
-- Requires multiple indexes, harder to optimize
```

### 2. Row-Level Locking (BR-024, BR-029)

**First-action-wins pattern:**
```sql
BEGIN;

-- Lock booking row (prevents concurrent modifications)
SELECT * FROM bookings WHERE id = :booking_id FOR UPDATE;

-- Check current state
-- Update if appropriate

COMMIT;
```

Standard SQL transaction pattern prevents race conditions.

### 3. Advanced Indexing

**Partial indexes (optimize common queries):**
```sql
-- Index only pending approvals (smaller, faster)
CREATE INDEX approvals_outstanding
ON approvals (party_id, booking_id)
WHERE response = 'NoResponse';
```

---

## Consequences

### Positive

✅ **ACID guarantees** - Transactional safety for conflicts
✅ **Date range types** - Native overlap detection
✅ **GiST indexes** - Fast range queries
✅ **Row-level locking** - SELECT FOR UPDATE prevents races
✅ **AI-friendly** - Massive training data, standard SQL
✅ **Mature & stable** - 30+ years
✅ **Open source** - No vendor lock-in
✅ **JSON support** - Future-proof (JSONB for metadata)

### Negative

⚠️ **More features than needed initially** - Range types powerful but simple MVP
⚠️ **Server required** - Not file-based (but appropriate for production)

### Neutral

➡️ **Version 15+** - Modern features (improved performance, better JSON)
➡️ **Range types** - PostgreSQL-specific (but worth it)

---

## Implementation Pattern

### Connection String

```bash
# Local
DATABASE_URL=postgresql://postgres:dev@localhost:5432/betzenstein

# Production (Fly.io Postgres - see ADR-015)
DATABASE_URL=postgresql://user:pass@betzenstein-db.internal:5432/betzenstein
```

### Schema Example

```sql
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_first_name VARCHAR(40) NOT NULL,
    requester_email VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days INTEGER NOT NULL,
    party_size INTEGER NOT NULL CHECK (party_size >= 1 AND party_size <= 10),
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- GiST index for overlap detection
CREATE INDEX bookings_date_range_gist
ON bookings USING GIST (daterange(start_date, end_date, '[]'));

-- B-tree indexes for common queries
CREATE INDEX bookings_status ON bookings (status);
CREATE INDEX bookings_last_activity_at ON bookings (last_activity_at DESC);
```

### Conflict Detection (BR-002)

```sql
-- Check if date range overlaps any existing booking
SELECT COUNT(*) FROM bookings
WHERE daterange(start_date, end_date, '[]') && daterange(:start, :end, '[]')
  AND status IN ('Pending', 'Confirmed')
  AND id != :exclude_id;  -- Exclude current booking (for edits)

-- If COUNT > 0, conflict exists
```

---

## References

**Related ADRs:**
- ADR-013: SQLAlchemy ORM (ORM for PostgreSQL)
- ADR-014: Alembic Migrations (schema migrations)
- ADR-015: Fly.io Postgres Hosting (hosting platform)

**Business Rules:**
- BR-001: Inclusive end date (range type `'[]'` matches this)
- BR-002: No overlaps (GiST index for fast detection)
- BR-024: First-action-wins (SELECT FOR UPDATE)
- BR-029: First-write-wins (SELECT FOR UPDATE)

**Tools:**
- [PostgreSQL Documentation](https://www.postgresql.org/docs/15/)
- [Range Types](https://www.postgresql.org/docs/15/rangetypes.html)
- [Indexes](https://www.postgresql.org/docs/15/indexes.html)
