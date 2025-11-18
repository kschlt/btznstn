# Phase 6: Web Booking - BR Analysis Summary

**Date:** 2025-11-17
**Phase:** Phase 6: Web Booking (Frontend Forms)
**User Stories:** US-6.1 (Create Form), US-6.2 (Date Picker), US-6.3 (Edit Booking)

---

## What You're Getting

This analysis package contains **three coordinated documents** to guide Phase 6 implementation:

### 1. **PHASE_6_BR_ANALYSIS.md** (Comprehensive Reference)
**Purpose:** Deep analysis of all business rules and their impact on Phase 6

**Contents:**
- Complete breakdown of 13 applicable BRs (BR-001, 002, 005, 011, 014–027)
- For each user story (US-6.1, 6.2, 6.3):
  - All applicable BRs with why they matter
  - Implementation impact on validation, UI, state management
  - Complete list of edge cases to test
  - Estimated test count per story
- German copy reference sheet (all error messages, success messages, dialog copy)
- Test data setup requirements
- Implementation checklist

**When to use:** During design phase and when you encounter questions about a specific BR or requirement

**Length:** ~850 lines; comprehensive but organized

---

### 2. **PHASE_6_TEST_MATRIX.md** (Visual Test Map)
**Purpose:** Structured test plan with traceability

**Contents:**
- 44 specific test cases organized into 6 groups:
  1. Form Creation & Submission (10 tests)
  2. Date Picker & Range Logic (10 tests)
  3. Conflict Detection & Error Handling (8 tests)
  4. Edit Booking - Approval Impact (8 tests)
  5. Reopen from Denied (4 tests)
  6. Mobile & Accessibility (4 tests)
- Complete BR-to-test traceability matrix
- Test data setup SQL
- Test response fixtures (JSON examples)
- Recommended test execution order
- GitHub/CI integration checklist

**When to use:** During test design and implementation; reference before writing each test

**Length:** ~350 lines; concise but complete

---

### 3. **PHASE_6_QUICK_REFERENCE.md** (Developer Checklist)
**Purpose:** Fast lookup for implementation decisions

**Contents:**
- Pre-implementation checklist (must complete before coding)
- 13 critical BRs in table format (rule → applies to → implementation → test example)
- Form field specifications with validation rules
- **Exact German copy** (can be copy-pasted directly into code):
  - All validation errors
  - All success messages
  - All dialog copy
- Code templates:
  - Zod validation schema
  - Date logic implementations (correct vs. incorrect examples)
  - React Hook Form usage
  - Playwright test template
- Mobile-first checklist
- Testing checklist
- Common mistakes to avoid
- Quick lookup table ("Which BR is this?" finder)

**When to use:** During implementation; keep open while coding

**Length:** ~450 lines; dense but scannable

---

## Key Findings

### 1. **13 Applicable Business Rules**

| BR | Title | Criticality | Applies To |
|:---|:------|:-----------|:----------|
| BR-001 | Inclusive end date (`TotalDays = End - Start + 1`) | 🔴 Critical | All |
| BR-002 | No overlaps with Pending/Confirmed | 🔴 Critical | Create, Edit |
| BR-005 | **Date extend resets approvals; shorten keeps** | 🔴 Critical | Edit only |
| BR-011 | **German-only UI** | 🔴 Critical | All |
| BR-014 | Past items read-only | 🟠 High | Edit |
| BR-016 | Party size "n Personen" format | 🟠 High | All |
| BR-017 | Party size range 1–10 | 🔴 Critical | All |
| BR-018 | Reopen guard (no conflicts) | 🟠 High | Edit/Reopen |
| BR-019 | First name validation | 🔴 Critical | All |
| BR-020 | Block URLs in Description | 🟠 High | All |
| BR-025 | First-name edit keeps approvals | 🟡 Medium | Edit |
| BR-026 | Future horizon ≤+18 months | 🔴 Critical | All |
| BR-027 | Long stay warning >7 days | 🟠 High | Create, Edit |

**Total:** 13 business rules directly applicable to Phase 6 forms

