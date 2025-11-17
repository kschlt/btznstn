# API Specification

## Overview

This document specifies all REST API endpoints for the Betzenstein booking & approval application backend.

**Base URL (Production):** `https://api.betzenstein.app`
**API Version:** `/api/v1`
**Format:** JSON (application/json)
**Authentication:** Token-based (query parameter `?token=xxx`)

---

## Authentication

### Token-Based Authentication

**No traditional login** - Access control via signed tokens in URLs.

**Token Structure:**
```json
{
  "email": "user@example.com",
  "role": "requester" | "approver",
  "booking_id": "uuid" (optional, for specific booking access),
  "party": "Ingeborg" | "Cornelia" | "Angelika" (for approver role),
  "iat": 1234567890
}
```

**Signing:** HMAC-SHA256 with `SECRET_KEY`
**Expiry:** None (per BR-010)

**Token Validation:**
- Middleware validates signature
- Extracts email + role + booking_id/party
- Per-endpoint authorization checks

**Example Token Usage:**
```
GET /api/v1/bookings/abc-123?token=eyJ0eXAiOiJKV1QiLCJh...
```

---

## Endpoints

### Public Endpoints

No authentication required.

#### `GET /health`

**Purpose:** Health check for load balancer / monitoring.

**Response:**
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200` - Healthy

---

#### `GET /api/v1/calendar`

**Purpose:** Retrieve calendar view of bookings (public, limited data).

**Query Parameters:**
- `month` (optional, integer 1-12) - Default: current month
- `year` (optional, integer) - Default: current year
- `view` (optional, string: "month" | "year") - Default: "month"

**Response:**
```json
{
  "view": "month",
  "month": 8,
  "year": 2025,
  "bookings": [
    {
      "id": "uuid",
      "start_date": "2025-08-01",
      "end_date": "2025-08-05",
      "total_days": 5,
      "requester_first_name": "Anna",
      "party_size": 4,
      "affiliation": "Ingeborg",
      "status": "Pending" | "Confirmed"
    }
  ]
}
```

**Notes:**
- Excludes `Denied` and `Canceled` bookings (not public per BR-008)
- Emails never exposed (privacy by design)

**Status Codes:**
- `200` - Success

---

#### `POST /api/v1/bookings`

**Purpose:** Create a new booking request.

**Request Body:**
```json
{
  "requester_first_name": "Anna",
  "requester_email": "anna@example.com",
  "start_date": "2025-08-01",
  "end_date": "2025-08-05",
  "party_size": 4,
  "affiliation": "Ingeborg",
  "description": "Optional description (max 500 chars)"
}
```

**Validation (Pydantic):**
- `requester_first_name`: 1-40 chars, letters/diacritics/space/hyphen/apostrophe (BR-019)
- `requester_email`: Valid email format
- `start_date`: ≤ `today + FUTURE_HORIZON_MONTHS` (default 18)
- `end_date`: ≥ `start_date`
- `party_size`: 1-10 (BR-016)
- `affiliation`: "Ingeborg" | "Cornelia" | "Angelika"
- `description`: ≤500 chars, no links (BR-020)

**Business Logic:**
- Check conflicts (BR-002, BR-029)
- Create booking with status = Pending
- Create 3 approval records (NoResponse)
- Send notification emails (BR-003)

**Response (Success):**
```json
{
  "id": "uuid",
  "requester_first_name": "Anna",
  "start_date": "2025-08-01",
  "end_date": "2025-08-05",
  "total_days": 5,
  "party_size": 4,
  "affiliation": "Ingeborg",
  "status": "Pending",
  "created_at": "2025-01-17T12:00:00Z",
  "requester_link": "https://betzenstein.app/bookings/uuid?token=xxx"
}
```

**Error Responses:**

**Conflict:**
```json
{
  "detail": "Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung (Max – Ausstehend).",
  "error_code": "BOOKING_CONFLICT",
  "correlation_id": "uuid"
}
```

**Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "party_size"],
      "msg": "Teilnehmerzahl muss zwischen 1 und 10 liegen.",
      "type": "value_error"
    }
  ]
}
```

**Status Codes:**
- `201` - Created
- `400` - Validation error
- `409` - Conflict
- `429` - Rate limit exceeded (10 per day per email, BR-012)

---

### Authenticated Endpoints

Require `?token=xxx` query parameter.

#### `GET /api/v1/bookings/{id}`

