# Phases 3-8: Implementation Guide Summary

## Overview

This document provides a consolidated summary of all business rules, test requirements, and implementation guidance for Phases 3-8. Each phase document has been analyzed and the following information extracted for AI agent implementation.

**Total Coverage:**
- **Phase 3:** 17 BRs, ~49 tests
- **Phase 4:** 10 BRs, ~75 tests
- **Phase 5:** 9 BRs, ~52 tests
- **Phase 6:** 13 BRs, ~44 tests
- **Phase 7:** Multiple BRs, ~40 tests
- **Phase 8:** Multiple BRs, ~140 tests

---

## Phase 3: Approval Flow

**See:** Complete detailed documentation in `phase-3-approval-flow.md` (to be updated)

**Applicable BRs:** BR-003, BR-004, BR-009, BR-010, BR-014, BR-015, BR-018, BR-022, BR-023, BR-024

**Critical Implementation Points:**
- **BR-024 (First-Action-Wins):** Use SELECT FOR UPDATE for all approval/denial operations
- **BR-010 (Idempotency):** Repeat actions return "Schon erledigt" result pages
- **BR-004 (Denial):** Non-blocking (frees dates), requires comment, hidden from public
- **BR-015 (Self-Approval):** Auto-approval counted at submission, applies again at reopen

**Test Count:** ~49 tests total
- US-3.1 (Approve): 14 tests
- US-3.2 (Deny): 17 tests
- US-3.3 (Reopen): 18 tests

---

## Phase 4: Email Integration

**See:** Complete detailed documentation in `phase-4-email-integration.md` (to be updated)

**Applicable BRs:** BR-001, BR-003, BR-004, BR-005, BR-009, BR-010, BR-015, BR-016, BR-022, BR-024

**Critical Implementation Points:**
- **BR-022 (Email Retries):** 3 attempts with exponential backoff (5s, 25s)
- **BR-015 (Self-Approver Suppression):** Don't email self-approver in "Request Submitted"
- **BR-009 (Weekly Digest):** Sunday 09:00 Europe/Berlin, Pending + NoResponse + aged ≥5 days
- **BR-005 (Edit Impact):** Shorten = no emails to approvers; Extend = re-approval emails to all 3

**11 Email Types:**
1. Request Submitted (to approvers except self)
2. Approve (Not Final) - to requester
3. Final Approval - to all 4
4. Deny - to all 4 (BR-004 critical)
5. Edit: Shorten - to requester only
6. Edit: Extend - to 3 approvers
7. Reopen - to 3 approvers
8. Cancel (Pending/Confirmed) - to all 4
9. Cancel (Denied) - to requester only
10. Link Recovery
11. Weekly Digest (per-approver)

**Test Count:** ~75 tests total

---

## Phase 5: Web Calendar (Frontend)

**See:** Complete detailed documentation in `phase-5-frontend-calendar.md` (to be updated)

**Applicable BRs:** BR-001, BR-002, BR-004, BR-011, BR-014, BR-016, BR-023, BR-026, BR-027

**Critical Implementation Points:**
- **BR-004 (Privacy):** Denied bookings completely hidden from public calendar
- **BR-001 (Multi-Month Display):** Booking Jan 15-Mar 15 appears in Jan, Feb, AND Mar calendars
- **BR-014 (Timezone):** Past/present flip at 00:00 Europe/Berlin (not UTC)
- **BR-011 (German):** All text in German with exact copy from ui-screens.md

**Mobile Requirements:**
- Minimum viewport: 375×667px (iPhone 8)
- Tap targets: ≥44×44pt
- No hover dependencies
- Affiliation colors with WCAG AA contrast

**Test Count:** ~52 tests total (Playwright E2E)
- US-5.1 (Calendar Display): 23 tests
- US-5.2 (Navigation): 12 tests
- US-5.3 (Booking Details): 17 tests

---

## Phase 6: Web Booking (Frontend)

**See:** Complete detailed documentation in `phase-6-frontend-booking.md` (to be updated)

**Applicable BRs:** BR-001, BR-002, BR-005, BR-011, BR-014, BR-016, BR-017, BR-018, BR-019, BR-020, BR-025, BR-026, BR-027

