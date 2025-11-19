# Increment 5: Production Ready

**Status:** 🚫 **Blocked** (Depends on all previous increments)
**Phases:** 8
**Dependencies:** Increments 1-4 complete (all features implemented)
**Target Start:** After Phases 0-7 complete
**Estimated Effort:** 3-4 days

---

## 📋 Overview

**Goal:** Optimize performance, ensure accessibility compliance, deploy to production.

**Deliverables:**
- Performance optimization (Lighthouse ≥90, TTI <3s)
- Accessibility compliance (WCAG AA, axe-core 0 violations)
- Production deployment (Fly.io + Vercel)
- Rate limiting enforced (BR-012)
- Background jobs scheduled (BR-028 auto-cleanup, BR-013 purge, BR-009 weekly digest)
- Email retry logic verified (BR-022)
- Monitoring and error logging configured

**Success Criteria:**
- Lighthouse Performance ≥90
- Lighthouse Accessibility = 100
- All WCAG AA criteria met
- Backend deployed to Fly.io Frankfurt
- Frontend deployed to Vercel
- Rate limits enforced server-side
- Background jobs running reliably
- All 140 estimated tests passing

---

## 📊 Progress Summary

| Phase | User Stories | Draft | Specified | Implemented | Status |
|-------|--------------|-------|-----------|-------------|--------|
| **8** | 3 | 0 | 3 | 0 | 🚫 Blocked |
| **Total** | **3** | **0** | **3** | **0** | **🚫 0%** |

---

## 🎯 Phase 8: Polish & Production

**Status:** 🚫 **Blocked**
**Dependencies:** All phases 0-7 complete

### User Stories (Dependency-Based Order)

#### US-8.1: Performance Optimization
**Status:** ✅ **Specified**
**Estimated Tests:** 21
**Priority:** P0 (Production readiness)

**Description:** Optimize backend and frontend performance to meet targets.

**Key Business Rules:**
- BR-023: Approver list queries must use eager loading (prevent N+1)

**Performance Targets:**
- Time to Interactive (TTI): <3s
- Lighthouse Performance: ≥90
- First Contentful Paint (FCP): <1.5s
- Largest Contentful Paint (LCP): <2.5s
- Cumulative Layout Shift (CLS): <0.1
- Bundle size (gzipped): <60KB
- API response time (p95): <500ms

**Acceptance Criteria:**

**Backend:**
- [ ] Database queries optimized (eager loading with selectinload)
- [ ] Indexes verified (date range GiST, status, email, last_activity_at DESC)
- [ ] N+1 queries eliminated (count SQL statements in tests)
- [ ] Calendar query uses index (<100ms for 1000+ bookings)
- [ ] Approver outstanding/history queries use selectinload (<200ms)
- [ ] Connection pooling configured (10-20 connections)

**Frontend:**
- [ ] Code splitting implemented (vendor, main, calendar separate bundles)
- [ ] Lazy loading for calendar view, approval forms, details dialogs
- [ ] Bundle size <60KB gzipped
- [ ] Lighthouse Performance ≥90
- [ ] TTI <3s, FCP <1.5s, LCP <2.5s, CLS <0.1
- [ ] Images optimized (if any)
- [ ] Unused CSS/JS removed (tree-shaking)

**Tests:**
- [ ] 5 backend performance tests (query benchmarks, N+1 detection)
- [ ] 4 API response time tests (calendar, approver list, create, get)
- [ ] 3 Lighthouse audits (performance, best practices, SEO)
- [ ] 3 bundle size tests (main, code splitting, lazy loading)
- [ ] 5 Core Web Vitals tests (TTI, FCP, LCP, CLS, load test)
- [ ] 1 concurrent request test (100 concurrent calendar requests)

**Files:**
- Optimization: Update existing backend/frontend files
- Tests: `/api/tests/performance/` (to create), `/web/tests/performance/` (to create)
- Spec: `/docs/implementation/phase-8-polish.md`

---

#### US-8.2: Accessibility (WCAG AA)
**Status:** ✅ **Specified**
**Estimated Tests:** 55
**Priority:** P0 (Legal compliance)

**Description:** Ensure full WCAG AA compliance and accessibility.

**Key Business Rules:**
- BR-011: German UI (all ARIA labels in German)
- BR-016, 019, 020: Validation errors must be accessible

**Accessibility Targets:**
- axe-core: 0 violations
- Lighthouse Accessibility: 100
- WCAG AA compliance (all criteria)
- Keyboard navigation: 100% functional
- Screen reader compatible
- Color contrast: ≥4.5:1 (text), ≥3:1 (UI components)
- Touch targets: ≥44×44pt

