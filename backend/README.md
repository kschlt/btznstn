# Betzenstein Booking API - Backend

FastAPI backend for the Betzenstein booking and approval system.

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for PostgreSQL)
- PostgreSQL 15+ (or use Docker Compose)

### Setup

1. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Start database:**
   ```bash
   docker-compose up -d postgres
   ```

5. **Run migrations (Phase 1+):**
   ```bash
   alembic upgrade head
   ```

6. **Start development server:**
   ```bash
   uvicorn app.main:app --reload
   ```

API will be available at http://localhost:8000

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Type checking
mypy app/

# Linting
ruff check app/
```

### API Documentation

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application
│   ├── core/             # Core configuration
│   ├── models/           # SQLAlchemy models (Phase 1+)
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── repositories/     # Data access layer
├── tests/
│   ├── unit/             # Unit tests
│   └── integration/      # Integration tests (Phase 1+)
├── alembic/              # Database migrations
├── requirements.txt      # Production dependencies
├── requirements-dev.txt  # Dev dependencies
└── pyproject.toml        # Project configuration
```

## Environment Variables

See `.env.example` for all available variables.

**Required:**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key (generate with `openssl rand -hex 32`)

**Optional:**
- `RESEND_API_KEY` - Email service (Phase 4+)
- `ALLOWED_ORIGINS` - CORS allowed origins

## Development

**Code Style:**
- PEP 8 compliance
- Type hints required (mypy strict)
- Docstrings for public functions (Google style)

**Git Workflow:**
- Feature branches: `claude/feature-name-<session-id>`
- Commit messages: Conventional Commits format
- All tests must pass before merge

## Deployment

See [Fly.io Setup Guide](../docs/deployment/flyio-setup.md) for production deployment instructions.

## Documentation

- [Project Overview](../CLAUDE.md)
- [Architecture](../docs/architecture/README.md)
- [API Specification](../docs/design/api-specification.md)
- [Database Schema](../docs/design/database-schema.md)
