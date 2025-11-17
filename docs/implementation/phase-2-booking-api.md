# Phase 2: Booking API

## Goal

Implement booking CRUD endpoints with validation and conflict detection.

**Duration:** 3-4 days | **Dependencies:** Phase 1

---

## User Stories

### US-2.1: Create Booking Endpoint

```gherkin
Feature: Create Booking

  Scenario: Successfully create booking
    Given I am a requester
    When I POST to /api/v1/bookings with:
      """json
      {
        "requester_first_name": "Anna",
        "requester_email": "anna@example.com",
        "start_date": "2025-08-01",
        "end_date": "2025-08-05",
        "party_size": 4,
        "affiliation": "Ingeborg"
      }
      """
    Then I should receive status 201
    And the response should include:
      | field       | value      |
      | status      | Pending    |
      | total_days  | 5          |
      | id          | <uuid>     |

  Scenario: Reject booking with conflict (BR-002)
    Given a booking exists from 2025-08-01 to 2025-08-05
    When I create a booking from 2025-08-03 to 2025-08-08
    Then I should receive status 409
    And the error should mention "überschneidet sich"

  Scenario: Reject invalid party size (BR-016)
    When I create a booking with party_size = 11
    Then I should receive status 400
    And the error should mention "zwischen 1 und 10"

  Scenario: Reject future horizon exceeded
    When I create a booking 19 months in future
    Then I should receive status 400
    And the error should mention "maximal 18 Monate"
```

**Tests:**
```python
@pytest.mark.asyncio
async def test_create_booking_success(client):
    response = await client.post("/api/v1/bookings", json={...})
    assert response.status_code == 201

@pytest.mark.asyncio
async def test_create_booking_conflict(client, existing_booking):
    response = await client.post("/api/v1/bookings", json={...})
    assert response.status_code == 409
    assert "überschneidet sich" in response.json()["detail"]
```

**Tasks:**
- [ ] Create Pydantic schemas (`BookingCreate`, `BookingResponse`)
- [ ] Implement `POST /api/v1/bookings` endpoint
- [ ] Validate all fields (Pydantic + custom validators)
- [ ] Check conflicts using repository
- [ ] Create 3 approval records (NoResponse)
- [ ] Generate tokens for requester + approvers
- [ ] Return booking with requester link

---

### US-2.2: Get Booking Endpoint

```gherkin
Feature: Get Booking

  Scenario: Public view (no token)
    Given a Pending booking exists
    When I GET /api/v1/bookings/{id} without token
    Then I should see limited fields:
      | field               |
      | requester_first_name|
      | start_date          |
      | end_date            |
      | party_size          |
      | status              |
    And I should NOT see:
      | field               |
      | requester_email     |
      | description         |
      | approvals           |

  Scenario: Requester view (with token)
    Given I am the requester
    When I GET /api/v1/bookings/{id}?token=xxx
    Then I should see all fields including:
      | field       |
      | approvals   |
      | timeline    |
      | description |

  Scenario: Denied booking hidden from public
    Given a Denied booking exists
    When I GET /api/v1/bookings/{id} without token
    Then I should receive status 404
```

**Tests:**
```python
async def test_get_booking_public_view(client, pending_booking):
    response = await client.get(f"/api/v1/bookings/{pending_booking.id}")
    data = response.json()
    assert "requester_first_name" in data
    assert "requester_email" not in data

async def test_get_booking_requester_view(client, booking_with_token):
    response = await client.get(f"/api/v1/bookings/{booking_with_token.id}?token={booking_with_token.token}")
    data = response.json()
    assert "approvals" in data
    assert "timeline" in data
```

---

### US-2.3: Update Booking Endpoint

```gherkin
Feature: Update Booking

  Scenario: Edit dates (approvals reset per BR-005)
    Given I am the requester of a Pending booking
    And two approvers have already approved
    When I PATCH /api/v1/bookings/{id}?token=xxx with new dates
    Then all approvals should reset to NoResponse
    And approvers should be notified

  Scenario: Edit non-date fields (approvals preserved)
    Given I am the requester
    When I PATCH with:
      """json
      {"party_size": 5, "description": "Updated"}
      """
    Then approvals should remain unchanged
```

---

### US-2.4: Cancel Booking Endpoint

```gherkin
Feature: Cancel Booking

  Scenario: Cancel Pending booking (no comment required)
    Given I am the requester of a Pending booking
    When I DELETE /api/v1/bookings/{id}?token=xxx
    Then status should change to Canceled
    And approvers should be notified

  Scenario: Cancel Confirmed booking (comment required per BR-026)
    Given I am the requester of a Confirmed booking
    When I DELETE without a comment
    Then I should receive status 400
    When I DELETE with:
      """json
      {"comment": "Kann leider nicht kommen"}
      """
    Then status should change to Canceled
```

---

## Definition of Done

- [ ] All endpoints implemented and documented (OpenAPI)
- [ ] Pydantic schemas validate all inputs
- [ ] Conflict detection works (BR-002, BR-029)
- [ ] Authorization checks work (token validation)
- [ ] Integration tests pass (≥80% coverage)
- [ ] OpenAPI docs accessible at /docs

**Next:** [Phase 3: Approval Flow](phase-3-approval-flow.md)
