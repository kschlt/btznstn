# Phase 7: Approver Interface - Complete Test Matrix

**Generated:** 2025-11-17
**Target:** 37-42 Playwright tests across 3 user stories

---

## US-7.1: Approver Overview - Test Matrix

### Outstanding Tab Tests

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.1.1 | Load Outstanding Tab | Approver loads /approver?token=valid, clicks "Outstanding" | Shows list of Pending bookings where approver=NoResponse | BR-003, BR-023 | P0 | TODO |
| 7.1.2 | Outstanding Filter Accuracy | System has 5 Pending (3 where approver=NoResponse, 2 where approver=Approved) | Shows exactly 3 items, not 2 or 5 | BR-023 | P0 | TODO |
| 7.1.3 | Outstanding Sorting by LastActivityAt | Multiple Pending items with different LastActivityAt timestamps | Sorted DESC (most recent first), not ASC or random | BR-023 | P0 | TODO |
| 7.1.4 | Outstanding Sorting Tiebreaker | Two items with same LastActivityAt | Consistent ordering (e.g., by ID or submission order) | BR-023 | P1 | TODO |
| 7.1.5 | Exclude Denied from Outstanding | Approver has Pending and Denied bookings | Denied bookings absent from Outstanding tab | BR-004 | P0 | TODO |
| 7.1.6 | Exclude Confirmed from Outstanding | Approver has Pending and 2/3 Approved (still Pending), and Confirmed | Confirmed absent; Pending visible | BR-004 | P0 | TODO |
| 7.1.7 | Empty Outstanding Message | Approver with zero NoResponse Pending items | Shows "Keine ausstehenden Anfragen." (exact copy) | BR-004 | P1 | TODO |
| 7.1.8 | Past Booking in Outstanding | Somehow past booking appears in Outstanding (shouldn't happen normally) | Action buttons disabled, visual "read-only" indicator | BR-014 | P1 | TODO |
| 7.1.9 | Infinite Scroll - Initial Load | Page loads Outstanding | Shows first 20 items, scroll indicator visible | BR-023 | P1 | TODO |
| 7.1.10 | Infinite Scroll - Load More | Scroll to bottom of 20-item list | Loads next batch (21-40), smooth loading indicator | BR-023 | P2 | TODO |

### History Tab Tests

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.1.11 | Load History Tab | Click "History" tab | Shows all bookings this approver involved with | BR-023 | P0 | TODO |
| 7.1.12 | History Includes Pending | Approver has Pending booking | Appears in History | BR-023 | P0 | TODO |
| 7.1.13 | History Includes Confirmed | Approver has Confirmed booking | Appears in History | BR-023 | P0 | TODO |
| 7.1.14 | History Includes Denied | Approver has Denied booking | Appears in History (read-only) | BR-004 | P0 | TODO |
| 7.1.15 | History Excludes Canceled | Approver approved booking, requester canceled | Booking appears as Canceled? OR excluded? (check spec) | BR-004 | P1 | TODO |
| 7.1.16 | History Sorting by LastActivityAt | Multiple bookings with different LastActivityAt | Sorted DESC (most recent first) | BR-023 | P0 | TODO |
| 7.1.17 | History Read-Only | Click on History booking | Opens details but no action buttons (read-only) | BR-023 | P0 | TODO |
| 7.1.18 | Empty History Message | Approver with zero bookings involved | Shows "Noch keine Aktivität." (exact copy) | BR-004 | P1 | TODO |
| 7.1.19 | History includes Self-Approved | Approver is requester, created booking (auto-approved) | Booking visible in History with approval already counted | BR-015 | P1 | TODO |
| 7.1.20 | History Infinite Scroll | Same as Outstanding | Scrolling loads more items | BR-023 | P1 | TODO |

### Access Control Tests

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.1.21 | Valid Token | Approver has valid token to /approver?token=valid_token | Interface loads, tabs visible | BR-003, BR-010 | P0 | TODO |
| 7.1.22 | Invalid Token | Visit /approver?token=invalid_token | 404 or redirect to recovery page | BR-003 | P0 | TODO |
| 7.1.23 | Wrong Approver Token | Ingeborg's token in Cornelia's browser (if simulated) | Access denied or wrong data shown | BR-003 | P1 | TODO |
| 7.1.24 | Token with Special Chars | Token contains URL-encoded chars (%20, %2B, etc) | Decoded correctly, interface loads | BR-010 | P1 | TODO |
| 7.1.25 | Approver Can't See Other Approvers' Items | Cornelia loads her interface | Sees only bookings where Cornelia's response=NoResponse (not Ingeborg's) | BR-003 | P0 | TODO |

