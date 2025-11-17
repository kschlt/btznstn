# Phase 4: Email Integration

## Goal
Integrate Resend email service with German templates.

**Duration:** 2 days | **Dependencies:** Phase 2, 3

---

## User Stories

### US-4.1: Email Service Setup
```gherkin
Feature: Email Service

  Scenario: Send test email
    Given Resend is configured with API key
    When I call send_email("test@example.com", "Test Subject", "<p>Body</p>")
    Then email should be sent successfully
    And Resend dashboard should show the email
```

### US-4.2: Booking Created Email
```gherkin
Feature: Booking Created Notification

  Scenario: Requester receives confirmation
    Given I create a booking
    Then I should receive an email with:
      | field          | value                    |
      | subject        | Deine Buchungsanfrage    |
      | body_includes  | Wir haben deine Anfrage  |
      | includes_link  | Personal access link     |

  Scenario: Approvers receive notification
    Given I create a booking
    Then Ingeborg, Cornelia, Angelika should each receive:
      | includes       |
      | Neue Anfrage   |
      | Approve link   |
      | Deny link      |
```

### US-4.3: Approval Notifications
```gherkin
Feature: Approval Notifications

  Scenario: Requester notified on partial approval
    Given two of three approvers approved
    When the third approver approves
    Then requester receives "Alles bestätigt!"

  Scenario: All parties notified on confirmation
    When final approval occurs
    Then requester and all approvers receive confirmation email
```

**Tasks:**
- [ ] Create `app/services/email_service.py`
- [ ] Configure Resend API client
- [ ] Create HTML email templates (11 types from specs)
- [ ] Implement send functions for each email type
- [ ] Add retry logic (3 attempts, exponential backoff per BR-022)
- [ ] Mock email service in tests

**Definition of Done:**
- [ ] All 11 email types implemented
- [ ] Emails sent on correct triggers
- [ ] German copy matches specifications
- [ ] Tests mock email sending
- [ ] Manual test: receive actual emails

**Next:** [Phase 5: Web Calendar](phase-5-frontend-calendar.md)
