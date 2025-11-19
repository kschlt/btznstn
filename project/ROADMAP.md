# Project Roadmap

**Last Updated:** 2025-11-19

---

## 🎯 Roadmap Overview

This roadmap maps **Phases → Increments** and shows dependencies, order, and current status.

**Total Increments:** 4
**Current Increment:** 2 (Backend COMPLETE)
**Completion:** ~37.5% overall (Phases 0-2 complete = 3/8 phases)

**📋 Backend-First Approach:**
This roadmap follows a backend-first strategy: complete ALL backend functionality (Phases 3-4) before starting ANY frontend work (Phases 5-7). This enables comprehensive backend testing, clear API contracts, and deferred Playwright configuration until frontend work begins.

---

## 📦 Increment Structure

### Increment Dependency Chain

```
Increment 1: Backend Core (Phases 0-2) ✅ COMPLETE
    ↓
Increment 2: Backend COMPLETE (Phases 3-4) ← 100% backend done
    ↓
Increment 3: Frontend COMPLETE (Phases 5-6-7) ← 100% frontend done
    ↓
Increment 4: Production Ready (Phase 8)
```

**Key Dependencies:**
- Increment 2 requires Increment 1 (booking API endpoints exist)
- Increment 3 requires BOTH Increment 1 (API endpoints) AND Increment 2 (approval backend) AND Playwright configuration
- Increment 4 requires ALL previous increments complete (all features implemented)

**Rationale for Backend-First:**
- Complete, testable backend before frontend work begins
- No frontend distractions while building complex approval logic
- API contract finalized before frontend consumes it
- Playwright configuration deferred until actually needed
- Clearer milestones (backend done = 50% complete)

---

## 📋 Increment Details

### ✅ Increment 0: Project Setup (If Exists)

**Status:** Assumed complete
**Phases:** N/A (pre-phase work)
**Deliverables:**
- Repository structure
- Initial documentation
- CLAUDE.md instructions
- Specifications complete

**Completion:** 100% (assumed)

---

### 🔄 Increment 1: Backend Core

**Status:** 🔄 **In Progress** (70% complete)
**Phases:** 0, 1, 2
**Started:** 2025-11 (estimated)
**Target:** TBD

#### Phases Included

**Phase 0: Foundation**
- ✅ Status: Complete
- User Stories: 5 (scaffold, database, tests, linting, type checking)
- Deliverables: FastAPI app, PostgreSQL, pytest, mypy, ruff

**Phase 1: Data Layer**
- ✅ Status: Complete (9 fixes applied)
- User Stories: 3 (models, repositories, migrations)
- Deliverables: Booking/Approval/TimelineEvent models, test factories
- Learnings: String constraints, indexes, test utilities

**Phase 2: Booking API**
- 🔄 Status: In Progress (70%)
- User Stories: 5 (create, get, edit, cancel, calendar)
- Current: 3/5 done (US-2.1, US-2.2 complete; US-2.3, US-2.4, US-2.5 pending)
- Deliverables: Booking CRUD endpoints, conflict detection, German errors

#### Success Criteria

- [ ] All Phase 0, 1, 2 user stories complete
- [ ] All backend tests passing (≥80% coverage)
- [ ] Type checking passes (mypy)
- [ ] Linting passes (ruff)
- [ ] Database migrations work
- [ ] German error messages match spec

#### Estimated Effort

- **Remaining:** 1-2 days (3 user stories)
- **Total Increment:** ~5 days (originally)

#### File Reference

→ `/project/increments/increment-01.md` (detailed tracking)

---

### ⏸️ Increment 2: Backend COMPLETE

**Status:** ⏸️ **Pending** (Next Up)
**Phases:** 3, 4
**Dependencies:** Increment 1 complete ✅
**Target Start:** Now (Increment 1 complete)
**Estimated Effort:** ~5-6 days

**🎯 Goal:** Complete ALL backend functionality before starting ANY frontend work.

#### Phases Included

**Phase 3: Approval Flow**
- ⏸️ Status: Pending
- User Stories: 3 (approve, deny, reopen)
- Deliverables:
  - Approve endpoint (POST /api/v1/bookings/{id}/approve)
  - Deny endpoint (POST /api/v1/bookings/{id}/deny)
  - Reopen endpoint (POST /api/v1/bookings/{id}/reopen)
  - BR-024 implementation (SELECT FOR UPDATE for concurrency)
  - BR-015 implementation (self-approval)