**Purpose:** Get booking details (permissions vary by role).

**Authorization:**
- **Viewer (no token):** Public fields only (first name, dates, status if Pending/Confirmed)
- **Requester (token):** All fields + timeline + comments + actions
- **Approver (token):** All fields + timeline + comments + actions

**Response (Requester/Approver):**
```json
{
  "id": "uuid",
  "requester_first_name": "Anna",
  "start_date": "2025-08-01",
  "end_date": "2025-08-05",
  "total_days": 5,
  "party_size": 4,
  "affiliation": "Ingeborg",
  "description": "Optional description",
  "status": "Pending",
  "created_at": "2025-01-17T12:00:00Z",
  "last_activity_at": "2025-01-17T13:00:00Z",
  "approvals": [
    {
      "party": "Ingeborg",
      "decision": "NoResponse" | "Approved" | "Denied",
      "comment": "Optional comment (only if Denied)",
      "decided_at": "2025-01-17T14:00:00Z"
    }
  ],
  "timeline": [
    {
      "when": "2025-01-17T12:00:00Z",
      "actor": "Requester",
      "event_type": "Submitted",
      "note": null
    },
    {
      "when": "2025-01-17T14:00:00Z",
      "actor": "Ingeborg",
      "event_type": "Approved",
      "note": null
    }
  ],
  "available_actions": ["edit", "cancel"]  // Depends on role + status
}
```

**Status Codes:**
- `200` - Success
- `403` - Unauthorized (invalid token or wrong role)
- `404` - Booking not found

---

#### `PATCH /api/v1/bookings/{id}`

**Purpose:** Edit a booking (Requester only, while Pending).

**Authorization:** Requester token for this booking

**Request Body (Partial):**
```json
{
  "start_date": "2025-08-03",  // Optional
  "end_date": "2025-08-08",    // Optional
  "party_size": 5,             // Optional
  "affiliation": "Cornelia",   // Optional
  "description": "Updated",    // Optional
  "requester_first_name": "Anna-Maria"  // Optional
}
```

**Business Logic (BR-005):**
- **Date change:** Reset approvals if dates change (BR-005)
- **Non-date change:** Approvals remain
- **Conflict check:** Re-check for conflicts if dates change
- **Notifications:** Email approvers if dates change

**Response:** Updated booking object (same as GET)

**Status Codes:**
- `200` - Success
- `400` - Validation error
- `403` - Unauthorized (not requester, or status != Pending)
- `409` - Conflict (if dates changed)

---

#### `DELETE /api/v1/bookings/{id}`

**Purpose:** Cancel a booking (Requester only).

**Authorization:** Requester token for this booking

**Request Body (if Confirmed):**
```json
{
  "comment": "Required if status = Confirmed (BR-026)"
}
```

**Business Logic:**
- Status → Canceled
- If Pending or Denied: No comment required
- If Confirmed: Comment required (BR-026)
- Send notification emails (BR-007)
- Move to Archive (logically, not physically deleted)

**Response:**
```json
{
  "message": "Anfrage storniert.",
  "notified": ["Ingeborg", "Cornelia", "Angelika"]
}
```

**Status Codes:**
- `200` - Success
- `400` - Comment required (if Confirmed)
- `403` - Unauthorized
- `410` - Already canceled

---

#### `POST /api/v1/bookings/{id}/approve`

**Purpose:** Approve a booking (Approver only).

**Authorization:** Approver token for this booking (party matches)

**Request Body:** None (idempotent one-click)

**Business Logic:**
- Update approval record: decision → Approved, decided_at → now
- Check if final approval (all 3 Approved):
  - If yes: Status → Confirmed, send confirmation emails (BR-004)
  - If no: Send approval notification to requester (BR-003)
- Idempotent: If already Approved, no-op

**Response:**
```json
{
  "message": "Danke – du hast zugestimmt.",
  "booking_status": "Confirmed" | "Pending",
  "pending_approvals": ["Cornelia", "Angelika"] | []
}
```

**Status Codes:**
- `200` - Success (idempotent)
- `403` - Unauthorized (not approver for this party, or booking status = Denied/Canceled)
- `409` - Conflict (if another approver denied first, BR-024)

---

#### `POST /api/v1/bookings/{id}/deny`

**Purpose:** Deny a booking (Approver only).

**Authorization:** Approver token for this booking (party matches)

