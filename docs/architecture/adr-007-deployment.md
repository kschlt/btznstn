# ADR-007: Deployment Strategy

**Status:** Accepted
**Date:** 2025-01-17
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)

---

## Context

We need a deployment strategy for the booking application that:

- **Deploys backend (FastAPI) reliably** - Zero-downtime updates
- **Deploys frontend (Next.js) reliably** - Fast, global CDN
- **Manages database migrations** - Safe, reversible schema changes
- **Supports multiple environments** - Dev, Staging, Production
- **Automates via CI/CD** - GitHub Actions on push to main
- **Is AI-friendly** - Simple commands, clear error messages
- **Stays within budget** - Free/cheap tiers for MVP

### Requirements

**Backend deployment:**
- EU region (GDPR, low latency for German users)
- PostgreSQL connection from backend
- Email service (Resend) API access
- Environment variables (secrets)
- Health checks + auto-restart

**Frontend deployment:**
- Global CDN (fast page loads)
- Edge caching for static assets
- Preview deployments for PRs
- Environment variables (API URL)

**Database:**
- Managed PostgreSQL (backups, monitoring)
- Connection pooling
- Migration runner

**CI/CD:**
- Run tests before deploy
- Type-check before deploy
- Deploy on push to `main`
- Manual approval for production (optional)

---

## Decision

We will deploy using:

- **Backend:** Fly.io (Frankfurt region)
- **Frontend:** Vercel (global CDN)
- **Database:** Fly.io Postgres (Frankfurt region, co-located with backend)
- **CI/CD:** GitHub Actions

---

## Rationale

### 1. Fly.io - Backend Hosting

**Why Fly.io:**

#### a) EU/German Region Support

- ✅ **Frankfurt (FRA) region** - Low latency for German users
- ✅ **GDPR compliant** - Data stays in EU
- ✅ **Close to users** - <50ms latency within Germany

**Example:**
```toml
# fly.toml
app = "betzenstein-api"
primary_region = "fra"  # Frankfurt, Germany

[env]
  DATABASE_URL = "postgresql://..."
  RESEND_API_KEY = "re_..."
```

#### b) Docker-Based Deployments

**AI-friendly:** Standard Dockerfile, no proprietary config.

**Example:**
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Deploy:**
```bash
fly deploy
```

**AI benefit:** AI knows Docker extremely well. Can generate Dockerfiles easily.

#### c) Zero-Downtime Deployments

**Fly.io strategy:**
- Starts new instances
- Health checks pass
- Routes traffic to new instances
- Shuts down old instances

**Health check:**
```python
# main.py
@app.get("/health")
def health():
    return {"status": "ok"}
```

```toml
# fly.toml
[http_service]
  internal_port = 8000
  force_https = true

  [[http_service.checks]]
    grace_period = "10s"
    interval = "30s"
    method = "GET"
    timeout = "5s"
    path = "/health"
```

**Result:** No downtime during deploys.

#### d) Auto-Scaling (Future)

**Fly.io supports:**
- Horizontal scaling (multiple instances)
- Auto-scaling based on load
- Global regions (if needed)

**MVP:** Single instance (free tier).

**Later:**
```bash
fly scale count 2  # Run 2 instances
fly regions add ams  # Add Amsterdam region
```

#### e) Free Tier

**Fly.io free allowance:**
- 3 shared-cpu VMs
- 3GB persistent storage
- 160GB outbound data transfer/month

**Sufficient for MVP.**

### 2. Vercel - Frontend Hosting

**Why Vercel:**

#### a) Zero-Config Next.js Deployment

**Vercel is made by Next.js creators:**
- ✅ **Push to deploy** - Auto-detects Next.js, builds, deploys
- ✅ **No configuration** - Works out of box
- ✅ **Preview deployments** - Every PR gets a unique URL
- ✅ **Global CDN** - Cloudflare-backed, <100ms worldwide

**Example:**
```bash
# Connect GitHub repo → Vercel auto-deploys on push
# No config needed!
```

**AI benefit:** Zero config = Less to go wrong.

