# ADR-012: PostgreSQL Database

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)
**Split from:** [ADR-003: Database & ORM](adr-003-database-orm.md)

---

## Context

We need to choose a relational database for the Betzenstein booking & approval application. The database must:

- Store structured data (bookings, approvals, timeline events)
- Support ACID transactions (booking conflicts, concurrent approvals)
- Handle complex queries (conflict detection, date range overlaps)
- Be AI-friendly (well-documented, popular)
- Scale for small application (~10-20 users)

### Requirements from Specifications

From `docs/foundation/business-rules.md`:
- **BR-002:** Conflict detection (overlapping date ranges)
- **BR-024:** First-action-wins (concurrent approval/denial)
- **BR-029:** First-write-wins (concurrent booking creation)

**Critical requirement:** Transactional consistency for concurrency safety.

---

## Decision

We will use **PostgreSQL 15+** as the relational database.

---

## Rationale

### 1. ACID Guarantees (Critical for Booking System)

**Why this matters:** Booking conflicts and concurrent approvals require transactional safety.

**PostgreSQL benefits:**
- ✅ **Full ACID compliance** - Atomicity, Consistency, Isolation, Durability
- ✅ **Row-level locking** - `SELECT FOR UPDATE` prevents race conditions (BR-024, BR-029)
- ✅ **Transaction isolation** - Read committed default, serializable available
- ✅ **Consistent** - No eventual consistency issues

**Example (conflict detection with lock):**
```sql
BEGIN;

-- Lock booking row (prevents concurrent modifications)
SELECT * FROM bookings
WHERE id = 'uuid'
FOR UPDATE;

-- Check current state
-- Update if appropriate

COMMIT;
```

**AI benefit:** Standard SQL transaction patterns prevent booking conflicts.

### 2. Date Range Types (Perfect for Booking System)

**PostgreSQL unique feature:** Native date range types + GiST indexes.

**Example (booking overlap detection):**
```sql
-- Create date range index
CREATE INDEX bookings_date_range_gist
ON bookings USING GIST (daterange(start_date, end_date, '[]'));

-- Check for overlapping bookings (fast!)
SELECT * FROM bookings
WHERE daterange(start_date, end_date, '[]') && daterange('2025-08-01', '2025-08-05', '[]')
  AND status IN ('Pending', 'Confirmed');
```

**Why this is powerful:**
- ✅ **Inclusive range** (`'[]'` matches BR-001: inclusive end date)
- ✅ **Overlap operator** (`&&`) is optimized by GiST index
- ✅ **Fast** - Index scan, not table scan
- ✅ **Correct** - PostgreSQL handles edge cases (same start/end, etc.)

**Alternative (without range types):**
```sql
-- MySQL/SQLite approach (slower, more complex)
SELECT * FROM bookings
WHERE (start_date <= '2025-08-05' AND end_date >= '2025-08-01')
  AND status IN ('Pending', 'Confirmed');
-- Requires multiple indexes, harder to optimize
```

**AI benefit:** PostgreSQL range types match booking domain naturally.

### 3. Advanced Indexing (GiST, B-tree)

**PostgreSQL indexes:**
- ✅ **GiST** - Generalized Search Tree (for ranges, geometries)
- ✅ **B-tree** - Standard (for equality, sorting)
- ✅ **Partial indexes** - Index only subset (e.g., `WHERE status = 'Pending'`)
- ✅ **Composite indexes** - Multiple columns

**Example (optimized queries):**
```sql
-- Partial index for outstanding approvals
CREATE INDEX approvals_outstanding
ON approvals (party_id, booking_id)
WHERE response = 'NoResponse';

-- Only indexes pending approvals (smaller, faster)
```

**AI benefit:** AI can generate index strategies for common queries.

### 4. JSON Support (Future-Proofing)

**PostgreSQL JSON:**
- ✅ **JSONB** - Binary JSON (fast, indexed)
- ✅ **JSON queries** - Extract fields, filter
- ✅ **Flexible schema** - Store metadata without migrations

