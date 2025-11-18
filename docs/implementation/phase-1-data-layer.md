# Phase 1: Data Layer

## Goal

Implement database schema, SQLAlchemy models, and repository pattern with full type safety.

**Duration:** 2-3 days | **Dependencies:** Phase 0 (Foundation)

---

## 🚨 MANDATORY: Read Before Starting

**Before writing ANY code:**

1. ✅ Read `/docs/implementation/CLAUDE.md` - Strict TDD workflow (Steps 1-7)
2. ✅ Complete pre-implementation checklist (identify ALL BRs, edge cases, DB patterns)
3. ✅ Write ALL tests FIRST (must fail initially)
4. ✅ **Review tests for completeness (Step 3 - Four-Eyes Principle)**
5. ✅ Implement code until tests pass
6. ✅ Self-review against checklist

**Phase 1 applies 15 business rules with ~89 tests across 4 user stories.**

**Critical learnings from Phase 1 implementation:**
- Schema drift (models vs migration) causes production bugs
- Multi-month calendar overlap logic is non-trivial
- N+1 query problems require explicit eager loading
- Ordering by `last_activity_at` not `created_at` per BR-023
- Return types matter (Booking vs Approval)

**See `/docs/implementation/phase-1-critical-fixes.md` for detailed analysis of 9 issues prevented by TDD.**

---

## User Stories

### US-1.1: Database Schema (Alembic Migration)

**As a** developer
**I want** PostgreSQL tables for bookings, approvals, timeline, and approver parties
**So that** I can persist booking data with full referential integrity

---

**Applicable Business Rules:**

- **BR-001** (Inclusive end date): Database stores dates; validation ensures `end_date >= start_date`
  - *Why:* Jan 1-5 = 5 days. Check constraint `end_date >= start_date` enforced at DB level.

- **BR-002** (No overlaps): GiST index on date range for efficient conflict detection
  - *Why:* PostgreSQL's `daterange` type with GiST index enables fast overlap queries.

- **BR-003** (Three approvers): Seed data for Ingeborg, Cornelia, Angelika in `approver_parties` table
  - *Why:* These are fixed parties, not user-managed data. Must be present at deployment.

- **BR-017** (Party size): Check constraint `party_size >= 1 AND party_size <= 10`
  - *Why:* Database-level validation prevents invalid data from ever being inserted.

- **BR-023** (Ordering): Index on `last_activity_at DESC` for fast sorted queries
  - *Why:* All list views sort by LastActivityAt desc. Index improves performance.

- **BR-024** (First-action-wins): Row-level locking supported by PostgreSQL
  - *Why:* SELECT FOR UPDATE prevents race conditions in approval flow.

- **BR-029** (First-write-wins): Transaction isolation supported by PostgreSQL
  - *Why:* Concurrent booking creations must serialize at database level.

- **Email length**: VARCHAR(254) per RFC 5321 maximum email address length
  - *Why:* Standard limit for email addresses. Prevents truncation.

- **First name length**: VARCHAR(40) sufficient for international names
  - *Why:* Balances storage with real-world name lengths.

- **Description/Comment**: VARCHAR(500) allows detailed explanations without abuse
  - *Why:* Timeline note unlimited (Text) for internal use; user input limited to 500.

---

**Database Schema Requirements:**

**Enums (3):**
- [ ] `affiliation_enum`: Ingeborg, Cornelia, Angelika
- [ ] `status_enum`: Pending, Denied, Confirmed, Canceled
- [ ] `decision_enum`: NoResponse, Approved, Denied

**Tables (4):**
- [ ] `approver_parties`: Party config (3 seed rows)
- [ ] `bookings`: Core booking entity
- [ ] `approvals`: 3 per booking (Ingeborg, Cornelia, Angelika)
- [ ] `timeline_events`: Activity log per booking

**Constraints:**
- [ ] `check_end_after_start`: `end_date >= start_date` on bookings
- [ ] `check_party_size_range`: `party_size >= 1 AND party_size <= 10` on bookings
- [ ] `uq_booking_party`: UNIQUE(booking_id, party) on approvals

**Indexes (9):**
- [ ] `idx_bookings_status` (BTREE)
- [ ] `idx_bookings_requester_email` (BTREE)
- [ ] `idx_bookings_last_activity` (BTREE DESC)
- [ ] `idx_bookings_date_range` (GIST) - for BR-002 conflict detection
- [ ] `idx_approvals_booking` (BTREE)
- [ ] `idx_approvals_decision` (BTREE)
- [ ] `idx_approvals_party_decision` (BTREE) - composite for approver queries
- [ ] `idx_timeline_booking` (BTREE)
- [ ] `idx_timeline_when` (BTREE DESC) - "when" is PostgreSQL keyword, quote it!

**Foreign Keys:**
- [ ] `approvals.booking_id` → `bookings.id` (CASCADE DELETE)
- [ ] `timeline_events.booking_id` → `bookings.id` (CASCADE DELETE)