- Estimated Tests: ~36-43
- Estimated Effort: 2-3 days

**Phase 4: Email Integration**
- ⏸️ Status: Pending
- User Stories: 4 (Resend integration, templates, retries, weekly digest)
- Deliverables:
  - Resend API integration
  - 11 German email templates (exact copy from specifications)
  - BR-022 retry logic (3 attempts, exponential backoff)
  - Weekly digest job (BR-009)
- Estimated Tests: ~47-60
- Estimated Effort: 2-3 days

#### Success Criteria

- [ ] All approval endpoints working
- [ ] BR-024 concurrency handled (SELECT FOR UPDATE)
- [ ] All email templates implemented (exact German copy)
- [ ] Email retry logic working (3 attempts)
- [ ] Weekly digest scheduled
- [ ] **Backend is 100% complete** (all API endpoints done)
- [ ] Code coverage ≥80%
- [ ] Type checking passes (mypy)
- [ ] Linting passes (ruff)

#### Estimated Effort

- **Phase 3:** 2-3 days
- **Phase 4:** 2-3 days
- **Total Increment:** ~5-6 days

#### File Reference

→ `/project/increments/increment-02.md`

---

### 🚫 Increment 3: Frontend COMPLETE

**Status:** 🚫 **Blocked** (Playwright not configured, Increment 2 pending)
**Phases:** 5, 6, 7
**Dependencies:** Increments 1-2 complete + Playwright configured
**Blockers:**
  1. Increment 2 must finish first (approval backend needed for Phase 7)
  2. Playwright not set up in `/web/`
**Estimated Effort:** ~10-11 days

**🎯 Goal:** Complete ALL frontend functionality in one increment.

#### Phases Included

**Phase 5: Web Calendar**
- 🚫 Status: Blocked (Playwright + Increment 1)
- User Stories: 3 (month view, year view, booking details)
- Deliverables:
  - Calendar component (month/year views)
  - Booking detail modal
  - Month/year navigation
  - Mobile-responsive (375px)
- Estimated Tests: ~52-61 E2E (Playwright)
- Estimated Effort: 3-4 days

**Phase 6: Web Booking**
- 🚫 Status: Blocked (Phase 5 + Playwright)
- User Stories: 3 (date picker, create form, edit form)
- Deliverables:
  - Create booking form (Zod validation, React Hook Form)
  - Date picker with conflict visualization
  - Edit booking form with approval reset detection (BR-005)
  - All German copy from specifications
- Estimated Tests: ~42-46 E2E (Playwright)
- Estimated Effort: 3-4 days

**Phase 7: Approver Interface**
- 🚫 Status: Blocked (Phases 5-6 + Increment 2)
- User Stories: 3 (overview, approve, deny)
- Deliverables:
  - Approver overview (Outstanding + History tabs)
  - Approve action (one-click from email or overview)
  - Deny action with comment (comment validation, BR-020 link blocking)
  - BR-023 query correctness (Outstanding vs History filtering)
  - BR-024 first-action-wins handling
- Estimated Tests: ~37-42 E2E (Playwright)
- Estimated Effort: 2-3 days

#### Success Criteria

- [ ] Playwright configured (iPhone 8 viewport 375×667px)
- [ ] All calendar views implemented
- [ ] All forms implemented with validation
- [ ] Approver interface complete
- [ ] All Playwright tests passing (~131-149 total)
- [ ] Mobile tested (375px viewport)
- [ ] German copy matches spec exactly
- [ ] **Frontend is 100% complete** (all pages done)
- [ ] Type checking passes (tsc)
- [ ] Linting passes (eslint)

#### Blockers to Resolve

1. **Wait for Increment 2 to complete** (approval backend needed for Phase 7)
2. **Install Playwright:**
   ```bash
   cd web
   npm install -D @playwright/test
   npx playwright install
   ```

3. **Create `playwright.config.ts`:**
   - Configure iPhone 8 viewport (375×667px)
   - Set up test directories
   - Configure browsers (Chromium, Firefox, WebKit)

**Estimated Time to Unblock:** Increment 2 completion + 1 hour (Playwright setup)

#### Estimated Effort

- **Phase 5:** 3-4 days
- **Phase 6:** 3-4 days
- **Phase 7:** 2-3 days
- **Playwright setup:** 1 hour
- **Total Increment:** ~10-11 days

