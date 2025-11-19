# Implementation - CLAUDE Guide

## What's in This Section

BDD (Behavior-Driven Development) implementation roadmap:
- **README.md** - 8-phase overview, BDD workflow, testing strategy
- **phase-0-foundation.md** - Project scaffolding, tools, CI/CD
- **phase-1-data-layer.md** - Database schema, models, repositories
- **phase-2-booking-api.md** - Create, read, update booking endpoints
- **phase-3-approval-flow.md** - Approve, deny, confirm logic
- **phase-4-email-integration.md** - Notification system with Resend
- **phase-5-frontend-calendar.md** - Calendar UI, booking display
- **phase-6-frontend-booking.md** - Create/edit forms, validation
- **phase-7-approver-interface.md** - Approver overview, actions
- **phase-8-polish.md** - Performance, accessibility, deployment

## Start Here

**Read `README.md` first** for the BDD workflow and overall approach.

**Then start with Phase 0** - don't skip ahead.

---

## 🚨 CRITICAL: STRICT TDD WORKFLOW (Test-First)

**THIS IS MANDATORY. DO NOT SKIP ANY STEP.**

### **Phase 1 Lessons Learned:**

We discovered 17 issues in Phase 1 implementation because tests were written AFTER code. This led to:
- Missing String length constraints (schema drift)
- Wrong business logic (calendar filtering, ordering)
- Missing methods (history query)
- Incorrect return types (Approval instead of Booking)

**Root cause:** Implementation came first, tests came second, bugs were invisible.

**Solution:** STRICT TEST-FIRST DEVELOPMENT with FOUR-EYES TEST REVIEW (below)

---

## Mandatory Implementation Workflow (7 Steps with Role Separation)

**Different perspectives at each step ensure comprehensive quality:**

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Pre-Implementation Check                            │
│ 🎭 Role: Requirements Analyst                               │
│ Output: Complete list of BRs, edge cases, German copy       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 2: Write Test Specifications                           │
│ 🎭 Role: Senior Test Engineer                               │
│ Output: Comprehensive test suite (must fail initially)      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Review Tests for Completeness ⚠️ CRITICAL           │
│ 🎭 Role: Senior Architect/Developer                         │
│ Output: Verified test coverage (gaps identified & fixed)    │
│ ↻ Loop back to Step 2 if gaps found                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 4: Implement Code                                      │
│ 🎭 Role: Implementation Specialist                          │
│ Output: Code that makes tests pass                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 5: Verify Tests Pass                                   │
│ 🎭 Role: Quality Assurance                                  │
│ Output: All tests green, type checks pass, linting clean    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 6: Final Code Review                                   │
│ 🎭 Role: Critical Senior Developer                          │
│ Output: Code verified against all requirements              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ Step 7: Commit and Push                                     │
│ Output: Clean commit with comprehensive message             │
└─────────────────────────────────────────────────────────────┘
```

**Key Innovation: Step 3 (Four-Eyes Test Review)**
- Prevents fixing BOTH tests AND code later
- Catches test gaps BEFORE implementation
- Higher likelihood of correct implementation on first try

---

### **Step 1: Pre-Implementation Check (REQUIRED)**

**🎭 Role: Requirements Analyst** - Gather ALL requirements comprehensively

**Before writing ANY code or tests, complete this checklist:**

- [ ] **Read the user story completely**
- [ ] **Identify ALL applicable business rules** (search `docs/foundation/business-rules.md`)
  - List them explicitly: BR-001, BR-002, BR-023, etc.
  - For EACH BR, understand what it requires
- [ ] **Identify ALL German copy requirements**
  - Check `docs/specification/notifications.md` for emails
  - Check `docs/specification/error-handling.md` for error messages
  - Check `docs/specification/ui-screens.md` for UI text
- [ ] **Identify ALL relevant data model fields**
  - Check `docs/design/database-schema.md`
  - Check `docs/specification/data-model.md`
- [ ] **List ALL edge cases** that must be tested:
  - Date boundaries (inclusive end dates per BR-001)
  - Overlapping bookings (multi-month spans)
  - Concurrent actions (BR-024, BR-029)
  - Empty states, max values, invalid inputs
- [ ] **Verify completeness**: Ask yourself:
  - "Is there any other BR that might apply here?"
  - "What edge cases am I missing?"
  - "What could go wrong?"

**DO NOT PROCEED until this checklist is 100% complete.**

If anything is unclear, **ASK THE USER** - do not assume or improvise.

---

### **Step 2: Write Test Specifications (BEFORE Code)**

**🎭 Role: Senior Test Engineer** - Focus on comprehensive test coverage

**For each user story, define COMPLETE test coverage:**

#### **A. List ALL Test Cases**

Create a test plan with:
1. **Happy path tests** (basic functionality)
2. **Business rule tests** (one per BR)
3. **Edge case tests** (boundaries, empty states, max values)
4. **Error case tests** (validation failures, conflicts)
5. **Schema validation tests** (models match migration)
6. **Performance tests** (N+1 queries, eager loading)

**Example (from Phase 1 learnings):**

```markdown
**Test Plan for BookingRepository.list_for_calendar():**

