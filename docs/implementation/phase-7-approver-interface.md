# Phase 7: Approver Interface

## Goal
Build approver overview and action workflows.

**Duration:** 2-3 days | **Dependencies:** Phase 3, 4

---

## User Stories

### US-7.1: Approver Overview
```gherkin
Feature: Approver Overview

  Scenario: View outstanding requests
    Given I am Ingeborg
    When I visit /approver?token=xxx
    Then I should see the "Outstanding" tab active
    And I should see all bookings where my decision = NoResponse
    And they should be sorted by last_activity_at DESC

  Scenario: View history
    Given I am Ingeborg
    When I click the "History" tab
    Then I should see all bookings I've been involved in
    And they should include Pending, Confirmed, and Denied statuses
```

### US-7.2: One-Click Approve
```gherkin
Feature: One-Click Approve

  Scenario: Approve from email link
    Given I receive an approval email
    When I click "Zustimmen" link
    Then the booking should be approved
    And I should see a result page: "Danke – du hast zugestimmt"

  Scenario: Approve from overview
    Given I am on the outstanding tab
    When I click "Zustimmen" on a booking
    Then it should be approved
    And it should disappear from outstanding
```

### US-7.3: Deny with Comment
```gherkin
Feature: Deny Booking

  Scenario: Deny requires comment
    Given I click "Ablehnen"
    Then a dialog should open requesting a comment
    When I submit without a comment
    Then I should see "Bitte gib einen kurzen Grund an."
    When I enter a comment and submit
    Then the booking should be denied
```

**Tasks:**
- [ ] Create ApproverOverview page
- [ ] Implement Outstanding tab (filter by NoResponse)
- [ ] Implement History tab (all bookings)
- [ ] Add approve button (one-click)
- [ ] Add deny dialog (require comment)
- [ ] Implement action link result pages
- [ ] Playwright tests

**Definition of Done:**
- [ ] Outstanding/History tabs work
- [ ] Approve/Deny actions work
- [ ] Result pages display correctly
- [ ] Tests pass

**Next:** [Phase 8: Polish & Production](phase-8-polish.md)
