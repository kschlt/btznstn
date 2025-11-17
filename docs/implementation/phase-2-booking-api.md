# Phase 2: Booking API

## Goal

Implement booking CRUD endpoints with validation and conflict detection.

**Duration:** 3-4 days | **Dependencies:** Phase 1

---

## 🚨 MANDATORY: Read Before Starting

**Before writing ANY code:**

1. ✅ Read `/docs/implementation/CLAUDE.md` - Strict TDD workflow (Steps 1-6)
2. ✅ Complete pre-implementation checklist (identify ALL BRs, edge cases, German copy)
3. ✅ Write ALL tests FIRST (must fail initially)
4. ✅ Implement code until tests pass
5. ✅ Self-review against checklist

**Phase 2 applies 20 business rules with ~142 tests across 4 user stories.**

---

## User Stories

### US-2.1: Create Booking Endpoint

**As a** requester
**I want** to submit a booking request via API
**So that** I can reserve dates at Betzenstein

---

**Applicable Business Rules:**

- **BR-001** (Inclusive end date): Calculate `total_days = (end_date - start_date) + 1`
  - *Why:* Jan 1-5 = 5 days, not 4. Off-by-one errors break everything.

- **BR-002** (No overlaps): Check conflicts with Pending/Confirmed bookings only
  - *Why:* Denied/Canceled bookings don't block dates. Must use GiST index for date range overlap.

- **BR-003** (Three approvers): Create 3 approval records (Ingeborg, Cornelia, Angelika) with decision=NoResponse
  - *Why:* Every booking requires exactly 3 approvals. No more, no less.

- **BR-011** (German-only UI): All error messages in German, informal "du" tone
  - *Why:* No English fallbacks. Exact copy from `docs/specification/error-handling.md`.

- **BR-012** (Rate limits): 10 bookings/day per email, 30 requests/hour per IP
  - *Why:* Prevent abuse. Must check BEFORE database operations.

- **BR-014** (Past items read-only): Cannot create booking with `end_date < today` (Europe/Berlin timezone)
  - *Why:* Validation prevents data corruption.

- **BR-015** (Self-approval): If `requester_email` matches approver email, auto-approve that party
  - *Why:* Ingeborg creating a booking auto-approves Ingeborg's approval (2 more needed).

- **BR-016** (Party size display): Format as "n Personen" (even for 1 person)
  - *Why:* Consistency. "1 Personen" not "1 Person".

- **BR-017** (Max party size): Validate `1 ≤ party_size ≤ 10`
  - *Why:* Business constraint. Return German error if violated.

- **BR-019** (First name validation): Letters, diacritics, space, hyphen, apostrophe; max 40 chars
  - *Why:* Prevent injection attacks, emojis, newlines. Trim whitespace.

