# ADR-008: Testing Strategy

**Status:** Accepted
**Date:** 2025-01-17
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)

---

## Context

We need a comprehensive testing strategy for the booking application that:

- **Validates AI-generated code** - Catch errors before deployment
- **Enables confident refactoring** - Test suite as safety net
- **Supports incremental development** - Test each phase independently
- **Runs in CI/CD** - Automated testing on every commit
- **Is AI-friendly** - Standard frameworks, clear patterns
- **Covers critical paths** - Business rules, edge cases
- **Fast feedback loops** - Quick test execution

### Requirements

**API testing:**
- Unit tests (business logic, repositories, services)
- Integration tests (database, API endpoints)
- Contract tests (Pydantic validation)
- Migration tests (Alembic reversibility)

**Web testing:**
- Component tests (UI components)
- Integration tests (forms, user flows)
- E2E tests (critical journeys)
- Accessibility tests (WCAG AA)

**Cross-cutting:**
- Type checking (Mypy, TypeScript)
- Linting (Ruff, ESLint)
- Code coverage (target: >80%)

---

## Decision

We will use:

### API (Python/FastAPI)
- **Pytest** for unit and integration tests
- **Pytest-asyncio** for async test support
- **SQLAlchemy test fixtures** for database tests
- **httpx** for API client tests
- **Coverage.py** for code coverage
- **Faker** for test data generation

### Web (TypeScript/Next.js)
- **Playwright** for E2E and integration tests
- **React Testing Library** for component tests (optional, if needed)
- **Axe-core** for accessibility tests
- **MSW (Mock Service Worker)** for API mocking

### CI/CD
- **GitHub Actions** for automated test execution
- **Pre-commit hooks** for local validation
- **Parallel test execution** where possible

---

## Rationale

### 1. Pytest - Python Testing Framework

**Why Pytest:**

#### a) AI-Friendly

- ✅ **Most popular** Python testing framework
- ✅ **Massive training data** - AI knows Pytest extremely well
- ✅ **Simple syntax** - `assert` statements (no `self.assertEqual`)
- ✅ **Fixtures** - Clear dependency injection pattern

**AI benefit:** AI can generate Pytest tests easily.

#### b) Async Support

**Requirement:** FastAPI is async, tests must be too.

**Pytest-asyncio:**
```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_booking():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/bookings", json={...})
        assert response.status_code == 201
```

#### c) Fixtures for Database Tests

**Pattern:**
```python
@pytest.fixture
async def db_session():
    # Create test database
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session

    await engine.dispose()

@pytest.mark.asyncio
async def test_booking_repository(db_session):
    repo = BookingRepository(db_session)
    booking = await repo.create(BookingCreate(...))
    assert booking.id is not None
```

**AI benefit:** Standard pattern for database tests.

#### d) Parametrized Tests

**Test multiple cases:**
```python
@pytest.mark.parametrize("party_size,expected", [
    (1, True),   # Valid
    (10, True),  # Valid (max)
    (0, False),  # Invalid (too low)
    (11, False), # Invalid (too high)
])
def test_party_size_validation(party_size, expected):
    # Test BR-016: Party size 1-10
    result = validate_party_size(party_size)
    assert result == expected
```

**AI benefit:** Concise way to test edge cases.

### 2. Playwright - E2E Testing

**Why Playwright:**

#### a) AI-Friendly

**Playwright has:**
- ✅ **Massive adoption** - Standard for modern E2E testing
- ✅ **Clear API** - `page.click()`, `page.fill()`, etc.
- ✅ **Auto-waiting** - Waits for elements automatically
- ✅ **Multi-browser** - Chromium, Firefox, WebKit

**AI benefit:** AI knows Playwright well, generates reliable tests.

#### b) Mobile-First Testing

**Requirement:** App must work on mobile (iPhone 8 class).