**Triggers:**
- [ ] `update_updated_at_column()` function + trigger for bookings.updated_at

**Seed Data:**
- [ ] 3 rows in `approver_parties` (idempotent with ON CONFLICT DO NOTHING)

---

**Granular Acceptance Criteria:**

Schema Completeness:
- [ ] All 3 enums created with exact values (case-sensitive: "Pending" not "PENDING")
- [ ] `bookings` table has exactly 13 columns with correct types
- [ ] `approvals` table has exactly 6 columns with correct types
- [ ] `timeline_events` table has exactly 6 columns with correct types
- [ ] `approver_parties` table has exactly 3 columns with correct types

String Length Constraints (CRITICAL - prevents schema drift):
- [ ] `bookings.requester_first_name` is VARCHAR(40) not unlimited Text
- [ ] `bookings.requester_email` is VARCHAR(254) per RFC 5321
- [ ] `bookings.description` is VARCHAR(500) (optional)
- [ ] `approvals.comment` is VARCHAR(500) (optional)
- [ ] `timeline_events.actor` is VARCHAR(50)
- [ ] `timeline_events.event_type` is VARCHAR(50)
- [ ] `timeline_events.note` is Text (unlimited for internal use)
- [ ] `approver_parties.email` is VARCHAR(254)

Check Constraints:
- [ ] `end_date >= start_date` enforced at database level
- [ ] `party_size >= 1 AND party_size <= 10` enforced at database level
- [ ] Inserting party_size=0 raises IntegrityError
- [ ] Inserting party_size=11 raises IntegrityError
- [ ] Inserting end_date < start_date raises IntegrityError

Index Creation (DESC pattern consistency):
- [ ] `idx_bookings_last_activity` uses `postgresql_ops={"last_activity_at": "DESC"}`
- [ ] `idx_timeline_when` uses `postgresql_ops={"when": "DESC"}` with quoted column name
- [ ] GiST index uses `daterange(start_date, end_date, '[]')` (inclusive bounds)

Seed Data Idempotency:
- [ ] Running migration twice does NOT create duplicate approver_parties
- [ ] `ON CONFLICT (party) DO NOTHING` prevents duplicates
- [ ] After migration: exactly 3 rows in approver_parties

Asyncpg Compatibility:
- [ ] Each `op.execute()` contains only ONE SQL statement (no semicolons)
- [ ] Enum creation uses separate DO blocks per enum
- [ ] Trigger function and trigger created in separate `op.execute()` calls

---

**Complete Test Plan:**

**Migration Success (5 tests):**
1. `test_migration_runs_successfully` - `alembic upgrade head` exits 0
2. `test_migration_idempotent` - Running upgrade twice succeeds
3. `test_downgrade_works` - `alembic downgrade base` succeeds
4. `test_upgrade_after_downgrade` - Round-trip migration works
5. `test_no_asyncpg_errors` - No multi-statement errors with asyncpg

**Enums Created (3 tests):**
6. `test_affiliation_enum_exists` - Query pg_type for affiliation_enum
7. `test_status_enum_exists` - Query pg_type for status_enum
8. `test_decision_enum_exists` - Query pg_type for decision_enum

**Tables Exist (4 tests):**
9. `test_approver_parties_table` - Query information_schema.tables
10. `test_bookings_table` - Query information_schema.tables
11. `test_approvals_table` - Query information_schema.tables
12. `test_timeline_events_table` - Query information_schema.tables

**Bookings Table Schema (13 tests - one per column):**
13. `test_bookings_id_uuid` - Column type is UUID
14. `test_bookings_start_date` - Column type is DATE
15. `test_bookings_end_date` - Column type is DATE
16. `test_bookings_total_days_integer` - Column type is INTEGER
17. `test_bookings_party_size_integer` - Column type is INTEGER
18. `test_bookings_affiliation_enum` - Column type is affiliation_enum
19. `test_bookings_requester_first_name_varchar40` - VARCHAR(40) exactly
20. `test_bookings_requester_email_varchar254` - VARCHAR(254) exactly
21. `test_bookings_description_varchar500` - VARCHAR(500) nullable
22. `test_bookings_status_enum` - Column type is status_enum
23. `test_bookings_created_at_timestamp` - TIMESTAMPTZ type
24. `test_bookings_updated_at_timestamp` - TIMESTAMPTZ type
25. `test_bookings_last_activity_at_timestamp` - TIMESTAMPTZ type

**Approvals Table Schema (6 tests - one per column):**
26. `test_approvals_id_uuid` - Column type is UUID
27. `test_approvals_booking_id_uuid` - Foreign key to bookings
28. `test_approvals_party_enum` - Column type is affiliation_enum
29. `test_approvals_decision_enum` - Column type is decision_enum
30. `test_approvals_comment_varchar500` - VARCHAR(500) nullable
31. `test_approvals_decided_at_timestamp` - TIMESTAMPTZ nullable

