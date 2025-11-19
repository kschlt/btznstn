# Increment 2: Backend Business Logic

**Status:** ⏸️ **Pending**
**Phases:** 3, 4
**Dependencies:** Increment 1 complete
**Target Start:** After Phase 2 complete
**Estimated Effort:** 5-6 days

---

## 📋 Overview

**Goal:** Implement approval workflow and email notification system.

**Deliverables:**
- Approve/Deny/Reopen endpoints with concurrency safety (BR-024)
- Resend email integration
- 11 German email templates
- Email retry logic (BR-022: 3 attempts, exponential backoff)
- Weekly digest job (BR-009)

**Success Criteria:**
- All approval endpoints working with SELECT FOR UPDATE
- All email templates implemented (exact German copy)
- Email retry logic verified
- Weekly digest scheduled and tested
- Code coverage ≥80%

---

## 📊 Progress Summary

| Phase | User Stories | Draft | Specified | Implemented | Status |
|-------|--------------|-------|-----------|-------------|--------|
| **3** | 3 | 0 | 3 | 0 | ⏸️ Pending |
| **4** | 4 | 0 | 4 | 0 | ⏸️ Pending |
| **Total** | **7** | **0** | **7** | **0** | **⏸️ 0%** |

---

## 🎯 Phase 3: Approval Flow

**Status:** ⏸️ **Pending**
**Dependencies:** Phase 2 complete (booking endpoints exist)

### User Stories (Dependency-Based Order)

#### US-3.1: Approve Endpoint
**Status:** ✅ **Specified**
**Estimated Tests:** 13-15
**Priority:** P0 (Core functionality)

**Description:** Implement POST /api/v1/bookings/{id}/approve for approvers to approve bookings.

**Key Business Rules:**
- BR-003: Three approvals required
- BR-010: Idempotent (same result on retry)
- BR-015: Self-approval (auto-approved if requester is approver)
- BR-024: **CRITICAL** - First-action-wins (SELECT FOR UPDATE)

**Acceptance Criteria:**
- [ ] POST /api/v1/bookings/{id}/approve?token={approver_token} endpoint
- [ ] Token validation (must be one of 3 approvers)
- [ ] Idempotent (approve twice = success both times, shows "Schon erledigt")
- [ ] SELECT FOR UPDATE prevents race conditions
- [ ] If 3rd approval → Transition to Confirmed
- [ ] Self-approval detected and allowed (BR-015)
- [ ] German result messages ("Danke – du hast zugestimmt")
- [ ] 13-15 tests passing

**German Copy:**
- Success: "Danke – du hast zugestimmt" (notifications.md)
- Already done: "Schon erledigt. Die Buchung ist bereits bestätigt." (BR-024)

**Files:**
- `/docs/implementation/phase-3-approval-flow.md` - Specification
- `/docs/implementation/phase-3-br-analysis.md` - BR analysis (32KB)
- Tests: `/api/tests/integration/test_approve.py` (to create)

---

#### US-3.2: Deny Endpoint
**Status:** ✅ **Specified**
**Estimated Tests:** 15-18
**Priority:** P0 (Core functionality)

**Description:** Implement POST /api/v1/bookings/{id}/deny for approvers to deny bookings with comment.

