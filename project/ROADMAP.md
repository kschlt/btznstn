# Project Roadmap

**Last Updated:** 2025-11-19

---

## 🎯 Roadmap Overview

This roadmap maps **Phases → Increments** and shows dependencies, order, and current status.

**Total Increments:** 5
**Current Increment:** 1 (Backend Core)
**Completion:** ~25% overall (Increment 1 is 70% done)

---

## 📦 Increment Structure

### Increment Dependency Chain

```
Increment 1: Backend Core (Phases 0-2)
    ↓
Increment 2: Backend Business Logic (Phases 3-4)
    ↓
    ↓──────────────────────┐
    ↓                      ↓
Increment 3: Frontend Core (Phases 5-6)
    ↓
Increment 4: Frontend Approver (Phase 7)
    ↓
Increment 5: Production (Phase 8)
```

**Key Dependencies:**
- Increment 3 requires both Increment 1 (API endpoints) AND Playwright configuration
- Increment 4 requires both Increment 2 (approval backend) AND Increment 3 (frontend core)
- Increment 5 requires ALL previous increments complete

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

### ⏸️ Increment 2: Backend Business Logic

**Status:** ⏸️ **Pending**
**Phases:** 3, 4
**Dependencies:** Increment 1 complete
**Target Start:** After Phase 2 done

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
- Estimated Tests: ~49

**Phase 4: Email Integration**
- ⏸️ Status: Pending
- User Stories: 4 (Resend integration, templates, retries, weekly digest)
- Deliverables:
  - Resend API integration
  - 11 German email templates (from specifications)
  - BR-022 retry logic (3 attempts, exponential backoff)
  - Weekly digest (BR-009)
- Estimated Tests: ~75

#### Success Criteria

- [ ] All approval endpoints working
- [ ] BR-024 concurrency handled (SELECT FOR UPDATE)
- [ ] All email templates implemented (exact German copy)
- [ ] Email retry logic working (3 attempts)
- [ ] Weekly digest scheduled

#### Estimated Effort

- **Phase 3:** 2-3 days
- **Phase 4:** 2-3 days
- **Total Increment:** ~5 days

#### File Reference

→ `/project/increments/increment-02.md` (to be created)

---

### 🚫 Increment 3: Frontend Core

**Status:** 🚫 **Blocked** (Playwright not configured)
**Phases:** 5, 6
**Dependencies:** Increment 1 complete + Playwright configured
**Blockers:** Playwright not set up in `/web/`

#### Phases Included

**Phase 5: Web Calendar**
- 🚫 Status: Blocked
- User Stories: 3 (month view, year view, booking details)
- Deliverables:
  - Calendar component (month/year views)
  - Booking detail modal
  - Month/year navigation
  - Mobile-responsive (375px)
- Estimated Tests: ~52 E2E (Playwright)

**Phase 6: Web Booking**
- 🚫 Status: Blocked (depends on Phase 5)
- User Stories: 3 (create form, date picker, edit form)
- Deliverables:
  - Create booking form (Zod validation, React Hook Form)
  - Date picker with conflict visualization
  - Edit booking form with approval reset detection (BR-005)
  - All German copy from specifications
- Estimated Tests: ~44 E2E (Playwright)

#### Success Criteria

- [ ] Playwright configured (iPhone 8 viewport 375×667px)
- [ ] All calendar views implemented
- [ ] All forms implemented with validation
- [ ] All Playwright tests passing
- [ ] Mobile tested (375px viewport)
- [ ] German copy matches spec exactly

#### Estimated Effort

- **Phase 5:** 3-4 days
- **Phase 6:** 3-4 days
- **Total Increment:** ~7 days

#### Blockers to Resolve

1. **Install Playwright:**
   ```bash
   cd web
   npm install -D @playwright/test
   npx playwright install
   ```

2. **Create `playwright.config.ts`:**
   - Configure iPhone 8 viewport (375×667px)
   - Set up test directories
   - Configure browsers (Chromium, Firefox, WebKit)

3. **Create test structure:**
   - `/web/tests/e2e/` directory
   - Example test file

**Estimated Time to Unblock:** 1 hour

#### File Reference

→ `/project/increments/increment-03.md` (to be created)

---

### 🚫 Increment 4: Frontend Approver

**Status:** 🚫 **Blocked** (Depends on Increments 2 and 3)
**Phases:** 7
**Dependencies:** Increments 2 (approval backend) + 3 (frontend core) complete

#### Phases Included

**Phase 7: Approver Interface**
- 🚫 Status: Blocked
- User Stories: 3 (overview, approve, deny)
- Deliverables:
  - Approver overview (Outstanding + History tabs)
  - Approve action (one-click from email or overview)
  - Deny action with comment (comment validation, BR-020 link blocking)
  - BR-023 query correctness (Outstanding vs History filtering)
  - BR-024 first-action-wins handling
- Estimated Tests: ~40 E2E (Playwright)

#### Success Criteria

