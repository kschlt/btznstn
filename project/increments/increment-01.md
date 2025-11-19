# Increment 1: Backend Core

**Status:** 🔄 **In Progress** (70% complete)
**Phases:** 0, 1, 2
**Started:** 2025-11 (estimated)
**Target Completion:** TBD
**Dependencies:** None (first increment)

---

## 📋 Overview

**Goal:** Build foundational backend infrastructure and booking CRUD endpoints.

**Deliverables:**
- FastAPI application scaffold
- PostgreSQL database with migrations
- Booking, Approval, TimelineEvent models
- Test infrastructure (pytest, factories, fixtures)
- Booking API endpoints (create, get, edit, cancel, calendar)

**Success Criteria:**
- All endpoints implemented and tested
- Type safety throughout (mypy strict)
- Linting passing (ruff)
- Code coverage ≥80%
- German error messages match specification

---

## 📊 Progress Summary

| Phase | User Stories | Completed | In Progress | Pending | Status |
|-------|--------------|-----------|-------------|---------|--------|
| **0** | 5 | 5 | 0 | 0 | ✅ Complete |
| **1** | 3 | 3 | 0 | 0 | ✅ Complete |
| **2** | 5 | 2 | 0 | 3 | 🔄 In Progress (40%) |
| **Total** | **13** | **10** | **0** | **3** | **🔄 77%** |

---

## 🎯 Phase 0: Foundation

**Status:** ✅ **Complete**
**Completion Date:** 2025-11 (estimated)

### User Stories

#### US-0.1: FastAPI Application Scaffold ✅
**Description:** Set up FastAPI application structure with basic configuration

**Completed:**
- ✅ FastAPI app initialized
- ✅ Project structure created (`/api/app/`)
- ✅ Basic routing setup
- ✅ CORS configuration
- ✅ Environment variable loading

**Files:**
- `/api/app/main.py` - FastAPI application entry point
- `/api/app/config.py` - Configuration management

---

#### US-0.2: PostgreSQL Database Setup ✅
**Description:** Configure PostgreSQL database with Alembic migrations

**Completed:**
- ✅ PostgreSQL connection configured
- ✅ SQLAlchemy async setup
- ✅ Alembic migrations initialized
- ✅ Database URL from environment variable

**Files:**
- `/api/app/database.py` - Database session management
- `/api/alembic/` - Migration scripts
- `/api/alembic.ini` - Alembic configuration

---

#### US-0.3: Test Infrastructure ✅
**Description:** Set up pytest with async support and test database

**Completed:**
- ✅ pytest configured
- ✅ Async test support (pytest-asyncio)
- ✅ Test database isolation (transactional tests)
- ✅ Fixtures for database session and API client

**Files:**
- `/api/tests/conftest.py` - Test fixtures
- `/api/pytest.ini` - pytest configuration

---

#### US-0.4: Linting Setup (ruff) ✅
**Description:** Configure code linting with ruff

**Completed:**
- ✅ ruff installed and configured
- ✅ Linting rules defined in `pyproject.toml`
- ✅ Pre-commit integration (optional)

**Files:**
- `/api/pyproject.toml` - ruff configuration

**Command:**
```bash
ruff check api/app/
```

---

#### US-0.5: Type Checking Setup (mypy) ✅
**Description:** Configure strict type checking with mypy

**Completed:**
- ✅ mypy installed and configured
- ✅ Strict mode enabled
- ✅ All existing code type-checked

**Files:**
- `/api/mypy.ini` - mypy configuration

**Command:**
```bash
mypy api/app/
```

---

### Phase 0: Definition of Done

- [x] FastAPI app runs locally
- [x] Database connects successfully
- [x] Tests run and pass
- [x] Linting passes (ruff)
- [x] Type checking passes (mypy)

---

## 🎯 Phase 1: Data Layer

**Status:** ✅ **Complete** (with 9 critical fixes applied)
**Completion Date:** 2025-11 (estimated)