1. test_calendar_shows_bookings_starting_in_month (happy path)
2. test_calendar_shows_multi_month_bookings (EDGE CASE - critical!)
3. test_calendar_excludes_denied_bookings (BR-004)
4. test_calendar_includes_pending_and_confirmed_only (BR filtering)
5. test_calendar_eager_loads_approvals (N+1 prevention)
6. test_calendar_ordering (should be by start_date, then last_activity_at)
```

**Why this matters:** Without test #2, the multi-month booking bug was invisible.

#### **B. Write Failing Tests in Code**

Translate your test plan into actual pytest/Playwright tests:

```python
@pytest.mark.asyncio
async def test_calendar_shows_multi_month_bookings(booking_repo):
    """
    EDGE CASE: Booking from Jan 15-Mar 15 must appear in Feb calendar.
    Tests BR-002 overlap detection logic.
    """
    booking = await booking_repo.create(
        start_date=date(2025, 1, 15),
        end_date=date(2025, 3, 15),
        status=StatusEnum.PENDING,
        # ... other fields
    )

    # Query February 2025 calendar
    results = await booking_repo.list_for_calendar(month=2, year=2025)

    # MUST include this booking (overlaps February)
    assert booking.id in [b.id for b in results], \
        "Multi-month booking must appear in overlapping month"
