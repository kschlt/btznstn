# Phase 0: Foundation Setup

## Goal

Establish project scaffolding, development tools, and CI/CD pipeline.

**Duration:** 1-2 days
**Dependencies:** None
**Outputs:** Working dev environment, passing CI checks

---

## User Stories

### US-0.1: API Project Setup

**As a** developer
**I want** a properly configured FastAPI project
**So that** I can start implementing API endpoints

**Acceptance Criteria:**

```gherkin
Feature: API Project Setup

  Scenario: Project structure created
    Given I clone the repository
    When I navigate to the backend directory
    Then I should see:
      | directory/file      |
      | app/__init__.py     |
      | app/main.py         |
      | app/core/           |
      | app/models/         |
      | app/schemas/        |
      | app/services/       |
      | app/repositories/   |
      | tests/              |
      | requirements.txt    |
      | pyproject.toml      |
      | .python-version     |

  Scenario: FastAPI application starts
    Given the backend is configured
    When I run "uvicorn app.main:app --reload"
    Then the server should start on port 8000
    And I should see "Application startup complete"
    And I can access http://localhost:8000/docs

  Scenario: Type checking passes
    Given Python code is written with type hints
    When I run "mypy app/"
    Then I should see "Success: no issues found"

  Scenario: Linting passes
    Given Python code follows style guide
    When I run "ruff check app/"
    Then I should see no errors
```

**Tasks:**
- [ ] Create `api/` directory structure
- [ ] Add `app/main.py` with FastAPI app
- [ ] Configure `pyproject.toml` with dependencies
- [ ] Set up `mypy.ini` with strict mode
- [ ] Configure `ruff` rules
- [ ] Create `.python-version` (3.11)
- [ ] Add `requirements.txt` and `requirements-dev.txt`

**Tests:**
```bash
# Run these to verify
uvicorn app.main:app --reload
mypy app/
ruff check app/
pytest tests/unit/test_main.py
```

---

### US-0.2: Web Project Setup

**As a** developer
**I want** a properly configured Next.js project
**So that** I can start building UI components

**Acceptance Criteria:**

```gherkin
Feature: Web Project Setup

  Scenario: Next.js project created
    Given I clone the repository
    When I navigate to the frontend directory
    Then I should see:
      | directory/file      |
      | app/                |
      | components/         |
      | lib/                |
      | public/             |
      | package.json        |
      | tsconfig.json       |
      | tailwind.config.ts  |
      | next.config.js      |

  Scenario: Development server starts
    Given the frontend is configured
    When I run "npm run dev"
    Then the server should start on port 3000
    And I can access http://localhost:3000

  Scenario: Type checking passes
    Given TypeScript is configured in strict mode
    When I run "npm run type-check"
    Then I should see no type errors

  Scenario: Linting passes
    Given ESLint is configured
    When I run "npm run lint"
    Then I should see no linting errors
```

**Tasks:**
- [ ] Run `npx create-next-app@latest frontend --typescript --tailwind --app --eslint`
- [ ] Configure `tsconfig.json` with strict mode
- [ ] Install Shadcn/ui: `npx shadcn-ui@latest init`
- [ ] Add design tokens to `tailwind.config.ts`
- [ ] Install dependencies: `zod`, `react-hook-form`, `@tanstack/react-query`
- [ ] Configure `.eslintrc.json`
- [ ] Add `components/ui/` (Shadcn components)

**Tests:**
```bash
npm run dev
npm run build
npm run type-check
npm run lint
```

---

### US-0.3: Database Setup

**As a** developer
**I want** a local PostgreSQL database
**So that** I can test database operations

**Acceptance Criteria:**

```gherkin
Feature: Database Setup

  Scenario: Local PostgreSQL running
    Given Docker is installed
    When I run "docker-compose up -d postgres"
    Then a PostgreSQL container should start
    And I can connect to postgresql://localhost:5432/betzenstein_dev

  Scenario: Alembic initialized
    Given the backend project exists
    When I run "alembic init alembic"
    Then I should see:
      | file                        |
      | alembic/                    |
      | alembic/env.py              |
      | alembic/versions/           |
      | alembic.ini                 |

  Scenario: Initial migration created
    Given Alembic is configured
    When I run "alembic revision --autogenerate -m 'Initial schema'"
    Then a migration file should be created
    And it should contain table definitions

  Scenario: Migration applied
    Given an initial migration exists
    When I run "alembic upgrade head"
    Then all tables should be created in the database
```

**Tasks:**
- [ ] Create `docker-compose.yml` with PostgreSQL service
- [ ] Initialize Alembic: `alembic init alembic`
- [ ] Configure `alembic/env.py` with async support
- [ ] Create `.env.example` with `DATABASE_URL`
- [ ] Add `python-dotenv` to load environment variables

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: betzenstein
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: betzenstein_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

### US-0.4: CI/CD Pipeline

**As a** developer
**I want** automated tests in CI
**So that** code quality is enforced

**Acceptance Criteria:**

```gherkin
Feature: CI/CD Pipeline

  Scenario: API CI passes
    Given I push code to GitHub
    When GitHub Actions runs
    Then it should:
      | step                  |
      | Install dependencies  |
      | Run mypy             |
      | Run ruff             |
      | Run pytest           |
    And all steps should pass

  Scenario: Web CI passes
    Given I push code to GitHub
    When GitHub Actions runs
    Then it should:
      | step                  |
      | Install dependencies  |
      | Run type-check       |
      | Run lint             |
      | Run build            |
    And all steps should pass
```

**Tasks:**
- [ ] Create `.github/workflows/backend-ci.yml`
- [ ] Create `.github/workflows/frontend-ci.yml`
- [ ] Add PostgreSQL service to backend workflow
- [ ] Configure code coverage reporting (Codecov)

**.github/workflows/backend-ci.yml:**
```yaml
name: API CI

on: [push, pull_request]

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

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        working-directory: ./backend
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Type check
        working-directory: ./backend
        run: mypy app/

      - name: Lint
        working-directory: ./backend
        run: ruff check app/

      - name: Test
        working-directory: ./backend
        run: pytest --cov=app --cov-report=xml
        env:
          DATABASE_URL: postgresql+asyncpg://test:test@localhost:5432/test_db

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Definition of Done

- [ ] API starts: `uvicorn app.main:app --reload`
- [ ] Web starts: `npm run dev`
- [ ] Type checking passes: `mypy app/` and `npm run type-check`
- [ ] Linting passes: `ruff check app/` and `npm run lint`
- [ ] Database migrations work: `alembic upgrade head`
- [ ] CI passes on GitHub Actions
- [ ] README.md updated with setup instructions

---

## Testing Commands

**API:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements-dev.txt
uvicorn app.main:app --reload  # Should start on :8000
mypy app/                      # Should pass
ruff check app/                # Should pass
```

**Web:**
```bash
cd frontend
npm install
npm run dev         # Should start on :3000
npm run build       # Should succeed
npm run type-check  # Should pass
npm run lint        # Should pass
```

**Database:**
```bash
docker-compose up -d postgres
alembic upgrade head  # Should create tables
```

---

## Next Phase

✅ Foundation complete → [Phase 1: Data Layer](phase-1-data-layer.md)
