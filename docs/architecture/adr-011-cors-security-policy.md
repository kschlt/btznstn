# ADR-011: CORS Security Policy

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)

---

## Context

We need to define a Cross-Origin Resource Sharing (CORS) policy for the FastAPI backend. The policy must:

- Allow the Next.js frontend (different domain) to access the API
- Support credentials (cookies, authorization headers)
- Enable all necessary HTTP methods (GET, POST, PATCH, DELETE)
- Work in development (localhost) and production (different domains)
- Maintain security appropriate for a small, trusted user group

### Requirements from Architecture

From `docs/architecture/README.md`:
- Backend on Fly.io (`api.betzenstein.app`)
- Frontend on Vercel (`betzenstein.app`)
- Different origins require CORS configuration
- Token-based authentication via URL parameters (no cookies initially, but CORS should support them)

### Security Context

**Trust model:**
- Small, trusted group (~10-20 users)
- No public API access
- Frontend is known and controlled
- Not a public-facing API with unknown clients

---

## Decision

We will use a **permissive CORS policy** for the trusted single-page application:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),  # Configurable via environment
    allow_credentials=True,                         # Enable credentials
    allow_methods=["*"],                           # All HTTP methods
    allow_headers=["*"],                           # All headers
)
```

**Configuration:**
- `allow_origins`: Environment-configurable (comma-separated list)
  - Development: `http://localhost:3000`
  - Production: `https://betzenstein.app`
- `allow_credentials`: `True` (allows cookies, authorization headers)
- `allow_methods`: `["*"]` (GET, POST, PATCH, DELETE, OPTIONS)
- `allow_headers`: `["*"]` (Content-Type, Authorization, etc.)

---

## Rationale

### 1. Why Permissive CORS?

#### a) Trusted Environment

**Context:**
- Small user group (10-20 people)
- Known frontend origin
- No public API access
- Private application

**Permissive policy is appropriate:**
- ✅ **Simplifies development** - No need to enumerate every header/method
- ✅ **Reduces maintenance** - No updates when adding new API features
- ✅ **Low risk** - Frontend is controlled, not user-submitted

**Evidence:** OWASP guidance allows permissive CORS for trusted origins.

#### b) Browser Security Model

**What CORS prevents:**
- Cross-site request forgery (CSRF) from untrusted sites
- JavaScript on `evil.com` accessing `api.betzenstein.app`

**What CORS does NOT prevent:**
- Direct API calls (curl, Postman, etc.)
- Server-to-server requests

**Our security:**
- Token-based authentication (signed HMAC tokens)
- Rate limiting (BR-012)
- Input validation (Pydantic)
- **CORS is defense-in-depth, not primary security**

### 2. Why `allow_credentials=True`?

**Rationale:**
- Enables cookies (if needed later)
- Enables `Authorization` header
- Standard for authenticated APIs

**Note:** With `allow_credentials=True`, `allow_origins` cannot be `["*"]`. Must specify exact origins.

**Our implementation:**
```python
# Development
allow_origins = ["http://localhost:3000"]

# Production
allow_origins = ["https://betzenstein.app"]
```

### 3. Why `allow_methods=["*"]`?

**Rationale:**
- API uses standard REST methods: GET, POST, PATCH, DELETE
- Future-proof (no updates needed when adding new endpoints)
- No security risk (token authentication required regardless of method)

**Alternative considered:** Enumerate methods `["GET", "POST", "PATCH", "DELETE"]`

**Rejected because:**
- ❌ More verbose
- ❌ Requires updates when API changes
- ❌ No security benefit (authentication still required)

### 4. Why `allow_headers=["*"]`?

**Rationale:**
- API accepts standard headers: `Content-Type`, `Authorization`
- Future-proof (no updates needed for new headers)
- No security risk (Pydantic validates request bodies)

**Alternative considered:** Enumerate headers `["Content-Type", "Authorization"]`

**Rejected because:**
- ❌ More verbose
- ❌ May break if frontend sends additional headers (e.g., `X-Request-ID`)
- ❌ No security benefit

---

## Alternatives Considered

### Restrictive CORS (Enumerate Everything)

**Configuration:**
```python
allow_origins = ["https://betzenstein.app"]  # Only production domain
allow_credentials = True
allow_methods = ["GET", "POST", "PATCH", "DELETE"]  # Specific methods
allow_headers = ["Content-Type", "Authorization"]   # Specific headers
```

**Pros:**
- More explicit
- Slightly more restrictive

**Cons:**
- ❌ **More maintenance** - Update config when adding methods/headers
- ❌ **Brittle** - May break if frontend adds headers (e.g., `Accept-Language`)
- ❌ **No real security benefit** - Token auth is the actual security

**Decision:** Permissive policy better for small, trusted app. Maintenance burden > security benefit.

---

### No CORS (Same-Origin Only)

**Configuration:**
```python
# No CORS middleware
```

**Pros:**
- Most restrictive
- No cross-origin access

**Cons:**
- ❌ **Breaks architecture** - Frontend and backend on different domains
- ❌ **Not viable** - Vercel (frontend) ≠ Fly.io (backend)

**Decision:** CORS required for distributed architecture.

---

### CORS Proxy

**Architecture:**
```
Browser → Vercel (Next.js) → API Routes (proxy) → Fly.io (FastAPI)
```

