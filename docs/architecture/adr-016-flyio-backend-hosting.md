# ADR-016: Fly.io Backend Hosting

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** Need EU-based hosting co-located with database
**Split from:** ADR-007: Deployment Strategy

---

## Context

Need hosting platform for FastAPI backend that:
- Runs Docker containers reliably
- Zero-downtime deployments
- EU region (GDPR compliance)
- Co-located with PostgreSQL database (low latency)
- Scales as needed (~10-20 users initially)
- AI-friendly (simple deployment, clear errors)
- Budget-friendly (free or cheap for MVP)

---

## Decision

Deploy FastAPI backend to **Fly.io** in **Frankfurt (FRA)** region.

---

## Rationale

### Why Fly.io vs AWS vs Heroku vs Railway?

**Fly.io (Chosen):**
- ✅ **EU region** - Frankfurt (GDPR compliant)
- ✅ **Co-located with database** - Same platform, same datacenter (<1ms latency)
- ✅ **Private network** - API connects to DB via `.internal` hostname (no egress fees)
- ✅ **Docker-based** - Standard Dockerfile, portable, AI-friendly
- ✅ **Zero-downtime** - Health checks + rolling updates
- ✅ **Simple CLI** - `fly deploy` one-command deploys
- ✅ **Free tier** - Sufficient for MVP

**AWS EC2 (Rejected):**
- ❌ Complex setup (VPCs, security groups, load balancers)
- ❌ Expensive ($20-50/month minimum)
- ❌ Not AI-friendly (too many options)

**Heroku (Rejected):**
- ❌ No free tier ($7/month minimum)
- ❌ Uncertain future (Salesforce ownership)

**Railway (Rejected):**
- ❌ Less mature
- ❌ Limited EU regions (Frankfurt not available initially)

---

## Key Benefits

### 1. Co-Location with Database (Ultra-Low Latency)

```bash
# Backend connects via private network
DATABASE_URL=postgresql://user:pass@betzenstein-db.internal:5432/betzenstein
```

**Latency:**
- Fly.io backend → Fly.io database: <1ms
- Fly.io backend → Railway database: 10-50ms

**Why this matters:**
- Conflict detection needs fast queries (BR-002)
- Concurrent approvals require low-latency locks (BR-024)

### 2. Docker-Based (AI-Friendly)

**Standard Dockerfile:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

AI can generate Dockerfiles, test locally, deploy to Fly.io.

### 3. Zero-Downtime Deployments

**Deployment strategy:**
1. Build new Docker image
2. Start new instances
3. Run health checks (`/health` endpoint)
4. If healthy, route traffic
5. Stop old instances

**Health check:**
```toml
# fly.toml
[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  path = "/health"
```

No downtime during deploys. Failed deployments automatically rolled back.

---

## Consequences

### Positive

✅ **EU region** - GDPR compliance (Frankfurt)
✅ **Co-located** - <1ms latency via private network
✅ **Docker-based** - Standard, portable, AI-friendly
✅ **Zero-downtime** - Health checks + rolling updates
✅ **Simple CLI** - `fly deploy` one-command
✅ **Free tier** - Sufficient for MVP
✅ **Auto-scaling** - Can scale later
✅ **HTTPS** - Automatic TLS certificates

### Negative

⚠️ **Vendor-specific config** - `fly.toml` is Fly.io-specific
⚠️ **Free tier limits** - Need to upgrade if traffic grows
⚠️ **Smaller community** - Compared to AWS/Heroku

### Neutral

➡️ **Container-based** - Not serverless (appropriate for FastAPI)
➡️ **Regional** - Can add more regions later

---

## Implementation Pattern

### Create Fly.io App

```bash
# Install CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Create app
fly launch --name betzenstein-api --region fra
```

### Configure fly.toml

```toml
# fly.toml
app = "betzenstein-api"
primary_region = "fra"

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = false  # Keep running
  min_machines_running = 1

  [[http_service.checks]]
    path = "/health"
    interval = "30s"
```

### Health Check Endpoint

```python
# app/main.py
@app.get("/health")
def health_check():
    """Health check endpoint for Fly.io."""
    return {"status": "ok"}
```

### Set Secrets

```bash
fly secrets set DATABASE_URL="postgresql://..."
fly secrets set RESEND_API_KEY="..."
```

### Deploy

```bash
fly deploy
```

---

## References

**Related ADRs:**
- ADR-001: Backend Framework (FastAPI)
- ADR-015: Fly.io Postgres Hosting (co-located database)
- ADR-018: GitHub Actions CI/CD (automated deployment)

**Tools:**
- [Fly.io Documentation](https://fly.io/docs/)
- [Fly.io Dockerfile Deployment](https://fly.io/docs/languages-and-frameworks/dockerfile/)