### Mobile & Responsive Tests

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.1.26 | Outstanding on 375px Mobile | Load approver interface on iPhone 8 (375×667) | Both tabs readable, no horizontal scroll, touch targets 44×44pt | BR-023 | P0 | TODO |
| 7.1.27 | History on 375px Mobile | Switch to History tab on mobile | Smooth transition, list items readable | BR-023 | P0 | TODO |
| 7.1.28 | Tab Navigation Mobile | Tap Outstanding/History tabs on mobile | Tab switches without lag, active indicator visible | BR-023 | P1 | TODO |
| 7.1.29 | Affiliation Colors on Mobile | Affiliation color indicator visible on list items | Colors distinguishable (Ingeborg=blue, Cornelia=green, Angelika=pink) | BR-023 | P1 | TODO |
| 7.1.30 | Status Badge on Mobile | Status badge (Pending, Confirmed, Denied) on list item | Readable contrast, not clipped | BR-023 | P1 | TODO |

---

## US-7.2: One-Click Approve - Test Matrix

### Happy Path Tests

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.2.1 | Approve from Email Link | Click "Zustimmen" link in email (has token + booking_id) | Redirects to result page: "Danke – du hast zugestimmt" (exact copy) | BR-003, BR-010 | P0 | TODO |
| 7.2.2 | Approve from Outstanding List | Click "Zustimmen" button on booking row | Booking approves, disappears from Outstanding | BR-023 | P0 | TODO |
| 7.2.3 | Final Approval → Confirmed | Booking has 2/3 approvals, 3rd approver clicks "Zustimmen" | Status transitions to Confirmed, booking moves to History | BR-003, BR-023 | P0 | TODO |
| 7.2.4 | Approve Shows Requester | Approver bookings list shows requester first name | Requester name matches submitted value | BR-003 | P0 | TODO |

### Idempotency Tests (BR-010)

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.2.5 | Approve Twice from Email | Click "Zustimmen" link twice in short succession | Both times show result page: "Danke – du hast zugestimmt" | BR-010 | P0 | TODO |
| 7.2.6 | Approve Twice from List | Click "Zustimmen" button, approve, then navigate back and click again | Second click shows success (or no-op, or shows booking in History) | BR-010 | P0 | TODO |
| 7.2.7 | Network Timeout then Retry | Click approve, network timeout, user clicks again | Second attempt succeeds, no double-submission | BR-010 | P0 | TODO |
| 7.2.8 | Refresh After Approval | Approve, page refreshes, approver clicks approve again | Idempotent - shows already-approved state (e.g., booking in History) | BR-010 | P0 | TODO |
| 7.2.9 | Already-Approved Result Page | Approver already approved; clicks "Zustimmen" link or button again | Shows "Schon erledigt. Die Buchung ist bereits bestätigt." (exact copy) | BR-010 | P0 | TODO |

### First-Action-Wins Tests (BR-024)

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.2.10 | Two Approves Simultaneously | Cornelia and Angelika click "Zustimmen" at exact same time | First to persist wins; second sees "Schon erledigt – bereits bestätigt" | BR-024 | P0 | TODO |
| 7.2.11 | Approve vs Deny Simultaneously | One approver approves, another denies at same time | First action persists; second sees appropriate error message | BR-024 | P0 | TODO |
| 7.2.12 | Approve After Another Denies | Approver clicks approve, but before action persists, another denies | Second action (approve) sees error "Schon erledigt – {{Partei}} hat bereits abgelehnt" | BR-024, BR-004 | P0 | TODO |

