# Phase 4: Email Integration - Business Rules Analysis

## Overview

Phase 4 implements the Resend email service with 11 German notification templates. This analysis identifies all applicable business rules, their implementation impact, required test coverage, and edge cases.

---

## Executive Summary

**Critical BRs for Phase 4:** BR-003, BR-004, BR-005, BR-006, BR-007, BR-009, BR-010, BR-015, BR-022, BR-024

**Key Constraints:**
- Three fixed approvers (Ingeborg, Cornelia, Angelika) - seed data required
- Self-approval auto-applied; affected emails suppress self-recipient
- Denial is non-blocking and non-public; all parties notified
- Tokens never expire; action links idempotent with "Schon erledigt" messaging
- Retry 3x with exponential backoff; failures logged with correlation IDs
- Date ranges always inclusive (BR-001); affects all email text
- Weekly digest: Pending only, NoResponse only, aged ≥5d, future-only, per-approver

---

## User Story: US-4.1: Email Service Setup

### Applicable Business Rules

| BR | Title | Implementation Impact | Test Priority |
|----|----|----|----|
| **BR-022** | Email Retries | 3 attempts, exponential backoff, correlation IDs, consistent copy | CRITICAL |
| BR-010 | Tokens and Links | Never expire, never revoked, idempotent actions | CRITICAL |
| BR-011 | German-Only UI | All email copy in German (informal "du") | HIGH |
| BR-016 | Party Size Display | Format "n Personen" (even 1 person) | HIGH |

### Why These BRs Matter

**BR-022 (Email Retries):**
- Email service may fail transiently; retry logic prevents lost notifications
- **Impact:** Must implement exponential backoff (not linear), avoid retry storms
- **Tests needed:** Mock Resend API to fail 1-2 times, verify 3rd succeeds; verify backoff timing; verify correlation IDs logged

**BR-010 (Tokens/Idempotency):**
- Users may click action links multiple times or retry email actions
- **Impact:** Links must be idempotent; repeated actions show result page, not error
- **Tests needed:** Click approve link twice, verify "Schon erledigt" message on second; verify booking state unchanged

**BR-011 & BR-016 (German Copy):**
- All email subjects, bodies, and button labels must be in German
- **Impact:** No i18n infrastructure; copy embedded in templates
- **Tests needed:** Verify all email text matches `docs/specification/notifications.md` exactly; verify "n Personen" format

### Edge Cases to Test

1. **Retry Exhaustion:** Email fails all 3 retries → logged as failure, user not notified (only error log)
2. **Retry Timing:** First retry ~5s, second ~25s (exponential, not linear)
3. **Correlation ID Consistency:** Same email attempt has same ID across retries
4. **Link Idempotency with State Change:** User approves, email resent, user clicks link again → shows "Schon erledigt" not success
5. **Multi-Email Concurrency:** Resend limits (if any) handled gracefully
6. **German Character Rendering:** ä, ö, ü, ß render correctly in HTML and plain-text

### Estimated Test Count: 12 tests

- 1 happy path (email sends successfully on first attempt)
- 3 retry scenarios (fail 1x/2x/exhausted)
- 2 correlation ID tests (same ID across retries, unique per email)
- 2 idempotency tests (approve 2x, deny 2x)
- 2 German character tests (HTML, plain-text)
- 1 rate limiting test (Resend API limits handled)
- 1 config validation test (API key present, domain configured)

---

## User Story: US-4.2: Booking Created Email

Covers emails triggered when booking is created (Request Submitted, and self-approver scenario).

### Applicable Business Rules

| BR | Title | Implementation Impact | Test Priority |
|----|----|----|----|
| **BR-015** | Self-Approval | Auto-approve requester if they are an approver; suppress their email in Request Submitted | CRITICAL |
| **BR-003** | Three Fixed Approvers | Exactly Ingeborg, Cornelia, Angelika; no dynamic approvers | CRITICAL |
| **BR-001** | Inclusive End Date | Date range calculations affect email text (e.g., "01.–05.08.2025") | CRITICAL |
| BR-010 | Tokens and Links | Action links (approve/deny) include secure tokens | HIGH |
| BR-022 | Email Retries | Retry 3x with exponential backoff | HIGH |
| BR-016 | Party Size Display | Always "n Personen" format | MEDIUM |
| BR-020 | Link Detection | Description field validated before stored; no URLs allowed | MEDIUM |

