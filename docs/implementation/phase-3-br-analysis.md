# Phase 3: BR Analysis & Test Matrix
## Approval Flow (US-3.1, US-3.2, US-3.3)

---

## Overview

Phase 3 implements the core approval state machine: approving bookings, denying with comments, and reopening denied bookings. This analysis identifies **ALL** applicable business rules, implementation impacts, edge cases, and test requirements.

**Phase 3 User Stories:**
- **US-3.1:** Approve Booking
- **US-3.2:** Deny Booking
- **US-3.3:** Reopen Denied Booking

---

## US-3.1: Approve Booking

### Applicable Business Rules

| Rule | Category | Why It Matters |
|------|----------|----------------|
| **BR-003** | Approval | Core requirement: determines when booking transitions to Confirmed (must have all 3 approvals) |
| **BR-010** | Access | Action links must be idempotent (approving twice = no side effects) |
| **BR-014** | Dates | Validation rule: cannot approve past bookings (read-only period) |
| **BR-015** | Approval | Logic: if requester is an approver, auto-approve at submission (one of 3 is done) |
| **BR-024** | Approval | Concurrency: handle race conditions (first approval/denial wins, later shows "Schon erledigt") |
| **BR-004** | Approval | State validation: cannot approve Denied bookings (locked for approvals while Denied) |
| **BR-023** | UI | View logic: after approval, remove item from approver's Outstanding bucket |
| **BR-022** | Notifications | Retry strategy: notification emails need exponential backoff (Phase 4, but affects timeline events) |
| **BR-009** | Notifications | Digest impact: approval removes item from NoResponse bucket (relevant for Phase 4) |

### Implementation Impact Details

#### BR-003: Three Fixed Approvers Required
- **What to implement:** Check approval count when approving
  - If count < 3, keep status Pending
  - If count = 3 (just became), transition to Confirmed
  - Update `last_activity_at` on all cases
- **Database:** Query approvals table, count Approved decisions
- **Logic:**
  ```python
  approved_count = len([a for a in booking.approvals if a.decision == DecisionEnum.APPROVED])
  if approved_count == 3:
      booking.status = StatusEnum.CONFIRMED
  ```

#### BR-010: Tokens and Links (Idempotent)
- **What to implement:** Idempotent approval endpoint
  - Same token submitted twice = same result, no error
  - Return success message "Danke – du hast zugestimmt" both times
  - No duplicate timeline events
- **Database:** Check if `approval.decision == Approved` before updating
  - If already Approved, just return success (don't re-update, don't create timeline event)
  - If NoResponse, update to Approved and create timeline event
- **Result page:** Different messaging depending on whether this is final approval:
  - Not final: "Danke – du hast zugestimmt. Status: Ausstehend: {{Restparteien}}"
  - Final: "Danke – du hast zugestimmt. Alles bestätigt!"
  - Already done: "Schon erledigt. Die Buchung ist bereits bestätigt."

#### BR-014: Past Items Read-Only
- **What to implement:** Validation before approving
  - If `end_date < today`, reject with German error: "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."
  - Timeline: "flip to past status at 00:00 Europe/Berlin the day after EndDate"
  - Use time zone aware comparisons
- **Database:** WHERE clause: `booking.end_date >= date.today()`
- **Return code:** 400 Bad Request

#### BR-015: Self-Approval
- **What to implement:** Auto-approval at submission time (already in Phase 2)
  - Here: just document that approval endpoint respects this (if requester was Ingeborg, her approval already exists in Approved state)
  - When Ingeborg approves via link, idempotent (already Approved per BR-010)
  - Can still Deny while Pending (separate from auto-approval)
- **Database:** No change (handled in Phase 2 create endpoint)
- **Logic:** Existing approvals[party] record already has Approved decision

#### BR-024: First-Action-Wins (Concurrency)
- **What to implement:** Pessimistic locking when updating approval
  - Use `SELECT ... FOR UPDATE` to lock booking row during approval
  - Prevents concurrent approval/denial race conditions
  - First to persist wins, second gets "Schon erledigt" response
