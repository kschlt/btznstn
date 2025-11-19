# Increment 3: Frontend COMPLETE

**Status:** 🚫 **Blocked** (Playwright not configured, Increment 2 pending)
**Phases:** 5, 6, 7
**Dependencies:**
  1. Increment 2 complete (approval backend needed for Phase 7)
  2. Playwright configured (1 hour setup)
**Target Start:** After Increment 2 complete
**Estimated Effort:** 10-11 days

**🎯 Backend-First Strategy:** This increment starts AFTER backend is 100% complete

---

## 📋 Overview

**Goal:** Build ALL frontend functionality in one focused increment.

**Deliverables:**
- Calendar component (month view, year view, booking details)
- Booking forms (create, edit with BR-005 detection)
- Date picker with conflict visualization
- Approver interface (Outstanding + History tabs, approve/deny actions)
- All German UI copy from specifications
- Mobile-responsive (iPhone 8 class, 375px width)

**Success Criteria:**
- Playwright configured (iPhone 8 viewport 375×667px)
- All calendar views implemented
- All forms implemented with validation
- Approver interface complete
- All Playwright tests passing (~131-149 total)
- Mobile tested (375px viewport)
- German copy matches spec exactly
- **Frontend is 100% complete** (all pages done)
- Type checking passes (tsc)
- Linting passes (eslint)

---

## 📊 Progress Summary

| Phase | User Stories | Draft | Specified | Implemented | Status |
|-------|--------------|-------|-----------|-------------|--------|
| **5** | 3 | 0 | 3 | 0 | 🚫 Blocked (Playwright + Increment 2) |
| **6** | 3 | 0 | 3 | 0 | 🚫 Blocked (Phase 5 + Playwright) |
| **7** | 3 | 0 | 3 | 0 | 🚫 Blocked (Phases 5-6 + Increment 2) |
| **Total** | **9** | **0** | **9** | **0** | **🚫 0%** |

---

## 🚧 Critical Blocker

### 1. Increment 2 Must Complete First

**Impact:** Phase 7 (Approver Interface) needs approval backend endpoints

**Blocking user stories:**
- US-7.2: Approve action needs POST /api/v1/bookings/{id}/approve
- US-7.3: Deny action needs POST /api/v1/bookings/{id}/deny

**Resolution:** Wait for Increment 2 completion (Phases 3-4)

---

### 2. Playwright Not Configured

**Impact:** Cannot start ANY frontend E2E testing

**Estimated Time to Fix:** 1 hour

**Steps to Resolve:**
```bash
cd /home/user/btznstn/web
npm install -D @playwright/test
npx playwright install
```

**Create `playwright.config.ts`:**
- Configure iPhone 8 viewport (375×667px)
- Set up test directories (`/tests/e2e/`)
- Configure browsers (Chromium, Firefox, WebKit minimum)
- Screenshots on failure, 2 retries

**Verify:**
```bash
npx playwright test --list  # Should show test files
npx playwright test          # Should run tests
```

**After resolution:** Move increment to Pending status.

---

## 🎯 Phase 5: Web Calendar

**Status:** 🚫 **Blocked** (Playwright + Increment 1)
**Dependencies:** Playwright configured, Phase 2 API (GET /api/v1/bookings/{id} endpoint)
**Estimated Effort:** 3-4 days

### User Stories (Dependency-Based Order)

#### US-5.1: Month View
**Status:** ✅ **Specified**
**Estimated Tests:** 25-28
**Priority:** P0 (Foundation)

**Description:** Implement calendar month view showing all bookings.

**Key Business Rules:**
- BR-002: Show Pending + Confirmed bookings only
- BR-004: Hide Denied + Canceled bookings
- BR-011: German UI (informal "du")
- BR-014: Past bookings visual distinction (is_past field)

**Acceptance Criteria:**
- [ ] Calendar component displays current month
- [ ] Shows all Pending + Confirmed bookings
- [ ] Past bookings visually distinguished (grayed out)
- [ ] Month navigation (arrows: previous/next)
- [ ] "Heute" button jumps to current date
- [ ] Click booking → opens details modal (US-5.3)
- [ ] Mobile-responsive (375px width)
- [ ] German labels ("Januar", "Februar", etc.)
- [ ] 25-28 E2E tests passing

**German Copy:**
- Month names: "Januar", "Februar", "März", etc.
- "Heute" button
- Empty state: "Keine Buchungen in diesem Monat."