**Request Body:**
```json
{
  "comment": "Required, plaintext, ≤500 chars (BR-004)"
}
```

**Business Logic:**
- Update approval record: decision → Denied, comment, decided_at → now
- Status → Denied (immediately, per BR-004)
- Send denial notification to requester + other approvers (BR-006)
- If booking was Confirmed: Show warning dialog (UI), require comment (same as above)

**Response:**
```json
{
  "message": "Erledigt – du hast abgelehnt.",
  "booking_status": "Denied"
}
```

**Status Codes:**
- `200` - Success
- `400` - Comment missing or invalid
- `403` - Unauthorized

---

#### `POST /api/v1/bookings/{id}/reopen`

**Purpose:** Reopen a denied booking (Requester only).

**Authorization:** Requester token for this booking

**Request Body:** Same as PATCH (can edit all fields)

**Business Logic:**
- Status → Pending
- Reset all approvals to NoResponse
- Send notification emails (BR-003, same as new booking)

**Response:** Updated booking object

**Status Codes:**
- `200` - Success
- `400` - Validation error
- `403` - Unauthorized (not requester, or status != Denied)
- `409` - Conflict (if new dates conflict)

---

#### `GET /api/v1/approver/outstanding`

**Purpose:** Get approver's outstanding requests (NoResponse only).

**Authorization:** Approver token

**Query Parameters:**
- `limit` (optional, integer, default 20) - Pagination
- `offset` (optional, integer, default 0) - Pagination

**Response:**
```json
{
  "bookings": [
    {
      "id": "uuid",
      "requester_first_name": "Anna",
      "start_date": "2025-08-01",
      "end_date": "2025-08-05",
      "party_size": 4,
      "affiliation": "Ingeborg",
      "status": "Pending",
      "last_activity_at": "2025-01-17T12:00:00Z",
      "days_until_start": 195
    }
  ],
  "total": 3,
  "limit": 20,
  "offset": 0
}
```

**Sorting:** By `last_activity_at DESC` (most recent first)

**Status Codes:**
- `200` - Success
- `403` - Unauthorized

---

#### `GET /api/v1/approver/history`

**Purpose:** Get approver's history (all statuses except Canceled).

**Authorization:** Approver token

**Query Parameters:**
- `limit` (optional, integer, default 20)
- `offset` (optional, integer, default 0)

**Response:** Same structure as `/approver/outstanding`, but includes all statuses (Pending, Confirmed, Denied)

**Status Codes:**
- `200` - Success
- `403` - Unauthorized

---

#### `POST /api/v1/recovery/request-link`

**Purpose:** Request lost link (email recovery).

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Business Logic:**
- Check cooldown (60s per email/IP, BR-021)
- Check rate limit (5 per hour per email)
- If email exists: Resend existing token (don't generate new)
- If email doesn't exist: Still show success (no enumeration)

**Response (Always Success):**
```json
{
  "message": "Wir haben dir – falls vorhanden – deinen persönlichen Zugangslink erneut gemailt. Kommt nichts an? Prüfe die Schreibweise oder deinen Spam-Ordner."
}
```

**Status Codes:**
- `200` - Success (always, even if email not found)
- `429` - Rate limit / cooldown

---

### Admin Endpoints (Future)

Not implemented in MVP. Potential endpoints:

- `GET /api/v1/admin/bookings` - List all bookings
- `DELETE /api/v1/admin/bookings/{id}` - Hard delete
- `POST /api/v1/admin/holidays` - Add holidays
- `GET /api/v1/admin/metrics` - Usage stats

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Human-readable error message (German)",
  "error_code": "MACHINE_READABLE_CODE",
  "correlation_id": "uuid-for-tracking"
}
```

### Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| `BOOKING_CONFLICT` | 409 | Date range overlaps with existing booking |
| `VALIDATION_ERROR` | 400 | Input validation failed |
| `UNAUTHORIZED` | 403 | Invalid or missing token |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `PAST_DATED` | 400 | Cannot modify past-dated booking |
| `INVALID_STATUS_TRANSITION` | 400 | Action not allowed in current status |
| `COMMENT_REQUIRED` | 400 | Comment field required but missing |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## Rate Limiting

Implemented via FastAPI middleware.

### Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `POST /api/v1/bookings` | 10 per email | 24 hours |
| `POST /api/v1/recovery/request-link` | 5 per email | 1 hour |
| All endpoints | 30 per IP | 1 hour |

### Headers

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1234567890
```

