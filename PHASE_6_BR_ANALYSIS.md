# Phase 6: Web Booking - Business Rules Analysis

## Executive Summary

**Phase 6 Focus:** Create/Edit booking forms with full validation
**User Stories:** US-6.1 (Create Form), US-6.2 (Date Picker), US-6.3 (Edit Booking)
**BR Impact:** 13 business rules directly applicable
**Estimated Total Playwright Tests:** 38–42 E2E tests

---

## User Story Breakdown

### US-6.1: Create Booking Form

**Scope:** New booking form with all required fields, validation, conflict detection, success flow

#### Applicable Business Rules

| BR | Description | Implementation Impact | Criticality |
|:---|:-----------|:---------------------|:-----------|
| **BR-001** | Whole-day bookings; inclusive end date (`TotalDays = End - Start + 1`) | Date picker must enforce date selection; form must calculate/display TotalDays correctly; must validate ≥1 day range | 🔴 Critical |
| **BR-002** | No overlaps with Pending/Confirmed bookings | On form submit: API validates conflicts; form must display conflict error dialog showing first name + status; user can adjust dates and resubmit | 🔴 Critical |
| **BR-011** | German-only UI, informal "du" tone | All labels, placeholders, errors, buttons must be German; NO English text visible | 🔴 Critical |
| **BR-016** | Party size always displays as "n Personen" (even 1 = "1 Personen") | Party size field must normalize display; affects form output and validation messages | 🟠 High |
| **BR-017** | Party size range 1 ≤ n ≤ MAX (default 10) | Form validation: reject <1 or >10; error: "Teilnehmerzahl muss zwischen 1 und {{MAX}} liegen." | 🔴 Critical |
| **BR-019** | First name validation: letters, diacritics, space, hyphen, apostrophe; max 40 chars; trim; no emojis/newlines | Form input validation on blur + submit; show exact error: "Bitte gib einen gültigen Vornamen an (Buchstaben, Leerzeichen, Bindestrich, Apostroph; max. 40 Zeichen)." | 🔴 Critical |
| **BR-020** | Block URLs in Description field: http://, https://, www, mailto: | Textarea validation: reject if contains any blocked pattern; error: "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden." | 🟠 High |
| **BR-026** | Future horizon: StartDate ≤ today + FUTURE_HORIZON_MONTHS (default 18) | Date picker: disable dates >18 months out; form validation; error: "Anfragen dürfen nur maximal {{MONTHS}} Monate im Voraus gestellt werden." | 🔴 Critical |
| **BR-027** | Long stay confirmation: if TotalDays > LONG_STAY_WARN_DAYS (default 7), show dialog before submission | Calculate TotalDays on date change; if >7 days, show: "Diese Anfrage umfasst {{TotalDays}} Tage. Möchtest du fortfahren?" Dialog with "Abbrechen" / "Bestätigen" buttons | 🟠 High |

#### Implementation Details

**Form Fields:**
- **Requester First Name** (required, Zod + client validation per BR-019)
- **Email** (required, immutable after create, email validation)
- **Start Date** (required, date picker, disabled past + >18 months per BR-026)
- **End Date** (required, date picker, ≥ Start Date per BR-001)
- **Party Size** (required, 1–10 per BR-017)
- **Affiliation** (required, 3 options: Ingeborg/Cornelia/Angelika)
- **Description** (optional, max 500 chars, link detection per BR-020)

**Validation Strategy:**
```
Client-side (Zod):
  - First name: regex for allowed chars, max 40, trim
  - Email: RFC 5322 minimal, max 254
  - Party size: integer 1–10
  - Description: max 500, no http/https/www/mailto
  - Start/End dates: date type, End ≥ Start
  - Future horizon: Start ≤ today + 18 months (configurable)

Server-side (always validate):
  - All validations above (never trust client)
  - Conflict detection (BR-002): check overlaps with Pending/Confirmed
  - May reject if another booking submitted concurrently (BR-029)
  - Self-approval: if requester email matches an approver, auto-approve

UI Flow:
  1. User fills form
  2. On blur: validate individual fields (show errors)
  3. On submit:
     a. Validate all fields
     b. Calculate TotalDays
     c. If TotalDays > 7, show long-stay confirmation dialog
     d. On confirmation, submit to API
  4. If conflict error: show modal with conflicting booking(s) details
  5. If success: show "Anfrage gesendet. Du erhältst E-Mails, sobald entschieden wurde." + redirect to details
```

