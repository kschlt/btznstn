# Implementation Roadmap

## Overview

Test-driven implementation plan for the Betzenstein booking application. Each phase follows BDD (Behavior-Driven Development) with Gherkin acceptance criteria.

**Approach:** Write failing tests first → Implement features → Tests pass

---

## Implementation Phases

### Phase 0: Foundation Setup
**Goal:** Project scaffolding, tools, CI/CD
**Duration:** 1-2 days
**Tests:** Linting, type checking, build passes
- [Phase 0 Details](phase-0-foundation.md)

### Phase 1: Data Layer
**Goal:** Database schema, models, repositories
**Duration:** 2-3 days
**Tests:** Database operations, migrations
- [Phase 1 Details](phase-1-data-layer.md)

### Phase 2: Booking API
**Goal:** Create, read, update booking endpoints
**Duration:** 3-4 days
**Tests:** API contract tests, conflict detection
- [Phase 2 Details](phase-2-booking-api.md)

### Phase 3: Approval Flow
**Goal:** Approve, deny, confirm logic
**Duration:** 2-3 days
**Tests:** State transitions, authorization
- [Phase 3 Details](phase-3-approval-flow.md)

### Phase 4: Email Integration
**Goal:** Notification system with Resend
**Duration:** 2 days
**Tests:** Email sending, templates
- [Phase 4 Details](phase-4-email-integration.md)

### Phase 5: Web Calendar
**Goal:** Calendar UI, booking display
**Duration:** 3-4 days
**Tests:** E2E calendar navigation, responsive
- [Phase 5 Details](phase-5-frontend-calendar.md)

### Phase 6: Web Booking
**Goal:** Create/edit forms, validation
**Duration:** 3-4 days
**Tests:** Form validation, submission
- [Phase 6 Details](phase-6-frontend-booking.md)

### Phase 7: Approver Interface
**Goal:** Approver overview, actions
**Duration:** 2-3 days
**Tests:** Approver workflows
- [Phase 7 Details](phase-7-approver-interface.md)

### Phase 8: Polish & Production
**Goal:** Performance, accessibility, deployment
**Duration:** 2-3 days
**Tests:** Lighthouse, a11y, load tests
- [Phase 8 Details](phase-8-polish.md)

---

## BDD Workflow

### 1. Write Feature File (Gherkin)

```gherkin
Feature: Create Booking
  As a requester
  I want to create a booking request
  So that I can reserve dates at Betzenstein

  Scenario: Successfully create booking
    Given I am on the calendar page
    When I click "Neue Anfrage"
    And I fill in:
      | field               | value              |
      | Vorname            | Anna               |
      | E-Mail             | anna@example.com   |
      | Startdatum         | 2025-08-01         |
      | Enddatum           | 2025-08-05         |
      | Teilnehmerzahl     | 4                  |
      | Zugehörigkeit      | Ingeborg           |
    And I submit the form
    Then I should see "Anfrage gesendet"
    And I should receive a confirmation email
```

### 2. Write Failing Tests

**API (Pytest):**
```python
@pytest.mark.asyncio
async def test_create_booking_api(client):
    response = await client.post("/api/v1/bookings", json={
        "requester_first_name": "Anna",
        "requester_email": "anna@example.com",
        "start_date": "2025-08-01",
        "end_date": "2025-08-05",
        "party_size": 4,
        "affiliation": "Ingeborg",
    })

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "Pending"
    assert data["total_days"] == 5
```

**Web (Playwright):**
```typescript
test('create booking via form', async ({ page }) => {
  await page.goto('/')
  await page.click('text=Neue Anfrage')

  await page.fill('input[name="requester_first_name"]', 'Anna')
  await page.fill('input[name="requester_email"]', 'anna@example.com')
  // ... fill other fields

  await page.click('button[type="submit"]')

  await expect(page.locator('text=Anfrage gesendet')).toBeVisible()
})
```

