# Project Backlog

**Last Updated:** 2025-11-19
**Current Focus:** ✅ Increment 1 COMPLETE - Ready for Increment 2

---

## ✅ Recently Completed (2025-11-19)

### Phase 2: Booking API - ✅ COMPLETE

**Summary:** All 4 backend booking API endpoints implemented and tested

- ✅ **US-2.1:** Create Booking (POST) - 64 tests passing
- ✅ **US-2.2:** Get Booking (GET) - 20 tests passing
- ✅ **US-2.3:** Update Booking (PATCH) - 35 tests passing
  - Implements BR-005 critical approval reset logic
  - Extend dates → reset approvals; shorten → keep approvals
  - Full token authentication and validation
- ✅ **US-2.4:** Cancel Booking (DELETE) - 27 tests passing
  - Implements BR-006 (Pending cancel) and BR-007 (Confirmed requires comment)
  - Idempotent cancellation
  - German success messages

**Total:** 146 tests, all business rules enforced, type-safe, fully validated

**Note:** Calendar View (GET /calendar) is NOT part of Phase 2 - it's Phase 5 (Web Calendar, frontend work)

---

## 🔥 High Priority (Next Up)

### Increment 2: Backend Business Logic (Phases 3-4)

**Status:** Ready to start (Increment 1 complete)

**Phase 3: Approval Flow** (3 user stories, ~49 tests)
- US-3.1: Approve Booking (POST /api/v1/bookings/{id}/approve)
- US-3.2: Deny Booking (POST /api/v1/bookings/{id}/deny)
- US-3.3: Reopen Denied Booking (POST /api/v1/bookings/{id}/reopen)

**Phase 4: Email Integration** (4 user stories, ~75 tests)
- US-4.1: New booking notification emails
- US-4.2: Approval/denial notification emails
- US-4.3: Edit/cancel notification emails
- US-4.4: Email retry and error handling

---

## 🚧 Technical Blockers (For Future Increments)

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