#### b) Edge Caching + CDN

**Vercel architecture:**
- Static assets cached at edge (HTML, CSS, JS, images)
- API routes run on serverless functions (if needed)
- ISR (Incremental Static Regeneration) for calendar pages

**Example (ISR for calendar page):**
```typescript
// app/calendar/page.tsx
export const revalidate = 60  // Revalidate every 60 seconds

export default async function CalendarPage() {
  const bookings = await fetchBookings()
  return <Calendar bookings={bookings} />
}
```

**Result:**
- First user: Fetches from API → Generates page → Caches at edge
- Next 59 seconds: All users get cached page (instant load)
- After 60s: Regenerates in background

**Fast for users, low load on backend.**

#### c) Preview Deployments

**Every PR gets a unique URL:**

**Workflow:**
1. AI creates PR with feature
2. Vercel auto-deploys to `https://betzenstein-pr-123.vercel.app`
3. User reviews feature on preview URL
4. User merges PR → Deploys to production

**AI benefit:** Test changes in production-like environment before merge.

#### d) Environment Variables

**Vercel dashboard:**
- Production env vars (e.g., `NEXT_PUBLIC_API_URL=https://api.betzenstein.app`)
- Preview env vars (e.g., `NEXT_PUBLIC_API_URL=https://betzenstein-api-staging.fly.dev`)

**Next.js reads:**
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL
```

**AI benefit:** Same code works in dev, preview, production.

#### e) Free Tier

**Vercel free (Hobby plan):**
- Unlimited deployments
- 100GB bandwidth/month
- Automatic HTTPS
- Preview deployments

**Sufficient for MVP.**

### 3. Fly.io Postgres

**Why Fly.io Postgres:**

#### a) Co-Located with Backend

**Same platform benefits:**
- ✅ **Private network** - Backend connects via `.internal` hostname (no public internet)
- ✅ **Ultra-low latency** - Same region, same datacenter
- ✅ **Simple management** - One platform, one CLI (`flyctl`)
- ✅ **EU region** - Frankfurt, data stays in EU (GDPR)

**AI benefit:** Simpler mental model - everything on Fly.io.

#### b) Always On (Unlike Supabase)

**No shutdown/pause:**
- ✅ **Always on** - Doesn't pause when idle
- ✅ **No cold starts** - Instant connections
- ✅ **Predictable** - No "database sleeping" errors

**User requirement:** This was critical - avoid Supabase shutdown behavior.

#### c) Simple Connection String

**Fly.io provides:**
```
DATABASE_URL=postgres://user:pass@appname-db.internal:5432/dbname
```

**Backend uses directly:**
```python
# config.py
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL)
```

**Internal networking = faster, more secure.**

#### d) Managed PostgreSQL

**Fly.io handles:**
- ✅ **Automated backups** - Snapshots included
- ✅ **Monitoring** - Dashboard shows CPU, memory, disk
- ✅ **Scaling** - Can increase storage/RAM as needed
- ✅ **Updates** - Postgres version updates managed

**AI benefit:** AI doesn't manage database infrastructure.

#### e) Migration Runner

**Alembic (SQLAlchemy migrations):**

**Generate migration:**
```bash
alembic revision --autogenerate -m "Add bookings table"
```

**Apply migration:**
```bash
alembic upgrade head
```

**Run in CI/CD before deploy:**
```yaml
# .github/workflows/deploy.yml
- name: Run migrations
  run: alembic upgrade head
  env:
    DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

**AI benefit:** AI generates migration scripts. Alembic applies them.

#### f) Free Tier

**Fly.io free allowance:**
- 3GB storage included
- Shared CPU (sufficient for MVP)
- No additional cost for small database

**Later:** ~$1-2/month for dedicated resources.

### 4. GitHub Actions - CI/CD

**Why GitHub Actions:**

#### a) Integrated with GitHub

**No separate CI/CD service:**
- ✅ **Same platform** - Code + CI/CD in GitHub
- ✅ **Free for public repos** - 2000 minutes/month for private
- ✅ **Secrets management** - Encrypted environment variables

