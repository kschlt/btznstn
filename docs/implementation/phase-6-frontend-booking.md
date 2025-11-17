# Phase 6: Web Booking

## Goal
Build booking create/edit forms with validation.

**Duration:** 3-4 days | **Dependencies:** Phase 5

---

## User Stories

### US-6.1: Create Booking Form
```gherkin
Feature: Create Booking

  Scenario: Open create form
    Given I am on the calendar page
    When I click "Neue Anfrage"
    Then a dialog should open with a form

  Scenario: Submit valid booking
    Given the create form is open
    When I fill in all required fields correctly
    And I submit
    Then I should see "Anfrage gesendet"
    And the calendar should refresh

  Scenario: Show validation errors
    Given the create form is open
    When I submit without filling required fields
    Then I should see error messages:
      | field   | error                       |
      | Vorname | Dieses Feld wird benötigt.  |
      | E-Mail  | Dieses Feld wird benötigt.  |

  Scenario: Prevent submission on conflict
    Given dates 2025-08-01 to 2025-08-05 are blocked
    When I select those dates and submit
    Then I should see "überschneidet sich mit"
    And the form should remain open
```

### US-6.2: Date Picker
```gherkin
Feature: Date Picker

  Scenario: Select dates via calendar
    Given the create form is open
    When I click "Startdatum"
    Then a calendar popup should appear
    When I select 2025-08-01
    Then "01.08.2025" should appear in the field

  Scenario: Disable past dates
    Given the date picker is open
    When I view today's date
    Then past dates should be disabled
```

### US-6.3: Edit Booking
```gherkin
Feature: Edit Booking

  Scenario: Requester edits Pending booking
    Given I am the requester with a Pending booking
    When I click "Bearbeiten"
    Then I should see a form pre-filled with current data
    When I change party_size to 5 and submit
    Then the booking should be updated
```

**Tasks:**
- [ ] Create BookingForm component (Shadcn + React Hook Form + Zod)
- [ ] Add date pickers (Shadcn Calendar)
- [ ] Add select for affiliation
- [ ] Implement client-side validation
- [ ] Handle API errors (show error messages)
- [ ] Add edit form (reuse BookingForm)
- [ ] Playwright tests for form workflows

**Definition of Done:**
- [ ] Form validation works (Zod)
- [ ] API integration works
- [ ] Error messages display correctly (German)
- [ ] Mobile-friendly (44px tap targets)
- [ ] Playwright E2E tests pass

**Next:** [Phase 7: Approver Interface](phase-7-approver-interface.md)
