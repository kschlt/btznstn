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

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Database | PostgreSQL 15+ | MySQL, SQLite, MongoDB |
| Date Range Queries | `daterange` type with GiST index | Manual overlap detection |
| Concurrency | `SELECT FOR UPDATE` row-level locking | No locking, race conditions |
| Indexes | GiST indexes for range queries | B-tree only, slow range queries |

---

## Rationale

**Why PostgreSQL:**
- PostgreSQL provides native date range types → **Constraint:** MUST use `daterange` type with GiST indexes for overlap detection
- PostgreSQL provides row-level locking → **Constraint:** MUST use `SELECT FOR UPDATE` for concurrent operations (BR-024, BR-029)
- PostgreSQL has massive AI training data → **Constraint:** MUST use PostgreSQL 15+ (modern features, better AI support)

**Why NOT MySQL:**
- MySQL lacks date range types → **Violation:** Requires custom conflict detection, slower queries, violates BR-002 requirement

**Why NOT SQLite:**
- SQLite has file-level locking → **Violation:** No concurrent writes, violates BR-024 and BR-029 requirements

**Why NOT MongoDB:**
- MongoDB lacks ACID across documents → **Violation:** No transactional safety, violates BR-002, BR-024, BR-029 requirements

## Consequences

### MUST (Required)

- MUST use PostgreSQL 15+ - Modern features, improved performance, better AI support
- MUST use `daterange` type with GiST indexes for overlap detection - Native overlap detection, fast queries (BR-002)
- MUST use `SELECT FOR UPDATE` for concurrent operations - Row-level locking prevents race conditions (BR-024, BR-029)
- MUST use GiST indexes for range queries - Fast overlap detection, optimized by PostgreSQL

### MUST NOT (Forbidden)

- MUST NOT use MySQL or SQLite - Violates date range type requirement, slower queries
- MUST NOT use MongoDB - Violates ACID requirement, no transactional safety
- MUST NOT use manual overlap detection - Violates native range type requirement, slower and error-prone

### Trade-offs

- PostgreSQL-specific features - MUST use PostgreSQL. MUST NOT use other databases. Range types are PostgreSQL-specific but worth it for BR-002.

### Code Examples

```sql
-- ✅ CORRECT: Date range type with GiST index
CREATE INDEX bookings_date_range_gist
ON bookings USING GIST (daterange(start_date, end_date, '[]'));

SELECT * FROM bookings
WHERE daterange(start_date, end_date, '[]') && daterange('2025-08-01', '2025-08-05', '[]')
  AND status IN ('Pending', 'Confirmed');

-- ❌ WRONG: Manual overlap detection (MySQL/SQLite pattern)
SELECT * FROM bookings
WHERE (start_date <= '2025-08-05' AND end_date >= '2025-08-01')
  AND status IN ('Pending', 'Confirmed');
```

```sql
-- ✅ CORRECT: Row-level locking for concurrency
BEGIN;
SELECT * FROM bookings WHERE id = :booking_id FOR UPDATE;
-- Update if appropriate
COMMIT;

-- ❌ WRONG: No locking (race condition)
SELECT * FROM bookings WHERE id = :booking_id;
-- Update (may conflict with concurrent request)
```

### Applies To

- ALL database schema definitions (Phase 1)
- ALL conflict detection queries (BR-002)
- ALL concurrent operations (BR-024, BR-029)
- File patterns: `alembic/versions/*.py`, `app/models/**/*.py`

### Validation Commands

- `grep -r "daterange" alembic/versions/` (should be present for date range queries)
- `grep -r "USING GIST" alembic/versions/` (should be present for range indexes)
- `grep -r "FOR UPDATE" app/repositories/` (should be present for concurrent operations)

---

**Related ADRs:**
- [ADR-013](adr-013-sqlalchemy-orm.md) - SQLAlchemy ORM
- [ADR-014](adr-014-alembic-migrations.md) - Alembic Migrations
- [ADR-016](adr-016-flyio-postgres-hosting.md) - Fly.io Postgres Hosting

---

## References

**Related ADRs:**
- [ADR-013](adr-013-sqlalchemy-orm.md) - SQLAlchemy ORM
- [ADR-014](adr-014-alembic-migrations.md) - Alembic Migrations
- [ADR-016](adr-016-flyio-postgres-hosting.md) - Fly.io Postgres Hosting

**Business Rules:**
- BR-001: Inclusive end date (range type `'[]'` matches this)
- BR-002: No overlaps (GiST index for fast detection)
- BR-024: First-action-wins (SELECT FOR UPDATE)
- BR-029: First-write-wins (SELECT FOR UPDATE)

**Tools:**
- [PostgreSQL Documentation](https://www.postgresql.org/docs/15/)
- [Range Types](https://www.postgresql.org/docs/15/rangetypes.html)
- [Indexes](https://www.postgresql.org/docs/15/indexes.html)
