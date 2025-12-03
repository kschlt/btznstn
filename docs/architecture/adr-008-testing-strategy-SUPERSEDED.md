# ADR-008: Testing Strategy

**Status:** Superseded by [ADR-020](adr-020-backend-testing-framework.md), [ADR-021](adr-021-frontend-testing-framework.md)
**Date:** 2025-01-17
**Superseded:** 2025-01-19
**Deciders:** Solution Architect
**Context:** AI-driven development - need comprehensive test coverage

---

## Supersession Note

This ADR bundled multiple independent architectural decisions:
1. **Backend testing framework**: Pytest → [ADR-020](adr-020-backend-testing-framework.md)
2. **Frontend testing framework**: Playwright → [ADR-021](adr-021-frontend-testing-framework.md)

**Note:** Test-first development workflow is documented in [Test-First Workflow](../../docs/implementation/test-first-workflow.md) (not an ADR, as it's a process decision).

These decisions can now be superseded independently following the "One Decision Per ADR" principle.

**Original decision content preserved below for historical reference.**

---

## Context

AI-generated code requires automated testing to:
- Catch errors before deployment
- Enable confident refactoring
- Validate business rules (BR-001 to BR-029)
- Support incremental development (test each phase)
- Provide fast feedback

**Requirements:**
- Backend: Unit tests, integration tests, database tests
- Frontend: Component tests, E2E tests
- Cross-cutting: Type checking, linting, coverage >80%

---

## Decision

Use **Pytest (backend) + Playwright (frontend)** with test-first approach.

**Backend (Python/FastAPI):**
- Pytest for unit & integration tests
- Pytest-asyncio for async support
- SQLAlchemy fixtures for database tests
- Coverage.py for metrics

**Frontend (TypeScript/Next.js):**
- Playwright for E2E tests
- React Testing Library for component tests (if needed)
- Axe for accessibility testing

**Test-First Workflow:**
- Write tests BEFORE implementation (BDD)
- Each phase has Gherkin scenarios
- Tests fail initially, pass after implementation

---

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Backend Testing | Pytest with pytest-asyncio | Unittest, Nose, manual testing |
| Frontend Testing | Playwright E2E tests | Selenium, Cypress, manual testing |
| Test Approach | Test-first (BDD) | Test-after, no tests |
| Coverage | Coverage.py metrics | No coverage tracking |
| Async Support | pytest-asyncio | Sync-only testing |

**Why Pytest + Playwright:**
- Pytest provides fixtures and async support → **Constraint:** MUST use Pytest with pytest-asyncio for backend tests
- Playwright provides reliable E2E testing → **Constraint:** MUST use Playwright for frontend E2E tests
- Test-first approach enables BDD workflow → **Constraint:** MUST write tests before implementation

**Why NOT Unittest (Backend):**
- Unittest uses verbose class-based structure → **Violation:** Verbose structure violates simplicity requirement, less readable assertions

**Why NOT Selenium (Frontend):**
- Selenium requires manual waits → **Violation:** Manual waits cause flaky tests, violates reliability requirement

---

## Consequences

### MUST (Required)

- MUST use Pytest for backend tests - Pytest provides fixtures and async support via pytest-asyncio
- MUST use pytest-asyncio for async tests - Backend uses async/await, tests must support async
- MUST use Playwright for frontend E2E tests - Playwright provides reliable E2E testing with auto-wait
- MUST write tests before implementation - Test-first approach enables BDD workflow
- MUST use Coverage.py for backend coverage metrics - Track test coverage to ensure quality

### MUST NOT (Forbidden)

- MUST NOT use Unittest or Nose for backend tests - Violates Pytest decision
- MUST NOT use Selenium or Cypress for frontend E2E tests - Violates Playwright decision
- MUST NOT write tests after implementation - Violates test-first approach
- MUST NOT skip async support in tests - Backend is async, tests must be async

### Trade-offs

- Many code examples use Unittest - MUST use Pytest. MUST NOT use Unittest. Check for unittest imports in test files.
- Code examples may use Selenium - MUST use Playwright. MUST NOT use Selenium. Check for Selenium imports in test files.

### Applies To

- ALL backend tests (all phases)
- ALL frontend E2E tests (Phase 5, 6, 7, 8)
- File patterns: `api/tests/**/*.py`, `web/tests/**/*.ts`

### Validation Commands

- `grep -r "import unittest\|from unittest" api/tests/` (should be empty - must use Pytest)
- `grep -r "selenium\|cypress" web/tests/` (should be empty - must use Playwright)
- `pytest api/tests/` (must pass)
- `npx playwright test` (must pass)

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - Backend Framework (FastAPI + pytest integration)
- [ADR-002](adr-002-frontend-framework.md) - Frontend Framework (Next.js + Playwright)
- [ADR-009](adr-009-test-data-factory-functions.md) - Test Data Factory Functions

---

## References

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - Backend Framework (FastAPI + pytest integration)
- [ADR-002](adr-002-frontend-framework.md) - Frontend Framework (Next.js + Playwright)
- [ADR-009](adr-009-test-data-factory-functions.md) - Test Data Factory Functions

**Tools:**
- [Pytest](https://pytest.org/)
- [Playwright](https://playwright.dev/)
- [Coverage.py](https://coverage.readthedocs.io/)

**Implementation:**
- `api/tests/` - Backend test files
- `web/tests/` - Frontend test files
- `api/tests/CLAUDE.md` - Testing patterns and guidelines
