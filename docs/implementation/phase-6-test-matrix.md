# Phase 6: Web Booking - Consolidated Test Matrix

## Executive Test Summary

**Total Recommended Playwright E2E Tests: 40–42**

These consolidated tests cover all three user stories (US-6.1, US-6.2, US-6.3) with deduplication to avoid repetitive coverage.

---

## Test Matrix by Category

### GROUP 1: Form Creation & Submission (10 tests)

| # | Test Name | Covers | BRs | Status |
|:--|:----------|:-------|:--:|:----:|
| 1 | `test_create_form_opens_and_closes` | US-6.1: Open form dialog | BR-011 | Pending |
| 2 | `test_create_form_submit_all_fields_valid` | US-6.1: Happy path submission | BR-001, 016 | Pending |
| 3 | `test_create_form_required_fields_validation` | US-6.1: All required fields error | BR-011 | Pending |
| 4 | `test_create_form_first_name_invalid_chars` | US-6.1: Name validation | BR-019 | Pending |
| 5 | `test_create_form_first_name_max_40_chars` | US-6.1: Name length boundary | BR-019 | Pending |
| 6 | `test_create_form_email_format_validation` | US-6.1: Email validation | BR-011 | Pending |
| 7 | `test_create_form_party_size_range_1_to_10` | US-6.1: Party size range | BR-017 | Pending |
| 8 | `test_create_form_description_no_links` | US-6.1: Block URLs | BR-020 | Pending |
| 9 | `test_create_form_description_max_500_chars` | US-6.1: Text length | BR-020 | Pending |
| 10 | `test_create_form_success_message_and_redirect` | US-6.1: Success flow | BR-011 | Pending |

### GROUP 2: Date Picker & Range Logic (10 tests)

| # | Test Name | Covers | BRs | Status |
|:--|:----------|:-------|:--:|:----:|
| 11 | `test_date_picker_opens_on_field_click` | US-6.2: Open calendar | BR-001 | Pending |
| 12 | `test_date_picker_select_range_dd_mm_yyyy_format` | US-6.2: Format display | BR-001 | Pending |
| 13 | `test_date_picker_inclusive_end_date_logic` | US-6.2: BR-001 semantics | BR-001 | Pending |
| 14 | `test_date_picker_same_day_booking_valid` | US-6.2: start = end | BR-001 | Pending |
| 15 | `test_date_picker_past_dates_disabled` | US-6.2: Cannot select before today | BR-014 | Pending |
| 16 | `test_date_picker_future_horizon_18_months` | US-6.2: Boundary at +18 months | BR-026 | Pending |
| 17 | `test_date_picker_future_horizon_19_months_disabled` | US-6.2: Reject >18 months | BR-026 | Pending |
| 18 | `test_date_picker_month_navigation_arrows` | US-6.2: UI navigation | BR-011 | Pending |
| 19 | `test_date_picker_heute_button_jumps_today` | US-6.2: "Heute" functionality | BR-011 | Pending |
| 20 | `test_date_picker_blocked_dates_visualization` | US-6.2: Show conflict blocking | BR-002 | Pending |

### GROUP 3: Conflict Detection & Error Handling (8 tests)

| # | Test Name | Covers | BRs | Status |
|:--|:----------|:-------|:--:|:----:|
| 21 | `test_conflict_overlap_pending_booking_error` | US-6.1, 6.3: Conflict detection | BR-002 | Pending |
| 22 | `test_conflict_overlap_confirmed_booking_error` | US-6.1, 6.3: Conflict detection | BR-002 | Pending |
| 23 | `test_conflict_error_shows_first_name_status` | US-6.1, 6.3: Error format | BR-002 | Pending |
| 24 | `test_conflict_no_error_adjacent_dates` | US-6.1, 6.3: Adjacent allowed | BR-002 | Pending |
| 25 | `test_conflict_user_adjusts_dates_resubmits` | US-6.1, 6.3: User can retry | BR-002 | Pending |
| 26 | `test_end_date_before_start_error` | US-6.1, 6.3: Date validation | BR-001 | Pending |
| 27 | `test_long_stay_confirmation_7_day_threshold` | US-6.1, 6.3: Long stay dialog | BR-027 | Pending |
| 28 | `test_long_stay_dialog_cancel_preserves_form` | US-6.1, 6.3: Dialog interaction | BR-027 | Pending |

### GROUP 4: Edit Booking - Approval Impact (8 tests)

