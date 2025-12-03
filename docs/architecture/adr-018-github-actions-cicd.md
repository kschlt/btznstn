# ADR-018: GitHub Actions CI/CD

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** Need automated testing and deployment
**Split from:** ADR-007: Deployment Strategy

---

## Context

Need CI/CD platform to automate:
- Run tests automatically on commits/PRs
- Run type checks (mypy, TypeScript)
- Run linters (ruff, ESLint)
- Deploy applications (deployment strategy decided separately)
- AI-friendly (YAML syntax, clear patterns)
- Integrated with GitHub
- Budget-friendly (free for private repos)

---

## Decision

Use **GitHub Actions** for CI/CD automation.

---

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| CI/CD Platform | GitHub Actions | GitLab CI, CircleCI, Jenkins |
| Workflow Syntax | YAML files in `.github/workflows/` | External CI/CD config |
| Integration | GitHub PR status checks | External CI/CD platforms |
| Secrets Management | GitHub Secrets (encrypted, masked) | Hardcoded secrets, unencrypted |
| Free Tier | 2,000 minutes/month (private repos) | Paid CI/CD platforms |

---

## Rationale

**Why GitHub Actions:**
- GitHub Actions integrates with GitHub (same platform) → **Constraint:** MUST use GitHub Actions for CI/CD (no external accounts, tight integration)
- GitHub Actions provides PR status checks → **Constraint:** MUST use GitHub Actions for merge protection (tests must pass before merge)
- GitHub Actions uses YAML syntax → **Constraint:** MUST use YAML workflow files in `.github/workflows/` (AI-friendly, clear structure)
- GitHub Actions provides encrypted secrets → **Constraint:** MUST use GitHub Secrets for sensitive data (encrypted, scoped, masked in logs)

**Why NOT GitLab CI:**
- GitLab CI requires different platform → **Violation:** Code on GitHub, CI on GitLab violates same-platform requirement, extra account needed

**Why NOT CircleCI:**
- CircleCI is separate platform → **Violation:** Separate platform violates integration requirement, less generous free tier

**Why NOT Jenkins:**
- Jenkins requires self-hosting → **Violation:** Self-hosted server violates simplicity requirement, complex setup, manual operations

---

## Consequences

### MUST (Required)

- MUST use GitHub Actions for CI/CD automation - Same platform as code, tight integration with GitHub
- MUST use YAML workflow files in `.github/workflows/` - AI-friendly syntax, clear structure
- MUST use GitHub Secrets for sensitive data (API keys, tokens) - Encrypted, scoped, masked in logs
- MUST use PR status checks for merge protection - Tests must pass before merge, prevents broken code
- MUST use marketplace actions for common tasks - Reusable, proven actions (deployment targets decided in other ADRs)

### MUST NOT (Forbidden)

- MUST NOT use GitLab CI, CircleCI, or Jenkins - Violates same-platform requirement, adds complexity
- MUST NOT hardcode secrets in workflow files - Violates security requirement, secrets exposed in logs
- MUST NOT skip PR status checks - Violates quality requirement, allows broken code to merge

### Trade-offs

- GitHub-specific YAML - MUST use GitHub Actions. MUST NOT use other CI/CD platforms. YAML not portable, but integration worth it.
- Free tier limits - MUST use free tier initially. MUST NOT exceed 2,000 minutes/month without upgrading. Monitor usage before scaling.
- Shared runners slower than dedicated - MUST use GitHub Actions shared runners. MUST NOT assume dedicated CI server performance. Sufficient for small projects.

### Code Examples

```yaml
# ✅ CORRECT: Backend test workflow
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
    defaults:
      run:
        working-directory: ./api
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: mypy app/
      - run: ruff check app/
      - run: pytest
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test_db
```

```yaml
# ✅ CORRECT: Deploy workflow using secrets (branch strategy decided separately)
# .github/workflows/deploy-backend.yml
name: Deploy Backend
on:
  push:
    branches: [main]  # Branch strategy may change - not part of this ADR
    paths:
      - 'api/**'
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}  # ✅ Secret from GitHub Secrets
```

```yaml
# ❌ WRONG: Hardcoded secret
env:
  FLY_API_TOKEN: "hardcoded-token-here"  # ❌ Secret exposed in logs!
```

### Applies To

- ALL CI/CD automation (all phases)
- File patterns: `.github/workflows/*.yml`
- Test automation (all phases)
- Deployment automation (deployment targets and strategies decided in other ADRs)

### Validation Commands

- `grep -r "secrets\." .github/workflows/` (should use secrets, not hardcoded values)
- `grep -r "FLY_API_TOKEN\|DATABASE_URL" .github/workflows/` (should use `${{ secrets.NAME }}` format)
- `grep -r "on:" .github/workflows/` (should have trigger events defined)

---

## References

**Related ADRs:**
- [ADR-006](adr-006-type-safety.md) - Type Safety Strategy (type checks in CI)
- [ADR-015](adr-015-flyio-backend-hosting.md) - Fly.io Backend Hosting (deploy target)
- [ADR-017](adr-017-vercel-frontend-hosting.md) - Vercel Frontend Hosting (deploy target)
- [ADR-020](adr-020-backend-testing-framework.md) - Backend Testing Framework (tests run in CI)

**Tools:**
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Fly.io GitHub Actions](https://fly.io/docs/app-guides/continuous-deployment-with-github-actions/)

**Implementation:**
- `.github/workflows/` - GitHub Actions workflow files