#### b) AI-Friendly Workflow Syntax

**YAML syntax is well-known to AI:**

**Example workflow:**
```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pytest
      - run: mypy src/

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

**AI benefit:** AI can generate GitHub Actions workflows easily.

#### c) Multi-Stage Deployments

**Strategy:**
1. **Test** - Run Pytest + Mypy + Ruff
2. **Build** - Build Docker image (backend) or Next.js app (frontend)
3. **Migrate** - Run Alembic migrations
4. **Deploy** - Deploy to Fly.io / Vercel
5. **Verify** - Run smoke tests

**Example:**
```yaml
jobs:
  test:
    # Run tests

  migrate:
    needs: test
    # Run migrations

  deploy:
    needs: migrate
    # Deploy app

  smoke-test:
    needs: deploy
    # Verify deployment
```

**AI benefit:** Clear separation of concerns. Easy to debug failures.

---

## Alternatives Considered

### AWS (EC2 + RDS + S3 + CloudFront)

**Pros:**
- Very mature
- Full control
- Scalable

**Cons:**
- ❌ **Complex setup** - VPCs, security groups, IAM, etc.
- ❌ **Expensive** - RDS + EC2 + data transfer
- ❌ **Not AI-friendly** - Too many options, configuration-heavy
- ❌ **Overkill** - Enterprise-scale for small app

**Decision:** Too complex for AI-driven development.

---

### Heroku

**Pros:**
- Simple
- Mature
- Good docs

**Cons:**
- ❌ **Expensive** - No free tier anymore ($7/month minimum)
- ❌ **US-centric** - EU regions more expensive
- ❌ **Sunset concerns** - Salesforce ownership, uncertain future

**Decision:** Fly.io + Vercel cheaper and more modern.

---

### Render

**Pros:**
- Simple
- Free tier
- Good for full-stack

**Cons:**
- ❌ **Slower cold starts** - Free tier spins down
- ❌ **Less AI training data** - Newer platform
- ❌ **Limited EU regions**

**Decision:** Fly.io has better EU support and performance.

---

### Railway (for Database)

**Pros:**
- Excellent PostgreSQL management
- Beautiful UI/dashboard
- Good free tier ($5 credit/month)
- Simple connection strings

**Cons:**
- ❌ **Separate platform** - Backend on Fly.io, DB on Railway
- ❌ **Public internet connection** - Slight latency overhead vs Fly.io internal network
- ❌ **One more service** - More accounts, more management

**Decision:** Keeping everything on Fly.io is simpler. Co-location wins.

---

### Supabase (for Database)

**Pros:**
- Managed PostgreSQL
- Good UI
- Generous free tier

**Cons:**
- ❌ **Shuts down when idle** - Pauses after ~7 days inactivity
- ❌ **Cold starts** - Slow to wake up (user annoyance)
- ❌ **Extra features we don't need** - Auth, Realtime, Storage
- ❌ **More expensive for always-on** - $25/month for no-pause

**Decision:** Shutdown behavior is unacceptable. Fly.io Postgres stays always-on.

---

### Netlify (instead of Vercel)

**Pros:**
- Similar to Vercel
- Good CDN
- Free tier

**Cons:**
- ❌ **Not Next.js-native** - Vercel made by Next.js team
- ❌ **Less seamless** - Requires more config for Next.js
- ❌ **Smaller edge network**

**Decision:** Vercel is optimal for Next.js (zero config).

---

### Self-Hosted (VPS)

**Pros:**
- Full control
- Cheap (DigitalOcean $5/month)

**Cons:**
- ❌ **Manual ops** - Updates, security patches, backups
- ❌ **No auto-scaling**
- ❌ **Single point of failure**
- ❌ **AI can't manage ops**

**Decision:** Managed platforms (Fly.io, Railway) remove ops burden.

---

## Consequences

### Positive

✅ **Zero-downtime deploys** - Fly.io health checks + rolling updates
✅ **Fast global frontend** - Vercel CDN + edge caching
✅ **EU data residency** - GDPR compliant (Frankfurt region)
✅ **Preview deployments** - Test PRs before merge
✅ **AI-friendly** - Standard Docker + simple YAML workflows
✅ **Free tier sufficient** - MVP runs on free plans
✅ **Co-located database** - Backend + DB on Fly.io, ultra-low latency
✅ **Always-on database** - No shutdown/pause on inactivity
✅ **Single platform** - Fly.io for backend + database (simpler)
✅ **Type-safe deploys** - CI runs Mypy + TSC before deploy

### Negative

⚠️ **Vendor lock-in (mild)** - Fly.io + Vercel specific configs
⚠️ **Free tier limits** - Need to upgrade if traffic grows
⚠️ **Regional limitations** - Free tiers may restrict regions

### Neutral

➡️ **Monitoring needed** - Set up Sentry, Prometheus, or similar
➡️ **Cost tracking** - Monitor usage to avoid surprise bills
➡️ **Database backups** - Railway handles, but test restore process

---

## Implementation Notes

### Environment Structure

**Three environments:**

| Environment | Backend | Frontend | Database | Purpose |
|-------------|---------|----------|----------|---------|
| **Development** | Local (`uvicorn`) | Local (`next dev`) | Local Postgres or Fly.io dev | AI development |
| **Staging** | Fly.io (`betzenstein-api-staging`) | Vercel preview | Fly.io Postgres staging | PR previews |
| **Production** | Fly.io (`betzenstein-api`) | Vercel prod | Fly.io Postgres prod | Live users |

### Backend Deployment (Fly.io)

#### 1. Install Fly CLI
```bash
curl -L https://fly.io/install.sh | sh
fly auth login
```

#### 2. Create App
```bash
fly launch --name betzenstein-api --region fra
```

#### 3. Set Secrets
```bash
fly secrets set DATABASE_URL="postgresql://..."
fly secrets set RESEND_API_KEY="re_..."
fly secrets set SECRET_KEY="..."
```

#### 4. Deploy
```bash
fly deploy
```

#### 5. Fly Config
```toml
# fly.toml
app = "betzenstein-api"
primary_region = "fra"

