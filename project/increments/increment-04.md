# Increment 4: Frontend Approver

**Status:** 🚫 **Blocked** (Depends on Increments 2 and 3)
**Phases:** 7
**Dependencies:** Increment 2 (approval backend) + Increment 3 (frontend core) complete
**Target Start:** After Phases 3-6 complete
**Estimated Effort:** 2-3 days

---

## 📋 Overview

**Goal:** Build approver-facing interface for reviewing and acting on booking requests.

**Deliverables:**
- Approver overview (Outstanding + History tabs)
- Approve action (one-click from email or overview)
- Deny action with comment (comment validation)
- BR-024 first-action-wins concurrency handling
- BR-023 query correctness (Outstanding vs History filtering)
- All German UI copy from specifications
- Mobile-responsive (iPhone 8 class, 375px width)

**Success Criteria:**
- All Playwright E2E tests passing (~40 total)
- Outstanding/History tabs filter correctly (BR-023)
- Approve/Deny actions handle concurrency (BR-024)
- Comment validation working (BR-020 link blocking)
- Mobile tested (375px viewport)
- German copy matches spec exactly

---

## 📊 Progress Summary

| Phase | User Stories | Draft | Specified | Implemented | Status |
|-------|--------------|-------|-----------|-------------|--------|
| **7** | 3 | 0 | 3 | 0 | 🚫 Blocked |
| **Total** | **3** | **0** | **3** | **0** | **🚫 0%** |

---

## 🎯 Phase 7: Approver Interface

**Status:** 🚫 **Blocked**
**Dependencies:** Increment 2 (approval backend) + Increment 3 (frontend core)

### User Stories (Dependency-Based Order)

#### US-7.1: Approver Overview (Outstanding + History Tabs)
**Status:** ✅ **Specified**
**Estimated Tests:** 15
**Priority:** P0 (Foundation)

**Description:** Two-tab interface showing outstanding approvals and historical approvals.

**Key Business Rules:**
- BR-003: Token must validate to one of 3 approvers
- BR-023: **CRITICAL** - Outstanding = NoResponse + Pending (sorted LastActivityAt DESC); History = All statuses (sorted LastActivityAt DESC)
- BR-004: Denied bookings visible in History (read-only), not in Outstanding
- BR-014: Past bookings disable approve/deny buttons
- BR-015: Self-approved bookings visible

**Acceptance Criteria:**
- [ ] Access via /approver?token={approver_token}
- [ ] Token validation (only Ingeborg, Cornelia, Angelika)
- [ ] Two tabs: "Ausstehend" (Outstanding) and "Verlauf" (History)
- [ ] **Outstanding tab:**
  - [ ] Shows only Pending bookings where approver response = NoResponse
  - [ ] Sorted by LastActivityAt DESC (most recent first)
  - [ ] Each item shows: Requester first name, dates, party size, approve/deny buttons
  - [ ] Empty state: "Keine ausstehenden Anfragen."
- [ ] **History tab:**
  - [ ] Shows all bookings (Pending, Confirmed, Denied - not Canceled)
  - [ ] Sorted by LastActivityAt DESC
  - [ ] Each item shows: Requester first name, dates, status, approver's decision
  - [ ] Read-only (no action buttons)
  - [ ] Empty state: "Noch keine Aktivität."
- [ ] Denied bookings appear in History, not Outstanding (BR-004)
- [ ] Past bookings have disabled action buttons (BR-014)
- [ ] Mobile-responsive (375px, tabs stack)
- [ ] 15 E2E tests passing

**German Copy:**
- Tabs: "Ausstehend", "Verlauf"
- Empty Outstanding: "Keine ausstehenden Anfragen."
- Empty History: "Noch keine Aktivität."
- Button labels: "Zustimmen", "Ablehnen"

**Files:**
- Component: `/web/app/approver/page.tsx` (to create)
- Components: `/web/app/components/Approver/OutstandingTab.tsx`, `HistoryTab.tsx` (to create)
- Tests: `/web/tests/e2e/approver-overview.spec.ts` (to create)
- Spec: `/docs/implementation/phase-7-approver-interface.md`

---

#### US-7.2: One-Click Approve
**Status:** ✅ **Specified**
**Estimated Tests:** 15
**Priority:** P0 (Core functionality)

**Description:** Approver approves booking with one click (from email link or overview).

**Key Business Rules:**
- BR-003: Token validation
- BR-010: **CRITICAL** - Idempotent (same result on retry)
- BR-015: Self-approval allowed (idempotent)
- BR-024: **CRITICAL** - First-action-wins (if two approvers click simultaneously)

**Acceptance Criteria:**
- [ ] Approve button in Outstanding list
- [ ] Approve link in email works (redirects to result page)
- [ ] POST /api/v1/bookings/{id}/approve called
- [ ] Idempotent: Click twice = success both times
- [ ] Result page: "Danke – du hast zugestimmt"
- [ ] If 3rd approval → Booking moves to Confirmed, disappears from Outstanding
- [ ] If race condition (two simultaneous approvals) → First wins, second sees "Schon erledigt – bereits bestätigt"
- [ ] Self-approver can approve again (idempotent, BR-015)
- [ ] Cannot approve Denied booking (error: "Schon erledigt – abgelehnt")
- [ ] Cannot approve past booking (error: "Diese Anfrage ist bereits abgelaufen.")
- [ ] Mobile-responsive result page
- [ ] 15 E2E tests passing

**German Copy:**
- Button: "Zustimmen"
- Result page: "Danke – du hast zugestimmt"
- Already confirmed: "Schon erledigt. Die Buchung ist bereits bestätigt."
- Already denied: "Schon erledigt. {{Partei}} hat bereits abgelehnt – die Anfrage ist jetzt abgelehnt (nicht öffentlich)."
- Past booking: "Diese Anfrage ist bereits abgelaufen."

