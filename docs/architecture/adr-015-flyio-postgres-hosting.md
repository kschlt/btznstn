# ADR-015: Fly.io Postgres Hosting

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)
**Split from:** [ADR-003: Database & ORM](adr-003-database-orm.md) and [ADR-007: Deployment Strategy](adr-007-deployment.md)

---

## Context

We need to choose a hosting platform for the PostgreSQL database. The hosting must:

- Run PostgreSQL 15+ reliably
- Provide low-latency access from backend API
- Support EU data residency (GDPR compliance)
- Be always-on (no shutdown when idle)
- Include automated backups
- Fit within budget (free or cheap for MVP)

### Requirements

**From architecture:**
- Backend on Fly.io (Frankfurt) - see ADR-016
- Database should be co-located with backend (low latency)
- No cold starts or pausing (unlike Supabase free tier)

**From business requirements:**
- Small user base (~10-20 users)
- Moderate traffic (~100 requests/day)
- EU data residency for GDPR

---

## Decision

We will host PostgreSQL on **Fly.io Postgres** in the Frankfurt (FRA) region, co-located with the backend API.

---

## Rationale

### 1. Co-Location with Backend (Ultra-Low Latency)

**Fly.io Postgres on same platform as API** - Critical performance benefit.

**Key advantages:**
- ✅ **Private network** - API connects via `.internal` hostname (no public internet)
- ✅ **Same datacenter** - Backend and database in same Fly.io region
- ✅ **Ultra-low latency** - <1ms connection time
- ✅ **No egress fees** - Internal network traffic free

**Example (connection string):**
```bash
# Public connection (slower, costs egress)
DATABASE_URL=postgresql://user:pass@db.fly.io:5432/betzenstein

# Internal connection (faster, free)
DATABASE_URL=postgresql://user:pass@betzenstein-db.internal:5432/betzenstein
```

**Latency comparison:**
- Public internet: 10-50ms per query
- Fly.io internal: <1ms per query

**Why this matters for booking system:**
- Conflict detection requires fast queries (BR-002)
- Concurrent approvals need low-latency locks (BR-024)
- Calendar views query many bookings (performance critical)

### 2. Always On (Unlike Supabase)

**Critical requirement:** Database must not pause when idle.

**Fly.io Postgres:**
- ✅ **Always on** - Never pauses, never shuts down
- ✅ **No cold starts** - Instant connections
- ✅ **Predictable** - No surprise "database sleeping" errors

**Supabase comparison:**
- ⚠️ **Free tier pauses** - After 7 days inactivity
- ⚠️ **Slow wake-up** - 10-30 seconds to resume
- ⚠️ **$25/month** - For always-on (more expensive than Fly.io)

**User requirement:** Explicitly requested to avoid Supabase pause behavior.

### 3. EU Region (GDPR Compliance)

**Fly.io Frankfurt (FRA) region:**
- ✅ **Data stays in EU** - GDPR compliance
- ✅ **Low latency for German users** - <50ms
- ✅ **Same region as backend** - Co-located

**Alternative regions:**
- Amsterdam (AMS) - Also EU, slightly farther
- Paris (CDG) - Also EU, slightly farther

**Decision:** Frankfurt optimal for German users.

### 4. Same Platform as Backend (Simpler Operations)

**One platform = simpler management:**
- ✅ **One CLI** - `flyctl` for both API and database
- ✅ **One dashboard** - Fly.io console shows both
- ✅ **One account** - Single billing, single login
- ✅ **Simpler mental model** - Everything on Fly.io

**Alternative (Railway for database):**
- ⚠️ **Two platforms** - Fly.io (API) + Railway (DB)
- ⚠️ **Public internet** - Slower, egress fees
- ⚠️ **Two accounts** - More management overhead

**Decision:** Co-location wins over Railway's nicer UI.

### 5. Managed PostgreSQL (Less Operations)

**Fly.io handles:**
- ✅ **Automated backups** - Daily snapshots included
- ✅ **Monitoring** - Dashboard shows CPU, memory, disk
- ✅ **Scaling** - Increase storage/RAM as needed
- ✅ **Updates** - PostgreSQL version updates managed

**AI benefit:** AI doesn't manage database infrastructure.

### 6. Free Tier (Budget-Friendly)

**Fly.io free allowance:**
- 3GB persistent storage
- Shared CPU VM
- Included in Fly.io free tier (with backend app)

**Sufficient for MVP:**
- Small user base (~10-20 users)
- Low traffic (~100 requests/day)
- Limited data (~1000 bookings initially)

**Later scaling:**
- ~$1-2/month for dedicated resources
- Can upgrade incrementally

---

## Alternatives Considered

### Railway Postgres

**Pros:**
- Excellent UI/dashboard
- Good PostgreSQL management
- Simple connection strings
- Good free tier ($5 credit/month)

**Cons:**
- ❌ **Separate platform** - API on Fly.io, DB on Railway
- ❌ **Public internet** - Slight latency overhead
- ❌ **Egress fees** - Data transfer costs
- ❌ **One more service** - More accounts, more management

**Decision:** Co-location with backend on Fly.io is more important than Railway's nicer UI.

---

### Supabase

**Pros:**
- Managed PostgreSQL
- Good UI
- Generous free tier features

**Cons:**
- ❌ **Pauses when idle** - Free tier shuts down after ~7 days
- ❌ **Cold starts** - Slow to wake up (10-30 seconds)
- ❌ **$25/month for always-on** - More expensive than Fly.io
- ❌ **Extra features we don't need** - Auth, Realtime, Storage

**Decision:** Shutdown behavior unacceptable. Fly.io stays always-on.