### 2. **Test Estimation**

**Granular approach (per story):**
- US-6.1 (Create Form): 46 tests
- US-6.2 (Date Picker): 33 tests
- US-6.3 (Edit Booking): 36 tests
- **Subtotal:** 115 tests

**Recommended consolidated approach:**
- Deduplicate overlapping test coverage (date validation, conflicts, etc.)
- Consolidate to **40–42 comprehensive E2E Playwright tests**
- Covers all 13 BRs + 40+ edge cases
- Faster execution, easier maintenance

**Test matrix includes:** 44 individual test specs organized into 6 groups

### 3. **Critical Implementation Points**

**Date Logic (BR-001):**
```typescript
// CORRECT: Inclusive end date
const totalDays = (endDate - startDate) / (1000*60*60*24) + 1;
// Jan 1–5 = 5 days, not 4

// Common mistake:
const totalDays = (endDate - startDate) / (1000*60*60*24); // OFF BY ONE
```

**Approval Reset Logic (BR-005):**
- **Shorten dates** (within original bounds) → Approvals **KEEP**
- **Extend dates** (earlier start OR later end) → Approvals **RESET**
- **Non-date changes only** (party size, affiliation, first name) → Approvals **KEEP**

**Conflict Detection (BR-002):**
```typescript
// CORRECT: overlap detection
return newStart <= existingEnd && newEnd >= existingStart;

// Shows error dialog with: {{FirstName}} – {{Status}}
// Example: "Anna – Ausstehend"
```

**Long Stay Dialog (BR-027):**
- Trigger: `TotalDays > 7` (NOT ≥7)
- Dialog: "Diese Anfrage umfasst {{TotalDays}} Tage. Möchtest du fortfahren?"
- Buttons: "Abbrechen" / "Bestätigen"

**German Copy (BR-011):**
- ALL text must be exact from specifications
- Use copy-paste from PHASE_6_QUICK_REFERENCE.md error messages section
- Never paraphrase or translate
- Informal "du" tone consistently

### 4. **Edge Cases by Category**

**40+ edge cases identified:**

| Category | Count | Examples |
|:---------|:---:|:---------|
| Date Range Validation | 6 | Same day, month boundary, year boundary, multi-month |
| First Name Validation | 9 | Min/max length, diacritics, special chars, emoji, newlines |
| Party Size | 6 | Boundary (1, 10), out of range, decimal, non-numeric |
| Description Field | 8 | Max length, URL detection (4 patterns), emojis, newlines |
| Conflicts | 5 | Pending, Confirmed, adjacent dates allowed, error display |
| Future Horizon | 3 | 17 months OK, 18 months OK, 19 months NOT OK |
| Long Stay | 3 | 6 days no dialog, 7 days no dialog, 8 days dialog |
| Email | 2 | Valid format, immutable in edit |
| Mobile | 4 | 375px viewport, 44px tap targets, no scroll |
| Approval Impact (Edit) | 6 | Shorten/extend/party/affiliation/first name/combination |
| Reopen | 4 | Same dates OK, conflicts reject, adjust & resubmit, transition |

---

## Recommended Implementation Sequence

**Phase 1: Design (Day 1)**
1. Read all three analysis documents
2. Complete pre-implementation checklist (PHASE_6_QUICK_REFERENCE.md)
3. Write all 40–42 Playwright test specs (failing tests)
4. Design form component structure

**Phase 2: Core Implementation (Days 2–3)**
5. Implement Zod validation schema
6. Implement form components (Shadcn, React Hook Form)
7. Implement date picker with conflict visualization
8. Implement API integration (create/update endpoints from Phase 2/3)
9. Implement error handling dialogs

**Phase 3: Verification (Day 4)**
10. Verify all tests pass
11. Mobile testing (375px viewport)
12. German copy audit (verify exact matches to spec)
13. Concurrent conflict testing (race conditions)
14. Self-review against Definition of Done

**Phase 4: Polish (as needed)**
15. Performance optimization
16. Accessibility testing
17. Browser compatibility
18. Deployment preparation