| # | Test Name | Covers | BRs | Status |
|:--|:----------|:-------|:--:|:----:|
| 29 | `test_edit_form_prefilled_with_booking_data` | US-6.3: Form state | BR-001 | Pending |
| 30 | `test_edit_shorten_dates_keep_approvals` | US-6.3: Shortened range | BR-005 | Pending |
| 31 | `test_edit_extend_dates_reset_approvals` | US-6.3: Extended range | BR-005 | Pending |
| 32 | `test_edit_party_size_only_keep_approvals` | US-6.3: Non-date change | BR-005 | Pending |
| 33 | `test_edit_first_name_only_keep_approvals` | US-6.3: First name edit | BR-025 | Pending |
| 34 | `test_edit_affiliation_only_keep_approvals` | US-6.3: Non-date change | BR-005 | Pending |
| 35 | `test_edit_email_field_immutable` | US-6.3: Email cannot change | BR-data-model | Pending |
| 36 | `test_edit_past_booking_read_only_banner` | US-6.3: Past restriction | BR-014 | Pending |

### GROUP 5: Reopen from Denied (4 tests)

| # | Test Name | Covers | BRs | Status |
|:--|:----------|:-------|:--:|:----:|
| 37 | `test_reopen_denied_booking_same_dates_allowed` | US-6.3: Reopen flow | BR-018 | Pending |
| 38 | `test_reopen_denied_booking_conflict_error_forces_adjust` | US-6.3: Reopen guard | BR-018 | Pending |
| 39 | `test_reopen_denied_booking_adjust_dates_resubmit` | US-6.3: Reopen recovery | BR-018 | Pending |
| 40 | `test_reopen_transitions_to_pending_resets_approvals` | US-6.3: State transition | BR-005 | Pending |

### GROUP 6: Mobile & Accessibility (4 tests)

| # | Test Name | Covers | BRs | Status |
|:--|:----------|:-------|:--:|:----:|
| 41 | `test_form_responsive_375px_viewport` | All: Mobile design | BR-011 | Pending |
| 42 | `test_date_picker_touch_targets_44px_minimum` | US-6.2: Mobile usability | BR-011 | Pending |
| 43 | `test_german_copy_validation_all_errors` | All: Language | BR-011 | Pending |
| 44 | `test_no_hover_dependencies_mobile_interactions` | All: Mobile UI | BR-011 | Pending |

---

## Test-to-BR Traceability

### BR-001: Whole-Day Bookings, Inclusive End Date
- Tests: 2, 13, 14, 26
- Coverage: Date range calculation, same-day validity, end-before-start validation
- Example: Jan 1–5 = 5 days, not 4

### BR-002: No Overlaps with Pending/Confirmed
- Tests: 20, 21, 22, 23, 24, 25
- Coverage: Conflict detection, error display, user recovery
- Example: Overlapping booking shows error with first name + status

### BR-005: Edit Impact on Approvals
- Tests: 30, 31, 32, 33, 34, 40
- Coverage: Shorten (keep) vs. extend (reset) logic, non-date changes
- Example: Extend start date earlier → reset approvals

### BR-011: German-Only UI, Informal "du"
- Tests: 3, 6, 10, 19, 43, 44
- Coverage: All field labels, errors, success messages in German
- Example: "Bitte gib einen gültigen Vornamen an..."

### BR-014: Past Items Read-Only
- Tests: 15, 36
- Coverage: Cannot select past dates, past bookings not editable
- Example: EndDate < today → no edit button

### BR-016: Party Size "n Personen" Format
- Tests: 2, 7
- Coverage: Display format consistency
- Example: 1 person = "1 Personen" (not "1 Person")

### BR-017: Party Size Range 1–10
- Tests: 7
- Coverage: Boundary validation, error on invalid range
- Example: 0 or 11 rejected

### BR-018: Reopen Guard
- Tests: 37, 38, 39
- Coverage: Reopening denied booking with conflict detection
- Example: Cannot reopen if new dates conflict

### BR-019: First Name Validation
- Tests: 4, 5
- Coverage: Invalid chars, max length, trim
- Example: Emoji rejected, 41 chars rejected

### BR-020: Link Detection in Text Fields
- Tests: 8
- Coverage: Block http://, https://, www, mailto:
- Example: "Check www.example.com" rejected

### BR-025: First-Name Edit
- Tests: 33
- Coverage: First name alone does not reset approvals
- Example: Edit first name → approvals unchanged

### BR-026: Future Horizon
- Tests: 16, 17
- Coverage: Boundary at today + 18 months
- Example: +19 months disabled

### BR-027: Long Stay Confirmation
- Tests: 27, 28
- Coverage: Trigger at >7 days, dialog interaction
- Example: 8 days → show confirmation dialog

---

## Recommended Test Execution Order

**Phase 1: Core Functionality (High Priority)**
1. Tests 2, 10 (Happy path create)
2. Tests 13, 14 (Date picker core)
3. Tests 21, 22, 23 (Conflict detection)
4. Tests 29, 30, 31 (Edit impact)