**German Copy Sources:**
- Error "überschneidet sich mit": `error-handling.md` line 45 + example line 22
- Error first name invalid: `error-handling.md` line 110–111
- Error party size: `error-handling.md` line 124–125
- Error links: `error-handling.md` line 175
- Error future horizon: `error-handling.md` line 41–42
- Success "Anfrage gesendet": `error-handling.md` line 211
- Long stay dialog (title, body): `error-handling.md` line 529–530

#### Edge Cases to Test (Playwright)

**Date Range Validation:**
1. Same day (start = end) → 1 day total, not rejected, displays "1.–01.08.2025"
2. Month boundary (Jan 31 – Feb 1) → 2 days, handles calendar change correctly
3. Year boundary (Dec 31 – Jan 2) → 3 days, handles year transition
4. Multi-month (Jan 15 – Mar 15) → 60 days, triggers long-stay dialog

**First Name Validation:**
5. Minimum (1 char) → accepted
6. Maximum (40 chars) → accepted
7. 41 chars → rejected with error
8. Whitespace trim ("  Anna  ") → stored/displayed as "Anna"
9. Diacritics ("Müller") → accepted
10. Hyphen ("Anna-Marie") → accepted
11. Apostrophe ("O'Brien") → accepted
12. Mixed ("José-María O'Donnell") → accepted (if fits 40 char limit)
13. Emoji ("Anna 😀") → rejected
14. Newline in input → rejected
15. Numbers ("Anna123") → rejected
16. Special chars ("Anna@#$") → rejected

**Party Size:**
17. Boundary minimum (1) → accepted, displays "1 Personen"
18. Boundary maximum (10) → accepted, displays "10 Personen"
19. Below minimum (0) → rejected, clears to 1 or shows error
20. Above maximum (11) → rejected, shows error
21. Decimal (3.5) → rejected, error "Bitte gib eine ganze Zahl ein."
22. Non-numeric ("five") → rejected

**Description Field:**
23. Empty (optional) → accepted
24. Max length (500 chars) → accepted
25. Over max (501 chars) → rejected, error "Text ist zu lang (max. 500 Zeichen)."
26. Contains "http://" → rejected, error "Links sind hier nicht erlaubt..."
27. Contains "https://" → rejected
28. Contains "www" → rejected
29. Contains "mailto:" → rejected
30. Contains newlines → accepted (allowed)
31. Contains emoji → accepted (allowed)

**Date Range Conflicts:**
32. Overlap with existing Pending booking → error dialog with first name + status
33. Overlap with existing Confirmed booking → same error
34. No overlap → accepted
35. Immediately after existing booking (Jan 1–5, new is Jan 6–10) → accepted (no overlap)
36. Immediately before existing booking → accepted

**Future Horizon:**
37. Start date today → accepted
38. Start date today + 17 months → accepted
39. Start date today + 18 months → accepted
40. Start date today + 19 months → rejected, error "Anfragen dürfen nur maximal 18 Monate im Voraus gestellt werden."

**Long Stay Confirmation:**
41. TotalDays = 6 → no dialog, submits directly
42. TotalDays = 7 → no dialog (=, not >)
43. TotalDays = 8 → shows dialog, requires confirmation
44. User cancels dialog → form remains open, data preserved
45. User confirms dialog → submission proceeds

**Email Validation:**
46. Valid email (john@example.com) → accepted
47. Missing @ → rejected, error "Bitte gib eine gültige E-Mail-Adresse an."
48. Missing domain → rejected
49. Email immutable after create (edit form) → field disabled/hidden

**Mobile Interactions:**
50. Tap targets all 44×44pt minimum → measured on 375px viewport
51. No hover states required → all interactions touch-friendly
52. Form submits on iPhone 8 viewport → no horizontal scroll

**Affiliation Selector:**
53. Three options visible (Ingeborg, Cornelia, Angelika) → each with color indicator
54. One required to be selected → default or required validation
55. Requester's affiliation changes UI state if they're an approver → visual cue

**Concurrent Submissions (Race Condition):**
56. Two users book same dates simultaneously → first wins (BR-029), second gets conflict error
57. API returns "Schon gebucht von Anna" → form shows error dialog

