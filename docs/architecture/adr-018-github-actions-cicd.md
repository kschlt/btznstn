# ADR-018: GitHub Actions CI/CD

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** Need automated testing and deployment
**Split from:** ADR-007: Deployment Strategy

---

## Context

Need CI/CD platform to automate:
- Run tests automatically on every commit
- Run type checks (mypy, TypeScript)
- Run linters (ruff, ESLint)
- Deploy backend to Fly.io on merge to main
- Deploy frontend to Vercel (handled by Vercel)
- AI-friendly (YAML syntax, clear patterns)
- Integrated with GitHub
- Budget-friendly (free for private repos)

---

## Decision

Use **GitHub Actions** for CI/CD automation.

---

## Rationale

### Why GitHub Actions vs GitLab CI vs CircleCI vs Jenkins?

**GitHub Actions (Chosen):**
- ✅ **Same platform** - Code + CI/CD in GitHub (no external accounts)
- ✅ **Tight integration** - PR status checks, merge protection
- ✅ **Free tier** - 2,000 minutes/month (private repos), unlimited (public)
- ✅ **YAML syntax** - AI-friendly, clear structure
- ✅ **Marketplace** - Reusable actions (Fly.io, Codecov, etc.)
- ✅ **Secrets management** - Encrypted, scoped, masked in logs

**GitLab CI (Rejected):**
- ❌ Different platform (code on GitHub, CI on GitLab)
- ❌ Extra account needed

**CircleCI (Rejected):**
- ❌ Separate platform
- ❌ Less generous free tier

**Jenkins (Rejected):**
- ❌ Self-hosted (must run server)
- ❌ Complex setup
- ❌ Manual operations

---

## Key Benefits

### 1. GitHub Integration (Same Platform)

**PR status checks:**
```
PR #123: Add booking feature
✅ Tests (74 passed)
✅ Type check (mypy)
✅ Lint (ruff)
→ Merge button enabled
```

One platform to manage.

### 2. YAML Syntax (AI-Friendly)

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

Clear structure. AI can generate workflows.

### 3. Marketplace Actions (Reusable)

```yaml
# Deploy to Fly.io
- uses: superfly/flyctl-actions/setup-flyctl@master
- run: flyctl deploy --remote-only
  env:
    FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Reuse proven actions.

### 4. Branch Protection (Enforce Quality)

**Required status checks:**
- `test-backend`
- `test-frontend`
- `type-check`
- `lint`

Merge button disabled until all pass. AI can't merge broken code.

---

## Consequences

### Positive

✅ **Integrated** - Same platform as code
✅ **Free tier** - 2,000 minutes/month sufficient
✅ **YAML syntax** - AI-friendly
✅ **Marketplace** - Reusable actions
✅ **Secrets management** - Encrypted, masked
✅ **Branch protection** - Enforce tests before merge
✅ **PR status checks** - Clear pass/fail

### Negative

⚠️ **GitHub-specific** - YAML not portable
⚠️ **Free tier limits** - 2,000 minutes/month (sufficient, but monitor)
⚠️ **Slower** - Shared runners vs dedicated CI server

### Neutral

➡️ **YAML complexity** - Large workflows verbose (but AI handles this)
➡️ **Debugging** - Must debug via logs (can't SSH into runner)

---

## Implementation Pattern

### Workflow Structure

```
.github/
└── workflows/
    ├── test-backend.yml      # Backend tests + lint + type-check
    ├── test-frontend.yml     # Frontend tests + lint + type-check
    └── deploy-backend.yml    # Deploy to Fly.io (on push to main)
```

### Backend Test Workflow

```yaml
# .github/workflows/test-backend.yml
name: Test Backend

on:
  push:
    paths:
      - 'api/**'
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
        run: pip install -r requirements.txt

      - name: Run type checker
        run: mypy src/

      - name: Run linter
        run: ruff check src/

      - name: Run tests
        run: pytest --cov=app
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
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

    steps:
      - uses: actions/checkout@v3

      - uses: superfly/flyctl-actions/setup-flyctl@master

      - name: Deploy to Fly.io
        run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

### Set Secrets

**Via GitHub UI:**
1. Settings → Secrets and variables → Actions
2. Add secrets:
   - `FLY_API_TOKEN` (get via `fly auth token`)

### Branch Protection

**Enable on `main`:**
1. Settings → Branches
2. Add rule for `main`:
   - ✅ Require status checks
   - Required: `test-backend / test`, `test-frontend / test`

---

## References

**Related ADRs:**
- ADR-008: Testing Strategy (tests run in CI)
- ADR-016: Fly.io Backend Hosting (deploy target)
- ADR-017: Vercel Frontend Hosting (deploy target)
- ADR-006: Type Safety Strategy (type checks in CI)

**Tools:**
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Fly.io GitHub Actions](https://fly.io/docs/app-guides/continuous-deployment-with-github-actions/)
