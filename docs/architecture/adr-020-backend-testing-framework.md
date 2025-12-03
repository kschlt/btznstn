# ADR-020: Backend Testing Framework

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** Need testing framework for Python/FastAPI backend

---

## Context

Need testing framework for backend that:
- Supports async/await (FastAPI is async)
- Provides fixtures for database tests
- Enables fast feedback
- Works well with AI code generation
- Integrates with FastAPI

---

## Decision

Use **Pytest with pytest-asyncio** as the backend testing framework.

---

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Testing Framework | Pytest | Unittest, Nose, manual testing |
| Async Support | pytest-asyncio | Sync-only testing |
| Coverage | Coverage.py | No coverage tracking |
| Database Tests | SQLAlchemy fixtures | Manual database setup |

---

## Rationale

**Why Pytest:**
- Pytest provides fixtures and async support → **Constraint:** MUST use Pytest with pytest-asyncio for backend tests
- Pytest integrates with FastAPI → **Constraint:** MUST use Pytest for FastAPI endpoint testing
- Pytest provides parametrized tests → **Constraint:** MUST use Pytest parametrization for DRY test code

**Why NOT Unittest:**
- Unittest uses verbose class-based structure → **Violation:** Verbose structure violates simplicity requirement, less readable assertions
- Unittest lacks native async support → **Violation:** No async support violates FastAPI async requirement

---

## Consequences

### MUST (Required)

- MUST use Pytest for backend tests - Pytest provides fixtures and async support via pytest-asyncio
- MUST use pytest-asyncio for async tests - Backend uses async/await, tests must support async
- MUST use Coverage.py for backend coverage metrics - Track test coverage to ensure quality
- MUST use SQLAlchemy fixtures for database tests - Database tests require proper setup/teardown

### MUST NOT (Forbidden)

- MUST NOT use Unittest or Nose for backend tests - Violates Pytest decision
- MUST NOT skip async support in tests - Backend is async, tests must be async
- MUST NOT use sync-only test patterns - Violates async requirement

### Trade-offs

- Many code examples use Unittest - MUST use Pytest. MUST NOT use Unittest. Check for unittest imports in test files.

### Applies To

- ALL backend tests (all phases)
- File patterns: `api/tests/**/*.py`

### Validation Commands

- `grep -r "import unittest\|from unittest" api/tests/` (should be empty - must use Pytest)
- `pytest api/tests/` (must pass)
- `pytest --cov=app api/tests/` (coverage report)

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - Backend Framework (FastAPI + pytest integration)
- [ADR-009](adr-009-test-data-factory-functions.md) - Test Data Factory Functions

**Workflow:**
- [Test-First Workflow](../../docs/implementation/test-first-workflow.md) - Test-first development approach (BDD)

---

## References

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - Backend Framework (FastAPI + pytest integration)
- [ADR-009](adr-009-test-data-factory-functions.md) - Test Data Factory Functions

**Workflow:**
- [Test-First Workflow](../../docs/implementation/test-first-workflow.md) - Test-first development approach (BDD)

**Tools:**
- [Pytest](https://pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Coverage.py](https://coverage.readthedocs.io/)

**Implementation:**
- `api/tests/` - Backend test files
- `api/tests/conftest.py` - Pytest fixtures
- `api/pytest.ini` - Pytest configuration