**Pros:**
- No CORS needed (API calls from Next.js server, not browser)

**Cons:**
- ❌ **Adds latency** - Extra hop through Vercel
- ❌ **More complex** - Maintain proxy logic
- ❌ **Stateless API benefit lost** - Proxy must forward tokens

**Decision:** Direct browser → API is simpler, faster.

---

## Consequences

### Positive

✅ **Simple configuration** - No enumeration of methods/headers
✅ **Future-proof** - No updates needed when API changes
✅ **Works in dev + prod** - Just change `allow_origins` environment variable
✅ **Standard approach** - Widely used for SPAs
✅ **Low maintenance** - Set once, forget

### Negative

⚠️ **Permissive** - Allows all methods/headers (appropriate for trusted app)
⚠️ **Environment-specific** - Must configure origins correctly per environment
⚠️ **Not suitable for public APIs** - Would need stricter policy for untrusted clients

### Neutral

➡️ **CORS is defense-in-depth** - Primary security is token authentication + rate limiting
➡️ **Browser-only protection** - Doesn't prevent direct API calls (by design)

---

## Implementation Notes

### Configuration

**Environment variables:**
```bash
# .env (development)
ALLOWED_ORIGINS=http://localhost:3000

# Fly.io secrets (production)
fly secrets set ALLOWED_ORIGINS=https://betzenstein.app
```

**Settings class:**
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

**FastAPI middleware:**
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

### Multiple Origins (Development + Preview)

**Support multiple origins:**
```bash
# Allow localhost + Vercel preview deployments
ALLOWED_ORIGINS=http://localhost:3000,https://betzenstein-preview.vercel.app,https://betzenstein.app
```

**Parsed as:**
```python
["http://localhost:3000", "https://betzenstein-preview.vercel.app", "https://betzenstein.app"]
```

### Preflight Requests (OPTIONS)

**CORS preflight:**
- Browser sends `OPTIONS` request before actual request
- FastAPI + CORSMiddleware handles automatically
- No manual `OPTIONS` routes needed

**Verification:**
```bash
# Preflight request
curl -X OPTIONS https://api.betzenstein.app/bookings \
  -H "Origin: https://betzenstein.app" \
  -H "Access-Control-Request-Method: POST" \
  -v

# Expected response headers:
# Access-Control-Allow-Origin: https://betzenstein.app
# Access-Control-Allow-Methods: GET, POST, PATCH, DELETE, OPTIONS
# Access-Control-Allow-Headers: *
# Access-Control-Allow-Credentials: true
```

---

## Validation

### Development Check

**Test CORS from frontend:**
```typescript
// app/lib/api/client.ts
const response = await fetch('http://localhost:8000/api/v1/bookings', {
  method: 'GET',
  credentials: 'include',  // Sends cookies if present
})
```

**Expected:**
- ✅ Request succeeds
- ✅ No CORS errors in browser console
- ✅ Response accessible to JavaScript

### Production Check

**Test CORS from production frontend:**
```bash
curl -X GET https://api.betzenstein.app/api/v1/bookings \
  -H "Origin: https://betzenstein.app" \
  -v
```

**Expected response headers:**
```
Access-Control-Allow-Origin: https://betzenstein.app
Access-Control-Allow-Credentials: true
```

### Security Check

**Verify unauthorized origin blocked:**
```bash
curl -X GET https://api.betzenstein.app/api/v1/bookings \
  -H "Origin: https://evil.com" \
  -v
```

**Expected:**
- ❌ No `Access-Control-Allow-Origin` header (browser blocks response)
- ✅ Server returns 200 (CORS is browser-enforced, not server-enforced)

**Note:** Token authentication prevents unauthorized access regardless of origin.

---

## Security Considerations

### What CORS Protects

✅ **Prevents malicious JavaScript** on `evil.com` from accessing `api.betzenstein.app` via browser
✅ **Prevents cross-site data theft** (attacker can't read API responses in browser)

### What CORS Does NOT Protect

❌ **Direct API calls** - curl, Postman, scripts can bypass CORS (browser-only)
❌ **CSRF on non-authenticated endpoints** - Need CSRF tokens for cookie-based auth (we use tokens in URL, not cookies)

### Actual Security Measures

**Primary security:**
1. **Token authentication** (BR-010) - HMAC-signed tokens required
2. **Rate limiting** (BR-012) - Prevents abuse
3. **Input validation** (Pydantic) - Prevents injection
4. **HTTPS only** (ADR-007) - Prevents MITM

**CORS is defense-in-depth**, not primary security.

---

## References

- [FastAPI CORS Documentation](https://fastapi.tiangolo.com/tutorial/cors/)
- [MDN: CORS](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [OWASP: CORS Security](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [Starlette CORSMiddleware](https://www.starlette.io/middleware/#corsmiddleware)

**Related ADRs:**
- [ADR-001: API Framework](adr-001-backend-framework.md) - FastAPI backend
- [ADR-002: Web Framework](adr-002-frontend-framework.md) - Next.js frontend
- [ADR-007: Deployment Strategy](adr-007-deployment.md) - Fly.io + Vercel (different domains)

**Business Rules:**
- BR-010: Token-based authentication (no cookies initially)
- BR-012: Rate limiting (primary abuse prevention)

---

## Changelog

- **2025-01-19:** Initial decision - Permissive CORS policy for trusted SPA