**Example (future use case - booking metadata):**
```sql
ALTER TABLE bookings ADD COLUMN metadata JSONB;

CREATE INDEX bookings_metadata_gin ON bookings USING GIN (metadata);

-- Query metadata
SELECT * FROM bookings
WHERE metadata @> '{"dietary_restrictions": ["vegetarian"]}';
```

**Not needed initially, but available if requirements change.**

### 5. AI-Friendly (Massive Training Data)

**Why this matters:** AI must generate SQL, migrations, queries.

**PostgreSQL advantages:**
- ✅ **Most popular** open-source RDBMS
- ✅ **Massive training data** - AI knows PostgreSQL extremely well
- ✅ **Standard SQL** - Portable queries
- ✅ **Excellent documentation** - AI can reference

**Evidence:** Stack Overflow, GitHub, tutorials heavily favor PostgreSQL.

### 6. Open Source & Community

**PostgreSQL benefits:**
- ✅ **MIT-style license** - No vendor lock-in
- ✅ **30+ years** - Mature, stable
- ✅ **Active community** - Frequent releases
- ✅ **Extensions** - PostGIS, pg_cron, etc.

---

## Alternatives Considered

### MySQL

**Pros:**
- Popular
- Good performance
- Oracle backing

**Cons:**
- ❌ **No date range types** - Custom conflict detection logic required
- ❌ **Weaker transaction isolation** - READ COMMITTED behaves differently
- ❌ **Less AI training data** - PostgreSQL more prevalent in modern stacks

**Decision:** PostgreSQL's range types are killer feature for booking system.

---

### SQLite

**Pros:**
- Simple (file-based)
- No server setup
- Good for testing

**Cons:**
- ❌ **No concurrent writes** - Locking at file level
- ❌ **No range types** - Custom conflict logic
- ❌ **Not production-suitable** - Single file, limited concurrency

**Decision:** SQLite great for testing, not for production with concurrent bookings.

---

### MongoDB (NoSQL)

**Pros:**
- Flexible schema
- JSON-native
- Good for unstructured data

**Cons:**
- ❌ **No ACID across documents** - Transactions limited (before v4)
- ❌ **No relational integrity** - Manual foreign key management
- ❌ **Overkill** - Bookings are structured, relational data
- ❌ **More complex queries** - No SQL, aggregation pipelines

**Decision:** Relational data requires relational database. PostgreSQL is ideal.

---

### CockroachDB (Distributed Postgres)

**Pros:**
- PostgreSQL compatible
- Distributed
- Auto-scaling

**Cons:**
- ❌ **Overkill** - Small app, ~10-20 users
- ❌ **More expensive** - Designed for massive scale
- ❌ **More complex** - Distributed systems complexity

**Decision:** PostgreSQL sufficient for MVP. Can migrate later if needed.

---

## Consequences

### Positive

✅ **ACID guarantees** - Transactional safety for booking conflicts
✅ **Date range types** - Native support for overlap detection
✅ **GiST indexes** - Fast range queries
✅ **JSON support** - Future-proof for metadata
✅ **AI-friendly** - Massive training data, standard SQL
✅ **Row-level locking** - SELECT FOR UPDATE prevents races
✅ **Mature & stable** - 30+ years of development
✅ **Open source** - No vendor lock-in

### Negative

⚠️ **More features than needed initially** - Range types, JSON not used in MVP
⚠️ **Server required** - Not file-based like SQLite (but appropriate for production)

### Neutral

➡️ **Version 15+** - Ensures modern features (improved performance, better JSON support)
➡️ **Standard SQL** - Portable to other databases if needed (though range types are PostgreSQL-specific)

---

## Implementation Notes

### Installation

**Local development:**
```bash
# macOS
brew install postgresql@15

# Ubuntu
sudo apt install postgresql-15

# Docker
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=dev \
  -e POSTGRES_DB=betzenstein \
  -p 5432:5432 \
  postgres:15
```

### Connection String

**Format:**
```
postgresql://username:password@host:port/database
```