**Acceptance Criteria:**

**Automated Testing:**
- [ ] 10 axe-core tests (0 violations on all 10 pages: calendar, forms, approver, details, etc.)
- [ ] Lighthouse Accessibility = 100

**Keyboard Navigation:**
- [ ] 10 keyboard navigation tests (calendar, forms, dialogs)
- [ ] Tab navigates through all interactive elements
- [ ] Shift+Tab reverses navigation
- [ ] Enter/Space activates buttons
- [ ] Esc closes dialogs
- [ ] Arrow keys navigate calendar dates
- [ ] No keyboard traps

**Screen Reader:**
- [ ] 9 screen reader tests (landmarks, labels, errors, content)
- [ ] All buttons have accessible names (ARIA labels in German)
- [ ] All form inputs have associated `<label>` elements
- [ ] Error messages announced via aria-live
- [ ] Status badges have aria-label
- [ ] Affiliation colors not the only indicator (text labels present)

**Color Contrast:**
- [ ] 10 contrast tests (text ≥4.5:1, UI ≥3:1)
- [ ] Affiliation colors (Ingeborg, Cornelia, Angelika) + text ≥4.5:1
- [ ] Focus indicator ≥3:1 contrast

**Mobile Accessibility:**
- [ ] 4 touch target tests (all buttons ≥44×44pt, 8px spacing)
- [ ] Mobile viewport (375px) works
- [ ] No horizontal scrolling

**Focus & Visual:**
- [ ] 5 focus indicator tests (visible, ≥3:1 contrast, ≥2px size, logical order)

**German Text:**
- [ ] 3 German accessibility tests (ARIA labels, error messages, form labels)

**Files:**
- Updates: All frontend components (add ARIA labels, keyboard handlers)
- Tests: `/web/tests/accessibility/` (to create)

---

#### US-8.3: Production Deployment
**Status:** ✅ **Specified**
**Estimated Tests:** 64
**Priority:** P0 (Production launch)

**Description:** Deploy to production (Fly.io + Vercel) with all production features enabled.

**Key Business Rules:**
- BR-010: Tokens never expire (production reliability)
- BR-012: **CRITICAL** - Rate limiting (10 bookings/day per email, 30 requests/hour per IP)
- BR-013: Archive purge (monthly job)
- BR-021: Link recovery cooldown (60 seconds)
- BR-022: Email retries (3 attempts, exponential backoff)
- BR-024, 029: Concurrency safety (SELECT FOR UPDATE, first-wins)
- BR-028: Auto-cleanup of past Pending bookings (daily at 00:01 Europe/Berlin)

**Acceptance Criteria:**

**Infrastructure:**
- [ ] 10 deployment tests (Fly.io health, Vercel build, database, migrations)
- [ ] Backend deployed to Fly.io Frankfurt
- [ ] Frontend deployed to Vercel
- [ ] PostgreSQL 15+ on Fly.io (co-located with backend)
- [ ] Database migrations run on deploy
- [ ] All indexes created
- [ ] Environment variables loaded from Fly.io secrets
- [ ] Health check endpoint (GET /health → 200 OK)

**Rate Limiting:**
- [ ] 8 rate limiting tests (booking submission, IP-based, link recovery, cooldown)
- [ ] 10 bookings/day per email enforced (BR-012)
- [ ] 30 requests/hour per IP enforced
- [ ] 5 link recovery/hour per email enforced
- [ ] 60-second cooldown on link recovery (BR-021)
- [ ] German error messages for rate limits

**Email Reliability:**
- [ ] 6 email tests (delivery, retries, logging, consistency)
- [ ] Resend integration configured
- [ ] 3-attempt retry with exponential backoff (BR-022)
- [ ] Failed emails logged with correlation ID
- [ ] Email content consistent across retries

**Concurrency Safety:**
- [ ] 8 concurrency tests (first-action-wins, first-write-wins, locking)
- [ ] SELECT FOR UPDATE on approve/deny (BR-024)
- [ ] Transaction isolation for create/extend (BR-029)
- [ ] Concurrent approvals handled correctly
- [ ] Concurrent bookings handled correctly

**Background Jobs:**
- [ ] 13 background job tests (auto-cleanup, archive purge, weekly digest)
- [ ] Auto-cleanup runs daily at 00:01 Europe/Berlin (BR-028)
- [ ] Archive purge runs monthly (BR-013)
- [ ] Weekly digest runs Sunday 09:00 Europe/Berlin (BR-009)
- [ ] All jobs log execution (success/failure)

