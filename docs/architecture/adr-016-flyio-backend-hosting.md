# ADR-016: Fly.io Backend Hosting

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)
**Split from:** [ADR-007: Deployment Strategy](adr-007-deployment.md)

---

## Context

We need to choose a hosting platform for the FastAPI backend. The hosting must:

- Run Docker containers reliably
- Support zero-downtime deployments
- Provide EU region (GDPR compliance)
- Co-locate with PostgreSQL database (low latency)
- Scale as needed (initially small, ~10-20 users)
- Be AI-friendly (simple deployment, clear errors)
- Fit within budget (free or cheap for MVP)

### Requirements

**From architecture:**
- Backend is FastAPI + Python 3.11+ (ADR-001)
- Database on Fly.io Postgres Frankfurt (ADR-015)
- Health checks required for zero-downtime
- HTTPS enforced

---

## Decision

We will deploy the FastAPI backend to **Fly.io** in the **Frankfurt (FRA)** region.

---

## Rationale

### 1. EU Region (GDPR Compliance)

**Fly.io Frankfurt (FRA) region:**
- ✅ **Data stays in EU** - GDPR compliant
- ✅ **Low latency for German users** - <50ms
- ✅ **Close to database** - Co-located in same region (see ADR-015)

**Why GDPR matters:**
- Application stores personal data (names, emails)
- EU data residency requirement
- Frankfurt region ensures compliance

### 2. Co-Location with Database (Ultra-Low Latency)

**Backend and database in same Fly.io region:**
- ✅ **Private network** - API connects to database via `.internal` hostname
- ✅ **Same datacenter** - Sub-millisecond latency
- ✅ **No egress fees** - Internal traffic is free
- ✅ **No public internet** - More secure

**Example (connection):**
```bash
# Backend connects via private network
DATABASE_URL=postgresql://user:pass@betzenstein-db.internal:5432/betzenstein
```

**Latency comparison:**
- Fly.io backend → Fly.io database: <1ms
- Fly.io backend → Railway database: 10-50ms

**Why this matters:**
- Booking conflict detection needs fast queries (BR-002)
- Concurrent approval handling requires low-latency locks (BR-024)

### 3. Docker-Based Deployments (AI-Friendly)

**Fly.io uses standard Docker:**
- ✅ **Standard Dockerfile** - No proprietary build system
- ✅ **AI knows Docker** - Massive training data
- ✅ **Local testing** - Same Dockerfile works locally
- ✅ **No vendor lock-in** - Can run anywhere Docker runs

**Example (Dockerfile):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**AI benefit:** AI can generate Dockerfiles, test locally, deploy to Fly.io.

### 4. Zero-Downtime Deployments

**Fly.io deployment strategy:**
1. Build new Docker image
2. Start new VM instances
3. Run health checks (`/health` endpoint)
4. If healthy, route traffic to new instances
5. Stop old instances

**Health check configuration:**
```toml
# fly.toml
[[http_service.checks]]
  grace_period = "10s"
  interval = "30s"
  method = "GET"
  timeout = "5s"
  path = "/health"
```

**Why this matters:**
- No downtime during deploys
- Users never see errors
- Failed deployments automatically rolled back

### 5. Simple CLI (flyctl)

**One command to deploy:**
```bash
fly deploy
```

**Common operations:**
```bash
fly status          # Check app status
fly logs            # View logs
fly ssh console     # SSH into container
fly secrets set KEY=value  # Set environment variables
```

**AI benefit:** Simple commands, clear error messages.

### 6. Auto-Scaling (Future-Proofing)

**Fly.io supports:**
- ✅ **Horizontal scaling** - Add more VMs
- ✅ **Multiple regions** - Deploy to multiple locations
- ✅ **Auto-scaling** - Scale based on load

**MVP: Single instance** (free tier sufficient)

**Later:**
```bash
fly scale count 2  # Run 2 instances
fly regions add ams  # Add Amsterdam region
```

### 7. Free Tier (Budget-Friendly)

**Fly.io free allowance:**
- 3 shared-CPU VMs
- 160GB outbound data transfer/month
- HTTPS included
- Custom domains included

**Sufficient for MVP:**
- Small user base (~10-20 users)
- Low traffic (~100 requests/day)
- Simple backend (FastAPI is efficient)

**Later:** ~$5-10/month for dedicated resources.

---

## Alternatives Considered

### AWS (EC2 + ALB)

**Pros:**
- Very mature
- Full control
- Enterprise-grade

**Cons:**
- ❌ **Complex setup** - VPCs, security groups, load balancers
- ❌ **Expensive** - EC2 + ALB ~$20-50/month minimum
- ❌ **Not AI-friendly** - Too many configuration options
- ❌ **Overkill** - Enterprise features for small app

**Decision:** Fly.io simpler and cheaper for MVP.

---

### Heroku

**Pros:**
- Simple
- Mature
- Good docs

