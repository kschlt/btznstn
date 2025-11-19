# Deployment - CLAUDE Guide

## What's in This Section

Production deployment guidance for the Betzenstein Booking application:

- **Fly.io Backend Deployment** - Frankfurt region, health checks, auto-scaling
- **Vercel Frontend Deployment** - Global CDN, preview URLs, environment variables
- **Database Setup** - PostgreSQL 15+ on Fly.io, migrations, connection pooling
- **Email Service (Resend)** - API setup, retry logic, delivery monitoring
- **Background Jobs** - Auto-cleanup, archive purge, weekly digest scheduling
- **Environment Variables** - Production configuration, secrets management
- **Rate Limiting** - Server-side enforcement (BR-012)
- **Monitoring & Logging** - Health checks, error tracking

---

## Critical Production Requirements

### Business Rules Enforced in Production

| BR | Rule | Implementation | Critical |
|----|------|----------------|----------|
| **BR-010** | Tokens never expire, links always redirect | API validates tokens on every request | YES |
| **BR-012** | Rate limits (10/day email, 30/hour IP, 5/hour recovery) | Backend enforces BEFORE operations | YES |
| **BR-013** | Archive purge (monthly job) | Cron deletes old Canceled/Denied | YES |
| **BR-021** | Link recovery cooldown (60s) | Track last recovery time per email/IP | YES |
| **BR-022** | Email retries (3 attempts, exponential backoff: 2s, 4s, 8s) | Resend client with retry logic | YES |
| **BR-024** | First-action-wins (approve/deny) | SELECT FOR UPDATE on booking row | YES |
| **BR-028** | Auto-cleanup of past Pending (daily 00:01 Berlin time) | Cron transitions to Canceled | YES |
| **BR-029** | First-write-wins (create/extend booking) | Transaction with conflict detection | YES |

**All BRs must be enforced server-side. Client-side checks are UX only, never security.**

---

## Fly.io Backend Deployment

### Prerequisites

1. **Install Fly.io CLI:**
```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

2. **Login to Fly.io:**
```bash
flyctl auth login
```

3. **Create Fly.io Account:**
- Sign up at https://fly.io
- Add payment method (required for databases)

---

### Initial Setup

**1. Create Fly.io App:**
```bash
cd api/
flyctl launch

# Answer prompts:
# App name: betzenstein-api (or your choice)
# Region: Frankfurt, Germany (fra)
# Database: Yes (PostgreSQL 15+)
# Deploy now: No (we'll configure first)
```

This creates `fly.toml` configuration file.

**2. Configure `fly.toml`:**
```toml
app = "betzenstein-api"
primary_region = "fra"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8080"
  PYTHONUNBUFFERED = "1"
  TIMEZONE = "Europe/Berlin"

[[services]]
  internal_port = 8080
  protocol = "tcp"

  [[services.ports]]
    port = 80
    handlers = ["http"]
    force_https = true

  [[services.ports]]
    port = 443
    handlers = ["tls", "http"]

  [services.concurrency]
    type = "connections"
    hard_limit = 25
    soft_limit = 20

  [[services.tcp_checks]]
    interval = "10s"
    timeout = "2s"
    grace_period = "5s"

  [[services.http_checks]]
    interval = "10s"
    timeout = "2s"
    grace_period = "5s"
    method = "GET"
    path = "/health"
    protocol = "http"
    tls_skip_verify = false

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256
```

**3. Set Secrets:**
```bash
# Database URL (automatically set by Fly.io database creation)
flyctl secrets set DATABASE_URL="postgresql://..."

# JWT Secret (generate secure random string)
flyctl secrets set JWT_SECRET="$(openssl rand -hex 32)"

# Resend API Key (get from Resend dashboard)
flyctl secrets set RESEND_API_KEY="re_..."

# API Base URL
flyctl secrets set API_BASE_URL="https://betzenstein-api.fly.dev"

