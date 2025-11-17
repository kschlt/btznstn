# Authentication Flow

## Overview

Token-based authentication using signed URLs. No traditional login - role determined by token embedded in URL.

**Method:** HMAC-SHA256 signed tokens
**Expiry:** None (per BR-010)
**Transport:** Query parameter `?token=xxx`

---

## Token Structure

### Payload

```python
{
  "email": "user@example.com",
  "role": "requester" | "approver",
  "booking_id": "uuid" (optional, for requester accessing specific booking),
  "party": "Ingeborg" | "Cornelia" | "Angelika" (for approver role),
  "iat": 1234567890  # Issued at timestamp
}
```

### Signing

**Algorithm:** HMAC-SHA256
**Secret:** `SECRET_KEY` environment variable (32+ random chars)

**Python Implementation:**
```python
import hmac
import hashlib
import json
import base64
from datetime import datetime

def generate_token(payload: dict, secret_key: str) -> str:
    """Generate signed token from payload."""
    # Add timestamp
    payload["iat"] = int(datetime.utcnow().timestamp())

    # JSON encode
    message = json.dumps(payload, sort_keys=True)

    # Sign with HMAC-SHA256
    signature = hmac.new(
        secret_key.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()

    # Base64 encode
    token = base64.urlsafe_b64encode(
        message.encode() + b"." + signature
    ).decode()

    return token

def verify_token(token: str, secret_key: str) -> dict | None:
    """Verify token signature and extract payload."""
    try:
        # Base64 decode
        decoded = base64.urlsafe_b64decode(token.encode())

        # Split message and signature
        parts = decoded.split(b".", 1)
        if len(parts) != 2:
            return None

        message, signature = parts

        # Verify signature
        expected_signature = hmac.new(
            secret_key.encode(),
            message,
            hashlib.sha256
        ).digest()

        if not hmac.compare_digest(signature, expected_signature):
            return None  # Invalid signature

        # Parse payload
        payload = json.loads(message.decode())
        return payload

    except Exception:
        return None
```

---

## Token Generation

### On Booking Creation

**Requester Token:**
```python
def create_booking_tokens(booking: Booking) -> dict[str, str]:
    """Generate tokens for new booking."""

    # Requester token
    requester_token = generate_token({
        "email": booking.requester_email,
        "role": "requester",
        "booking_id": str(booking.id),
    }, SECRET_KEY)

    # Approver tokens (one per party)
    approver_tokens = {}
    for party in ["Ingeborg", "Cornelia", "Angelika"]:
        party_email = get_approver_email(party)
        approver_tokens[party] = generate_token({
            "email": party_email,
            "role": "approver",
            "booking_id": str(booking.id),
            "party": party,
        }, SECRET_KEY)

    return {
        "requester": requester_token,
        "approvers": approver_tokens,
    }
```

### For Approver Overview

**Approver Token (no specific booking):**
```python
def create_approver_overview_token(party: str) -> str:
    """Generate token for approver overview page."""
    party_email = get_approver_email(party)

    return generate_token({
        "email": party_email,
        "role": "approver",
        "party": party,
        # No booking_id - can access all bookings for this party
    }, SECRET_KEY)
```

---

## Token Validation

### FastAPI Middleware

```python
from fastapi import Request, HTTPException
from typing import Optional

async def verify_request_token(request: Request) -> Optional[dict]:
    """Extract and verify token from request."""
    # Get token from query parameter
    token = request.query_params.get("token")

    if not token:
        return None  # No token (public access)

    # Verify token
    payload = verify_token(token, SECRET_KEY)

    if not payload:
        raise HTTPException(status_code=403, detail="Ungültiger Token")

    return payload

# Dependency for protected routes
async def require_token(request: Request) -> dict:
    """Require valid token."""
    payload = await verify_request_token(request)

    if not payload:
        raise HTTPException(status_code=403, detail="Authentifizierung erforderlich")

    return payload
```

### Route Protection

```python
from fastapi import Depends

@app.get("/api/v1/bookings/{booking_id}")
async def get_booking(
    booking_id: UUID,
    token_payload: dict = Depends(verify_request_token),  # Optional token
):
    """Get booking details (permissions vary by token)."""
    booking = await booking_repo.get(booking_id)

    if not booking:
        raise HTTPException(404, "Buchung nicht gefunden")

    # Apply role-based filtering
    if not token_payload:
        # Public view: limited fields, only Pending/Confirmed
        if booking.status not in ["Pending", "Confirmed"]:
            raise HTTPException(404, "Buchung nicht gefunden")
        return booking_to_public_view(booking)

    # Requester access
    if token_payload["role"] == "requester":
        if token_payload["email"] != booking.requester_email:
            raise HTTPException(403, "Nicht autorisiert")
        return booking_to_requester_view(booking)

    # Approver access
    if token_payload["role"] == "approver":
        # Check if approver is assigned to this booking
        if not is_approver_for_booking(token_payload["party"], booking):
            raise HTTPException(403, "Nicht autorisiert")
        return booking_to_approver_view(booking)
```

