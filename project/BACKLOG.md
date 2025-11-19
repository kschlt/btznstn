# Project Backlog

**Last Updated:** 2025-11-19
**Current Focus:** Increment 2 (Backend COMPLETE) - Phases 3-4
**Strategy:** 🎯 **Backend-First** - Complete ALL backend (Phases 3-4) before ANY frontend (Phases 5-7)

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

## 🔥 High Priority (Immediate Focus)

### 🎯 Increment 2: Backend COMPLETE (Phases 3-4) ← **START NOW**

**Goal:** Complete ALL backend functionality before ANY frontend work

**Status:** ✅ Ready to start (Increment 1 complete, no blockers)

**Estimated Effort:** 5-6 days (with AI assistance)

---

#### Phase 3: Approval Flow (3 user stories, ~36-43 tests)

**Deliverables:**
- US-3.1: Approve Booking (POST /api/v1/bookings/{id}/approve)
  - BR-024: SELECT FOR UPDATE for concurrency
  - BR-015: Self-approval detection
  - BR-010: Idempotency
- US-3.2: Deny Booking (POST /api/v1/bookings/{id}/deny)
  - BR-004: Denial handling (comment required, frees dates immediately)
  - BR-020: Link detection in comment
  - BR-024: SELECT FOR UPDATE
- US-3.3: Reopen Denied Booking (POST /api/v1/bookings/{id}/reopen)
  - BR-018: Reopen guard (no conflicts allowed)
  - BR-005: Reset approvals to NoResponse

**Estimated:** 2-3 days

---

#### Phase 4: Email Integration (4 user stories, ~47-60 tests)

**Deliverables:**
- US-4.1: Resend Integration (5-8 tests)
  - Set up Resend account and API key
  - Test email sending
- US-4.2: Email Templates (20-25 tests)
  - 11 German email templates (exact copy from spec)
  - Dynamic placeholders ({{Vorname}}, {{StartDatum}}, etc.)
  - Informal "du" tone throughout
- US-4.3: Email Retry Logic (10-12 tests)
  - BR-022: 3 attempts, exponential backoff (2s, 4s, 8s)
  - Log failures with correlation ID
- US-4.4: Weekly Digest (12-15 tests)
  - BR-009: Sunday 09:00 Europe/Berlin
  - Old NoResponse items for each approver

**Estimated:** 2-3 days

---

**After Increment 2:** Backend is 100% complete, ready for frontend work

---

## 🚧 Technical Blockers (Deferred Until Backend Complete)

### Configure Playwright (After Increment 2)

**Status:** Deferred until backend 100% complete

**Rationale:** Backend-first strategy - no frontend work until Phases 3-4 done

**When to do this:** After Increment 2 complete, before starting Increment 3

**Estimated Time:** 1 hour

**Steps:**
- [ ] Navigate to frontend: `cd /home/user/btznstn/web`
- [ ] Install Playwright:
  ```bash
  npm install -D @playwright/test
  npx playwright install
  ```
- [ ] Create `playwright.config.ts`:
  - [ ] Configure iPhone 8 viewport (375×667px)
  - [ ] Set up test directories (`/tests/e2e/`)
  - [ ] Configure browsers (Chromium, Firefox, WebKit)
  - [ ] Set up screenshots on failure, 2 retries
- [ ] Create example test: `/web/tests/e2e/example.spec.ts`
- [ ] Run test: `npx playwright test`
- [ ] Verify test passes

**Blocks:** Increment 3 (all frontend work - Phases 5-6-7)

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

## 🟡 Medium Priority (After Backend Complete)

### Increment 3: Frontend COMPLETE (Phases 5-6-7)

**Status:** Blocked - waiting for Increment 2 to finish

**Dependencies:**
1. Increment 2 complete (backend 100% done)
2. Playwright configured (1 hour setup)

**Estimated Effort:** 10-11 days

---

#### Phase 5: Web Calendar (3 user stories, ~52-61 E2E tests)
- [ ] Implement month view component
- [ ] Implement year view component
- [ ] Implement booking detail modal
- [ ] Write Playwright E2E tests

**Estimated:** 3-4 days

---

#### Phase 6: Web Booking (3 user stories, ~42-46 E2E tests)
- [ ] Implement date picker component
- [ ] Implement create booking form
- [ ] Implement edit booking form (BR-005 approval reset detection)
- [ ] Write Playwright E2E tests

**Estimated:** 3-4 days

---

#### Phase 7: Approver Interface (3 user stories, ~37-42 E2E tests)
- [ ] Implement approver overview (Outstanding + History tabs)
- [ ] Implement approve action (one-click)
- [ ] Implement deny action with comment (BR-020 link validation)
- [ ] Write Playwright E2E tests

**Estimated:** 2-3 days

---

**After Increment 3:** Frontend is 100% complete (all pages done)

---

## 🟢 Low Priority (Final Polish)

### Increment 4: Production Ready (Phase 8)

**Status:** Blocked - waiting for Increments 1-3 to finish

**Dependencies:** All features implemented (Phases 0-7 complete)

**Estimated Effort:** 3-4 days

---

#### Phase 8: Polish & Production (3 user stories, ~140 tests)
- [ ] Performance optimization (Lighthouse ≥90)
- [ ] Accessibility audit (WCAG AA, axe-core 0 violations)
- [ ] Production deployment (Fly.io + Vercel)
- [ ] Rate limiting (BR-012)
- [ ] Background jobs (BR-028, BR-013, BR-009)
- [ ] Monitoring and error logging

**Estimated:** 3-4 days

---

**After Increment 4:** Production launch 🚀

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

## 📊 Quick Metrics (Backend-First)

**Completed:**
- ✅ Phases 0, 1, 2: 100% (Increment 1 complete)
- ✅ Increment 1: Backend Core (4/4 user stories, 146 tests)

**In Progress:**
- Increment 2: Backend COMPLETE (Phases 3-4)
  - Phase 3: 0/3 user stories
  - Phase 4: 0/4 user stories

**Next Up:**
- US-3.1: Approve Booking
- US-3.2: Deny Booking
- US-3.3: Reopen Denied Booking

**Blockers:**
- 🟢 None! Ready to start Increment 2
- 🟠 Playwright deferred until backend complete

**Backend-First Progress:**
- Backend: 37.5% complete (Phases 0-2 of 0-4)
- Frontend: 0% (deferred until backend done)

---

## 🚀 Current Focus (Week 1-2)

**Goal: Complete Increment 2 (Backend 100% Complete)**

**Week 1: Phase 3 (Approval Flow)**
1. Implement US-3.1 (Approve endpoint with BR-024 concurrency)
2. Implement US-3.2 (Deny endpoint with BR-004/BR-020)
3. Implement US-3.3 (Reopen endpoint with BR-018)
4. All ~36-43 tests passing
5. SELECT FOR UPDATE working (concurrency safety)

**Week 2: Phase 4 (Email Integration)**
6. Set up Resend integration
7. Implement 11 German email templates
8. Implement email retry logic (BR-022)
9. Schedule weekly digest job (BR-009)
10. All ~47-60 tests passing

**Success Criteria:**
- **Backend is 100% complete** (all API endpoints done)
- All backend tests passing (≥80% coverage)
- Email integration working (Resend)
- German email templates verified
- **Milestone 1 achieved:** Backend fully functional

---

**For strategic view, see `/project/STATUS.md`**
**For tactical view, see `/project/ROADMAP.md`**
**For detailed tracking, see `/project/increments/increment-XX.md`**