### Why These BRs Matter

**BR-015 (Self-Approval):**
- When Ingeborg creates a booking, her approval is auto-applied immediately at submission
- **Impact:** Request Submitted email must NOT be sent to Ingeborg (self-recipient suppressed); only 2 approval notification emails sent (Cornelia, Angelika)
- **Tests needed:** Create booking as Ingeborg → verify only Cornelia and Angelika receive Request Submitted email; verify Ingeborg's approval = Approved in DB; verify approval count = 1 (self-approval counts)

**BR-003 (Fixed Approvers):**
- Three approvers always: Ingeborg, Cornelia, Angelika (not configurable, not dynamic)
- **Impact:** Seed data must create exactly 3 ApproverParty rows; Request Submitted email must be sent to exact recipients (except self if self-approver)
- **Tests needed:** Verify 3 approver parties seeded; verify email sent to correct 3 (or 2 if self-approver); verify approver names match spec exactly (spelling, capitalization)

**BR-001 (Inclusive End Date):**
- Booking from Jan 1–5 covers 5 days total, not 4
- **Impact:** Email date range text must be accurate; total_days calculation must be `end_date - start_date + 1`
- **Tests needed:** Create booking Jan 1–5 (inclusive) → verify email says "01.–05.01.2025" and email text displays correctly; test same-day booking (start=end) shows 1 day

**BR-010 (Tokens in Links):**
- Approve/Deny action links must include secure tokens for stateless email processing
- **Impact:** Action links are stateless; tokens encode approver identity, booking ID, action type
- **Tests needed:** Extract token from email; verify token decodes correctly; verify token includes booking_id and approver_id

**BR-022 (Retries):**
- If email send fails, retry up to 3 times
- **Impact:** Phase 4 infrastructure must support retries; copy must remain consistent across attempts
- **Tests needed:** Mock Resend to fail, verify retry; verify second attempt includes same variables (no re-fetch from DB)

**BR-016 (Party Size Format):**
- Party size always displayed as "n Personen" (even for 1 person)
- **Impact:** Email template must format as "1 Personen" (grammatically odd but per spec)
- **Tests needed:** Create booking with 1 person → verify email says "1 Personen"; create booking with 5 people → verify "5 Personen"

