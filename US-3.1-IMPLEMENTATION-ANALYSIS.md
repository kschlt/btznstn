# US-3.1 Implementation Analysis & Questions
**Date:** 2025-11-19
**User Story:** US-3.1 Approve Booking
**Status:** Pre-implementation analysis (awaiting clarifications)

---

## Executive Summary

This document analyzes 5 critical implementation questions for US-3.1 (Approve Booking endpoint). Each question includes:
- Context from existing codebase & specifications
- Analysis of options
- **Recommendation** (highlighted for quick review)
- Questions for clarification (if needed)

**Status of existing infrastructure:**
- ✅ Token authentication implemented ([api/app/core/tokens.py](api/app/core/tokens.py:1))
- ✅ Error handling pattern established (ValueError → HTTPException)
- ✅ Timeline events fully specified
- ✅ German error messages documented
- ⚠️ Email notifications NOT yet implemented (Phase 4)

---

## Question 1: BR-024 SELECT FOR UPDATE - What to Lock?

### Context

**BR-024:** "First-action-wins for concurrent approval/denial actions on same booking."

**Scenario:** Two approvers (e.g., Ingeborg and Cornelia) click "Approve" at nearly the same time.

**Current Implementation Pattern:**
- Existing code uses repository pattern with async SQLAlchemy
- No locking currently implemented in Phase 2 (create/update/cancel)

### Analysis

**Option A: Lock only the Booking row**
```python
# In approval endpoint
booking = await session.execute(
    select(Booking).where(Booking.id == booking_id).with_for_update()
).scalar_one_or_none()
```

**Pros:**
- Simple, standard pattern
- Prevents concurrent state transitions (Pending → Confirmed)
- Sufficient for most race conditions

**Cons:**
- Doesn't lock individual Approval rows
- Could theoretically have race on approval decision update (unlikely with proper logic)

---

**Option B: Lock both Booking + specific Approval row**
```python
# Lock both tables
booking = await session.execute(
    select(Booking).where(Booking.id == booking_id).with_for_update()
).scalar_one_or_none()

approval = await session.execute(
    select(Approval)
    .where(Approval.booking_id == booking_id, Approval.party == approver_party)
    .with_for_update()
).scalar_one_or_none()
```

**Pros:**
- Maximum safety - guarantees no concurrent updates to same approval
- Prevents edge case where two requests with same token update same approval

**Cons:**
- More complex
- Slightly slower (two locks)
- Overkill for typical scenarios (different approvers = different rows)

---

**Option C: Lock Booking + load all Approvals with relationship**
```python
booking = await session.execute(
    select(Booking)
    .options(selectinload(Booking.approvals))
    .where(Booking.id == booking_id)
    .with_for_update()
).scalar_one_or_none()
```

**Pros:**
- Single query loads everything needed
- Booking lock prevents concurrent state changes
- Standard ORM pattern

**Cons:**
- Approvals themselves not explicitly locked (but Booking lock provides serialization)

---

### 🎯 **RECOMMENDATION: Option A (Lock Booking only)**

**Rationale:**
1. **Sufficient for BR-024:** The critical race condition is on `booking.status` transition (Pending → Confirmed). Locking the Booking row serializes this.

2. **Different approvers = different rows:** When Ingeborg and Cornelia approve simultaneously, they're updating **different** Approval rows. No conflict.

3. **Same approver = idempotent:** If same token hits twice (BR-010), we check `if approval.decision == Approved: return` before updating. First request wins, second is no-op.

4. **Simpler = better:** Matches standard patterns, easier to test and maintain.