**Idempotency:**
- [ ] 4 idempotency tests (action links, "Schon erledigt" messages)
- [ ] Approve/Deny/Cancel links idempotent (BR-010)

**Smoke Tests:**
- [ ] 5 end-to-end smoke tests (create booking, approve, deny, edit, cancel)

**Security & Stability:**
- [ ] 6 security tests (HTTPS, CORS, headers, timezone, load test, error logging)
- [ ] HTTPS enforced
- [ ] CORS configured
- [ ] Security headers present (HSTS, X-Frame-Options)
- [ ] Timezone handling correct (Europe/Berlin for business logic, UTC in database)
- [ ] Production handles 100 concurrent calendar requests
- [ ] Error logging working (Fly.io logs or Sentry)

**Files:**
- Deployment config: `/api/fly.toml`, `/web/vercel.json` (to create)
- Environment: `.env.production.example` (to create)
- Jobs: `/api/app/jobs/` (auto_cleanup.py, archive_purge.py, weekly_digest.py)
- Tests: `/api/tests/production/` (to create)
- Spec: `/docs/deployment/flyio-setup.md`, `resend-setup.md`

---

### Phase 8: Definition of Done

- [ ] All 3 user stories implemented
- [ ] Lighthouse Performance ≥90, Accessibility = 100
- [ ] All WCAG AA criteria met (axe-core 0 violations)
- [ ] Backend deployed to Fly.io Frankfurt
- [ ] Frontend deployed to Vercel
- [ ] Rate limiting enforced (BR-012)
- [ ] Background jobs scheduled (BR-028, BR-013, BR-009)
- [ ] Email retries working (BR-022)
- [ ] Concurrency safety verified (BR-024, BR-029)
- [ ] All 140 tests passing
- [ ] Production smoke tests pass
- [ ] Monitoring configured
- [ ] Error logging working

---

## 📚 Specification References

**Business Rules:**
- `/docs/foundation/business-rules.md` - BR-009, 010, 012, 013, 021, 022, 023, 024, 028, 029

**Phase Specification:**
- `/docs/implementation/phase-8-polish.md`

**Deployment Guides:**
- `/docs/deployment/flyio-setup.md` - Fly.io setup, CLI, app deployment
- `/docs/deployment/resend-setup.md` - Resend account, API keys, domain verification

**Constraints:**
- `/docs/constraints/non-functional.md` - Performance targets, availability
- `/docs/constraints/technical-constraints.md` - Mobile-first, browser support

---

## 🎓 Known Gotchas

### Rate Limiting Must Be Server-Side
**Why:** Client-side rate limiting can be bypassed.
**Solution:** Enforce all rate limits in backend before database operations (BR-012).

### Background Jobs Timezone
**Why:** Jobs must run in Europe/Berlin timezone, not UTC.
**Solution:** Use timezone-aware scheduler or convert UTC to Europe/Berlin.

### Lighthouse Performance vs Accessibility Tradeoff
**Why:** Some accessibility features (ARIA, landmarks) add bytes, hurting performance.
**Solution:** Both are mandatory - optimize bundle size with tree-shaking and code splitting.

### SELECT FOR UPDATE Deadlocks
**Why:** If two transactions both try to lock the same rows in different order, deadlock.
**Solution:** Always lock in consistent order (e.g., always lock booking before approvals).

### Email Retry Exponential Backoff
**Why:** Immediate retries can overload email service.
**Solution:** BR-022 specifies 2s, 4s, 8s delays - follow exactly.

---

## 🔄 Next Steps

**To start Increment 5:**

1. Verify all increments 1-4 complete (all features implemented, tested)
2. Start with US-8.1 (Performance)
   - Run Lighthouse audits (baseline)
   - Identify slow queries (add indexes, eager loading)
   - Optimize bundle size (code splitting, lazy loading)
   - Re-run Lighthouse (verify ≥90)

3. Continue with US-8.2 (Accessibility)
   - Run axe-core audits (identify violations)
   - Add ARIA labels (all in German)
   - Fix color contrast issues
   - Test keyboard navigation
   - Verify screen reader compatibility
   - Re-run axe-core (verify 0 violations)

4. Finish with US-8.3 (Deployment)
   - Set up Fly.io account + app
   - Deploy backend (verify health check)
   - Set up Resend account + domain
   - Deploy frontend (verify preview URL)
   - Configure rate limiting
   - Schedule background jobs
   - Run production smoke tests
   - Launch 🚀

**When starting, always read `/project/BACKLOG.md` first to confirm priority.**