#### Test Matrix - US-6.1

**Happy Path:**
1. `test_open_create_form_via_button` - Click "Neue Anfrage" opens dialog
2. `test_fill_and_submit_valid_booking` - All fields valid, submit succeeds

**Validation Tests:**
3. `test_required_field_first_name` - Error "Dieses Feld wird benötigt."
4. `test_required_field_email` - Error "Dieses Feld wird benötigt."
5. `test_required_field_start_date` - Error "Dieses Feld wird benötigt."
6. `test_required_field_end_date` - Error "Dieses Feld wird benötigt."
7. `test_required_field_party_size` - Error "Dieses Feld wird benötigt."
8. `test_first_name_max_length_40` - 40 chars accepted, 41 rejected
9. `test_first_name_invalid_chars` - Emoji/number/special chars rejected
10. `test_first_name_whitespace_trimmed` - "  Anna  " → "Anna"
11. `test_first_name_diacritics` - "Müller" accepted
12. `test_first_name_hyphen_apostrophe` - "Anna-Marie O'Brien" accepted
13. `test_email_format` - Invalid format rejected
14. `test_party_size_range_1_to_10` - 0 rejected, 1 accepted, 10 accepted, 11 rejected
15. `test_party_size_integer_only` - 3.5 rejected
16. `test_description_optional` - Empty accepted
17. `test_description_max_500_chars` - 500 accepted, 501 rejected
18. `test_description_blocks_http` - "http://example.com" rejected
19. `test_description_blocks_https` - "https://example.com" rejected
20. `test_description_blocks_www` - "Check www.example.com" rejected
21. `test_description_blocks_mailto` - "Email: mailto:test@test.com" rejected
22. `test_description_allows_newlines` - Newlines in description accepted
23. `test_description_allows_emoji` - Emoji in description accepted

**Date Tests (BR-001):**
24. `test_same_day_booking_valid` - start=end → 1 day, accepted
25. `test_date_range_inclusive` - Jan 1–5 = 5 days (not 4)
26. `test_end_date_before_start_rejected` - "Ende darf nicht vor dem Start liegen."
27. `test_past_dates_disabled_in_picker` - Cannot select before today
28. `test_month_boundary_dates` - Jan 31–Feb 1 → 2 days calculated correctly
29. `test_year_boundary_dates` - Dec 31–Jan 1 → 2 days calculated correctly
30. `test_multi_month_dates` - Jan 15–Mar 15 → 60 days, triggers long-stay

**Future Horizon (BR-026):**
31. `test_future_horizon_accepted` - +17 months accepted
32. `test_future_horizon_boundary_18_months` - +18 months accepted
33. `test_future_horizon_exceeded` - +19 months rejected

**Long Stay Confirmation (BR-027):**
34. `test_long_stay_threshold_7_days` - 7 days = no dialog, 8 days = dialog
35. `test_long_stay_dialog_cancel` - User cancels, form remains open
36. `test_long_stay_dialog_confirm` - User confirms, submission proceeds

**Conflict Detection (BR-002):**
37. `test_conflict_with_pending_booking` - Error dialog shows conflicting booking
38. `test_conflict_with_confirmed_booking` - Same error dialog
39. `test_no_conflict_adjacent_dates` - Jan 1–5 and Jan 6–10 allowed
40. `test_error_shows_first_name_and_status` - "überschneidet sich mit... (Anna – Ausstehend)"
41. `test_adjust_dates_and_resubmit` - User adjusts, resubmits, succeeds

**Success Flow:**
42. `test_booking_submitted_success_message` - "Anfrage gesendet. Du erhältst E-Mails..."
43. `test_booking_submitted_redirect_to_details` - Redirects to booking details

**Mobile/Accessibility (BR-011):**
44. `test_all_labels_german` - No English visible
45. `test_tap_targets_44px_minimum` - Measured on 375px viewport
46. `test_form_responsive_375px_viewport` - No horizontal scroll

**Estimated: 46 tests**

---

### US-6.2: Date Picker

**Scope:** Interactive calendar component for selecting start/end dates with conflict visualization

#### Applicable Business Rules

