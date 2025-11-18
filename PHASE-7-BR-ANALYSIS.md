# Phase 7: Approver Interface - Business Rules Analysis

**Date:** 2025-11-17
**Phase:** 7 (Approver Interface - Frontend)
**User Stories:** US-7.1, US-7.2, US-7.3

---

## Executive Summary

Phase 7 implements the approver-facing interface for reviewing and acting on pending bookings. This phase is heavily constrained by approval-related business rules (BR-003, BR-004, BR-010, BR-015, BR-024) and visibility rules (BR-023, BR-014).

**Key Testing Complexity:** Concurrency (BR-024 first-action-wins), idempotency (BR-010), and state-dependent actions (BR-004 Denied bookings).

**Estimated Total Playwright Tests:** 37-42 tests across three user stories

---

## US-7.1: Approver Overview

**Feature:** View outstanding approval requests and historical approvals

### Applicable Business Rules

| BR | Rule | Implementation Impact | Test Focus |
|----|------|--------|------|
| **BR-003** | Three fixed approvers (Ingeborg, Cornelia, Angelika) | Token must validate to one of 3 approvers; UI shows no other approvers | Token validation; guard against missing approvers |
| **BR-004** | Denial handling (Denied status = non-blocking, hidden from public, non-actionable) | History tab MUST include Denied bookings; Outstanding must exclude Denied (no action possible) | Denied visible in History; absent from Outstanding |
| **BR-010** | Tokens never expire, no revocation, links always idempotent | Token access to /approver?token=xxx never fails due to age; repeat visits work | Token persistence; no expiry checks |
| **BR-014** | Past items read-only (EndDate < today → no approvals/denials) | Disable action buttons for past bookings; visual "read-only" indicator | Disable approve/deny for past; allow viewing only |
| **BR-023** | Approver lists: Outstanding = NoResponse+Pending (sorted LastActivityAt DESC); History = All items (all statuses) sorted LastActivityAt DESC | Two separate queries with CORRECT filtering and sorting; critical for UX | Sorting order; filtering by approver response; status filtering |
| **BR-015** | Self-approval (if requester is approver, auto-approve at submission) | Self-approved bookings visible in Outstanding/History; approver can see their own auto-approval; may see "Pending" → "Approved" transition | Self-approval case in both tabs; verify auto-approval visible |

### Why Each BR Matters for US-7.1

**BR-003:** Access control - ensures only the 3 approvers can use this interface. Token must validate server-side.

**BR-004:** Status filtering - Denied bookings must appear in History (readonly) but NOT in Outstanding (because approver cannot act on them). Critical for correct tab behavior.

**BR-010:** Token lifecycle - tokens are permanent, so no "expired token" error possible. Approvers never lose access.

**BR-014:** State machine enforcement - past bookings cannot be approved/denied; UI must disable actions. This is a critical constraint because approvers might try to act on old items.

**BR-023:** Query correctness - this is the MOST CRITICAL BR for Phase 7. Wrong queries = wrong data shown. Outstanding must show ONLY items where `approver.response = NoResponse AND booking.status = Pending`. History must show ALL statuses. BOTH must be sorted `LastActivityAt DESC`.