```

**Requirements for tests:**
- **Specific assertions** - not just `assert result`, but `assert result.field == expected_value`
- **Business rule references** - comment with "Tests BR-XXX"
- **Edge case documentation** - explain WHY this test exists
- **Complete coverage** - test ALL acceptance criteria, not just happy path

#### **C. Verify Tests Fail**

Run tests and **confirm they fail**:

```bash
pytest tests/unit/test_booking_repository.py::test_calendar_shows_multi_month_bookings -v
```

**Expected:** `FAILED` (because code doesn't exist yet)

**If test passes:** Your test is wrong or incomplete. Fix it before proceeding.

---

### **Step 3: Review Tests for Completeness (CRITICAL - Four-Eyes Principle)**

**🎭 Role: Senior Architect/Developer** - Verify tests comprehensively cover all requirements

**STOP. Before implementing ANY code, review the tests you just wrote.**

**This step prevents the need to change BOTH tests AND code later. Catch gaps now.**

#### **Test Review Checklist:**

Cross-reference tests against Step 1 (Pre-Implementation Checklist):

- [ ] **Every BR from Step 1 has at least one test**
  - Go through your BR list: BR-001, BR-002, etc.
  - For EACH BR, verify: "Which test validates this BR?"
  - If no test exists for a BR, ADD IT NOW

- [ ] **Every edge case from Step 1 has a test**
  - Date boundaries? ✓ Test exists
  - Multi-month overlaps? ✓ Test exists
  - Concurrent actions? ✓ Test exists
  - Empty states, max values? ✓ Tests exist

- [ ] **Every acceptance criterion has a test**
  - Go through the user story's acceptance criteria checkboxes
  - For EACH checkbox, verify: "Which test validates this?"
  - If no test exists for a criterion, ADD IT NOW

- [ ] **Every German copy string has a test**
  - Error messages validated in tests
  - Success messages validated in tests
  - Exact wording verified (not just "error occurs")

- [ ] **Schema validation tests exist** (if data layer work)
  - String length constraints match migration
  - Nullable/non-nullable correct
  - Foreign keys, indexes present

- [ ] **Performance tests exist** (if query work)
  - N+1 query prevention verified
  - Eager loading tested
  - Index usage verified

- [ ] **Concurrency tests exist** (if BR-024 or BR-029 apply)
  - Race conditions tested
  - SELECT FOR UPDATE verified
  - First-wins behavior tested

#### **Ask Yourself:**

1. "If I run these tests and they all pass, am I 100% confident the implementation is correct?"
2. "What could still go wrong even if these tests pass?"
3. "Are there any gaps between the requirements (Step 1) and the tests (Step 2)?"

#### **If Gaps Found:**

**DO NOT PROCEED TO IMPLEMENTATION.**

1. Add missing tests to Step 2
2. Update test plan documentation
3. Verify new tests fail
4. Return to this checklist and verify completeness again

#### **Only When:**

- [ ] All Step 1 requirements have corresponding tests
- [ ] All edge cases have tests
- [ ] All acceptance criteria have tests
- [ ] No gaps identified

**THEN proceed to Step 4 (Implementation).**

---

### **Step 4: Implement Code (Until Tests Pass)**

**🎭 Role: Implementation Specialist** - Write code to make tests pass

**Now and only now, write implementation code.**

**Rules:**
- Reference business rules in code comments: `# Per BR-001: inclusive end date`
- Use exact German copy from specifications (no paraphrasing)
- Match data types exactly (String(254) not String, Text() not String(500))
- Implement ALL methods listed in acceptance criteria

**Example:**

```python
async def list_for_calendar(
    self, month: int, year: int
) -> Sequence[Booking]:
    """
    List bookings overlapping with the specified month.

    Business Rules:
    - BR-002: Show bookings that overlap month range (not just starting in month)
    - BR-023: Sorted by start_date, then last_activity_at

    Returns: Bookings with status Pending or Confirmed only.
    """
    # Calculate month date range (per BR-001: inclusive dates)
    month_start = date(year, month, 1)
    _, last_day = monthrange(year, month)
    month_end = date(year, month, last_day)

    # Overlap logic: start <= month_end AND end >= month_start
    result = await self.session.execute(
        select(Booking)
        .where(
            and_(
                Booking.start_date <= month_end,     # Starts before/during month
                Booking.end_date >= month_start,     # Ends during/after month
                Booking.status.in_([StatusEnum.PENDING, StatusEnum.CONFIRMED]),
            )
        )
        .options(selectinload(Booking.approvals))  # Prevent N+1 queries
        .order_by(Booking.start_date, Booking.last_activity_at.desc())
    )
    return result.scalars().all()
```

---

### **Step 5: Verify Tests Pass**

**🎭 Role: Quality Assurance** - Ensure all quality gates pass

Run the full test suite:

```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Type checking
mypy app/
python -m mypy app/  # If mypy.ini has issues

# Linting
ruff check app/
```

**ALL tests must pass.** If any fail, fix the code (not the tests).

---

### **Step 6: Final Code Review (Self-Review)**

**🎭 Role: Critical Senior Developer** - Final verification before commit

**Before committing, review your own code one final time:**

Ask yourself:
- [ ] Do all String columns specify length constraints matching migration?
- [ ] Are all business rules correctly implemented?
- [ ] Is the ordering correct (last_activity_at DESC per BR-023)?
- [ ] Are there N+1 query problems (missing selectinload)?
- [ ] Are return types correct (Booking not Approval)?
- [ ] Is all German copy exact from specifications?
- [ ] Are all edge cases handled?
- [ ] Did I follow the exact patterns from the test review (Step 3)?