### User Stories

#### US-1.1: Database Models ✅
**Description:** Create SQLAlchemy models for Booking, Approval, TimelineEvent, ApproverParty

**Completed:**
- ✅ `Booking` model with all fields per spec
- ✅ `Approval` model with FK to Booking and ApproverParty
- ✅ `TimelineEvent` model for audit trail
- ✅ `ApproverParty` model (3 fixed approvers)
- ✅ Enums: StatusEnum, DecisionEnum, AffiliationEnum
- ✅ Relationships configured (Booking.approvals, etc.)
- ✅ String constraints match specification exactly

**Files:**
- `/api/app/models/booking.py`
- `/api/app/models/approval.py`
- `/api/app/models/timeline_event.py`
- `/api/app/models/approver_party.py`
- `/api/app/models/enums.py`

**Business Rules Implemented:**
- BR-001: total_days calculated as (end - start).days + 1
- BR-014: is_past calculated with Europe/Berlin timezone

**Critical Fixes Applied (9 total):**
1. String constraints corrected (email: 254, first_name: 40, description: 500)
2. Indexes added for performance (date range GiST, status, email, last_activity_at DESC)
3. Other fixes documented in `/docs/implementation/phase-1-critical-fixes.md` (if exists)

---

#### US-1.2: Repository Pattern ✅
**Description:** Create repository classes for data access

**Completed:**
- ✅ `BookingRepository` - CRUD operations for bookings
- ✅ `ApprovalRepository` - CRUD operations for approvals
- ✅ `TimelineRepository` - Create timeline events
- ✅ Async methods throughout
- ✅ Type hints on all methods

**Files:**
- `/api/app/repositories/booking_repository.py`
- `/api/app/repositories/approval_repository.py`
- `/api/app/repositories/timeline_repository.py`

---

#### US-1.3: Database Migration ✅
**Description:** Create initial database migration with all tables and seed data

**Completed:**
- ✅ Migration `001_initial_schema.py` created
- ✅ All tables created (bookings, approvals, timeline_events, approver_parties)
- ✅ All indexes created
- ✅ Seed data for 3 approver parties (Ingeborg, Cornelia, Angelika)
- ✅ Migration tested (up and down)

**Files:**
- `/api/alembic/versions/001_initial_schema.py`

**Command to run:**
```bash
alembic upgrade head
```

---

### US-1.4: Test Utilities ✅
**Description:** Create test factories and fixtures for test data

**Completed:**
- ✅ Factory functions: `make_booking()`, `make_approval()`, `make_timeline_event()`
- ✅ Test fixtures: `booking_with_approvals`, `confirmed_booking`, `denied_booking`
- ✅ Utility functions: `get_today()`, `get_now()`, `booking_request()`, `assert_booking_response_structure()`
- ✅ CLAUDE.md guidance created (1016 lines of test patterns)

**Files:**
- `/api/tests/fixtures/factories.py` - Factory functions
- `/api/tests/utils.py` - Utility functions
- `/api/tests/CLAUDE.md` - Test guidance (exceptional quality)