- **Database:**
  ```python
  # Lock booking row
  booking = await session.execute(
      select(Booking).where(Booking.id == booking_id).with_for_update()
  )
  # Then update approval
  ```
- **Return code:** 200 (idempotent, both approve and deny return success with context message)
- **Response messaging:**
  - First approval: success with "Danke" message
  - Second action (approval after denial): "Schon erledigt. {{Partei}} hat bereits abgelehnt – die Anfrage ist jetzt abgelehnt (nicht öffentlich)."

#### BR-004: Denial Handling (State Validation)
- **What to implement:** Check booking status before allowing approval
  - If status = Denied, reject with error: "Diese Aktion ist für deine Rolle nicht verfügbar."
  - Per BR-004: "While Denied: Approvers cannot act (no approve/deny possible)"
  - Also cannot approve Canceled bookings
- **Database:** Check `booking.status IN (Pending, Confirmed)`
  - Pending: normal approval path
  - Confirmed: idempotent (if already Approved)
- **Return code:** 400 Bad Request (or show "Schon erledigt" if trying to approve already-Confirmed)

#### BR-023: Approver Lists (View Consistency)
- **What to implement:** Understand that approval removes item from Outstanding list
  - Outstanding bucket: items where `approval.decision = NoResponse`
  - After approval: `approval.decision = Approved` → item no longer in Outstanding
  - History bucket: still visible (all statuses)
- **Database:** No direct impact for approval endpoint, but queries depend on decision field
- **Query:** Outstanding list filters `decision = NoResponse`

#### BR-022: Email Retries (Notification System)
- **What to implement:** Generate timeline events that will trigger emails
  - Approval triggers notifications (Phase 4)
  - Timeline event stores decision info
  - Retry logic in notification layer (not approval endpoint itself)
- **Database:** Create timeline event with event_type = "Approved"
- **Details:** Not a direct constraint on approval logic, but affects what data is stored

#### BR-009: Weekly Digest Impact
- **What to implement:** Understand digest exclusion after approval
  - Digest includes items where `approval.decision = NoResponse`
  - After approval: `approval.decision = Approved` → excluded from digest
- **Database:** No direct change, but relevant for queries
- **Impact:** Digest selection query filters by NoResponse decision

### Edge Cases (Must Test)

1. **Single approval (not final)** - Booking stays Pending, no email to requester about Confirmed
2. **Final approval (third approval)** - Status transitions to Confirmed, different email copy
3. **Idempotent approval** - Approving same booking twice via same token = same result, no error, no duplicate timeline
4. **Approval on already-Confirmed booking** - Idempotent, returns "Schon erledigt" message
5. **Approval on Denied booking** - Error: "Diese Aktion ist für deine Rolle nicht verfügbar."
6. **Approval on Canceled booking** - Error (not allowed to act on canceled)
7. **Approval on past booking** (end_date < today) - Error: "Dieser Eintrag liegt in der Vergangenheit..."
8. **Self-approver approving** - Already approved at submission (idempotent)
9. **Concurrent approval + denial** (BR-024) - First to persist wins, second gets "Schon erledigt" with context
10. **Concurrent approval + approval by different parties** - All succeed (no race with different parties)
11. **All three approvals in rapid succession** - Each succeeds, third triggers Confirmed transition
12. **Invalid token** - Error: "Der Link ist ungültig oder bereits verwendet."
13. **Approval response includes remaining NoResponse parties** - Show who still needs to approve (not final)
14. **Approval updates last_activity_at** - Booking's last activity timestamp updated

### Estimated Test Count: 14

**Backend Tests (pytest):**

1. `test_single_approval_keeps_status_pending` - BR-003
2. `test_final_approval_transitions_to_confirmed` - BR-003
3. `test_idempotent_approval_no_error` - BR-010
4. `test_idempotent_approval_no_duplicate_timeline` - BR-010
5. `test_approval_on_past_booking_fails` - BR-014
6. `test_approval_on_denied_booking_fails` - BR-004
7. `test_approval_on_confirmed_booking_idempotent` - BR-010
8. `test_self_approver_already_approved` - BR-015
9. `test_concurrent_approval_and_denial_first_wins` - BR-024
10. `test_approval_removes_from_outstanding_list` - BR-023
11. `test_approval_generates_timeline_event` - Timeline audit
12. `test_approval_response_includes_remaining_parties` - BR-003
13. `test_approval_updates_last_activity_at` - Timestamp consistency
14. `test_invalid_token_fails` - BR-010 (access control)

