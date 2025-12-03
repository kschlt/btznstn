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

### Implementation Constraints

✅ **FastAPI dependency injection REQUIRED** - ALL authenticated endpoints use dependencies (not middleware)
✅ **Token in query parameter** - ALL auth tokens passed via `?token=xxx` (not headers, not body)
✅ **Type-safe auth** - ALL auth dependencies return Pydantic `TokenPayload` models
✅ **German error messages** - ALL auth errors use exact German copy from specification
✅ **Role-specific dependencies** - Use `require_approver` or `require_requester` (not manual role checks)

### Complexity Trade-offs

⚠️ **Token visible in URL** - Tokens appear in query parameters (mitigated: HTTPS, don't log query params)
⚠️ **No token expiry** - Per BR-010, tokens never expire (mitigated: rate limiting, trusted users)
⚠️ **Custom auth pattern** - Not using OAuth/JWT libraries (pragmatic for email-first system)

### Neutral

➡️ **HMAC-SHA256 signing** - Simple, sufficient for single backend (no asymmetric keys needed)

---

## LLM Implementation Constraints

### Required Patterns

**MUST:**
- ALL authenticated endpoints use FastAPI dependency injection (not middleware)
- ALL tokens passed via query parameter `?token=xxx` (not headers, not body)
- ALL auth dependencies return `TokenPayload` Pydantic model (type-safe)
- ALL role checks use `require_approver` or `require_requester` dependencies (not manual checks)
- ALL auth errors use German messages from `docs/specification/error-handling.md`
- Token validation happens in `get_current_token` dependency (single source of truth)
- Role validation happens in role-specific dependencies (`require_approver`, `require_requester`)

**MUST NOT:**
- Use middleware for authentication (violates granular control requirement)
- Put tokens in headers (`Authorization: Bearer xxx`) - not email-friendly
- Put tokens in request body - not email-friendly
- Manually validate tokens in endpoints (use dependencies)
- Manually check roles in endpoints (use role-specific dependencies)
- Use OAuth/JWT libraries (HMAC-SHA256 sufficient, per ADR decision)

**Example - Correct Pattern:**
```python
from typing import Annotated
from fastapi import APIRouter, Depends
from app.core.auth import require_approver, TokenPayload
from app.models.enums import AffiliationEnum

@router.post("/api/v1/bookings/{id}/approve")
async def approve_booking(
    id: UUID,
    token_data: Annotated[TokenPayload, Depends(require_approver)],  # ✅ Auth + role check
    db: AsyncSession = Depends(get_db),
) -> ApprovalResponse:
    """Approve booking (Approver only)."""
    # token_data.party is already validated as AffiliationEnum
    service = BookingService(db)
    return await service.approve_booking(
        booking_id=id,
        approver_party=token_data.party,  # ✅ Type-safe
    )
```

**Example - WRONG (Anti-patterns):**
```python
# ❌ WRONG: Manual token validation
@router.post("/api/v1/bookings/{id}/approve")
async def approve_booking(
    id: UUID,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    payload = verify_token(token)  # Manual validation!
    if not payload:
        raise HTTPException(401, "Invalid token")
    if payload["role"] != "approver":  # Manual role check!
        raise HTTPException(403, "Not allowed")
    # ...

# ❌ WRONG: Token in header
@router.post("/api/v1/bookings/{id}/approve")
async def approve_booking(
    id: UUID,
    authorization: str = Header(...),  # Not email-friendly!
    db: AsyncSession = Depends(get_db),
):
    # ...

# ❌ WRONG: Middleware approach
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # All-or-nothing, can't have public endpoints
    # ...
```

### Applies To

**This constraint affects:**
- ALL authenticated endpoints (Phase 3, 4, 6, 7)
- Approve/deny/reopen endpoints (Phase 3)
- Booking edit endpoints (Phase 2, 6)
- User story specifications must require dependency injection pattern
- Acceptance criteria must validate token in query parameter

### When Writing User Stories

**Ensure specifications include:**
- Endpoint uses FastAPI dependency injection for auth (`Depends(require_approver)` or `Depends(require_requester)`)
- Token passed via query parameter (`?token=xxx`)
- German error messages from `docs/specification/error-handling.md`
- Role-specific dependency matches endpoint purpose (approver endpoints use `require_approver`)

**Validation commands for user story checklists:**
- No manual token validation: `grep -r "verify_token" app/routers/` (should only appear in `app/core/auth.py`)
- No manual role checks: `grep -r 'role.*!=' app/routers/` (should be empty)
- All auth endpoints use dependencies: Review router files for `Depends(require_approver)` or `Depends(require_requester)`
- Token in query parameter: Verify no `Header(...)` or `Body(...)` for tokens

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - FastAPI dependency injection pattern
- [ADR-006](adr-006-type-safety.md) - Pydantic models for type safety

**Related Specifications:**
- Token utilities: `api/app/core/tokens.py`
- Auth dependencies: `api/app/core/auth.py` (create in Phase 3)
- German error messages: `docs/specification/error-handling.md`
- Business rules: BR-010 (token-based links, no expiry)

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
