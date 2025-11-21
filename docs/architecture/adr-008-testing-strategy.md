# ADR-008: Testing Strategy

**Status:** Accepted
**Date:** 2025-01-17
**Deciders:** Solution Architect
**Context:** AI-driven development - need comprehensive test coverage

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

## Rationale

### Why Pytest vs Unittest vs Nose?

**Pytest (Chosen):**
- ✅ Most popular Python testing framework
- ✅ Fixtures > setUp/tearDown (cleaner, reusable)
- ✅ Async support (pytest-asyncio)
- ✅ Parametrized tests (DRY)
- ✅ Clear assertion failures

**Unittest (Rejected):**
- ❌ Verbose (class-based, setUp/tearDown)
- ❌ Less readable assertions

**Nose (Rejected):**
- ❌ Unmaintained since 2016

---

### Why Playwright vs Selenium vs Cypress?

**Playwright (Chosen):**
- ✅ Modern, fast, reliable
- ✅ Auto-wait (no flaky tests)
- ✅ Multiple browsers (Chromium, Firefox, WebKit)
- ✅ Mobile viewport testing (iPhone 8 requirement)
- ✅ Better DX than Selenium

**Selenium (Rejected):**
- ❌ Older, flaky tests common
- ❌ Manual waits required
- ❌ Slower

**Cypress (Rejected):**
- ❌ Only Chromium (can't test Firefox/Safari)
- ❌ Limited mobile testing

---

## Consequences

### Positive

✅ **Fast feedback** - Pytest runs in seconds
✅ **Reliable E2E** - Playwright auto-wait prevents flaky tests
✅ **Mobile testing** - Playwright viewport emulation
✅ **AI-friendly** - Standard frameworks, well-documented

### Negative

⚠️ **Test maintenance** - Tests must be updated with code changes
⚠️ **CI time** - Full test suite adds ~2-5 min to builds

### Neutral

➡️ **Coverage target 80%** - Enforced in CI but not blocking initially

---

## Implementation Pattern

### Backend: Pytest Integration Test

```python
import pytest
from httpx import AsyncClient
from app.models import Booking
from tests.utils import get_today

@pytest.mark.asyncio
async def test_create_booking_success(client: AsyncClient, db_session):
    """Test BR-001: Create booking with inclusive end date."""
    # Arrange
    today = get_today()
    data = {
        "requester_email": "test@example.com",
        "start_date": str(today),
        "end_date": str(today + timedelta(days=2)),
        "party_size": 4,
    }

    # Act
    response = await client.post("/api/v1/bookings", json=data)

    # Assert
    assert response.status_code == 201
    assert response.json()["total_days"] == 3  # Inclusive (BR-001)
```

### Frontend: Playwright E2E Test

```typescript
import { test, expect } from '@playwright/test'

test('create booking flow', async ({ page }) => {
  // Mobile viewport (BR requirement: iPhone 8)
  await page.setViewportSize({ width: 375, height: 667 })

  await page.goto('/calendar')
  await page.click('text=Neue Buchung')

  // Fill form
  await page.fill('[name="email"]', 'test@example.com')
  await page.fill('[name="partySize"]', '4')

  // Submit
  await page.click('button:has-text("Absenden")')

  // Verify success
  await expect(page.locator('text=Anfrage gesendet')).toBeVisible()
})
```

### Test Organization

```
api/tests/
  conftest.py          # Fixtures
  utils.py             # Helpers (get_today, factories)
  test_bookings.py     # Booking endpoints
  test_approvals.py    # Approval endpoints

web/tests/
  e2e/
    calendar.spec.ts   # Calendar tests
    booking.spec.ts    # Booking flow tests
```

---

## References

**Related ADRs:**
- ADR-001: Backend Framework (FastAPI + pytest integration)
- ADR-002: Frontend Framework (Next.js + Playwright)
- ADR-009: Test Patterns (factories, fixtures)

**Tools:**
- [Pytest](https://pytest.org/)
- [Playwright](https://playwright.dev/)
- [Coverage.py](https://coverage.readthedocs.io/)

**Implementation:**
- [BDD Roadmap](../../implementation/README.md) - Test-first workflow
- [Test CLAUDE.md](../../api/tests/CLAUDE.md) - Testing patterns