**Files:**
- Action: Update `/web/app/approver/page.tsx` (approve handler)
- API call: `/web/app/lib/api.ts` (approve function)
- Result page: `/web/app/approver/result/page.tsx` (to create)
- Tests: `/web/tests/e2e/approve-action.spec.ts` (to create)

---

#### US-7.3: Deny with Comment
**Status:** ✅ **Specified**
**Estimated Tests:** 18
**Priority:** P0 (Core functionality)

**Description:** Approver denies booking with required comment (validates for links).

**Key Business Rules:**
- BR-004: Denial requires comment, frees dates immediately, hidden from public
- BR-010: Idempotent
- BR-020: **CRITICAL** - Block links in comment (http://, https://, www, mailto:)
- BR-024: First-action-wins

**Acceptance Criteria:**
- [ ] Deny button in Outstanding list
- [ ] Click "Ablehnen" → Opens comment dialog
- [ ] Dialog shows booking context (requester name, dates)
- [ ] Comment textarea (required, max 500 chars)
- [ ] Comment validation (client-side + server-side):
  - [ ] Empty comment rejected: "Bitte gib einen kurzen Grund an."
  - [ ] Links rejected (BR-020): "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden."
  - [ ] Umlaut/emoji/newline allowed
  - [ ] 501+ chars rejected: "Text ist zu lang (max. 500 Zeichen)."
- [ ] Submit button: "Ja, ablehnen"
- [ ] Cancel button closes dialog without action
- [ ] POST /api/v1/bookings/{id}/deny called
- [ ] Result page: "Danke – du hast abgelehnt"
- [ ] Booking disappears from Outstanding, appears in History as Denied
- [ ] Dates freed immediately (calendar shows as available)
- [ ] If Confirmed booking → Show warning dialog before deny
- [ ] Idempotent: Deny twice = success both times
- [ ] Mobile-responsive dialog (full-screen on 375px)
- [ ] 18 E2E tests passing

**German Copy:**
- Button: "Ablehnen"
- Dialog title: "Grund für Ablehnung"
- Confirmed warning: "Buchung ist bereits bestätigt. Du möchtest eine bereits bestätigte Buchung ablehnen. Bist du sicher? Bitte gib einen kurzen Grund an."
- Submit button: "Ja, ablehnen"
- Cancel button: "Abbrechen"
- Result: "Danke – du hast abgelehnt"
- Comment required: "Bitte gib einen kurzen Grund an."
- Link blocked: "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden."

**Files:**
- Dialog component: `/web/app/components/Approver/DenyDialog.tsx` (to create)
- Action: Update `/web/app/approver/page.tsx` (deny handler)
- API call: `/web/app/lib/api.ts` (deny function)
- Tests: `/web/tests/e2e/deny-action.spec.ts` (to create)

---

### Phase 7: Definition of Done

- [ ] All 3 user stories implemented
- [ ] Outstanding/History tabs filter correctly (BR-023)
- [ ] Approve/Deny actions work with concurrency safety (BR-024)
- [ ] Comment validation working (BR-020)
- [ ] All E2E tests passing (~48 total)
- [ ] Mobile tested (375px viewport)
- [ ] German copy matches spec exactly
- [ ] Type checking passes (tsc)
- [ ] Linting passes (eslint)
- [ ] Accessibility basics (ARIA labels, keyboard nav)

---

## 📚 Specification References

**Business Rules:**
- `/docs/foundation/business-rules.md` - BR-003, 004, 010, 014, 015, 020, 023, 024

**Phase Specification:**
- `/docs/implementation/phase-7-approver-interface.md`

**German Copy:**
- `/docs/specification/ui-screens.md` - All UI labels and button text (lines 253-292)
- `/docs/specification/error-handling.md` - All error messages

---

## 🎓 Known Gotchas

### BR-023: Query Correctness is CRITICAL
**Why:** Wrong filtering = approvers see wrong data or miss approvals.
**Outstanding query:** `response = NoResponse AND status = Pending AND sorted LastActivityAt DESC`
**History query:** `All statuses (Pending, Confirmed, Denied) AND sorted LastActivityAt DESC`
**Common mistake:** Forgetting to filter by approver (each approver sees only their own items).

### BR-024: Concurrency Tests Are Mandatory
**Why:** Two approvers clicking at the same time WILL happen in production.
**Solution:** Write Playwright tests that simulate concurrent clicks with `Promise.all()`.

### BR-020: Link Detection Must Be Case-Insensitive
**Why:** Users can type "HTTP://", "Www", "MAILTO:", etc.
**Solution:** Use regex with `i` flag: `/http[s]?:\/\//i`, `/www\./i`, `/mailto:/i`

### Idempotency Edge Case (BR-010)
**Why:** User clicks approve, network timeout, clicks again.
**Solution:** Backend must return success on second click, not error.

---

## 🔄 Next Steps

**To start Increment 4:**

1. Verify Increments 2 and 3 complete (approval backend + frontend core exist)
2. Start with US-7.1 (Approver Overview)
   - Read phase-7-approver-interface.md
   - Write Playwright tests for Outstanding/History tabs (BR-023 filtering)
   - Implement tabs
   - Verify tests pass

3. Continue with US-7.2 (Approve)
   - Write concurrency tests (BR-024)
   - Implement approve action
   - Verify idempotency (BR-010)

4. Finish with US-7.3 (Deny)
   - Write comment validation tests (BR-020)
   - Implement deny dialog
   - Verify link blocking works

**When starting, always read `/project/BACKLOG.md` first to confirm priority.**
