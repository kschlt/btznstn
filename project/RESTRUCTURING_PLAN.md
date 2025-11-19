# Increment Restructuring Plan

**Date:** 2025-11-19
**Task:** Create all 5 increment files with dependency-based user story ordering

---

## Increment Structure

###  Increment 1: Backend Core (Phases 0-2)
**Dependencies:** None
**User Story Order (Dependency-Based):**

**Phase 0:** (All complete)
- US-0.1: FastAPI scaffold ✅
- US-0.2: PostgreSQL setup ✅
- US-0.3: Test infrastructure ✅
- US-0.4: Linting (ruff) ✅
- US-0.5: Type checking (mypy) ✅

**Phase 1:** (All complete)
- US-1.1: Database models ✅
- US-1.2: Repository pattern ✅
- US-1.3: Database migration ✅
- US-1.4: Test utilities ✅

**Phase 2:** (Reordered by dependency)
1. US-2.1: Create Booking ✅ (Foundation - must be first)
2. US-2.2: Get Booking ✅ (Depends on US-2.1)
3. US-2.4: Cancel Booking ⏸️ (Depends on US-2.1, simpler than edit)
4. US-2.5: Calendar View ⏸️ (Depends on US-2.2, read-only, simpler)
5. US-2.3: Edit Booking ⏸️ (Depends on US-2.1, most complex - BR-005 logic)

**Rationale:** Calendar and Cancel are simpler than Edit. Edit has complex BR-005 logic (extend vs shorten detection), so do it last when team is most familiar with codebase.

---

### Increment 2: Backend Business Logic (Phases 3-4)
**Dependencies:** Increment 1 complete
**User Story Order (Dependency-Based):**

**Phase 3:**
1. US-3.1: Approve Endpoint (Core functionality)
2. US-3.2: Deny Endpoint (Core functionality)
3. US-3.3: Reopen from Denied (Depends on US-3.2 conceptually)

**Phase 4:**
4. US-4.1: Resend Integration (Foundation for emails)
5. US-4.2: Email Templates (Depends on US-4.1)
6. US-4.3: Email Retry Logic (Depends on US-4.1, US-4.2)
7. US-4.4: Weekly Digest (Depends on all Phase 4 + Phase 3 approvals)

**Rationale:** Phase 3 must complete before Phase 4 can fully work (emails reference approval status). Within Phase 4, setup first, then templates, then advanced features.

---

### Increment 3: Frontend Core (Phases 5-6)
**Dependencies:** Increment 1 complete + Playwright configured
**User Story Order (Dependency-Based):**

**Phase 5:**
1. US-5.1: Month View (Foundation - calendar core)
2. US-5.2: Year View (Depends on US-5.1 components)
3. US-5.3: Booking Details Modal (Depends on US-5.1 for integration)

**Phase 6:**
4. US-6.2: Date Picker (Shared component - used by US-6.1 and US-6.3)
5. US-6.1: Create Booking Form (Depends on US-5.1 calendar, US-6.2 date picker)
6. US-6.3: Edit Booking Form (Depends on US-6.1, US-6.2, reuses components)

**Rationale:** Calendar views first (read-only, simpler). Date picker before forms (shared dependency). Create before Edit (Edit reuses Create patterns).

---

### Increment 4: Frontend Approver (Phase 7)
**Dependencies:** Increment 2 (approval backend) + Increment 3 (frontend core)
**User Story Order (Dependency-Based):**

1. US-7.1: Approver Overview (Outstanding/History tabs - foundation)
2. US-7.2: One-Click Approve (Depends on US-7.1 for list integration)
3. US-7.3: Deny with Comment (Depends on US-7.1, similar to US-7.2)

**Rationale:** Overview first (displays data), then actions (modify data). Approve and Deny are parallel, but Approve is simpler (no comment validation).

---

### Increment 5: Production Ready (Phase 8)
**Dependencies:** All increments 1-4 complete
**User Story Order (Dependency-Based):**

1. US-8.1: Performance Optimization (Can start first, improves existing code)
2. US-8.2: Accessibility (WCAG AA) (Can run parallel to US-8.1)
3. US-8.3: Production Deployment (Depends on US-8.1, US-8.2 complete)

**Rationale:** Performance and Accessibility can be done in parallel. Deployment last (requires both complete).

---

## User Story Status System

**Three statuses:**
- 📝 **Draft** - Idea exists, not fully specified (acceptance criteria incomplete)
- ✅ **Specified** - Fully documented, acceptance criteria complete, ready for dev
- 🎉 **Implemented** - Code complete, all tests passing, merged

**Current Status (as of 2025-11-19):**
- Phase 0: All 🎉 Implemented
- Phase 1: All 🎉 Implemented
- Phase 2: US-2.1, US-2.2 🎉 Implemented; US-2.3, US-2.4, US-2.5 ✅ Specified
- Phase 3-8: All ✅ Specified (per existing docs)

---

## Tracking Decisions

**YES - Track:**
- ✅ Test counts (Estimated vs Actual) - Helps verify completeness
- ✅ Checkboxes in Definition of Done - Update as work progresses
- ✅ User story status (Draft/Specified/Implemented) - Critical for planning

**NO - Don't Track:**
- ❌ Git branches per user story - Adds maintenance, minimal value
- ❌ Time tracking (estimated vs actual) - Not relevant to user

---

## Next Steps

1. Update `/project/increments/increment-01.md` with corrected user story order
2. Create `/project/increments/increment-02.md` (Phases 3-4)
3. Create `/project/increments/increment-03.md` (Phases 5-6)
4. Create `/project/increments/increment-04.md` (Phase 7)
5. Create `/project/increments/increment-05.md` (Phase 8)
6. Extract insights from 8 analysis files into user stories / CLAUDE.md files
7. Update main `/CLAUDE.md` to reference `/project/` first

---

**This plan ensures dependency-based ordering and proper status tracking.**