**BR-015:** Approver as requester edge case - if Ingeborg approves her own booking, she sees the booking in Outstanding (because it's Pending) but her approval is auto-applied. She can still manually click "Approve" (idempotent per BR-010).

### Edge Cases to Test

#### Token & Access
1. **Invalid token** - 404 or redirect to recovery
2. **Wrong approver token** - sees different approver's outstanding (must verify each approver sees ONLY their own items)
3. **Token with special characters** - validate encoding
4. **Expired session cookie** (if applicable) - recovery flow

#### BR-023 Query Correctness (CRITICAL)
5. **Outstanding list accuracy** - verify ONLY `response=NoResponse AND status=Pending` appears
6. **Outstanding ordering** - verify sorted by `LastActivityAt DESC` (most recent activity first)
   - Edge: Two bookings with same LastActivityAt - tiebreaker? (check ID or submission order)
7. **Outstanding count accuracy** - if 5 Pending where approver=NoResponse, show 5; not 4, not 6
8. **History list includes all statuses** - Pending, Confirmed, Denied (NOT Canceled - in Archive)
   - Edge: Confirmed booking created by this approver appears in History
9. **History ordering** - sorted by `LastActivityAt DESC`
10. **Multi-status history** - book starts Pending (in History), gets approved (still in History), confirmed (still in History)

#### BR-004 Denied Handling
11. **Denied booking NOT in Outstanding** - even if approver hasn't acted, Denied is not actionable
12. **Denied booking visible in History** - shows full audit trail
13. **Denied booking shows denial comment** - approver can see why it was denied

#### BR-014 Past Items
14. **Past booking in Outstanding** - shouldn't happen, but if it does, show disabled action buttons
15. **Past booking visual indicator** - e.g., "read-only" badge or grayed out
16. **Cannot click approve/deny on past booking** - button disabled or no-op

#### BR-015 Self-Approval
17. **Self-approver sees their own booking in Outstanding** - Pending status visible
18. **Self-approver can manually approve again** - second click is idempotent
19. **Self-approver's approval already counted** - if 2/3 need to approve, only 1 more needed

#### UI/UX Edge Cases
20. **Empty Outstanding list** - message: "Keine ausstehenden Anfragen."
21. **Empty History list** - message: "Noch keine Aktivität."
22. **Zero bookings for this approver** - both tabs empty
23. **Infinite scroll pagination** - load 20 items, scroll loads more
24. **Slow load** - skeleton UI, no jank
25. **Refresh/back-to-tab** - state preserved, not re-fetched unnecessarily

#### Mobile-Specific (375px)
26. **Outstanding tab on iPhone 8** - readable, tappable, no horizontal scroll
27. **Affiliation colors visible on mobile** - distinguish three approvers' bookings
28. **Status badge on mobile** - clear contrast, readable
29. **List items touch-friendly** - 44×44pt minimum

### German Copy References

- **Button labels:** `docs/specification/ui-screens.md` lines 284-286
- **Tab titles:** "Ausstehend" / "Verlauf" (Outstanding / History)
- **Empty state Outstanding:** "Keine ausstehenden Anfragen." (line 507)
- **Empty state History:** "Noch keine Aktivität." (line 511)

### Estimated Playwright Test Count: 13-15 tests

```
Happy Path Tests (2):
  ✓ Load Outstanding tab, display pending bookings
  ✓ Load History tab, display all bookings

BR-003 Access Control (2):
  ✓ Token validation (valid token loads)
  ✓ Invalid token (404 or redirect)

BR-023 Sorting & Filtering (4):
  ✓ Outstanding filters by NoResponse + Pending
  ✓ Outstanding sorts by LastActivityAt DESC
  ✓ History includes Pending, Confirmed, Denied
  ✓ History sorts by LastActivityAt DESC

BR-004 Denied Handling (2):
  ✓ Denied booking visible in History
  ✓ Denied booking absent from Outstanding

BR-014 Past Items (1):
  ✓ Past booking has disabled actions

BR-015 Self-Approval (1):
  ✓ Self-approver sees own booking in Outstanding

Edge Cases (2):
  ✓ Empty Outstanding list shows correct message
  ✓ Infinite scroll loads more items

Mobile (1):
  ✓ Outstanding/History tabs responsive on 375px

TOTAL: 15 tests
```

---

## US-7.2: One-Click Approve

**Feature:** Approver approves a booking with one click (from email or overview)

### Applicable Business Rules

| BR | Rule | Implementation Impact | Test Focus |
|----|------|--------|------|
| **BR-003** | Three fixed approvers | Token must match one of 3; invalid token rejects | Token validation |
| **BR-004** | Denial handling | Cannot approve Denied booking; show "Schon erledigt – abgelehnt" | State check before approval |
| **BR-010** | Tokens idempotent, links always redirect to result page | Approve twice = success both times; show "Schon erledigt" if already approved | Idempotency per BR-010 |
| **BR-014** | Past items read-only | Cannot approve past booking (EndDate < today) | Reject approval, show error |
| **BR-015** | Self-approval auto-applied | If requester is approver, auto-approved at submission; but approver can still click (idempotent) | Verify auto-approval; second click shows success |
| **BR-023** | Approver lists | After approval, if 3rd approval → Confirmed (moves from Outstanding to History) | Booking disappears from Outstanding after final approval |
| **BR-024** | First-action-wins | If two approvers simultaneously approve, first persists; second sees "Schon erledigt – bereits bestätigt" | Race condition handling; SELECT FOR UPDATE |

### Why Each BR Matters for US-7.2

**BR-003:** Only 3 approvers can perform approvals. Invalid token must be rejected before any action.

**BR-004:** Denied bookings are terminal for approvers - they cannot reverse a denial. If booking is Denied, approval request is invalid; show idempotent error.

**BR-010:** CRITICAL FOR UX - users often retry failed clicks (slow network, app crash). Approval must be idempotent: same result every time, always shows success page with "Danke – du hast zugestimmt".

**BR-015:** If Ingeborg creates a booking and Ingeborg is an approver, she auto-approves herself. Her approval is already recorded. She can click "Approve" again → same result (idempotent).

**BR-023:** After approval, if final (3rd) approval received → Confirmed. Booking must disappear from Outstanding (because status != Pending). Must re-query or remove from view.

**BR-024:** CRITICAL FOR CONCURRENCY - Two approvers clicking approve simultaneously. First transaction persists, second must detect and show "Schon erledigt – bereits bestätigt" (per BR-024 message templates, line 141-145 of business-rules.md).

**BR-014:** Cannot approve past bookings. Must reject with error message.

### Edge Cases to Test

#### Idempotency (BR-010)
1. **Approve same booking twice** - both times success, show "Danke – du hast zugestimmt"
2. **Network timeout on first approval, click again** - idempotent, not double-submitted
3. **Approve from email link twice** - both clicks show result page with success
4. **Approve, refresh page, approve again** - idempotent
5. **Approve while navigation pending** - no race with list reload

#### First-Action-Wins (BR-024)
6. **Two approvers click approve simultaneously** - first persists, second sees "Schon erledigt – bereits bestätigt"
7. **Approve while another denies** - first action wins (approve persists, deny sees "Schon erledigt")
8. **Approve Confirmed booking** - shows "Schon erledigt – bereits bestätigt" (idempotent)

#### BR-004 Denied State
9. **Approve Denied booking** - error "Schon erledigt – {{Partei}} hat bereits abgelehnt – die Anfrage ist jetzt abgelehnt (nicht öffentlich)."
10. **Approve after booking denied between page load and click** - race condition, show error

#### BR-014 Past Items
11. **Approve booking with EndDate = today** - allowed (becomes past tomorrow at 00:00 Berlin time)
12. **Approve booking with EndDate = yesterday** - error "Diese Anfrage ist bereits abgelaufen."
13. **Approve during timezone transition** - boundary test at 00:00 Europe/Berlin

#### BR-015 Self-Approval
14. **Self-approver sees auto-approval already counted** - progress bar shows 2/3 if only 1 more needed
15. **Self-approver clicks approve anyway** - idempotent success (BR-010)

#### BR-023 List Update
16. **Approve, Outstanding list auto-updates** - booking disappears or moves to History
17. **Final approval (3rd) → Confirmed transition** - booking appears as Confirmed in History
18. **Partial approval (1st of 3)** - still in Outstanding for other 2 approvers

#### Result Page (BR-010)
19. **Result page displays "Danke – du hast zugestimmt"** - exact German copy from spec
20. **Result page has link back to approver overview** - can continue with other bookings
21. **Result page mobile-friendly** - 375px viewport

#### Error Cases
22. **Invalid token** - 404 or redirect to recovery
23. **Token belongs to wrong approver** - 403 or redirect
24. **Booking doesn't exist** - 404
25. **Booking is Canceled** - show appropriate error (not actionable)

#### Performance
26. **Approve updates downstream correctly** - email to requester sent (if 3/3), no duplicates
27. **No N+1 queries** - single approval fetches all 3 approvals

### German Copy References

From `docs/specification/notifications.md` and `ui-screens.md`:

- **Result page:** "Danke – du hast zugestimmt" (line 38 in phase-7)
- **Button label:** "Zustimmen" (line 36 in phase-7)
- **Already confirmed:** "Schon erledigt. Die Buchung ist bereits bestätigt." (line 144, business-rules.md)
- **Already denied:** "Schon erledigt. {{Partei}} hat bereits abgelehnt – die Anfrage ist jetzt abgelehnt (nicht öffentlich)." (line 145, business-rules.md)

### Estimated Playwright Test Count: 14-16 tests

```
Happy Path (2):
  ✓ Approve from email link, show result page
  ✓ Approve from outstanding list, booking disappears

BR-003 Validation (1):
  ✓ Invalid token rejects approval

BR-010 Idempotency (4):
  ✓ Approve twice shows success both times
  ✓ Network retry (timeout then retry) is idempotent
  ✓ Approve from email link twice is idempotent
  ✓ Result page has back link to overview

BR-024 First-Action-Wins (3):
  ✓ Two simultaneous approves, first wins
  ✓ Approve vs deny simultaneously, first wins
  ✓ Approve already-approved shows "Schon erledigt"

BR-004 Denied State (1):
  ✓ Cannot approve Denied booking (shows error)

BR-014 Past Items (1):
  ✓ Cannot approve past booking

BR-015 Self-Approval (1):
  ✓ Self-approver can approve again (idempotent)

BR-023 List Updates (1):
  ✓ After final approval, booking moves to History

Mobile (1):
  ✓ Result page responsive on 375px

TOTAL: 15 tests
```

---

## US-7.3: Deny with Comment

**Feature:** Approver denies booking with required comment

### Applicable Business Rules

| BR | Rule | Implementation Impact | Test Focus |
|----|------|--------|------|
| **BR-004** | Denial handling (comment required, status → Denied, non-blocking, not public) | Show comment dialog; validate comment provided; transition booking to Denied | Comment dialog; Denied status transition |
| **BR-010** | Idempotent links | Deny twice = success both times; show "Schon erledigt" with context | Idempotency of denial action |
| **BR-014** | Past items read-only | Cannot deny past booking | Disable deny button for past |
| **BR-020** | Link detection (block http://, https://, www, mailto:) | Validate comment for blocked patterns; reject if found | Link blocking validation |
| **BR-023** | Approver lists | After denial, booking removed from Outstanding, appears in History | Booking disappears from Outstanding |
| **BR-024** | First-action-wins | Two denials or approve+deny simultaneously → first persists, second sees error | Race condition with SELECT FOR UPDATE |
| **BR-004 (post-confirm)** | Deny Confirmed requires warning dialog | If Confirmed, show warning before allowing denial (per BR-004 post-confirm) | Warning dialog for Confirmed denial |

### Why Each BR Matters for US-7.3

**BR-004:** Core rule for denial - comment is required and stored. Denial immediately frees dates (non-blocking). Hidden from public view. Critical UI: must force comment entry before submission.

**BR-010:** Denial is idempotent - if network fails and user retries, same result (already denied). Must show "Schon erledigt – bereits abgelehnt" on retry.

**BR-014:** Cannot deny past bookings. UI must disable button or reject action.

**BR-020:** CRITICAL - prevent spam/phishing by blocking URLs in comments. Must validate before accepting.

**BR-023:** After denial, booking status changes so it's no longer in Outstanding (status != Pending). Must update list or re-fetch.

**BR-024:** Two denials simultaneously → first persists. Second must detect and show idempotent error. Two deniers shouldn't both record the same denial.

**BR-004 (post-confirm):** If booking is already Confirmed, show warning dialog before allowing denial (per spec line 213-218 of ui-screens.md).

### Edge Cases to Test

#### Comment Validation
1. **No comment provided** - error "Bitte gib einen kurzen Grund an." (from phase-7, line 55)
2. **Comment is whitespace only** - error (treat as empty)
3. **Comment with URL (http://)** - error "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden." (BR-020)
4. **Comment with https://** - error (BR-020)
5. **Comment with www** - error (BR-020)
6. **Comment with mailto:** - error (BR-020)
7. **Comment exactly 500 chars** - allowed
8. **Comment 501+ chars** - error "Text ist zu lang (max. 500 Zeichen)."
9. **Comment with German umlaut ä, ö, ü** - allowed
10. **Comment with newlines** - allowed (not blocked like Description in BR-020)
11. **Comment with emoji** - allowed (not blocked)

#### Idempotency (BR-010)
12. **Deny twice, both succeed** - show "Danke – du hast abgelehnt" both times
13. **Deny, network timeout, retry** - idempotent, same result
14. **Deny from email link twice** - both show success
15. **Deny after another approver denies** - second sees "Schon erledigt – bereits abgelehnt"

#### BR-004 Denial Effects
16. **Dates freed immediately** - calendar shows dates as available after denial
17. **Not shown on public calendar** - Denied booking hidden (BR-004)
18. **Requester can see denial comment** - full timeline visible to requester
19. **Deny Confirmed booking shows warning** - "Buchung ist bereits bestätigt" dialog (spec line 213-218)
20. **Deny Confirmed requires comment** - same as Pending

#### BR-024 Race Conditions
21. **Two approvers deny simultaneously** - first persists, second sees idempotent error
22. **Deny while other approves** - first action wins
23. **Deny while booking transitions to Confirmed** - race condition, show appropriate error

#### BR-014 Past Items
24. **Deny booking with EndDate = today** - allowed (becomes past tomorrow)
25. **Deny booking with EndDate = yesterday** - error "Diese Anfrage ist bereits abgelaufen."
26. **Deny button disabled for past bookings** - visual disable

#### BR-023 List Updates
27. **After denial, booking removed from Outstanding** - no longer in action list
28. **After denial, booking appears in History as Denied** - full audit trail visible
29. **Denial affects other approvers' Outstanding** - booking still shows for those not yet acted

#### Dialog/UX
30. **Comment dialog opens on "Ablehnen" click** - shows input field, not inline
31. **Cancel button closes dialog without action** - booking still Pending
32. **Dialog shows booking context** - which booking is being denied
33. **Submit button in dialog labeled correctly** - "Ja, ablehnen" or similar

#### Email Notifications
34. **Requester notified of denial** - email with comment and context
35. **Other approvers notified** - reduced set if booking already denied
36. **Self-denial** - requester receives their own denial (edge case)

#### Mobile
37. **Comment dialog on 375px** - readable, tappable, full keyboard support
38. **Textarea with mobile keyboard** - works on iOS/Android

#### Error Handling
39. **Network error on denial submit** - graceful retry, idempotent
40. **Booking deleted between load and deny** - show 404
41. **Token expires between load and deny** - unlikely per BR-010, but handle gracefully

### German Copy References

From `docs/specification/ui-screens.md`, `error-handling.md`, and `phase-7-approver-interface.md`:

- **Button label:** "Ablehnen" (line 52 in phase-7)
- **Dialog title (Pending):** "Grund für Ablehnung" or similar (check error-handling.md)
- **Dialog title (Confirmed):** "Buchung ist bereits bestätigt" (line 213, ui-screens.md)
- **Dialog body (Confirmed):** "Du möchtest eine bereits bestätigte Buchung ablehnen. Bist du sicher? Bitte gib einen kurzen Grund an." (line 215, ui-screens.md)
- **Empty comment error:** "Bitte gib einen kurzen Grund an." (line 55, phase-7)
- **Link blocked error:** "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden." (line 367, error-handling.md / BR-020)
- **Result page:** "Danke – du hast abgelehnt" (implied, similar to approve)

### Estimated Playwright Test Count: 15-18 tests

```
Happy Path (1):
  ✓ Deny with comment, show result page

BR-004 Denial (3):
  ✓ Comment dialog opens and requires comment
  ✓ Deny Confirmed shows warning dialog
  ✓ Dates freed after denial (calendar check)

BR-010 Idempotency (2):
  ✓ Deny twice shows success both times
  ✓ Network retry is idempotent

BR-020 Link Blocking (5):
  ✓ Block http:// in comment
  ✓ Block https:// in comment
  ✓ Block www in comment
  ✓ Block mailto: in comment
  ✓ Allow umlaut/emoji/newline

BR-024 First-Action-Wins (2):
  ✓ Two simultaneous denials, first wins
  ✓ Approve vs deny, first action wins

BR-014 Past Items (1):
  ✓ Cannot deny past booking

BR-023 List Updates (1):
  ✓ After denial, booking removed from Outstanding

Comment Validation (2):
  ✓ Empty comment rejected
  ✓ 500+ char comment rejected

Mobile (1):
  ✓ Comment dialog responsive on 375px

TOTAL: 18 tests
```

---

## Cross-Story Test Matrix

### Concurrency Tests (BR-024 First-Action-Wins)

These tests involve multiple approvers acting on same booking simultaneously:

| Test Scenario | US-7.2 (Approve) | US-7.3 (Deny) | Implementation Notes |
|---|---|---|---|
| Approver A approves, Approver B approves simultaneously | ✓ | - | First to persist wins; second sees "Schon erledigt" |
| Approver A approves, Approver B denies simultaneously | ✓ | ✓ | First action wins; second sees appropriate error |
| Approver A denies, Approver B denies simultaneously | - | ✓ | First denial persists; second sees "Schon erledigt" |
| Approver A denies, Approver B tries to approve | ✓ | - | First (deny) persists; second (approve) sees "Schon erledigt – abgelehnt" |

**Implementation Pattern (Backend):**
- Use `SELECT FOR UPDATE` to lock booking row
- Check current state before allowing action
- Atomically update approval and booking status
- Detect if state changed since user loaded page

**Playwright Pattern:**
- Simulate concurrent actions with Promise.all()
- Verify one succeeds, other shows error
- Check final state is consistent

### Token & Security Tests (BR-003, BR-010)

| Test | US-7.1 | US-7.2 | US-7.3 | Notes |
|---|---|---|---|---|
| Valid token loads interface | ✓ | ✓ | ✓ | No expiration per BR-010 |
| Invalid token rejected | ✓ | ✓ | ✓ | 404 or redirect to recovery |
| Wrong approver token | ✓ | ✓ | ✓ | Each approver sees only their items |
| Token with encoding issues | ✓ | ✓ | ✓ | URL decode properly |

### State Machine Tests (BR-004, BR-014, BR-023)

| State | US-7.1 (View) | US-7.2 (Approve) | US-7.3 (Deny) | Notes |
|---|---|---|---|---|
| Pending | Outstanding + History | ✓ Allow approve | ✓ Allow deny | Normal flow |
| 1/3 Approved | Outstanding + History | ✓ Allow approve | ✓ Allow deny | Continued action |
| 2/3 Approved | Outstanding + History | ✓ Allow approve (final) | ✓ Allow deny | Approval to Confirmed |
| Confirmed | History only (not Outstanding) | Show "Schon erledigt" | ✓ Allow deny (with warning) | Cannot approve again |
| Denied | History only (not Outstanding) | Show error "abgelehnt" | Show "Schon erledigt" | Terminal state for others |
| Past (EndDate < today) | View-only, disabled buttons | Show error, disabled | Show error, disabled | BR-014 enforcement |

### German Copy Accuracy Tests

All German text must be exact from specifications:

| Element | Source | Phase 7 Usage | Test |
|---|---|---|---|
| Tab names | `ui-screens.md` line 255-265 | "Ausstehend" / "Verlauf" | String match |
| Empty Outstanding | `ui-screens.md` line 507 | "Keine ausstehenden Anfragen." | Exact copy |
| Empty History | `ui-screens.md` line 511 | "Noch keine Aktivität." | Exact copy |
| Approve button | `ui-screens.md` line 204 | "Zustimmen" | Exact copy |
| Approve result | `phase-7-approver-interface.md` line 38 | "Danke – du hast zugestimmt" | Exact copy |
| Deny button | `ui-screens.md` line 208 | "Ablehnen" | Exact copy |
| Comment required | `phase-7-approver-interface.md` line 55 | "Bitte gib einen kurzen Grund an." | Exact copy |
| Link blocked | `error-handling.md` line 367 | "Links sind hier nicht erlaubt..." | Exact copy |
| Already confirmed | `business-rules.md` line 144 | "Schon erledigt. Die Buchung ist bereits bestätigt." | Exact copy |
| Already denied | `business-rules.md` line 145 | "Schon erledigt. {{Partei}} hat bereits abgelehnt..." | Exact copy |

---

## Implementation Checklist

### Pre-Implementation (REQUIRED)

- [ ] All applicable BRs identified above confirmed with team
- [ ] German copy extracted and verified against specifications
- [ ] Data model reviewed:
  - Approval table structure (response: NoResponse|Approved|Denied)
  - Booking status enum (Pending|Confirmed|Denied|Canceled)
  - LastActivityAt timestamp behavior
  - Token validation logic
- [ ] Query patterns defined for:
  - Outstanding (NoResponse + Pending, sorted LastActivityAt DESC)
  - History (All statuses, sorted LastActivityAt DESC)
- [ ] Concurrency handling strategy documented (SELECT FOR UPDATE)
- [ ] Error message mapping created (all German errors)

### Test-First Development

**Must write tests BEFORE implementation:**

- [ ] **Outstanding tab tests** (7 tests)
  - Load with valid token
  - Filter by NoResponse + Pending
  - Sort by LastActivityAt DESC
  - Exclude Denied bookings
  - Empty state message
  - Past bookings disabled
  - Mobile responsive

- [ ] **History tab tests** (6 tests)
  - Load with valid token
  - Include Pending, Confirmed, Denied (not Canceled)
  - Sort by LastActivityAt DESC
  - Show all statuses
  - Empty state message
  - Mobile responsive

- [ ] **Approve tests** (13 tests)
  - Email link approve → result page
  - Overview list approve → disappears
  - Idempotent (approve twice)
  - BR-024 race (two simultaneous approves)
  - BR-004 error (cannot approve Denied)
  - BR-014 error (cannot approve past)
  - BR-015 self-approval visible
  - BR-023 final approval → Confirmed
  - Invalid token
  - Mobile result page
  - Network retry idempotent
  - Already-confirmed shows "Schon erledigt"
  - Approve Denied shows error message

- [ ] **Deny tests** (16 tests)
  - Comment dialog required
  - Comment validation (empty, too long)
  - BR-020 link blocking (http, https, www, mailto)
  - BR-004 Denied status transition
  - BR-004 Confirmed warning dialog
  - BR-010 idempotent deny
  - BR-024 race (two simultaneous denies)
  - BR-014 error (past booking)
  - BR-023 removed from Outstanding
  - Result page "Danke – du hast abgelehnt"
  - Invalid token
  - Mobile comment dialog
  - Network retry
  - Dates freed (calendar check)
  - Two deniers don't both succeed
  - Deny after other denies shows "Schon erledigt"

### Definition of Done

- [ ] All test cases pass (37-42 tests)
- [ ] All BRs enforced and tested
- [ ] German copy exact from specifications
- [ ] Type safety (TypeScript strict mode)
- [ ] No N+1 queries
- [ ] Mobile tested (375px minimum)
- [ ] Concurrency tests pass
- [ ] Idempotency verified (BR-010)
- [ ] Code coverage ≥80%
- [ ] Self-review completed

---

## Summary Table: BR Coverage by Story

| BR | US-7.1 | US-7.2 | US-7.3 | Critical | Impact |
|----|--------|--------|--------|----------|--------|
| BR-003 | ✓ Access | ✓ Access | ✓ Access | YES | Must validate approver identity |
| BR-004 | ✓ Denied in History | ✓ Cannot approve | ✓ Denial state | YES | State machine core |
| BR-010 | ✓ Token access | ✓ Idempotent | ✓ Idempotent | YES | UX critical, retry safety |
| BR-014 | ✓ Disabled buttons | ✓ Cannot approve | ✓ Cannot deny | YES | Past read-only enforcement |
| BR-015 | ✓ Visible | ✓ Visible | - | NO | Edge case |
| BR-020 | - | - | ✓ Link blocking | YES | Security, spam prevention |
| BR-023 | ✓ Filtering/Sorting | ✓ List updates | ✓ List updates | YES | Query correctness critical |
| BR-024 | - | ✓ Race handling | ✓ Race handling | YES | Concurrency core |

**Most Critical BRs for Phase 7:**
1. **BR-023** - Approver list queries (Outstanding vs History, sorting, filtering)
2. **BR-024** - First-action-wins concurrency (SELECT FOR UPDATE)
3. **BR-010** - Idempotency (same result on retry/refresh)
4. **BR-004** - Denial state machine (non-blocking, hidden)
5. **BR-014** - Past items read-only (no approval/denial)

---

## Testing Strategy

### Unit Tests (Backend)

- Query tests for Outstanding (NoResponse + Pending filter, ordering)
- Query tests for History (all statuses, ordering)
- Approval state machine tests (can approve? can deny? based on status)
- Concurrency simulation tests (SELECT FOR UPDATE behavior)
- Idempotency tests (repeated actions return same result)

### E2E Tests (Playwright)

- **Account:** Token-based access (no login)
- **Browsers:** Chrome, Firefox (Safari if possible)
- **Devices:** Desktop 1024px, Tablet 768px, Mobile 375px
- **Networks:** Normal, Slow 3G (concurrent operations)

### Accessibility

- WCAG AA compliance
- Focus indicators visible
- Touch targets 44×44pt
- Color contrast adequate
- Screen reader compatibility

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| BR-024 race condition (first-action-wins) | Medium | High | Use SELECT FOR UPDATE; concurrent test suite |
| BR-023 query incorrectness | High | High | Granular unit tests; multiple edge cases |
| Token validation bypass | Low | Critical | Input validation tests; security review |
| Idempotency broken | Medium | High | Network failure simulation; retry testing |
| German copy mismatch | Medium | Medium | Programmatic string comparison tests |
| Mobile layout issues | Medium | Medium | 375px device testing; touch target verification |

---

## Estimated Timeline

**Phase 7 Total:** 2-3 days

- **Day 1:** Frontend setup, US-7.1 (Outstanding/History tabs)
- **Day 2:** US-7.2 (Approve), US-7.3 (Deny)
- **Day 3:** Testing, concurrency scenarios, mobile verification

**Test Implementation:** ~3-4 hours (37-42 Playwright tests)

---

## References

**Business Rules:** `/home/user/btznstn/docs/foundation/business-rules.md`
**UI Screens:** `/home/user/btznstn/docs/specification/ui-screens.md` (lines 253-292)
**Error Messages:** `/home/user/btznstn/docs/specification/error-handling.md`
**Phase Definition:** `/home/user/btznstn/docs/implementation/phase-7-approver-interface.md`