**Check Constraints (5 tests):**
32. `test_party_size_zero_constraint` - INSERT party_size=0 fails
33. `test_party_size_eleven_constraint` - INSERT party_size=11 fails
34. `test_party_size_negative_constraint` - INSERT party_size=-1 fails
35. `test_end_before_start_constraint` - INSERT end_date < start_date fails
36. `test_valid_data_passes_constraints` - Valid data inserts successfully

**Indexes Exist (9 tests):**
37. `test_idx_bookings_status` - Index exists
38. `test_idx_bookings_requester_email` - Index exists
39. `test_idx_bookings_last_activity_desc` - Index exists with DESC operator
40. `test_idx_bookings_date_range_gist` - GiST index exists
41. `test_idx_approvals_booking` - Index exists
42. `test_idx_approvals_decision` - Index exists
43. `test_idx_approvals_party_decision` - Composite index exists
44. `test_idx_timeline_booking` - Index exists
45. `test_idx_timeline_when_desc` - Index exists with DESC operator and quoted "when"

**Foreign Keys Cascade (2 tests):**
46. `test_delete_booking_cascades_approvals` - Deleting booking deletes approvals
47. `test_delete_booking_cascades_timeline` - Deleting booking deletes timeline events

**Seed Data (4 tests):**
48. `test_approver_parties_count` - Exactly 3 rows
49. `test_approver_parties_ingeborg` - Ingeborg row exists with email
50. `test_approver_parties_cornelia` - Cornelia row exists with email
51. `test_approver_parties_angelika` - Angelika row exists with email

**Trigger (2 tests):**
52. `test_updated_at_trigger_exists` - Function and trigger created
53. `test_updated_at_trigger_works` - Updating booking updates updated_at

**TOTAL: ~53 tests for US-1.1**

---

**Gherkin Scenarios:**

```gherkin
Feature: Database Schema Migration

  Scenario: Migration runs successfully
    Given Alembic is configured
    When I run "alembic upgrade head"
    Then the command should exit with code 0
    And I should see "Running upgrade -> 001"

  Scenario: Tables created
    Given the migration has run
    When I query information_schema.tables
    Then I should see tables:
      | table            |
      | approver_parties |
      | bookings         |
      | approvals        |
      | timeline_events  |

  Scenario: String length constraints prevent schema drift (CRITICAL)
    Given the bookings table exists
    When I query column definitions
    Then I should see:
      | column               | type         |
      | requester_first_name | VARCHAR(40)  |
      | requester_email      | VARCHAR(254) |
      | description          | VARCHAR(500) |
    And NOT unlimited Text types for user input fields

  Scenario: Check constraints validated
    Given the bookings table exists
    When I try to INSERT party_size = 0
    Then I should get IntegrityError
    When I try to INSERT party_size = 11
    Then I should get IntegrityError
    When I try to INSERT end_date < start_date
    Then I should get IntegrityError

  Scenario: GiST index for date range overlaps
    Given the bookings table exists
    When I query pg_indexes for idx_bookings_date_range
    Then index type should be "gist"
    And index definition should include "daterange(start_date, end_date, '[]')"

  Scenario: DESC indexes created consistently
    Given the bookings table exists
    When I query idx_bookings_last_activity definition
    Then it should use postgresql_ops pattern
    And NOT use sa.text("last_activity_at DESC")

  Scenario: Seed data is idempotent
    Given the migration has run
    When I run "alembic upgrade head" again
    Then approver_parties should still have exactly 3 rows
    And no duplicates should exist

  Scenario: Foreign key cascades
    Given a booking exists with 3 approvals and 2 timeline events
    When I DELETE the booking
    Then all 3 approvals should be deleted
    And all 2 timeline events should be deleted
```

---

### US-1.2: SQLAlchemy Models

**As a** developer
**I want** type-safe ORM models with proper relationships
**So that** I can query the database with Python type hints and avoid runtime errors

---

**Applicable Business Rules:**

- **BR-001** (Inclusive end date): `compute_total_days()` method returns `(end_date - start_date).days + 1`
  - *Why:* Off-by-one errors are common. Method centralizes calculation.

- **BR-023** (Ordering): Models define DESC indexes for `last_activity_at` and timeline `when`
  - *Why:* Ordering must match migration exactly. Inconsistency causes confusion.

- **Schema Drift Prevention**: Model `mapped_column()` definitions MUST match migration column types
  - *Why:* Migration enforces VARCHAR(40), but model without String(40) allows unlimited text in Python.

---

**Granular Acceptance Criteria:**

Type Safety:
- [ ] All models use `Mapped[type]` type hints (SQLAlchemy 2.0 style)
- [ ] Nullable fields use `Mapped[type | None]`
- [ ] Enums use `Mapped[AffiliationEnum]` not `Mapped[str]`
- [ ] Dates use `Mapped[date]` not `Mapped[datetime]`
- [ ] UUIDs use `Mapped[UUID]` not `Mapped[str]`