**Implementation:**
```python
async def approve_booking(booking_id: UUID, approver_party: AffiliationEnum, db: AsyncSession):
    # Lock booking row for duration of transaction
    booking = await db.execute(
        select(Booking)
        .where(Booking.id == booking_id)
        .with_for_update()
    )
    booking = booking.scalar_one_or_none()

    if not booking:
        raise ValueError("Booking not found")

    # Check state (Denied/Canceled = reject)
    if booking.status in [StatusEnum.DENIED, StatusEnum.CANCELED]:
        raise ValueError("Diese Aktion ist für deine Rolle nicht verfügbar.")

    # Check past (BR-014)
    if booking.end_date < get_today():
        raise ValueError("Dieser Eintrag liegt in der Vergangenheit...")

    # Get approval record (no lock needed - different approvers = different rows)
    approval = await db.execute(
        select(Approval)
        .where(Approval.booking_id == booking_id, Approval.party == approver_party)
    )
    approval = approval.scalar_one_or_none()

    # Idempotency check (BR-010)
    if approval.decision == DecisionEnum.APPROVED:
        # Already approved - return success, no changes
        return {"message": "Danke – du hast zugestimmt.", "already_done": True}

    # Update approval
    approval.decision = DecisionEnum.APPROVED
    approval.decided_at = get_now()

    # Check if final approval (BR-003)
    approved_count = sum(1 for a in booking.approvals if a.decision == DecisionEnum.APPROVED)
    if approved_count == 3:
        booking.status = StatusEnum.CONFIRMED

    # Update activity timestamp
    booking.last_activity_at = get_now()

    # Create timeline event
    # (code here)

    await db.commit()
    return {"message": "Danke – du hast zugestimmt.", "status": booking.status}
```

**Testing:**
- Test concurrent approvals (different parties) → both succeed
- Test concurrent approval + denial (same booking) → first wins via Booking lock
- Test idempotent approval (same token twice) → second returns early, no DB update

---

### ❓ **QUESTION FOR USER:**

**Q:** Do you agree with locking only the Booking row (Option A), or do you want to lock both Booking + Approval for maximum safety (Option B)?

**My recommendation:** Option A is sufficient and simpler.

---

## Question 2: Timeline Events - What to Log?

### Context from Specification

From [docs/specification/data-model.md](docs/specification/data-model.md:228):

**EventType Values:**
- **Submitted:** Initial submission ✅
- **Approved:** Approver approved (store approver name) ✅
- **Denied:** Approver denied (store approver name) ✅
- **EditedAffectsApproval:** Date edit that reset approvals (store diff) ✅
- **EditedNoApprovalChange:** Date edit that kept approvals (store diff) ✅
- **Confirmed:** All three approved (final approval) ✅
- **Canceled:** Requester canceled (or System auto-canceled) ✅
- **Reopened:** Requester reopened from Denied ✅

**Logged:**
- ✅ Submitted
- ✅ Approved (by named party)
- ✅ Denied (by named party)
- ✅ **All date edits** (with diffs and approval impact)
- ✅ Confirmed
- ✅ Canceled
- ✅ Reopened

**NOT Logged:**
- ❌ Party size edits
- ❌ Affiliation edits
- ❌ First name edits
- ❌ Description edits
- ❌ Digest/system events (not public-facing in timeline)

**Note Field (internal context):**
- Date diffs: "01.–05.08. → 03.–08.08."
- Auto-cancel reason: "Auto-canceled past-dated pending booking"
- **Approver name for Approved/Denied events** ← relevant for US-3.1

### Analysis for US-3.1 (Approve Endpoint)

**What to log when approval happens:**

1. **Always create timeline event** with:
   - `EventType = Approved`
   - `Actor = Approver`
   - `Note = "{Approver party name}"` (e.g., "Ingeborg")
   - `When = now()`

