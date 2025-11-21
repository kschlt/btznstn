# ADR-019: Authentication & Authorization Pattern

**Status:** Accepted
**Date:** 2025-11-19
**Deciders:** Solution Architect
**Context:** Phase 3 (Approval Flow) - need reusable auth pattern

---

## Context

We need authentication and authorization for API endpoints (approve, deny, reopen). The system has unique requirements:

### Business Requirements

**From BR-010:** Token-based access, no login/passwords, tokens never expire

**User Roles:**
- **Requester:** Creates bookings (any email)
- **Approver:** One of three fixed people (Ingeborg, Cornelia, Angelika)
- **Viewer:** Public calendar (no auth)

### Existing Implementation

**Token utilities exist** ([`api/app/core/tokens.py`](../../api/app/core/tokens.py)):
- `generate_token(payload)` - HMAC-SHA256 signing
- `verify_token(token)` - Validates signature, extracts payload

**Missing:**
- FastAPI pattern for token validation in endpoints
- Role-based access control (approver vs requester)
- Consistent auth errors (401 vs 403)

---

## Decision

Use **FastAPI dependency injection** for authentication and authorization.

**Pattern:**
```
Request → Token Dependency → Role Dependency → Endpoint
   ↓            ↓                  ↓              ↓
?token=xxx   Validate          Check role     Business logic
             Extract           Raise 403
```

**Files:**
- `api/app/core/tokens.py` - Already exists (generate/verify)
- `api/app/core/auth.py` - Create dependencies (get_current_token, require_approver, require_requester)

---

## Rationale

### Why Dependency Injection vs Middleware?

**Dependency Injection (Chosen):**
- ✅ Granular control (some endpoints public, some authenticated)
- ✅ Role-specific per endpoint
- ✅ Type-safe (Pydantic models)
- ✅ Standard FastAPI pattern

**Middleware (Rejected):**
- ❌ All-or-nothing (can't have public calendar)
- ❌ Role checking awkward
- ❌ Less explicit

### Why Query Parameter vs Header?

**Query Parameter `?token=xxx` (Chosen):**
- ✅ Email-friendly (clickable links)
- ✅ No JavaScript required
- ✅ Matches BR-010 (action links in emails)

**Header (Rejected):**
- ❌ Can't embed in email links
- ❌ Requires frontend to extract and add header

### Why HMAC vs JWT Libraries?

**HMAC-SHA256 (Chosen):**
- ✅ Simple (built-in `hmac` module)
- ✅ Sufficient for single backend
- ✅ Lightweight

**JWT Libraries (Rejected):**
- ❌ Overkill (don't need asymmetric keys)
- ❌ Extra dependency

---

## Consequences

### Positive

✅ **Reusable across all endpoints** - Same pattern for approve/deny/reopen/etc
✅ **Type-safe** - Pydantic models catch errors
✅ **Explicit** - Clear which endpoints need auth
✅ **Testable** - Easy to mock dependencies

### Negative

⚠️ **Token in URL** - Visible in logs (mitigated: HTTPS, don't log query params)
⚠️ **No expiry** - Per BR-010 (mitigated: rate limiting, trusted users)

### Neutral

➡️ **Custom auth** - Not using OAuth (pragmatic for email-first system)

---

## Implementation Notes

### Auth Dependencies (`api/app/core/auth.py`)

```python
from fastapi import Depends, HTTPException, Query
from app.core.tokens import verify_token

async def get_current_token(token: str = Query(...)) -> TokenPayload:
    """Validate token, extract payload. Raises 401 if invalid."""
    payload = verify_token(token)
    if not payload:
        raise HTTPException(401, "Ungültiger Zugangslink.")
    return TokenPayload(**payload)

async def require_approver(token_data: TokenPayload = Depends(get_current_token)) -> TokenPayload:
    """Require approver role. Raises 403 if not approver."""
    if token_data.role != "approver":
        raise HTTPException(403, "Diese Aktion ist für deine Rolle nicht verfügbar.")
    return token_data
```

### Endpoint Usage

```python
@router.post("/api/v1/bookings/{id}/approve")
async def approve_booking(
    id: UUID,
    token_data: Annotated[TokenPayload, Depends(require_approver)],
    db: AsyncSession = Depends(get_db),
):
    # Auth validated automatically
    return await service.approve_booking(id, token_data.party)
```

### Error Messages (German, from spec)

- Invalid token (401): `"Ungültiger Zugangslink."`
- Wrong role (403): `"Diese Aktion ist für deine Rolle nicht verfügbar."`

---

## References

**Related ADRs:**
- ADR-001: Backend Framework (FastAPI dependency injection)
- ADR-006: Type Safety (Pydantic models)
- ADR-011: CORS Security

**Business Rules:**
- BR-010: Token-based links, no expiry

**Implementation:**
- [`api/app/core/tokens.py`](../../api/app/core/tokens.py) - Token utilities
- [`api/app/core/auth.py`](../../api/app/core/auth.py) - Dependencies (create in Phase 3)
- [`docs/specification/error-handling.md`](../specification/error-handling.md) - Error messages