---

## US-3.2: Deny Booking

### Applicable Business Rules

| Rule | Category | Why It Matters |
|------|----------|----------------|
| **BR-004** | Approval | Core requirement: deny status, non-blocking dates, requires comment, hidden from public |
| **BR-003** | Approval | Context: any of the three can deny (affects who sees in Outstanding list) |
| **BR-020** | Validation | Comment field validation: block URLs (prevent spam/phishing) |
| **BR-014** | Dates | Validation: cannot deny past bookings |
| **BR-010** | Access | Idempotent: denying twice = same result, no error, shows "Schon erledigt" |
| **BR-024** | Approval | Concurrency: first denial wins, concurrent approval shows "Schon erledigt" |
| **BR-023** | UI | View logic: after denial, remove item from Outstanding bucket |
| **BR-004** | State | Post-confirm deny: denying Confirmed booking requires warning dialog (UI component, but endpoint must support) |
| **BR-022** | Notifications | Notifications after denial (retry strategy) |
| **BR-009** | Notifications | Digest exclusion after denial (decision changes from NoResponse) |

### Implementation Impact Details

#### BR-004: Denial Handling (Core Logic)
- **What to implement:** Deny endpoint transitions booking to Denied status
  - Requires comment parameter (request validation)
  - Comment displayed to requester
  - Status becomes Denied (non-blocking, dates freed up immediately)
  - Denied bookings hidden from public calendar (filtering responsibility of calendar endpoint)
  - Only requester can Reopen (enforced in US-3.3 endpoint)
  - While Denied: approvers cannot act (BR-024 handles concurrent denial)
- **Database:**
  ```python
  booking.status = StatusEnum.DENIED
  approval.decision = DecisionEnum.DENIED
  approval.comment = comment
  approval.decided_at = now()
  booking.last_activity_at = now()
  ```
- **Validation:** Comment required, not empty

#### BR-003: Three Fixed Approvers (Context)
- **What to implement:** Any of three can deny, not all need to
  - Denial by ANY party makes booking Denied
  - No need to wait for other parties
  - Affects Outstanding list (removed immediately)
- **Database:** No change (existing approver_parties table)
- **Logic:** One denial = status change (unlike approval which needs all 3)

#### BR-020: Link Detection in Text (Comment Field)
- **What to implement:** Validate comment field
  - Block patterns: `http://`, `https://`, `www`, `mailto:`
  - Error message: "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden."
  - Validation on submit (client and server)
- **Validation:** Regex check before updating database
- **Return code:** 400 Bad Request if link detected

#### BR-014: Past Items Read-Only
- **What to implement:** Cannot deny past bookings
  - Validation: `booking.end_date >= date.today()`
  - Error: "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."
- **Database:** WHERE clause filter
- **Return code:** 400 Bad Request

#### BR-010: Idempotent Action Links
- **What to implement:** Denying twice = same result
  - If already Denied by this party, return success with "Schon erledigt" message
  - No duplicate timeline events
  - Response shows current status
- **Database:** Check if `approval.decision == Denied` before updating
  - If already Denied, return success with "Schon erledigt. Die Anfrage ist jetzt abgelehnt (nicht öffentlich)."
  - If NoResponse, update to Denied and create timeline event
- **Message:** Different depending on context:
  - "Erledigt – du hast abgelehnt. Die Anfrage ist jetzt abgelehnt und nicht mehr öffentlich sichtbar."
  - "Schon erledigt. Die Anfrage ist bereits abgelehnt (nicht öffentlich)."

#### BR-024: First-Action-Wins (Concurrency)
- **What to implement:** Pessimistic locking for concurrent approval + denial
  - If approval A and denial D happen simultaneously, first to persist wins
  - Second returns "Schon erledigt" with context showing what happened