#### File Reference

→ `/project/increments/increment-03.md`

---

### 🚫 Increment 4: Production Ready

**Status:** 🚫 **Blocked** (Depends on all previous increments)
**Phases:** 8
**Dependencies:** Increments 1-3 complete (all features implemented)

#### Phases Included

**Phase 8: Polish & Production**
- 🚫 Status: Blocked
- User Stories: 3 (performance, accessibility, deployment)
- Deliverables:
  - **US-8.1:** Performance optimization (Lighthouse ≥90, TTI <3s)
  - **US-8.2:** Accessibility (WCAG AA, axe-core 0 violations)
  - **US-8.3:** Production deployment (Fly.io + Vercel)
  - Rate limiting enforced (BR-012)
  - Email retries working (BR-022)
  - Background jobs scheduled (BR-028 auto-cleanup, BR-013 purge)
- Estimated Tests: ~140 (performance, accessibility, deployment)

#### Success Criteria

- [ ] Lighthouse Performance ≥90
- [ ] Lighthouse Accessibility = 100
- [ ] All WCAG AA criteria met
- [ ] Backend deployed to Fly.io (Frankfurt)
- [ ] Frontend deployed to Vercel
- [ ] Rate limiting enforced
- [ ] Background jobs scheduled
- [ ] Monitoring configured

#### Estimated Effort

- **US-8.1:** 1 day (performance)
- **US-8.2:** 1 day (accessibility)
- **US-8.3:** 1 day (deployment)
- **Total Increment:** ~3 days

#### File Reference

→ `/project/increments/increment-04.md`

---

## 🎯 Milestones

### Milestone 1: Backend Complete

**Target:** Increments 1-2 done
**Phases:** 0, 1, 2, 3, 4
**Estimated Completion:** TBD
**Deliverables:**
- All backend endpoints working (booking + approval API)
- All backend tests passing (≥80% coverage)
- Email integration complete (Resend)
- German email templates verified (11 templates)
- Background jobs scheduled (weekly digest)

**Progress:** 🔄 37.5% (Increment 1 ✅ complete, Increment 2 pending)

**Benefits of Backend-First:**
- Complete, testable API before frontend work
- API contract finalized
- Email templates tested without frontend
- No context switching between backend/frontend

---

### Milestone 2: Frontend Complete

**Target:** Increment 3 done
**Phases:** 5, 6, 7
**Estimated Completion:** TBD (after Milestone 1 + Playwright setup)
**Deliverables:**
- All frontend pages working (calendar, forms, approver)
- All E2E tests passing (Playwright)
- Mobile tested (375px viewport)
- German copy verified (exact match to specs)
- Accessibility basics implemented

**Progress:** ⏸️ 0% (Blocked on Milestone 1 + Playwright)

**Benefits of Frontend-Complete:**
- All UI work done in one focused effort
- Consistent design patterns
- No switching between calendar/forms/approver
- Playwright configured once, used throughout

---

### Milestone 3: Production Launch

**Target:** Increment 4 done
**Phases:** 8
**Estimated Completion:** TBD (after Milestones 1-2)
**Deliverables:**
- Performance optimized (Lighthouse ≥90)
- Accessibility compliant (WCAG AA)
- Deployed to production (Fly.io + Vercel)
- Monitoring configured
- Rate limiting enforced
- Background jobs verified

**Progress:** ⏸️ 0% (Blocked on all previous)

---

## 📊 Summary View

| Increment | Phases | Status | Progress | Blockers | Estimated Days |
|-----------|--------|--------|----------|----------|----------------|
| **1** | 0-2 | ✅ Complete | 100% | None | 0 (done) |
| **2** | 3-4 | ⏸️ Pending | 0% | None (ready!) | 5-6 days |
| **3** | 5-6-7 | 🚫 Blocked | 0% | Increment 2 + Playwright | 10-11 days |
| **4** | 8 | 🚫 Blocked | 0% | Increments 1-3 | 3-4 days |

**Total Remaining Effort:** 18-21 days (with AI assistance) or 25-30 days (single developer)

**Backend-First Benefits:**
- Clear separation: Backend done = 50% complete
- No frontend distractions during complex approval logic
- API contract finalized before UI consumes it
- Playwright setup deferred until actually needed

---

## 🔄 Increment Planning Notes