| BR | Description | Implementation Impact | Criticality |
|:---|:-----------|:---------------------|:-----------|
| **BR-001** | Inclusive end date semantics | Date picker must allow end = start; label/display must reflect inclusive range; range calculation must add 1 day | 🔴 Critical |
| **BR-002** | Show blocked dates (Pending/Confirmed) | Picker must visually disable/gray out conflicting dates; tooltip or indicator on blocked dates; cannot select through blocks | 🔴 Critical |
| **BR-014** | Past dates are read-only | Date picker must disable all dates < today | 🟠 High |
| **BR-026** | Future horizon check | Disable dates > today + 18 months (configurable) | 🟠 High |

#### Implementation Details

**Date Picker Component:**
```
Interactions:
  - Click "Startdatum" or "Enddatum" field → calendar popup appears
  - Calendar shows month view, week starts Monday (per spec)
  - Navigate months: arrows, swipe (mobile)
  - Click date: selected, format shown as "DD.MM.YYYY" (e.g., "01.08.2025")

Visual States:
  - Past dates (< today): disabled (gray, unclickable)
  - Future dates (> today + 18 months): disabled
  - Free dates: enabled (clickable)
  - Blocked dates (Pending/Confirmed bookings): disabled with visual indicator
  - Selected date: highlighted
  - Date range (after selecting start + end): highlighted in between

Display Format:
  - Input shows "DD.MM.YYYY" (e.g., "01.08.2025")
  - Range display shows "DD.–DD.MM.YYYY" (e.g., "01.–05.08.2025")
  - TotalDays calculation visible if both dates selected

Conflict Indicators:
  - Red/orange background on blocked date
  - Tooltip on hover/focus: "Besetzt (Anna – Ausstehend)" or similar
  - Cannot start drag/selection on blocked date
  - Drag stops at blocker (cannot cross)
```

**German Copy:**
- Date format in display: "01.–05.08.2025" (per spec)
- Blocked date label: not explicitly specified; suggest "Besetzt" or similar
- "Heute" button (jump to current date)

#### Edge Cases to Test (Playwright)

**Date Range Selection:**
1. Same day selection (start = end) → 1 day, not rejected
2. Forward selection (start before end) → correctly highlighted
3. Backward selection (user selects end before start) → resets or prompts
4. Multi-month selection → both months visible in range

**Blocked Dates:**
5. Start on free date, end on blocked date → error or auto-adjust
6. Start on blocked date → cannot select (disabled)
7. Multi-month booking shown as blocked → entire range disabled
8. Overlap with Pending and Confirmed → both shown as blocked
9. Overlap with Denied (should be free) → not shown as blocked
10. Adjacent to blocked dates → start/end on day before/after allowed

**Past/Future Boundaries:**
11. Today's date is selectable
12. Yesterday is disabled
13. 18 months out is selectable
14. 18 months + 1 day is disabled
15. Visual indicator for "today" (e.g., circle, highlight)

**UI Interactions:**
16. Month navigation forward/backward works
17. "Heute" button jumps to current month
18. Keyboard navigation (arrows) works on desktop
19. Mobile: swipe to change months
20. Select date → input field updates immediately
21. Close picker (click outside, ESC) → selection preserved

**Date Format Display:**
22. Selected date shows "DD.MM.YYYY" format
23. Date range shows "DD.–DD.MM.YYYY" format
24. Non-German locale (browser) still displays German format
25. Typing directly into date field (if allowed) accepts "01.08.2025"

**Concurrency (Blocked Dates):**
26. While user has picker open, another user books same dates → picker must refresh/warn
27. Dates update in real-time if API polling/WebSocket in place

#### Test Matrix - US-6.2

**Happy Path:**
1. `test_click_start_date_opens_picker` - Calendar popup appears
2. `test_select_start_date_populates_field` - "DD.MM.YYYY" format shown
3. `test_select_end_date_populates_field` - Same format
4. `test_range_displayed_as_dd_dd_mm_yyyy` - "01.–05.08.2025"

**Date Range Logic (BR-001):**
5. `test_same_day_booking_allowed` - start = end = 1 day
6. `test_inclusive_end_date_calculation` - 5 days (not 4) for Jan 1–5

**Past Date Blocking (BR-014):**
7. `test_past_dates_disabled` - Before today grayed out
8. `test_today_is_selectable` - Today's date clickable
9. `test_yesterday_disabled` - Yesterday grayed out

**Future Horizon (BR-026):**
10. `test_18_months_future_selectable` - Today + 18 months clickable
11. `test_19_months_future_disabled` - Today + 19 months grayed out