**If unsure, ask the user for a review before proceeding.**

---

### **Step 7: Commit and Push**

```bash
git add .
git commit -m "feat(phase-X): implement US-X.Y with full test coverage"
git push -u origin <branch>
```

---

## Why This Process Matters

### **Without TDD (What Happened in Phase 1):**

1. Wrote migration with `String(254)`
2. Wrote model with `Mapped[str]` (no length)
3. Wrote repository with wrong filtering logic
4. Tests would have caught these... but tests were written last
5. Tests passed because they tested the WRONG implementation
6. 17 issues found only during manual code review

### **With TDD but Without Test Review:**

1. Write tests based on understanding
2. Miss edge case (multi-month booking overlap)
3. Implement code
4. Tests pass, but edge case not covered
5. Bug found in production or late review
6. Must fix BOTH tests AND code

### **With This Process (7-Step TDD with Four-Eyes Test Review):**

1. **Step 1 (Requirements Analyst):** Identify BR-002 (multi-month overlaps must be detected)
2. **Step 2 (Test Engineer):** Write tests for basic conflict detection
3. **Step 3 (Architect Review):** "Wait, BR-002 says multi-month overlaps. Where's the test for Jan 15-Mar 15 overlapping Feb 1-28?"
4. **Step 3 (Loop back):** Add missing test: `test_conflict_multi_month`
5. **Step 3 (Verify):** All BRs covered, proceed to implementation
6. **Step 4 (Implementation):** Write code to pass ALL tests (including the multi-month one)
7. **Steps 5-7:** Verify, review, commit

**Result:** Bug impossible because test was added BEFORE implementation.

**TDD + Test Review makes bugs impossible, not just unlikely.**

## Phase Dependencies

```
Phase 0 (Foundation)
    ↓
Phase 1 (Data Layer)
    ↓
Phase 2 (Booking API) ←─┐
    ↓                    │
Phase 3 (Approval Flow)  │
    ↓                    │
Phase 4 (Email) ─────────┘
    ↓
Phase 5 (Web Calendar)
    ↓
Phase 6 (Web Booking)
    ↓
Phase 7 (Approver Interface)
    ↓
Phase 8 (Polish & Production)
```

**Don't skip phases** - each builds on previous.

---

## Per-Phase Traceability Requirements

**EVERY user story must include:**

### **1. Business Rule References**

List ALL applicable BRs at the start of each user story:

```markdown
### US-X.Y: Feature Name

**Applicable Business Rules:**
- **BR-001**: Inclusive end date (End - Start + 1 days)
- **BR-002**: No overlaps with Pending/Confirmed bookings
- **BR-023**: Lists sorted by LastActivityAt DESC
- **BR-029**: First-write-wins for create/extend

**Why these BRs matter:**
- BR-001: Affects total_days calculation in booking creation
- BR-002: Must check conflicts before allowing booking
- BR-023: All repository list methods must use this ordering
- BR-029: Must use transactions with SELECT FOR UPDATE
```

### **2. Granular Acceptance Criteria**

NOT vague: ✗ "Models match database schema"

INSTEAD granular: ✓ "Every String column specifies max_length matching migration"

**Example:**

```markdown
**Granular Acceptance Criteria:**
- [ ] Booking.requester_email is String(254), not unlimited Text
- [ ] Booking.description is String(500), nullable
- [ ] TimelineEvent.note is Text() (unlimited), nullable
- [ ] list_for_calendar() returns bookings overlapping month (not just starting in month)
- [ ] list_pending_for_party() returns Booking objects (not Approval objects)
- [ ] list_pending_for_party() filters by booking.status = Pending
- [ ] All list methods use last_activity_at.desc() ordering per BR-023
- [ ] All list methods eager load relationships to prevent N+1 queries
```

