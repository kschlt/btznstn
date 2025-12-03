# ADR-015: Fly.io Backend Hosting

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

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Hosting Platform | Fly.io | AWS EC2, Heroku, Railway |
| Region | Frankfurt (FRA) | Other regions |
| Connection | `.internal` hostname to database | Public internet connection |
| Deployment | Docker-based | Serverless, VM-based |

---

## Rationale

**Why Fly.io:**
- Fly.io provides EU region (Frankfurt) → **Constraint:** MUST deploy to Fly.io Frankfurt (FRA) region for GDPR compliance
- Fly.io co-locates with database → **Constraint:** MUST use `.internal` hostname for database connection (low latency, no egress fees)
- Fly.io uses Docker → **Constraint:** MUST use Docker-based deployment (standard Dockerfile, portable, AI-friendly)

**Why NOT AWS EC2:**
- AWS EC2 requires complex setup → **Violation:** VPCs, security groups, load balancers add complexity, violates simplicity requirement

**Why NOT Heroku:**
- Heroku has no free tier → **Violation:** $7/month minimum, violates budget-friendly requirement

**Why NOT Railway:**
- Railway has limited EU regions → **Violation:** Frankfurt not available initially, violates EU region requirement

## Consequences


### MUST (Required)

- MUST deploy to Fly.io Frankfurt (FRA) region - GDPR compliance, co-located with database
- MUST use Docker-based deployment - Standard Dockerfile, portable, AI-friendly
- MUST use `.internal` hostname for database connection - Private network, <1ms latency, no egress fees
- MUST implement health check endpoint (`/health`) - Required for zero-downtime deployments

### MUST NOT (Forbidden)

- MUST NOT use AWS EC2, Heroku, or Railway - Violates EU region, co-location, or budget requirements
- MUST NOT use public internet for database connection - Violates private network requirement
- MUST NOT skip health check endpoint - Violates zero-downtime deployment requirement

### Trade-offs

- Vendor-specific configuration - MUST use `fly.toml` for Fly.io configuration. MUST NOT use other platform configs. Migration to other platform requires effort.
- Free tier limits - MUST use free tier initially. MUST NOT exceed free tier limits without upgrading. Check resource usage before scaling.

### Code Examples

```toml
# ✅ CORRECT: Frankfurt region, health check configured
# fly.toml
app = "betzenstein-api"
primary_region = "fra"

[http_service]
  [[http_service.checks]]
    path = "/health"
    interval = "30s"

# ❌ WRONG: Wrong region
primary_region = "ord"  # Wrong region

# ❌ WRONG: Missing health check
# No health check configured
```

```python
# ✅ CORRECT: Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Fly.io."""
    return {"status": "ok"}

# ❌ WRONG: Missing health check endpoint
# No /health endpoint
```

### Applies To

- ALL backend deployment configuration (Phase 1)
- File patterns: `fly.toml`, `Dockerfile`, `app/main.py`

### Validation Commands

- `grep -r "primary_region.*fra" fly.toml` (should be present - Frankfurt region)
- `grep -r "/health" app/main.py` (should be present - health check endpoint)
- `grep -r "\.internal" fly.toml` (should be present - private network connection)

---

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - Backend Framework
- [ADR-016](adr-016-flyio-postgres-hosting.md) - Fly.io Postgres Hosting
- [ADR-018](adr-018-github-actions-cicd.md) - GitHub Actions CI/CD

---

## References

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - Backend Framework
- [ADR-016](adr-016-flyio-postgres-hosting.md) - Fly.io Postgres Hosting
- [ADR-018](adr-018-github-actions-cicd.md) - GitHub Actions CI/CD

**Tools:**
- [Fly.io Documentation](https://fly.io/docs/)
- [Fly.io Dockerfile Deployment](https://fly.io/docs/languages-and-frameworks/dockerfile/)

**Implementation:**
- `fly.toml` - Fly.io configuration
- `Dockerfile` - Docker container definition
- `app/main.py` - Health check endpoint