**Blocked Dates (BR-002):**
12. `test_pending_booking_shown_blocked` - Dates grayed, unclickable
13. `test_confirmed_booking_shown_blocked` - Same blocking
14. `test_denied_booking_not_blocked` - Free dates remain clickable
15. `test_blocked_date_tooltip` - Hover shows conflict info
16. `test_cannot_start_on_blocked_date` - Start date picker rejects
17. `test_cannot_select_through_block` - Drag stops at blocked date
18. `test_multi_month_booking_blocked` - Entire range shown as blocked

**Date Range Selection:**
19. `test_select_forward_range` - start < end works
20. `test_same_month_range` - Both dates in August selectable
21. `test_cross_month_range` - July 25–August 5 works
22. `test_cross_year_range` - Dec 25–Jan 5 works

**UI/UX:**
23. `test_close_picker_on_esc_key` - Keyboard close works
24. `test_close_picker_click_outside` - Click outside closes picker
25. `test_selection_preserved_after_close` - Dates remain selected
26. `test_navigate_months_with_arrows` - Forward/backward navigation
27. `test_hoje_button_jumps_to_today` - "Heute" button works
28. `test_month_swipe_on_mobile` - Swipe gesture changes month
29. `test_keyboard_arrow_navigation` - Desktop arrow key navigation

**German Format:**
30. `test_date_format_is_german_locale` - DD.MM.YYYY (not MM/DD/YYYY)
31. `test_week_starts_monday` - Calendar layout per German convention

**Mobile Accessibility:**
32. `test_date_picker_responsive_375px` - Works on narrow viewport
33. `test_tap_dates_44px_minimum` - Date cells large enough

**Estimated: 33 tests**

---

### US-6.3: Edit Booking

**Scope:** Requester edits Pending/Denied booking with approval impact based on change type

#### Applicable Business Rules

| BR | Description | Implementation Impact | Criticality |
|:---|:-----------|:---------------------|:-----------|
| **BR-001** | Inclusive end date in edited range | Edit form uses same date logic; TotalDays = End - Start + 1 | 🔴 Critical |
| **BR-002** | Edited dates cannot conflict with Pending/Confirmed | Validation same as create; show conflict error; user adjusts | 🔴 Critical |
| **BR-005** | Edit impact on approvals: **Shorten = keep approvals; Extend = reset approvals** | Detect change type; if extend (earlier start OR later end) → approvals reset; if shorten → keep; if party size/affiliation/first name only → keep | 🔴 Critical |
| **BR-014** | Past bookings are read-only | If EndDate < today, show read-only view, no edit button | 🟠 High |
| **BR-018** | Reopen guard (reopening Denied): no conflicts allowed | When reopening denied booking from edit form, check new dates against Pending/Confirmed | 🟠 High |
| **BR-025** | First-name edit allowed anytime, no approval reset | Editing first name alone does not reset approvals | 🟡 Medium |
| **BR-026** | Future horizon check on edited start date | Edited start date must still be ≤ today + 18 months | 🟠 High |
| **BR-027** | Long stay confirmation on edited dates | If edited TotalDays > 7, show confirmation dialog | 🟠 High |

#### Implementation Details

**Edit Form Pre-population:**
```
When opening edit form:
  - Fetch booking details (ID from URL token)
  - Pre-populate all fields with current values:
    - Requester First Name
    - Email (IMMUTABLE, shown but disabled/hidden)
    - Start Date
    - End Date
    - Party Size
    - Affiliation
    - Description
  - Calculate current TotalDays
  - Show current status and approval progress (visual only, not editable)
```

**Change Detection Logic:**
```
On form submit:
  1. Compare new values against original
  2. Identify change type:
     - DATE_SHORTENED (start is later OR end is earlier, but within original bounds)
     - DATE_EXTENDED (start is earlier OR end is later, beyond original bounds)
     - PARTY_SIZE_ONLY (dates unchanged, party size changed)
     - AFFILIATION_ONLY (dates unchanged, affiliation changed)
     - FIRST_NAME_ONLY (dates unchanged, first name changed)
     - DESCRIPTION_ONLY (dates unchanged, description changed)
     - COMBINATION (multiple changes including dates)

  3. Based on change type:
     - If DATE_EXTENDED → approvals must reset to NoResponse
     - Otherwise → keep approvals unchanged
     - First name edit alone never resets approvals (per BR-025)

  4. Conflict check:
     - Check new date range against Pending/Confirmed
     - Show conflict error if found (same dialog as create form)

  5. Long stay confirmation:
     - If new TotalDays > 7 and > old TotalDays, show dialog

  6. Submit to API with:
     - Changed fields
     - Change type (helps backend decide approval handling)
```