**Key Patterns:**
- DRY principle enforced (Don't Repeat Yourself)
- Request builder pattern for API tests
- Parametrized tests for validation scenarios

---

### Phase 1: Definition of Done

- [x] All models created and tested
- [x] All repositories created and tested
- [x] Migration runs successfully (up and down)
- [x] Test utilities available and documented
- [x] String constraints match specification
- [x] Indexes created for performance
- [x] Type safety throughout (mypy passes)
- [x] 9 critical issues identified and fixed

---

## 🎯 Phase 2: Booking API

**Status:** 🔄 **In Progress** (40% complete)
**Started:** 2025-11 (estimated)
**Target Completion:** TBD

### User Stories

#### US-2.1: Create Booking ✅
**Description:** Implement POST /api/v1/bookings endpoint for creating new bookings

**Status:** ✅ **Complete**
**Completed:** 2025-11 (estimated)

**Implemented:**
- ✅ POST /api/v1/bookings endpoint
- ✅ Request validation (Pydantic schemas)
- ✅ Conflict detection (BR-002: no overlaps with Pending/Confirmed)
- ✅ First-write-wins concurrency (BR-029)
- ✅ German error messages (exact copy from spec)
- ✅ Return booking with token for requester
- ✅ 3 approvals created with NoResponse status
- ✅ Comprehensive tests (parametrized for validation)

**Files:**
- `/api/app/routers/bookings.py` - Endpoint implementation
- `/api/app/schemas/booking.py` - Pydantic schemas (BookingCreate, BookingResponse)
- `/api/app/services/booking_service.py` - Business logic
- `/api/tests/integration/test_create_booking.py` - Tests

**Business Rules Enforced:**
- BR-001: Inclusive end date (total_days = end - start + 1)
- BR-002: No overlaps with Pending/Confirmed bookings
- BR-003: Three approvals created automatically
- BR-011: German error messages
- BR-017: Party size 1-10
- BR-019: First name validation
- BR-020: URL blocking in description
- BR-026: Future horizon ≤18 months
- BR-029: First-write-wins (conflict detection)

**Tests:** ~15 tests (parametrized validation + happy path + conflicts)

**Definition of Done:**
- [x] Endpoint implemented
- [x] All validation rules enforced
- [x] Conflict detection working
- [x] German errors match spec
- [x] Tests passing
- [x] Type checking passes
- [x] Linting passes

---

#### US-2.2: Get Booking ✅
**Description:** Implement GET /api/v1/bookings/{id} endpoint with public and authenticated views

**Status:** ✅ **Complete**
**Completed:** 2025-11 (estimated)

**Implemented:**
- ✅ GET /api/v1/bookings/{id} endpoint
- ✅ Public view (no token): Shows Pending/Confirmed only, no email, no approvals
- ✅ Authenticated view (with token): Shows full details including approvals
- ✅ Privacy enforcement (BR-004: Denied bookings not public)
- ✅ German error messages (404, 401)
- ✅ Comprehensive tests (public + requester views)

**Files:**
- `/api/app/routers/bookings.py` - Endpoint implementation
- `/api/app/schemas/booking.py` - PublicBookingResponse, BookingResponse schemas
- `/api/tests/integration/test_get_booking.py` - Tests

**Business Rules Enforced:**
- BR-004: Denied/Canceled bookings not shown publicly
- BR-010: Tokens never expire
- BR-011: German error messages
- BR-014: is_past field calculated (Europe/Berlin timezone)

**Tests:** ~10 tests (public view, requester view, privacy, errors)

**Definition of Done:**
- [x] Endpoint implemented
- [x] Public vs authenticated views working
- [x] Privacy enforced (no email in public view)
- [x] Denied/Canceled hidden from public
- [x] German errors match spec
- [x] Tests passing
- [x] Type checking passes
- [x] Linting passes

---

#### US-2.3: Edit Booking ⏸️
**Description:** Implement PATCH /api/v1/bookings/{id} endpoint for editing bookings

**Status:** ⏸️ **Pending**

**Requirements:**
- PATCH /api/v1/bookings/{id}?token={requester_token}
- Allow editing: start_date, end_date, party_size, affiliation, description
- Email is immutable (cannot change)
- Past bookings (EndDate < today) cannot be edited (BR-014)
- Detect change type:
  - **Date extend** (earlier start OR later end) → Reset approvals to NoResponse (BR-005)
  - **Date shorten** (within original bounds) → Keep approvals (BR-005)
  - **Non-date changes** (party size, affiliation, description only) → Keep approvals
- Conflict detection on new date range (BR-002)
- German error messages

**Business Rules:**
- BR-001: Inclusive end date
- BR-002: No conflicts with Pending/Confirmed
- BR-005: **Critical** - Date extend resets approvals; shorten keeps
- BR-011: German errors
- BR-014: Past items read-only
- BR-026: Future horizon

**Files to Create:**
- `/api/tests/integration/test_edit_booking.py` - Tests FIRST
- Update `/api/app/routers/bookings.py` - Endpoint implementation
- Update `/api/app/services/booking_service.py` - Edit logic

**Tests to Write (~15 tests):**
- Test edit with date shortening (approvals kept)
- Test edit with date extension (approvals reset)
- Test edit start earlier (extend → reset)
- Test edit end later (extend → reset)
- Test edit party size only (approvals kept)
- Test edit description only (approvals kept)
- Test edit past booking (rejected)
- Test edit with new conflict (rejected)
- Test German error messages

**Definition of Done:**
- [ ] All tests written and failing
- [ ] Endpoint implemented
- [ ] BR-005 logic correct (extend vs shorten detection)
- [ ] Conflict detection working
- [ ] Past booking check working
- [ ] German errors match spec
- [ ] All tests passing
- [ ] Type checking passes
- [ ] Linting passes

**Estimated Effort:** 4-6 hours

---

#### US-2.4: Cancel Booking ⏸️
**Description:** Implement DELETE /api/v1/bookings/{id} endpoint for canceling bookings

**Status:** ⏸️ **Pending**

**Requirements:**
- DELETE /api/v1/bookings/{id}?token={requester_token}
- Requester can cancel Pending or Confirmed bookings (BR-006)
- Cannot cancel Denied bookings (already terminal)
- Cancel is idempotent - cancel twice shows "Schon storniert" (already canceled)
- Canceled booking transitions to Canceled status
- Move to Archive (BR-013)
- German success/error messages

**Business Rules:**
- BR-006: Requester can cancel Pending/Confirmed
- BR-010: Idempotent (same result on retry)
- BR-011: German messages
- BR-013: Canceled → Archive

**Files to Create:**
- `/api/tests/integration/test_cancel_booking.py` - Tests FIRST
- Update `/api/app/routers/bookings.py` - Endpoint implementation
- Update `/api/app/services/booking_service.py` - Cancel logic

**Tests to Write (~10 tests):**
- Test cancel Pending booking (success)
- Test cancel Confirmed booking (success)
- Test cancel Denied booking (rejected - already terminal)
- Test cancel already Canceled (idempotent - shows "Schon storniert")
- Test cancel without token (401)
- Test cancel with wrong token (403)
- Test cancel non-existent booking (404)
- Test German messages

**Definition of Done:**
- [ ] All tests written and failing
- [ ] Endpoint implemented
- [ ] Status transition to Canceled working
- [ ] Idempotency working (cancel twice = success)
- [ ] Archive logic implemented
- [ ] German messages match spec
- [ ] All tests passing
- [ ] Type checking passes
- [ ] Linting passes

**Estimated Effort:** 3-4 hours

---

#### US-2.5: Calendar View ⏸️
**Description:** Implement GET /api/v1/calendar endpoint for month/year calendar view

**Status:** ⏸️ **Pending**

**Requirements:**
- GET /api/v1/calendar?month=2&year=2025
- Return all Pending and Confirmed bookings for the specified month
- Exclude Denied and Canceled bookings (BR-004)
- Include bookings that overlap the month (not just start in month)
- Calculate is_past for each booking (BR-014)
- Return minimal public data (no emails, no approval details)
- Optimize query (use indexes on date range)

**Business Rules:**
- BR-002: Show Pending + Confirmed
- BR-004: Hide Denied + Canceled
- BR-014: Calculate is_past (Europe/Berlin timezone)

**Files to Create:**
- `/api/tests/integration/test_calendar.py` - Tests FIRST
- Update `/api/app/routers/bookings.py` - Endpoint implementation
- Update `/api/app/services/booking_service.py` - Calendar query

**Tests to Write (~12 tests):**
- Test calendar month view (February 2025)
- Test includes Pending bookings
- Test includes Confirmed bookings
- Test excludes Denied bookings
- Test excludes Canceled bookings
- Test date range filtering (overlap detection)
- Test ordering (by start_date ASC)
- Test is_past field calculated correctly
- Test empty month (no bookings)
- Test query performance (<100ms for 100+ bookings)
- Test privacy (no emails in response)

**Definition of Done:**
- [ ] All tests written and failing
- [ ] Endpoint implemented
- [ ] Query filters correctly (Pending + Confirmed only)
- [ ] Date range overlap logic correct
- [ ] is_past calculated correctly (Europe/Berlin)
- [ ] Privacy enforced (no emails)
- [ ] Query optimized (indexes used)
- [ ] All tests passing
- [ ] Type checking passes
- [ ] Linting passes

**Estimated Effort:** 3-4 hours

---

### Phase 2: Definition of Done

- [ ] All 5 user stories complete
- [ ] All endpoints implemented and tested
- [ ] All business rules enforced
- [ ] German error messages match specification exactly
- [ ] Type safety throughout (mypy strict)
- [ ] Linting passing (ruff)
- [ ] Code coverage ≥80%
- [ ] All tests passing
- [ ] API documentation updated (if using Swagger/OpenAPI)

---

## 📚 Specification References

### Business Rules
- `/docs/foundation/business-rules.md` - BR-001 to BR-029

### API Specifications
- `/docs/design/api-specification.md` - Endpoint details

### Data Model
- `/docs/design/database-schema.md` - Schema and constraints

### German Copy
- `/docs/specification/error-handling.md` - All error messages
- `/docs/specification/notifications.md` - Email templates (for Phase 4)

### Implementation Guides
- `/docs/implementation/phase-2-booking-api.md` - Phase 2 user stories
- `/api/tests/CLAUDE.md` - Test patterns and guidance (1016 lines)

---

## 🎓 Learnings & Notes

### Phase 1 Learnings

**9 Critical Fixes Applied:**
1. String constraints must match specification exactly
2. Indexes are critical for performance (especially date range GiST for BR-002, BR-029)
3. Test utilities (factories) prevent duplication
4. Request builder pattern eliminates JSON repetition in tests
5. (Other fixes - see full documentation if available)

**Takeaway:** Thorough review after implementation catches issues before they compound.

### Test Patterns

**From `/api/tests/CLAUDE.md`:**
- Use factories (`make_booking()`) instead of manual `Booking(...)`
- Use request builder (`booking_request()`) instead of repeating JSON
- Parametrize validation tests (DRY principle)
- Always use `get_today()` for dates (Europe/Berlin timezone)
- Assert response structure with `assert_booking_response_structure()`

### German Copy

**All error messages MUST be exact copy from specifications:**
- "Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung ({{Vorname}} – {{Status}})."
- "Bitte gib einen gültigen Vornamen an (Buchstaben, Leerzeichen, Bindestrich, Apostroph; max. 40 Zeichen)."
- Never paraphrase or translate

---

## 🔄 Next Steps

**To complete Increment 1:**

1. ✅ Implement US-2.3 (Edit Booking)
   - Read spec and BR-005
   - Write tests first
   - Implement endpoint
   - Verify all tests pass

2. ✅ Implement US-2.4 (Cancel Booking)
   - Read spec and BR-006
   - Write tests first
   - Implement endpoint
   - Verify idempotency

3. ✅ Implement US-2.5 (Calendar View)
   - Read spec and BR-002, BR-004
   - Write tests first
   - Implement endpoint
   - Optimize query

4. ✅ Verify increment complete
   - All tests passing
   - Coverage ≥80%
   - Type checking passes
   - Linting passes

5. ✅ Move to Increment 2
   - Start Phase 3 (Approval Flow)

---

**When starting work, always read `/project/BACKLOG.md` first to confirm priority.**
