# ADR-021: Frontend UI/E2E Testing Framework

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** Need E2E testing framework for Next.js frontend UI

---

## Context

Need E2E testing framework for frontend UI that:
- Tests rendered UI and user interactions
- Supports mobile viewport testing (iPhone 8: 375×667px)
- Provides reliable, non-flaky tests
- Tests across multiple browsers
- Validates visual behavior and accessibility

---

## Decision

Use **Playwright** as the frontend UI/E2E testing framework.

---

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| E2E Testing | Playwright | Selenium, Cypress, manual testing |
| Browser Support | Multiple browsers (Chromium, Firefox, WebKit) | Single browser only |
| Mobile Testing | Viewport emulation | No mobile testing |
| Auto-wait | Built-in auto-wait | Manual waits required |

---

## Rationale

**Why Playwright:**
- Playwright provides reliable E2E testing with auto-wait → **Constraint:** MUST use Playwright for frontend E2E tests
- Playwright supports multiple browsers → **Constraint:** MUST test across Chromium, Firefox, WebKit
- Playwright supports mobile viewport testing → **Constraint:** MUST use viewport emulation for iPhone 8 testing

**Why NOT Selenium:**
- Selenium requires manual waits → **Violation:** Manual waits cause flaky tests, violates reliability requirement
- Selenium is slower → **Violation:** Slower tests violate fast feedback requirement

**Why NOT Cypress:**
- Cypress only supports Chromium → **Violation:** Single browser violates cross-browser testing requirement
- Cypress has limited mobile testing → **Violation:** Limited mobile testing violates iPhone 8 requirement

---

## Consequences

### MUST (Required)

- MUST use Playwright for frontend E2E tests - Playwright provides reliable E2E testing with auto-wait
- MUST test across multiple browsers - Playwright supports Chromium, Firefox, WebKit
- MUST use viewport emulation for mobile testing - Test iPhone 8 viewport (375×667px) requirement

### MUST NOT (Forbidden)

- MUST NOT use Selenium or Cypress for frontend E2E tests - Violates Playwright decision
- MUST NOT skip mobile viewport testing - Mobile-first design requires mobile testing
- MUST NOT use manual waits - Playwright auto-wait must be used, not manual waits

### Trade-offs

- Code examples may use Selenium - MUST use Playwright. MUST NOT use Selenium. Check for Selenium imports in test files.
- Code examples may use Cypress - MUST use Playwright. MUST NOT use Cypress. Check for Cypress imports in test files.

### Applies To

- ALL frontend UI/E2E tests (Phase 5, 6, 7, 8)
- File patterns: `web/tests/e2e/**/*.spec.ts`

### Validation Commands

- `grep -r "selenium\|cypress" web/tests/` (should be empty - must use Playwright)
- `npx playwright test` (must pass)
- `npx playwright test --project=chromium --project=firefox --project=webkit` (test all browsers)

**Related ADRs:**
- [ADR-002](adr-002-frontend-framework.md) - Frontend Framework (Next.js + Playwright)
- [ADR-022](adr-022-frontend-unit-component-testing.md) - Frontend Unit/Component Testing Framework

**Workflow:**
- [Test-First Workflow](../../docs/implementation/test-first-workflow.md) - Test-first development approach (BDD)

---

## References

**Related ADRs:**
- [ADR-002](adr-002-frontend-framework.md) - Frontend Framework (Next.js + Playwright)
- [ADR-022](adr-022-frontend-unit-component-testing.md) - Frontend Unit/Component Testing Framework

**Workflow:**
- [Test-First Workflow](../../docs/implementation/test-first-workflow.md) - Test-first development approach (BDD)

**Tools:**
- [Playwright](https://playwright.dev/)

**Implementation:**
- `web/tests/e2e/` - Frontend E2E test files
- `web/playwright.config.ts` - Playwright configuration

