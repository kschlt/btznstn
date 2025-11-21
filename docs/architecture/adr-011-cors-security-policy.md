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

## Rationale

### Why Permissive vs Restrictive?

**Permissive CORS (Chosen):**
- ✅ **Trusted environment** - Small user group (10-20 people), known frontend
- ✅ **Simple** - No enumeration of methods/headers
- ✅ **Future-proof** - No updates when adding API features
- ✅ **Low maintenance** - Set once, forget
- ✅ **Low risk** - Frontend is controlled, not user-submitted

**Restrictive CORS (Rejected):**
- ❌ **More maintenance** - Update config when adding methods/headers
- ❌ **Brittle** - May break if frontend adds headers (e.g., `Accept-Language`)
- ❌ **No real security benefit** - Token auth is the actual security

### Why `allow_credentials=True`?

- Enables cookies (if needed later)
- Enables `Authorization` header
- Standard for authenticated APIs
- **Requires exact origins** (not `["*"]`)

### What CORS Protects (and Doesn't)

**Protects:**
- ✅ JavaScript on `evil.com` accessing `api.betzenstein.app` via browser
- ✅ Cross-site data theft in browser

**Does NOT protect:**
- ❌ Direct API calls (curl, Postman) - CORS is browser-only
- ❌ Server-to-server requests

**Our actual security:**
- Token authentication (HMAC-signed tokens)
- Rate limiting (BR-012)
- Input validation (Pydantic)
- HTTPS only
- **CORS is defense-in-depth**, not primary security

---

## Alternatives Considered

### Restrictive CORS (Enumerate Everything)

```python
allow_origins = ["https://betzenstein.app"]
allow_methods = ["GET", "POST", "PATCH", "DELETE"]
allow_headers = ["Content-Type", "Authorization"]
```

**Rejected:** More maintenance, no security benefit for trusted app.

---

### No CORS (Same-Origin Only)

**Rejected:** Breaks distributed architecture (Vercel ≠ Fly.io).

---

### CORS Proxy

**Architecture:** Browser → Vercel API Routes → Fly.io FastAPI

**Rejected:**
- Adds latency (extra hop)
- More complex (proxy logic)
- Loses stateless API benefit

---

## Consequences

### Positive

✅ **Simple configuration** - No enumeration needed
✅ **Future-proof** - No updates when API changes
✅ **Works in dev + prod** - Just change environment variable
✅ **Low maintenance** - Set once, forget

### Negative

⚠️ **Permissive** - Allows all methods/headers (appropriate for trusted app)
⚠️ **Environment-specific** - Must configure origins correctly
⚠️ **Not suitable for public APIs** - Would need stricter policy

### Neutral

➡️ **CORS is defense-in-depth** - Primary security is token auth + rate limiting
➡️ **Browser-only** - Doesn't prevent direct API calls (by design)

---

## Implementation Pattern

### Configuration

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    allowed_origins: str = "http://localhost:3000"

    def get_allowed_origins(self) -> list[str]:
        """Parse comma-separated CORS origins."""
        return [
            origin.strip()
            for origin in self.allowed_origins.split(",")
            if origin.strip()
        ]
```

### FastAPI Middleware

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Variables

```bash
# .env (development)
ALLOWED_ORIGINS=http://localhost:3000

# Production (Fly.io secrets)
fly secrets set ALLOWED_ORIGINS=https://betzenstein.app

# Multiple origins (dev + preview)
ALLOWED_ORIGINS=http://localhost:3000,https://preview.vercel.app,https://betzenstein.app
```

---

## References

**Related ADRs:**
- ADR-001: Backend Framework (FastAPI)
- ADR-002: Frontend Framework (Next.js)
- ADR-016: Fly.io Backend Hosting (backend domain)
- ADR-017: Vercel Frontend Hosting (frontend domain)
- ADR-019: Authentication & Authorization (token-based security)

**Business Rules:**
- BR-010: Token-based authentication (no cookies initially)
- BR-012: Rate limiting (primary abuse prevention)

**Tools:**
- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