# Configuration (optional - defaults in code)
flyctl secrets set MAX_PARTY_SIZE="10"
flyctl secrets set FUTURE_HORIZON_MONTHS="18"
flyctl secrets set LONG_STAY_WARN_DAYS="7"
flyctl secrets set RATE_LIMIT_BOOKING_PER_DAY="10"
flyctl secrets set RATE_LIMIT_REQUESTS_PER_HOUR="30"
flyctl secrets set RATE_LIMIT_RECOVERY_PER_HOUR="5"
flyctl secrets set RATE_LIMIT_RECOVERY_COOLDOWN_SECONDS="60"
```

**4. Create Dockerfile (if not exists):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations on startup (optional - can be separate deploy step)
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8080"]
```

**5. Deploy:**
```bash
flyctl deploy
```

**6. Verify Deployment:**
```bash
# Check app status
flyctl status

# Check health endpoint
curl https://betzenstein-api.fly.dev/health

# View logs
flyctl logs

# Check database connection
flyctl postgres connect -a <db-app-name>
```

---

### Database Setup (Fly.io PostgreSQL)

**1. Create PostgreSQL Database:**
```bash
flyctl postgres create \
  --name betzenstein-db \
  --region fra \
  --initial-cluster-size 1 \
  --vm-size shared-cpu-1x \
  --volume-size 10
```

**2. Attach Database to App:**
```bash
flyctl postgres attach betzenstein-db -a betzenstein-api
```

This automatically sets `DATABASE_URL` secret.

**3. Run Migrations:**
```bash
# Option A: Run locally pointing to Fly.io database
flyctl proxy 5432 -a betzenstein-db
# In another terminal:
DATABASE_URL="postgresql://..." alembic upgrade head

# Option B: Run migrations in Fly.io machine
flyctl ssh console -a betzenstein-api
cd /app
alembic upgrade head
exit
```

**4. Verify Indexes Created:**
```sql
-- Connect to database
flyctl postgres connect -a betzenstein-db

-- Check indexes
\di

-- Expected indexes:
-- idx_bookings_date_range (start_date, end_date, status) - GiST
-- idx_bookings_status
-- idx_bookings_last_activity_at_desc
-- idx_approvals_booking_id
-- idx_approvals_party_id
```

**5. Configure Connection Pooling (PgBouncer):**

Fly.io PostgreSQL includes PgBouncer. Configure in `fly.toml`:
```toml
[env]
  PGBOUNCER_POOL_SIZE = "20"
  PGBOUNCER_MAX_CLIENT_CONN = "100"
```

---

### Health Check Endpoint

**Required: GET /health → 200 OK**

```python
# app/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    """
    Health check endpoint for Fly.io monitoring.
    Returns 200 OK if service is healthy.
    """
    # Optional: Check database connection
    # try:
    #     await db.execute("SELECT 1")
    # except Exception:
    #     raise HTTPException(status_code=503, detail="Database unhealthy")

    return {"status": "ok", "service": "betzenstein-api"}
```

---

## Resend Email Service Setup

### Prerequisites

1. **Create Resend Account:**
   - Sign up at https://resend.com
   - Verify email address
   - Add payment method (if needed)

2. **Get API Key:**
   - Dashboard → API Keys → Create API Key
   - Copy key (starts with `re_`)
   - Store in Fly.io secrets: `flyctl secrets set RESEND_API_KEY="re_..."`

---

### Domain Configuration

**1. Add Domain to Resend:**
- Resend Dashboard → Domains → Add Domain
- Enter: `yourdomain.com`

**2. Configure DNS Records:**
Add these DNS records to your domain:

```
Type: TXT
Name: resend._domainkey
Value: [provided by Resend]

Type: MX
Name: @
Value: feedback-smtp.us-east-1.amazonses.com
Priority: 10
```

**3. Verify Domain:**
- Resend Dashboard → Domains → Verify
- Wait for DNS propagation (up to 48 hours, usually <1 hour)

**4. Set From Address:**
```python
# app/services/email_service.py
FROM_EMAIL = "no-reply@yourdomain.com"
FROM_NAME = "Betzenstein Buchungssystem"
```

---

### Email Service Implementation

**1. Install Resend SDK:**
```bash
pip install resend
```