- **Database:** SELECT FOR UPDATE locking
- **Scenarios:**
  - Denial first, then approval: "Schon erledigt. {{Partei}} hat bereits abgelehnt..."
  - Approval first, then denial: "Schon erledigt. Die Buchung ist bereits bestätigt."
- **Note:** Denial by different party is independent (multiple denials not possible per BR-003 logic, but concurrent approval by different party is possible)

#### BR-023: Approver Lists (View Impact)
- **What to implement:** After denial, item removed from Outstanding
  - Outstanding: `decision = NoResponse` and `status = Pending`
  - After denial: `decision = Denied` → excluded from Outstanding
  - History still shows all items (approver views denials in history)
- **Database:** No direct change
- **Query impact:** Outstanding list filters by `decision = NoResponse`

#### BR-004: Post-Confirm Deny (Dialog UI)
- **What to implement:** Support denying Confirmed bookings
  - Check if `booking.status = Confirmed` before denying
  - Client shows warning dialog (not endpoint's responsibility, but endpoint must support)
  - Endpoint requires comment (always required for denial)
  - Status transitions to Denied (same as Pending deny)
  - All parties notified
- **Database:** Same as Pending denial
- **Difference:** Just a state validation (Confirmed booking can be denied, no logic change)

#### BR-022: Email Retries (Notification System)
- **What to implement:** Generate timeline event that triggers retry-able notifications
  - Timeline: event_type = "Denied", note = comment
  - Notifications will retry with backoff (Phase 4)
- **Database:** Create timeline event

#### BR-009: Digest Exclusion
- **What to implement:** Understand denial removes from digest
  - Decision changes to Denied → excluded from weekly digest
- **Database:** No direct change
- **Query impact:** Digest filters by `decision = NoResponse`

### Edge Cases (Must Test)

1. **Deny without comment** - Error: "Bitte gib einen kurzen Grund an."
2. **Deny with valid comment** - Success, status → Denied
3. **Deny with link in comment** - Error: "Links sind hier nicht erlaubt..."
4. **Deny on already-Denied booking** - Idempotent, returns "Schon erledigt"
5. **Deny on already-Confirmed booking** - Success (post-confirm deny allowed per BR-004)
6. **Deny on past booking** (end_date < today) - Error: "Dieser Eintrag liegt in der Vergangenheit..."
7. **Deny on Canceled booking** - Error (not allowed to act on canceled)
8. **Concurrent approval + denial** (BR-024) - First wins, second shows "Schon erledigt"
9. **Concurrent denial + denial by different parties** - Both succeed (different parties can each have decision)
10. **Deny stores comment correctly** - Comment visible to requester
11. **Deny generates timeline event** - Audit trail includes comment in note
12. **Deny updates last_activity_at** - Timestamp updated
13. **Deny removes item from Outstanding list** - Query filters by NoResponse
14. **Deny hides booking from public calendar** - Calendar endpoint filters out Denied
15. **Deny response includes appropriate message** - Different for first-time vs idempotent
16. **Comment length validation** - Max 500 chars (per schema)
17. **Invalid token fails** - BR-010

### Estimated Test Count: 17

**Backend Tests (pytest):**

1. `test_deny_without_comment_fails` - Validation
2. `test_deny_with_valid_comment_succeeds` - BR-004
3. `test_deny_changes_status_to_denied` - BR-004
4. `test_deny_with_link_in_comment_fails` - BR-020
5. `test_deny_on_past_booking_fails` - BR-014
6. `test_deny_on_denied_booking_idempotent` - BR-010
7. `test_deny_on_confirmed_booking_succeeds` - BR-004
8. `test_deny_on_canceled_booking_fails` - State validation
9. `test_concurrent_approval_and_denial_first_wins` - BR-024
10. `test_deny_stores_comment_in_approval` - BR-004
11. `test_deny_generates_timeline_event_with_comment` - Audit
12. `test_deny_updates_last_activity_at` - Timestamp
13. `test_deny_removes_from_outstanding_list` - BR-023
14. `test_deny_hides_from_calendar_endpoint` - BR-004 (non-blocking)
15. `test_deny_response_message_content` - BR-010 (idempotency message)
16. `test_deny_comment_max_length_validation` - Schema constraint
17. `test_invalid_token_fails` - BR-010

---

## US-3.3: Reopen Denied Booking

### Applicable Business Rules

| Rule | Category | Why It Matters |
|------|----------|----------------|
| **BR-004** | Approval | Core requirement: reopen transitions Denied → Pending, resets ALL approvals to NoResponse |
| **BR-018** | Validation | Guard: cannot reopen if new dates conflict with existing Pending/Confirmed bookings |
| **BR-001** | Dates | Date validation: new dates must respect inclusive end date semantics |
| **BR-005** | Edit | Approval reset: reopening resets all approvals (similar to edit extending dates) |
| **BR-014** | Dates | Validation: cannot reopen past Denied bookings |
| **BR-010** | Access | Idempotent: reopening twice = same result, no error |
| **BR-015** | Approval | Self-approval: if requester is approver, auto-approve applies again after reopen |
| **BR-002** | Overlap | Conflict detection: reopen uses same conflict rules as create |
| **BR-029** | Concurrency | First-write-wins: reopen must serialize with overlapping create/extend (transaction safety) |
| **BR-023** | UI | View impact: after reopen, reopened item removed from Denied view, appears in Outstanding |

### Implementation Impact Details

#### BR-004: Denial Handling (Reopen Logic)
- **What to implement:** Reopen endpoint transitions Denied → Pending, resets approvals
  - Request includes new dates (optional to change, can be same)
  - Transition: `booking.status = Pending`
  - All approvals reset to NoResponse: `all approvals.decision = NoResponse`, `decided_at = NULL`
  - Only requester can reopen (enforced by token validation)
  - After reopen, requester notified, all approvers notified (re-approval emails)
- **Database:**
  ```python
  booking.status = StatusEnum.PENDING
  booking.start_date = new_start_date
  booking.end_date = new_end_date
  booking.total_days = (new_end_date - new_start_date).days + 1
  for approval in booking.approvals:
      approval.decision = DecisionEnum.NO_RESPONSE
      approval.decided_at = NULL
  booking.last_activity_at = now()
  ```

#### BR-018: Reopen Guard (Conflict Detection)
- **What to implement:** Validate new dates before allowing reopen
  - Check if new dates conflict with Pending/Confirmed bookings (other than self)
  - Same conflict logic as booking creation (overlap detection)
  - Error message: "Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung ({{Vorname}} – {{Status}})."
  - If conflict, return 400 without updating
- **Database:**
  ```python
  # Check for conflicts (same as create)
  conflicts = await session.execute(
      select(Booking)
      .where(
          and_(
              Booking.id != booking.id,  # Exclude self
              Booking.status.in_([StatusEnum.PENDING, StatusEnum.CONFIRMED]),
              # Overlap detection
              and_(
                  Booking.start_date <= new_end_date,
                  Booking.end_date >= new_start_date
              )
          )
      )
  )
  ```
- **Return code:** 400 Bad Request with conflict details

#### BR-001: Whole-Day Bookings (Date Validation)
- **What to implement:** Reopen validates date range with inclusive end date
  - Calculation: `total_days = new_end_date - new_start_date + 1`
  - End date must be >= start date
  - Check: `end_date >= start_date` constraint already in schema
- **Database:** Schema CHECK constraint enforces this
- **Validation:** Client-side and server-side checks

#### BR-005: Edit While Pending (Approval Impact)
- **What to implement:** Understand that reopen is like extending dates (resets approvals)
  - Reopening always resets approvals (regardless of date change direction)
  - Compare with edit: shortening keeps approvals, extending resets
  - Reopen: always reset (even if dates didn't change)
- **Database:** Set all `approval.decision = NoResponse`
- **Notification:** Re-approval emails sent showing date changes (old → new)

#### BR-014: Past Items Read-Only
- **What to implement:** Cannot reopen past Denied bookings
  - Validation: `booking.end_date >= date.today()`
  - Error: "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."
- **Database:** WHERE clause filter
- **Return code:** 400 Bad Request

#### BR-010: Idempotent Action Links
- **What to implement:** Reopening twice = same result
  - If already Pending (from first reopen), second reopen with same dates = idempotent
  - Return success with "Schon erledigt" message
  - No duplicate timeline events
- **Database:** Check if `booking.status == Pending` before reopening
  - If already Pending, return success with context message
  - If Denied, transition to Pending and create timeline event
- **Note:** If dates changed between two reopen attempts, might be a conflict (reject second)

#### BR-015: Self-Approval (Reopen Logic)
- **What to implement:** If requester is an approver, auto-approval applies again
  - After reopen, all approvals = NoResponse
  - If requester is Ingeborg, immediately set Ingeborg's approval to Approved
  - Same as submission logic (implemented in create, reuse here)
- **Database:**
  ```python
  if booking.requester_email == APPROVER_EMAILS[booking.affiliation]:
      approval = get_approval(booking.affiliation)
      approval.decision = DecisionEnum.APPROVED
      approval.decided_at = now()
  ```
- **Logic:** Happens after resetting all to NoResponse, then re-apply self-approval

#### BR-002: No Overlaps (Conflict Detection)
- **What to implement:** Use same overlap detection as booking creation
  - Reopen with new dates must not conflict with Pending/Confirmed (other than self)
  - Uses GiST index on date ranges (fast)
- **Database:** Same query as BR-018
- **Performance:** GiST index `idx_bookings_date_range` on `daterange(start_date, end_date, '[]')`

#### BR-029: First-Write-Wins (Concurrency)
- **What to implement:** Serialize reopen with overlapping create/extend operations
  - Both must check conflicts in a transaction
  - First to persist wins, second gets conflict error
  - Use SELECT FOR UPDATE on conflicting bookings (if available)
- **Database:** Transaction with conflict check
  - Order: lock → check conflicts → update
- **Implementation:** Similar to create endpoint (already in Phase 2)

#### BR-023: Approver Lists (View Impact)
- **What to implement:** After reopen, item appears in Outstanding (all approvals = NoResponse)
  - Moves from Denied view back to Outstanding
  - All approvers see in their Outstanding lists
- **Database:** No direct change
- **Query impact:** Outstanding lists now include this booking (because decision = NoResponse)

### Edge Cases (Must Test)

1. **Reopen without changing dates** - Success, all approvals reset
2. **Reopen with new dates (no conflict)** - Success, all approvals reset, dates updated
3. **Reopen with new dates (conflict)** - Error: conflict message
4. **Reopen on non-Denied booking** - Error: cannot reopen Pending/Confirmed/Canceled
5. **Reopen on past Denied booking** (end_date < today) - Error: "Dieser Eintrag liegt in der Vergangenheit..."
6. **Reopen twice with same dates** - Idempotent, returns "Schon erledigt"
7. **Reopen twice with different dates** - Second might conflict, returns error
8. **Reopen resets all three approvals** - Verify all are NoResponse after reopen
9. **Reopen triggers re-approval emails** - Notifications sent with date diffs
10. **Reopen with self-approver** - Auto-approval applies again (one of three already approved)
11. **Reopen updates last_activity_at** - Timestamp changes
12. **Reopen generates timeline event** - Audit includes action, maybe date diff
13. **Reopen date validation (end >= start)** - Constraint enforced
14. **Reopen with multi-month dates** - Spanning multiple months works
15. **Reopen with shortened dates** - Dates reduced but still valid
16. **Reopen with extended dates** - Dates extended (might retest long-stay warning)
17. **Invalid token fails** - BR-010
18. **Reopen requires requester token** - Approvers cannot reopen (role validation)

### Estimated Test Count: 18

**Backend Tests (pytest):**

1. `test_reopen_without_changing_dates` - BR-004
2. `test_reopen_changes_status_to_pending` - BR-004
3. `test_reopen_resets_all_approvals` - BR-004
4. `test_reopen_with_conflicting_dates_fails` - BR-018
5. `test_reopen_with_new_non_conflicting_dates` - BR-018
6. `test_reopen_on_past_denied_booking_fails` - BR-014
7. `test_reopen_on_non_denied_booking_fails` - State validation
8. `test_idempotent_reopen_same_dates` - BR-010
9. `test_idempotent_reopen_different_dates_conflicts` - BR-010 + BR-018
10. `test_reopen_self_approval_auto_applies` - BR-015
11. `test_reopen_generates_timeline_event` - Audit
12. `test_reopen_updates_last_activity_at` - Timestamp
13. `test_reopen_date_validation_end_after_start` - BR-001
14. `test_reopen_with_multi_month_dates` - Edge case
15. `test_reopen_with_shortened_dates` - Edge case
16. `test_reopen_with_extended_dates` - Edge case
17. `test_reopen_removed_from_denied_view` - BR-023
18. `test_requester_only_can_reopen` - Role validation

---

## Test Matrix Summary

### Complete Test Count by User Story

| User Story | Category | Count | Details |
|-----------|----------|-------|---------|
| **US-3.1** | Core Logic | 4 | Approve, Final, Idempotent, Status transition |
| **US-3.1** | Validation | 3 | Past items, Denied state, Confirmed state |
| **US-3.1** | Concurrency | 1 | First-action-wins (BR-024) |
| **US-3.1** | Business Rules | 2 | Self-approval, Outstanding list |
| **US-3.1** | Audit/UX | 4 | Timeline, Last activity, Response message, Invalid token |
| **US-3.1 Subtotal** | | **14** | |
| | | | |
| **US-3.2** | Core Logic | 3 | Deny with comment, Status change, Idempotent |
| **US-3.2** | Validation | 5 | No comment, Links in comment, Past items, Confirmed deny, Canceled |
| **US-3.2** | Concurrency | 2 | Approval + denial, Multiple denials |
| **US-3.2** | Business Rules | 2 | Outstanding list, Calendar filtering |
| **US-3.2** | Audit/UX | 5 | Timeline event, Last activity, Comment storage, Message content, Token |
| **US-3.2 Subtotal** | | **17** | |
| | | | |
| **US-3.3** | Core Logic | 3 | Reopen basic, Status change, Reset approvals |
| **US-3.3** | Validation | 4 | Conflict detection, Non-Denied state, Past items, Date validation |
| **US-3.3** | Idempotency | 2 | Same dates, Different dates |
| **US-3.3** | Business Rules | 2 | Self-approval reapply, Outstanding view impact |
| **US-3.3** | Concurrency | 1 | First-write-wins (BR-029) |
| **US-3.3** | Edge Cases | 5 | Multi-month, Shortened, Extended, Requester only, Last activity |
| **US-3.3 Subtotal** | | **18** | |
| | | | |
| **TOTAL PHASE 3** | | **49** | Full approval flow coverage |

### Test Distribution by Business Rule

| BR | Count | Tests |
|----|-------|-------|
| BR-001 | 1 | Reopen date validation |
| BR-002 | 2 | Reopen conflict, Concurrent writes |
| BR-003 | 2 | Final approval, Approval count |
| BR-004 | 6 | Deny logic, Deny Confirmed, Reopen, State validation |
| BR-005 | 1 | Approval reset on reopen |
| BR-009 | 0 | (Phase 4 - digest impact, but documented) |
| BR-010 | 6 | Idempotent approval, idempotent deny, idempotent reopen |
| BR-014 | 3 | Approve past, Deny past, Reopen past |
| BR-015 | 2 | Self-approval approve, self-approval reopen |
| BR-018 | 2 | Reopen conflict detection |
| BR-020 | 1 | Link detection in deny comment |
| BR-022 | 0 | (Phase 4 - retry logic, but documented) |
| BR-023 | 3 | Outstanding list updates |
| BR-024 | 3 | Concurrent approval/denial |
| BR-029 | 1 | First-write-wins for reopen |
| **Other** | 15 | Schema validation, timeline events, timestamps, token validation |
| **TOTAL** | **49** | |

---

## Implementation Impact Summary

### Database Changes Required

**No new tables or columns needed.** Phase 1 (data layer) already provides:
- `bookings` table with status enum
- `approvals` table with decision enum and comment field
- `timeline_events` table for audit trail

**Critical Operations:**
- SELECT FOR UPDATE on booking (BR-024 concurrency)
- UPDATE approvals with decision and decided_at
- INSERT timeline_events
- UPDATE booking.status and last_activity_at

### API Endpoints

**Three new endpoints:**

1. **POST /api/v1/bookings/{id}/approve?token=xxx**
   - No request body
   - Returns approval result with decision count + remaining parties

2. **POST /api/v1/bookings/{id}/deny?token=xxx**
   - Request: `{"comment": "..."}`
   - Validation: comment required, no links, <= 500 chars
   - Returns denial result

3. **POST /api/v1/bookings/{id}/reopen?token=xxx**
   - Request: `{"start_date": "2025-08-01", "end_date": "2025-08-05"}`
   - Validation: dates required, no conflicts, end >= start
   - Returns reopen result

### Critical Implementation Details

#### Concurrency & Transactions

- **BR-024 (First-Action-Wins):** Use `SELECT ... FOR UPDATE` on booking row
  - Lock prevents concurrent approval/denial race conditions
  - Serialize all approval-related actions

- **BR-029 (First-Write-Wins):** Reopen must check conflicts in transaction
  - Similar to create booking (Phase 2)
  - All conflict checks must happen within transaction

#### Idempotency & Result Messages

- **BR-010 requires context-aware responses:**
  - "Danke – du hast zugestimmt." (first approve, not final)
  - "Danke – du hast zugestimmt. Alles bestätigt!" (first approve, final)
  - "Schon erledigt. Die Buchung ist bereits bestätigt." (idempotent approve)
  - "Erledigt – du hast abgelehnt..." (first deny)
  - "Schon erledigt. Die Anfrage ist jetzt abgelehnt..." (idempotent deny)
  - "Schon erledigt. {{Partei}} hat bereits abgelehnt..." (denial happened first)

#### Timeline Events

Create events for:
- `Approved` - When approving
- `Denied` - When denying (note = comment)
- `Confirmed` - When status transitions to Confirmed (not on every approval, just when final)
- `Reopened` - When reopening (maybe note = date diff)

#### German Copy (All Exact from Specs)

**Error messages:** From `docs/specification/error-handling.md`
- Past items: "Dieser Eintrag liegt in der Vergangenheit..."
- Links: "Links sind hier nicht erlaubt..."
- Comment required: "Bitte gib einen kurzen Grund an."
- Conflicts: "Dieser Zeitraum überschneidet sich..."

**Result page messages:** From `docs/specification/notifications.md`
- Success approval: Various, depending on final/non-final
- Success deny: "Erledigt – du hast abgelehnt..."
- Already done: "Schon erledigt. ..." (context dependent)

### Pre-Implementation Checklist

- [ ] Understand ALL 17 applicable BRs and their interactions
- [ ] Review Phase 2 models (Booking, Approval, TimelineEvent)
- [ ] Plan transaction strategy for concurrency (SELECT FOR UPDATE)
- [ ] Identify all German copy from specs
- [ ] Design test cases for all 49 tests
- [ ] Map response message logic (context-dependent)
- [ ] Verify timeline event types
- [ ] Check constraint validation (dates, comment length, link detection)
- [ ] Plan idempotency implementation strategy
- [ ] Review BR-024 and BR-029 transaction requirements

---

## Next Steps

1. **Read this analysis** (you're doing it now!)
2. **Start Phase 3 implementation:**
   - Write all 49 tests FIRST (test-first approach)
   - Verify tests fail
   - Implement endpoints until all tests pass
   - Type check, lint, coverage check
3. **Reference this matrix** for test coverage tracking
4. **Move to Phase 4** once all tests pass (Email Integration)

---

## Related Documentation

- **Business Rules:** `/home/user/btznstn/docs/foundation/business-rules.md` (BR-001 to BR-029)
- **Phase 3 Spec:** `/home/user/btznstn/docs/implementation/phase-3-approval-flow.md`
- **Error Messages:** `/home/user/btznstn/docs/specification/error-handling.md`
- **Email Templates:** `/home/user/btznstn/docs/specification/notifications.md`
- **Database Schema:** `/home/user/btznstn/docs/design/database-schema.md`
- **API Spec:** `/home/user/btznstn/docs/design/api-specification.md`