String Constraints Match Migration (CRITICAL):
- [ ] `Booking.requester_first_name` is `mapped_column(String(40), nullable=False)`
- [ ] `Booking.requester_email` is `mapped_column(String(254), nullable=False)`
- [ ] `Booking.description` is `mapped_column(String(500), nullable=True)`
- [ ] `Approval.comment` is `mapped_column(String(500), nullable=True)`
- [ ] `TimelineEvent.actor` is `mapped_column(String(50), nullable=False)`
- [ ] `TimelineEvent.event_type` is `mapped_column(String(50), nullable=False)`
- [ ] `TimelineEvent.note` is `mapped_column(Text(), nullable=True)` - unlimited
- [ ] `ApproverParty.email` is `mapped_column(String(254), unique=True, nullable=False)`

Relationships:
- [ ] `Booking.approvals` is `Mapped[list[Approval]]` with cascade delete
- [ ] `Booking.timeline_events` is `Mapped[list[TimelineEvent]]` with cascade delete
- [ ] `Approval.booking` is `Mapped[Booking]` back-reference
- [ ] `TimelineEvent.booking` is `Mapped[Booking]` back-reference

Indexes Match Migration:
- [ ] `idx_bookings_last_activity` uses `postgresql_ops={"last_activity_at": "DESC"}`
- [ ] `idx_bookings_date_range` uses GiST with `func.daterange(start_date, end_date, "[]")`
- [ ] `idx_timeline_when` uses `postgresql_ops={"when": "DESC"}` - quoted column name

Constraints Match Migration:
- [ ] `check_end_after_start` constraint defined in model
- [ ] `check_party_size_range` constraint defined in model
- [ ] `uq_booking_party` unique constraint defined in Approval model

Methods:
- [ ] `Booking.compute_total_days()` returns `int`
- [ ] `Booking.__repr__()` includes id, dates, status for debugging

---

**Complete Test Plan:**

**Model Attributes (4 tests):**
1. `test_booking_model_has_attributes` - All 13 attributes present
2. `test_approval_model_has_attributes` - All 6 attributes present
3. `test_timeline_model_has_attributes` - All 6 attributes present
4. `test_approver_party_model_has_attributes` - All 3 attributes present

**String Constraint Verification (CRITICAL - 8 tests):**
5. `test_booking_requester_first_name_string40` - Verify String(40) type
6. `test_booking_requester_email_string254` - Verify String(254) type
7. `test_booking_description_string500` - Verify String(500) type
8. `test_approval_comment_string500` - Verify String(500) type
9. `test_timeline_actor_string50` - Verify String(50) type
10. `test_timeline_event_type_string50` - Verify String(50) type
11. `test_timeline_note_text` - Verify Text() type (unlimited)
12. `test_approver_party_email_string254` - Verify String(254) type

**Type Hints (5 tests):**
13. `test_booking_type_hints` - Verify Mapped[date], Mapped[UUID], etc.
14. `test_approval_type_hints` - Verify Mapped[DecisionEnum], etc.
15. `test_timeline_type_hints` - Verify Mapped[datetime], etc.
16. `test_nullable_fields` - Verify Mapped[str | None] for optional fields
17. `test_enum_fields` - Verify Mapped[AffiliationEnum] not Mapped[str]

**Relationships (4 tests):**
18. `test_booking_approvals_relationship` - Access booking.approvals
19. `test_booking_timeline_relationship` - Access booking.timeline_events
20. `test_approval_booking_backref` - Access approval.booking
21. `test_timeline_booking_backref` - Access timeline_event.booking

**BR-001: Compute Total Days (5 tests):**
22. `test_compute_total_days_same_day` - Jan 1-1 = 1 day
23. `test_compute_total_days_multi_day` - Jan 1-5 = 5 days (not 4)
24. `test_compute_total_days_month_boundary` - Jan 30-Feb 2 = 4 days
25. `test_compute_total_days_leap_year` - Feb 28-29 (2024) = 2 days
26. `test_compute_total_days_year_boundary` - Dec 30-Jan 3 = 5 days

**Model Indexes (3 tests):**
27. `test_booking_indexes_match_migration` - Verify all 4 indexes defined
28. `test_approval_indexes_match_migration` - Verify all 3 indexes defined
29. `test_timeline_indexes_match_migration` - Verify all 2 indexes defined

**TOTAL: ~29 tests for US-1.2**

---

**Gherkin Scenarios:**

