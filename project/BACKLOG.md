# Project Backlog

**Last Updated:** 2025-11-19
**Current Focus:** Complete Increment 1 (Phase 2)

---

## 🔥 High Priority (Do This Week)

### Complete Phase 2: Booking API

#### US-2.3: Edit Booking (PATCH /api/v1/bookings/{id})
- [ ] **Read specification:** `/docs/implementation/phase-2-booking-api.md` (US-2.3)
- [ ] **Read BR-005:** Date extend resets approvals; shorten keeps approvals
- [ ] **Read BR-014:** Past bookings are read-only (EndDate < today)
- [ ] **Write tests first:**
  - [ ] Test edit with date shortening (approvals kept)
  - [ ] Test edit with date extension (approvals reset)
  - [ ] Test edit non-date fields (party size, description - approvals kept)
  - [ ] Test edit past booking (rejected)
  - [ ] Test edit with conflict detection
  - [ ] Test German error messages
- [ ] **Implement endpoint:**
  - [ ] PATCH /api/v1/bookings/{id}
  - [ ] Accept token parameter
  - [ ] Validate requester owns booking
  - [ ] Detect date change type (extend vs shorten)
  - [ ] Reset approvals if extend (BR-005)
  - [ ] Keep approvals if shorten or non-date changes
  - [ ] Conflict detection (BR-002)
  - [ ] Return updated booking
- [ ] **Verify:**
  - [ ] All tests pass
  - [ ] Type checking passes (mypy)
  - [ ] Linting passes (ruff)
  - [ ] German error messages match spec

#### US-2.4: Cancel Booking (DELETE /api/v1/bookings/{id})
- [ ] **Read specification:** `/docs/implementation/phase-2-booking-api.md` (US-2.4)
- [ ] **Read BR-006:** Requester can cancel Pending/Confirmed (not Denied/Canceled)
- [ ] **Write tests first:**
  - [ ] Test cancel Pending booking (success)
  - [ ] Test cancel Confirmed booking (success)
  - [ ] Test cancel Denied booking (rejected - already terminal)
  - [ ] Test cancel already Canceled (idempotent, shows "Schon storniert")
  - [ ] Test cancel past booking (should be allowed or rejected? Check spec)
  - [ ] Test German messages
- [ ] **Implement endpoint:**
  - [ ] DELETE /api/v1/bookings/{id}
  - [ ] Accept token parameter
  - [ ] Validate requester owns booking
  - [ ] Check current status (Pending or Confirmed allowed)
  - [ ] Transition to Canceled
  - [ ] Move to Archive (BR-013)
  - [ ] Return success message
- [ ] **Verify:**
  - [ ] All tests pass
  - [ ] Type checking passes
  - [ ] Linting passes
  - [ ] Idempotency works (cancel twice = success both times)

#### US-2.5: Calendar View (GET /api/v1/calendar)
- [ ] **Read specification:** `/docs/implementation/phase-2-booking-api.md` (US-2.5)
- [ ] **Read BR-002:** Show Pending and Confirmed bookings (not Denied/Canceled)
- [ ] **Read BR-014:** Past bookings shown as read-only
- [ ] **Write tests first:**
  - [ ] Test calendar month view (query by month/year)
  - [ ] Test calendar includes Pending bookings
  - [ ] Test calendar includes Confirmed bookings
  - [ ] Test calendar excludes Denied bookings (BR-004)
  - [ ] Test calendar excludes Canceled bookings
  - [ ] Test date range filtering works correctly
  - [ ] Test ordering (by start_date ASC)
  - [ ] Test is_past field calculated correctly (Europe/Berlin timezone)
- [ ] **Implement endpoint:**
  - [ ] GET /api/v1/calendar?month=2&year=2025
  - [ ] Query bookings where status IN (Pending, Confirmed)
  - [ ] Filter by date range (month overlap)
  - [ ] Calculate is_past for each booking (BR-014)
  - [ ] Return list of bookings with minimal data (public view)
  - [ ] Optimize query (eager load if needed)
- [ ] **Verify:**
  - [ ] All tests pass
  - [ ] Query performance acceptable (<100ms)
  - [ ] Date math correct (inclusive ranges)
  - [ ] Privacy respected (no emails in response)

---

### Technical Blockers

#### Configure Playwright (Frontend Work)
- [ ] **Navigate to frontend:**
  ```bash
  cd /home/user/btznstn/web
  ```
- [ ] **Install Playwright:**
  ```bash
  npm install -D @playwright/test
  npx playwright install
  ```