**Files:**
- Component: `/web/app/components/Calendar/MonthView.tsx` (to create)
- Tests: `/web/tests/e2e/calendar-month-view.spec.ts` (to create)
- Spec: `/docs/implementation/phase-5-frontend-calendar.md`
- BR Analysis: `/docs/implementation/phase-5-br-analysis.md` (33KB)

---

#### US-5.2: Year View
**Status:** ✅ **Specified**
**Estimated Tests:** 15-18
**Priority:** P1 (Nice-to-have)

**Description:** Implement calendar year view showing all 12 months at a glance.

**Acceptance Criteria:**
- [ ] Year view shows all 12 months (grid layout)
- [ ] Each month shows bookings as colored blocks
- [ ] Click month → switch to month view
- [ ] Year navigation (previous/next year)
- [ ] Mobile-responsive (stacked layout on 375px)
- [ ] German month names
- [ ] 15-18 E2E tests passing

**German Copy:**
- Year navigation: "2025", "2026", etc.

**Files:**
- Component: `/web/app/components/Calendar/YearView.tsx` (to create)
- Tests: `/web/tests/e2e/calendar-year-view.spec.ts` (to create)

---

#### US-5.3: Booking Details Modal
**Status:** ✅ **Specified**
**Estimated Tests:** 12-15
**Priority:** P0 (Core functionality)

**Description:** Modal showing booking details when clicked in calendar.

**Key Business Rules:**
- BR-004: Public view (no token) vs Requester view (with token)
- Privacy: Never show email addresses

**Acceptance Criteria:**
- [ ] Modal opens when booking clicked in calendar
- [ ] Public view: Shows dates, party size, first name, status (no email)
- [ ] Requester view (with token): Shows edit/cancel buttons if applicable
- [ ] Past bookings: No edit/cancel buttons (BR-014)
- [ ] Close modal (X button, ESC key, click outside)
- [ ] Mobile-responsive (full-screen on 375px)
- [ ] German labels
- [ ] 12-15 E2E tests passing

**German Copy:**
- Heading: "Buchungsdetails"
- Labels: "Zeitraum:", "Personen:", "Status:", etc.
- Close button: "Schließen"

**Files:**
- Component: `/web/app/components/BookingDetailsModal.tsx` (to create)
- Tests: `/web/tests/e2e/booking-details.spec.ts` (to create)

---

### Phase 5: Definition of Done

- [ ] All 3 user stories implemented
- [ ] All E2E tests passing (~52-61 tests total)
- [ ] Mobile tested (375px viewport)
- [ ] Calendar works on iPhone 8 class devices
- [ ] German copy matches spec exactly
- [ ] Type checking passes (tsc)
- [ ] Linting passes (eslint)
- [ ] Accessibility basics (keyboard nav, ARIA labels)

---

## 🎯 Phase 6: Web Booking

**Status:** 🚫 **Blocked** (Phase 5 + Playwright)
**Dependencies:** Phase 5 complete (calendar component exists), Playwright configured
**Estimated Effort:** 3-4 days

**📋 Test Matrix:** `/docs/implementation/phase-6-test-matrix.md` - 44 detailed E2E test specifications

### User Stories (Dependency-Based Order)

#### US-6.2: Date Picker Component
**Status:** ✅ **Specified**
**Estimated Tests:** 10 (included in US-6.1, US-6.3)
**Priority:** P0 (Shared dependency)

**Description:** Reusable date picker component with conflict visualization.

**Key Business Rules:**
- BR-001: Inclusive end date (Jan 1-5 = 5 days)
- BR-002: Show conflicting dates as blocked
- BR-014: Past dates disabled
- BR-026: Future horizon ≤18 months

**Acceptance Criteria:**
- [ ] Date picker opens on field click
- [ ] Select start and end dates (inclusive range)
- [ ] Format: DD.MM.YYYY (German format)
- [ ] Same-day booking allowed (start = end)
- [ ] Past dates disabled (visual + functional)
- [ ] Future dates beyond 18 months disabled
- [ ] Conflicting dates shown as blocked (fetched from API)
- [ ] Month navigation arrows
- [ ] "Heute" button jumps to today
- [ ] Mobile-responsive (375px)
- [ ] Keyboard accessible (arrow keys, Enter, Esc)
- [ ] German labels

**German Copy:**
- Month names: "Januar", "Februar", etc.
- "Heute" button
- Disabled tooltip: "Dieser Tag ist bereits belegt."