**BR-020 (Link Detection):**
- Description field cannot contain URLs (http://, https://, www, mailto:)
- **Impact:** Validation happens before booking stored; email includes description text as-is (already validated)
- **Tests needed:** Validation prevents storing description with URL; email includes clean description text

### Email Type 1: Request Submitted
**Trigger:** New booking created
**Recipients:** All three approvers, EXCEPT self if requester is an approver
**German Copy:** `docs/specification/notifications.md` lines 55-102

**Email Template Variables:**
- ApproverVorname (approver's first name)
- RequesterVorname (requester's first name)
- DateRange (formatted as "DD.–DD.MM.YYYY" per BR-001)
- PartySize (formatted as "n Personen" per BR-016)
- Description (optional, only if provided)
- Approve link (token-based per BR-010)
- Deny link (token-based, opens comment form)

### Edge Cases to Test

1. **Self-Approver Suppression:** Ingeborg creates booking → only Cornelia + Angelika receive email, not Ingeborg
2. **Non-Self-Approver:** Anna (non-approver) creates booking → all 3 approvers receive email
3. **Date Range Formatting:** Different month boundaries
   - Same month: "01.–05.08.2025"
   - Spanning months: "28.07.–12.08.2025"
   - Spanning years: (if allowed) "28.12.2025–02.01.2026"
4. **Same-Day Booking:** start_date = end_date → email shows single day, "1 Personen"
5. **Long Booking:** 30-day booking → "n Personen" (test large numbers)
6. **Description Formatting:** With/without description; long description (max 500 chars)
7. **Special Characters in Names:**
   - Requester: "Anna-Luise", "François", "Müller", "Schäfer"
   - Email must render diacritics correctly
8. **Email Generation Failure:** Email fail + retry → on 3rd retry succeeds, user eventually gets email
9. **Multiple Concurrent Bookings:** User creates 2 bookings in rapid succession → 2 separate emails generated, each with correct details
10. **Empty Description:** Description field omitted → email conditionally excludes "Beschreibung:" line

### Estimated Test Count: 18 tests

- 2 happy path (non-self-approver, self-approver)
- 4 self-approver scenarios (Ingeborg, Cornelia, Angelika as requester; plus non-approver)
- 4 date range tests (same month, spanning months, years, same-day)
- 2 party size tests (1 person, large number)
- 2 description tests (with/without, special chars)
- 1 special characters in requester name test
- 1 email retry test
- 1 concurrent booking test
- 1 template variable validation test (verify all variables present in email)

---

## User Story: US-4.3: Approval Notifications

Covers emails triggered by approval actions (partial approval, final approval, denial, reopen, cancel, edit).

### Applicable Business Rules

| BR | Title | Implementation Impact | Test Priority |
|----|----|----|----|
| **BR-003** | Three Fixed Approvers | Approval count always 0-3 | CRITICAL |
| **BR-004** | Denial Handling | Deny → non-blocking, non-public, email to all (req + 3 approvers) | CRITICAL |
| **BR-005** | Edit Approval Impact | Shorten: no reset, no re-approval email; Extend: reset all, send re-approval email | CRITICAL |
| **BR-024** | First-Action-Wins | Concurrent actions; result page shows "Schon erledigt" | CRITICAL |
| **BR-006** | Cancel While Pending | Email to all 4 (req + 3 approvers); no comment required | HIGH |
| **BR-007** | Cancel While Confirmed | Same as BR-006 but email says "bestätigte Buchung" | HIGH |
| **BR-009** | Weekly Digest | Sunday 09:00, per-approver, inclusion criteria, suppression | CRITICAL |
| **BR-010** | Tokens and Links | Action links idempotent; "Schon erledigt" messaging | HIGH |
| **BR-015** | Self-Approval | Self-approver's approval already applied; other approvers continue approving | MEDIUM |
| BR-022 | Email Retries | Retry logic applies to all emails | MEDIUM |

### Why These BRs Matter

**BR-004 (Denial Handling):**
- Denial is non-blocking (dates become free) and non-public (hidden from calendar)
- **Impact:** Deny email sent to ALL parties (requester + 3 approvers) with reason; email includes reopen/cancel buttons for requester; non-requester version hides buttons
- **Tests needed:** Deny booking → verify 4 emails (req + Ingeborg + Cornelia + Angelika); verify requester email includes "[Wieder eröffnen]  [Stornieren]" buttons; verify approver emails omit buttons; verify approval status = Denied; verify booking hidden from calendar

**BR-005 (Edit Approval Impact):**
- Shorten dates within original bounds: approvals unchanged, no re-approval email, requester-only email
- Extend dates (earlier start or later end): all approvals reset to NoResponse, re-approval email sent to all 3, requester notified via "Termine geändert – bitte neu bestätigen"
- **Impact:** Must have TWO different email templates (Edit: Shorten vs. Edit: Extend); must distinguish between shorten/extend and reset approvals accordingly
- **Tests needed:**
  - Shorten: Jan 1–10 → Jan 5–10 → verify requester gets "Daten aktualisiert", approvers get NO email, approvals unchanged
  - Extend: Jan 1–10 → Dec 15–15 Jan → verify all 3 approvers get "Termine geändert", approvals reset to NoResponse, requester notified approvals were reset

**BR-024 (First-Action-Wins):**
- Concurrent approval/denial; first to persist wins; late action shows "Schon erledigt" on result page
- **Impact:** Result page template must handle "Schon erledigt" case; must show context (e.g., "Cornelia hat bereits abgelehnt – die Anfrage ist jetzt abgelehnt")
- **Tests needed:** Simulate concurrent approve/deny → verify first one succeeds; verify second one shows "Schon erledigt" with context; verify booking state matches first action

**BR-009 (Weekly Digest):**
- Sunday 09:00 Europe/Berlin; per-approver; includes Pending bookings where this approver = NoResponse, aged ≥5d, future-only
- **Impact:** Scheduler job (separate from immediate emails); digest includes summary + action links; suppressed if zero items; requires day-0 logic (submission date = day 0)
- **Tests needed:**
  - Scheduler runs Sunday 09:00 Berlin time → per-approver digest sent
  - Inclusion criteria: test that booking submitted on Day 0 appears in digest on Day 6 (≥5 calendar days); test that submission Day 0 doesn't appear on Day 4 (too young)
  - Future-only: test that past-dated bookings excluded
  - Suppression: test that approver with zero items gets no digest
  - Ordering: test that items ordered by soonest start_date

**BR-006 & BR-007 (Cancel):**
- Pending cancel: "Die Buchung von {{RequesterVorname}} für {{DateRange}} wurde storniert"
- Confirmed cancel: "Die bestätigte Buchung von {{RequesterVorname}} für {{DateRange}} wurde storniert"
- Both send to all 4 (req + 3 approvers); comment included if provided (BR-007 requires comment)
- **Tests needed:** Cancel Pending → verify 4 emails, no prefix "bestätigte"; Cancel Confirmed → verify 4 emails, includes "bestätigte", includes comment if provided

### Email Type 2: Approve (Not Final)
**Trigger:** Approver approves, but <3 approvals yet
**Recipients:** Requester only
**German Copy:** `docs/specification/notifications.md` lines 106-142

**Template Variables:**
- Partei (approver name, e.g., "Ingeborg")
- RequesterVorname
- DateRange
- OutstandingList (list of remaining approvers, e.g., "Cornelia und Angelika")

### Email Type 3: Final Approval (Confirmed)
**Trigger:** Third and final approval
**Recipients:** Requester + all three approvers (4 people)
**German Copy:** `docs/specification/notifications.md` lines 145-195
**Suppression:** Suppress intermediate "Approve Not Final" email to requester; send only Final Approval email

**Template Variables:**
- Vorname (recipient's name)
- DateRange
- PartySize
- Description (optional)
- IsRequester (conditional: show personal link vs. approver link)

### Email Type 4: Deny (Pending or Confirmed)
**Trigger:** Any approver denies
**Recipients:** ALL (Requester + all three approvers)
**German Copy:** `docs/specification/notifications.md` lines 198-271

**Template Variables:**
- Partei (denier's name)
- RequesterVorname
- DateRange
- PartySize
- Kommentar (required)
- IsRequester (conditional: requester sees "[Wieder eröffnen]  [Stornieren]" buttons)

### Email Type 5: Edit: Shorten Dates
**Trigger:** Requester shortens dates within original bounds (Pending state)
**Recipients:** Requester only
**German Copy:** `docs/specification/notifications.md` lines 274-311

**Template Variables:**
- RequesterVorname
- OldDateRange
- NewDateRange
- Note: Approvals remain unchanged, no re-approval email

### Email Type 6: Edit: Extend Dates
**Trigger:** Requester extends dates (earlier start or later end) (Pending state)
**Recipients:** All three approvers
**German Copy:** `docs/specification/notifications.md` lines 315-358

**Template Variables:**
- ApproverVorname
- RequesterVorname
- OldDateRange
- NewDateRange
- PartySize
- Note: All approvals reset to NoResponse; re-approval buttons included

### Email Type 7: Reopen (From Denied)
**Trigger:** Requester reopens denied booking
**Recipients:** All three approvers
**German Copy:** `docs/specification/notifications.md` lines 362-417

**Template Variables:**
- ApproverVorname
- RequesterVorname
- DateRange
- PartySize
- Description (optional)
- DatesChanged (conditional; if dates changed during reopen, show old/new)
- OldDateRange, NewDateRange (if DatesChanged)

### Email Type 8 & 9: Cancel
**Email Type 8:** Cancel Pending or Confirmed
**Trigger:** Requester cancels (Pending or Confirmed state)
**Recipients:** Requester + all three approvers
**German Copy:** `docs/specification/notifications.md` lines 421-471

**Email Type 9:** Cancel Denied
**Trigger:** Requester cancels denied booking
**Recipients:** Requester only
**German Copy:** `docs/specification/notifications.md` lines 475-503

**Template Variables (Type 8):**
- Vorname (recipient name)
- RequesterVorname
- DateRange
- WasConfirmed (boolean)
- IsRequester (conditional)
- Kommentar (optional, only if BR-007 comment provided)

**Template Variables (Type 9):**
- RequesterVorname
- DateRange

### Email Type 10: Personal Link Recovery
**Trigger:** User clicks "Ist das deine Anfrage?" → enters email → "Link erneut senden"
**Recipients:** Provided email (if exists in system)
**German Copy:** `docs/specification/notifications.md` lines 507-534

**Key:**
- Same copy sent whether email exists or NOT (no enumeration per BR-021)
- Soft cooldown: 60s per email/IP (BR-021) → UI message "Bitte warte kurz..."

### Email Type 11: Weekly Digest
**Trigger:** Sunday 09:00 Europe/Berlin
**Recipients:** Per-approver (only if they have items meeting criteria)
**German Copy:** `docs/specification/notifications.md` lines 537-607

**Inclusion Criteria:**
- Booking status = Pending
- This approver's approval = NoResponse
- Age ≥5 calendar days (submission date = day 0)
- Excludes past-dated bookings
- Suppressed if zero items for that approver

**Template Variables:**
- ApproverVorname
- Count (number of items)
- Plural (boolean; "Anfrage" vs. "Anfragen")
- Items array with:
  - RequesterVorname
  - DateRange
  - PartySize
  - Description (optional)
  - DaysAgo (age in days since submission)
  - Approve/Deny action links

### Edge Cases to Test

1. **Self-Approver in Approval Flow:**
   - Ingeborg creates booking → her approval auto-applied (BR-015)
   - Cornelia approves → Ingeborg (auto-approved) + Anna (requester) notified of progress
   - Angelika approves → all 3 approvers + Anna get final approval email
   - Test: Verify only Cornelia and Angelika's approvals count as actions; Ingeborg's is silent

2. **First-Action-Wins Concurrency (BR-024):**
   - Cornelia and Angelika simultaneously approve same booking
   - First to persist wins; second sees "Schon erledigt" message
   - Test: Simulate race with transactions; verify first succeeds, second shows "Schon erledigt"

3. **Edit Approval Impact:**
   - Scenario A (Shorten): Bookings approved by Ingeborg and Cornelia; requester shortens dates
     - Test: Angelika still has NoResponse (approvals not reset); Ingeborg and Cornelia unchanged; only requester gets email
   - Scenario B (Extend): Same state; requester extends dates
     - Test: All approvals reset to NoResponse; all 3 approvers get re-approval email

4. **Date Changes in Email Templates:**
   - Edit: Extend email must show "Alter Zeitraum: 01.–10.08.2025" and "Neuer Zeitraum: 28.07.–12.08.2025"
   - Reopen with date change must show both old and new
   - Test: Verify date ranges formatted correctly in all templates

5. **Denial with Comment:**
   - Comment length: must be ≤500 chars, no links (BR-020)
   - Email includes comment in "Grund:" field
   - Test: Deny with long comment; verify comment appears verbatim in email

6. **Cancel with Comment (BR-007):**
   - Confirmed cancellation requires comment
   - Comment appears in email
   - Test: Cancel Confirmed with comment; verify comment in email; Cancel Pending with no comment; verify no "Grund:" line

7. **Weekly Digest Age Calculation:**
   - Booking submitted Monday Day 0 → appears in digest Saturday morning? NO (only 5 days old)
   - Booking submitted Monday Day 0 → appears in digest Sunday morning (Day 6)? YES (6 days old, ≥5)
   - Test: Create booking at known time; advance to different days; verify digest includes/excludes correctly

8. **Weekly Digest Suppression:**
   - Approver has no pending items with NoResponse aged ≥5 days → no digest sent
   - Test: Empty digest should not be sent

9. **Weekly Digest Ordering:**
   - Multiple items; ordered by soonest start_date
   - Test: Create 3 bookings with different start dates; verify digest orders correctly

10. **Result Page: "Schon Erledigt" Messages:**
    - User approves, then immediately clicks approve link again → result page shows "Danke – du hast zugestimmt. Schon erledigt: Cornelia und Angelika ausstehend"? NO
    - Result page shows "Schon erledigt. Die Buchung ist bereits bestätigt." (if already confirmed) OR lists outstanding
    - Test: Create booking, approve as Ingeborg (self-approved), click approval link again → "Schon erledigt" with appropriate message

11. **Personal Link Recovery:**
    - User enters non-existent email → same message sent as if email exists (no enumeration)
    - User enters valid email → link resent
    - Test: Request link for non-existent email → verify same "Wir haben dir..." message; request link for valid email → verify link resent

12. **Retry Correlation IDs:**
    - Each email attempt has unique correlation ID
    - All retries for same email have same ID
    - Test: Logging includes correlation IDs; verify same ID for retries

### Estimated Test Count: 45+ tests

**Approval Flow Tests:**
- 1 happy path (Ingeborg creates, Cornelia approves, Angelika approves)
- 3 self-approver tests (Ingeborg, Cornelia, Angelika as requester)
- 2 first-action-wins tests (concurrent approve/deny)
- 2 result page tests ("Schon erledigt" messages)

**Approval Partial/Final Emails:**
- 2 partial approval tests (different approver orders)
- 2 final approval tests (requester + approver versions)
- 1 final approval suppression test (intermediate email suppressed)

**Denial Tests:**
- 1 deny from Pending
- 1 deny from Confirmed
- 1 deny with long comment
- 1 deny result page test

**Edit Tests:**
- 1 shorten with unchanged approvals
- 1 extend with approval reset
- 1 shorten email suppression (approvers get no email)
- 1 extend email to approvers
- 2 date range formatting tests (different month boundaries)

**Cancel Tests:**
- 1 cancel Pending
- 1 cancel Confirmed with comment
- 1 cancel Denied
- 3 result page tests (by status)

**Reopen Tests:**
- 1 reopen without date change
- 1 reopen with date change (show diffs in email)

**Weekly Digest Tests:**
- 1 digest generation (scheduler job)
- 2 inclusion criteria (aged ≥5d, future-only)
- 1 suppression (zero items)
- 1 ordering (by start_date)
- 2 per-approver tests (different approvers have different outstanding items)

**Personal Link Recovery Tests:**
- 1 recovery for valid email
- 1 recovery for non-existent email (no enumeration)
- 1 cooldown test (60s per BR-021)

**German Copy Tests:**
- 3 special character tests (ä, ö, ü, ß in names, descriptions)
- 1 party size formatting test

**Retry Tests:**
- 2 retry tests (exponential backoff, correlation IDs)

---

## Test Matrix: All 11 Email Types × Scenarios

### Matrix Legend
- ✓ = Tested in acceptance scenario
- C = Custom scenario required
- S = Scheduler job (not immediate email)
- T = Template variable test

| Email Type | Happy Path | Self-Approver | Edge Case 1 | Edge Case 2 | Edge Case 3 |
|---|---|---|---|---|---|
| 1. Request Submitted | ✓ | ✓ (skip self) | C: non-approver | C: special chars in names | C: long description |
| 2. Approve (Not Final) | ✓ | ✓ (after self-approval) | C: 2 approvers before 3rd | C: result page ordering | T: outstanding list format |
| 3. Final Approval | ✓ | ✓ (requester + approvers) | C: suppress intermediate | T: requester vs. approver links | T: description optional |
| 4. Deny | ✓ | ✓ (approver denies) | C: long comment | C: reopen/cancel buttons | C: first-action-wins race |
| 5. Edit: Shorten | ✓ | C: requester is approver | C: no approver emails | C: approvals unchanged | C: date formatting |
| 6. Edit: Extend | ✓ | C: requester is approver | C: all approvals reset | C: approvers re-approve | C: diff formatting |
| 7. Reopen | ✓ | ✓ (approvers re-evaluate) | C: with date change | C: show diff in email | C: reset approvals |
| 8. Cancel (P/C) | ✓ | C: all 4 recipients | C: Confirmed has comment | C: shows "bestätigte" | C: all recipients get email |
| 9. Cancel (Denied) | ✓ | ✓ (requester only) | C: no approver emails | C: no "bestätigte" prefix | N/A |
| 10. Link Recovery | ✓ | ✓ (resend to valid email) | C: non-existent email | C: cooldown (60s) | C: no enumeration |
| 11. Weekly Digest | S | S (per-approver) | C: aged ≥5d filter | C: future-only filter | C: suppress if zero items |

---

## Cross-Reference: Notifications.md Email Types

All 11 email types defined in `/home/user/btznstn/docs/specification/notifications.md`:

| # | Type | Trigger | Recipients | Key Variables |
|---|---|---|---|---|
| 1 | Request Submitted | New booking created | Approvers (except self) | ApproverVorname, RequesterVorname, DateRange, PartySize, Description, Action links |
| 2 | Approve (Not Final) | Approver approves (incomplete) | Requester | Partei, RequesterVorname, DateRange, OutstandingList |
| 3 | Final Approval | 3rd approver approves | Requester + all 3 approvers | Vorname, DateRange, PartySize, Description, IsRequester |
| 4 | Deny | Any approver denies | ALL (Req + 3 approvers) | Partei, RequesterVorname, DateRange, PartySize, Kommentar, IsRequester |
| 5 | Edit: Shorten | Requester shortens dates | Requester | RequesterVorname, OldDateRange, NewDateRange |
| 6 | Edit: Extend | Requester extends dates | All 3 approvers | ApproverVorname, RequesterVorname, OldDateRange, NewDateRange, PartySize |
| 7 | Reopen | Requester reopens denied | All 3 approvers | ApproverVorname, RequesterVorname, DateRange, PartySize, Description, DatesChanged, OldDateRange (opt) |
| 8 | Cancel (P/C) | Requester cancels (any state) | Req + 3 approvers | Vorname, RequesterVorname, DateRange, WasConfirmed, IsRequester, Kommentar (opt) |
| 9 | Cancel (Denied) | Requester cancels denied | Requester | RequesterVorname, DateRange, Kommentar (opt) |
| 10 | Link Recovery | User requests link | Provided email (if exists) | HasBookings, PersonalLink, Note: no enumeration |
| 11 | Weekly Digest | Sunday 09:00 Berlin | Per-approver (if items exist) | ApproverVorname, Count, Plural, Items[], DaysAgo, Action links |

---

## Phase 4 Infrastructure Requirements

### Email Service Configuration

**Resend API Integration:**
- API key from environment (configurable)
- Domain configured for From address (`no-reply@<app-domain>`)
- SPF/DKIM/DMARC setup (per email service docs)
- Rate limiting handling (if Resend has limits)

**Retry Strategy (BR-022):**
```
Attempt 1: Immediate
Attempt 2: ~5 seconds (exponential backoff)
Attempt 3: ~25 seconds (exponential backoff)
Failure: Log with correlation ID, no user notification
```

**Correlation IDs:**
- Generate unique ID per email send attempt
- Log all retries with same ID
- Include in error messages for debugging

### Template Engine

**Requirements:**
- Variables: `{{VariableName}}`
- Conditionals: `{{#if Condition}}...{{/if}}`
- Loops: `{{#each Items}}...{{/each}}`
- HTML escaping
- Plain-text fallback
- German character support (ä, ö, ü, ß)

**Recommended:** Handlebars/Jinja2 compatible template language

### Database Schema (Phase 1 dependency)

**Required tables:**
- `booking` (with status, start_date, end_date, requester_email, requester_vorname)
- `approver_party` (3 fixed rows: Ingeborg, Cornelia, Angelika)
- `approval` (junction: booking_id, approver_party_id, decision_status)
- `token` (for action links: booking_id, approver_id, action_type, created_at)

**Required columns for email:**
- Booking.start_date, end_date (for DateRange)
- Booking.requester_email (for sending)
- Booking.requester_vorname (for template)
- Booking.party_size, description
- ApproverParty.vorname (for template)
- Approval.decision (for status, approval count)
- Approval.created_at, updated_at (for digest age calculation)

### Scheduler Integration (BR-009)

**Weekly Digest Job:**
- Runs: Sunday 09:00 Europe/Berlin
- Frequency: Once per week
- Tasks:
  1. For each approver: find Pending bookings where this approver = NoResponse, aged ≥5 days, future-only
  2. If count > 0: generate digest email
  3. If count = 0: skip (suppress)
  4. Send email with action links

**Tools:** APScheduler (Python), Celery, or similar scheduler

### Logging & Monitoring

**Required logs:**
- Email send attempts (with correlation ID, timestamp, recipient)
- Retry attempts (same correlation ID, attempt number, error reason)
- Failures after all retries (correlation ID, final error)
- Bounces (email address, bounce reason)

**Monitoring:**
- Track send success rate
- Alert on failure rate >5%
- Monitor retry distribution (high retries = service issue)

---

## Implementation Checklist (Pre-Code)

**Before writing any code or tests:**

- [ ] Read all 11 email templates in `docs/specification/notifications.md`
- [ ] Identify all German copy to be used (no improvising)
- [ ] Design token format for action links (include booking_id, approver_id, action_type, timestamp)
- [ ] Design correlation ID generation (UUIDs or similar)
- [ ] List all template variables needed per email type (matrix above)
- [ ] Identify database schema dependencies (ensure Phase 1 provides all needed columns)
- [ ] Design retry logic (exponential backoff algorithm)
- [ ] Plan scheduler job for weekly digest (timing, filtering logic)
- [ ] Design approval state tracking for "first-action-wins" result pages
- [ ] Plan mock email service for testing (Resend has sandbox mode?)

---

## Complete Test Count Summary

| Category | Count |
|----------|-------|
| **US-4.1: Email Service Setup** | 12 |
| **US-4.2: Booking Created Email** | 18 |
| **US-4.3: Approval Notifications** | 45+ |
| **Total Phase 4** | **75+ tests** |

**Breakdown:**
- Unit tests (email generation, template rendering): ~40
- Integration tests (email service, retries): ~20
- End-to-end tests (full workflow): ~15

---

## Critical Success Factors

1. **Exact German Copy:** All email text must match `docs/specification/notifications.md` EXACTLY (no paraphrasing)
2. **Business Rule Enforcement:**
   - BR-015: Self-approver suppression
   - BR-004: Denial to all parties + non-public
   - BR-005: Edit approval impact (shorten vs. extend)
   - BR-024: First-action-wins result pages
   - BR-009: Weekly digest inclusion criteria & suppression
3. **Token Security:** Action links must be secure, idempotent, and never expire (BR-010)
4. **Retry Resilience:** 3 attempts with exponential backoff; failures logged with correlation IDs (BR-022)
5. **Date Formatting:** Inclusive end dates; "DD.–DD.MM.YYYY" format; handle multi-month ranges
6. **Party Size Format:** Always "n Personen" (even for 1)
7. **First Name Validation:** Special characters (ä, ö, ü, ß, hyphens, apostrophes) render correctly

---

## Next Steps

1. **Implement email service:** Resend client, correlation IDs, retry logic
2. **Create email templates:** 11 Handlebars/Jinja2 templates with German copy
3. **Write tests FIRST:** 75+ tests per BDD workflow
4. **Implement trigger functions:** One per email type
5. **Implement scheduler:** Weekly digest job
6. **Manual testing:** Send real emails to test addresses; verify Resend dashboard
7. **Code review:** Verify German copy matches specs, BRs enforced, tests pass

---

## References

- Business Rules: `/home/user/btznstn/docs/foundation/business-rules.md` (BR-001 to BR-029)
- Notifications Spec: `/home/user/btznstn/docs/specification/notifications.md` (all 11 email types)
- Implementation Guide: `/home/user/btznstn/docs/implementation/CLAUDE.md` (strict TDD workflow)
- Phase 4 Details: `/home/user/btznstn/docs/implementation/phase-4-email-integration.md`
