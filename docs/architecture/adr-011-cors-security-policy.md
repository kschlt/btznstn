# ADR-011: CORS Security Policy

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** Distributed architecture - backend (Fly.io) + frontend (Vercel)

---

## Context

Need Cross-Origin Resource Sharing (CORS) policy for FastAPI backend that:
- Allows Next.js frontend (different domain) to access API
- Supports credentials (cookies, authorization headers)
- Works in development (localhost) and production (different domains)
- Maintains security for small, trusted user group

**Architecture:**
- Backend: `api.betzenstein.app` (Fly.io)
- Frontend: `betzenstein.app` (Vercel)
- Different origins → CORS required

---

## Decision

Use **permissive CORS policy** for the trusted single-page application:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),  # Environment-configurable
    allow_credentials=True,                         # Enable credentials
    allow_methods=["*"],                           # All HTTP methods
    allow_headers=["*"],                           # All headers
)
```

**Configuration:**
- `allow_origins`: Environment variable (comma-separated)
  - Development: `http://localhost:3000`
  - Production: `https://betzenstein.app`
- `allow_credentials`: `True` (cookies, authorization headers)
- `allow_methods`: `["*"]` (GET, POST, PATCH, DELETE, OPTIONS)
- `allow_headers`: `["*"]` (Content-Type, Authorization, etc.)

---

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| CORS Origins | Environment-configurable via `settings.get_allowed_origins()` | Hardcoded origins |
| CORS Credentials | `allow_credentials=True` | `allow_credentials=False` |
| CORS Methods | `allow_methods=["*"]` | Enumerated methods list |
| CORS Headers | `allow_headers=["*"]` | Enumerated headers list |

---

## Rationale

**Why Permissive CORS:**
- Trusted environment with small user group → **Constraint:** MUST use permissive CORS policy (`allow_methods=["*"]`, `allow_headers=["*"]`)
- Simple configuration reduces maintenance → **Constraint:** MUST use environment-configurable origins via `settings.get_allowed_origins()`
- Credentials required for authenticated API → **Constraint:** MUST use `allow_credentials=True`

**Why NOT Restrictive CORS:**
- Restrictive CORS requires enumeration of methods/headers → **Violation:** More maintenance, brittle when API changes, no security benefit for trusted app

**Why NOT CORS Proxy:**
- CORS proxy adds latency and complexity → **Violation:** Adds extra hop, loses stateless API benefit, violates simplicity requirement

## Consequences

### MUST (Required)

- MUST use permissive CORS policy (`allow_methods=["*"]`, `allow_headers=["*"]`) - Simple configuration, future-proof for trusted app
- MUST use `allow_credentials=True` - Enables cookies and Authorization header for authenticated API
- MUST use environment-configurable origins via `settings.get_allowed_origins()` - Works in dev + prod, supports multiple origins

### MUST NOT (Forbidden)

- MUST NOT enumerate methods/headers - Violates permissive policy, creates maintenance burden
- MUST NOT hardcode origins - Violates environment-configurable requirement
- MUST NOT use CORS proxy - Violates simplicity requirement, adds latency

### Trade-offs

- Permissive policy allows all methods/headers - MUST use permissive policy for trusted app. MUST NOT use restrictive policy. Appropriate for small trusted user group.
- CORS is defense-in-depth - MUST use CORS middleware. MUST NOT rely on CORS as primary security. Primary security is token auth + rate limiting (BR-012).

### Code Examples

```python
# ✅ CORRECT: Permissive CORS configuration
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),  # Environment-configurable
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ❌ WRONG: Restrictive CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://betzenstein.app"],  # Hardcoded
    allow_methods=["GET", "POST", "PATCH", "DELETE"],  # Enumerated
    allow_headers=["Content-Type", "Authorization"],  # Enumerated
)
```

```python
# ✅ CORRECT: Environment-configurable origins
class Settings(BaseSettings):
    allowed_origins: str = "http://localhost:3000"

    def get_allowed_origins(self) -> list[str]:
        """Parse comma-separated CORS origins."""
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]

# ❌ WRONG: Hardcoded origins
allow_origins = ["https://betzenstein.app"]
```

### Applies To

- ALL FastAPI middleware configuration (Phase 1)
- File patterns: `app/main.py`, `app/core/config.py`

### Validation Commands

- `grep -r "allow_methods=\[" app/main.py` (should show `["*"]` - must use permissive)
- `grep -r "allow_headers=\[" app/main.py` (should show `["*"]` - must use permissive)
- `grep -r "allow_credentials" app/main.py` (should show `True` - must enable credentials)

---

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - Backend Framework (FastAPI)
- [ADR-002](adr-002-frontend-framework.md) - Frontend Framework (Next.js)
- [ADR-015](adr-015-flyio-backend-hosting.md) - Fly.io Backend Hosting
- [ADR-017](adr-017-vercel-frontend-hosting.md) - Vercel Frontend Hosting
- [ADR-019](adr-019-authentication-authorization.md) - Authentication & Authorization

---

## References

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - Backend Framework
- [ADR-002](adr-002-frontend-framework.md) - Frontend Framework
- [ADR-015](adr-015-flyio-backend-hosting.md) - Fly.io Backend Hosting
- [ADR-017](adr-017-vercel-frontend-hosting.md) - Vercel Frontend Hosting
- [ADR-019](adr-019-authentication-authorization.md) - Authentication & Authorization

**Business Rules:**
- BR-012: Rate limiting (primary abuse prevention)

**Tools:**
- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)

**Implementation:**
- `app/main.py` - CORS middleware configuration
- `app/core/config.py` - CORS origins configuration