**Playwright:**
```python
from playwright.async_api import async_playwright

async def test_mobile_calendar():
    async with async_playwright() as p:
        # iPhone 8 viewport
        iphone = p.devices["iPhone 8"]
        browser = await p.chromium.launch()
        context = await browser.new_context(**iphone)
        page = await context.new_page()

        await page.goto("http://localhost:3000")

        # Test tap targets (BR: min 44x44 points)
        booking = page.locator(".booking-card").first
        box = await booking.bounding_box()
        assert box["height"] >= 44
        assert box["width"] >= 44
```

**AI benefit:** Test mobile requirements directly.

#### c) Visual Regression (Optional)

**Playwright screenshots:**
```python
async def test_calendar_visual():
    await page.goto("/calendar")
    await page.screenshot(path="calendar.png")
    # Compare with baseline (manual review initially)
```

**Later:** Integrate Percy or similar for automated visual regression.

#### d) Accessibility Testing

**Playwright + Axe-core:**
```python
from playwright.async_api import async_playwright

async def test_booking_form_accessibility():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto("/bookings/new")

        # Inject axe-core
        await page.add_script_tag(url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.2/axe.min.js")

        # Run accessibility scan
        results = await page.evaluate("""
            async () => {
                const results = await axe.run();
                return results.violations;
            }
        """)

        assert len(results) == 0, f"Accessibility violations: {results}"
```

**AI benefit:** Automated WCAG AA compliance checking.

### 3. Test Database Strategy

**Approach:** In-memory SQLite for fast unit tests, Postgres for integration tests.

#### a) Unit Tests (Fast)

**Use SQLite in-memory:**
```python
@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # ... setup
    yield session
    # ... teardown
```

**Pros:**
- ✅ **Fast** - No I/O, runs in RAM
- ✅ **Isolated** - Each test gets fresh DB
- ✅ **No cleanup** - Disposable

**Cons:**
- ⚠️ **Not exact Postgres** - Some features differ

**Decision:** Use for unit tests (business logic, repositories).

#### b) Integration Tests (Realistic)

**Use Postgres test database:**
```python
@pytest.fixture(scope="session")
async def postgres_engine():
    engine = create_async_engine("postgresql+asyncpg://test:test@localhost:5432/test_db")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
```

**Pros:**
- ✅ **Exact Postgres** - Range types, GiST indexes work
- ✅ **Realistic** - Tests actual deployment DB

**Cons:**
- ⚠️ **Slower** - I/O overhead
- ⚠️ **Requires Postgres** - CI must run Postgres service

**Decision:** Use for integration tests (API endpoints, conflict detection).

### 4. Coverage Strategy

**Target:** >80% code coverage

**Coverage.py:**
```bash
pytest --cov=app --cov-report=html --cov-report=term
```

**Report:**
```
Name                     Stmts   Miss  Cover
--------------------------------------------
app/models/booking.py       42      2    95%
app/services/booking.py     67      8    88%
app/repositories/...        53      4    92%
--------------------------------------------
TOTAL                      312     28    91%
```

**AI benefit:** Coverage gaps show where AI needs to add tests.

**Exclusions:**
- Test files themselves
- Type stubs (`.pyi`)
- Migration scripts (tested via deployment)

### 5. Test Organization

#### API Structure

```
tests/
├── unit/
│   ├── test_booking_service.py
│   ├── test_approval_service.py
│   ├── test_validation.py
│   └── test_business_rules.py
├── integration/
│   ├── test_booking_api.py
│   ├── test_approval_api.py
│   └── test_conflict_detection.py
├── fixtures/
│   ├── database.py
│   ├── test_data.py
│   └── mock_clients.py
└── conftest.py  # Shared fixtures
```

#### Web Structure

```
e2e/
├── booking-flow.spec.ts
├── approval-flow.spec.ts
├── calendar.spec.ts
└── accessibility.spec.ts
```

**AI benefit:** Clear separation of concerns, easy to navigate.

### 6. Test Data Generation

**Use Faker for realistic test data:**

```python
from faker import Faker

fake = Faker("de_DE")  # German locale

@pytest.fixture
def booking_data():
    return BookingCreate(
        requester_first_name=fake.first_name(),
        requester_email=fake.email(),
        start_date=fake.date_between(start_date="today", end_date="+1y"),
        end_date=fake.date_between(start_date="+1d", end_date="+1y"),
        party_size=fake.random_int(min=1, max=10),
        affiliation=fake.random_element(["Ingeborg", "Cornelia", "Angelika"]),
        description=fake.text(max_nb_chars=200),
    )
```