---

## URL Construction

### Requester Link

```python
def build_requester_url(booking_id: UUID, token: str) -> str:
    """Build requester access URL."""
    base_url = "https://betzenstein.app"
    return f"{base_url}/bookings/{booking_id}?token={token}"
```

**Example:**
```
https://betzenstein.app/bookings/abc-123-def-456?token=eyJlbWFpbCI6ImFubmFA...
```

### Approver Action Link

```python
def build_approve_url(booking_id: UUID, token: str) -> str:
    """Build one-click approve URL."""
    base_url = "https://api.betzenstein.app"
    return f"{base_url}/api/v1/bookings/{booking_id}/approve?token={token}"
```

**Example:**
```
https://api.betzenstein.app/api/v1/bookings/abc-123/approve?token=eyJlbWFpbCI6ImluZ2Vib3Jn...
```

### Approver Overview Link

```python
def build_approver_overview_url(party: str, token: str) -> str:
    """Build approver overview page URL."""
    base_url = "https://betzenstein.app"
    return f"{base_url}/approver?token={token}"
```

---

## Link Recovery Flow

### Request Recovery

**Endpoint:** `POST /api/v1/recovery/request-link`

```python
@app.post("/api/v1/recovery/request-link")
async def request_link_recovery(email: str):
    """Send recovery email (neutral response for security)."""

    # Check rate limit (5 per hour per email, 60s cooldown)
    if is_rate_limited(email):
        raise HTTPException(429, "Bitte warte kurz...")

    # Find user by email
    user = await find_user_by_email(email)

    if user:
        # Resend existing token (don't generate new)
        if user.role == "requester":
            token = user.requester_token
            url = build_requester_url(user.booking_id, token)
        else:  # approver
            token = user.approver_token
            url = build_approver_overview_url(user.party, token)

        await send_recovery_email(email, url)

    # Always return success (no enumeration)
    return {
        "message": "Wir haben dir – falls vorhanden – deinen persönlichen Zugangslink erneut gemailt."
    }
```

---

## Security Considerations

### Token Security

✅ **Strong signature** - HMAC-SHA256 prevents tampering
✅ **No expiry** - Per BR-010, links don't expire
✅ **Opaque** - Base64-encoded, not human-readable
✅ **Constant-time comparison** - Prevents timing attacks (`hmac.compare_digest`)

### Rate Limiting

```python
# Per-email limits
RATE_LIMITS = {
    "booking_create": (10, "24h"),  # 10 per day per email
    "recovery_request": (5, "1h"),   # 5 per hour per email
    "recovery_cooldown": (1, "60s"), # 1 per 60 seconds
}
```

### HTTPS Only

- All tokens transmitted over HTTPS
- `force_https: true` in Fly.io config
- Vercel automatic HTTPS

---

## Testing

### Unit Tests

```python
def test_token_generation():
    payload = {
        "email": "test@example.com",
        "role": "requester",
        "booking_id": "abc-123",
    }

    token = generate_token(payload, "test-secret")
    assert token is not None
    assert len(token) > 0

def test_token_verification():
    payload = {"email": "test@example.com", "role": "requester"}
    token = generate_token(payload, "test-secret")

    verified = verify_token(token, "test-secret")
    assert verified["email"] == "test@example.com"
    assert verified["role"] == "requester"

def test_token_tamper_detection():
    payload = {"email": "test@example.com"}
    token = generate_token(payload, "test-secret")

    # Tamper with token
    tampered = token[:-5] + "xxxxx"

    verified = verify_token(tampered, "test-secret")
    assert verified is None  # Signature invalid

def test_wrong_secret():
    payload = {"email": "test@example.com"}
    token = generate_token(payload, "secret-1")

    verified = verify_token(token, "secret-2")
    assert verified is None  # Wrong secret
```

---

## Related Documentation

- [API Specification](api-specification.md) - Token usage in endpoints
- [Business Rules](../foundation/business-rules.md) - BR-010 (no expiry)
- [Notifications](../specification/notifications.md) - Email templates with tokens