**German Copy:**
- Same field errors as create form
- Same conflict error as create form
- Same success message structure (e.g., "Buchung aktualisiert...")
- Reopen flow uses edit form with "Wieder eröffnen" button → transitions to Pending

#### Edge Cases to Test (Playwright)

**Shortening Dates (keep approvals):**
1. Original: Jan 1–10, shorten to Jan 3–8 → approvals unchanged
2. Original: Jan 1–10, shorten to Jan 1–5 → approvals unchanged
3. Original: Jan 1–10, shorten to Jan 1–1 (1 day) → approvals unchanged
4. Short within bounds but new range still conflicts → error

**Extending Dates (reset approvals):**
5. Original: Jan 1–10, extend to Dec 31–Jan 15 → approvals reset
6. Original: Jan 1–10, extend start earlier (Dec 25–10) → approvals reset
7. Original: Jan 1–10, extend end later (Jan 1–20) → approvals reset
8. Extend both directions → approvals reset

**Non-Date Changes (keep approvals):**
9. Party size only (5→6) → approvals unchanged
10. Affiliation only (Ingeborg→Cornelia) → approvals unchanged
11. First name only ("Anna"→"Anne") → approvals unchanged per BR-025
12. Description only → approvals unchanged
13. Multiple non-date changes → approvals unchanged

**Combination Changes:**
14. Dates + party size → approvals follow date change rules
15. Dates (shortened) + description → approvals kept
16. Dates (extended) + party size → approvals reset (date change dominates)

**Immutable Email:**
17. Email field disabled/hidden (cannot edit)
18. Submitting form does not change email

**Past Booking Read-Only:**
19. EndDate < today → "Dieses Feld wird nicht mehr geändert" banner
20. No edit button visible on past booking details
21. If URL somehow allows edit form, API rejects with error

**Reopen from Denied (BR-018):**
22. Reopen with same dates but now a conflict exists → error "überschneidet sich..."
23. Reopen and adjust dates to avoid conflict → allowed
24. Reopen form pre-populated with previous dates

**Conflict During Edit:**
25. Dates shortened to free range → accepted
26. Dates extended into another booking → error
27. Another user books while edit form open → conflict detected on submit

**Long Stay on Edit:**
28. Original 3 days, extend to 10 days → long stay dialog shown
29. Original 10 days, shorten to 6 days → no long stay dialog
30. Original 10 days, stay 10 days → no dialog (no change)

**Approval Reset Notification:**
31. After extend + submit, user sees message (in success or timeline) that approvals reset
32. Re-approval emails sent to all approvers (backend, but frontend shows this info)

#### Test Matrix - US-6.3

**Happy Path:**
1. `test_edit_form_opens_with_prefilled_data` - All fields populated
2. `test_edit_party_size_and_submit` - Change 5→6, success message

**Date Shortening Tests (BR-005 - Keep Approvals):**
3. `test_shorten_start_date_keeps_approvals` - Jan 1–10 → Jan 3–10
4. `test_shorten_end_date_keeps_approvals` - Jan 1–10 → Jan 1–5
5. `test_shorten_both_boundaries_keeps_approvals` - Jan 1–10 → Jan 3–8

**Date Extending Tests (BR-005 - Reset Approvals):**
6. `test_extend_start_earlier_resets_approvals` - Dec 25–Jan 10
7. `test_extend_end_later_resets_approvals` - Jan 1–20
8. `test_extend_both_resets_approvals` - Dec 25–Jan 20

**Non-Date Changes (BR-005, BR-025 - Keep Approvals):**
9. `test_change_party_size_keeps_approvals` - Approval state unchanged
10. `test_change_affiliation_keeps_approvals` - Approval state unchanged
11. `test_change_first_name_keeps_approvals` - Per BR-025
12. `test_change_description_keeps_approvals` - Not logged in timeline
13. `test_multiple_non_date_changes_keep_approvals` - Party + affiliation + description