**Key Business Rules:**
- BR-004: Denial requires comment, frees dates immediately, hidden from public
- BR-010: Idempotent
- BR-020: **CRITICAL** - Block links in comment (http://, https://, www, mailto:)
- BR-024: First-action-wins (SELECT FOR UPDATE)

**Acceptance Criteria:**
- [ ] POST /api/v1/bookings/{id}/deny?token={approver_token} endpoint
- [ ] Comment required (validated, max 500 chars)
- [ ] Link detection in comment (BR-020) - reject with German error
- [ ] SELECT FOR UPDATE prevents race conditions
- [ ] Status → Denied, dates freed immediately
- [ ] Booking hidden from public calendar (BR-004)
- [ ] Idempotent (deny twice = success)
- [ ] German messages ("Danke – du hast abgelehnt")
- [ ] 15-18 tests passing

**German Copy:**
- Success: "Danke – du hast abgelehnt"
- Comment required: "Bitte gib einen kurzen Grund an."
- Link blocked: "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden." (error-handling.md line 367)

**Files:**
- Specification: `phase-3-approval-flow.md`
- Tests: `/api/tests/integration/test_deny.py` (to create)

---

#### US-3.3: Reopen from Denied
**Status:** ✅ **Specified**
**Estimated Tests:** 8-10
**Priority:** P1 (Secondary functionality)

**Description:** Allow requester to reopen Denied bookings if dates are still free.

**Key Business Rules:**
- BR-018: Reopen guard - cannot reopen if new conflict exists
- BR-005: Reopen resets approvals to NoResponse

**Acceptance Criteria:**
- [ ] POST /api/v1/bookings/{id}/reopen?token={requester_token} endpoint
- [ ] Only works on Denied bookings
- [ ] Conflict check (BR-018) - if dates now taken, show error
- [ ] Status → Pending, approvals reset to NoResponse
- [ ] German messages
- [ ] 8-10 tests passing

**German Copy:**
- Success: "Anfrage erneut gestellt"
- Conflict: "Dieser Zeitraum überschneidet sich..." (reuse from BR-002)

---

### Phase 3: Definition of Done

- [ ] All 3 user stories implemented
- [ ] SELECT FOR UPDATE working (verified with concurrent tests)
- [ ] Idempotency working (all endpoints)
- [ ] German messages match spec exactly
- [ ] All tests passing (~36-43 tests total)
- [ ] Type checking passes (mypy)
- [ ] Linting passes (ruff)
- [ ] Code coverage ≥80%

---

## 🎯 Phase 4: Email Integration

**Status:** ⏸️ **Pending**
**Dependencies:** Phase 3 complete (approval status needed for emails)

### User Stories (Dependency-Based Order)

#### US-4.1: Resend Integration
**Status:** ✅ **Specified**
**Estimated Tests:** 5-8
**Priority:** P0 (Foundation)

**Description:** Set up Resend API integration for sending emails.

**Acceptance Criteria:**
- [ ] Resend account created
- [ ] API key stored in environment variable (RESEND_API_KEY)
- [ ] Resend client initialized in backend
- [ ] Test email sending works
- [ ] Error handling for API failures
- [ ] 5-8 tests passing (mock Resend API)

**Files:**
- Config: `/api/app/config.py` (add RESEND_API_KEY)
- Service: `/api/app/services/email_service.py` (to create)
- Tests: `/api/tests/integration/test_email_service.py` (to create)

---

#### US-4.2: Email Templates (11 templates)
**Status:** ✅ **Specified**
**Estimated Tests:** 20-25
**Priority:** P0 (Core functionality)

**Description:** Implement all 11 German email templates from specification.

**Templates to Implement:**
1. Booking created → Requester
2. Booking created → 3 Approvers
3. Approved (not final) → Requester
4. Approved (3rd, Confirmed) → Requester
5. Approved (3rd, Confirmed) → All 3 Approvers
6. Denied → Requester
7. Denied → Other 2 Approvers
8. Booking edited (date extend) → Requester + 3 Approvers
9. Booking canceled → Requester
10. Booking canceled → 3 Approvers
11. Weekly digest → Approver (old NoResponse items)

**Acceptance Criteria:**
- [ ] All 11 templates implemented
- [ ] Exact German copy from `/docs/specification/notifications.md`
- [ ] Dynamic placeholders ({{Vorname}}, {{StartDatum}}, etc.)
- [ ] Informal "du" tone throughout
- [ ] Links with tokens work correctly
- [ ] 20-25 tests (one per template + edge cases)

**German Copy Source:**
- `/docs/specification/notifications.md` (864 lines of exact email copy)

**Files:**
- Templates: `/api/app/templates/email/` (to create)
- Service: Update `/api/app/services/email_service.py`
- Tests: Update `/api/tests/integration/test_email_service.py`

---

#### US-4.3: Email Retry Logic (BR-022)
**Status:** ✅ **Specified**
**Estimated Tests:** 10-12
**Priority:** P0 (Reliability)

**Description:** Implement 3-attempt retry with exponential backoff for email sending.

**Key Business Rules:**
- BR-022: 3 attempts with exponential backoff (2s, 4s, 8s)
- Log failures with correlation ID

**Acceptance Criteria:**
- [ ] Email send retries up to 3 times on transient failure
- [ ] Exponential backoff: 2s, 4s, 8s between retries
- [ ] Permanent failures (e.g., invalid email) don't retry
- [ ] All failures logged with correlation ID
- [ ] Email content consistent across retries (no mutations)
- [ ] 10-12 tests passing (mock failure scenarios)

**Files:**
- Service: Update `/api/app/services/email_service.py`
- Tests: Update `/api/tests/integration/test_email_service.py`

---

#### US-4.4: Weekly Digest (BR-009)
**Status:** ✅ **Specified**
**Estimated Tests:** 12-15
**Priority:** P1 (Nice-to-have)

**Description:** Implement weekly digest email for approvers with old outstanding items.

**Key Business Rules:**
- BR-009: Weekly digest on Sundays at 09:00 Europe/Berlin
- Only includes Pending bookings where approver response = NoResponse
- Only includes bookings created ≥7 days ago (not fresh items)
- Excludes past bookings (EndDate < today)

**Acceptance Criteria:**
- [ ] Background job scheduled (Sunday 09:00 Europe/Berlin)
- [ ] Query finds old NoResponse items for each approver
- [ ] Email sent to approver with list of outstanding items
- [ ] German copy matches spec
- [ ] Job logs execution (success/failure)
- [ ] 12-15 tests passing

**German Copy:**
- Subject: "Deine ausstehenden Anfragen für Betzenstein"
- Body: Template from `notifications.md` (weekly digest section)

**Files:**
- Job: `/api/app/jobs/weekly_digest.py` (to create)
- Service: Update `/api/app/services/email_service.py`
- Tests: `/api/tests/integration/test_weekly_digest.py` (to create)

---

### Phase 4: Definition of Done

- [ ] All 4 user stories implemented
- [ ] Resend integration working
- [ ] All 11 email templates implemented (exact German copy)
- [ ] Email retry logic working (verified with failure tests)
- [ ] Weekly digest job scheduled and tested
- [ ] All tests passing (~47-60 tests total)
- [ ] Type checking passes
- [ ] Linting passes
- [ ] Code coverage ≥80%

---

## 📚 Specification References

**Business Rules:**
- `/docs/foundation/business-rules.md` - BR-003, 004, 009, 010, 015, 018, 020, 022, 024

**Phase Specifications:**
- `/docs/implementation/phase-3-approval-flow.md`
- `/docs/implementation/phase-3-br-analysis.md` (32KB detailed analysis)
- `/docs/implementation/phase-4-email-integration.md`
- `/docs/implementation/phase-4-br-analysis.md` (32KB detailed analysis)

**German Copy:**
- `/docs/specification/notifications.md` - All 11 email templates
- `/docs/specification/error-handling.md` - All error messages

**API Design:**
- `/docs/design/api-specification.md` - Endpoint details

---

## 🎓 Known Gotchas

### BR-024: SELECT FOR UPDATE is Critical
**Why:** Two approvers clicking at the same time WILL cause race conditions without locking.
**Solution:** Always wrap approval/deny in transaction with `SELECT FOR UPDATE` on booking row.

### BR-022: Email Retries Must Not Mutate Content
**Why:** If email content changes between retries, user gets inconsistent messages.
**Solution:** Generate email body once, store it, retry with same content.

### Weekly Digest Timezone
**Why:** Job must run at 09:00 Europe/Berlin, not UTC.
**Solution:** Use timezone-aware scheduler or convert UTC to Europe/Berlin.

---

## 🔄 Next Steps

**To start Increment 2:**

1. Verify Increment 1 complete (all Phase 2 user stories done)
2. Start with US-3.1 (Approve endpoint)
   - Read phase-3-approval-flow.md
   - Read phase-3-br-analysis.md (critical BR-024 details)
   - Write tests first (SELECT FOR UPDATE concurrency tests)
   - Implement endpoint
   - Verify idempotency

3. Continue with US-3.2, 3.3 (Deny, Reopen)
4. Set up Resend (US-4.1)
5. Implement email templates (US-4.2)
6. Add retry logic (US-4.3)
7. Schedule weekly digest (US-4.4)

**When starting, always read `/project/BACKLOG.md` first to confirm priority.**