**Phase 2: Validation (High Priority)**
5. Tests 3, 4, 5, 6, 7, 8, 9 (All validations)
6. Tests 11, 12, 15, 16, 17 (Date picker boundaries)

**Phase 3: Error Cases (Medium Priority)**
7. Tests 24, 25, 26, 27, 28 (Edge cases)
8. Tests 32, 33, 34, 35, 36 (Edit variants)

**Phase 4: Reopen Flow (Medium Priority)**
9. Tests 37, 38, 39, 40 (Reopen scenario)

**Phase 5: Polish (Lower Priority)**
10. Tests 41, 42, 43, 44 (Mobile, accessibility, German copy)

---

## Test Data Setup Requirements

**Before running tests, seed the database with:**

```sql
-- 3 Fixed Approvers
INSERT INTO approver_party (name, display_name, approver_email, personal_link_token)
VALUES
  ('Ingeborg', 'Ingeborg', 'ingeborg@example.com', 'token-ingeborg'),
  ('Cornelia', 'Cornelia', 'cornelia@example.com', 'token-cornelia'),
  ('Angelika', 'Angelika', 'angelika@example.com', 'token-angelika');

-- Existing Pending booking (for conflict tests)
INSERT INTO booking (booking_id, start_date, end_date, party_size, requester_first_name, requester_email, affiliation, status, created_at)
VALUES ('existing-pending-id', '2025-08-01', '2025-08-05', 4, 'Anna', 'anna@example.com', 'Ingeborg', 'Pending', NOW());

-- Existing Confirmed booking (for conflict tests)
INSERT INTO booking (booking_id, start_date, end_date, party_size, requester_first_name, requester_email, affiliation, status, created_at)
VALUES ('existing-confirmed-id', '2025-09-10', '2025-09-15', 3, 'Max', 'max@example.com', 'Cornelia', 'Confirmed', NOW());

-- Existing Denied booking (for reopen tests)
INSERT INTO booking (booking_id, start_date, end_date, party_size, requester_first_name, requester_email, affiliation, status, created_at)
VALUES ('existing-denied-id', '2025-10-01', '2025-10-05', 2, 'Test User', 'test@example.com', 'Angelika', 'Denied', NOW());
```

---

## Key Test Fixtures

### Form Submission Success Response
```json
{
  "id": "booking-id",
  "status": "Pending",
  "message": "Anfrage gesendet. Du erhältst E-Mails, sobald entschieden wurde.",
  "token": "user-token-xxxxx"
}
```

### Conflict Error Response
```json
{
  "error": {
    "code": "CONFLICT",
    "message": "Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung (Anna – Ausstehend).",
    "details": {
      "conflictingBooking": {
        "firstName": "Anna",
        "status": "Pending"
      }
    }
  }
}
```

### Edit Form Success Response
```json
{
  "id": "booking-id",
  "status": "Pending",
  "approvals_reset": true,
  "message": "Buchung aktualisiert.",
  "re_approval_emails_sent": true
}
```

---

## GitHub/CI Integration Checklist

- [ ] Create Playwright test file: `tests/e2e/booking-form.spec.ts`
- [ ] Configure test database seeding (migrations + seed script)
- [ ] Set up GitHub Actions workflow for CI (runs on PR)
- [ ] Configure headless browser (Chromium, Firefox, WebKit)
- [ ] Generate coverage report (aim for ≥80%)
- [ ] Mobile viewport testing (375×667px)
- [ ] Keyboard navigation testing (desktop)
- [ ] Screenshot comparison for UI changes
- [ ] Configure test timeout (30s per test)
- [ ] Parallel test execution (split by file)
- [ ] Report failed tests clearly (with screenshots)

---

## Deduplication Notes

**Why 40–42 instead of 115+:**

1. **Overlapping validations consolidated:**
   - Create + Edit forms share most validation logic
   - Single test covers both via form reuse

2. **Date picker logic centralized:**
   - Date picker component tested once
   - Used by create + edit forms
   - One test for functionality, one for each form context

3. **Conflict detection consolidated:**
   - Same logic in create + edit
   - Tested once with parametrization

4. **Approval logic focused:**
   - Only tested in edit (create always starts Pending)
   - Specifically tests extend vs. shorten distinction

5. **Error messages unified:**
   - German copy validation in one comprehensive test
   - Spot-checks in context of specific features

---

## Next Phase Integration

**Phase 7 (Approver Interface) will add:**
- Approver overview tests (Outstanding/History tabs)
- Approve/Deny action tests
- Weekly digest tests
- Permission enforcement tests

**Tests in Phase 6 should NOT:**
- Test approval actions (belong in Phase 7)
- Test weekly digest (backend, not UI)
- Test permission enforcement (backend validation)

---

**Total Effort: 40–42 comprehensive Playwright E2E tests = Full coverage of Phase 6 functionality with all 13 applicable BRs**