**2. Create Email Service:**
```python
# app/services/email_service.py
import asyncio
import logging
from typing import Optional
import resend

logger = logging.getLogger(__name__)

# Initialize Resend client
resend.api_key = os.getenv("RESEND_API_KEY")

FROM_EMAIL = "no-reply@yourdomain.com"
FROM_NAME = "Betzenstein Buchungssystem"

async def send_email_with_retry(
    to: str,
    subject: str,
    html: str,
    max_attempts: int = 3
) -> bool:
    """
    Send email with retry logic per BR-022.
    Retries: 3 attempts with exponential backoff (2s, 4s, 8s).
    """
    delays = [2, 4, 8]  # BR-022: Exponential backoff

    for attempt in range(max_attempts):
        try:
            params = {
                "from": f"{FROM_NAME} <{FROM_EMAIL}>",
                "to": [to],
                "subject": subject,
                "html": html
            }

            # Send email
            response = await asyncio.to_thread(resend.Emails.send, params)

            logger.info(
                f"Email sent successfully to {to} (attempt {attempt + 1})",
                extra={"email_id": response.get("id"), "to": to}
            )
            return True

        except resend.exceptions.ResendError as e:
            # Permanent error (e.g., invalid email) - don't retry
            if e.status_code in [400, 404]:
                logger.error(
                    f"Permanent email error to {to}: {e}",
                    exc_info=True
                )
                return False

            # Transient error - retry
            if attempt < max_attempts - 1:
                delay = delays[attempt]
                logger.warning(
                    f"Email failed to {to} (attempt {attempt + 1}), "
                    f"retrying in {delay}s: {e}"
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"Email failed to {to} after {max_attempts} attempts",
                    exc_info=True
                )
                return False

    return False
```

**3. Email Templates (German Copy):**

See `/docs/specification/notifications.md` for all 11 email templates with exact German copy.

Example:
```python
# app/templates/email/booking_created.html
def booking_created_email(
    requester_name: str,
    start_date: str,
    end_date: str,
    party_size: int,
    token: str
) -> str:
    """
    Email sent to requester when booking is created.
    German copy from notifications.md.
    """
    return f"""
    <h2>Hallo {requester_name},</h2>
    <p>deine Anfrage für <strong>{start_date}–{end_date}</strong> ({party_size} Personen) wurde erfasst.</p>
    <p>Du erhältst E-Mails, sobald entschieden wurde.</p>
    <p><a href="https://yourdomain.com/booking/{token}">Details ansehen</a></p>
    """
```

---

### Monitoring Email Delivery

**1. Resend Dashboard:**
- View sent emails
- Check delivery status
- Monitor bounce rates
- Track open/click rates (optional)

**2. Logging:**
```python
# All email sends logged with:
# - Recipient email
# - Subject
# - Email ID (from Resend)
# - Success/failure status
# - Retry attempts
```

**3. Alerts (Optional):**
- Set up alerts for high bounce rates
- Monitor failed delivery attempts
- Track API quota usage

---

## Vercel Frontend Deployment

### Prerequisites

1. **GitHub Repository:**
   - Push code to GitHub repository
   - Ensure `main` branch is up to date

2. **Vercel Account:**
   - Sign up at https://vercel.com
   - Connect GitHub account

---

### Deployment Steps

**1. Import Project:**
- Vercel Dashboard → Add New → Project
- Import Git Repository → Select your repo
- Framework Preset: Next.js
- Root Directory: `web/` (if applicable)
- Click "Deploy"

**2. Configure Environment Variables:**

Vercel Dashboard → Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://betzenstein-api.fly.dev
```

**3. Build & Deploy Settings:**
- Build Command: `npm run build`
- Output Directory: `.next`
- Install Command: `npm install`
- Framework: Next.js

**4. Production Domain:**
- Vercel Dashboard → Settings → Domains
- Add custom domain (e.g., `betzenstein.yourdomain.com`)
- Configure DNS: Add CNAME record pointing to Vercel

**5. Automatic Deployments:**
- Push to `main` → Production deployment
- Pull requests → Preview deployments
- Branches → Preview deployments (optional)

---

## Background Jobs Setup

### Job Scheduling (APScheduler)

**1. Install APScheduler:**
```bash
pip install apscheduler pytz
```

**2. Create Job Scheduler:**
```python
# app/jobs/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