- [ ] Outstanding/History tabs implemented
- [ ] Approve/Deny actions working
- [ ] BR-024 concurrency handled (first-action-wins)
- [ ] Comment validation working (BR-020 link blocking)
- [ ] All Playwright tests passing
- [ ] German copy matches spec

#### Estimated Effort

- **Phase 7:** 2-3 days
- **Total Increment:** ~3 days

#### File Reference

→ `/project/increments/increment-04.md` (to be created)

---

### 🚫 Increment 5: Production Ready

**Status:** 🚫 **Blocked** (Depends on all previous increments)
**Phases:** 8
**Dependencies:** All phases 0-7 complete

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

→ `/project/increments/increment-05.md` (to be created)

---

## 🎯 Milestones

### Milestone 1: Backend Complete

**Target:** Increments 1-2 done
**Phases:** 0, 1, 2, 3, 4
**Estimated Completion:** TBD
**Deliverables:**
- All backend endpoints working
- All backend tests passing
- Email integration complete
- German email templates verified

**Progress:** 🔄 50% (Increment 1 at 70%, Increment 2 at 0%)

---

### Milestone 2: Frontend Complete

**Target:** Increments 3-4 done
**Phases:** 5, 6, 7
**Estimated Completion:** TBD (after Milestone 1 + Playwright setup)
**Deliverables:**
- All frontend pages working
- All E2E tests passing
- Mobile tested (375px)
- German copy verified

**Progress:** ⏸️ 0% (Blocked on Playwright)

---

### Milestone 3: Production Launch

**Target:** Increment 5 done
**Phases:** 8
**Estimated Completion:** TBD (after Milestones 1-2)
**Deliverables:**
- Performance optimized
- Accessibility compliant
- Deployed to production
- Monitoring configured

**Progress:** ⏸️ 0% (Blocked on all previous)

---

## 📊 Summary View

| Increment | Phases | Status | Progress | Blockers | Estimated Days |
|-----------|--------|--------|----------|----------|----------------|
| **1** | 0-2 | 🔄 In Progress | 70% | None | 1-2 remaining |
| **2** | 3-4 | ⏸️ Pending | 0% | Increment 1 | 5 days |
| **3** | 5-6 | 🚫 Blocked | 0% | Playwright | 7 days |
| **4** | 7 | 🚫 Blocked | 0% | Increments 2-3 | 3 days |
| **5** | 8 | 🚫 Blocked | 0% | All previous | 3 days |

**Total Remaining Effort:** 18-20 days (with AI assistance) or 25-30 days (single developer)

---

## 🔄 Increment Planning Notes

### Why This Grouping?

**Increment 1 (Phases 0-2):**
- Foundation for everything else
- Can be deployed independently
- Backend CRUD complete

**Increment 2 (Phases 3-4):**
- Adds business logic to backend
- Still deployable independently
- Completes backend functionality

**Increment 3 (Phases 5-6):**
- Frontend requires backend APIs (Increment 1)
- Calendar and forms are tightly coupled
- Both need same test infrastructure (Playwright)

**Increment 4 (Phase 7):**
- Approver interface needs approval backend (Increment 2)
- Needs frontend core components (Increment 3)
- Standalone phase = standalone increment

**Increment 5 (Phase 8):**
- Polish requires all features complete
- Production requires all previous increments
- Standalone phase = standalone increment

### Flexibility

Increments can be adjusted based on:
- **Dependency changes:** If Increment 3 can start without Increment 2, reorder
- **Resource availability:** If multiple developers, parallelize Increments 2 and 3
- **Priority shifts:** If production urgency, compress Increments 3-4

**Current plan assumes single developer or AI agent working sequentially.**

---

## 📅 Timeline Estimate

### Conservative Estimate (Single Developer)

- **Increment 1:** 2 days remaining
- **Increment 2:** 5 days
- **Increment 3:** 7 days (+ 1 day Playwright setup)
- **Increment 4:** 3 days
- **Increment 5:** 3 days

**Total:** ~21 days (4-5 weeks at 5 days/week)

### Optimistic Estimate (AI-Assisted)

- **Increment 1:** 1 day remaining
- **Increment 2:** 3 days
- **Increment 3:** 5 days (+ 1 hour Playwright setup)
- **Increment 4:** 2 days
- **Increment 5:** 2 days

**Total:** ~13 days (2.5-3 weeks at 5 days/week)

---

## 📝 Next Steps

**Immediate (This Week):**
1. Complete Increment 1 (Phase 2 remaining user stories)
2. Configure Playwright (unblock Increment 3)
3. Organize documentation (move 8 phase files)

**Short-Term (Next 2 Weeks):**
4. Start Increment 2 (Phases 3-4)
5. Complete backend functionality
6. Test email integration

**Medium-Term (Next 4-6 Weeks):**
7. Start Increment 3 (Phases 5-6)
8. Build frontend calendar and forms
9. Start Increment 4 (Phase 7)
10. Build approver interface

**Long-Term (Production):**
11. Start Increment 5 (Phase 8)
12. Optimize performance
13. Audit accessibility
14. Deploy to production

---

**For detailed user story tracking, see increment files in `/project/increments/`**