### 3. Implement Features

**Run tests:** `pytest` (backend) or `npx playwright test` (frontend)
**Watch mode:** `pytest --watch` or `npx playwright test --ui`

**Implement until tests pass.**

### 4. Refactor

- Clean up code
- Add error handling
- Improve performance
- Tests still pass

---

## Testing Strategy

### API Tests

**Unit Tests (Fast):**
- Business logic functions
- Validation rules
- Repository methods
- **Database:** SQLite in-memory

**Integration Tests (Realistic):**
- API endpoints
- Database transactions
- Email sending (mocked)
- **Database:** PostgreSQL test DB

**Run:**
```bash
pytest tests/unit/        # Unit tests only
pytest tests/integration/ # Integration tests
pytest --cov=app         # With coverage
```

### Web Tests

**E2E Tests (Playwright):**
- Full user journeys
- Mobile + desktop viewports
- Cross-browser (Chromium, Firefox, WebKit)

**Run:**
```bash
npx playwright test                    # All tests
npx playwright test --project="iPhone 8"  # Mobile only
npx playwright test --headed           # Watch browser
npx playwright test --debug            # Debug mode
```

---

## Acceptance Criteria Format

Each user story includes:

**User Story:**
```
As a [role]
I want [feature]
So that [benefit]
```

**Acceptance Criteria (Gherkin):**
```gherkin
Scenario: [Description]
  Given [precondition]
  And [another precondition]
  When [action]
  And [another action]
  Then [expected result]
  And [another expected result]
```

**Definition of Done:**
- [ ] All scenarios pass (backend + frontend)
- [ ] Code coverage ≥80%
- [ ] Type checks pass (mypy + tsc)
- [ ] Linting passes (ruff + eslint)
- [ ] No accessibility violations (axe-core)
- [ ] Reviewed and merged

---

## Phase Dependencies

```
Phase 0 (Foundation)
    ↓
Phase 1 (Data Layer)
    ↓
Phase 2 (Booking API) ←──┐
    ↓                     │
Phase 3 (Approval Flow)   │
    ↓                     │
Phase 4 (Email) ──────────┘
    ↓
Phase 5 (Web Calendar)
    ↓
Phase 6 (Web Booking)
    ↓
Phase 7 (Approver Interface)
    ↓
Phase 8 (Polish & Production)
```

**Parallel Work Possible:**
- Phase 5-7 can partially overlap (different UI areas)
- Phase 4 can start while Phase 2-3 finish

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: CI

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - run: pip install -r requirements-dev.txt
      - run: mypy src/
      - run: ruff check src/
      - run: pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v3

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run type-check
      - run: npm run lint
      - run: npx playwright install --with-deps
      - run: npx playwright test
```

**All tests must pass before merge.**

---

## Development Workflow

1. **Pick a phase** - Start with Phase 0
2. **Read phase doc** - Understand user stories + scenarios
3. **Write tests** - API + frontend tests (failing)
4. **Implement** - Code until tests pass
5. **Refactor** - Clean up, maintain test coverage
6. **Commit** - `git commit -m "feat: implement user story X"`
7. **Push** - CI runs all tests
8. **Review** - Ensure all criteria met
9. **Merge** - Move to next story

---

## Documentation References

- [Development Workflow](development-workflow.md) - Git flow, PR process
- [Testing Guide](testing-guide.md) - How to run/write tests
- [Deployment Guide](deployment-guide.md) - How to deploy

---

## Summary

This roadmap provides:

✅ **Clear phases** - 9 incremental milestones
✅ **BDD scenarios** - Gherkin acceptance criteria for each feature
✅ **Test-first** - Write failing tests before implementation
✅ **AI-friendly** - Executable specs for Claude Code
✅ **Testable** - Every feature has automated tests
✅ **Incremental** - Deploy after each phase

**Next:** Start with Phase 0 (Foundation Setup).