berlin_tz = pytz.timezone('Europe/Berlin')

def start_scheduler():
    scheduler = AsyncIOScheduler(timezone=berlin_tz)

    # BR-028: Auto-cleanup of past Pending bookings
    # Daily at 00:01 Europe/Berlin
    scheduler.add_job(
        auto_cleanup_past_pending,
        CronTrigger(hour=0, minute=1, timezone=berlin_tz),
        id='auto_cleanup',
        name='Auto-cleanup past pending bookings'
    )

    # BR-013: Archive purge
    # Monthly on 1st at 02:00 Europe/Berlin
    scheduler.add_job(
        purge_old_archived_bookings,
        CronTrigger(day=1, hour=2, minute=0, timezone=berlin_tz),
        id='archive_purge',
        name='Purge old archived bookings'
    )

    # BR-009: Weekly digest
    # Sunday at 09:00 Europe/Berlin
    scheduler.add_job(
        send_weekly_digest,
        CronTrigger(day_of_week='sun', hour=9, minute=0, timezone=berlin_tz),
        id='weekly_digest',
        name='Send weekly digest to approvers'
    )

    scheduler.start()
    return scheduler
```

**3. Job Implementations:**

See `/docs/implementation/phase-8-polish.md` for complete job specifications.

Key jobs:
- **Auto-cleanup** (BR-028): Transition past Pending → Canceled, move to Archive
- **Archive purge** (BR-013): Delete old Canceled (>1 year), past Denied
- **Weekly digest** (BR-009): Email approvers with old outstanding items

---

## Rate Limiting Implementation

### Server-Side Enforcement (BR-012)

**1. Rate Limit Middleware:**
```python
# app/middleware/rate_limit.py
from fastapi import HTTPException, Request
from datetime import datetime, timedelta
import redis

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

BOOKING_LIMIT_PER_DAY = 10
REQUESTS_LIMIT_PER_HOUR = 30
RECOVERY_LIMIT_PER_HOUR = 5
RECOVERY_COOLDOWN_SECONDS = 60

async def check_booking_rate_limit(email: str):
    """BR-012: 10 bookings per day per email."""
    key = f"booking_limit:{email}:{datetime.now().date()}"
    count = redis_client.get(key)

    if count and int(count) >= BOOKING_LIMIT_PER_DAY:
        raise HTTPException(
            status_code=429,
            detail="Du hast heute bereits 10 Anfragen gestellt. Bitte versuche es morgen erneut."
        )

    # Increment counter
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, 86400)  # 24 hours
    pipe.execute()

async def check_ip_rate_limit(request: Request):
    """BR-012: 30 requests per hour per IP."""
    ip = request.client.host
    key = f"ip_limit:{ip}:{datetime.now().hour}"
    count = redis_client.get(key)

    if count and int(count) >= REQUESTS_LIMIT_PER_HOUR:
        raise HTTPException(
            status_code=429,
            detail="Zu viele Anfragen. Bitte versuche es später erneut."
        )

    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, 3600)  # 1 hour
    pipe.execute()

async def check_recovery_rate_limit(email: str):
    """BR-012: 5 recovery requests per hour per email."""
    key = f"recovery_limit:{email}:{datetime.now().hour}"
    count = redis_client.get(key)

    if count and int(count) >= RECOVERY_LIMIT_PER_HOUR:
        raise HTTPException(
            status_code=429,
            detail="Zu viele Wiederherstellungsanfragen. Bitte versuche es später erneut."
        )

    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, 3600)
    pipe.execute()

async def check_recovery_cooldown(email: str):
    """BR-021: 60-second cooldown on link recovery."""
    key = f"recovery_cooldown:{email}"
    last_recovery = redis_client.get(key)

    if last_recovery:
        elapsed = datetime.now().timestamp() - float(last_recovery)
        if elapsed < RECOVERY_COOLDOWN_SECONDS:
            # Don't reveal if email exists - always show success
            return True  # Cooldown active, but show success

    # Update last recovery time
    redis_client.setex(
        key,
        RECOVERY_COOLDOWN_SECONDS,
        datetime.now().timestamp()
    )
    return False  # No cooldown
