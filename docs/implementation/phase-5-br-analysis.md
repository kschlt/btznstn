# Phase 5: Business Rules Analysis for Web Calendar Frontend

**Date:** 2025-11-17 | **Duration:** 3-4 days | **Frontend Focus:** Calendar UI with booking display

---

## Executive Summary

Phase 5 implements three core frontend features: calendar display, month navigation, and booking detail views. These features depend on **12 critical business rules** spanning date handling, privacy, status management, and UI localization.

**Key Risk Areas:**
- Inclusive end date calculations (BR-001) → off-by-one errors common
- Denied booking privacy (BR-004) → data exposure if not enforced
- Past item read-only state (BR-014) → concurrent action timing issues
- Date format localization (BR-011) → German format DD.–DD.MM.YYYY

**Estimated Test Coverage:** 40-50 Playwright E2E tests across 3 user stories

---

## User Story: US-5.1 - Calendar Display

**Gherkin:**
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
      | requester_first_name |
      | party_size           |
      | status badge         |
      | affiliation color    |

  Scenario: Mobile-responsive calendar
    Given I am on iPhone 8 viewport (375px)
    When I view the calendar
    Then all elements should be visible
    And tap targets should be ≥44px
```

### Applicable Business Rules

| BR # | Rule | Implementation Impact | Why It Matters |
|------|------|----------------------|----------------|
| **BR-001** | **Inclusive End Date** | Calendar cells must represent full date range. Booking Jan 1-3 spans 3 days (1, 2, 3), not 2. | Off-by-one errors cause hidden bookings. Multi-month bookings must appear in ALL overlapping months. |
| **BR-002** | **No Overlaps** | Pending/Confirmed bookings block dates. Denied/Canceled don't. Conflict summary shows first name + status. | Calendar must visually distinguish "booked" (blocks future bookings) from "denied" (frees dates). |
| **BR-004** | **Denial Handling** | Denied bookings HIDDEN from public calendar. Dates freed immediately. Only requester sees denied status. | Privacy critical: Denied bookings must not appear in public calendar view. Requires role-based filtering. |
| **BR-011** | **German-Only UI** | All text in German (informal "du"). Weekday headers: Mo-So. Month names German. Date format: DD.–DD.MM.YYYY. | Localization affects display, sorting, formatting. No English fallback. |
| **BR-014** | **Past Items Read-Only** | EndDate < today → read-only. Visual "Past" indicator. Flip at 00:00 Europe/Berlin day after EndDate. | Timeline boundary issues: booking ending "today" is NOT past, ending "yesterday" IS. Timezone matters (Berlin time). |
| **BR-016** | **Party Size Format** | Always "n Personen" (even 1 person = "1 Personen", not "1 Person"). Grammatically incorrect but required. | Display consistency. Never show "1 Person" or "n Guests". |
| **BR-026** | **Future Horizon** | StartDate ≤ today + FUTURE_HORIZON_MONTHS (default 18). Booking creation limited to 18 months out. | Calendar should reflect this limit. Very old bookings (19+ months out) shouldn't exist, but display should account for config. |
| **BR-027** | **Long Stay Confirmation** | TotalDays > LONG_STAY_WARN_DAYS (default 7) triggers confirmation dialog before submission. | Calendar might show visual indicator for "long stay" bookings (e.g., multi-week bookings highlighted). Helps users understand 2-week bookings at a glance. |

### Edge Cases for Testing

#### Date Boundary Edge Cases
1. **Same-day booking** (Jan 15-15 = 1 day)
   - Must display as single cell
   - Total days = 1
   - GH: Then I should see "1 Personen" and 1-day span

2. **Multi-month booking** (Jan 15 - Mar 15)
   - Must appear in January, February, AND March calendars
   - Spans entire month view for February
   - GH: When I navigate to February, Then I should see Jan 15-Mar 15 booking card spanning entire month

3. **Month boundary bookings**
   - Booking Jan 28 - Feb 5 appears in both months
   - GH: Then I should see the booking in both month views

4. **Inclusive end date verification**
   - Jan 1-5: displays 5 cells (not 4)
   - Verify total_days = end - start + 1
   - GH: Then booking should span 5 calendar cells

#### Past/Present Boundary Edge Cases
5. **Booking ending today**
   - EndDate = today → NOT past, still interactive
   - GH: Given booking ends today, When I view calendar, Then I should see action buttons enabled

6. **Booking ending yesterday**
   - EndDate = today - 1 → IS past, read-only
   - GH: Given booking ended yesterday, When I view calendar, Then I should see "Vergangen" indicator

7. **Timezone boundary**
   - Europe/Berlin time, flip at 00:00 Berlin time
   - GH: Given current time 23:59 UTC on Jan 15, EndDate = Jan 15, When calendar re-renders, Then should still show as future (not yet 00:00 Berlin time)

#### Status/Privacy Edge Cases
8. **Denied bookings visibility**
   - Public calendar: Denied HIDDEN
   - Requester view: Denied VISIBLE (but grayed/disabled)
   - Approver view: Denied visible if involved
   - GH: Given public link, When viewing denied booking cell, Then cell should not be present

9. **Pending vs Confirmed blocking**
   - Both block future bookings (BR-002)
   - Denied does NOT block (frees dates)
   - Visual distinction needed
   - GH: Given Pending and Confirmed bookings, When viewing calendar, Then both should show as "blocked" in date pickers

10. **Affiliation color contrast**
    - Ingeborg: #C1DBE3 (light blue)
    - Cornelia: #C7DFC5 (light green)
    - Angelika: #DFAEB4 (light pink)
    - All must have WCAG AA contrast with text on mobile
    - GH: Then text over affiliation color should pass axe accessibility checks

#### German Localization Edge Cases
11. **German date format**
    - Jan 1-5, 2025 → "01.–05.01.2025" (with en-dash, not hyphen)
    - Single day → "15.01.2025"
    - Verify exact format from spec
    - GH: Then booking should display "01.–05.08.2025" (not "1.-5.8.2025" or "08/01-08/05")

12. **German weekday headers**
    - Mo, Di, Mi, Do, Fr, Sa, So (not Mon, Tue, etc.)
    - Week starts Monday (not Sunday)
    - GH: Then weekday headers should be "Mo Di Mi Do Fr Sa So"

13. **German holiday display** (optional per spec)
    - Holidays shown visually only
    - No business logic impact
    - Region configurable (DE, DE-NRW, etc.)
    - GH: Then German holidays should appear if configured

#### Party Size Edge Cases
14. **Single person booking**
    - "1 Personen" (not "1 Person")
    - GH: Then party size should display "1 Personen"

15. **Maximum party size**
    - MAX_PARTY_SIZE = 10 default
    - Display "10 Personen"
    - Anything > 10 shouldn't exist in DB
    - GH: Then party size should never show > 10

#### Long Stay Indication
16. **Booking exactly at warning threshold**
    - 7 days: no warning
    - 8 days: shows warning dialog (BR-027)
    - Display might show visual indicator
    - GH: Given 8-day booking, Then calendar cell might show "long stay" indicator or warning

#### Empty/Full States
17. **Empty calendar**
    - No bookings for month
    - GH: Then "Keine Einträge in diesem Zeitraum." message shown

18. **Fully booked calendar**
    - Many overlapping bookings
    - All visible (not truncated)
    - GH: Then all bookings visible (with scrolling if needed)

#### Future Horizon Edge Case
19. **Booking near future horizon**
    - Default 18 months: can book up to today + 18 months
    - Booking at exactly 18-month mark: allowed
    - Booking at 18-month + 1 day: not allowed (backend blocks, but frontend respects visually)
    - GH: When navigating to month 19+, Then calendar should show readonly or disabled state

### German Copy Requirements (from ui-screens.md)

| Copy Element | German Text | Location |
|--------------|-------------|----------|
| Weekday headers | Mo, Di, Mi, Do, Fr, Sa, So | Calendar grid |
| Empty state | "Keine Einträge in diesem Zeitraum." | Below calendar |
| Month/year selector | January=Januar, February=Februar, etc. | Calendar header |
| Status badge | "Ausstehend" (Pending), "Bestätigt" (Confirmed), "Abgelehnt" (Denied, not public), "Storniert" (Canceled, not public) | Card on calendar cell |
| Past indicator | "Vergangen" | Read-only booking card |
| Affiliation | Ingeborg, Cornelia, Angelika (names, not English) | Color legend or card attribution |

### Playwright Test Matrix for US-5.1

**Total Estimated Tests: 22 E2E tests**

#### Happy Path Tests (3)
```
1. test_calendar_displays_current_month
   - Navigate to home
   - Assert current month displays
   - Assert weekday headers present (Mo-So)
   - Assert weekends visually distinct