[build]
  dockerfile = "Dockerfile"

[env]
  PORT = "8000"
  PYTHON_ENV = "production"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = false  # Keep running (not free tier default)
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

[mounts]
  source = "data"
  destination = "/data"
```

### Frontend Deployment (Vercel)

#### 1. Install Vercel CLI
```bash
npm install -g vercel
vercel login
```

#### 2. Link Project
```bash
vercel link
```

#### 3. Set Environment Variables
```bash
# Via Vercel dashboard or CLI
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://betzenstein-api.fly.dev
```

#### 4. Deploy
```bash
vercel --prod
```

**Or:** Push to GitHub → Vercel auto-deploys.

### Database Migrations (Alembic)

#### 1. Install Alembic
```bash
pip install alembic
alembic init alembic
```

#### 2. Configure Alembic
```python
# alembic/env.py
from app.models import Base  # Import all models

target_metadata = Base.metadata

def run_migrations_online():
    connectable = create_engine(DATABASE_URL)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
```

#### 3. Generate Migration
```bash
alembic revision --autogenerate -m "Create bookings table"
```

**AI generates:**
```python
# alembic/versions/001_create_bookings_table.py
def upgrade():
    op.create_table(
        'bookings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        # ...
    )

def downgrade():
    op.drop_table('bookings')
```

#### 4. Apply Migration
```bash
alembic upgrade head
```

### CI/CD Workflow

#### Backend Workflow
```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'
  pull_request:
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./backend
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run type checker
        run: mypy src/

      - name: Run linter
        run: ruff check src/

      - name: Run tests
        run: pytest
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: superfly/flyctl-actions/setup-flyctl@master

      - name: Run migrations
        run: |
          cd backend
          pip install alembic
          alembic upgrade head
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}

      - name: Deploy to Fly.io
        run: |
          cd backend
          flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}

      - name: Smoke test
        run: |
          sleep 10
          curl --fail https://betzenstein-api.fly.dev/health