```

---

## Monitoring & Logging

### Fly.io Logs

**View logs:**
```bash
# Live logs
flyctl logs

# Last 100 lines
flyctl logs --tail 100

# Filter by app
flyctl logs -a betzenstein-api
```

**Log format:**
- Timestamp
- Level (INFO, WARNING, ERROR)
- Message
- Extra context (user_id, booking_id, email, etc.)

### Error Tracking (Optional - Sentry)

**1. Install Sentry:**
```bash
pip install sentry-sdk
```

**2. Initialize:**
```python
# app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)
```

**3. Set secret:**
```bash
flyctl secrets set SENTRY_DSN="https://..."
```

---

## Production Checklist

Before going live:

- [ ] Fly.io app deployed to Frankfurt region
- [ ] Health check endpoint returns 200 OK
- [ ] Database migrations applied
- [ ] All indexes created and verified
- [ ] Secrets configured (DATABASE_URL, JWT_SECRET, RESEND_API_KEY)
- [ ] Resend domain verified and sending emails
- [ ] Vercel frontend deployed and connected to backend
- [ ] Rate limiting enforced (tested with >10 bookings/day)
- [ ] Background jobs scheduled and tested
  - [ ] Auto-cleanup runs at 00:01 Berlin time
  - [ ] Archive purge runs monthly
  - [ ] Weekly digest runs Sunday 09:00 Berlin time
- [ ] Email retry logic working (3 attempts, exponential backoff)
- [ ] Concurrency safety verified (SELECT FOR UPDATE)
- [ ] HTTPS enforced (all HTTP → HTTPS redirect)
- [ ] CORS configured (allow frontend origin)
- [ ] Security headers present (HSTS, X-Frame-Options)
- [ ] Error logging working (Fly.io logs or Sentry)
- [ ] Smoke tests pass (create booking, approve, deny, edit, cancel)
- [ ] Load test: 100 concurrent calendar requests handled
- [ ] Timezone handling correct (Europe/Berlin for business logic)

---

## Common Production Issues

### Issue: Database Connection Exhausted

**Symptom:** "Too many connections" error

**Solution:**
- Increase connection pool size in `fly.toml`
- Use PgBouncer (included in Fly.io PostgreSQL)
- Close database sessions properly (use context managers)

---

### Issue: Email Delivery Failures

**Symptom:** Emails not arriving

**Checklist:**
1. Resend domain verified (check DNS)
2. Resend API key correct
3. From address matches verified domain
4. Check Resend dashboard for bounce/failure logs
5. Verify retry logic (logs show 3 attempts)

---

### Issue: Background Jobs Not Running

**Symptom:** Auto-cleanup or digest not executing

**Solution:**
1. Check APScheduler logs: `flyctl logs | grep "scheduler"`
2. Verify timezone (must be Europe/Berlin)
3. Check cron syntax (hour, minute, day_of_week)
4. Ensure scheduler started in main app

---

### Issue: Rate Limiting Not Working

**Symptom:** Users can submit >10 bookings/day

**Solution:**
1. Verify Redis running (or use in-memory store)
2. Check middleware applied to booking endpoint
3. Test with API calls (not just UI)
4. Verify rate limit counters reset correctly

---

## Next Steps

1. **Test deployment locally:**
   - Run backend with production-like settings
   - Test all endpoints
   - Verify rate limiting
   - Test background jobs

2. **Deploy to staging (optional):**
   - Create `betzenstein-api-staging` app
   - Test with real data
   - Run smoke tests

3. **Deploy to production:**
   - Follow checklist above
   - Monitor logs for first 24 hours
   - Test critical flows (create, approve, email)

4. **Post-launch monitoring:**
   - Check email delivery rates
   - Monitor error logs
   - Verify background jobs execute
   - Track API performance (response times)

---

**For detailed specifications, see:**
- `/docs/implementation/phase-8-polish.md` - US-8.3 Production Deployment
- `/docs/foundation/business-rules.md` - BR-012, BR-021, BR-022, BR-024, BR-028, BR-029
- `/docs/constraints/non-functional.md` - Performance targets, availability