**Files:**
- Component: `/web/app/components/DatePicker.tsx` (to create)
- Hook: `/web/app/hooks/useDatePicker.ts` (to create)
- Tests: Covered by US-6.1 and US-6.3 tests

---

#### US-6.1: Create Booking Form
**Status:** ✅ **Specified**
**Estimated Tests:** 20-22
**Priority:** P0 (Core functionality)

**Description:** Form for creating new bookings with validation.

**Key Business Rules:**
- BR-001, 002, 011, 014, 016, 017, 019, 020, 026, 027, 029

**Acceptance Criteria:**
- [ ] Form with fields: Start date, End date, First name, Email, Party size, Affiliation, Description
- [ ] Date picker integration (US-6.2)
- [ ] All validation rules enforced (client-side with Zod)
- [ ] Party size: 1-10 (BR-017)
- [ ] First name: Letters, diacritics, space, hyphen, apostrophe; max 40 chars (BR-019)
- [ ] Description: Block URLs (BR-020), max 500 chars
- [ ] Long stay warning (>7 days) with confirmation dialog (BR-027)
- [ ] Conflict detection (API call) before submit
- [ ] Error messages in German (exact copy from spec)
- [ ] Success message + redirect to booking details with token
- [ ] Mobile-responsive (375px)
- [ ] 20-22 E2E tests passing

**German Copy:**
- Field labels: "Vorname", "E-Mail", "Anzahl Personen", etc.
- Submit button: "Anfrage senden"
- Success: "Anfrage gesendet. Du erhältst E-Mails, sobald entschieden wurde."
- Errors: From `/docs/specification/error-handling.md`

**Files:**
- Component: `/web/app/components/CreateBookingForm.tsx` (to create)
- Tests: `/web/tests/e2e/create-booking.spec.ts` (to create)
- Spec: `/docs/implementation/phase-6-frontend-booking.md`

---

#### US-6.3: Edit Booking Form
**Status:** ✅ **Specified**
**Estimated Tests:** 22-24
**Priority:** P1 (Secondary functionality)

**Description:** Form for editing existing bookings with approval reset detection.

**Key Business Rules:**
- BR-005: **CRITICAL** - Date extend resets approvals; shorten keeps
- BR-014: Past bookings cannot be edited
- BR-025: Email is immutable

**Acceptance Criteria:**
- [ ] Form pre-filled with booking data
- [ ] All fields except email are editable
- [ ] Date picker integration (US-6.2)
- [ ] Detect date change type (extend vs shorten):
  - **Extend** (earlier start OR later end) → Show warning: "Termine werden auf 'Ausstehend' zurückgesetzt."
  - **Shorten** (within original range) → No warning
  - **Non-date change** (party size, description only) → No warning
- [ ] Conflict detection on new dates
- [ ] Past bookings: Show read-only banner (BR-014)
- [ ] Success message + updated booking display
- [ ] Mobile-responsive (375px)
- [ ] 22-24 E2E tests passing

**German Copy:**
- Extend warning: "Achtung: Die Termine werden dadurch auf 'Ausstehend' zurückgesetzt."
- Past booking banner: "Diese Buchung ist bereits abgelaufen und kann nicht bearbeitet werden."
- Success: "Buchung aktualisiert."

**Files:**
- Component: `/web/app/components/EditBookingForm.tsx` (to create)
- Tests: `/web/tests/e2e/edit-booking.spec.ts` (to create)

---

### Phase 6: Definition of Done

- [ ] All 3 user stories implemented
- [ ] All E2E tests passing (~42-46 tests total)
- [ ] Date picker reused in both forms
- [ ] BR-005 approval reset logic working (extend vs shorten detection)
- [ ] Mobile tested (375px viewport)
- [ ] German copy matches spec exactly
- [ ] Type checking passes (tsc)
- [ ] Linting passes (eslint)
- [ ] Accessibility basics (form labels, ARIA, keyboard nav)

---

## 🎯 Phase 7: Approver Interface

**Status:** 🚫 **Blocked** (Phases 5-6 + Increment 2)
**Dependencies:**
  1. Increment 2 complete (approval backend: POST /approve, POST /deny)
  2. Phase 5-6 complete (frontend core components)
**Estimated Effort:** 2-3 days

