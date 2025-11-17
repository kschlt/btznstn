# Fly.io Deployment Setup

## Overview

This guide walks you through setting up Fly.io for deploying the Betzenstein Booking backend API and PostgreSQL database.

**When needed:** Before deploying to production (typically Phase 8 or when ready for production)

**Prerequisites:** Credit card for account verification (free tier available)

---

## Manual Setup Steps

### 1. Create Fly.io Account

1. Go to [https://fly.io/app/sign-up](https://fly.io/app/sign-up)
2. Sign up with GitHub or email
3. Verify your email address
4. Add payment method (required for verification, but free tier available)

**Free Tier Includes:**
- Up to 3 shared-cpu VMs (256MB RAM each)
- 3GB persistent volume storage
- 160GB outbound data transfer

---

### 2. Install Fly.io CLI (flyctl)

**macOS:**
```bash
brew install flyctl
```

**Linux:**
```bash
curl -L https://fly.io/install.sh | sh
```

**Windows:**
```powershell
pwsh -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

**Verify installation:**
```bash
flyctl version
```

---

### 3. Authenticate CLI

```bash
flyctl auth login
```

This opens a browser window to authenticate. Log in with your Fly.io account.

**Verify authentication:**
```bash
flyctl auth whoami
```

---

### 4. Create Fly.io App (API)

```bash
cd backend
flyctl launch --no-deploy
```

**During launch wizard:**
- App name: `betzenstein-api` (or your preferred name)
- Region: `fra` (Frankfurt, Germany - for GDPR compliance)
- Add PostgreSQL? **No** (we'll create it separately)
- Add Redis? **No**

This creates `fly.toml` configuration file.

---

### 5. Create PostgreSQL Database

```bash
flyctl postgres create --name betzenstein-db --region fra
```

**Configuration options:**
- Choose **Development** configuration (single node, 1GB RAM)
- Region: **Frankfurt (fra)**
- This is free tier eligible

**Save the connection string** displayed after creation:
```
postgres://postgres:password@betzenstein-db.internal:5432
```

**Attach database to app:**
```bash
flyctl postgres attach betzenstein-db --app betzenstein-api
```

This automatically sets `DATABASE_URL` environment variable.

---

### 6. Configure Secrets

Set environment variables (secrets) for the backend:

```bash
flyctl secrets set \
  SECRET_KEY="$(openssl rand -hex 32)" \
  RESEND_API_KEY="re_your_key_here" \
  ALLOWED_ORIGINS="https://betzenstein.app" \
  --app betzenstein-api
```

**Required secrets:**
- `DATABASE_URL` - Auto-set by Postgres attach
- `SECRET_KEY` - Generated above (JWT signing)
- `RESEND_API_KEY` - From Resend setup
- `ALLOWED_ORIGINS` - Your frontend URL

**Verify secrets:**
```bash
flyctl secrets list --app betzenstein-api
```

---

### 7. Configure fly.toml

Update `api/fly.toml` with proper configuration:

```toml
app = "betzenstein-api"
primary_region = "fra"

[build]
  dockerfile = "Dockerfile"

[env]
  PYTHON_ENV = "production"
  LOG_LEVEL = "INFO"
  MAX_PARTY_SIZE = "10"
  FUTURE_HORIZON_MONTHS = "18"
  LONG_STAY_WARN_DAYS = "7"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

[[http_service.checks]]
  interval = "15s"
  timeout = "10s"
  grace_period = "5s"
  method = "get"
  path = "/health"

[[vm]]
  memory = "256mb"
  cpu_kind = "shared"
  cpus = 1
```

---

### 8. Create Dockerfile

Create `api/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Run migrations and start server
CMD alembic upgrade head && \
    uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### 9. Deploy API

```bash
flyctl deploy --app betzenstein-api
```

**Monitor deployment:**
```bash
flyctl logs --app betzenstein-api
```

**Check app status:**
```bash
flyctl status --app betzenstein-api
```

---

### 10. Verify Deployment

**Test API:**
```bash
curl https://betzenstein-api.fly.dev/health
```

**Expected response:**
```json
{"status": "healthy", "version": "0.1.0"}
```

**Check database connection:**
```bash
flyctl ssh console --app betzenstein-api
# Inside container:
python -c "import asyncio; from app.core.database import engine; print('DB connected')"
```

---

## Web Deployment (Vercel)

**Web is deployed separately on Vercel:**

1. Go to [https://vercel.com/new](https://vercel.com/new)
2. Import GitHub repository
3. Select `web/` as root directory
4. Set environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://betzenstein-api.fly.dev`
5. Deploy

Vercel handles everything automatically (build, deploy, CDN).

---

## Database Management

**Connect to production database:**
```bash
flyctl postgres connect --app betzenstein-db
```

**Run database migrations:**
```bash
flyctl ssh console --app betzenstein-api
alembic upgrade head
```

**Backup database:**
```bash
flyctl postgres db dump betzenstein-db > backup.sql
```

**Restore database:**
```bash
psql $(flyctl postgres conn-str -a betzenstein-db) < backup.sql
```

---

## Monitoring & Logs

**View application logs:**
```bash
flyctl logs --app betzenstein-api
```

**Monitor metrics:**
```bash
flyctl metrics --app betzenstein-api
```

**SSH into container:**
```bash
flyctl ssh console --app betzenstein-api
```

---

## Scaling

**Scale up VM resources:**
```bash
flyctl scale vm shared-cpu-1x --memory 512 --app betzenstein-api
```

**Scale to multiple regions:**
```bash
flyctl regions add ams --app betzenstein-api  # Amsterdam
```

**Auto-scaling:**
Configured in `fly.toml` with `auto_start_machines` and `auto_stop_machines`.

---

## Cost Management

**Free Tier Limits:**
- 3 shared-cpu VMs (256MB each)
- 3GB storage
- 160GB bandwidth/month

**Monitor usage:**
```bash
flyctl dashboard
```

**Estimated costs for Betzenstein (beyond free tier):**
- Single VM (512MB): ~$5/month
- PostgreSQL (1GB): Included in free tier
- Bandwidth: Likely within free tier

---

## Troubleshooting

**Issue:** Deployment fails
- **Solution:** Check `flyctl logs` for errors
- **Solution:** Verify Dockerfile syntax
- **Solution:** Ensure all secrets are set

**Issue:** Database connection fails
- **Solution:** Verify `DATABASE_URL` is set: `flyctl secrets list`
- **Solution:** Check database is running: `flyctl status --app betzenstein-db`

**Issue:** App won't start
- **Solution:** Check health check endpoint is accessible
- **Solution:** Verify internal port matches `fly.toml` (8000)

---

## Security Best Practices

**Secrets Management:**
- ✅ Use `flyctl secrets set` (never commit secrets)
- ✅ Rotate `SECRET_KEY` periodically
- ✅ Use strong database passwords

**Network Security:**
- ✅ Force HTTPS in `fly.toml`
- ✅ Use `.internal` hostnames for database (private network)
- ✅ Set CORS `ALLOWED_ORIGINS` correctly

**Database:**
- ✅ Regular backups (automated daily snapshots)
- ✅ Use connection pooling (configured in SQLAlchemy)
- ✅ Monitor query performance

---

## Deployment Checklist

Before deploying to production:

- [ ] Fly.io account created and verified
- [ ] flyctl CLI installed and authenticated
- [ ] PostgreSQL database created in Frankfurt region
- [ ] Secrets configured (SECRET_KEY, RESEND_API_KEY, etc.)
- [ ] Dockerfile created
- [ ] fly.toml configured
- [ ] Database migrations tested
- [ ] Health check endpoint working
- [ ] Web deployed on Vercel
- [ ] DNS configured (if using custom domain)
- [ ] SSL certificate verified (automatic with Fly.io)

---

## Related Documentation

- [Technology Stack](../architecture/technology-stack.md)
- [ADR-007: Deployment Strategy](../architecture/adr-007-deployment.md)
- [Phase 8: Polish & Production](../implementation/phase-8-polish.md)

---

## Summary

✅ **Account created** → Sign up at fly.io
✅ **CLI installed** → Install flyctl
✅ **App created** → `flyctl launch`
✅ **Database created** → `flyctl postgres create`
✅ **Secrets configured** → `flyctl secrets set`
✅ **Deployed** → `flyctl deploy`

**Next:** Monitor logs and verify all endpoints work correctly in production.