- [ ] **Create `playwright.config.ts`:**
  - [ ] Configure iPhone 8 viewport (375×667px)
  - [ ] Set up test directories (`/tests/e2e/`)
  - [ ] Configure browsers (Chromium, Firefox, WebKit)
  - [ ] Set up screenshots on failure
  - [ ] Configure retries (2 retries on failure)
- [ ] **Create example test:**
  - [ ] `/web/tests/e2e/example.spec.ts`
  - [ ] Basic navigation test
  - [ ] Verify viewport works
- [ ] **Run test:**
  ```bash
  npx playwright test
  ```
- [ ] **Verify:** Test runs and passes

**Estimated Time:** 1 hour
**Blocks:** Increments 3-4 (all frontend work)

---

### Documentation Organization

#### Move Phase Analysis Files
- [ ] **Move Phase 6 files:**
  ```bash
  mv /home/user/btznstn/PHASE_6_INDEX.md \
     /home/user/btznstn/docs/implementation/phase-6-index.md

  mv /home/user/btznstn/PHASE_6_BR_ANALYSIS.md \
     /home/user/btznstn/docs/implementation/phase-6-br-analysis.md

  mv /home/user/btznstn/PHASE_6_BR_ANALYSIS_SUMMARY.md \
     /home/user/btznstn/docs/implementation/phase-6-br-summary.md

  mv /home/user/btznstn/PHASE_6_QUICK_REFERENCE.md \
     /home/user/btznstn/docs/implementation/phase-6-quick-reference.md

  mv /home/user/btznstn/PHASE_6_TEST_MATRIX.md \
     /home/user/btznstn/docs/implementation/phase-6-test-matrix.md
  ```

- [ ] **Move Phase 7 files:**
  ```bash
  mv /home/user/btznstn/PHASE-7-BR-ANALYSIS.md \
     /home/user/btznstn/docs/implementation/phase-7-br-analysis.md

  mv /home/user/btznstn/PHASE-7-TEST-MATRIX.md \
     /home/user/btznstn/docs/implementation/phase-7-test-matrix.md
  ```

- [ ] **Move Phase 8 file:**
  ```bash
  mv /home/user/btznstn/PHASE-8-BR-ANALYSIS.md \
     /home/user/btznstn/docs/implementation/phase-8-br-analysis.md
  ```

- [ ] **Update `/docs/implementation/CLAUDE.md`:**
  - [ ] Add references to new supplementary files
  - [ ] Update navigation guide

**Estimated Time:** 15 minutes

#### Create Missing CLAUDE.md
- [ ] **Create `/docs/deployment/CLAUDE.md`:**
  - [ ] Guide for Fly.io setup
  - [ ] Guide for Resend setup
  - [ ] Environment variables documentation
  - [ ] Deployment checklist
  - [ ] Production readiness criteria

**Estimated Time:** 30 minutes

---

## 🟡 Medium Priority (Next 2 Weeks)

### Increment 2: Backend Business Logic

#### Phase 3: Approval Flow

**US-3.1: Approve Endpoint**
- [ ] Read specification: `/docs/implementation/phase-3-approval-flow.md`
- [ ] Read BR-024: First-action-wins (SELECT FOR UPDATE)
- [ ] Read BR-015: Self-approval
- [ ] Write tests (13-15 estimated)
- [ ] Implement POST /api/v1/bookings/{id}/approve
- [ ] Implement SELECT FOR UPDATE for concurrency
- [ ] Implement self-approval detection
- [ ] Verify idempotency (BR-010)

**US-3.2: Deny Endpoint**
- [ ] Read specification
- [ ] Read BR-004: Denial handling (comment required, non-blocking)
- [ ] Read BR-020: Link detection in comment
- [ ] Write tests (15-18 estimated)
- [ ] Implement POST /api/v1/bookings/{id}/deny
- [ ] Implement comment validation
- [ ] Implement SELECT FOR UPDATE
- [ ] Verify dates freed immediately

**US-3.3: Reopen from Denied**
- [ ] Read specification
- [ ] Read BR-018: Reopen guard (no conflicts allowed)
- [ ] Write tests
- [ ] Implement reopen logic
- [ ] Implement conflict check on reopen
- [ ] Reset approvals to NoResponse

**Estimated Total:** 2-3 days

---

#### Phase 4: Email Integration

**US-4.1: Resend Integration**
- [ ] Set up Resend account
- [ ] Get API key
- [ ] Configure environment variable
- [ ] Test email sending

**US-4.2: Email Templates (11 templates)**
- [ ] Read `/docs/specification/notifications.md`
- [ ] Implement all 11 German email templates (exact copy from spec)
- [ ] Test each template with sample data
- [ ] Verify German copy matches exactly