2. test_calendar_displays_all_bookings_in_month
   - Create 3 bookings in August 2025
   - Navigate to August
   - Assert all 3 booking cards visible
   - Assert each card shows name, party size, status, color

3. test_booking_card_shows_all_required_fields
   - Navigate to month with booking
   - Assert requester_first_name visible (truncated if long)
   - Assert party_size shows "n Personen" format
   - Assert status badge visible (Pending/Confirmed/etc.)
   - Assert affiliation color present
```

#### BR-001: Inclusive End Date (3)
```
4. test_same_day_booking_displays_correctly
   - Create booking Jan 15-15
   - Navigate to January
   - Assert booking occupies 1 cell (not 2)
   - Assert total_days = 1

5. test_multimonth_booking_appears_in_all_months
   - Create booking Jan 15 - Mar 15
   - Navigate to January → Assert visible
   - Navigate to February → Assert visible
   - Navigate to March → Assert visible

6. test_inclusive_end_date_spans_correctly
   - Create booking Jan 1-5
   - Assert 5 cells highlighted/occupied
   - Not 4 cells
```

#### BR-002: No Overlaps & Conflict Summary (2)
```
7. test_pending_and_confirmed_show_as_booked
   - Create Pending and Confirmed bookings
   - Assert both appear with status badge
   - Assert both visually indicate "blocked" status