---

### AWS RDS

**Pros:**
- Very mature
- High availability
- Advanced features

**Cons:**
- ❌ **Expensive** - $15-50/month minimum
- ❌ **Complex setup** - VPCs, security groups, etc.
- ❌ **Separate platform** - API on Fly.io, DB on AWS
- ❌ **Overkill** - Enterprise features for small app

**Decision:** Too complex and expensive for MVP.

---

### Heroku Postgres

**Pros:**
- Mature
- Good tooling
- Well-documented

**Cons:**
- ❌ **Expensive** - No free tier ($7/month minimum)
- ❌ **Separate platform** - API on Fly.io, DB on Heroku
- ❌ **Sunset concerns** - Salesforce ownership, uncertain future

**Decision:** Fly.io cheaper and more modern.

---

### Neon (Serverless Postgres)

**Pros:**
- Modern
- Serverless (autoscaling)
- Generous free tier

**Cons:**
- ❌ **Separate platform** - API on Fly.io, DB on Neon
- ❌ **Newer service** - Less proven
- ❌ **Cold starts on free tier** - Similar to Supabase

**Decision:** Fly.io co-location more important.

---

### Self-Hosted (VPS)

**Pros:**
- Full control
- Cheap (DigitalOcean $5/month)

**Cons:**
- ❌ **Manual operations** - Updates, backups, security
- ❌ **No high availability** - Single point of failure
- ❌ **AI can't manage ops** - Requires manual intervention

**Decision:** Managed platform removes operations burden.

---

## Consequences

### Positive

✅ **Ultra-low latency** - <1ms via private network
✅ **Always on** - No pausing or cold starts
✅ **Same platform** - Simpler management (one CLI, one dashboard)
✅ **EU region** - GDPR compliance (Frankfurt)
✅ **Automated backups** - Daily snapshots included
✅ **Free tier** - Sufficient for MVP
✅ **Co-located** - Same datacenter as backend
✅ **Managed** - No manual operations

### Negative

⚠️ **Fly.io-specific** - Migration to other platform requires effort
⚠️ **Limited UI** - Fly.io dashboard less polished than Railway/Supabase
⚠️ **Free tier limits** - 3GB storage (need to upgrade if growth exceeds)

### Neutral

➡️ **Connection pooling** - May need PgBouncer for high concurrency (not needed initially)
➡️ **Read replicas** - Can add if read-heavy workload (not needed for MVP)

---

## Implementation Notes

### Create Fly.io Postgres

**Using Fly.io CLI:**
```bash
# Create Postgres app
fly postgres create --name betzenstein-db --region fra

# Output:
# Username:    postgres
# Password:    <generated-password>
# Hostname:    betzenstein-db.internal
# Flycast:     fdaa:x:x:x::x
# Proxy port:  5432
# Postgres port: 5433
```

### Attach to Backend App

**Link database to API app:**
```bash
# Attach database to backend app
fly postgres attach --app betzenstein-api betzenstein-db

# Automatically sets DATABASE_URL secret in betzenstein-api
```

**Connection string format:**
```
postgresql://postgres:<password>@betzenstein-db.internal:5432/betzenstein
```

### Verify Connection

**From local machine (via Fly.io proxy):**
```bash
# Open proxy to database
fly proxy 5432 -a betzenstein-db

# Connect with psql
psql postgresql://postgres:<password>@localhost:5432/betzenstein
```

**From backend app (internal network):**
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

**Fly.io handles automatically:**
- Daily snapshots
- Retained for 7 days (free tier)
- Longer retention available (paid)

**Manual backup:**
```bash
# Dump database
fly postgres db dump -a betzenstein-db > backup.sql

# Restore
fly postgres db restore -a betzenstein-db < backup.sql
```

### Monitoring

**Fly.io dashboard:**
- CPU usage
- Memory usage
- Disk usage
- Connection count

**Query via CLI:**
```bash
fly status -a betzenstein-db
fly logs -a betzenstein-db
```

### Scaling

**Increase storage:**
```bash
fly volumes extend <volume-id> --size 10  # Increase to 10GB
```

**Upgrade to dedicated CPU:**
```bash
fly scale vm dedicated-cpu-1x -a betzenstein-db
```

---

## Validation

### Verify Connection from Backend

**Test query:**
```python
# Test from backend container
async def test_connection():
    async with AsyncSessionLocal() as session:
        result = await session.execute("SELECT 1")
        print(f"Connection works: {result.scalar()}")
```

**Expected:** Query succeeds, low latency (<5ms).

### Verify Backups

**Check backup schedule:**
```bash
fly postgres backup list -a betzenstein-db
```

**Expected:** Daily backups appear.

### Verify Private Network

**Check connection is using `.internal`:**
```bash
# From backend, print DATABASE_URL
echo $DATABASE_URL
```

**Expected:** Hostname ends with `.internal` (not `.fly.dev`).

---

## References

- [Fly.io Postgres Documentation](https://fly.io/docs/postgres/)
- [Fly.io Private Networking](https://fly.io/docs/reference/private-networking/)
- [Fly.io Regions](https://fly.io/docs/reference/regions/)

**Related ADRs:**
- [ADR-012: PostgreSQL Database](adr-012-postgresql-database.md) - Database choice
- [ADR-016: Fly.io Backend Hosting](adr-016-flyio-backend-hosting.md) - Co-located backend
- [ADR-007: Deployment Strategy](adr-007-deployment.md) - Original bundled decision (superseded)

---

## Changelog

- **2025-01-19:** Split from ADR-003 and ADR-007 - Fly.io Postgres hosting as independent decision