- **BR-020** (Link detection): Block URLs in description field (http://, https://, www, mailto:)
  - *Why:* Prevent spam/phishing. Case-insensitive detection.

- **BR-026** (Future horizon): Cannot create booking with `start_date > today + 18 months`
  - *Why:* Configurable business constraint. Use Europe/Berlin timezone.

- **BR-027** (Long stay warning): Warn if `total_days > 7` (frontend confirmation)
  - *Why:* UX improvement. Backend accepts flag acknowledging warning.

- **BR-029** (First-write-wins): Concurrent booking creations serialize; first to persist wins
  - *Why:* Race condition handling. Use database transaction with conflict check inside.

- **Privacy** (Email never exposed): `requester_email` stored but NOT returned in public responses
  - *Why:* Privacy by design. Only requester (with token) sees their own email.

---

**German Copy Sources:**

- Conflict error: `docs/specification/error-handling.md` line 13
- Party size error: `docs/specification/error-handling.md` line 89
- First name error: `docs/specification/error-handling.md` line 234
- Link detection error: `docs/specification/error-handling.md` line 367
- Future horizon error: `docs/specification/error-handling.md` line 42
- Past date error: `docs/specification/error-handling.md` line 156
- Rate limit error: `docs/specification/error-handling.md` line 401

---

**Granular Acceptance Criteria:**

Schema/Type Safety:
- [ ] `BookingCreate` Pydantic schema validates all fields with exact types
- [ ] `BookingResponse` schema excludes `requester_email` (privacy)
- [ ] `total_days` calculated as `(end_date - start_date).days + 1` per BR-001
- [ ] Party size constrained to `conint(ge=1, le=10)` per BR-017

Business Logic:
- [ ] Conflict detection queries `status IN (Pending, Confirmed)` only per BR-002
- [ ] Conflict detection uses date range overlap: `start_date <= other.end_date AND end_date >= other.start_date`
- [ ] Multi-month bookings detected (Jan 15-Mar 15 conflicts with Feb 1-28)
- [ ] 3 approval records created with `decision=NoResponse` per BR-003
- [ ] Self-approval auto-applied if `requester_email == approver.email` per BR-015
- [ ] Rate limit checked BEFORE database insert per BR-012
- [ ] `end_date >= today` (Europe/Berlin) validation per BR-014
- [ ] `start_date <= today + 18 months` (Europe/Berlin) validation per BR-026
- [ ] Long stay flag accepted if `total_days > 7` and `long_stay_confirmed=true` per BR-027

Validation:
- [ ] First name regex: `^[A-Za-zÀ-ÿ\s'-]+$` with max 40 chars, trimmed per BR-019
- [ ] First name rejects emojis, newlines, special characters
- [ ] Description max 500 chars, blocks http://, https://, www, mailto: per BR-020
- [ ] Link detection is case-insensitive (HTTP://, WWW, MAILTO:)

Performance:
- [ ] Conflict detection uses GiST index on date range
- [ ] Transaction used for conflict check + insert (BR-029)
- [ ] No N+1 queries when creating approval records

German Copy:
- [ ] All error messages exact from `error-handling.md` (no paraphrasing)
- [ ] Informal "du" tone throughout
- [ ] Conflict error includes conflicting requester's first name and status

---

**Complete Test Plan:**

**Happy Path (2 tests):**
1. `test_create_booking_success` - Basic booking creation with all valid fields
2. `test_response_excludes_email` - Privacy: response does not include requester_email

**BR-001 (Inclusive End Date - 3 tests):**
3. `test_total_days_same_day` - Jan 1-1 = 1 day (not 0)
4. `test_total_days_multi_day` - Jan 1-5 = 5 days (not 4)
5. `test_total_days_leap_year` - Feb 28-29 in leap year = 2 days

**BR-002 (Conflict Detection - 8 tests):**
6. `test_conflict_exact_match` - Aug 1-5 conflicts with Aug 1-5
7. `test_conflict_partial_start` - Aug 3-8 conflicts with Aug 1-5
8. `test_conflict_partial_end` - Jul 28-Aug 2 conflicts with Aug 1-5
9. `test_conflict_enclosure` - Aug 2-4 conflicts with Aug 1-5
10. `test_conflict_multi_month` - Jan 15-Mar 15 conflicts with Feb 1-28 (CRITICAL edge case)
11. `test_no_conflict_denied` - Denied booking doesn't block dates
12. `test_no_conflict_canceled` - Canceled booking doesn't block dates
13. `test_conflict_returns_german_error` - Error message format correct

**BR-003 (Three Approvers - 4 tests):**
14. `test_three_approvals_created` - Exactly 3 approval records created
15. `test_approvals_no_response` - All approvals have decision=NoResponse
16. `test_approvals_decided_at_null` - All approvals have decided_at=NULL
17. `test_approvals_parties` - Ingeborg, Cornelia, Angelika present

**BR-015 (Self-Approval - 5 tests):**
18. `test_self_approval_ingeborg` - Ingeborg creates → Ingeborg approval auto-approved
19. `test_self_approval_cornelia` - Cornelia creates → Cornelia approval auto-approved
20. `test_self_approval_angelika` - Angelika creates → Angelika approval auto-approved
21. `test_no_self_approval_non_approver` - Non-approver creates → all 3 NoResponse
22. `test_self_approval_timeline_event` - Timeline event created for self-approval

**BR-017 (Party Size - 6 tests):**
23. `test_party_size_zero_fails` - party_size=0 rejected
24. `test_party_size_one_succeeds` - party_size=1 accepted
25. `test_party_size_ten_succeeds` - party_size=10 accepted (boundary)
26. `test_party_size_eleven_fails` - party_size=11 rejected
27. `test_party_size_negative_fails` - party_size=-1 rejected
28. `test_party_size_non_integer_fails` - party_size=3.5 rejected

**BR-019 (First Name Validation - 11 tests):**
29. `test_first_name_valid_simple` - "Anna" accepted
30. `test_first_name_hyphen` - "Marie-Claire" accepted
31. `test_first_name_apostrophe` - "O'Brien" accepted
32. `test_first_name_umlaut` - "Müller" accepted
33. `test_first_name_diacritic` - "José" accepted
34. `test_first_name_emoji_rejected` - "Anna 😊" rejected
35. `test_first_name_max_length` - "A" * 40 accepted
36. `test_first_name_too_long` - "A" * 41 rejected
37. `test_first_name_trimmed` - "  Anna  " trimmed to "Anna"
38. `test_first_name_empty_after_trim` - "   " rejected
39. `test_first_name_newline_rejected` - "Anna\nTest" rejected

**BR-020 (Link Detection - 6 tests):**
40. `test_description_no_links_succeeds` - "Family reunion" accepted
41. `test_description_https_rejected` - "Visit https://example.com" rejected
42. `test_description_http_rejected` - "Visit http://example.com" rejected
43. `test_description_www_rejected` - "Visit www.example.com" rejected
44. `test_description_mailto_rejected` - "Email mailto:test@example.com" rejected
45. `test_description_case_insensitive` - "HTTP://", "WWW", "MAILTO:" rejected

**BR-014 (Past Date - 3 tests):**
46. `test_end_date_today_succeeds` - Booking ending today accepted
47. `test_end_date_yesterday_fails` - Booking ending yesterday rejected
48. `test_end_date_timezone` - Timezone edge case (Europe/Berlin)

**BR-026 (Future Horizon - 4 tests):**
49. `test_start_17_months_succeeds` - Booking starting in 17 months accepted
50. `test_start_18_months_succeeds` - Booking starting in 18 months accepted (boundary)
51. `test_start_19_months_fails` - Booking starting in 19 months rejected
52. `test_future_horizon_timezone` - Timezone edge case (Europe/Berlin)

**BR-027 (Long Stay - 4 tests):**
53. `test_7_days_no_confirmation_succeeds` - 7-day booking succeeds without flag
54. `test_8_days_no_confirmation_returns_warning` - 8-day booking returns flag
55. `test_8_days_with_confirmation_succeeds` - 8-day booking with flag succeeds
56. `test_30_days_with_confirmation_succeeds` - 30-day booking with flag succeeds

**BR-012 (Rate Limiting - 5 tests):**
57. `test_rate_limit_email_10th_succeeds` - 10th booking from same email succeeds
58. `test_rate_limit_email_11th_fails` - 11th booking from same email rejected
59. `test_rate_limit_ip_30th_succeeds` - 30th request from same IP succeeds
60. `test_rate_limit_ip_31st_fails` - 31st request from same IP rejected
61. `test_rate_limit_resets` - Rate limit resets after time window

**BR-029 (Concurrency - 2 tests):**
62. `test_concurrent_creates_first_wins` - Two simultaneous POST requests, first wins
63. `test_concurrent_creates_second_gets_conflict` - Second gets 409 with details

**German Errors (1 test per validation):**
64. `test_german_error_messages` - All validation errors return correct German text

**TOTAL: ~64 tests for US-2.1**

---

**Gherkin Scenarios:**

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
    And the response should NOT include requester_email

  Scenario: BR-001 - Inclusive end date calculation
    Given I create a booking from 2025-01-01 to 2025-01-05
    Then total_days should be 5 (not 4)

  Scenario: BR-002 - Multi-month overlap detection (CRITICAL edge case)
    Given a booking exists from 2025-01-15 to 2025-03-15
    When I create a booking from 2025-02-01 to 2025-02-28
    Then I should receive status 409
    And the error should be "Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung ({{FirstName}} – Ausstehend)."

  Scenario: BR-002 - Denied bookings don't block dates
    Given a Denied booking exists from 2025-08-01 to 2025-08-05
    When I create a booking from 2025-08-01 to 2025-08-05
    Then I should receive status 201 (no conflict)

  Scenario: BR-015 - Self-approval when requester is approver
    Given I am Ingeborg (approver email: ingeborg@example.com)
    When I create a booking with requester_email = "ingeborg@example.com"
    Then 3 approval records should be created
    And Ingeborg's approval should have decision = Approved
    And Cornelia's and Angelika's approvals should have decision = NoResponse

  Scenario: BR-017 - Party size validation
    When I create a booking with party_size = 11
    Then I should receive status 400
    And the error should be "Teilnehmerzahl muss zwischen 1 und 10 liegen."

  Scenario: BR-019 - First name with emoji rejected
    When I create a booking with requester_first_name = "Anna 😊"
    Then I should receive status 400
    And the error should be "Bitte gib einen gültigen Vornamen an (Buchstaben, Leerzeichen, Bindestrich, Apostroph; max. 40 Zeichen)."

  Scenario: BR-020 - Description with URL rejected
    When I create a booking with description = "Visit https://example.com"
    Then I should receive status 400
    And the error should be "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden."

  Scenario: BR-026 - Future horizon exceeded
    When I create a booking starting 19 months in future
    Then I should receive status 400
    And the error should be "Anfragen dürfen nur maximal 18 Monate im Voraus gestellt werden."

  Scenario: BR-029 - Concurrent creation race condition
    Given two simultaneous POST requests for Aug 1-5
    When both requests hit the server at the same time
    Then one should receive status 201 (first to persist)
    And the other should receive status 409 (conflict)
```

---

**Implementation Tasks:**

- [ ] **FIRST:** Write ALL 64 tests (must fail initially)
- [ ] **Verify:** All tests fail (run `pytest tests/integration/test_create_booking.py -v`)
- [ ] Create Pydantic schemas (`BookingCreate`, `BookingResponse`)
- [ ] Implement `POST /api/v1/bookings` endpoint
- [ ] Add Pydantic validators for all fields (BR-017, BR-019, BR-020)
- [ ] Add custom validators for dates (BR-001, BR-014, BR-026)
- [ ] Implement conflict detection repository method (BR-002)
- [ ] Implement rate limiting middleware (BR-012)
- [ ] Create 3 approval records in transaction (BR-003)
- [ ] Check self-approval and auto-approve if match (BR-015)
- [ ] Generate tokens for requester + 3 approvers (BR-010 - Phase 4 will use)
- [ ] Return `BookingResponse` excluding email
- [ ] **Verify:** All tests pass (run `pytest tests/integration/test_create_booking.py -v`)
- [ ] Run `mypy app/` (type checking)
- [ ] Run `ruff check app/` (linting)
- [ ] **Self-review:** Complete Step 5 checklist from CLAUDE.md

---

### US-2.2: Get Booking Endpoint

**As a** visitor
**I want** to view booking details
**So that** I can see public information or my private details with a token

---

**Applicable Business Rules:**

- **BR-004** (Denial handling): Denied bookings hidden from public GET (return 404)
  - *Why:* Privacy. Only requester/approvers with token can view Denied bookings.

- **BR-010** (Tokens and links): Token validation for authenticated access
  - *Why:* Tokens never expire. Validate signature and structure.

- **BR-011** (German-only UI): Error messages in German
  - *Why:* 404, 401, 403 errors must be German.

- **BR-014** (Past items read-only): Include `is_past: bool` in response
  - *Why:* Calculated as `end_date < today` (Europe/Berlin). Frontend shows read-only banner.

- **Privacy** (Limited public view): Public GET returns limited fields only
  - *Why:* Hide `requester_email`, `description`, `approvals`, `timeline_events` from public.

---

**German Copy Sources:**

- 404 error: `docs/specification/error-handling.md` line 178
- 401 error: `docs/specification/error-handling.md` line 423
- 403 error: `docs/specification/error-handling.md` line 456

---

**Granular Acceptance Criteria:**

Public View (No Token):
- [ ] GET without token returns `PublicBookingResponse` schema
- [ ] Includes: `id`, `requester_first_name`, `start_date`, `end_date`, `party_size`, `status`, `affiliation`, `total_days`
- [ ] Excludes: `requester_email`, `description`, `approvals`, `timeline_events`
- [ ] Denied booking returns 404 per BR-004
- [ ] Canceled booking returns 404 (archived)
- [ ] Pending/Confirmed bookings return 200

Authenticated View (With Token):
- [ ] GET with valid requester token returns `FullBookingResponse`
- [ ] GET with valid approver token returns `FullBookingResponse`
- [ ] Includes all fields: `approvals`, `timeline_events`, `description`, `requester_email` (in token context)
- [ ] Denied booking accessible with valid token per BR-004
- [ ] Invalid token signature returns 401
- [ ] Token for different booking returns 403

Past Indicator:
- [ ] `is_past` calculated as `end_date < today` (Europe/Berlin) per BR-014
- [ ] Booking ending yesterday has `is_past=true`
- [ ] Booking ending today has `is_past=false`

German Copy:
- [ ] All error messages exact from `error-handling.md`

---

**Complete Test Plan:**

**Public View (6 tests):**
1. `test_get_public_pending_booking` - Public GET on Pending returns limited fields
2. `test_get_public_confirmed_booking` - Public GET on Confirmed returns limited fields
3. `test_get_public_denied_booking_404` - Public GET on Denied returns 404 per BR-004
4. `test_get_public_canceled_booking_404` - Public GET on Canceled returns 404
5. `test_get_public_excludes_email` - Response does not include requester_email
6. `test_get_public_excludes_description` - Response does not include description

**Authenticated View (5 tests):**
7. `test_get_with_requester_token` - Valid requester token returns full details
8. `test_get_with_approver_token` - Valid approver token returns full details
9. `test_get_denied_with_token` - Denied booking accessible with valid token
10. `test_get_invalid_token_401` - Invalid token signature returns 401
11. `test_get_wrong_booking_token_403` - Token for different booking returns 403

**Past Indicator (3 tests):**
12. `test_is_past_yesterday` - Booking ending yesterday has is_past=true
13. `test_is_past_today` - Booking ending today has is_past=false
14. `test_is_past_tomorrow` - Booking ending tomorrow has is_past=false

**German Errors (3 tests):**
15. `test_german_404` - 404 error message in German
16. `test_german_401` - 401 error message in German
17. `test_german_403` - 403 error message in German

**TOTAL: ~20 tests for US-2.2**

---

**Gherkin Scenarios:**

```gherkin
Feature: Get Booking

  Scenario: Public view (no token)
    Given a Pending booking exists
    When I GET /api/v1/bookings/{id} without token
    Then I should see limited fields:
      | field                |
      | requester_first_name |
      | start_date           |
      | end_date             |
      | party_size           |
      | status               |
    And I should NOT see:
      | field               |
      | requester_email     |
      | description         |
      | approvals           |

  Scenario: BR-004 - Denied booking hidden from public
    Given a Denied booking exists
    When I GET /api/v1/bookings/{id} without token
    Then I should receive status 404
    And the error should be in German

  Scenario: Requester view (with token)
    Given I am the requester
    When I GET /api/v1/bookings/{id}?token=xxx
    Then I should see all fields including:
      | field       |
      | approvals   |
      | timeline    |
      | description |

  Scenario: BR-014 - Past indicator
    Given a booking ending yesterday
    When I GET /api/v1/bookings/{id}
    Then is_past should be true
```

---

**Implementation Tasks:**

- [ ] **FIRST:** Write ALL 20 tests (must fail initially)
- [ ] **Verify:** All tests fail
- [ ] Create `PublicBookingResponse` Pydantic schema (limited fields)
- [ ] Create `FullBookingResponse` Pydantic schema (all fields)
- [ ] Implement `GET /api/v1/bookings/{id}` endpoint
- [ ] Check token presence/validity
- [ ] If no token and status=Denied/Canceled, return 404 per BR-004
- [ ] If token valid, return `FullBookingResponse`
- [ ] If no token, return `PublicBookingResponse`
- [ ] Calculate `is_past` using Europe/Berlin timezone per BR-014
- [ ] **Verify:** All tests pass
- [ ] Run `mypy app/` and `ruff check app/`
- [ ] **Self-review:** Step 5 checklist

---

### US-2.3: Update Booking Endpoint

**As a** requester
**I want** to edit my booking
**So that** I can change dates or details

---

**Applicable Business Rules:**

- **BR-001** (Inclusive end date): Recalculate `total_days` if dates change
- **BR-002** (No overlaps): Check conflicts excluding current booking
- **BR-005** (Edit approval impact): **CRITICAL LOGIC**
  - *Shorten dates (within original bounds):* Approvals remain unchanged
  - *Extend dates (earlier start OR later end):* All approvals reset to NoResponse
  - *Non-date changes (party size, affiliation, first name):* Approvals remain unchanged
- **BR-010** (Tokens): Validate requester token to authorize edit
- **BR-011** (German-only): Error messages in German
- **BR-012** (Rate limits): Edits count toward rate limit
- **BR-014** (Past items read-only): Cannot edit booking with `end_date < today`
- **BR-017** (Max party size): Validate new party_size
- **BR-019** (First name validation): Validate new requester_first_name
- **BR-020** (Link detection): Validate new description
- **BR-025** (First-name edit): First name edits do NOT reset approvals
- **BR-026** (Future horizon): Validate new start_date
- **BR-027** (Long stay warning): Validate if new total_days > 7
- **BR-029** (First-write-wins): Use optimistic locking for concurrent edits

---

**German Copy Sources:**

- Past edit error: `docs/specification/error-handling.md` line 156
- Conflict error: `docs/specification/error-handling.md` line 13
- All validation errors: Same as US-2.1

---

**Granular Acceptance Criteria:**

Authorization:
- [ ] Requester token validated per BR-010
- [ ] Token email must match `booking.requester_email`
- [ ] Invalid token returns 401
- [ ] Valid token for different requester returns 403

Date Recalculation:
- [ ] If start_date or end_date changed, recalculate `total_days = (end - start) + 1` per BR-001

Conflict Detection:
- [ ] Query conflicts WHERE `booking_id != current_id AND status IN (Pending, Confirmed)` per BR-002
- [ ] Return 409 if new dates conflict
- [ ] Self-overlap doesn't count (exclude current booking)

Approval Reset Logic (BR-005 - CRITICAL):
- [ ] **Shorten:** Original Jan 1-10 → New Jan 3-8 → Approvals KEEP
- [ ] **Extend start:** Original Jan 5-10 → New Jan 1-10 → Approvals RESET
- [ ] **Extend end:** Original Jan 1-5 → New Jan 1-10 → Approvals RESET
- [ ] **Extend both:** Original Jan 3-8 → New Jan 1-10 → Approvals RESET
- [ ] **Party size only:** Jan 1-5, 4 ppl → Jan 1-5, 6 ppl → Approvals KEEP
- [ ] **Affiliation only:** Approvals KEEP
- [ ] **First name only:** Approvals KEEP per BR-025 (special case)
- [ ] **Extend on Confirmed:** Approvals reset, status stays Confirmed

Timeline Events:
- [ ] Date edits logged with diff format: "01.–05.08. → 03.–08.08."
- [ ] First name edits NOT logged per BR-025

Validation:
- [ ] `end_date >= today` (Europe/Berlin) per BR-014
- [ ] Same validation as US-2.1 for all fields

Performance:
- [ ] Use SELECT FOR UPDATE or check `updated_at` for optimistic locking per BR-029

---

**Complete Test Plan:**

**Authorization (4 tests):**
1. `test_edit_with_valid_token` - Valid requester token allows edit
2. `test_edit_with_invalid_token_401` - Invalid token returns 401
3. `test_edit_with_wrong_requester_token_403` - Valid token for different requester returns 403
4. `test_edit_with_approver_token_403` - Approver token does not allow edit

**Date Recalculation (2 tests):**
5. `test_edit_dates_recalculates_total_days` - Jan 1-5 (5 days) → Jan 1-10 (10 days)
6. `test_shorten_dates_recalculates_total_days` - Jan 1-10 (10 days) → Jan 3-8 (6 days)

**Conflict Detection (4 tests):**
7. `test_edit_to_non_conflicting_dates` - No conflict, edit succeeds
8. `test_edit_to_conflicting_dates_409` - Conflict with another booking, edit fails
9. `test_edit_same_dates_succeeds` - No change to dates, edit succeeds
10. `test_self_overlap_excluded` - Current booking excluded from conflict check

**BR-005 Approval Reset Logic (8 tests):**
11. `test_shorten_keeps_approvals` - Jan 1-10 → Jan 3-8, approvals remain
12. `test_extend_start_resets_approvals` - Jan 5-10 → Jan 1-10, approvals reset
13. `test_extend_end_resets_approvals` - Jan 1-5 → Jan 1-10, approvals reset
14. `test_extend_both_resets_approvals` - Jan 3-8 → Jan 1-10, approvals reset
15. `test_party_size_only_keeps_approvals` - Party size 4 → 6, approvals remain
16. `test_affiliation_only_keeps_approvals` - Affiliation change, approvals remain
17. `test_first_name_only_keeps_approvals` - First name change, approvals remain per BR-025
18. `test_extend_on_confirmed_resets_approvals` - Confirmed booking extended, approvals reset

**Timeline Events (2 tests):**
19. `test_date_edit_creates_timeline_event` - Timeline event with diff format
20. `test_first_name_edit_no_timeline_event` - No timeline event per BR-025

**Past Items Read-Only (3 tests):**
21. `test_edit_past_booking_fails` - Booking ending yesterday cannot be edited
22. `test_edit_booking_ending_today_succeeds` - Booking ending today can be edited
23. `test_edit_booking_ending_tomorrow_succeeds` - Booking ending tomorrow can be edited

**Validation (6 tests):**
24. `test_edit_party_size_validation` - Same as US-2.1
25. `test_edit_first_name_validation` - Same as US-2.1
26. `test_edit_description_validation` - Same as US-2.1
27. `test_edit_future_horizon` - Same as US-2.1
28. `test_edit_long_stay_warning` - Same as US-2.1
29. `test_edit_past_date_validation` - Same as US-2.1

**Optimistic Locking (2 tests):**
30. `test_concurrent_edits_first_wins` - Two simultaneous PATCH requests, first wins
31. `test_concurrent_edits_second_gets_409` - Second gets 409 conflict

**German Errors (1 test):**
32. `test_edit_german_errors` - All error messages in German

**TOTAL: ~35 tests for US-2.3**

---

**Gherkin Scenarios:**

```gherkin
Feature: Update Booking

  Scenario: BR-005 - Shorten dates keeps approvals
    Given I am the requester of a Pending booking from Jan 1-10
    And two approvers have already approved
    When I PATCH /api/v1/bookings/{id}?token=xxx with:
      """json
      {"start_date": "2025-01-03", "end_date": "2025-01-08"}
      """
    Then the booking dates should update to Jan 3-8
    And all approvals should remain unchanged
    And no emails should be sent to approvers

  Scenario: BR-005 - Extend dates resets approvals
    Given I am the requester of a Pending booking from Jan 5-10
    And two approvers have already approved
    When I PATCH with start_date = "2025-01-01" (earlier start)
    Then all approvals should reset to NoResponse
    And approvers should be notified via email

  Scenario: BR-025 - First name edit keeps approvals
    Given I am the requester with approvals partially complete
    When I PATCH with:
      """json
      {"requester_first_name": "Anna-Marie"}
      """
    Then approvals should remain unchanged
    And no timeline event should be created

  Scenario: BR-014 - Cannot edit past booking
    Given a booking ending yesterday
    When I attempt to PATCH
    Then I should receive status 400
    And the error should be "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."
```

---

**Implementation Tasks:**

- [ ] **FIRST:** Write ALL 35 tests (must fail initially)
- [ ] **Verify:** All tests fail
- [ ] Create `BookingUpdate` Pydantic schema
- [ ] Implement `PATCH /api/v1/bookings/{id}` endpoint
- [ ] Validate requester token per BR-010
- [ ] Check `end_date >= today` per BR-014
- [ ] Implement shorten/extend detection logic per BR-005
- [ ] If extend: reset all approvals to NoResponse, send re-approval emails
- [ ] If shorten or non-date change: keep approvals unchanged
- [ ] Check conflicts excluding current booking per BR-002
- [ ] Recalculate total_days if dates changed per BR-001
- [ ] Create timeline event for date changes (not first name) per BR-025
- [ ] Use SELECT FOR UPDATE or optimistic locking per BR-029
- [ ] **Verify:** All tests pass
- [ ] Run `mypy app/` and `ruff check app/`
- [ ] **Self-review:** Step 5 checklist

---

### US-2.4: Cancel Booking Endpoint

**As a** requester
**I want** to cancel my booking
**So that** I can free up the dates

---

**Applicable Business Rules:**

- **BR-006** (Cancel Pending): Requester can cancel Pending booking; comment NOT required
  - *Why:* Status transitions Pending → Canceled → Archive. Notifications sent to 4 people.

- **BR-007** (Cancel Confirmed): Requester can cancel Confirmed booking; comment REQUIRED
  - *Why:* Warning dialog (frontend). Status transitions Confirmed → Canceled → Archive.

- **BR-010** (Tokens): Validate requester token
- **BR-011** (German-only): Error messages and result pages in German
- **BR-014** (Past items read-only): Cannot cancel booking with `end_date < today`
- **BR-020** (Link detection): Validate comment field (for Confirmed cancel)
- **State Validation**: Can only cancel Pending or Confirmed bookings

---

**German Copy Sources:**

- Comment required: `docs/specification/error-handling.md` line 289
- Link blocked: `docs/specification/error-handling.md` line 367
- Past date: `docs/specification/error-handling.md` line 156
- Success message: `docs/specification/notifications.md` line 456

---

**Granular Acceptance Criteria:**

Cancel Pending (BR-006):
- [ ] DELETE on Pending booking succeeds without comment
- [ ] DELETE on Pending booking succeeds with optional comment
- [ ] Status changes to Canceled
- [ ] Notifications sent to requester + 3 approvers (4 emails total)
- [ ] Result page shows "Anfrage storniert. Benachrichtigt: Ingeborg, Cornelia und Angelika."

Cancel Confirmed (BR-007):
- [ ] DELETE on Confirmed booking without comment returns 400
- [ ] Error message: "Bitte gib einen kurzen Grund an."
- [ ] DELETE on Confirmed booking with comment succeeds
- [ ] Status changes to Canceled
- [ ] Comment stored in timeline
- [ ] Notifications sent to requester + 3 approvers (4 emails total)

Authorization:
- [ ] Requester token validated per BR-010
- [ ] Invalid token returns 401
- [ ] Valid token for different requester returns 403
- [ ] Approver token does not allow cancel (403)

Past Items Read-Only:
- [ ] Cannot cancel booking with `end_date < today` per BR-014
- [ ] Booking ending yesterday returns 400
- [ ] Booking ending today can be canceled
- [ ] Booking ending tomorrow can be canceled

Comment Validation:
- [ ] Comment for Confirmed cancel validated per BR-020
- [ ] Links blocked (http://, https://, www, mailto:)

State Validation:
- [ ] Can cancel Pending → 200
- [ ] Can cancel Confirmed → 200
- [ ] Cannot cancel Denied → 400
- [ ] Cannot cancel already Canceled → 404

---

**Complete Test Plan:**

**Cancel Pending (4 tests):**
1. `test_cancel_pending_no_comment` - Cancel Pending without comment succeeds
2. `test_cancel_pending_with_comment` - Cancel Pending with comment succeeds
3. `test_cancel_pending_notifications` - 4 emails sent (requester + 3 approvers)
4. `test_cancel_pending_result_page` - Result page shows German message

**Cancel Confirmed (4 tests):**
5. `test_cancel_confirmed_no_comment_400` - Cancel Confirmed without comment fails
6. `test_cancel_confirmed_with_comment_succeeds` - Cancel Confirmed with comment succeeds
7. `test_cancel_confirmed_comment_in_timeline` - Comment stored in timeline
8. `test_cancel_confirmed_notifications` - 4 emails sent

**Authorization (4 tests):**
9. `test_cancel_with_valid_token` - Valid requester token allows cancel
10. `test_cancel_with_invalid_token_401` - Invalid token returns 401
11. `test_cancel_with_wrong_requester_token_403` - Valid token for different requester returns 403
12. `test_cancel_with_approver_token_403` - Approver token does not allow cancel

**Past Items Read-Only (3 tests):**
13. `test_cancel_past_booking_fails` - Booking ending yesterday cannot be canceled
14. `test_cancel_booking_ending_today_succeeds` - Booking ending today can be canceled
15. `test_cancel_booking_ending_tomorrow_succeeds` - Booking ending tomorrow can be canceled

**Comment Validation (3 tests):**
16. `test_cancel_comment_no_links` - "Can't make it" accepted
17. `test_cancel_comment_with_http_rejected` - "See http://example.com" rejected
18. `test_cancel_comment_case_insensitive` - "HTTP://", "WWW" rejected

**State Validation (4 tests):**
19. `test_cancel_pending_succeeds` - Pending → Canceled
20. `test_cancel_confirmed_succeeds` - Confirmed → Canceled
21. `test_cancel_denied_fails` - Denied cannot be canceled (400)
22. `test_cancel_already_canceled_404` - Already Canceled returns 404

**German Errors (3 tests):**
23. `test_cancel_german_comment_required` - "Bitte gib einen kurzen Grund an."
24. `test_cancel_german_link_blocked` - "Links sind hier nicht erlaubt..."
25. `test_cancel_german_success` - "Anfrage storniert. Benachrichtigt: ..."

**TOTAL: ~27 tests for US-2.4**

---

**Gherkin Scenarios:**

```gherkin
Feature: Cancel Booking

  Scenario: BR-006 - Cancel Pending without comment
    Given I am the requester of a Pending booking
    When I DELETE /api/v1/bookings/{id}?token=xxx
    Then status should change to Canceled
    And approvers should be notified (4 emails total)
    And I should see "Anfrage storniert. Benachrichtigt: Ingeborg, Cornelia und Angelika."

  Scenario: BR-007 - Cancel Confirmed requires comment
    Given I am the requester of a Confirmed booking
    When I DELETE without a comment
    Then I should receive status 400
    And the error should be "Bitte gib einen kurzen Grund an."
    When I DELETE with:
      """json
      {"comment": "Kann leider nicht kommen"}
      """
    Then status should change to Canceled
    And comment should be stored in timeline

  Scenario: BR-020 - Comment validation blocks URLs
    Given I am canceling a Confirmed booking
    When I provide comment = "See http://example.com for details"
    Then I should receive status 400
    And the error should be "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden."

  Scenario: BR-014 - Cannot cancel past booking
    Given a booking ending yesterday
    When I attempt to DELETE
    Then I should receive status 400
    And the error should be "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."
```

---

**Implementation Tasks:**

- [ ] **FIRST:** Write ALL 27 tests (must fail initially)
- [ ] **Verify:** All tests fail
- [ ] Create `BookingCancel` Pydantic schema (optional comment)
- [ ] Implement `DELETE /api/v1/bookings/{id}` endpoint
- [ ] Validate requester token per BR-010
- [ ] Check `end_date >= today` per BR-014
- [ ] If status=Pending: allow cancel without comment per BR-006
- [ ] If status=Confirmed: require comment per BR-007
- [ ] Validate comment for links per BR-020
- [ ] If status=Denied/Canceled: return 400/404
- [ ] Update status to Canceled
- [ ] Create timeline event with optional comment
- [ ] Send notifications to requester + 3 approvers (4 emails)
- [ ] Return result page with German message
- [ ] **Verify:** All tests pass
- [ ] Run `mypy app/` and `ruff check app/`
- [ ] **Self-review:** Step 5 checklist

---

## Definition of Done

**Complete this checklist before considering Phase 2 done:**

- [ ] **Pre-implementation checklist completed** for all 4 user stories
- [ ] **All ~142 tests written FIRST** (before implementation)
- [ ] All tests initially FAILED (confirmed)
- [ ] All tests now PASS
- [ ] Type checks pass: `python -m mypy app/` (no errors)
- [ ] Linting passes: `ruff check app/` (no errors)
- [ ] Code coverage ≥80%: `pytest --cov=app`
- [ ] **All 20 BRs enforced** and referenced in code comments
- [ ] **German copy exact** from `error-handling.md` (audited, no paraphrasing)
- [ ] Self-review completed (Step 5 checklist from CLAUDE.md):
  - [ ] All String columns have length constraints matching migration
  - [ ] Conflict detection uses GiST index and correct overlap logic
  - [ ] Approval reset logic correct (extend → reset, shorten → keep)
  - [ ] No N+1 query problems (eager loading used where applicable)
  - [ ] Return types correct (schemas exclude sensitive fields)
  - [ ] All edge cases tested (multi-month overlaps, self-approval, concurrency)
- [ ] OpenAPI docs accessible at `/docs`
- [ ] All endpoints return correct status codes (201, 200, 400, 401, 403, 404, 409)
- [ ] Rate limiting enforced server-side per BR-012
- [ ] Concurrency safety implemented (SELECT FOR UPDATE or optimistic locking)
- [ ] Documentation updated if needed

---

## Next Phase

✅ Phase 2 complete → [Phase 3: Approval Flow](phase-3-approval-flow.md)