```

#### Frontend Workflow
```yaml
# .github/workflows/deploy-frontend.yml
name: Deploy Frontend

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'
  pull_request:
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./frontend
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: "20"

      - name: Install dependencies
        run: npm ci

      - name: Run type checker
        run: npm run type-check

      - name: Run linter
        run: npm run lint

      - name: Build
        run: npm run build
        env:
          NEXT_PUBLIC_API_URL: https://betzenstein-api.fly.dev

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
          working-directory: ./frontend
```

### Secrets Management

**GitHub Secrets (Settings → Secrets and variables → Actions):**

**Backend:**
- `FLY_API_TOKEN` - Fly.io API token
- `DATABASE_URL` - Railway PostgreSQL connection string
- `RESEND_API_KEY` - Resend email API key
- `SECRET_KEY` - FastAPI secret key (for JWT signing)

**Frontend:**
- `VERCEL_TOKEN` - Vercel API token
- `VERCEL_ORG_ID` - Vercel organization ID
- `VERCEL_PROJECT_ID` - Vercel project ID

**How to get tokens:**

**Fly.io:**
```bash
fly auth token
```

**Vercel:**
```bash
vercel login
vercel project ls  # Get project ID
```

### Zero-Downtime Deployment Strategy

**Backend (Fly.io):**
1. Build new Docker image
2. Start new machine(s)
3. Run health checks (`/health` endpoint)
4. If healthy, route traffic to new machines
5. Stop old machines

**Frontend (Vercel):**
1. Build new Next.js app
2. Deploy to new edge nodes
3. Atomically switch DNS/routing
4. Old version remains accessible during switch

**Database (Railway + Alembic):**
1. Migrations run BEFORE deploy
2. Use backward-compatible migrations:
   - Add columns as nullable first
   - Drop columns in separate migration (later)
3. If migration fails, deploy aborts

**Example (safe migration):**
```python
# Good: Add column as nullable
def upgrade():
    op.add_column('bookings', sa.Column('new_field', sa.String(), nullable=True))

# Later migration: Make non-nullable
def upgrade():
    op.alter_column('bookings', 'new_field', nullable=False, server_default='default')

# Much later: Remove old column
def upgrade():
    op.drop_column('bookings', 'old_field')
```

---

## Validation

### Deployment Checklist

**Backend deployment:**
- [ ] Health check endpoint returns 200
- [ ] Database migrations applied
- [ ] Environment variables set
- [ ] HTTPS enforced
- [ ] CORS configured
- [ ] OpenAPI docs accessible (`/docs`)

**Verify:**
```bash
curl https://betzenstein-api.fly.dev/health
# Expected: {"status": "ok"}

curl https://betzenstein-api.fly.dev/docs
# Expected: OpenAPI UI
```

**Frontend deployment:**
- [ ] Preview deployment works
- [ ] Production deployment accessible
- [ ] API calls succeed (check Network tab)
- [ ] Static assets cached (check headers)
- [ ] HTTPS enforced

**Verify:**
```bash
curl -I https://betzenstein.app
# Expected: 200 OK, cache-control headers
```

**Database:**
- [ ] Migrations applied
- [ ] Backup configured
- [ ] Connection pooling enabled

**Verify:**
```bash
alembic current
# Expected: Current revision ID

psql $DATABASE_URL -c "SELECT COUNT(*) FROM bookings;"
# Expected: Query succeeds
```

---

## References

- [Fly.io Documentation](https://fly.io/docs/)
- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

## Related ADRs

- [ADR-001: Backend Framework](adr-001-backend-framework.md) - FastAPI deployment considerations
- [ADR-002: Frontend Framework](adr-002-frontend-framework.md) - Next.js deployment on Vercel
- [ADR-003: Database & ORM](adr-003-database-orm.md) - Railway PostgreSQL + Alembic migrations
- [ADR-008: Testing Strategy](adr-008-testing-strategy.md) - CI/CD test execution

---

## Changelog

- **2025-01-17:** Initial decision - Fly.io (backend + Postgres) + Vercel + GitHub Actions chosen for deployment