**AI benefit:** Realistic test data without manual entry.

---

## Alternatives Considered

### Jest (instead of Playwright)

**Pros:**
- Fast
- Good for unit tests
- React Testing Library integration

**Cons:**
- ❌ **Not real browser** - jsdom limitations
- ❌ **No mobile testing** - Can't test touch targets
- ❌ **No E2E** - Requires separate tool (Cypress/Playwright)

**Decision:** Playwright covers E2E + integration. Jest not needed.

---

### Cypress (instead of Playwright)

**Pros:**
- Popular
- Good DX
- Time-travel debugging

**Cons:**
- ❌ **Less AI training data** - Playwright more modern
- ❌ **Slower** - Single-browser execution
- ❌ **No multi-tab** - Can't test multiple windows

**Decision:** Playwright is more modern, better multi-browser support.

---

### Django Test Framework (instead of Pytest)

**Pros:**
- Batteries-included
- DB fixtures built-in

**Cons:**
- ❌ **Requires Django** - We're using FastAPI
- ❌ **Less flexible** - Pytest more modular
- ❌ **No async** - Django tests are sync

**Decision:** Pytest is better for FastAPI + async.

---

## Consequences

### Positive

✅ **AI-generated tests** - Pytest + Playwright well-known to AI
✅ **Fast feedback** - SQLite for unit tests
✅ **Realistic integration tests** - Postgres for API tests
✅ **Mobile testing** - Playwright device emulation
✅ **Accessibility validated** - Axe-core integration
✅ **High coverage** - Coverage.py tracking
✅ **CI/CD ready** - Automated execution in GitHub Actions
✅ **Incremental testing** - Each phase can be tested independently

### Negative

⚠️ **Two test DBs** - SQLite (unit) + Postgres (integration) adds complexity
⚠️ **E2E tests slower** - Playwright takes longer than unit tests
⚠️ **CI time** - Full test suite may take 5-10 minutes

### Neutral

➡️ **Test maintenance** - Tests need updates when requirements change
➡️ **Flaky tests** - E2E tests may need retries for timing issues
➡️ **Coverage targets** - Need discipline to maintain >80%

---

## Implementation Notes

### API Test Setup

#### 1. Install Dependencies
```bash
pip install pytest pytest-asyncio pytest-cov faker httpx
```

#### 2. Pytest Config
```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = [
    "--cov=app",
    "--cov-report=html",
    "--cov-report=term-missing",
    "-v",
]

[tool.coverage.run]
omit = [
    "*/tests/*",
    "*/migrations/*",
]
```

#### 3. Example Unit Test
```python
# tests/unit/test_booking_service.py
import pytest
from app.services.booking_service import BookingService
from app.schemas.booking import BookingCreate

@pytest.mark.asyncio
async def test_create_booking_success(db_session):
    service = BookingService(db_session)

    data = BookingCreate(
        requester_first_name="Anna",
        requester_email="anna@example.com",
        start_date=date(2025, 8, 1),
        end_date=date(2025, 8, 5),
        party_size=4,
        affiliation="Ingeborg",
    )

    booking = await service.create_booking(data)

    assert booking.id is not None
    assert booking.status == "Pending"
    assert booking.total_days == 5  # Inclusive (BR-001)

@pytest.mark.asyncio
async def test_create_booking_conflict(db_session):
    service = BookingService(db_session)

    # Create first booking
    await service.create_booking(BookingCreate(...))

    # Try overlapping booking (should fail per BR-002)
    with pytest.raises(ConflictError):
        await service.create_booking(BookingCreate(...))
```

#### 4. Example Integration Test
```python
# tests/integration/test_booking_api.py
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_post_booking_api(client: AsyncClient):
    response = await client.post("/api/v1/bookings", json={
        "requester_first_name": "Max",
        "requester_email": "max@example.com",
        "start_date": "2025-08-01",
        "end_date": "2025-08-05",
        "party_size": 3,
        "affiliation": "Cornelia",
    })

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "Pending"
    assert data["total_days"] == 5
```