**Immutable Email (BR-002 context):**
14. `test_email_field_disabled` - Cannot edit email
15. `test_email_not_changed_on_submit` - Original email persists

**Past Booking (BR-014):**
16. `test_past_booking_read_only_banner` - "Dieser Eintrag liegt in der Vergangenheit..."
17. `test_past_booking_no_edit_button` - Edit button not visible
18. `test_edit_past_booking_api_rejects` - If form somehow allows, API blocks

**Conflict Validation (BR-002):**
19. `test_edit_creates_conflict` - Extend into another booking → error
20. `test_edit_resolves_conflict_by_shortening` - Adjust dates, resubmit, succeeds
21. `test_conflict_error_shows_first_name_status` - Same error format as create

**Long Stay Confirmation (BR-027):**
22. `test_extend_to_8_days_shows_dialog` - Original 3→10 days
23. `test_extend_within_long_stay_no_dialog` - Original 10→12 days (both >7)
24. `test_cancel_long_stay_dialog_keeps_form_open` - User cancels, data preserved
25. `test_confirm_long_stay_proceeds_to_submit` - Submission continues

**Future Horizon (BR-026):**
26. `test_edit_date_beyond_18_months_rejected` - Extended start date too far

**Date Logic (BR-001):**
27. `test_edit_same_day_valid` - Change to start = end

**Reopen from Denied (BR-018):**
28. `test_reopen_denied_booking_with_same_dates` - Works if no new conflicts
29. `test_reopen_denied_booking_conflict_error` - New conflicts reject
30. `test_reopen_denied_booking_adjust_dates` - User adjusts, resubmit succeeds
31. `test_reopen_transitions_to_pending` - Status changes, approvals reset

**Approval Reset Messaging:**
32. `test_extend_shows_approval_reset_message` - Success message/timeline shows reset
33. `test_re_approval_emails_sent_on_extend` - Backend verification in integration test

**Mobile/Accessibility:**
34. `test_edit_form_responsive_375px` - Mobile viewport
35. `test_edit_form_german_labels` - No English
36. `test_edit_form_tap_targets_44px` - Touch-friendly

**Estimated: 36 tests**

---

## Cross-Cutting Concerns

### Mobile-First Design (BR-011 context)

**Applies to all three user stories:**
- Minimum viewport: 375×667px (iPhone 8)
- All tap targets: ≥44×44pt
- No hover dependencies
- Responsive form layout
- Touch-friendly date picker (large calendar cells)
- Full-width buttons
- Readable text on small screens

**Tests (consolidated):**
- Form renders correctly on 375px viewport
- Date picker large enough for touch on mobile
- No horizontal scroll
- All buttons/links 44×44pt minimum

### German-Only UI (BR-011)

**Applied throughout:**
- All labels, placeholders, errors, buttons in German
- No English fallback or technical terms
- Informal "du" tone consistently
- Exact copy from specifications

**Error Message Tests:**
- Every error message matches spec exactly (no paraphrasing)
- All validation errors in German
- Success messages in German

### Privacy (BR constraints)

**No changes to Phase 6, but remember:**
- Email never displayed in form UI
- Only first name shown
- Form doesn't expose PII

---

## Consolidated Test Matrix Summary

| User Story | Test Count | Focus Areas |
|:-----------|:----------|:-----------|
| **US-6.1: Create Form** | 46 | Validation, conflicts, long-stay, dates, party size, name, description, links |
| **US-6.2: Date Picker** | 33 | Date range, blocked dates, future horizon, UI, formatting, mobile |
| **US-6.3: Edit Booking** | 36 | Approval impact, date changes, immutability, conflicts, reopen, past read-only |
| **Subtotal** | **115** | — |
| **Consolidated (deduped)** | **38–42** | High-level E2E flows that naturally cover multiple stories |

### Recommended Deduplicated Approach

Rather than 115 granular tests, consolidate to ~40 comprehensive E2E Playwright tests:

1. **Form Creation Tests (10–12):**
   - Happy path (valid submission)
   - All field-level validations
   - Conflict detection + retry
   - Long stay confirmation
   - Mobile responsive

2. **Date Picker Tests (8–10):**
   - Selection and formatting
   - Blocked date visualization
   - Past/future boundaries
   - Month navigation
   - Keyboard/swipe on mobile