8. test_denied_booking_not_shown_in_public_calendar
   - Create Denied booking
   - View as public link
   - Assert cell is empty/not shown
   - Verify dates appear free for new bookings
```

#### BR-004: Denial Hidden/Privacy (2)
```
9. test_denied_booking_hidden_from_public_view
   - Create Denied booking
   - View calendar with public link
   - Assert booking cell not visible
   - Navigate date picker → Assert dates shown as free

10. test_denied_booking_visible_to_requester
    - Create Denied booking
    - View with requester link
    - Assert booking visible with "Abgelehnt" status
    - Assert grayed/disabled state
```

#### BR-011: German UI (3)
```
11. test_weekday_headers_german
    - Load calendar
    - Assert headers "Mo Di Mi Do Fr Sa So"
    - Not "Mon Tue Wed Thu Fri Sat Sun"

12. test_date_format_german
    - Create booking Jan 1-5, 2025
    - Assert displays "01.–05.01.2025"
    - Not "1-5 January" or "01/01-01/05"

13. test_month_year_names_german
    - Navigate each month
    - Assert "Januar", "Februar", "März", etc.
    - Not English month names
```

#### BR-014: Past Items Read-Only (3)
```
14. test_past_booking_shows_readonly_indicator
    - Create booking ending yesterday
    - Navigate to that month
    - Assert "Vergangen" indicator visible
    - Assert action buttons disabled/hidden

15. test_current_day_booking_not_past
    - Create booking ending today
    - Assert NOT marked as past
    - Assert action buttons enabled