```gherkin
Feature: SQLAlchemy Models

  Scenario: Booking model has correct type hints
    Given I import the Booking model
    When I inspect its attributes
    Then I should see:
      | attribute            | type                  |
      | id                   | Mapped[UUID]          |
      | start_date           | Mapped[date]          |
      | end_date             | Mapped[date]          |
      | total_days           | Mapped[int]           |
      | party_size           | Mapped[int]           |
      | affiliation          | Mapped[AffiliationEnum] |
      | requester_first_name | Mapped[str]           |
      | requester_email      | Mapped[str]           |
      | description          | Mapped[str | None]    |
      | status               | Mapped[StatusEnum]    |

  Scenario: String constraints match migration (prevents schema drift)
    Given I inspect Booking model column definitions
    Then I should see:
      | column               | type         |
      | requester_first_name | String(40)   |
      | requester_email      | String(254)  |
      | description          | String(500)  |
    And these should match migration exactly

  Scenario: BR-001 - Compute total days (inclusive end date)
    Given a Booking instance with start_date=2025-01-01, end_date=2025-01-05
    When I call booking.compute_total_days()
    Then it should return 5 (not 4)
    Because the end date is inclusive (days: 1, 2, 3, 4, 5)

  Scenario: Relationships work correctly
    Given a booking exists with 3 approvals
    When I access booking.approvals
    Then I should get a list of 3 Approval objects
    And no additional database queries should be made (eager loading)

  Scenario: Cascade delete works
    Given a booking exists with 3 approvals and 2 timeline events
    When I delete the booking via session.delete(booking)
    Then the approvals should also be deleted
    And the timeline events should also be deleted
```

---

### US-1.3: Repository Pattern (Booking Repository)

**As a** developer
**I want** a repository layer for booking data access
**So that** business logic is separated from database queries and N+1 problems are avoided

---

**Applicable Business Rules:**

- **BR-001** (Inclusive end date): Multi-month bookings detected in calendar
  - *Why:* Booking Jan 15-Mar 15 must appear in Jan, Feb, AND Mar calendars.

- **BR-002** (No overlaps): `check_conflicts()` queries Pending/Confirmed only
  - *Why:* Denied/Canceled bookings don't block dates. Must check status explicitly.

- **BR-004** (Denied not public): `list_for_calendar()` excludes Denied bookings
  - *Why:* Privacy requirement. Public calendar shows Pending/Confirmed only.

- **BR-023** (Ordering): All list methods sort by `last_activity_at DESC`
  - *Why:* Most recent activity first, not oldest created. Critical for UX.

- **BR-023** (N+1 Prevention): Use `selectinload(Booking.approvals)` for eager loading
  - *Why:* Without eager loading, 10 bookings = 11 queries (1 + 10). With: 1-2 queries.

- **BR-024/BR-029** (Concurrency): Repository methods support SELECT FOR UPDATE
  - *Why:* Row-level locking for approval operations and conflict checks.

---

**Critical Edge Cases from Phase 1 Implementation:**

**CRITICAL: Multi-Month Overlap Detection**