---

## Success Criteria (Definition of Done)

Before Phase 6 is complete:

- [ ] All 40–42 Playwright tests passing
- [ ] Zero test failures on all edge cases
- [ ] All German copy matches specification exactly (audited)
- [ ] Date calculations correct per BR-001 (inclusive semantics)
- [ ] Conflict detection working (BR-002)
- [ ] Approval reset logic correct (BR-005: extend → reset, shorten → keep)
- [ ] Long stay dialog appears for >7 days (BR-027)
- [ ] Email immutable in edit form
- [ ] Past bookings show read-only banner, no edit
- [ ] Mobile: 375px viewport, no horizontal scroll, ≥44pt tap targets
- [ ] Keyboard navigation works (desktop)
- [ ] No hover dependencies (mobile-first)
- [ ] All validations working:
  - First name (BR-019)
  - Email format
  - Party size range (BR-017)
  - Description URLs (BR-020)
  - Future horizon (BR-026)
- [ ] Reopen from Denied with conflict guard (BR-018)
- [ ] Type safety throughout (TypeScript strict)
- [ ] Code coverage ≥80%

---

## Files in This Package

### Primary Documents (Read in Order)

1. **PHASE_6_BR_ANALYSIS.md** (Start here for deep understanding)
   - Complete BR breakdown per user story
   - Implementation impacts, edge cases, test counts
   - German copy reference sheet
   - 850 lines

2. **PHASE_6_TEST_MATRIX.md** (Reference while designing tests)
   - Visual 6-group test matrix (44 tests)
   - BR-to-test traceability
   - Test data setup
   - 350 lines

3. **PHASE_6_QUICK_REFERENCE.md** (Keep open while coding)
   - Developer checklist
   - Copy-paste German strings
   - Code templates
   - Common mistakes
   - 450 lines

### This File

4. **PHASE_6_BR_ANALYSIS_SUMMARY.md** (You are here)
   - Executive summary
   - Key findings
   - Next steps

---

## How to Use These Documents

### Scenario 1: **"I need to understand what Phase 6 requires"**
→ Read: PHASE_6_BR_ANALYSIS.md (full context)

### Scenario 2: **"I'm implementing the form and need error messages"**
→ Jump to: PHASE_6_QUICK_REFERENCE.md → "Validation Error Messages" section → Copy exact text

### Scenario 3: **"What's the test plan for this story?"**
→ Check: PHASE_6_TEST_MATRIX.md → Relevant test group

### Scenario 4: **"Is this a business rule or just a detail?"**
→ Reference: PHASE_6_BR_ANALYSIS.md → "[US-X.Y]: Applicable Business Rules" table

### Scenario 5: **"I'm implementing edit form approval logic, what's the rule?"**
→ Jump to: PHASE_6_QUICK_REFERENCE.md → "Date Logic Implementation" → BR-005 code example

### Scenario 6: **"What does BR-005 actually mean?"**
→ Read: PHASE_6_BR_ANALYSIS.md → "US-6.3: Edit Booking" → "BR-005" entry

---

## Questions to Ask Yourself While Implementing

**On Requirements:**
- "Which BRs apply to this feature?" (check analysis)
- "What's the exact German copy?" (copy-paste from quick reference)
- "What are the validation rules?" (check data model section)

**On Testing:**
- "Is this edge case already in the test matrix?" (check test matrix)
- "What should this test verify?" (check test description)
- "Are there other similar tests I should look at?" (check traceability)

**On Implementation:**
- "Did I miss any field?" (check form field specs in analysis)
- "Is my date calculation correct?" (check BR-001 code examples)
- "How do I detect approval reset?" (check BR-005 logic in quick reference)
- "What error message should I show?" (copy from error messages section)

---

## Known Gotchas

1. **BR-001: Off-by-one errors**
   - Common mistake: `(end - start)` instead of `(end - start) + 1`
   - Impact: Jan 1–5 shows as 4 days instead of 5
   - Prevention: Use template code from quick reference