**Examples:**
```bash
# Local
DATABASE_URL=postgresql://postgres:dev@localhost:5432/betzenstein

# Production (Fly.io Postgres - see ADR-015)
DATABASE_URL=postgresql://user:pass@betzenstein-db.internal:5432/betzenstein
```

### Schema Example

**Bookings table with range index:**
```sql
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requester_first_name VARCHAR(40) NOT NULL,
    requester_email VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_days INTEGER NOT NULL,
    party_size INTEGER NOT NULL CHECK (party_size >= 1 AND party_size <= 10),
    affiliation VARCHAR(20) NOT NULL,
    description TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- GiST index for fast overlap detection
CREATE INDEX bookings_date_range_gist
ON bookings USING GIST (daterange(start_date, end_date, '[]'));

-- B-tree indexes for common queries
CREATE INDEX bookings_status ON bookings (status);
CREATE INDEX bookings_created_at ON bookings (created_at DESC);
CREATE INDEX bookings_last_activity_at ON bookings (last_activity_at DESC);
```

### Conflict Detection Query

**BR-002: No overlaps with Pending/Confirmed:**
```sql
-- Check if date range overlaps any existing booking
SELECT COUNT(*) FROM bookings
WHERE daterange(start_date, end_date, '[]') && daterange(:start, :end, '[]')
  AND status IN ('Pending', 'Confirmed')
  AND id != :exclude_id;  -- Exclude current booking (for edits)

-- If COUNT > 0, conflict exists
```

### Row-Level Locking (BR-024, BR-029)

**First-action-wins for approvals:**
```sql
BEGIN;

-- Lock booking row
SELECT * FROM bookings
WHERE id = :booking_id
FOR UPDATE;

-- Check approval can proceed
-- (booking status, approval not already responded, etc.)

-- Update approval
UPDATE approvals
SET response = 'Approved', responded_at = CURRENT_TIMESTAMP
WHERE id = :approval_id;

-- Check if all approvals complete
-- Update booking status if needed

COMMIT;
```

**AI benefit:** Standard transaction pattern prevents race conditions.

---

## Validation

### Verify Installation

```bash
# Check PostgreSQL version
psql --version
# Expected: psql (PostgreSQL) 15.x

# Connect to database
psql postgresql://postgres:dev@localhost:5432/betzenstein

# Verify range types support
SELECT '[2025-08-01,2025-08-05]'::daterange;
# Expected: [2025-08-01,2025-08-05]
```

### Verify GiST Index

```sql
-- Create test data
INSERT INTO bookings (requester_first_name, requester_email, start_date, end_date, total_days, party_size, affiliation, status)
VALUES ('Test', 'test@example.com', '2025-08-01', '2025-08-05', 5, 4, 'Ingeborg', 'Confirmed');

-- Query with range overlap (should use GiST index)
EXPLAIN ANALYZE
SELECT * FROM bookings
WHERE daterange(start_date, end_date, '[]') && daterange('2025-08-03', '2025-08-07', '[]');

-- Expected plan: Index Scan using bookings_date_range_gist
```

---

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/15/)
- [PostgreSQL Range Types](https://www.postgresql.org/docs/15/rangetypes.html)
- [PostgreSQL Indexes](https://www.postgresql.org/docs/15/indexes.html)
- [PostgreSQL Transactions](https://www.postgresql.org/docs/15/tutorial-transactions.html)

**Related ADRs:**
- [ADR-013: SQLAlchemy ORM](adr-013-sqlalchemy-orm.md) - ORM for PostgreSQL
- [ADR-014: Alembic Migrations](adr-014-alembic-migrations.md) - Schema migrations
- [ADR-015: Fly.io Postgres Hosting](adr-015-flyio-postgres-hosting.md) - Hosting platform

**Business Rules:**
- BR-001: Inclusive end date (range type `'[]'` matches this)
- BR-002: No overlaps with Pending/Confirmed (GiST index for fast detection)
- BR-024: First-action-wins (SELECT FOR UPDATE prevents races)
- BR-029: First-write-wins (SELECT FOR UPDATE prevents double-booking)

---

## Changelog

- **2025-01-19:** Split from ADR-003 - PostgreSQL database choice as independent decision