**📋 Test Matrix:** `/docs/implementation/phase-7-test-matrix.md` - 37-42 detailed E2E test specifications

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
- [ ] All E2E tests passing (~37-42 total)
- [ ] Mobile tested (375px viewport)
- [ ] German copy matches spec exactly
- [ ] Type checking passes (tsc)
- [ ] Linting passes (eslint)
- [ ] Accessibility basics (ARIA labels, keyboard nav)

---

## 📚 Specification References

**Business Rules:**
- `/docs/foundation/business-rules.md` - BR-001, 002, 003, 004, 005, 010, 011, 014, 015, 016, 017, 019, 020, 023, 024, 025, 026, 027, 029

**Phase Specifications:**
- `/docs/implementation/phase-5-frontend-calendar.md`
- `/docs/implementation/phase-5-br-analysis.md` (33KB)
- `/docs/implementation/phase-6-frontend-booking.md`
- `/docs/implementation/phase-6-test-matrix.md` (44 tests)
- `/docs/implementation/phase-7-approver-interface.md`
- `/docs/implementation/phase-7-test-matrix.md` (37-42 tests)

**German Copy:**
- `/docs/specification/ui-screens.md` - All UI labels and button text
- `/docs/specification/error-handling.md` - All error messages

**Design:**
- `/docs/design/component-guidelines.md` - Shadcn/ui component usage
- `/docs/design/design-tokens.md` - Colors, spacing, typography

---

## 🎓 Known Gotchas (from Phase Analysis Files)

### BR-005: Extend vs Shorten Detection is Complex
**Why:** Must detect if new range extends BEYOND original bounds (earlier start OR later end).
**Example:** Original: Jan 5-10
- Edit to Jan 4-10 → **Extend** (earlier start) → Reset approvals
- Edit to Jan 5-11 → **Extend** (later end) → Reset approvals
- Edit to Jan 6-9 → **Shorten** → Keep approvals
**Solution:** Compare new start/end with original start/end carefully.

### BR-020: Link Detection Must Be Case-Insensitive
**Why:** Users can type "HTTP://", "Www", "MAILTO:", etc.
**Solution:** Use regex with `i` flag: `/http[s]?:\/\//i`, `/www\./i`, `/mailto:/i`

### BR-023: Query Correctness is CRITICAL
**Why:** Wrong filtering = approvers see wrong data or miss approvals.
**Outstanding query:** `response = NoResponse AND status = Pending AND sorted LastActivityAt DESC`
**History query:** `All statuses (Pending, Confirmed, Denied) AND sorted LastActivityAt DESC`
**Common mistake:** Forgetting to filter by approver (each approver sees only their own items).

### BR-024: Concurrency Tests Are Mandatory
**Why:** Two approvers clicking at the same time WILL happen in production.
**Solution:** Write Playwright tests that simulate concurrent clicks with `Promise.all()`.

### Date Picker Conflicts Must Refresh
**Why:** While user is picking dates, conflicts can change (another user books).
**Solution:** Fetch conflicts on every month navigation, not just on form load.

### Mobile Date Picker UX
**Why:** Native mobile date pickers (iOS/Android) don't support date ranges or blocking.
**Solution:** Build custom date picker, not `<input type="date">`.

### Idempotency Edge Case (BR-010)
**Why:** User clicks approve, network timeout, clicks again.
**Solution:** Backend must return success on second click, not error.

---

## 🔄 Next Steps

**To start Increment 3:**

1. **FIRST:** Verify Increment 2 complete (approval backend done)
2. **Configure Playwright** (see blocker section above)
3. **Start Phase 5** (Web Calendar)
   - Read phase-5-frontend-calendar.md
   - Read phase-5-br-analysis.md
   - Write Playwright tests first (calendar rendering, navigation)
   - Implement month view component
   - Implement year view component
   - Implement booking details modal
   - Verify all tests pass

4. **Continue with Phase 6** (Web Booking)
   - Build date picker (US-6.2) - reusable component
   - Build create form (US-6.1)
   - Build edit form (US-6.3 - watch BR-005 carefully!)

5. **Finish with Phase 7** (Approver Interface)
   - Write concurrency tests (BR-024) first
   - Build approver overview (Outstanding + History tabs)
   - Build approve action (one-click)
   - Build deny dialog with comment validation (BR-020)

**When starting, always read `/project/BACKLOG.md` first to confirm priority.**

---

**After Increment 3:** Frontend is 100% complete, ready for Phase 8 (Production Polish)