16. test_booking_boundary_at_timezone_transition
    - Create booking ending "tomorrow" 23:55 UTC
    - Mock time to 00:05 UTC = 01:05 Berlin
    - Assert still shows as future (00:00 Berlin hasn't hit yet)
    - [This is tricky - requires timezone mocking]
```

#### BR-016: Party Size Format (1)
```
17. test_party_size_always_personen_format
    - Create bookings with 1, 5, 10 persons
    - Assert displays "1 Personen", "5 Personen", "10 Personen"
    - Never "1 Person", "5 Guests", etc.
```

#### BR-026: Future Horizon (1)
```
18. test_future_horizon_respected_visually
    - Default 18 months
    - Navigate to month at 18-month mark → Visible
    - Navigate to month at 19-month mark → Grayed or disabled
```

#### Mobile & Responsive (3)
```
19. test_calendar_responsive_375px
    - Set viewport to iPhone 8 (375×667)
    - Assert all calendar cells visible
    - Assert no horizontal scrolling
    - Assert layout readability

20. test_tap_targets_minimum_44px
    - Inspect booking cards
    - Assert each card touch area ≥44×44pt
    - Assert spacing between targets sufficient

21. test_no_hover_dependencies_mobile
    - Load calendar on 375px
    - Verify all actions triggered by tap, not hover
    - Assert focus states visible without hover
```

#### Accessibility (2)
```
22. test_affiliation_color_contrast_wcag_aa
    - Inspect text over each affiliation color (#C1DBE3, #C7DFC5, #DFAEB4)
    - Run axe accessibility checks
    - Assert WCAG AA contrast ratio met
    - Assert no color-only information

23. test_keyboard_navigation_and_focus
    - Tab through calendar elements
    - Assert focus visible on all interactive elements
    - Assert logical tab order
```

---

## User Story: US-5.2 - Navigation

**Gherkin:**
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

### Applicable Business Rules

| BR # | Rule | Implementation Impact | Why It Matters |
|------|------|----------------------|----------------|
| **BR-011** | **German-Only UI** | Navigation button "Heute" (not "Today"). Month controls in German. | All navigation labels must be German. No English text. |
| **BR-014** | **Past Items Read-Only** | Past months visually distinct/disabled. Can navigate to past but see readonly state. | Users should understand past months are archived/read-only. Timezone boundary matters. |
| **BR-026** | **Future Horizon** | Cannot navigate/book beyond today + FUTURE_HORIZON_MONTHS. Visually limit or disable navigation beyond this point. | Users should not navigate to far future. System enforces 18-month max by default. |

### Edge Cases for Testing

1. **Navigate forward from January → February** (normal case)
2. **Navigate backward from January → December** (wraps previous year)
3. **Navigate to December → cannot go forward further** (recent past only, or wraps to future year)
4. **Jump to "today" from distant month** ("Heute" button)
5. **Keyboard navigation** (arrow keys left/right for month)
6. **Mobile swipe navigation** (swipe left/right on calendar)
7. **Month/year selector dropdown** (jump directly to specific month/year)
8. **Boundary: navigate to January 2023** (past, should show readonly)
9. **Boundary: navigate to month 19 months out** (beyond FUTURE_HORIZON)
10. **Double-click prevention** (rapid next/prev clicks)

### German Copy Requirements

| Copy Element | German Text | Location |
|--------------|-------------|----------|
| Next button | "Nächster Monat" or ">" with aria-label | Calendar header |
| Previous button | "Vorheriger Monat" or "<" with aria-label | Calendar header |
| Today button | "Heute" | Calendar header |
| Month dropdown | January=Januar, February=Februar, etc. | Calendar header |

### Playwright Test Matrix for US-5.2

**Total Estimated Tests: 12 E2E tests**

#### Happy Path (2)
```
1. test_navigate_next_month
   - Start viewing January 2025
   - Click next month button
   - Assert February 2025 displayed

2. test_jump_to_today
   - Navigate to December 2025
   - Click "Heute" button
   - Assert current month displayed
```

#### Previous Month Navigation (2)
```
3. test_navigate_previous_month
   - Start viewing March 2025
   - Click previous month button
   - Assert February 2025 displayed

4. test_navigate_wraps_to_previous_year
   - Start viewing January 2025
   - Click previous month button
   - Assert December 2024 displayed
```

#### Keyboard Navigation (2)
```
5. test_keyboard_arrow_right_next_month
   - Focus calendar
   - Press right arrow
   - Assert next month displayed

6. test_keyboard_arrow_left_previous_month
   - Focus calendar
   - Press left arrow
   - Assert previous month displayed
```

#### Mobile Swipe (2)
```
7. test_swipe_left_next_month (mobile 375px)
   - Focus calendar on mobile
   - Swipe left
   - Assert next month displayed

8. test_swipe_right_previous_month (mobile 375px)
   - Focus calendar on mobile
   - Swipe right
   - Assert previous month displayed
```

#### Boundaries & Limits (2)
```
9. test_cannot_navigate_beyond_future_horizon
   - Current date: Nov 2025
   - FUTURE_HORIZON = 18 months
   - Try to navigate to June 2027 (19+ months out)
   - Assert month shows but appears grayed/disabled
   - OR assert can't navigate beyond max

10. test_past_month_shows_readonly_indicator
    - Navigate to January 2024 (past month)
    - Assert all bookings/dates show "Vergangen" indicator
    - Assert interaction disabled
```

#### BR-011: German Labels (1)
```
11. test_navigation_labels_german
    - Load calendar
    - Assert "Heute" button visible (not "Today")
    - Assert month names German (Januar, Februar, etc.)
    - Assert nav buttons have German aria-labels
```

#### Accessibility (1)
```
12. test_keyboard_focus_visible_on_nav_buttons
    - Tab to navigation buttons
    - Assert focus outline visible
    - Assert logical tab order (prev, month/year, next, heute)
```

---

## User Story: US-5.3 - Booking Details

**Gherkin:**
```gherkin
Feature: View Booking Details

  Scenario: Click booking opens details
    Given a booking card is visible
    When I click it
    Then I should see full booking details
    And I should see approval status
    And I should see timeline
```

### Applicable Business Rules

| BR # | Rule | Implementation Impact | Why It Matters |
|------|------|----------------------|----------------|
| **BR-001** | **Inclusive End Date** | Total days calculation: end - start + 1. Display "Jan 1-5" as 5 days. | Calculate and display total_days correctly. Affects summary display. |
| **BR-004** | **Denial Privacy** | Denied bookings hidden from public. Requester sees full status. Approvers see if involved. | Privacy critical: must check viewer role before showing denied status. Public link cannot see denied bookings. |
| **BR-011** | **German-Only UI** | All detail labels, timeline, status badges in German. Date format DD.–DD.MM.YYYY. | No English text in details view. Localized status labels. |
| **BR-014** | **Past Read-Only** | Past bookings show readonly indicator. No action buttons (Edit, Cancel, Approve). | Disable user interactions for past bookings. Show "Vergangen" state. |
| **BR-016** | **Party Size Format** | Display "n Personen" in details. | Consistency with calendar display. |
| **BR-023** | **Timeline Sorting** | Timeline events sorted by LastActivityAt (chronological). Each event shows actor + action. | Audit trail clarity. Chronological order helps understand booking history. |

### Edge Cases for Testing

1. **Single-day booking (Jan 15-15)**
   - Total days = 1
   - Display date as "15.01.2025" (not "15.–15.01.2025")

2. **Multi-month booking (Jan 15 - Mar 15)**
   - Total days = 60
   - Display "15.01.–15.03.2025"

3. **Past booking (ended yesterday)**
   - Show "Vergangen" indicator
   - Disable all action buttons
   - Show read-only timeline

4. **Denied booking access**
   - Public link: HIDDEN (should not be accessible)
   - Requester link: VISIBLE with "Abgelehnt" status
   - Approver link (if not involved): depends on implementation (typically hidden)

5. **Timeline with no events** (only submission)
   - Show "Eingereicht" event

6. **Timeline with all event types**
   - Submitted, Approved (3x), Confirmed
   - Sorted chronologically

7. **Timeline with date edit**
   - Show old→new diff: "15.01. → 20.01."
   - Indicate if approvals reset

8. **Timeline with comment (approval)**
   - Show comment below approval event

9. **Missing optional fields**
   - Description: show "Keine Beschreibung"
   - Affiliation: always present

10. **Requester vs Public vs Approver access**
    - Public: limited info, no comments, no denied bookings
    - Requester: full info, own details, can edit/cancel
    - Approver: full info, can approve/deny, timeline visible

### German Copy Requirements (from ui-screens.md)

| Copy Element | German Text | Location |
|--------------|-------------|----------|
| Status badge | "Ausstehend", "Bestätigt", "Abgelehnt", "Storniert" | Details header |
| Past indicator | "Vergangen" | Read-only overlay |
| Timeline header | "Chronik" or "Zeitstrahl" | Details section |
| Submitted event | "Eingereicht" | Timeline |
| Approved event | "Zugestimmt" | Timeline (with approver name) |
| Confirmed event | "Bestätigt" | Timeline |
| Denied event | "Abgelehnt" (with comment) | Timeline |
| Edit button | "Bearbeiten" | Action buttons |
| Cancel button | "Stornieren" | Action buttons |
| Reopen button | "Wieder eröffnen" | Action buttons (if Denied) |
| Approve button | "Zustimmen" | Approver actions |
| Deny button | "Ablehnen" | Approver actions |
| Party size | "n Personen" | Details |
| Date format | "01.–05.01.2025" | Details |
| Empty description | "Keine Beschreibung" | Details |

### Playwright Test Matrix for US-5.3

**Total Estimated Tests: 16 E2E tests**

#### Happy Path (2)
```
1. test_click_booking_card_opens_details_modal
   - View calendar
   - Click booking card
   - Assert modal/page opens
   - Assert booking details visible

2. test_details_show_all_required_fields
   - Open booking details
   - Assert name visible (full, not truncated)
   - Assert date range (DD.–DD.MM.YYYY format)
   - Assert party size ("n Personen")
   - Assert status badge
   - Assert timeline
```

#### BR-001: Inclusive End Date (1)
```
3. test_total_days_calculated_correctly
   - Open booking Jan 1-5
   - Assert displays "5 Tage" or "5 days" translated
   - Assert calculation = end - start + 1
   - Test same-day: Jan 15-15 → "1 Personen" (not days, but party size)
```

#### BR-004: Privacy/Denial (2)
```
4. test_denied_booking_hidden_from_public_link
   - Create Denied booking
   - Attempt access via public calendar → booking not shown
   - Attempt direct URL access via public link → should redirect or show 404/permission error

5. test_denied_booking_visible_to_requester
   - Create Denied booking
   - Access via requester link
   - Assert "Abgelehnt" status visible
   - Assert denial comment visible (if provided)
   - Assert "Wieder eröffnen" button visible
```

#### BR-011: German Localization (2)
```
6. test_all_details_text_german
   - Open details
   - Assert all labels German
   - Assert status badges German ("Ausstehend", "Bestätigt", etc.)
   - Assert buttons German ("Bearbeiten", "Stornieren", "Zustimmen")

7. test_date_format_german_with_endash
   - Open details
   - Assert date shows "01.–05.01.2025" (with en-dash, not hyphen)
   - Assert single day shows "15.01.2025" (not "15.–15.01.2025")
```

#### BR-014: Past Read-Only (2)
```
8. test_past_booking_shows_readonly_indicator
   - Open booking ended yesterday
   - Assert "Vergangen" indicator visible
   - Assert action buttons disabled/hidden (Edit, Cancel, etc.)

9. test_past_booking_approval_buttons_disabled
   - Open past booking as approver
   - Assert Approve/Deny buttons disabled/hidden
   - Assert timeline visible but actions not available
```

#### BR-016: Party Size (1)
```
10. test_party_size_format_personen
    - Open bookings with 1, 5, 10 persons
    - Assert displays "1 Personen", "5 Personen", "10 Personen"
```

#### BR-023: Timeline (2)
```
11. test_timeline_displays_all_events
    - Create booking with submission, approvals, confirmation
    - Open details
    - Assert all events visible
    - Assert events in chronological order (oldest first)

12. test_timeline_shows_correct_actors
    - Booking submitted by Requester
    - Approved by Ingeborg, Cornelia, Angelika
    - Confirmed by system
    - Assert timeline shows named parties + actions
    - Assert "Schon erledigt" message if action already taken
```

#### Modal/Dialog Behavior (1)
```
13. test_details_modal_closes_on_backdrop_click
    - Open details modal
    - Click backdrop/outside modal
    - Assert modal closes
    - Calendar still visible underneath
```

#### Mobile & Responsive (2)
```
14. test_details_modal_responsive_375px
    - Open details on iPhone 8 (375px)
    - Assert all content visible
    - Assert readable without horizontal scroll
    - Assert close button accessible

15. test_details_tap_targets_44px_minimum
    - Open details on 375px
    - Inspect action buttons
    - Assert each button ≥44×44pt
    - Assert spacing adequate
```

#### Accessibility (2)
```
16. test_details_keyboard_navigation
    - Open details modal
    - Press Tab → cycle through action buttons
    - Press Esc → modal closes
    - Assert focus trapped in modal while open

17. test_details_focus_management
    - Click booking → focus moves to modal (not body)
    - Close modal → focus returns to booking card
    - Assert focus outline visible on all elements
```

---

## Comprehensive Test Matrix Summary

| User Story | Test Category | Count | Notes |
|------------|---------------|-------|-------|
| **US-5.1: Calendar Display** | Happy Path | 3 | Display, bookings, responsive |
| | BR-001 (Inclusive) | 3 | Same-day, multi-month, spans |
| | BR-002 (Overlaps) | 2 | Pending/Confirmed, Denied |
| | BR-004 (Denial) | 2 | Hidden public, visible requester |
| | BR-011 (German) | 3 | Weekday headers, date format, months |
| | BR-014 (Past) | 3 | Past indicator, boundary, timezone |
| | BR-016 (Party) | 1 | "n Personen" format |
| | BR-026 (Horizon) | 1 | Future limit |
| | Mobile | 3 | 375px, 44×44pt, no hover |
| | Accessibility | 2 | Color contrast, keyboard |
| | **US-5.1 Total** | **23** | |
| **US-5.2: Navigation** | Happy Path | 2 | Next, today button |
| | Previous | 2 | Prev month, year wrap |
| | Keyboard | 2 | Arrow left/right |
| | Mobile | 2 | Swipe left/right |
| | Boundaries | 2 | Future horizon, past readonly |
| | BR-011 (German) | 1 | German labels |
| | Accessibility | 1 | Keyboard focus |
| | **US-5.2 Total** | **12** | |
| **US-5.3: Booking Details** | Happy Path | 2 | Click opens, shows fields |
| | BR-001 (Inclusive) | 1 | Total days calculation |
| | BR-004 (Denial) | 2 | Hidden public, visible requester |
| | BR-011 (German) | 2 | All text German, en-dash format |
| | BR-014 (Past) | 2 | Readonly indicator, disabled buttons |
| | BR-016 (Party) | 1 | "n Personen" format |
| | BR-023 (Timeline) | 2 | All events, chronological |
| | Modal | 1 | Close behavior |
| | Mobile | 2 | 375px responsive, 44×44pt |
| | Accessibility | 2 | Keyboard nav, focus management |
| | **US-5.3 Total** | **17** | |
| **GRAND TOTAL** | | **52** | Playwright E2E tests |

---

## Critical Implementation Notes

### Timezone Considerations (BR-014)
- All date/time logic must use **Europe/Berlin** timezone
- BookingEndDate < today (Berlin time) → past
- Boundary: booking ending "today" (Berlin) is NOT past
- Database stores dates in UTC; convert to Berlin for display/logic

### German Localization (BR-011)
**Date Format:** `DD.–DD.MM.YYYY`
- Use en-dash (–) not hyphen (-)
- Example: "01.–05.08.2025"
- Single day: "15.01.2025"
- German locale: `de-DE`

**Weekday Order:** Mo, Di, Mi, Do, Fr, Sa, So (week starts Monday)

**Status Badges:**
- Pending: "Ausstehend"
- Confirmed: "Bestätigt"
- Denied: "Abgelehnt" (not shown in public)
- Canceled: "Storniert" (not shown in public)

### Inclusive End Date Calculations (BR-001)
```
total_days = (endDate - startDate).days + 1

Examples:
- Jan 1-1: (Jan1 - Jan1 = 0) + 1 = 1 day ✓
- Jan 1-5: (Jan5 - Jan1 = 4) + 1 = 5 days ✓
- Jan 15 - Mar 15: (Mar15 - Jan15 = 60) + 1 = 61 days ✓
```

### Privacy Rules (BR-004)
```
Denied Booking Visibility:
- Public Link: HIDDEN (don't show in calendar or details)
- Requester Link: VISIBLE (show with "Abgelehnt" status)
- Approver Link: HIDDEN (unless involved - TBD based on requirements)

Check:
if (booking.status == DENIED && !currentUser.isRequester) {
    return 404 or hide from list
}
```

### Multi-Month Booking Display (BR-001 + BR-002)
```
Booking Jan 15 - Mar 15 must appear in:
- January calendar (partial month)
- February calendar (full month)
- March calendar (partial month)

Query logic:
SELECT * FROM bookings
WHERE start_date <= month_end AND end_date >= month_start
  AND status IN (PENDING, CONFIRMED)
```

### Affiliation Colors (from ui-screens.md)
| Approver | Color Code | WCAG AA Check Required |
|----------|-----------|----------------------|
| Ingeborg | #C1DBE3 (light blue) | Contrast ratio with text |
| Cornelia | #C7DFC5 (light green) | Contrast ratio with text |
| Angelika | #DFAEB4 (light pink) | Contrast ratio with text |

### Party Size Always "n Personen" (BR-016)
```
WRONG: "1 Person", "5 Guests", "10 people"
RIGHT: "1 Personen", "5 Personen", "10 Personen"

Implementation:
const formatPartySize = (count: number) => `${count} Personen`;
```

---

## Test Execution Roadmap

### Phase 5 Sprint Structure (3-4 days)

**Day 1: US-5.1 - Calendar Display**
- Write 23 Playwright tests
- Implement calendar component
- Run tests, fix failures

**Day 2: US-5.2 - Navigation**
- Write 12 Playwright tests
- Implement navigation controls
- Run tests, fix failures

**Day 3: US-5.3 - Booking Details**
- Write 17 Playwright tests
- Implement details modal/page
- Run tests, fix failures

**Day 4: Polish & Accessibility**
- Fix any remaining test failures
- Run full suite: `npx playwright test`
- Run type-check: `npm run type-check`
- Run linting: `npm run lint`
- Accessibility audit: `npx axe-core`

### Test Execution Commands

```bash
# Run all Phase 5 tests
npx playwright test tests/e2e/phase-5-*.spec.ts

# Run specific user story
npx playwright test tests/e2e/phase-5-calendar-display.spec.ts

# Run with mobile viewport
npx playwright test --project="iPhone 8"

# Run in headed mode (see browser)
npx playwright test --headed

# Type checking
npm run type-check

# Linting
npm run lint

# Accessibility
npx playwright test --grep "@accessibility"
```

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Off-by-one in date ranges (BR-001) | **CRITICAL** | Automated tests for same-day, multi-month, month boundaries |
| Denied bookings exposed in public (BR-004) | **CRITICAL** | Privacy tests: public link cannot see/access denied bookings |
| Past booking state incorrectly calculated (BR-014) | **HIGH** | Timezone boundary tests, mock time for edge cases |
| German localization paraphrased (BR-011) | **HIGH** | Use exact copy from specs, linting check |
| Touch targets < 44px (mobile) | **MEDIUM** | Responsive tests on 375px, inspection tools |
| Affiliation color contrast failure (BR-011) | **MEDIUM** | Axe accessibility checks, manual verification |

---

## Definition of Done (Phase 5)

- [ ] **All 52 Playwright tests pass** (US-5.1: 23, US-5.2: 12, US-5.3: 17)
- [ ] **All business rules enforced and tested** (BR-001, 002, 004, 011, 014, 016, 023, 026, 027)
- [ ] **German copy exact from specifications** (no paraphrasing)
- [ ] **Mobile responsive** (375px minimum, 44×44pt tap targets)
- [ ] **Accessibility compliant** (WCAG AA for contrast, focus management, keyboard nav)
- [ ] **Type-check passes** (`npm run type-check`)
- [ ] **Linting passes** (`npm run lint`)
- [ ] **Code coverage ≥80%**
- [ ] **Timezone handling correct** (Europe/Berlin)
- [ ] **No N+1 query problems** (eager loading, if applicable to frontend)
- [ ] **Self-review completed** (all acceptance criteria met)
- [ ] **Documentation updated** (any deviations from spec documented)

---

## Cross-Reference Index

**Business Rules:**
- BR-001: `docs/foundation/business-rules.md` line 11-16
- BR-002: `docs/foundation/business-rules.md` line 20-28
- BR-004: `docs/foundation/business-rules.md` line 102-120
- BR-011: `docs/foundation/business-rules.md` line 291-299
- BR-014: `docs/foundation/business-rules.md` line 31-42
- BR-016: `docs/foundation/business-rules.md` line 302-310
- BR-023: `docs/foundation/business-rules.md` line 411-428
- BR-026: `docs/foundation/business-rules.md` line 45-56
- BR-027: `docs/foundation/business-rules.md` line 58-70

**UI Specifications:**
- Calendar View: `docs/specification/ui-screens.md` line 9-124
- Booking Details: `docs/specification/ui-screens.md` line 126-251
- Mobile Considerations: `docs/specification/ui-screens.md` line 443-475
- Accessibility: `docs/specification/ui-screens.md` line 559-580

**Color Specifications:**
- Affiliation Colors: `docs/specification/ui-screens.md` line 69-76

---

**Next Phase:** [Phase 6: Web Booking](phase-6-frontend-booking.md) - Create/edit forms with full validation