### **3. Complete Test Plan**

For each user story, enumerate ALL tests to be written:

```markdown
**Required Tests:**

**Happy Path:**
1. test_create_booking_success - Basic booking creation works
2. test_get_booking_by_id - Retrieve existing booking

**Business Rules:**
3. test_total_days_inclusive (BR-001) - Jan 1-5 = 5 days, not 4
4. test_conflict_detection (BR-002) - Overlapping bookings rejected
5. test_ordering_by_last_activity (BR-023) - Results sorted correctly

**Edge Cases:**
6. test_multi_month_booking_appears_in_calendar - Booking from Jan 15-Mar 15 appears in Feb
7. test_same_day_booking - start_date = end_date = 1 day
8. test_max_party_size - party_size = 10 accepted, 11 rejected

**Schema Validation:**
9. test_model_string_lengths_match_migration - Programmatic check
10. test_indexes_exist - Verify performance indexes created

**Performance:**
11. test_no_n_plus_one_queries - Eager loading works
```

### **4. German Copy References**

Specify exact source of ALL German text:

```markdown
**German Copy Sources:**
- Error "überschneidet sich mit": `docs/specification/error-handling.md` line 45
- Email subject "Deine Buchungsanfrage": `docs/specification/notifications.md` line 123
- Button label "Zustimmen": `docs/specification/ui-screens.md` line 89
```

---

## Critical Testing Requirements

**Every phase must have:**
- [ ] **Pre-implementation checklist completed** (Step 1)
- [ ] **All test cases written BEFORE code** (Step 2)
- [ ] **Tests reviewed for completeness** (Step 3 - Four-Eyes Review)
- [ ] **Tests fail initially** (Step 2C)
- [ ] **Code implemented until tests pass** (Step 4)
- [ ] **Self-review completed** (Step 6)
- Gherkin scenarios (Given/When/Then)
- API tests (pytest)
- Web tests (playwright) if UI involved
- ≥80% code coverage target

**Run tests:**
```bash
# API
pytest tests/unit/ -v
pytest tests/integration/ -v

# Web
npx playwright test
npx playwright test --project="iPhone 8"

# Type checking
mypy app/
python -m mypy app/  # If mypy.ini has issues

# Linting
ruff check app/
```

## Definition of Done (Per Phase)

**Complete this checklist before considering phase done:**

- [ ] **Pre-implementation checklist completed** for all user stories (Step 1)
- [ ] **All tests written FIRST** (before implementation) (Step 2)
- [ ] **Tests reviewed for completeness** (Step 3 - Four-Eyes Review passed)
- [ ] All Gherkin scenarios pass
- [ ] All pytest tests pass (unit + integration)
- [ ] All Playwright tests pass (if frontend phase)
- [ ] Type checks pass (mypy + tsc)
- [ ] Linting passes (ruff + eslint)
- [ ] Code coverage ≥80%
- [ ] German copy matches specs EXACTLY (no paraphrasing)
- [ ] All business rules enforced and referenced in code
- [ ] Mobile tested (375px width minimum)
- [ ] Self-review completed (Step 5 checklist)
- [ ] All String columns have length constraints matching migration
- [ ] No N+1 query problems (eager loading used)
- [ ] Ordering uses last_activity_at DESC per BR-023 (where applicable)
- [ ] Documentation updated if needed

---

## User Story Template

**Use this template for all future user stories:**

