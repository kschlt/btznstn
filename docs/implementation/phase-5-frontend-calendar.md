# Phase 5: Frontend Calendar

## Goal
Build calendar UI with booking display and navigation.

**Duration:** 3-4 days | **Dependencies:** Phase 2

---

## User Stories

### US-5.1: Calendar Display
```gherkin
Feature: Calendar View

  Scenario: Display month view
    Given I visit the home page
    Then I should see a calendar for the current month
    And I should see weekday headers (Mo-So)
    And weekends should be visually distinct

  Scenario: Display bookings in calendar
    Given bookings exist in August 2025
    When I navigate to August 2025
    Then I should see booking cards for each booking
    And each card should show:
      | field               |
      | requester_first_name|
      | party_size          |
      | status badge        |
      | affiliation color   |

  Scenario: Mobile-responsive calendar
    Given I am on iPhone 8 viewport (375px)
    When I view the calendar
    Then all elements should be visible
    And tap targets should be ≥44px
```

### US-5.2: Navigation
```gherkin
Feature: Calendar Navigation

  Scenario: Navigate months
    Given I am viewing January 2025
    When I click "Next Month"
    Then I should see February 2025

  Scenario: Jump to today
    Given I am viewing December 2025
    When I click "Heute"
    Then I should see the current month
```

### US-5.3: Booking Details
```gherkin
Feature: View Booking Details

  Scenario: Click booking opens details
    Given a booking card is visible
    When I click it
    Then I should see full booking details
    And I should see approval status
    And I should see timeline
```

**Tasks:**
- [ ] Create calendar grid component
- [ ] Fetch bookings from API
- [ ] Display booking cards with affiliation colors
- [ ] Implement month navigation
- [ ] Add "Heute" button
- [ ] Make responsive (mobile-first)
- [ ] Add loading states
- [ ] Playwright E2E tests

**Definition of Done:**
- [ ] Calendar displays correctly on mobile + desktop
- [ ] Bookings visible with correct data
- [ ] Navigation works
- [ ] Playwright tests pass
- [ ] Accessibility: no axe violations

**Next:** [Phase 6: Frontend Booking](phase-6-frontend-booking.md)