2. **BR-005: Approval reset direction**
   - Common mistake: Reset approvals for shorten, keep for extend (backwards)
   - Impact: Wrong approval behavior on date edits
   - Prevention: Shorten = keep, Extend = reset (counter-intuitive!)

3. **BR-027: Long stay threshold**
   - Common mistake: Use ≥7 days instead of >7 days
   - Impact: 7-day bookings incorrectly trigger dialog
   - Prevention: Check code has strict > not ≥

4. **BR-011: English text in German UI**
   - Common mistake: Use generic error messages instead of spec copy
   - Impact: User sees "Please enter" instead of "Bitte gib"
   - Prevention: Copy-paste from quick reference error section

5. **BR-002: Conflict detection formula**
   - Common mistake: Use wrong overlap detection logic
   - Impact: Allows overlaps or blocks adjacent dates
   - Prevention: Use exact formula from quick reference

---

## Success Story: Expected Workflow

**Day 1 (Design):**
```
Read analysis (2 hours) → Complete pre-checklist (30 min)
→ Write test specs (2 hours) → All tests failing ✓
```

**Day 2 (Implementation):**
```
Implement validation schema (1 hour) → Form components (3 hours)
→ Date picker (2 hours) → API integration (2 hours)
→ Some tests passing ✓
```

**Day 3 (Completion):**
```
Fix remaining bugs (2 hours) → Mobile testing (1 hour)
→ German copy audit (1 hour) → All tests passing ✓
→ Self-review (1 hour) → Ready for PR ✓
```

---

## Integration with Other Phases

**Phase 6 depends on:**
- Phase 2: Booking create/update API endpoints
- Phase 3: Approval logic (for edit impact calculations)
- Phase 5: Calendar component (reuse date picker if available)

**Phase 7 depends on:**
- Phase 6: Forms must be complete for approver to use
- Phase 6: Edit form reopen flow must work

**Parallel with Phase 6:**
- Phase 4: Email integration (can proceed independently)
- Phase 5: Calendar (UI can proceed; backend not needed)

---

## Next Steps

1. **Immediately:** Read PHASE_6_BR_ANALYSIS.md thoroughly
2. **Today:** Complete pre-implementation checklist (quick reference)
3. **Day 1:** Write all Playwright test specs (failing)
4. **Days 2–3:** Implement form, date picker, validation
5. **Day 4:** Verify tests pass, mobile test, audit copy, submit PR

---

## Document Statistics

| Document | Lines | Purpose | Time to Read |
|:---------|:-----:|:--------|:------------|
| PHASE_6_BR_ANALYSIS.md | ~850 | Deep analysis | 45 min |
| PHASE_6_TEST_MATRIX.md | ~350 | Test blueprint | 20 min |
| PHASE_6_QUICK_REFERENCE.md | ~450 | Developer reference | 30 min (scan), 2 hours (implement) |
| PHASE_6_BR_ANALYSIS_SUMMARY.md | ~400 | This file | 15 min |
| **Total** | **~2050** | **Complete guidance** | **~90 min to review all** |

---

## Contact & Questions

If documentation is unclear or conflicts found:
1. **Check all three documents** for cross-references
2. **Search for specific BR number** (e.g., "BR-005" appears in all three)
3. **Review original spec files** referenced in analysis
4. **Ask user for clarification** if ambiguity remains

---

## Summary

You have everything needed to implement Phase 6 successfully:

✅ **13 business rules analyzed** with implementation impact
✅ **40+ edge cases identified** with test coverage
✅ **44 test specs** organized in 6 groups
✅ **German copy** ready to copy-paste
✅ **Code templates** for validation, date logic, React Hook Form
✅ **Quick reference** for fast lookup during implementation
✅ **Traceability** between BRs, tests, and code

**Start with PHASE_6_BR_ANALYSIS.md. Keep PHASE_6_QUICK_REFERENCE.md open while coding. Reference PHASE_6_TEST_MATRIX.md while writing tests.**

Good luck! This phase covers all form creation/editing flows with comprehensive business rule coverage.