### Error Response

```json
{
  "detail": "Bitte warte kurz – wir haben dir deinen persönlichen Link gerade erst gesendet.",
  "error_code": "RATE_LIMIT_EXCEEDED",
  "retry_after": 45
}
```

---

## CORS

### Configuration

**Allowed Origins:**
- `https://betzenstein.app` (production)
- `https://*.vercel.app` (preview deployments)
- `http://localhost:3000` (local development)

**Allowed Methods:** GET, POST, PATCH, DELETE, OPTIONS

**Allowed Headers:** Content-Type, Authorization

**Credentials:** Allowed (cookies, if needed)

---

## OpenAPI Documentation

FastAPI auto-generates OpenAPI spec.

**Access:**
- Swagger UI: `https://api.betzenstein.app/docs`
- ReDoc: `https://api.betzenstein.app/redoc`
- OpenAPI JSON: `https://api.betzenstein.app/openapi.json`

**Usage:**
- Web can generate type-safe client from `/openapi.json`
- AI can reference `/docs` for implementation

---

## Webhooks (Future)

Not implemented in MVP. Potential webhooks:

- Booking created
- Booking confirmed
- Booking denied
- Booking canceled

---

## Versioning

**Strategy:** URL versioning (`/api/v1/`, `/api/v2/`)

**Breaking Changes:**
- New major version (e.g., `/api/v2/`)
- Old version supported for deprecation period (e.g., 6 months)

**Non-Breaking Changes:**
- Add new fields to responses (clients ignore unknown fields)
- Add new endpoints
- Add new query parameters (optional)

---

## Performance Considerations

### Caching

**Not implemented initially** (small user base).

**Future:**
- Redis cache for calendar view
- TTL: 60 seconds (BR: ISR on frontend)

### Database Optimization

**Indexes:**
- `bookings.status`
- `bookings.start_date`, `bookings.end_date`
- `bookings.requester_email`
- `bookings.last_activity_at`
- GiST index on `daterange(start_date, end_date)`

### Pagination

**Default limit:** 20 items
**Max limit:** 100 items

---

## Testing

### Contract Testing

**Pydantic schemas enforce contracts:**
- Request validation automatic
- Response validation automatic

### Integration Testing

**Example:**
```python
@pytest.mark.asyncio
async def test_create_booking_api(client: AsyncClient):
    response = await client.post("/api/v1/bookings", json={
        "requester_first_name": "Anna",
        "requester_email": "anna@example.com",
        "start_date": "2025-08-01",
        "end_date": "2025-08-05",
        "party_size": 4,
        "affiliation": "Ingeborg",
    })

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "Pending"
    assert data["total_days"] == 5
```

---

## Implementation Checklist

API implementation order:

- [ ] FastAPI app setup
- [ ] Database models (SQLAlchemy)
- [ ] Pydantic schemas (request/response)
- [ ] Token signing/validation middleware
- [ ] CORS middleware
- [ ] Rate limiting middleware
- [ ] Booking endpoints (CRUD)
- [ ] Approval endpoints (approve/deny)
- [ ] Approver overview endpoints
- [ ] Recovery endpoint
- [ ] Email integration (Resend)
- [ ] Error handling + logging
- [ ] OpenAPI customization
- [ ] Tests (unit + integration)

---

## Related Documentation

- [Data Model](../specification/data-model.md) - Database schema, entities
- [Business Rules](../foundation/business-rules.md) - BR-001 to BR-029
- [Error Handling](../specification/error-handling.md) - Error messages
- [Authentication Flow](authentication-flow.md) - Token generation/validation
- [ADR-001: API Framework](../architecture/adr-001-backend-framework.md) - FastAPI
- [ADR-003: Database & ORM](../architecture/adr-003-database-orm.md) - PostgreSQL + SQLAlchemy

---

## Summary

This API is designed for:

- ✅ **AI implementation** - Standard REST patterns, clear Pydantic schemas
- ✅ **Type safety** - Auto-generated OpenAPI → TypeScript types for frontend
- ✅ **Security** - Token-based auth, rate limiting, CORS
- ✅ **Privacy** - Emails never exposed, role-based access
- ✅ **Mobile-first** - JSON responses, optimized payloads
- ✅ **Testability** - Pydantic validation, contract testing

**Next:** Implement FastAPI routes + Pydantic schemas following this spec.