```markdown
### US-X.Y: [Feature Name]

**As a** [role]
**I want** [feature]
**So that** [benefit]

---

**Applicable Business Rules:**
- **BR-XXX**: [Description] - [Why it matters for this story]
- **BR-YYY**: [Description] - [Why it matters for this story]

**German Copy Sources:**
- [Text snippet]: `docs/specification/[file].md` line XXX
- [Text snippet]: `docs/specification/[file].md` line YYY

**Data Model References:**
- Table: `[table_name]` - `docs/design/database-schema.md` line XXX
- Fields: [list fields involved]

---

**Granular Acceptance Criteria:**

Schema/Type Safety:
- [ ] [Specific constraint, e.g., "Booking.email is String(254)"]
- [ ] [Specific constraint]

Business Logic:
- [ ] [Specific behavior, e.g., "total_days = end - start + 1"]
- [ ] [Specific behavior]

Performance:
- [ ] [Specific requirement, e.g., "Eager load approvals with selectinload"]

---

**Complete Test Plan:**

Happy Path Tests:
1. test_[name] - [What it tests]

Business Rule Tests:
2. test_[name] (BR-XXX) - [What BR it verifies]

Edge Case Tests:
3. test_[name] - [What edge case]

Schema Validation Tests:
4. test_[name] - [What schema aspect]

Performance Tests:
5. test_[name] - [What performance aspect]

---

**Gherkin Scenarios:**

\`\`\`gherkin
Feature: [Feature Name]

  Scenario: [Happy path]
    Given [precondition]
    When [action]
    Then [expected result]

  Scenario: [Edge case - specify why important]
    Given [precondition]
    When [action]
    Then [expected result]

  Scenario: [BR-XXX validation]
    Given [precondition]
    When [action violating BR-XXX]
    Then [error response with German message]
\`\`\`

---

**Implementation Tasks:**
- [ ] Write ALL tests (listed above)
- [ ] Verify tests FAIL
- [ ] Implement [component/function]
- [ ] Implement [component/function]
- [ ] Verify ALL tests PASS
- [ ] Run mypy + ruff
- [ ] Self-review (Step 5 checklist)
- [ ] Commit and push

---

**Definition of Done:**
- [ ] All tests from test plan pass
- [ ] All acceptance criteria met
- [ ] All BRs enforced
- [ ] German copy exact from specs
- [ ] Code coverage ≥80%
- [ ] Self-review checklist completed
```

## Common Gotchas

**Phase 1 (Data Layer):**
- Don't forget indexes on date ranges
- Add CHECK constraints for validation
- Seed 3 approver parties

**Phase 2 (Booking API):**
- Check conflicts in transaction (BR-029)
- Calculate TotalDays correctly (BR-001)
- Never expose email in responses (privacy)

**Phase 3 (Approval Flow):**
- Use SELECT FOR UPDATE (BR-024)
- Check for self-approval (BR-015)
- Handle concurrent actions

**Phase 4 (Email):**
- Include tokens in all action links
- Retry 3 times with backoff (BR-022)
- Use exact German copy from notifications.md

**Phases 5-7 (Web):**
- Design for 375px first (mobile)
- 44×44pt tap targets
- No hover dependencies
- Use exact German copy from specs

---

## Phase-Specific Critical Implementation Guidance

### Phase 6: Web Booking Forms - Critical Gotchas

**Test Matrices Available:**
- `/docs/implementation/phase-6-test-matrix.md` - 44 E2E test specifications
- `/docs/implementation/phase-7-test-matrix.md` - 37-42 E2E test specifications

#### BR-005: Date Extend vs. Shorten Detection (MOST COMPLEX)

**Why this is critical:**
- Edit booking with date changes requires detecting if approvals should reset
- **Shorten** (within original bounds) → Approvals **KEEP**
- **Extend** (earlier start OR later end) → Approvals **RESET**
- Non-date changes (party size, affiliation, first name) → Approvals **KEEP**

**Common mistake:** Resetting approvals for shorten, keeping for extend (backwards logic)

**Correct implementation:**
```typescript
function detectDateChangeType(
  oldStart: Date,
  oldEnd: Date,
  newStart: Date,
  newEnd: Date
): 'SHORTENED' | 'EXTENDED' | 'SAME' {
  const startExtended = newStart < oldStart; // earlier = extended
  const endExtended = newEnd > oldEnd; // later = extended

  if (startExtended || endExtended) {
    return 'EXTENDED'; // Reset approvals per BR-005
  }

  return 'SHORTENED'; // Keep approvals per BR-005
}

// Examples:
// Old: Jan 1–10, New: Jan 3–8 → SHORTENED (keep approvals) ✓
// Old: Jan 1–10, New: Dec 31–10 → EXTENDED (reset approvals) ✓
// Old: Jan 1–10, New: Jan 1–20 → EXTENDED (reset approvals) ✓
```