**Cons:**
- ❌ **No free tier** - $7/month minimum
- ❌ **Expensive** - $7/dyno vs Fly.io free tier
- ❌ **Uncertain future** - Salesforce ownership concerns
- ❌ **US-centric** - EU regions more expensive

**Decision:** Fly.io cheaper and more modern.

---

### Railway

**Pros:**
- Excellent UI
- Simple deployments
- Good free tier ($5 credit/month)

**Cons:**
- ❌ **Less mature** - Newer platform
- ❌ **Smaller community** - Less AI training data
- ❌ **Limited EU regions** - Frankfurt not available initially

**Decision:** Fly.io more mature, better EU support.

---

### Render

**Pros:**
- Simple
- Free tier
- Good for full-stack

**Cons:**
- ❌ **Slower cold starts** - Free tier spins down
- ❌ **Limited EU regions**
- ❌ **Less AI training data**

**Decision:** Fly.io better EU support, no cold starts.

---

### Vercel Serverless Functions

**Pros:**
- Same platform as frontend
- Auto-scaling
- Global CDN

**Cons:**
- ❌ **Not designed for FastAPI** - Serverless doesn't match FastAPI patterns
- ❌ **Stateless limitations** - Hard to manage database connections
- ❌ **Cold starts** - Slower than always-on containers

**Decision:** FastAPI needs persistent containers, not serverless.

---

## Consequences

### Positive

✅ **EU region** - GDPR compliance (Frankfurt)
✅ **Co-located with database** - <1ms latency via private network
✅ **Docker-based** - Standard, portable, AI-friendly
✅ **Zero-downtime** - Health checks + rolling updates
✅ **Simple CLI** - `fly deploy` one-command deploys
✅ **Free tier** - Sufficient for MVP
✅ **Auto-scaling** - Can scale later if needed
✅ **HTTPS** - Automatic TLS certificates

### Negative

⚠️ **Vendor-specific config** - `fly.toml` is Fly.io-specific
⚠️ **Free tier limits** - Need to upgrade if traffic grows
⚠️ **Smaller community** - Compared to AWS/Heroku

### Neutral

➡️ **Container-based** - Not serverless (appropriate for FastAPI)
➡️ **Regional deployment** - Can add more regions later if needed

---

## Implementation Notes

### Create Fly.io App

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Create app (interactive)
fly launch --name betzenstein-api --region fra

# Or create manually
fly apps create betzenstein-api --org personal
```

### Configure fly.toml

```toml
# fly.toml
app = "betzenstein-api"
primary_region = "fra"  # Frankfurt, Germany

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"
  PYTHON_ENV = "production"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = false  # Keep running (important!)
  auto_start_machines = true
  min_machines_running = 1

  [[http_service.checks]]
    grace_period = "10s"
    interval = "30s"
    method = "GET"
    timeout = "5s"
    path = "/health"

[[services]]
  protocol = "tcp"
  internal_port = 8000

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]
```

### Health Check Endpoint

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health_check():
    """Health check endpoint for Fly.io."""
    return {"status": "ok"}
```

### Set Secrets

```bash
# Set environment variables
fly secrets set DATABASE_URL="postgresql://..."
fly secrets set JWT_SECRET="..."
fly secrets set RESEND_API_KEY="..."
```

### Deploy

```bash
# Deploy app
fly deploy

# Check status
fly status

# View logs
fly logs

# Open app
fly open
```

### Custom Domain

```bash
# Add custom domain
fly certs add api.betzenstein.app

# Fly.io provides DNS records to configure
```

---

## Validation

### Verify Deployment

```bash
# Check app is running
fly status -a betzenstein-api

# Expected: Status = running, Health = passing
```

### Verify Health Check

```bash
curl https://betzenstein-api.fly.dev/health
# Expected: {"status": "ok"}
```

### Verify Database Connection

```bash
# Check logs for database connection
fly logs -a betzenstein-api

# Expected: No database connection errors
```

### Verify HTTPS

```bash
curl -I https://betzenstein-api.fly.dev
# Expected: HTTP/2 200, TLS certificate valid
```

---

## References

- [Fly.io Documentation](https://fly.io/docs/)
- [Fly.io Regions](https://fly.io/docs/reference/regions/)
- [Fly.io Health Checks](https://fly.io/docs/reference/configuration/#services-http_checks)
- [Fly.io Dockerfile Deployment](https://fly.io/docs/languages-and-frameworks/dockerfile/)

**Related ADRs:**
- [ADR-001: API Framework](adr-001-backend-framework.md) - FastAPI backend
- [ADR-015: Fly.io Postgres Hosting](adr-015-flyio-postgres-hosting.md) - Co-located database
- [ADR-018: GitHub Actions CI/CD](adr-018-github-actions-cicd.md) - Automated deployment

---

## Changelog

- **2025-01-19:** Split from ADR-007 - Fly.io backend hosting as independent decision