**Critical Implementation Points:**
- **BR-005 (Approval Reset UI):** Show warning when extending dates: "Approvals will be reset"
- **BR-027 (Long Stay Warning):** Dialog for >7 days: "Diese Anfrage umfasst {{TotalDays}} Tage. Möchtest du fortfahren?"
- **BR-019 (First Name Validation):** Regex `^[A-Za-zÀ-ÿ\s'-]+$`, max 40, trim
- **BR-020 (Link Detection):** Block http://, https://, www, mailto: (case-insensitive)

**Form Field Validation:**
- **Zod schema** for all client-side validation
- **Server-side validation** always enforced (never trust client)
- **Inline errors** on blur + submit

**Test Count:** ~44 tests total (Playwright E2E)
- US-6.1 (Create Form): 18 tests
- US-6.2 (Date Picker): 12 tests
- US-6.3 (Edit Booking): 14 tests

---

## Phase 7: Approver Interface (Frontend)

**See:** Complete detailed documentation in `phase-7-approver-interface.md` (to be updated)

**Applicable BRs:** BR-003, BR-004, BR-009, BR-010, BR-014, BR-015, BR-020, BR-023, BR-024

**Critical Implementation Points:**
- **BR-023 (Approver Lists):** Outstanding = NoResponse + Pending only; History = all statuses; sorted by last_activity_at DESC
- **BR-024 (First-Action-Wins UI):** Show "Schon erledigt" result pages for concurrent actions
- **BR-010 (Idempotency):** Action links work after page refresh, network failure
- **BR-020 (Comment Validation):** Deny comment must not contain URLs

**Outstanding Tab Query:**
```sql
WHERE approval.party = {current_approver}
  AND approval.decision = NoResponse
  AND booking.status = Pending
ORDER BY booking.last_activity_at DESC
```

**History Tab Query:**
```sql
WHERE approval.party = {current_approver}
ORDER BY booking.last_activity_at DESC
```

**Test Count:** ~40 tests total (Playwright E2E)
- US-7.1 (Approver Overview): 15 tests
- US-7.2 (One-Click Approve): 15 tests
- US-7.3 (Deny with Comment): 10 tests

---

## Phase 8: Polish & Production

**See:** Complete detailed documentation in `phase-8-polish.md` (to be updated)

**Applicable BRs:** BR-010, BR-012, BR-013, BR-021, BR-022, BR-023, BR-024, BR-028, BR-029

**Critical Implementation Points:**
- **BR-023 (N+1 Prevention):** Eager loading with selectinload() on all approver queries (learned from Phase 1)
- **BR-024/BR-029 (Concurrency):** SELECT FOR UPDATE verified in production under load
- **BR-028 (Auto-Cleanup):** Background job runs 04:00 Europe/Berlin daily
- **BR-013 (Archive Purge):** Background job purges bookings end_date < today - ARCHIVE_DAYS

**Performance Targets:**
- Lighthouse Performance ≥90
- Time to Interactive <3s
- No N+1 queries (verified)
- Core Web Vitals pass

**Accessibility Targets (WCAG AA):**
- axe-core 0 violations
- All ARIA labels in German
- 4.5:1 color contrast minimum
- Keyboard navigation complete
- Screen reader support verified

**Production Infrastructure:**
- API: Fly.io Frankfurt (Europe proximity)
- Web: Vercel (global CDN)
- DB: PostgreSQL with connection pooling
- Email: Resend with retry logic

**Test Count:** ~140 tests total
- US-8.1 (Performance): 21 tests
- US-8.2 (Accessibility): 55 tests
- US-8.3 (Production Deployment): 64 tests

---

## Cross-Phase Dependencies

### **Phase 2 → Phase 3 → Phase 4**
- Phase 2 creates booking + approvals
- Phase 3 handles approve/deny/reopen logic
- Phase 4 sends email notifications for all actions

**Critical:** Phase 4 email tests depend on Phase 2-3 endpoints working.

### **Phase 2-4 (API) → Phase 5-7 (Frontend)**
- Frontend depends on working API endpoints
- Token validation must be consistent
- German copy must match exactly between API errors and frontend display

**Critical:** Phase 5-7 E2E tests require Phase 2-4 API running.