**Test thoroughly:**
- Shorten start date (Jan 1–10 → Jan 3–10) = keep
- Shorten end date (Jan 1–10 → Jan 1–5) = keep
- Extend start earlier (Jan 1–10 → Dec 25–10) = reset
- Extend end later (Jan 1–10 → Jan 1–20) = reset
- Party size only change = keep (BR-025)
- First name only change = keep (BR-025)

---

#### BR-020: Link Detection Must Be Case-Insensitive

**Why this matters:**
- Users can type "HTTP://", "Www", "MAILTO:", etc.
- Validation must catch all variations to prevent spam/phishing

**Common mistake:** Using case-sensitive regex: `/http:\/\//`

**Correct implementation:**
```typescript
// ✓ CORRECT: Case-insensitive with 'i' flag
function hasBlockedURL(text: string): boolean {
  const patterns = [
    /http[s]?:\/\//i,  // Matches http://, https://, HTTP://, etc.
    /www\./i,          // Matches www., Www., WWW., etc.
    /mailto:/i         // Matches mailto:, MAILTO:, etc.
  ];
  return patterns.some(pattern => pattern.test(text));
}
```

**Applies to:** Description field (create/edit forms), Comment field (deny dialog)

---

#### Date Picker: Conflicts Must Refresh

**Why this matters:**
- While user has date picker open, another user can book conflicting dates
- Stale conflict data allows double-booking

**Solution:** Fetch conflicts on every month navigation, not just on form load

---

#### Mobile Date Picker: Don't Use Native `<input type="date">`

**Why this matters:**
- iOS/Android native date pickers don't support:
  - Date ranges (start + end)
  - Blocking specific dates (conflicts)
  - Visual conflict indicators

**Correct approach:** Build custom date picker (Shadcn Calendar or similar) with 44×44pt touch targets

---

### Phase 7: Approver Interface - Critical Gotchas

**Test Matrix Available:** `/docs/implementation/phase-7-test-matrix.md`

#### BR-023: Query Correctness is CRITICAL

**Why this is the #1 gotcha for Phase 7:**
- Wrong query = approvers see wrong data
- Missing approvals = broken approval flow

**Outstanding Tab Query (EXACT REQUIREMENTS):**
```sql
-- MUST filter by:
-- 1. booking.status = Pending
-- 2. approval.response = NoResponse (for this approver)
-- 3. Sort by booking.last_activity_at DESC

SELECT bookings.*
FROM bookings
JOIN approvals ON approvals.booking_id = bookings.id
WHERE bookings.status = 'Pending'
  AND approvals.party_id = :approver_party_id
  AND approvals.response = 'NoResponse'
ORDER BY bookings.last_activity_at DESC;
```

**History Tab Query (EXACT REQUIREMENTS):**
```sql
-- MUST include:
-- 1. All statuses (Pending, Confirmed, Denied - NOT Canceled)
-- 2. All approvals (regardless of response)
-- 3. Sort by booking.last_activity_at DESC

SELECT bookings.*
FROM bookings
JOIN approvals ON approvals.booking_id = bookings.id
WHERE bookings.status IN ('Pending', 'Confirmed', 'Denied')
  AND approvals.party_id = :approver_party_id
ORDER BY bookings.last_activity_at DESC;
```

**Common mistakes:**
- Outstanding includes Denied bookings (should exclude)
- Outstanding includes bookings where approver already responded (should be NoResponse only)
- History missing Denied bookings (should include)
- Wrong sort order (should be DESC, not ASC)

---

#### BR-024: Concurrency Tests Are Mandatory

