# Increment 3: Frontend Core

**Status:** 🚫 **Blocked** (Playwright not configured)
**Phases:** 5, 6
**Dependencies:** Increment 1 complete + Playwright configured
**Target Start:** After Phase 2 complete AND Playwright setup
**Estimated Effort:** 7-8 days

---

## 📋 Overview

**Goal:** Build calendar display and booking forms (create/edit) for end users.

**Deliverables:**
- Calendar component (month view, year view)
- Booking detail modal
- Date picker with conflict visualization
- Create booking form (with validation)
- Edit booking form (with approval reset detection)
- All German UI copy from specifications
- Mobile-responsive (iPhone 8 class, 375px width)

**Success Criteria:**
- All Playwright E2E tests passing (~96 total)
- Mobile tested (375px viewport)
- German copy matches spec exactly
- Type safety throughout (TypeScript strict)
- Lint passing (eslint)
- Accessibility basics (keyboard navigation, ARIA labels)

---

## 📊 Progress Summary

| Phase | User Stories | Draft | Specified | Implemented | Status |
|-------|--------------|-------|-----------|-------------|--------|
| **5** | 3 | 0 | 3 | 0 | 🚫 Blocked (Playwright) |
| **6** | 3 | 0 | 3 | 0 | 🚫 Blocked (Phase 5) |
| **Total** | **6** | **0** | **6** | **0** | **🚫 0%** |

---

## 🚧 Critical Blocker

### Playwright Not Configured

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
- Screenshots on failure
- 2 retries on failure

**Verify:**
```bash
npx playwright test --list  # Should show test files
npx playwright test          # Should run tests
```

**After resolution:** Remove blocker status, move increment to Pending.

---

## 🎯 Phase 5: Web Calendar

**Status:** 🚫 **Blocked** (Playwright)
**Dependencies:** Playwright configured, Phase 2 API (calendar endpoint)

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

**Status:** 🚫 **Blocked** (Phase 5)
**Dependencies:** Phase 5 complete (calendar component), Playwright configured

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

## 📚 Specification References

**Business Rules:**
- `/docs/foundation/business-rules.md` - BR-001, 002, 004, 005, 011, 014, 016, 017, 019, 020, 025, 026, 027, 029

**Phase Specifications:**
- `/docs/implementation/phase-5-frontend-calendar.md`
- `/docs/implementation/phase-5-br-analysis.md` (33KB)
- `/docs/implementation/phase-6-frontend-booking.md`

**German Copy:**
- `/docs/specification/ui-screens.md` - All UI labels and button text
- `/docs/specification/error-handling.md` - All error messages

**Design:**
- `/docs/design/component-guidelines.md` - Shadcn/ui component usage
- `/docs/design/design-tokens.md` - Colors, spacing, typography

---

## 🎓 Known Gotchas (from 8 Analysis Files)

### BR-005: Extend vs Shorten Detection is Complex
**Why:** Must detect if new range extends BEYOND original bounds (earlier start OR later end).
**Example:** Original: Jan 5-10
- Edit to Jan 4-10 → **Extend** (earlier start) → Reset approvals
- Edit to Jan 5-11 → **Extend** (later end) → Reset approvals
- Edit to Jan 6-9 → **Shorten** → Keep approvals
**Solution:** Compare new start/end with original start/end carefully.

### BR-020: Link Detection Must Be Case-Insensitive
**Why:** Users can type "HTTP://", "Www", etc.
**Solution:** Use regex with case-insensitive flag: `/http[s]?:\/\//i`

### Date Picker Conflicts Must Refresh
**Why:** While user is picking dates, conflicts can change (another user books).
**Solution:** Fetch conflicts on every month navigation, not just on form load.

### Mobile Date Picker UX
**Why:** Native mobile date pickers (iOS/Android) don't support date ranges or blocking.
**Solution:** Build custom date picker, not `<input type="date">`.

---

## 🔄 Next Steps

**To start Increment 3:**

1. **FIRST:** Configure Playwright (see blocker section above)
2. Verify Increment 1 complete (Phase 2 calendar endpoint works)
3. Start with US-5.1 (Month View)
   - Read phase-5-frontend-calendar.md
   - Read phase-5-br-analysis.md
   - Write Playwright tests first (calendar rendering, navigation)
   - Implement component
   - Verify tests pass

4. Continue with US-5.2, US-5.3 (Year view, Details modal)
5. Build date picker (US-6.2)
6. Build create form (US-6.1)
7. Build edit form (US-6.3 - watch BR-005 carefully!)

**When starting, always read `/project/BACKLOG.md` first to confirm priority.**