**US-4.3: Email Retry Logic (BR-022)**
- [ ] Implement 3-attempt retry with exponential backoff
- [ ] Log failed emails with correlation ID
- [ ] Test retry behavior

**US-4.4: Weekly Digest (BR-009)**
- [ ] Implement weekly digest query (old NoResponse items)
- [ ] Schedule job (Sunday 09:00 Europe/Berlin)
- [ ] Test digest generation

**Estimated Total:** 2-3 days

---

### Project Management Setup

#### Create Increment Files
- [ ] **Create `increment-01.md`:**
  - [ ] List all Phase 0, 1, 2 user stories
  - [ ] Mark Phase 0, 1 as ✅ Complete
  - [ ] Mark Phase 2 as 🔄 In Progress (detail each US)
  - [ ] Add definition of done checklist
  - [ ] Link to specifications

- [ ] **Create `increment-02.md`:**
  - [ ] List all Phase 3, 4 user stories
  - [ ] Mark as ⏸️ Pending
  - [ ] Add definition of done checklist
  - [ ] Link to specifications

- [ ] **Create `increment-03.md`:** (Phases 5-6)
- [ ] **Create `increment-04.md`:** (Phase 7)
- [ ] **Create `increment-05.md`:** (Phase 8)

**Estimated Time:** 1-2 hours

---

## 🟢 Low Priority (Future)

### Phase 5: Web Calendar (After Playwright)
- [ ] Implement month view component
- [ ] Implement year view component
- [ ] Implement booking detail modal
- [ ] Write 52 E2E tests

### Phase 6: Web Booking (After Phase 5)
- [ ] Implement create booking form
- [ ] Implement date picker
- [ ] Implement edit booking form
- [ ] Write 44 E2E tests

### Phase 7: Approver Interface (After Phases 3-6)
- [ ] Implement outstanding tab
- [ ] Implement history tab
- [ ] Implement approve/deny actions
- [ ] Write 40 E2E tests

### Phase 8: Polish & Production (After All Phases)
- [ ] Performance optimization
- [ ] Accessibility audit
- [ ] Production deployment
- [ ] Write 140 tests

---

## 📝 Documentation TODOs

### High Priority
- [ ] Update main `/CLAUDE.md` to reference `/project/` first
- [ ] Create deployment CLAUDE.md
- [ ] Move 8 phase analysis files to correct location

### Medium Priority
- [ ] Review all CLAUDE.md files for consistency
- [ ] Ensure all German copy centralized
- [ ] Verify all BR cross-references work

### Low Priority
- [ ] Add diagrams (state machine, architecture)
- [ ] Create video walkthrough (optional)
- [ ] Add API documentation with Swagger/OpenAPI

---

## 🐛 Bugs / Issues

**None currently tracked**

*When bugs are found:*
- Add to this section
- Reference file location and error
- Link to specification if behavior unclear
- Mark priority (🔴 Critical, 🟠 High, 🟡 Medium, 🟢 Low)

---

## 💡 Ideas / Enhancements

### Project Management
- [ ] Add GitHub Projects kanban board (optional)
- [ ] Set up CI/CD pipeline for automated testing
- [ ] Add coverage reporting (Codecov or similar)
- [ ] Add pre-commit hooks (run tests, linting before commit)

### Development Tools
- [ ] Docker Compose for local development
- [ ] Make commands for common tasks
- [ ] VSCode recommended extensions file

### Documentation
- [ ] Interactive API documentation (Swagger UI)
- [ ] Component storybook (Storybook.js)
- [ ] Architecture diagrams (Mermaid or similar)

---

## 📊 Quick Metrics

**Completed:**
- ✅ Phases 0, 1: 100%
- 🔄 Phase 2: 70% (3/5 user stories)

**In Progress:**
- US-2.3, US-2.4, US-2.5 (Phase 2)

**Next Up:**
- Phase 3: Approval Flow
- Phase 4: Email Integration

**Blockers:**
- 🚫 Playwright not configured (blocks Phases 5-7)

---

## 🚀 This Week's Goal

**Complete Increment 1:**
1. ✅ Finish US-2.3 (Edit Booking)
2. ✅ Finish US-2.4 (Cancel Booking)
3. ✅ Finish US-2.5 (Calendar View)
4. ✅ All Phase 2 tests passing
5. ✅ Playwright configured (unblock frontend)
6. ✅ Documentation organized

**Success Criteria:**
- All backend CRUD endpoints working
- All tests passing (≥80% coverage)
- Frontend can start immediately next week

---

**For strategic view, see `/project/STATUS.md`**
**For tactical view, see `/project/ROADMAP.md`**
**For detailed tracking, see `/project/increments/increment-XX.md`**
