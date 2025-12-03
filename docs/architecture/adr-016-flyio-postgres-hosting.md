# ADR-016: Fly.io Postgres Hosting

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** Need always-on PostgreSQL hosting co-located with backend
**Split from:** ADR-003: Database & ORM, ADR-007: Deployment Strategy

---

## Context

Need hosting platform for PostgreSQL that:
- Runs PostgreSQL 15+ reliably
- Low-latency access from backend API
- EU data residency (GDPR compliance)
- Always-on (no shutdown when idle)
- Automated backups
- Budget-friendly (free or cheap for MVP)

**Critical requirement:** Backend on Fly.io (Frankfurt) - database should be co-located.

---

## Decision

Host PostgreSQL on **Fly.io Postgres** in Frankfurt (FRA) region, co-located with backend API.

---

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Hosting Platform | Fly.io Postgres | Supabase, Railway, AWS RDS |
| Region | Frankfurt (FRA) | Other regions |
| Connection | `.internal` hostname (private network) | Public internet connection |
| Always-On | Never pauses or shuts down | Pausing/shutting down when idle |

---

## Rationale

**Why Fly.io Postgres:**
- Fly.io Postgres co-locates with backend → **Constraint:** MUST use Fly.io Postgres in Frankfurt (FRA) region, same as backend
- Fly.io Postgres provides private network → **Constraint:** MUST use `.internal` hostname for database connection (low latency, no egress fees)
- Fly.io Postgres never pauses → **Constraint:** MUST use always-on hosting (no pausing, no cold starts)

**Why NOT Supabase:**
- Supabase free tier pauses when idle → **Violation:** Pauses after 7 days inactivity, slow wake-up (10-30 seconds), violates always-on requirement

**Why NOT Railway:**
- Railway is separate platform → **Violation:** Public internet connection adds latency, egress fees, violates co-location requirement

## Consequences

### MUST (Required)

- MUST use Fly.io Postgres in Frankfurt (FRA) region - Co-located with backend, GDPR compliance
- MUST use `.internal` hostname for database connection - Private network, <1ms latency, no egress fees
- MUST use always-on hosting - Never pauses or shuts down, no cold starts

### MUST NOT (Forbidden)

- MUST NOT use Supabase or Railway - Violates co-location requirement, adds latency
- MUST NOT use public internet connection - Violates private network requirement, adds latency and egress fees
- MUST NOT use hosting that pauses when idle - Violates always-on requirement

### Trade-offs

- Fly.io-specific configuration - MUST use Fly.io Postgres. MUST NOT use other platforms. Migration to other platform requires effort.
- Free tier limits - MUST use free tier initially. MUST NOT exceed 3GB storage without upgrading. Check storage usage before scaling.

### Code Examples

```bash
# ✅ CORRECT: Private network connection
DATABASE_URL=postgresql://postgres:<password>@betzenstein-db.internal:5432/betzenstein

# ❌ WRONG: Public internet connection
DATABASE_URL=postgresql://postgres:<password>@betzenstein-db.fly.io:5432/betzenstein
```

```bash
# ✅ CORRECT: Create Postgres in Frankfurt region
fly postgres create --name betzenstein-db --region fra

# ❌ WRONG: Different region
fly postgres create --name betzenstein-db --region ord  # Wrong region
```

### Applies To

- ALL database hosting configuration (Phase 1)
- File patterns: `fly.toml`, deployment scripts

### Validation Commands

- `grep -r "\.internal" fly.toml` (should be present - private network connection)
- `grep -r "region.*fra" fly.toml` (should be present - Frankfurt region)
- `fly postgres list` (should show betzenstein-db in fra region)

---

**Related ADRs:**
- [ADR-012](adr-012-postgresql-database.md) - PostgreSQL Database
- [ADR-015](adr-015-flyio-backend-hosting.md) - Fly.io Backend Hosting
- [ADR-013](adr-013-sqlalchemy-orm.md) - SQLAlchemy ORM

---

## References

**Related ADRs:**
- [ADR-012](adr-012-postgresql-database.md) - PostgreSQL Database
- [ADR-015](adr-015-flyio-backend-hosting.md) - Fly.io Backend Hosting
- [ADR-013](adr-013-sqlalchemy-orm.md) - SQLAlchemy ORM

**Tools:**
- [Fly.io Postgres Documentation](https://fly.io/docs/postgres/)
- [Fly.io Private Networking](https://fly.io/docs/reference/private-networking/)