**Why this matters:**
- Two approvers clicking approve/deny simultaneously WILL happen in production
- Without SELECT FOR UPDATE, race conditions corrupt data

**Correct backend pattern:**
```python
async def approve_booking(booking_id: int, approver_id: int):
    async with session.begin():
        # Lock booking row
        booking = await session.execute(
            select(Booking)
            .where(Booking.id == booking_id)
            .with_for_update()  # CRITICAL: Row-level lock
        ).scalar_one()

        # Check current state and update
        # ...
```

**Playwright concurrency test pattern:**
```typescript
test('concurrent approvals - first wins', async ({ page, context }) => {
  const page1 = page;
  const page2 = await context.newPage();

  // Navigate both to same booking
  await page1.goto('/approver?token=ingeborg_token');
  await page2.goto('/approver?token=cornelia_token');

  // Click approve simultaneously
  await Promise.all([
    page1.click('button:has-text("Zustimmen")'),
    page2.click('button:has-text("Zustimmen")')
  ]);

  // Verify: One success, one "Schon erledigt"
  // ...
});
```

**Must test scenarios:**
- Two simultaneous approves (first wins)
- Two simultaneous denies (first wins)
- Approve vs. deny simultaneously (first wins)

---

#### BR-010: Idempotency Edge Cases

**Why this matters:**
- Users retry failed clicks (slow network, app crash)
- Email links can be clicked multiple times
- Action must return same result every time

**Common mistake:** Returning error on second click instead of success

**Correct pattern:** Check state, return "Schon erledigt" success message (not error)

---

### Phase 8: Production Deployment - Critical Gotchas

#### Rate Limiting Must Be Server-Side

**Why this matters:**
- Client-side rate limiting can be bypassed
- Production security depends on server-side enforcement

**Correct approach:**
- Backend enforces all rate limits BEFORE database operations
- Track: 10 bookings/day per email, 30 requests/hour per IP (BR-012)
- Return German error messages with remaining time

---

#### Background Jobs: Timezone Handling

**Why this matters:**
- Jobs must run in Europe/Berlin timezone, not UTC
- Auto-cleanup at 00:01 Berlin time (BR-028)
- Weekly digest on Sunday 09:00 Berlin time (BR-009)

**Common mistake:** Scheduling jobs in UTC without conversion

**Correct approach:**
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

berlin_tz = pytz.timezone('Europe/Berlin')
scheduler = AsyncIOScheduler(timezone=berlin_tz)

# Auto-cleanup: Daily at 00:01 Europe/Berlin
scheduler.add_job(
    auto_cleanup_past_pending,
    CronTrigger(hour=0, minute=1, timezone=berlin_tz),
    id='auto_cleanup'
)
```

---

#### SELECT FOR UPDATE: Deadlock Prevention

**Why this matters:**
- If two transactions lock rows in different order → deadlock

**Correct pattern:** Always lock in consistent order (booking → approvals → parties)

---

#### Email Retry: Exponential Backoff Must Match Spec

**Why this matters:**
- BR-022 specifies exact delays: 2s, 4s, 8s
- Too short → overloads email service

**Correct implementation:**
```python
async def send_email_with_retry(email_data: dict, max_attempts: int = 3):
    delays = [2, 4, 8]  # Seconds between retries (BR-022)

    for attempt in range(max_attempts):
        try:
            await email_service.send(email_data)
            return  # Success
        except TransientError:
            if attempt < max_attempts - 1:
                await asyncio.sleep(delays[attempt])
            else:
                raise  # Failed after all attempts
```

**Must ensure:**
- Email content unchanged across retries (no mutations)
- Failed emails logged with correlation ID
- Exponential backoff matches spec exactly (2s, 4s, 8s)

---

## Parallel Work Opportunities

**Some overlap possible:**
- Phase 5-7 work on different UI areas
- Phase 4 can start while Phase 2-3 finish

**But maintain phase order for core dependencies.**

---

**Ready to start?** Begin with [`phase-0-foundation.md`](phase-0-foundation.md).