3. **Edit Booking Tests (10–12):**
   - Prefill and submit (no changes)
   - Date extension (approval reset)
   - Date shortening (approvals keep)
   - Non-date changes
   - Past booking read-only
   - Reopen from denied

4. **Error & Edge Case Tests (8–10):**
   - Invalid inputs (all field types)
   - Concurrent conflicts
   - Email immutability
   - German copy validation

5. **Mobile/Accessibility Tests (4–6):**
   - Viewport testing (375px)
   - Touch target sizing
   - No horizontal scroll
   - Keyboard navigation

---

## Implementation Checklist

**Before writing any code:**

- [ ] Read all BRs (BR-001, 002, 005, 011, 014–027) thoroughly
- [ ] Identify all German copy sources (error-handling.md, ui-screens.md)
- [ ] Map form fields to data model constraints (max lengths, validation rules)
- [ ] Design date picker blocking/disabled state logic
- [ ] Define approval reset detection algorithm (date extend vs. other changes)
- [ ] Plan Playwright test scenarios (40–42 E2E tests)

**Development workflow:**

1. Write all Playwright test specs (failing tests)
2. Implement form components (Shadcn, React Hook Form, Zod)
3. Implement date picker (Shadcn Calendar or similar)
4. Implement API integration and error handling
5. Verify all tests pass
6. Mobile testing (375px viewport)
7. German copy verification against specs

---

## German Copy Reference Sheet

**All copy sourced from specification documents:**

| Error/Message | German Copy | Source |
|:---|:---|:---|
| First name required | "Dieses Feld wird benötigt." | error-handling.md line 460 |
| First name invalid | "Bitte gib einen gültigen Vornamen an (Buchstaben, Leerzeichen, Bindestrich, Apostroph; max. 40 Zeichen)." | error-handling.md line 110–111 |
| Email required | "Dieses Feld wird benötigt." | error-handling.md line 460 |
| Email invalid | "Bitte gib eine gültige E-Mail-Adresse an." | error-handling.md line 79 |
| Party size invalid | "Teilnehmerzahl muss zwischen 1 und {{MAX}} liegen." | error-handling.md line 124 |
| Party size not integer | "Bitte gib eine ganze Zahl ein." | error-handling.md line 146 |
| Date conflict | "Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung ({{Vorname}} – {{Status}})." | error-handling.md line 17 |
| End before start | "Ende darf nicht vor dem Start liegen." | error-handling.md line 63 |
| Future horizon exceeded | "Anfragen dürfen nur maximal {{MONTHS}} Monate im Voraus gestellt werden." | error-handling.md line 42 |
| Description/comment too long | "Text ist zu lang (max. 500 Zeichen)." | error-handling.md line 160 |
| Links not allowed | "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden." | error-handling.md line 175 |
| Success submitted | "Anfrage gesendet. Du erhältst E-Mails, sobald entschieden wurde." | error-handling.md line 211 |
| Long stay dialog title | "Langer Aufenthalt" | error-handling.md line 529 (suggested) |
| Long stay dialog body | "Diese Anfrage umfasst {{TotalDays}} Tage. Möchtest du fortfahren?" | error-handling.md line 530 (suggested) |
| Long stay buttons | "Abbrechen" / "Bestätigen" | error-handling.md line 531 |
| Past item read-only | "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden." | error-handling.md line 193 |
| Button "Neue Anfrage" | "Neue Anfrage" | ui-screens.md line 326 |
| Button "Bearbeiten" | "Bearbeiten" | ui-screens.md line 172 |
| Button "Wieder eröffnen" | "Wieder eröffnen" | ui-screens.md line 187 |

---

## Next Steps

1. **Prioritize test writing** - Write all 40–42 Playwright E2E tests FIRST
2. **Implement components** - Form, date picker, edit flow
3. **Integrate with Phase 5 API** - Use endpoints from Phase 2 (create/update booking)
4. **Manual mobile testing** - 375px viewport, touch interactions
5. **German copy audit** - Verify every string matches spec exactly
6. **Concurrent testing** - Simulate race conditions (two users booking same dates)

---

**This analysis ensures Phase 6 implementation covers all 13 applicable business rules, delivers accurate German copy, handles 40+ edge cases, and passes 40–42 comprehensive Playwright E2E tests.**
