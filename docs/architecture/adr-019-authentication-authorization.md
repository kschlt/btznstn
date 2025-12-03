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

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Authentication Pattern | FastAPI dependency injection | Middleware, manual validation |
| Token Location | Query parameter `?token=xxx` | Header, request body |
| Token Signing | HMAC-SHA256 | JWT libraries, OAuth |
| Role Checking | Role-specific dependencies (`require_approver`, `require_requester`) | Manual role checks in endpoints |
| Error Messages | German messages from specification | English messages, custom messages |

---

## Rationale

**Why FastAPI Dependency Injection:**
- Dependency injection provides granular control → **Constraint:** MUST use FastAPI dependency injection for authentication (not middleware)
- Dependency injection enables role-specific per endpoint → **Constraint:** MUST use role-specific dependencies (`require_approver`, `require_requester`)
- Dependency injection provides type-safe auth → **Constraint:** MUST use Pydantic `TokenPayload` models for type safety

**Why Query Parameter (not Header):**
- Query parameter enables email-friendly links → **Constraint:** MUST use query parameter `?token=xxx` for tokens (email-friendly, clickable links, matches BR-010)

**Why HMAC-SHA256 (not JWT Libraries):**
- HMAC-SHA256 is simple (built-in module) → **Constraint:** MUST use HMAC-SHA256 signing (sufficient for single backend, lightweight)

**Why NOT Middleware:**
- Middleware is all-or-nothing → **Violation:** Can't have public calendar endpoints, role checking awkward, violates granular control requirement

**Why NOT Header:**
- Header can't embed in email links → **Violation:** Not email-friendly, requires frontend to extract and add header, violates BR-010 requirement

**Why NOT JWT Libraries:**
- JWT libraries are overkill → **Violation:** Don't need asymmetric keys, extra dependency, violates simplicity requirement

---

## Consequences

### MUST (Required)

- ALL authenticated endpoints MUST use FastAPI dependency injection (not middleware) - Granular control, role-specific per endpoint
- ALL tokens MUST be passed via query parameter `?token=xxx` (not headers, not body) - Email-friendly, clickable links, matches BR-010
- ALL auth dependencies MUST return `TokenPayload` Pydantic model (type-safe) - Type safety requirement
- ALL role checks MUST use `require_approver` or `require_requester` dependencies (not manual checks) - Single source of truth, consistent error handling
- ALL auth errors MUST use German messages from `docs/specification/error-handling.md` - Specification requirement
- Token validation MUST happen in `get_current_token` dependency (single source of truth) - Consistent validation, prevents duplication
- Role validation MUST happen in role-specific dependencies (`require_approver`, `require_requester`) - Consistent role checking, prevents duplication

### MUST NOT (Forbidden)

- MUST NOT use middleware for authentication - Violates granular control requirement, can't have public endpoints
- MUST NOT put tokens in headers (`Authorization: Bearer xxx`) - Not email-friendly, violates BR-010 requirement
- MUST NOT put tokens in request body - Not email-friendly, violates BR-010 requirement
- MUST NOT manually validate tokens in endpoints - Violates single source of truth, use dependencies instead
- MUST NOT manually check roles in endpoints - Violates single source of truth, use role-specific dependencies instead
- MUST NOT use OAuth/JWT libraries - HMAC-SHA256 sufficient, violates simplicity requirement

### Trade-offs

- Token visible in URL - MUST use query parameter for email-friendly links. MUST NOT use headers or body. Mitigated: HTTPS, don't log query params.
- No token expiry - Per BR-010, tokens never expire. MUST NOT add expiry without business rule change. Mitigated: rate limiting, trusted users.
- Custom auth pattern - MUST use HMAC-SHA256 (not OAuth/JWT). MUST NOT use OAuth/JWT libraries. Pragmatic for email-first system.

### Code Examples

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

- ALL authenticated endpoints (Phase 3, 4, 6, 7)
- Approve/deny/reopen endpoints (Phase 3)
- Booking edit endpoints (Phase 2, 6)
- File patterns: `app/routers/*.py`, `app/core/auth.py`

### Validation Commands

- `grep -r "verify_token" app/routers/` (should only appear in `app/core/auth.py` - no manual validation)
- `grep -r 'role.*!=' app/routers/` (should be empty - no manual role checks)
- `grep -r "Depends(require_approver)\|Depends(require_requester)" app/routers/` (should be present - all auth endpoints use dependencies)
- `grep -r "Header.*token\|Body.*token" app/routers/` (should be empty - tokens in query parameter only)

---

## References

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - Backend Framework (FastAPI dependency injection)
- [ADR-006](adr-006-type-safety.md) - Type Safety (Pydantic models)
- [ADR-011](adr-011-cors-security-policy.md) - CORS Security Policy

**Business Rules:**
- BR-010: Token-based links, no expiry

**Implementation:**
- `api/app/core/tokens.py` - Token utilities (HMAC-SHA256 signing)
- `api/app/core/auth.py` - Auth dependencies (create in Phase 3)
- `docs/specification/error-handling.md` - German error messages