### Web Test Setup

#### 1. Install Dependencies
```bash
npm install -D @playwright/test @axe-core/playwright
npx playwright install
```

#### 2. Playwright Config
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 8'] },  // Test mobile (BR requirement)
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
})
```

#### 3. Example E2E Test
```typescript
// e2e/booking-flow.spec.ts
import { test, expect } from '@playwright/test'

test('requester can create booking', async ({ page }) => {
  await page.goto('/')

  // Click "Neue Anfrage" button
  await page.click('text=Neue Anfrage')

  // Fill form
  await page.fill('input[name="requester_first_name"]', 'Anna')
  await page.fill('input[name="requester_email"]', 'anna@example.com')
  await page.fill('input[name="start_date"]', '2025-08-01')
  await page.fill('input[name="end_date"]', '2025-08-05')
  await page.selectOption('select[name="affiliation"]', 'Ingeborg')

  // Submit
  await page.click('button[type="submit"]')

  // Verify success message
  await expect(page.locator('text=Anfrage gesendet')).toBeVisible()
})

test('mobile: tap targets are large enough', async ({ page }) => {
  // Test on iPhone 8 viewport
  await page.setViewportSize({ width: 375, height: 667 })
  await page.goto('/')

  // Check booking card tap target (BR: min 44x44 points)
  const booking = page.locator('.booking-card').first()
  const box = await booking.boundingBox()

  expect(box!.height).toBeGreaterThanOrEqual(44)
  expect(box!.width).toBeGreaterThanOrEqual(44)
})
```

#### 4. Example Accessibility Test
```typescript
// e2e/accessibility.spec.ts
import { test, expect } from '@playwright/test'
import AxeBuilder from '@axe-core/playwright'

test('booking form has no accessibility violations', async ({ page }) => {
  await page.goto('/bookings/new')

  const results = await new AxeBuilder({ page }).analyze()

  expect(results.violations).toEqual([])
})
```

### CI/CD Integration

#### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  backend-tests:
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

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run unit tests
        run: pytest tests/unit/ -v

      - name: Run integration tests
        run: pytest tests/integration/ -v
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test_db

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  frontend-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-node@v3
        with:
          node-version: "20"

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright
        run: npx playwright install --with-deps

      - name: Run E2E tests
        run: npx playwright test

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

### Running Tests Locally

**API:**
```bash
# All tests
pytest

# Unit tests only (fast)
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/unit/test_booking_service.py::test_create_booking_success
```

**Web:**
```bash
# All E2E tests
npx playwright test

# Headed mode (see browser)
npx playwright test --headed

# Specific test
npx playwright test booking-flow.spec.ts

# Debug mode
npx playwright test --debug

# Mobile only
npx playwright test --project="Mobile Safari"
```

---

## Validation

### Test Coverage Check

**Run:**
```bash
pytest --cov=app --cov-report=term-missing
```

**Expected:** >80% coverage overall, >90% on business logic.

### CI/CD Check

**Expected:** All tests pass in GitHub Actions before merge.

### E2E Check

**Run:**
```bash
npx playwright test
```

**Expected:** All critical journeys pass (create, approve, deny, cancel).

---

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Playwright Documentation](https://playwright.dev/)
- [Faker Documentation](https://faker.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Axe-core Documentation](https://github.com/dequelabs/axe-core)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)

---

## Related ADRs

- [ADR-001: API Framework](adr-001-backend-framework.md) - FastAPI testing patterns
- [ADR-002: Web Framework](adr-002-frontend-framework.md) - Next.js testing
- [ADR-006: Type Safety Strategy](adr-006-type-safety.md) - Mypy + TSC in CI
- [ADR-018: GitHub Actions CI/CD](adr-018-github-actions-cicd.md) - CI/CD integration

---

## Changelog

- **2025-01-17:** Initial decision - Pytest + Playwright chosen for comprehensive testing strategy