**WRONG Implementation (Issue #5):**
```python
# Only finds bookings STARTING in month
extract("month", Booking.start_date) == month
```

**Example that breaks:**
- Booking: Jan 15 - Mar 15
- Query: `list_for_calendar(month=2, year=2025)` (February)
- Result: NOT SHOWN ❌
- Expected: SHOULD BE SHOWN ✅ (overlaps with Feb)

**CORRECT Implementation:**
```python
# Finds ALL overlapping bookings
month_start = date(year, month, 1)
_, last_day = monthrange(year, month)
month_end = date(year, month, last_day)

Booking.start_date <= month_end,  # Starts on or before month end
Booking.end_date >= month_start,  # Ends on or after month start
```

**This edge case MUST be tested explicitly!**

---

**Granular Acceptance Criteria:**

CRUD Operations:
- [ ] `create(booking)` inserts and returns booking with ID
- [ ] `get(booking_id)` returns booking or None
- [ ] `get_with_approvals(booking_id)` eager loads approvals
- [ ] `update(booking)` persists changes
- [ ] `delete(booking)` removes booking (cascades to approvals/timeline)

Calendar Filtering (CRITICAL):
- [ ] `list_for_calendar(month, year)` includes single-month bookings
- [ ] `list_for_calendar(month, year)` includes multi-month bookings (Jan 15-Mar 15 in Feb)
- [ ] `list_for_calendar(month, year)` includes month-boundary bookings (Jan 31-Feb 1)
- [ ] `list_for_calendar(month, year)` filters to Pending/Confirmed only (BR-004)
- [ ] `list_for_calendar(month, year)` eager loads approvals (no N+1)
- [ ] `list_for_calendar(month, year)` sorts by start_date ASC (chronological)

Conflict Detection:
- [ ] `check_conflicts()` detects exact match (Aug 1-5 conflicts with Aug 1-5)
- [ ] `check_conflicts()` detects partial overlap start (Aug 3-8 conflicts with Aug 1-5)
- [ ] `check_conflicts()` detects partial overlap end (Jul 28-Aug 2 conflicts with Aug 1-5)
- [ ] `check_conflicts()` detects enclosure (Aug 2-4 conflicts with Aug 1-5)
- [ ] `check_conflicts()` ignores Denied bookings (BR-002)
- [ ] `check_conflicts()` ignores Canceled bookings (BR-002)
- [ ] `check_conflicts()` excludes specific booking ID (for edit operations)

Requester Queries:
- [ ] `list_by_requester_email()` returns all bookings for email
- [ ] `list_by_requester_email()` sorts by `last_activity_at DESC` (BR-023)
- [ ] `list_by_requester_email()` includes all statuses

Performance:
- [ ] No N+1 queries when accessing approvals (use `selectinload()`)
- [ ] Calendar query uses GiST index for date range overlap
- [ ] All list methods use appropriate indexes (last_activity_at, status, requester_email)

---

**Complete Test Plan:**

**CRUD Operations (5 tests):**
1. `test_create_booking` - Create returns booking with ID
2. `test_get_booking_by_id` - Get returns correct booking
3. `test_get_nonexistent_returns_none` - Get returns None for invalid ID
4. `test_update_booking` - Update persists changes
5. `test_delete_booking_cascades` - Delete removes booking and related records

**Calendar Filtering (CRITICAL - 8 tests):**
6. `test_calendar_single_month_booking` - Feb 10-15 appears in Feb only
7. `test_calendar_multi_month_booking` - Jan 15-Mar 15 appears in Jan, Feb, AND Mar
8. `test_calendar_month_boundary` - Jan 31-Feb 1 appears in Jan AND Feb
9. `test_calendar_excludes_denied` - Denied booking not shown (BR-004)
10. `test_calendar_excludes_canceled` - Canceled booking not shown
11. `test_calendar_includes_pending` - Pending booking shown
12. `test_calendar_includes_confirmed` - Confirmed booking shown
13. `test_calendar_eager_loads_approvals` - No N+1 queries

**Conflict Detection (7 tests):**
14. `test_conflict_exact_match` - Aug 1-5 conflicts with Aug 1-5
15. `test_conflict_partial_start` - Aug 3-8 conflicts with Aug 1-5
16. `test_conflict_partial_end` - Jul 28-Aug 2 conflicts with Aug 1-5
17. `test_conflict_enclosure` - Aug 2-4 conflicts with Aug 1-5
18. `test_no_conflict_denied` - Denied booking doesn't conflict
19. `test_no_conflict_canceled` - Canceled booking doesn't conflict
20. `test_conflict_excludes_booking_id` - Exclude specific booking for edits

**Ordering per BR-023 (2 tests):**
21. `test_list_by_email_ordered_by_last_activity` - Most recent activity first
22. `test_ordering_not_created_at` - Verify NOT using created_at

**Eager Loading (2 tests):**
23. `test_get_with_approvals_eager_loads` - Single query for booking + approvals
24. `test_no_n_plus_1_in_calendar` - Calendar list avoids N+1 queries

**TOTAL: ~24 tests for US-1.3 (Booking Repository)**

---

**Gherkin Scenarios:**

```gherkin
Feature: Booking Repository

  Scenario: Create booking
    Given a BookingRepository instance
    When I call repository.create(booking_instance)
    Then a new booking should be inserted
    And it should return the created booking with ID

  Scenario: CRITICAL - Multi-month booking appears in all months
    Given a booking exists from 2025-01-15 to 2025-03-15
    When I call repository.list_for_calendar(month=1, year=2025)
    Then the booking should be included
    When I call repository.list_for_calendar(month=2, year=2025)
    Then the booking should be included
    When I call repository.list_for_calendar(month=3, year=2025)
    Then the booking should be included
    When I call repository.list_for_calendar(month=4, year=2025)
    Then the booking should NOT be included

  Scenario: CRITICAL - Month boundary bookings appear in both months
    Given a booking exists from 2025-01-31 to 2025-02-01
    When I call repository.list_for_calendar(month=1, year=2025)
    Then the booking should be included
    When I call repository.list_for_calendar(month=2, year=2025)
    Then the booking should be included

  Scenario: BR-004 - Denied bookings hidden from calendar
    Given a Denied booking exists from 2025-08-01 to 2025-08-05
    When I call repository.list_for_calendar(month=8, year=2025)
    Then the booking should NOT be included

  Scenario: BR-002 - Conflict detection ignores Denied bookings
    Given a Denied booking exists from 2025-08-01 to 2025-08-05
    When I call repository.check_conflicts(start=2025-08-01, end=2025-08-05)
    Then no conflicts should be returned

  Scenario: BR-023 - Ordering by last_activity_at DESC
    Given booking A created first, booking B created second
    And booking A updated (now has most recent activity)
    When I call repository.list_by_requester_email(email)
    Then booking A should be first in the list
    And booking B should be second

  Scenario: N+1 query prevention
    Given 10 bookings exist with 3 approvals each
    When I call repository.list_for_calendar(month=8, year=2025)
    And access booking.approvals for each result
    Then total queries should be ≤2 (not 11)
```

---

### US-1.4: Repository Pattern (Approval Repository)

**As a** developer
**I want** a repository layer for approval data access
**So that** approver queries are efficient and return correct types

---

**Applicable Business Rules:**

- **BR-023** (Outstanding List): Outstanding = NoResponse decision + Pending status only
  - *Why:* Approvers only act on items awaiting their decision.

- **BR-023** (History List): History = all statuses, all decisions for this party
  - *Why:* Read-only view of everything they've been involved in.

- **BR-023** (Ordering): Both lists sort by `last_activity_at DESC`
  - *Why:* Most recently active items first (not oldest created).

---

**Critical Issues from Phase 1 Implementation:**

**Issue #6: Wrong Return Type (MAJOR)**

**WRONG Implementation:**
```python
async def list_pending_for_party(...) -> Sequence[Approval]:
    result = await self.session.execute(
        select(Approval).where(...)  # Returns Approval!
    )
```

**Problem:** Frontend needs booking info (dates, requester, status), not just approval decision.

**CORRECT Implementation:**
```python
async def list_pending_for_party(...) -> Sequence[Booking]:
    result = await self.session.execute(
        select(Booking).join(Approval).where(...)  # Returns Booking!
    )
```

**Issue #7: Missing History Method**

**WRONG:** No `list_history_for_party()` method exists

**CORRECT:** Implement method returning all bookings for party (all statuses)

**Issue #8: Missing Status Filter**

**WRONG:**
```python
# Only filters by decision, not status
Approval.decision == DecisionEnum.NO_RESPONSE
```

**CORRECT:**
```python
# Must ALSO filter status
Approval.decision == DecisionEnum.NO_RESPONSE,
Booking.status == StatusEnum.PENDING  # Critical!
```

---

**Granular Acceptance Criteria:**

CRUD Operations:
- [ ] `create(approval)` inserts and returns approval with ID
- [ ] `get(approval_id)` returns approval or None
- [ ] `get_by_booking_and_party()` returns specific approval
- [ ] `list_by_booking()` returns all 3 approvals for booking
- [ ] `update(approval)` persists changes

Outstanding List (CRITICAL):
- [ ] `list_pending_for_party()` returns `Sequence[Booking]` NOT `Sequence[Approval]`
- [ ] Filters by `Approval.decision == NoResponse`
- [ ] Filters by `Booking.status == Pending` (Issue #8 fix)
- [ ] Sorts by `Booking.last_activity_at DESC` (not `Approval.id`)
- [ ] Eager loads approvals with `selectinload(Booking.approvals)`
- [ ] Does NOT include Confirmed/Denied/Canceled bookings

History List (CRITICAL):
- [ ] `list_history_for_party()` method exists (Issue #7 fix)
- [ ] Returns `Sequence[Booking]` NOT `Sequence[Approval]`
- [ ] Includes ALL statuses (Pending, Confirmed, Denied, Canceled)
- [ ] Sorts by `Booking.last_activity_at DESC`
- [ ] Eager loads approvals
- [ ] Read-only view (no filtering by decision)

Performance:
- [ ] No N+1 queries when accessing approvals
- [ ] Uses composite index on (party, decision)

---

**Complete Test Plan:**

**CRUD Operations (5 tests):**
1. `test_create_approval` - Create returns approval with ID
2. `test_get_approval_by_id` - Get returns correct approval
3. `test_get_by_booking_and_party` - Get specific approval
4. `test_list_by_booking` - Returns all 3 approvals
5. `test_update_approval` - Update persists changes

**Pending List (CRITICAL - 7 tests):**
6. `test_pending_returns_bookings_not_approvals` - Type is Booking
7. `test_pending_filters_by_no_response` - Only NoResponse included
8. `test_pending_filters_by_status_pending` - Only Pending status included
9. `test_pending_excludes_confirmed` - Confirmed status excluded
10. `test_pending_orders_by_last_activity` - Most recent first
11. `test_pending_eager_loads_approvals` - No N+1 queries
12. `test_pending_respects_limit` - Limit parameter works

**History List (CRITICAL - 6 tests):**
13. `test_history_method_exists` - Method is callable
14. `test_history_returns_bookings_not_approvals` - Type is Booking
15. `test_history_includes_all_statuses` - Pending, Confirmed, Denied, Canceled all included
16. `test_history_orders_by_last_activity` - Most recent first
17. `test_history_eager_loads_approvals` - No N+1 queries
18. `test_history_respects_limit` - Limit parameter works

**TOTAL: ~18 tests for US-1.4 (Approval Repository)**

---

**Gherkin Scenarios:**

```gherkin
Feature: Approval Repository

  Scenario: CRITICAL - Pending list returns Booking instances
    Given Ingeborg has 3 bookings awaiting her decision
    When I call repository.list_pending_for_party(AffiliationEnum.INGEBORG)
    Then I should receive a list of 3 Booking objects
    And NOT Approval objects

  Scenario: CRITICAL - Pending list filters by status=Pending
    Given a booking exists with status=Confirmed and Cornelia decision=NoResponse
    When I call repository.list_pending_for_party(AffiliationEnum.CORNELIA)
    Then the booking should NOT be included
    Because status is Confirmed, not Pending

  Scenario: CRITICAL - History method exists and returns all statuses
    Given bookings exist with statuses: Pending, Confirmed, Denied, Canceled
    And all involve Angelika
    When I call repository.list_history_for_party(AffiliationEnum.ANGELIKA)
    Then I should receive all 4 bookings
    And they should be ordered by last_activity_at DESC

  Scenario: BR-023 - Ordering by last_activity_at
    Given booking A has last_activity_at = yesterday
    And booking B has last_activity_at = today
    When I call repository.list_pending_for_party(party)
    Then booking B should be first
    And booking A should be second

  Scenario: N+1 query prevention
    Given 10 pending bookings for Ingeborg
    When I call repository.list_pending_for_party(AffiliationEnum.INGEBORG)
    And access booking.approvals for each result
    Then total queries should be ≤2 (not 11)
```

---

## Definition of Done

**For ALL user stories:**

Pre-Implementation:
- [ ] Pre-implementation checklist completed (BRs, edge cases identified)
- [ ] German copy sources identified (if applicable)

Test-First (TDD):
- [ ] All tests written FIRST (before implementation)
- [ ] Tests initially FAILED (verified)
- [ ] Tests reviewed for completeness (Step 3 - four-eyes principle)

Implementation:
- [ ] All tests now PASS
- [ ] Type checks pass (`mypy api/`)
- [ ] Linting passes (`ruff check api/`)
- [ ] Code coverage ≥80%

Schema Verification:
- [ ] Migration runs successfully: `alembic upgrade head`
- [ ] All 4 tables exist: bookings, approvals, timeline_events, approver_parties
- [ ] All 3 enums exist: affiliation_enum, status_enum, decision_enum
- [ ] String length constraints match migration (no schema drift)
- [ ] Check constraints enforced at database level
- [ ] All 9 indexes created correctly
- [ ] Seed data present (3 approver_parties rows)

Model Verification:
- [ ] All models have type hints (`Mapped[type]`)
- [ ] String constraints match migration exactly
- [ ] Relationships work (booking ↔ approvals ↔ timeline)
- [ ] `compute_total_days()` returns correct value (BR-001)
- [ ] Indexes match migration (DESC pattern consistent)

Repository Verification:
- [ ] CRUD operations work (create, get, update, delete)
- [ ] Multi-month calendar filtering works (Jan 15-Mar 15 in Feb) ✅
- [ ] Conflict detection excludes Denied/Canceled (BR-002, BR-004) ✅
- [ ] Ordering uses `last_activity_at DESC` (BR-023) ✅
- [ ] Pending list returns Booking not Approval (Issue #6 fix) ✅
- [ ] Pending list filters by status=Pending (Issue #8 fix) ✅
- [ ] History method exists and includes all statuses (Issue #7 fix) ✅
- [ ] No N+1 queries (eager loading with selectinload) ✅

Quality:
- [ ] Self-review completed
- [ ] No critical/major issues from review
- [ ] Documentation updated

---

## Testing Commands

```bash
# Run migrations
cd api
alembic upgrade head

# Verify schema
psql $DATABASE_URL -c "\dt"  # List tables
psql $DATABASE_URL -c "\d bookings"  # Describe bookings table
psql $DATABASE_URL -c "SELECT * FROM approver_parties;"  # Verify seed data

# Run unit tests
pytest tests/unit/test_models.py -v
pytest tests/unit/test_booking_repository.py -v
pytest tests/unit/test_approval_repository.py -v

# Run integration tests (requires PostgreSQL)
pytest tests/integration/test_schema.py -v

# Check coverage
pytest --cov=app.models --cov=app.repositories --cov-report=html

# Type checking
mypy api/app

# Linting
ruff check api/app
```

---

## Critical Learnings from Phase 1 Implementation

**These 9 issues would have been prevented by writing tests FIRST:**

1. ✅ **Schema Drift** (Issues #1-3): String length constraints missing in models
2. ✅ **Multi-Month Overlap** (Issue #4): Calendar filtering logic wrong
3. ✅ **Wrong Ordering** (Issue #5): Used `created_at` instead of `last_activity_at`
4. ✅ **Wrong Return Type** (Issue #6): Pending list returned Approval not Booking
5. ✅ **Missing Method** (Issue #7): History query not implemented
6. ✅ **Missing Status Filter** (Issue #8): Pending list didn't check booking.status
7. ✅ **N+1 Queries** (Issue #8): Missing eager loading
8. ✅ **Index Inconsistency** (Issue #9): DESC index pattern not consistent

**See `/docs/implementation/phase-1-critical-fixes.md` for detailed analysis.**

**Conclusion:** Test-first development with test review (Step 3) prevents all these issues.

---

## Next Phase

✅ Data Layer complete → [Phase 2: Booking API](phase-2-booking-api.md)

**Before starting Phase 2:**
1. Verify all 89 Phase 1 tests pass
2. Confirm database schema matches migration exactly
3. Run mypy and ruff with zero errors
4. Review critical fixes document to understand what went wrong and why