2. **If final approval** (3rd approval that triggers Confirmed):
   - Create **TWO** timeline events:
     - Event 1: `Approved` (for this approver's action)
     - Event 2: `Confirmed` (for status transition)

   **OR** (simpler):
   - Create **ONE** event: `Confirmed` with note indicating who gave final approval

   **Spec says:** Both "Approved" and "Confirmed" are logged events.

3. **Idempotent approval** (already approved):
   - **Do NOT create duplicate timeline event**
   - Return early before timeline creation

### 🎯 **RECOMMENDATION: Log both "Approved" + "Confirmed" (if final)**

**Implementation:**
```python
# After updating approval.decision = Approved

# Always log individual approval
timeline_event = TimelineEvent(
    booking_id=booking.id,
    event_type=EventTypeEnum.APPROVED,
    actor=ActorEnum.APPROVER,
    note=f"{approver_party.value}",  # "Ingeborg", "Cornelia", or "Angelika"
    when=get_now(),
)
await timeline_repo.create(timeline_event)

# If final approval, also log Confirmed
if approved_count == 3:
    booking.status = StatusEnum.CONFIRMED

    confirmed_event = TimelineEvent(
        booking_id=booking.id,
        event_type=EventTypeEnum.CONFIRMED,
        actor=ActorEnum.APPROVER,  # Or SYSTEM?
        note=f"Alle drei genehmigt (letzte: {approver_party.value})",
        when=get_now(),
    )
    await timeline_repo.create(confirmed_event)
```

**Rationale:**
1. Spec explicitly lists both "Approved" and "Confirmed" as logged events
2. Separate events make timeline clearer:
   - "Ingeborg approved"
   - "Cornelia approved"
   - "Angelika approved"
   - "Booking confirmed" ← distinct from individual approvals
3. Allows querying "when was it confirmed?" separately from "who approved when?"

### ✅ **NO GAPS FOUND**

Your specification is **complete** for timeline events. All scenarios are covered:
- Individual approvals → logged ✅
- Final confirmation → logged ✅
- Denials → logged ✅
- Edits (date changes) → logged with diffs ✅
- Non-logged edits (party size, affiliation) → explicitly excluded ✅

**Only clarification needed:**

### ❓ **QUESTION FOR USER:**

**Q2a:** When final approval happens, should we create:
- **Option A:** TWO events (`Approved` for approver + `Confirmed` for status change)
- **Option B:** ONE event (`Confirmed` only, with note about who gave final approval)

**My recommendation:** Option A (two events) - clearer audit trail.

**Q2b:** For `Confirmed` event, should `Actor` be:
- `Approver` (the person who gave final approval)
- `System` (automatic state transition)

**My recommendation:** `Approver` (it's a human action, not automated).

---

## Question 3: Email Notifications - Architecture Decision

### Context

**Current State:**
- Phase 2 (Booking API) complete - NO email sending ✅
- Phase 3 (Approval Flow) - current work ⬅️
- Phase 4 (Email Integration) - NOT started ⚠️

**Email requirements from spec:**
- Approval triggers notifications (requester notified when approved)
- Final approval triggers confirmation emails (requester + all approvers)
- Resend integration coming in Phase 4

**Existing Pattern (from booking_service.py):**
- Services have access to repositories (booking, approval, timeline)
- No email service exists yet
- No notification queue exists yet

### Analysis

**Option A: Inline email sending in endpoint**
```python
# In approve endpoint
async def approve_booking(...):
    # ... approval logic ...

    # Send email immediately
    await send_approval_email(requester_email, booking)

    return response
```

**Pros:**
- Simple, direct
- Works for synchronous flows

**Cons:**
- ❌ Blocks API response on email delivery
- ❌ If email fails, request fails (bad UX)
- ❌ No retry logic (BR-022 requires retries)
- ❌ Tight coupling (approval logic + email delivery)

---

**Option B: Placeholder/stub in service, implement in Phase 4**
```python
# Phase 3 (NOW): Add placeholder
async def approve_booking(...):
    # ... approval logic ...

    # TODO(Phase 4): Implement email notification
    # await self.notification_service.send_approval_email(...)

    return response
```

**Pros:**
- ✅ Clear separation of concerns
- ✅ Approval flow works immediately (no email dependency)
- ✅ Easy to find placeholders later (search "TODO(Phase 4)")

**Cons:**
- No emails sent in Phase 3 (acceptable if documented)
- Need to remember to implement later

---

**Option C: Event-driven architecture (timeline events trigger emails)**
```python
# Phase 3 (NOW): Emit timeline event
timeline_event = TimelineEvent(event_type=Approved, ...)
await timeline_repo.create(timeline_event)

# Phase 4 (LATER): Background worker listens for timeline events
# Worker sees "Approved" event → sends email asynchronously
```

**Pros:**
- ✅ Clean separation (approval doesn't know about emails)
- ✅ Async/non-blocking (timeline event persisted, email sent later)
- ✅ Retry logic easy to add (worker retries failed emails)
- ✅ Matches BR-022 (exponential backoff in worker, not endpoint)
- ✅ Scalable (can add more event listeners later)

**Cons:**
- More complex architecture
- Requires background worker setup (Celery, or simple async task)

---

**Option D: Hybrid - Service method exists, but empty**
```python
# Phase 3 (NOW): Define interface in booking_service.py
class BookingService:
    async def _send_notifications_after_approval(self, booking: Booking, approver: str):
        """
        Send notification emails after approval.

        Phase 4: Implement with Resend integration.
        For now, this is a no-op.
        """
        # TODO(Phase 4): Implement
        pass

# In approval logic
await self._send_notifications_after_approval(booking, approver_party.value)
```

**Pros:**
- ✅ Clear architecture boundary
- ✅ Easy to test (mock this method in Phase 3 tests)
- ✅ Method signature defined now, implementation later
- ✅ No breaking changes when implementing Phase 4

**Cons:**
- Slightly more code now for no immediate functionality

---

### 🎯 **RECOMMENDATION: Option D (Service method stub) or Option C (Event-driven)**

**My preference: Option D** (simpler for this project size)

**Rationale:**
1. **Option D is pragmatic:** Defines clear contract now, implements later
2. **Easy testing:** Mock `_send_notifications_after_approval()` in tests
3. **No dependency hell:** Phase 3 tests don't need Resend setup
4. **Clear TODO tracking:** One method to implement in Phase 4

**Implementation:**

```python
# In booking_service.py (Phase 3)

class BookingService:
    async def approve_booking(self, booking_id: UUID, approver_party: AffiliationEnum) -> ApprovalResponse:
        """Approve a booking (US-3.1)."""
        # ... approval logic ...

        # Timeline event
        await self.timeline_repo.create(timeline_event)

        # Notifications (stub for Phase 4)
        await self._send_approval_notifications(booking, approver_party.value, is_final_approval)

        return response

    async def _send_approval_notifications(
        self,
        booking: Booking,
        approver_name: str,
        is_final: bool,
    ) -> None:
        """
        Send email notifications after approval.

        Triggers:
        - Single approval: Notify requester ("{Approver} has approved")
        - Final approval: Notify requester + all approvers ("Booking confirmed!")

        Business Rules:
        - BR-022: Email retry logic (3 attempts, exponential backoff)
        - BR-011: All copy in German

        Phase 4 Implementation:
        - Integrate with Resend API
        - Use templates from docs/specification/notifications.md
        - Implement retry logic per BR-022

        For Phase 3: No-op (emails deferred to Phase 4).
        """
        # TODO(Phase 4): Implement email sending
        # if is_final:
        #     await self.notification_service.send_confirmation_email(booking)
        # else:
        #     await self.notification_service.send_approval_email(booking, approver_name)
        pass
```

**Phase 4 User Story addition:**
```gherkin
Scenario: Backfill email notifications for approval flow
  Given approval endpoints implemented in Phase 3
  When implementing US-4.2 (Email Templates)
  Then implement BookingService._send_approval_notifications()
  And verify emails sent for single approval
  And verify emails sent for final approval (confirmation)
```

---

### ❓ **QUESTIONS FOR USER:**

**Q3a:** Do you prefer:
- **Option D** (stub method, implement in Phase 4) ← My recommendation
- **Option C** (event-driven with background worker)

**Q3b:** Should Phase 3 user story explicitly mention "email notifications deferred to Phase 4" in acceptance criteria, or is the stub method self-documenting enough?

**Q3c:** Do you want me to create a tracking issue/checklist for Phase 4 to ensure we don't miss implementing the stub?

---

## Question 4: Authorization - Token Middleware Status

### Current State (from codebase inspection)

✅ **Token utilities implemented:** [api/app/core/tokens.py](api/app/core/tokens.py:1)
- `generate_token(payload)` - creates HMAC-SHA256 signed token
- `verify_token(token)` - validates signature and extracts payload

✅ **Token structure defined:**
```python
{
  "email": "user@example.com",
  "role": "requester" | "approver",
  "booking_id": "uuid",  # Optional
  "party": "Ingeborg" | "Cornelia" | "Angelika",  # For approver
  "iat": 1234567890  # Issued-at timestamp
}
```

❌ **Middleware NOT implemented yet** - No automatic token validation per request

**Current pattern (from existing endpoints):**
```python
# In routers/bookings.py - manual token handling
@router.get("/api/v1/bookings/{id}")
async def get_booking(
    id: UUID,
    token: str = Query(...),  # Token as query parameter
    db: AsyncSession = Depends(get_db),
):
    # Manual validation (if needed)
    payload = verify_token(token)
    if not payload:
        raise HTTPException(401, "Ungültiger Zugangslink.")

    # Manual authorization
    if payload["role"] != "requester" or payload.get("booking_id") != str(id):
        raise HTTPException(403, "Du hast keinen Zugriff auf diesen Eintrag.")

    # ... endpoint logic ...
```

### Analysis

**Current approach works but has issues:**
1. ❌ Repetitive code (every endpoint validates manually)
2. ❌ Easy to forget authorization check
3. ❌ Error messages might be inconsistent
4. ✅ Explicit (easy to see what's happening)

**Better approach: Dependency injection**

```python
# Create auth dependency in app/core/auth.py

from typing import Annotated
from fastapi import Depends, HTTPException, Query, status
from app.core.tokens import verify_token

class TokenPayload(BaseModel):
    """Validated token payload."""
    email: str
    role: Literal["requester", "approver"]
    booking_id: UUID | None = None
    party: Literal["Ingeborg", "Cornelia", "Angelika"] | None = None
    iat: int

async def get_current_token(token: str = Query(..., description="Access token")) -> TokenPayload:
    """
    Validate token and extract payload.

    Raises:
        401: Invalid token signature
    """
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Zugangslink.",
        )

    return TokenPayload(**payload)

async def require_approver(token_data: Annotated[TokenPayload, Depends(get_current_token)]) -> TokenPayload:
    """
    Require approver role.

    Raises:
        403: Not an approver
    """
    if token_data.role != "approver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Diese Aktion ist für deine Rolle nicht verfügbar.",
        )

    return token_data

# Usage in endpoint:
@router.post("/api/v1/bookings/{id}/approve")
async def approve_booking(
    id: UUID,
    token_data: Annotated[TokenPayload, Depends(require_approver)],
    db: AsyncSession = Depends(get_db),
):
    """Approve booking (approver only)."""
    approver_party = AffiliationEnum(token_data.party)

    # Additional check: party matches booking
    # (Could be another dependency, but inline is fine)

    service = BookingService(db)
    return await service.approve_booking(id, approver_party)
```

### 🎯 **RECOMMENDATION: Implement auth dependencies now (part of US-3.1)**

**Rationale:**
1. **Needed for approval endpoint:** US-3.1 requires approver-only access
2. **Reusable:** Deny (US-3.2) and Reopen (US-3.3) need same pattern
3. **Small effort:** ~30 lines of code, easy to test
4. **Big benefit:** Cleaner endpoints, consistent error messages

**Files to create:**
- `api/app/core/auth.py` - Token dependencies
- `api/tests/test_auth.py` - Dependency tests

**Implementation approach:**
```python
# app/core/auth.py

from typing import Annotated, Literal
from uuid import UUID

from fastapi import Depends, HTTPException, Query, status
from pydantic import BaseModel

from app.core.tokens import verify_token
from app.models.enums import AffiliationEnum


class TokenPayload(BaseModel):
    """Validated and parsed token payload."""

    email: str
    role: Literal["requester", "approver"]
    booking_id: UUID | None = None
    party: AffiliationEnum | None = None
    iat: int


async def get_current_token(
    token: str = Query(..., description="Access token from URL")
) -> TokenPayload:
    """
    Dependency: Validate token and extract payload.

    Raises:
        HTTPException 401: Invalid token
    """
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Zugangslink.",
        )

    # Parse party if present
    if payload.get("party"):
        payload["party"] = AffiliationEnum(payload["party"])

    return TokenPayload(**payload)


async def require_approver(
    token_data: Annotated[TokenPayload, Depends(get_current_token)]
) -> TokenPayload:
    """
    Dependency: Require approver role.

    Raises:
        HTTPException 403: Not an approver
    """
    if token_data.role != "approver":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Diese Aktion ist für deine Rolle nicht verfügbar.",
        )

    if not token_data.party:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ungültiger Zugangslink (keine Partei zugeordnet).",
        )

    return token_data


async def require_requester(
    token_data: Annotated[TokenPayload, Depends(get_current_token)]
) -> TokenPayload:
    """
    Dependency: Require requester role.

    Raises:
        HTTPException 403: Not a requester
    """
    if token_data.role != "requester":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Diese Aktion ist nur für Anfragende verfügbar.",
        )

    return token_data
```

**Usage in approve endpoint:**
```python
@router.post("/api/v1/bookings/{id}/approve")
async def approve_booking(
    id: UUID,
    token_data: Annotated[TokenPayload, Depends(require_approver)],
    db: AsyncSession = Depends(get_db),
) -> ApprovalResponse:
    """
    Approve a booking (Approver only).

    Authorization:
    - Token must have role = approver
    - Token must have party field (Ingeborg, Cornelia, or Angelika)

    Business Rules:
    - BR-003: Check if final approval (all 3 approved)
    - BR-010: Idempotent (approving twice = no error)
    - BR-014: Reject past bookings
    - BR-024: First-action-wins (SELECT FOR UPDATE)
    """
    service = BookingService(db)
    return await service.approve_booking(
        booking_id=id,
        approver_party=token_data.party,  # Already validated by dependency
    )
```

### ✅ **ANSWER: Auth utilities exist, middleware does NOT**

**What's implemented:**
- ✅ Token generation (HMAC-SHA256)
- ✅ Token verification (signature validation)
- ✅ Token structure defined

**What's missing (need to implement for US-3.1):**
- ❌ FastAPI dependencies for token validation
- ❌ Role-based access control (approver vs requester)
- ❌ Reusable auth pattern

**Action items for US-3.1:**
1. Create `app/core/auth.py` with dependencies
2. Create tests for auth dependencies
3. Use in approve endpoint
4. Reuse for deny (US-3.2) and reopen (US-3.3)

---

### ❓ **QUESTION FOR USER:**

**Q4:** Do you want me to implement the auth dependencies as part of US-3.1, or create a separate user story for "Authentication Middleware" in Phase 3?

**My recommendation:** Include in US-3.1 (small, necessary for the feature).

---

## Question 5: Past Bookings & Error Message Strategy

### Part A: Should Approve Endpoint Reject Past Bookings?

**From BR-014:**
> **BR-014: Past Items Read-Only**
> No operations allowed when `EndDate < today`.
> **Restrictions:** No edits, No approvals/denials, No cancellations, No reopen

**Answer: YES**, approve endpoint must reject past bookings.

**Implementation:**
```python
# In approval logic
from app.utils import get_today  # Utility for Europe/Berlin timezone

if booking.end_date < get_today():
    raise ValueError(
        "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."
    )
```

**Error response:**
- **Status code:** 400 Bad Request
- **German message:** "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."
- **Frontend handling:** Show error banner, no action buttons

✅ **This is already specified** in [docs/specification/error-handling.md](docs/specification/error-handling.md:189)

---

### Part B: Error Message Strategy & Pattern

**Current Pattern (from Phase 2 implementation):**

```python
# In service (booking_service.py)
async def create_booking(self, data: BookingCreate) -> Booking:
    # Business logic validation
    if conflicts:
        raise ValueError(f"Dieser Zeitraum überschneidet sich... ({name} – {status}).")

    if end_date < start_date:
        raise ValueError("Ende darf nicht vor dem Start liegen.")

    return booking


# In router (bookings.py)
@router.post("/api/v1/bookings")
async def create_booking(...):
    try:
        booking = await service.create_booking(data)
        return booking
    except ValueError as e:
        # Map ValueError to appropriate HTTP status
        if "überschneidet" in str(e):
            status_code = status.HTTP_409_CONFLICT
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        raise HTTPException(status_code=status_code, detail=str(e))
```

**Analysis:**

✅ **Good:**
- German error messages in service layer (business logic)
- ValueError used for business rule violations
- HTTPException in router layer (HTTP concerns)
- Error messages from spec ([error-handling.md](docs/specification/error-handling.md))

❌ **Gaps:**
1. **String matching is fragile:** `if "überschneidet" in str(e)` breaks if message changes
2. **No structured error types:** Can't distinguish error types programmatically
3. **Frontend can't internationalize:** Message is German-only (fine for this project, but worth noting)

---

**Better Pattern (for US-3.1 and beyond):**

**Option A: Custom exception types**
```python
# app/core/exceptions.py

class BookingError(Exception):
    """Base class for booking business rule violations."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class ConflictError(BookingError):
    """Raised when booking conflicts with existing booking."""

    def __init__(self, conflicting_booking: Booking):
        status_map = {
            StatusEnum.PENDING: "Ausstehend",
            StatusEnum.CONFIRMED: "Bestätigt",
        }
        status_german = status_map.get(conflicting_booking.status, "Unbekannt")
        message = (
            f"Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung "
            f"({conflicting_booking.requester_first_name} – {status_german})."
        )
        super().__init__(message, status_code=409)


class PastBookingError(BookingError):
    """Raised when trying to modify past booking (BR-014)."""

    def __init__(self):
        message = "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."
        super().__init__(message, status_code=400)


class ForbiddenActionError(BookingError):
    """Raised when action not allowed for current booking state."""

    def __init__(self, action: str):
        message = "Diese Aktion ist für deine Rolle nicht verfügbar."
        super().__init__(message, status_code=403)


# In router
@router.post("/api/v1/bookings/{id}/approve")
async def approve_booking(...):
    try:
        return await service.approve_booking(...)
    except BookingError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        # Unexpected errors
        raise HTTPException(status_code=500, detail="Internal server error")
```

**Pros:**
- ✅ Type-safe error handling
- ✅ Status codes attached to error types
- ✅ German messages centralized
- ✅ Easy to test (catch specific exception types)
- ✅ No string matching

**Cons:**
- More files/classes to maintain
- Slight overkill for small project

---

**Option B: Keep current pattern, improve consistency**
```python
# Keep ValueError, but use error codes

# In service
if booking.end_date < get_today():
    raise ValueError("PAST_BOOKING: Dieser Eintrag liegt in der Vergangenheit...")

if booking.status in [StatusEnum.DENIED, StatusEnum.CANCELED]:
    raise ValueError("FORBIDDEN_STATE: Diese Aktion ist für deine Rolle nicht verfügbar.")

# In router
ERROR_STATUS_MAP = {
    "PAST_BOOKING": 400,
    "FORBIDDEN_STATE": 403,
    "CONFLICT": 409,
    "VALIDATION": 400,
}

try:
    return await service.method()
except ValueError as e:
    msg = str(e)
    # Extract error code prefix
    error_code = msg.split(":")[0] if ":" in msg else "VALIDATION"
    status_code = ERROR_STATUS_MAP.get(error_code, 400)

    # Remove error code from user-facing message
    detail = msg.split(":", 1)[1].strip() if ":" in msg else msg

    raise HTTPException(status_code=status_code, detail=detail)
```

**Pros:**
- ✅ Simple (no new classes)
- ✅ Error codes for programmatic handling
- ✅ German messages still in service

**Cons:**
- Error code prefix in message (could be cleaner)
- Still somewhat fragile

---

**Option C: Keep current pattern as-is (simplest)**

Just improve documentation and consistency.

```python
# Document the pattern clearly

# Service layer: Raise ValueError with German message from error-handling.md
# Router layer: Catch ValueError, map to appropriate HTTP status
# Frontend: Display error.detail directly to user
```

**Pros:**
- ✅ No changes needed
- ✅ Works fine for this project size
- ✅ German messages in service layer (correct layer)

**Cons:**
- String matching fragile
- Hard to extend later

---

### 🎯 **RECOMMENDATION: Option C (current pattern) with documentation**

**Rationale:**
1. **Current pattern works** and is already implemented in Phase 2
2. **Consistency matters more** than perfect architecture for this project size
3. **German messages are specified** in [error-handling.md](docs/specification/error-handling.md)
4. **Easy to improve later** if needed (refactor to Option A in Phase 8 polish)

**Action items for US-3.1:**
1. Follow existing pattern (ValueError with German message)
2. Document error messages in code comments with BR references
3. Create test cases for each error scenario
4. Ensure all messages match [error-handling.md](docs/specification/error-handling.md)

**Example for approve endpoint:**
```python
async def approve_booking(self, booking_id: UUID, approver_party: AffiliationEnum) -> ApprovalResponse:
    """Approve a booking."""

    # BR-014: Reject past bookings
    if booking.end_date < get_today():
        raise ValueError(
            "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."
        )

    # BR-004: Cannot approve Denied bookings
    if booking.status in [StatusEnum.DENIED, StatusEnum.CANCELED]:
        raise ValueError("Diese Aktion ist für deine Rolle nicht verfügbar.")

    # ... rest of logic ...
```

---

### ✅ **ERROR HANDLING STRATEGY: Fully Specified**

**What exists:**
- ✅ All German error messages documented in [error-handling.md](docs/specification/error-handling.md)
- ✅ Validation errors specified (conflicts, past dates, invalid input)
- ✅ API errors specified (401, 403, 404)
- ✅ Concurrent action errors specified (BR-024 "Schon erledigt")
- ✅ Consistent pattern established in Phase 2

**What's needed for US-3.1:**
- Use existing messages from spec
- Follow existing ValueError → HTTPException pattern
- Test all error scenarios

**No gaps found** - error handling is comprehensive.

---

### ❓ **QUESTIONS FOR USER:**

**Q5a:** Are you happy with the current error handling pattern (ValueError with German messages), or do you want custom exception types (Option A)?

**My recommendation:** Keep current pattern (Option C) - it works well.

**Q5b:** Should we add error codes (e.g., `PAST_BOOKING`, `FORBIDDEN_STATE`) for better frontend handling, or are German-only messages sufficient?

**My recommendation:** German messages sufficient (frontend can match on text for now, improve in Phase 8 if needed).

---

## Summary of Recommendations

| Question | Recommendation | Confidence |
|----------|---------------|------------|
| **Q1: SELECT FOR UPDATE** | Lock Booking row only (Option A) | High ✅ |
| **Q2a: Timeline Events** | Log both "Approved" + "Confirmed" (two events if final) | Medium 🟡 |
| **Q2b: Confirmed Actor** | Actor = Approver (human action) | Medium 🟡 |
| **Q3: Email Notifications** | Stub method in service (Option D) | High ✅ |
| **Q4: Auth Middleware** | Implement as part of US-3.1 | High ✅ |
| **Q5: Error Handling** | Keep current pattern (ValueError → HTTPException) | High ✅ |

---

## Next Steps (After User Review)

1. **User reviews this document** and answers questions
2. **Confirmed decisions** documented in US-3.1 acceptance criteria
3. **Implementation begins** with:
   - Auth dependencies (`app/core/auth.py`)
   - Approval service method with BR-024 locking
   - Timeline events (Approved + Confirmed)
   - Email notification stub
   - Tests for all scenarios (14 estimated)

**Estimated implementation time:** 1-2 days after decisions confirmed

---

## Open Questions (Need User Input)

1. **Q1:** Lock Booking only (A) or Booking + Approval (B)? → **Recommend A**
2. **Q2a:** Two timeline events (Approved + Confirmed) or one? → **Recommend two**
3. **Q2b:** Confirmed event Actor = Approver or System? → **Recommend Approver**
4. **Q3a:** Email stub (D) or event-driven (C)? → **Recommend D**
5. **Q3b:** Explicitly document email deferral in Phase 3 AC?
6. **Q3c:** Create Phase 4 tracking checklist for stub implementation?
7. **Q4:** Auth dependencies in US-3.1 or separate story? → **Recommend US-3.1**
8. **Q5a:** Keep current error pattern (C) or custom exceptions (A)? → **Recommend C**
9. **Q5b:** Add error codes or German messages sufficient? → **Recommend messages only**

---

**Status:** ✅ **CONFIRMED - All decisions approved**

**Date Confirmed:** 2025-11-19

**Next:** Implementation begins with confirmed decisions documented in:
- [ADR-019: Authentication & Authorization](docs/architecture/adr-019-authentication-authorization.md)
- [Phase 3: Approval Flow](docs/implementation/phase-3-approval-flow.md) (updated with decisions)

---

## 📋 CONFIRMED DECISIONS (2025-11-19)

All recommendations approved by user:

| Question | Decision | Status |
|----------|----------|--------|
| **Q1: BR-024 Locking** | Lock Booking row only (Option A) | ✅ Approved |
| **Q2a: Timeline Events** | Log both "Approved" + "Confirmed" (two events) | ✅ Approved |
| **Q2b: Confirmed Actor** | Actor = Approver (human action) | ✅ Approved |
| **Q3a: Email Pattern** | Stub method in service (Option D) | ✅ Approved |
| **Q3b: Document deferral** | Captured in Phase 3 tasks | ✅ Approved |
| **Q3c: Phase 4 tracking** | Stub method has TODO comment | ✅ Approved |
| **Q4: Auth Middleware** | Implement as part of US-3.1 | ✅ Approved |
| **Q5a: Error Pattern** | Keep current pattern (ValueError → HTTPException) | ✅ Approved |
| **Q5b: Error codes** | German messages sufficient | ✅ Approved |

**Documentation Updates Completed:**
- ✅ Created [ADR-019](docs/architecture/adr-019-authentication-authorization.md) (authentication pattern)
- ✅ Updated [docs/architecture/README.md](docs/architecture/README.md) (ADR list)
- ✅ Updated [docs/architecture/CLAUDE.md](docs/architecture/CLAUDE.md) (auth quick reference)
- ✅ Updated [docs/implementation/phase-3-approval-flow.md](docs/implementation/phase-3-approval-flow.md) (decisions captured)
- ✅ Updated [docs/implementation/CLAUDE.md](docs/implementation/CLAUDE.md) (auth pattern guidance)

**Ready for Implementation:** Yes - all decisions documented, ADR created, patterns established