### State Validation Tests (BR-004)

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.2.13 | Cannot Approve Denied Booking | Approver tries to approve already-Denied booking | Error: "Schon erledigt. {{Partei}} hat bereits abgelehnt – die Anfrage ist jetzt abgelehnt (nicht öffentlich)." (exact copy) | BR-004 | P0 | TODO |
| 7.2.14 | Cannot Approve Canceled Booking | Approver tries to approve Canceled booking | Error or no-op (booking not shown in Outstanding) | BR-004 | P1 | TODO |

### Past Booking Tests (BR-014)

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.2.15 | Cannot Approve Past Booking | EndDate < today, approver clicks "Zustimmen" | Error: "Diese Anfrage ist bereits abgelaufen." | BR-014 | P0 | TODO |
| 7.2.16 | Approve Boundary (EndDate = today) | EndDate = today, approver approves | Allowed (becomes past tomorrow at 00:00 Berlin time) | BR-014 | P1 | TODO |
| 7.2.17 | Past Booking Approve Button Disabled | Past booking in Outstanding (shouldn't happen) | Button disabled or no-op | BR-014 | P1 | TODO |

### Self-Approval Tests (BR-015)

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.2.18 | Self-Approver Sees Auto-Approval | Ingeborg creates booking; sees it in Outstanding; sees 1/3 already approved (self) | Correct approval count shown (1/3, not 0/3) | BR-015 | P0 | TODO |
| 7.2.19 | Self-Approver Can Approve Again | Self-approver clicks "Zustimmen" on own booking | Idempotent success (BR-010); shows already-approved state | BR-015, BR-010 | P0 | TODO |

### Result Page Tests

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.2.20 | Result Page Title | After approval, result page displays | Title: "Danke – du hast zugestimmt" (exact copy) | BR-010 | P0 | TODO |
| 7.2.21 | Result Page Back Link | Result page shows way to continue | "Zurück zu den ausstehenden Anfragen" or similar link | BR-010 | P0 | TODO |
| 7.2.22 | Result Page Mobile | Result page on 375px mobile | Full width, readable, button accessible | BR-010 | P0 | TODO |

### Error Handling Tests

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.2.23 | Invalid Token | Approve with invalid token | 404 or redirect to recovery | BR-003 | P0 | TODO |
| 7.2.24 | Booking Not Found | Approve non-existent booking | 404 | BR-003 | P1 | TODO |
| 7.2.25 | Token Wrong Approver | Use Cornelia's token with Ingeborg's booking | 403 or permission denied | BR-003 | P1 | TODO |

---

## US-7.3: Deny with Comment - Test Matrix

### Happy Path Tests

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.3.1 | Deny with Comment | Click "Ablehnen", dialog opens, enter comment, submit | Booking status → Denied, shows result page: "Danke – du hast abgelehnt" | BR-004, BR-010 | P0 | TODO |
| 7.3.2 | Deny from Outstanding List | Click "Ablehnen" button on booking row | Comment dialog opens with context of which booking | BR-004 | P0 | TODO |

### Comment Validation Tests (BR-004, BR-020)

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.3.3 | Comment Required | Click "Ablehnen", dialog opens, submit without text | Error: "Bitte gib einen kurzen Grund an." (exact copy) | BR-004 | P0 | TODO |
| 7.3.4 | Whitespace-Only Comment | Submit comment with only spaces | Treated as empty, error shown | BR-004 | P0 | TODO |
| 7.3.5 | Block http:// in Comment | Submit comment containing "http://example.com" | Error: "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden." | BR-020 | P0 | TODO |
| 7.3.6 | Block https:// in Comment | Submit comment containing "https://example.com" | Error (BR-020) | BR-020 | P0 | TODO |
| 7.3.7 | Block www in Comment | Submit comment containing "www.example.com" | Error (BR-020) | BR-020 | P0 | TODO |
| 7.3.8 | Block mailto: in Comment | Submit comment containing "mailto:user@example.com" | Error (BR-020) | BR-020 | P0 | TODO |
| 7.3.9 | Allow Umlaut in Comment | Submit comment "Das ist nicht okay – Äußerungen weg." | Accepted, no error | BR-020 | P1 | TODO |
| 7.3.10 | Allow Emoji in Comment | Submit comment "Das ist nicht okay 😞" | Accepted, no error (not blocked by BR-020) | BR-020 | P1 | TODO |
| 7.3.11 | Allow Newline in Comment | Submit comment "Grund 1:\nGrund 2:" | Accepted (newlines allowed unlike Description field) | BR-020 | P1 | TODO |
| 7.3.12 | Comment Exactly 500 Chars | Submit comment of exactly 500 characters | Accepted | BR-004 | P1 | TODO |
| 7.3.13 | Comment 501+ Chars | Submit comment longer than 500 characters | Error: "Text ist zu lang (max. 500 Zeichen)." | BR-004 | P0 | TODO |

### Idempotency Tests (BR-010)

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.3.14 | Deny Twice | Deny with comment, then click "Ablehnen" and deny again with same/different comment | Both times succeed; second shows "Schon erledigt – bereits abgelehnt" | BR-010 | P0 | TODO |
| 7.3.15 | Network Timeout then Retry | Deny, network timeout, retry with same comment | Second attempt succeeds, no double-denial | BR-010 | P0 | TODO |

### Confirmed Booking Tests (BR-004 post-confirm)

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.3.16 | Deny Confirmed Shows Warning Dialog | Click "Ablehnen" on Confirmed booking | Dialog opens: Title "Buchung ist bereits bestätigt", Body "Du möchtest eine bereits bestätigte Buchung ablehnen. Bist du sicher? Bitte gib einen kurzen Grund an." (exact copy) | BR-004 | P0 | TODO |
| 7.3.17 | Deny Confirmed Requires Comment | Confirmed booking, dialog opens, submit without comment | Error: "Bitte gib einen kurzen Grund an." | BR-004 | P0 | TODO |
| 7.3.18 | Cancel Deny Confirmed Dialog | Dialog opens, click "Abbrechen" | Dialog closes, booking still Confirmed | BR-004 | P0 | TODO |

### First-Action-Wins Tests (BR-024)

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.3.19 | Two Denies Simultaneously | Cornelia and Angelika both submit deny (with comments) at same time | First to persist wins; second sees "Schon erledigt – bereits abgelehnt" | BR-024 | P0 | TODO |
| 7.3.20 | Deny vs Approve Simultaneously | One denies, another approves at same time | First action persists; second sees appropriate error | BR-024 | P0 | TODO |
| 7.3.21 | Deny After Another Denies | First approver denies, second approver submits denial immediately after | Second sees "Schon erledigt – bereits abgelehnt – die Anfrage ist jetzt abgelehnt" | BR-024 | P0 | TODO |

### State & Effects Tests (BR-004)

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.3.22 | Denied Booking Not Public | Approver denies booking | Booking no longer appears on public calendar | BR-004 | P0 | TODO |
| 7.3.23 | Dates Freed After Denial | Booking denies, dates are no longer blocked | Another requester can book same dates immediately | BR-004 | P0 | TODO |
| 7.3.24 | Requester Sees Denial Comment | Requester views booking, sees "Abgelehnt" status and denial comment | Comment displayed to requester only | BR-004 | P0 | TODO |

### List Updates Tests (BR-023)

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.3.25 | After Denial, Outstanding Removed | Approver in Outstanding view, denies booking | Booking immediately removed from Outstanding (status no longer Pending) | BR-023 | P0 | TODO |
| 7.3.26 | After Denial, History Updated | After denial, open History tab | Denied booking now appears in History with denial comment | BR-023 | P0 | TODO |
| 7.3.27 | Denial Affects Other Approvers | Approver A denies, Approver B still sees booking in their Outstanding | Status is now Denied, but if Approver B hasn't acted yet, they see it's already handled | BR-023 | P0 | TODO |

### Past Booking Tests (BR-014)

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.3.28 | Cannot Deny Past Booking | EndDate < today, approver clicks "Ablehnen" | Error: "Diese Anfrage ist bereits abgelaufen." | BR-014 | P0 | TODO |
| 7.3.29 | Deny Button Disabled for Past | Past booking in Outstanding (shouldn't happen) | "Ablehnen" button disabled or hidden | BR-014 | P1 | TODO |

### Dialog & UX Tests

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.3.30 | Comment Dialog Context | Click "Ablehnen", dialog shows which booking | Dialog title/context shows requester name and dates | BR-004 | P0 | TODO |
| 7.3.31 | Comment Input Focused | Dialog opens | Comment textarea has focus (mobile keyboard opens) | BR-004 | P1 | TODO |
| 7.3.32 | Submit Button in Dialog | Dialog open | Submit button labeled "Ja, ablehnen" or similar (exact copy) | BR-004 | P0 | TODO |

### Result Page Tests

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.3.33 | Denial Result Page | After successful denial | Shows "Danke – du hast abgelehnt" (exact copy) | BR-010 | P0 | TODO |
| 7.3.34 | Result Page Back Link | Result page visible | Link to continue: "Zurück zu den ausstehenden Anfragen" | BR-010 | P0 | TODO |

### Mobile Tests

| Test ID | Test Name | Scenario | Expected Result | BR Coverage | Priority | Status |
|---------|-----------|----------|-----------------|-------------|----------|--------|
| 7.3.35 | Deny Button on Mobile | Booking list on 375px | "Ablehnen" button tappable (44×44pt) | BR-004 | P0 | TODO |
| 7.3.36 | Comment Dialog on Mobile | Comment dialog on 375px iPhone 8 | Full height, textarea visible, keyboard accessible | BR-004 | P0 | TODO |
| 7.3.37 | Comment Input Mobile Keyboard | Tap comment textarea on iOS/Android | Mobile keyboard opens correctly for text input | BR-004 | P1 | TODO |
| 7.3.38 | Result Page Mobile | Result page on 375px | Full width, readable, back link accessible | BR-010 | P0 | TODO |

---

## Cross-Story Test Summary

### Test Count by Priority

| Priority | US-7.1 | US-7.2 | US-7.3 | Total |
|----------|--------|--------|--------|-------|
| **P0 (Critical)** | 15 | 13 | 18 | **46** |
| **P1 (Important)** | 15 | 3 | 5 | **23** |
| **P2 (Nice-to-have)** | 1 | 0 | 0 | **1** |
| **Total** | **30** | **16** | **23** | **69** |

**Recommendation:** Implement all P0 tests (46) for Phase 7. P1 tests (23) for enhanced coverage. P2 tests (1) optional.

### Test Count by Business Rule

| BR | Tests | User Stories |
|----|-------|--------------|
| BR-003 (Access) | 6 | 7.1, 7.2, 7.3 |
| BR-004 (Denial) | 11 | 7.1, 7.2, 7.3 |
| BR-010 (Idempotency) | 10 | 7.2, 7.3 |
| BR-014 (Past) | 6 | 7.1, 7.2, 7.3 |
| BR-015 (Self-Approval) | 3 | 7.1, 7.2 |
| BR-020 (Link Blocking) | 5 | 7.3 |
| BR-023 (Approver Lists) | 15 | 7.1, 7.2, 7.3 |
| BR-024 (First-Action-Wins) | 7 | 7.2, 7.3 |
| **Other (Mobile, UX)** | 6 | All |

### Concurrency Test Scenarios (BR-024)

All first-action-wins tests use the same pattern:

```javascript
// Simulate two concurrent actions
const [result1, result2] = await Promise.all([
  approveBooking(bookingId, approverA),
  approveBooking(bookingId, approverB),
]);

// First should succeed
expect(result1.status).toBe('approved');

// Second should show "Schon erledigt" error
expect(result2.error).toContain('Schon erledigt');
```

---

## Test Implementation Checklist

### Setup (Before Writing Tests)

- [ ] Test fixtures created (sample bookings, approvers, tokens)
- [ ] Database seeded with 3 approver parties (Ingeborg, Cornelia, Angelika)
- [ ] Token generation logic available for test tokens
- [ ] Error message constants imported from spec files
- [ ] German copy constants centralized (exact match to spec)
- [ ] Timezone set to Europe/Berlin for date calculations
- [ ] Mock email/notification system (or disable for tests)

### US-7.1 Outstanding/History (30 tests)

**Backend Setup:**
- [ ] Query: `list_outstanding(approver_id)` → Pending + NoResponse, sorted LastActivityAt DESC
- [ ] Query: `list_history(approver_id)` → All statuses, sorted LastActivityAt DESC
- [ ] Both queries eager-load relationships (prevent N+1)

**Frontend Setup:**
- [ ] Tabs component with active state
- [ ] List item component (booking name, dates, status badge, affiliation color)
- [ ] Infinite scroll integration
- [ ] Loading skeletons

**Tests:**
- [ ] 20 core Outstanding/History tests
- [ ] 5 access control tests (token validation)
- [ ] 5 mobile responsive tests

### US-7.2 Approve (16 tests)

**Backend Setup:**
- [ ] Endpoint: `POST /booking/{id}/approve` with token
- [ ] Action is idempotent (same result on retry)
- [ ] Uses SELECT FOR UPDATE to handle BR-024 race
- [ ] Returns Booking in Confirmed state if final approval
- [ ] Sends email to requester if Confirmed

**Frontend Setup:**
- [ ] Approve button on list item and booking details
- [ ] Result page component with success message
- [ ] Idempotency handling (don't double-submit)
- [ ] Error message display for "Schon erledigt"

**Tests:**
- [ ] 4 happy path tests
- [ ] 5 idempotency tests (BR-010)
- [ ] 3 concurrency tests (BR-024)
- [ ] 2 state validation tests (BR-004)
- [ ] 2 mobile tests

### US-7.3 Deny (23 tests)

**Backend Setup:**
- [ ] Endpoint: `POST /booking/{id}/deny` with token + comment
- [ ] Comment validation (required, no links, max 500 chars)
- [ ] Action is idempotent
- [ ] Uses SELECT FOR UPDATE (BR-024)
- [ ] Returns Booking in Denied state
- [ ] Frees dates immediately (calendar conflict check removed)
- [ ] Sends email to requester + other approvers

**Frontend Setup:**
- [ ] Deny button on list item and booking details
- [ ] Comment dialog component
- [ ] Comment validation display (inline errors)
- [ ] Warning dialog for Confirmed bookings
- [ ] Result page component

**Tests:**
- [ ] 2 happy path tests
- [ ] 13 comment validation tests (BR-020 link blocking)
- [ ] 2 idempotency tests
- [ ] 3 Confirmed booking tests
- [ ] 3 concurrency tests (BR-024)

---

## Success Criteria

**All tests must pass:**
- [ ] 46 P0 (critical) tests pass
- [ ] 23 P1 (important) tests pass
- [ ] Code coverage ≥80%
- [ ] No flaky tests (retry test 3x, all pass)
- [ ] Mobile tests on actual 375px viewport
- [ ] German copy matches spec exactly (programmatic check)
- [ ] Concurrency tests pass with 100% success rate

**Performance targets:**
- [ ] Page load < 2s (3G)
- [ ] Approve action < 1s
- [ ] Deny action < 1s
- [ ] No N+1 queries
- [ ] No memory leaks

---

## Test Execution Order

**Recommended:**
1. **US-7.1 (Outstanding/History)** - Foundation for viewing data
2. **US-7.2 (Approve)** - Core action flow
3. **US-7.3 (Deny)** - Core action flow + validation
4. **Cross-story concurrency** - After all story tests pass

**Parallel execution:** Tests can run in parallel (different data, no conflicts)

---

## Notes

- **BR-024 tests are timing-sensitive:** Use small delays/thread waits to simulate true concurrency
- **Idempotency tests must retry:** Simulate network timeout with `await new Promise(r => setTimeout(r, 100))` before retry
- **German copy tests:** Use exact string matching, not substring contains
- **Mobile tests:** Use Playwright's device presets (iPhone 12, Pixel 5) plus custom 375px viewport
- **Token tests:** Generate different token formats (valid, expired format, wrong approver, corrupted)

---

**Next Steps:**
1. Read all 46 P0 tests carefully
2. Identify any missing edge cases
3. Write test code (failing tests first)
4. Implement backend/frontend code
5. Verify all tests pass
6. Self-review per Phase 7 implementation guide