### **All Phases → Phase 8**
- Phase 8 validates everything works in production
- Performance tests require full implementation (Phases 1-7)
- Accessibility tests require all UI (Phases 5-7)

---

## German Copy Master Reference

**All German text must be exact from these sources:**

| Category | Source File | Lines |
|----------|-------------|-------|
| Error messages | `docs/specification/error-handling.md` | All |
| Email templates | `docs/specification/notifications.md` | All |
| UI labels/buttons | `docs/specification/ui-screens.md` | All |

**Rules:**
- Informal "du" tone (never "Sie")
- Date format: DD.–DD.MM.YYYY with en-dash
- Party size: "n Personen" (even for 1)
- No English fallbacks anywhere

---

## Test-First Workflow Reminder

**For EVERY phase, EVERY user story:**

1. ✅ Complete pre-implementation checklist
2. ✅ Write ALL tests FIRST (must fail initially)
3. ✅ Confirm tests fail
4. ✅ Implement code
5. ✅ Confirm tests pass
6. ✅ Run mypy + ruff (or tsc + eslint for frontend)
7. ✅ Self-review
8. ✅ Commit

**DO NOT skip this workflow. Phase 1 had 17 issues because tests came after code.**

---

## Common Gotchas Across All Phases

### **BR-001 (Inclusive End Date)**
```python
# ✓ CORRECT
total_days = (end_date - start_date).days + 1  # Jan 1-5 = 5 days

# ✗ WRONG
total_days = (end_date - start_date).days  # Jan 1-5 = 4 days (off by one)
```

### **BR-002 (Conflict Detection)**
```python
# ✓ CORRECT: Multi-month bookings detected
WHERE start_date <= month_end AND end_date >= month_start

# ✗ WRONG: Only shows bookings starting in month
WHERE EXTRACT(month FROM start_date) = month
```

### **BR-004 (Denied Privacy)**
```python
# ✓ CORRECT
if booking.status == Denied and not has_valid_token:
    return 404  # Hidden from public

# ✗ WRONG
if booking.status == Denied:
    return booking  # Privacy violation
```

### **BR-014 (Timezone)**
```python
# ✓ CORRECT
from zoneinfo import ZoneInfo
today = datetime.now(ZoneInfo("Europe/Berlin")).date()

# ✗ WRONG
today = datetime.utcnow().date()  # Wrong timezone
```

### **BR-023 (Ordering)**
```python
# ✓ CORRECT
.order_by(Booking.last_activity_at.desc())

# ✗ WRONG
.order_by(Booking.created_at.desc())  # Wrong field
```

### **BR-024 (Concurrency)**
```python
# ✓ CORRECT
booking = await session.execute(
    select(Booking).where(Booking.id == id).with_for_update()
)

# ✗ WRONG
booking = await session.execute(
    select(Booking).where(Booking.id == id)  # Race condition
)
```

---

## Implementation Order

**Recommended sequence:**

1. **Phase 0-1:** ✅ Complete (foundation, data layer)
2. **Phase 2:** API endpoints (booking CRUD)
3. **Phase 3:** API endpoints (approval flow)
4. **Phase 4:** Email service (critical for testing Phases 2-3 fully)
5. **Phase 5-7:** Frontend (can partially overlap)
6. **Phase 8:** Polish, accessibility, production deployment

**Parallel work possible:**
- Phase 5-7 can partially overlap (different UI areas)
- Phase 4 can start while Phase 2-3 finish

---

## Success Criteria Summary

**Every phase must meet ALL of these:**

- [ ] Pre-implementation checklist completed
- [ ] All tests written FIRST
- [ ] All tests initially FAILED
- [ ] All tests now PASS
- [ ] Type checks pass (mypy/tsc)
- [ ] Linting passes (ruff/eslint)
- [ ] Code coverage ≥80%
- [ ] All applicable BRs enforced
- [ ] German copy exact from specs
- [ ] Self-review completed
- [ ] Mobile tested (375px for frontend phases)
- [ ] No N+1 query problems
- [ ] Concurrency safety verified (BR-024, BR-029)
- [ ] Documentation updated

---

**This summary complements the individual phase documents. Each phase document provides detailed user stories, Gherkin scenarios, and complete test enumerations.**
