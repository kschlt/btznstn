# Phase 3: Approval Flow

## Goal

Implement approve, deny, and state transition logic.

**Duration:** 2-3 days | **Dependencies:** Phase 2

---

## Key User Stories

### US-3.1: Approve Booking

```gherkin
Feature: Approve Booking

  Scenario: Single approval (not final)
    Given a Pending booking with 3 NoResponse approvals
    When Ingeborg approves via POST /api/v1/bookings/{id}/approve?token=xxx
    Then Ingeborg's decision should be Approved
    And booking status should remain Pending
    And requester should be notified

  Scenario: Final approval (BR-004)
    Given Ingeborg and Cornelia have approved
    When Angelika approves
    Then booking status should change to Confirmed
    And all parties should be notified

  Scenario: Idempotent approval
    Given Ingeborg has already approved
    When Ingeborg approves again
    Then no error should occur
    And decision should remain Approved
```

### US-3.2: Deny Booking

```gherkin
Feature: Deny Booking

  Scenario: Deny with comment (BR-004)
    Given a Pending booking
    When I POST /api/v1/bookings/{id}/deny?token=xxx with:
      """json
      {"comment": "Termine passen nicht"}
      """
    Then booking status should change to Denied
    And requester should be notified
    And comment should be visible to requester

  Scenario: Post-confirm deny (warning required)
    Given a Confirmed booking
    When I deny with comment
    Then status should change to Denied
    And all parties should be notified
```

### US-3.3: Reopen Denied Booking

```gherkin
Feature: Reopen Booking

  Scenario: Requester reopens denied booking
    Given I am the requester of a Denied booking
    When I POST /api/v1/bookings/{id}/reopen?token=xxx with new dates
    Then status should change to Pending
    And all approvals should reset to NoResponse
    And approvers should be notified
```

**Tasks:**
- [ ] Implement approve endpoint (idempotent)
- [ ] Implement deny endpoint (require comment)
- [ ] Implement reopen endpoint
- [ ] Check state transitions (Pending → Confirmed/Denied)
- [ ] Handle first-action-wins (BR-024)
- [ ] Add timeline events for all actions

**Definition of Done:**
- [ ] All approval scenarios pass
- [ ] State machine works correctly
- [ ] Timeline events logged
- [ ] Tests ≥85% coverage

**Next:** [Phase 4: Email Integration](phase-4-email-integration.md)
