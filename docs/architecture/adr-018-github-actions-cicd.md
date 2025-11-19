# ADR-018: GitHub Actions CI/CD

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)
**Split from:** [ADR-007: Deployment Strategy](adr-007-deployment.md)

---

## Context

We need a CI/CD (Continuous Integration / Continuous Deployment) platform to automate testing and deployment. The platform must:

- Run tests automatically on every commit
- Run type checks (mypy, TypeScript)
- Run linters (ruff, ESLint)
- Deploy backend to Fly.io on merge to main
- Deploy frontend to Vercel on merge to main (handled by Vercel)
- Be AI-friendly (YAML syntax, clear patterns)
- Integrate with GitHub (code is on GitHub)
- Fit within budget (free for open source/private repos)

### Requirements

**From development workflow:**
- Test-first approach (tests must pass before merge)
- Type safety enforced (mypy + TypeScript)
- Automated deployment (no manual steps)

---

## Decision

We will use **GitHub Actions** for CI/CD automation.

---

## Rationale

### 1. GitHub Integration (Same Platform)

**GitHub Actions is built into GitHub** - No separate service.

**Key benefits:**
- ✅ **Same platform** - Code + CI/CD in one place
- ✅ **No external accounts** - Use GitHub login
- ✅ **Tight integration** - PR status checks, merge protection
- ✅ **Secrets management** - GitHub handles secrets

**Example (PR status check):**
```
PR #123: Add booking feature
✅ Tests (74 passed)
✅ Type check (mypy)
✅ Lint (ruff)
→ Merge button enabled
```

**AI benefit:** One platform to manage, not two.

### 2. Free Tier (Generous for Private Repos)

**GitHub Actions free allowance:**
- **Public repos**: Unlimited minutes
- **Private repos**: 2,000 minutes/month
- **Storage**: 500MB artifacts
- **Concurrent jobs**: 20

**Our usage (estimated):**
- Backend tests: ~3 minutes/run
- Frontend tests: ~5 minutes/run
- Total: ~8 minutes per push
- ~250 pushes/month = 2,000 minutes

**Fits within free tier.**

### 3. YAML Syntax (AI-Friendly)

**GitHub Actions uses YAML** - AI knows it extremely well.

**Example workflow:**
```yaml
# .github/workflows/test-backend.yml
name: Test Backend

on: [push, pull_request]

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
      - run: ruff check src/
```

**AI benefit:** Clear structure, AI can generate workflows.

### 4. Marketplace Actions (Reusable Components)

**GitHub Actions Marketplace:**
- ✅ **Official actions** - `actions/checkout`, `actions/setup-python`
- ✅ **Community actions** - Fly.io deploy, Codecov upload
- ✅ **Version pinning** - `@v3` for stability

**Example (deploy to Fly.io):**
```yaml
- uses: superfly/flyctl-actions/setup-flyctl@master
- run: flyctl deploy --remote-only
  env:
    FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

**AI benefit:** Reuse proven actions, don't reinvent.

### 5. Matrix Builds (Test Multiple Versions)

**Test against multiple versions/environments:**
```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - run: pytest
```

**Benefits:**
- ✅ **Compatibility testing** - Ensure works on Python 3.11 and 3.12
- ✅ **Cross-platform** - Test on Linux and macOS
- ✅ **Parallel** - Runs concurrently

**Not needed initially, but available.**

### 6. Secrets Management (Secure)

**GitHub Secrets:**
- ✅ **Encrypted** - Secrets stored encrypted
- ✅ **Scoped** - Per-repo or organization-wide
- ✅ **Masked in logs** - Values not printed

**Example (set secrets):**
```bash
# Via GitHub UI: Settings → Secrets and variables → Actions
# Add secrets:
# - FLY_API_TOKEN
# - DATABASE_URL
# - RESEND_API_KEY
```

**Usage in workflow:**
```yaml
- run: flyctl deploy
  env:
    FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

**AI benefit:** AI doesn't need to handle secrets, GitHub manages them.

### 7. Branch Protection (Enforce Quality)

**GitHub branch protection rules:**
- ✅ **Require status checks** - Tests must pass before merge
- ✅ **Require reviews** - PR must be reviewed
- ✅ **Block force push** - Prevent history rewriting on main

**Example (main branch protection):**
```
Required status checks:
- test-backend
- test-frontend
- type-check
- lint
```

**Merge button disabled until all pass.**

**AI benefit:** AI can't accidentally merge broken code.

---

## Alternatives Considered

### GitLab CI

**Pros:**
- Powerful
- Good UI
- Built-in container registry

**Cons:**
- ❌ **Different platform** - Code on GitHub, CI on GitLab
- ❌ **Extra account** - Need GitLab account
- ❌ **More complex** - `.gitlab-ci.yml` more verbose

**Decision:** GitHub Actions simpler (same platform).

---

### CircleCI

**Pros:**
- Mature
- Fast
- Good caching

**Cons:**
- ❌ **Separate platform** - Extra account
- ❌ **Free tier limits** - 2,500 credits/month (less generous)
- ❌ **More config** - `.circleci/config.yml` more complex

**Decision:** GitHub Actions sufficient, no need for external service.

---

### Jenkins