### Why This Grouping? (Backend-First Approach)

**Increment 1 (Phases 0-2): Backend Core** ✅
- Foundation for everything else
- Can be deployed independently
- Backend CRUD complete
- Status: **COMPLETE**

**Increment 2 (Phases 3-4): Backend COMPLETE**
- Adds approval logic to backend
- Completes ALL backend functionality
- Still deployable independently (can test with curl/Postman)
- Email integration included (can be tested without frontend)
- **Key benefit:** 100% backend done before ANY frontend work

**Increment 3 (Phases 5-6-7): Frontend COMPLETE**
- Requires backend fully functional (Increments 1-2)
- All frontend work grouped together (calendar + forms + approver)
- Playwright configured once, used throughout
- Consistent design patterns across all pages
- **Key benefit:** 100% frontend done in one focused effort

**Increment 4 (Phase 8): Production Ready**
- Polish requires all features complete
- Production deployment requires all previous increments
- Standalone phase = standalone increment
- **Key benefit:** No performance/accessibility rework during development

### Why Backend-First?

**Advantages:**
1. **Testability:** Backend fully testable without frontend (pytest only)
2. **API Contract:** Frontend knows exactly what endpoints exist
3. **No Context Switching:** Focus on backend logic, then focus on UI
4. **Defer Playwright:** Setup frontend testing only when needed
5. **Clear Milestones:** Backend done = 50% complete (easy to measure)
6. **Email Testing:** Email templates tested without frontend
7. **Deployment Flexibility:** Backend can deploy to production first

**Trade-offs:**
1. **Delayed Visual Feedback:** No UI until Increment 3
2. **Potential Backend Changes:** Frontend work might reveal API gaps
3. **Frontend Specs Need Work:** UI mockups not as detailed yet

**Decision:** Backend-first is APPROVED based on user preference and technical benefits.

### Flexibility

Increments can be adjusted based on:
- **Dependency changes:** If frontend specs solidify, could parallelize some work
- **Resource availability:** Multiple developers could work on backend + frontend in parallel
- **Priority shifts:** If production urgency, could skip some polish

**Current plan assumes single developer or AI agent working sequentially.**

---

## 📅 Timeline Estimate

### Conservative Estimate (Single Developer)

- **Increment 1:** ✅ Complete (0 days remaining)
- **Increment 2:** 5-6 days (Phases 3-4)
- **Increment 3:** 10-11 days (Phases 5-6-7 + 1 hour Playwright)
- **Increment 4:** 3-4 days (Phase 8)

**Total:** ~18-21 days remaining (3.5-4 weeks at 5 days/week)

### Optimistic Estimate (AI-Assisted)

- **Increment 1:** ✅ Complete (0 days remaining)
- **Increment 2:** 3-4 days (Phases 3-4)
- **Increment 3:** 8-9 days (Phases 5-6-7 + 1 hour Playwright)
- **Increment 4:** 2-3 days (Phase 8)

**Total:** ~13-16 days remaining (2.5-3 weeks at 5 days/week)

---

## 📝 Next Steps (Backend-First)

**Immediate (Now - Week 1):**
1. ✅ Increment 1 complete (Phases 0-2 done)
2. **START Increment 2** (Phases 3-4)
3. Implement approval endpoints (US-3.1, 3.2, 3.3)
4. Set up Resend integration
5. Implement 11 German email templates

**Short-Term (Week 2):**
6. Complete Increment 2 (backend 100% done)
7. Test all email templates
8. Verify weekly digest job
9. **Milestone 1 complete:** Backend fully functional

**Medium-Term (Weeks 3-4):**
10. Configure Playwright (unblock Increment 3)
11. **START Increment 3** (Phases 5-6-7)
12. Build calendar views (month, year, details)
13. Build booking forms (create, edit)
14. Build approver interface (overview, approve, deny)
15. **Milestone 2 complete:** Frontend fully functional

**Long-Term (Week 5+):**
16. **START Increment 4** (Phase 8)
17. Optimize performance (Lighthouse ≥90)
18. Audit accessibility (WCAG AA)
19. Deploy to production (Fly.io + Vercel)
20. **Milestone 3 complete:** Production launch 🚀

**Key Difference:**
Backend-first means **NO frontend work** until Increment 2 is done. This allows focused effort on complex approval logic without UI distractions.

---

**For detailed user story tracking, see increment files in `/project/increments/`**
