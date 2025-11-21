# ADR-015: Fly.io Postgres Hosting

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

## Rationale

### Why Fly.io Postgres vs Supabase vs Railway?

**Fly.io Postgres (Chosen):**
- ✅ **Co-located with backend** - Same platform, same datacenter
- ✅ **Private network** - API connects via `.internal` hostname (<1ms latency)
- ✅ **Always on** - Never pauses or shuts down
- ✅ **No cold starts** - Instant connections
- ✅ **EU region** - Frankfurt (GDPR compliance)
- ✅ **Simpler ops** - One platform for API + DB (one CLI, one dashboard)
- ✅ **Free tier** - 3GB storage included

**Supabase (Rejected):**
- ❌ **Pauses when idle** - Free tier shuts down after ~7 days
- ❌ **Cold starts** - Slow to wake up (10-30 seconds)
- ❌ **$25/month for always-on** - More expensive than Fly.io
- ❌ User explicitly requested to avoid Supabase pause behavior

**Railway (Rejected):**
- ❌ **Separate platform** - API on Fly.io, DB on Railway
- ❌ **Public internet** - Slight latency overhead
- ❌ **Egress fees** - Data transfer costs

---

## Key Benefits of Co-Location

### 1. Ultra-Low Latency (Private Network)

```bash
# Public connection (slower, costs egress)
DATABASE_URL=postgresql://user:pass@db.fly.io:5432/betzenstein

# Internal connection (faster, free)
DATABASE_URL=postgresql://user:pass@betzenstein-db.internal:5432/betzenstein
```

**Latency comparison:**
- Public internet: 10-50ms per query
- Fly.io internal: <1ms per query

**Why this matters:**
- Conflict detection requires fast queries (BR-002)
- Concurrent approvals need low-latency locks (BR-024)
- Calendar views query many bookings

### 2. Same Platform (Simpler Management)

**One platform = simpler operations:**
- One CLI (`flyctl`)
- One dashboard
- One account
- No egress fees (internal network free)

### 3. Always On (No Pausing)

**Fly.io Postgres:**
- Never pauses
- Never shuts down
- No cold starts
- Predictable performance

**Contrast with Supabase free tier:**
- Pauses after 7 days inactivity
- Slow wake-up (10-30 seconds)

### 4. EU Region (GDPR)

**Fly.io Frankfurt (FRA):**
- Data stays in EU
- Low latency for German users (<50ms)
- Same region as backend

---

## Consequences

### Positive

✅ **Ultra-low latency** - <1ms via private network
✅ **Always on** - No pausing or cold starts
✅ **Same platform** - Simpler management
✅ **EU region** - GDPR compliance (Frankfurt)
✅ **Automated backups** - Daily snapshots included
✅ **Free tier** - Sufficient for MVP
✅ **Managed** - No manual operations

### Negative

⚠️ **Fly.io-specific** - Migration to other platform requires effort
⚠️ **Limited UI** - Dashboard less polished than Railway/Supabase
⚠️ **Free tier limits** - 3GB storage (upgrade if growth exceeds)

### Neutral

➡️ **Connection pooling** - May need PgBouncer for high concurrency (not needed initially)
➡️ **Read replicas** - Can add if read-heavy (not needed for MVP)

---

## Implementation Pattern

### Create Fly.io Postgres

```bash
# Create Postgres app
fly postgres create --name betzenstein-db --region fra

# Output:
# Username:    postgres
# Password:    <generated-password>
# Hostname:    betzenstein-db.internal
# Proxy port:  5432
```

### Attach to Backend App

```bash
# Link database to API app
fly postgres attach --app betzenstein-api betzenstein-db

# Automatically sets DATABASE_URL secret
```

**Connection string:**
```
postgresql://postgres:<password>@betzenstein-db.internal:5432/betzenstein
```

### Verify Connection

```python
# app/core/config.py
DATABASE_URL = "postgresql+asyncpg://postgres:<password>@betzenstein-db.internal:5432/betzenstein"

# Test connection
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(DATABASE_URL)
async with engine.connect() as conn:
    result = await conn.execute("SELECT version();")
    print(result.scalar())
```

### Backups

**Automatic:**
- Daily snapshots
- Retained for 7 days (free tier)

**Manual:**
```bash
# Dump database
fly postgres db dump -a betzenstein-db > backup.sql

# Restore
fly postgres db restore -a betzenstein-db < backup.sql
```

### Scaling

```bash
# Increase storage
fly volumes extend <volume-id> --size 10  # 10GB

# Upgrade to dedicated CPU
fly scale vm dedicated-cpu-1x -a betzenstein-db
```

---

## References

**Related ADRs:**
- ADR-012: PostgreSQL Database (database choice)
- ADR-016: Fly.io Backend Hosting (co-located backend)
- ADR-013: SQLAlchemy ORM (database access)

**Tools:**
- [Fly.io Postgres Documentation](https://fly.io/docs/postgres/)
- [Fly.io Private Networking](https://fly.io/docs/reference/private-networking/)