**Pros:**
- Very powerful
- Self-hosted
- Highly customizable

**Cons:**
- ❌ **Self-hosted** - Must run Jenkins server
- ❌ **Manual ops** - Updates, security, plugins
- ❌ **Complex setup** - Groovy pipelines
- ❌ **Overkill** - Enterprise features for small app

**Decision:** GitHub Actions managed, no server to maintain.

---

### Travis CI

**Pros:**
- Mature
- Simple YAML

**Cons:**
- ❌ **Pricing changes** - Free tier removed, then restored
- ❌ **Uncertain future** - Acquisition, layoffs
- ❌ **Less integrated** - Not as tight with GitHub

**Decision:** GitHub Actions more stable, better integration.

---

## Consequences

### Positive

✅ **Integrated** - Same platform as code (GitHub)
✅ **Free tier** - 2,000 minutes/month sufficient
✅ **YAML syntax** - AI-friendly, clear structure
✅ **Marketplace** - Reusable actions (Fly.io, Codecov, etc.)
✅ **Secrets management** - Encrypted, scoped secrets
✅ **Branch protection** - Enforce tests before merge
✅ **Matrix builds** - Test multiple versions (if needed)
✅ **PR status checks** - Clear pass/fail on PRs

### Negative

⚠️ **GitHub-specific** - YAML not portable to other CI platforms
⚠️ **Free tier limits** - 2,000 minutes/month (sufficient for now, but monitor)
⚠️ **Slower than self-hosted** - Shared runners slower than dedicated CI server

### Neutral

➡️ **YAML complexity** - Large workflows can get verbose (but AI handles this)
➡️ **Debugging** - Must debug via logs, can't SSH into runner (vs Jenkins)

---

## Implementation Notes

### Workflow Structure

```
.github/
└── workflows/
    ├── test-backend.yml      # Backend tests + lint + type-check
    ├── test-frontend.yml     # Frontend tests + lint + type-check
    ├── deploy-backend.yml    # Deploy API to Fly.io (on push to main)
    └── deploy-frontend.yml   # Deploy web to Vercel (handled by Vercel, optional)
```

### Backend Test Workflow

```yaml
# .github/workflows/test-backend.yml
name: Test Backend

on:
  push:
    paths:
      - 'api/**'
      - '.github/workflows/test-backend.yml'
  pull_request:
    paths:
      - 'api/**'

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    defaults:
      run:
        working-directory: ./api

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
        run: pytest --cov=app
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./api/coverage.xml
```

### Backend Deploy Workflow

```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths:
      - 'api/**'

jobs:
  deploy:
    runs-on: ubuntu-latest

    defaults:
      run:
        working-directory: ./api

    steps:
      - uses: actions/checkout@v3

      - uses: superfly/flyctl-actions/setup-flyctl@master

      - name: Deploy to Fly.io
        run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

### Frontend Test Workflow

```yaml
# .github/workflows/test-frontend.yml
name: Test Frontend

on:
  push:
    paths:
      - 'web/**'
      - '.github/workflows/test-frontend.yml'
  pull_request:
    paths:
      - 'web/**'

jobs:
  test:
    runs-on: ubuntu-latest

    defaults:
      run:
        working-directory: ./web

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

      - name: Run E2E tests
        run: npx playwright test
```

### Set Secrets

**Via GitHub UI:**
1. Go to repo → Settings → Secrets and variables → Actions
2. Add repository secrets:
   - `FLY_API_TOKEN` (get via `fly auth token`)
   - `DATABASE_URL` (for migrations in CI, if needed)
   - `VERCEL_TOKEN` (if deploying via GitHub Actions, optional)

### Branch Protection

**Enable on `main` branch:**
1. Go to repo → Settings → Branches
2. Add rule for `main`:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Required status checks:
     - `test-backend / test`
     - `test-frontend / test`

**Result:** Can't merge PR until tests pass.

---

## Validation

### Verify Workflow Runs

**Check workflow status:**
1. Go to repo → Actions tab
2. See recent workflow runs
3. Click run to see logs

**Expected:** All workflows pass (green checkmark).

### Verify PR Status Checks

**Create test PR:**
```bash
git checkout -b test-feature
git push origin test-feature
# Create PR on GitHub
```

**Expected:** PR shows status checks (test-backend, test-frontend).

### Verify Deployment

**Push to main:**
```bash
git push origin main
```

**Expected:**
- GitHub Actions triggers deploy workflow
- Fly.io deploys new version
- Site updated

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Fly.io GitHub Actions](https://fly.io/docs/app-guides/continuous-deployment-with-github-actions/)
- [Vercel GitHub Integration](https://vercel.com/docs/deployments/git/vercel-for-github)

**Related ADRs:**
- [ADR-008: Testing Strategy](adr-008-testing-strategy.md) - Tests run in CI
- [ADR-016: Fly.io Backend Hosting](adr-016-flyio-backend-hosting.md) - Deploy target
- [ADR-017: Vercel Frontend Hosting](adr-017-vercel-frontend-hosting.md) - Deploy target
- [ADR-006: Type Safety Strategy](adr-006-type-safety.md) - Type checks in CI

---

## Changelog

- **2025-01-19:** Split from ADR-007 - GitHub Actions CI/CD as independent decision
