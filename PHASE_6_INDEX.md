# Phase 6: Web Booking - Complete BR Analysis Package

**Index & Navigation Guide**

---

## 📦 What's in This Package

Four coordinated documents providing complete guidance for Phase 6 implementation:

### Document Overview

| Document | Purpose | For | Read Time |
|:---------|:--------|:----|:----------|
| **PHASE_6_BR_ANALYSIS.md** | Deep reference; comprehensive BR breakdown | Architects, reviewers | 45 min |
| **PHASE_6_TEST_MATRIX.md** | Visual test plan; 44 tests organized by feature | QA, test engineers | 20 min |
| **PHASE_6_QUICK_REFERENCE.md** | Developer handbook; copy-paste snippets | Implementers | 30 min scan; 2 hrs implement |
| **PHASE_6_BR_ANALYSIS_SUMMARY.md** | Executive summary; key findings | Everyone | 15 min |
| **PHASE_6_INDEX.md** | This file; navigation guide | Everyone | 5 min |

---

## 🎯 Start Here (By Role)

### I'm the Project Architect
1. Read: PHASE_6_BR_ANALYSIS_SUMMARY.md (15 min overview)
2. Read: PHASE_6_BR_ANALYSIS.md (45 min deep dive)
3. Review: PHASE_6_TEST_MATRIX.md (20 min; confirm coverage)

### I'm the Implementation Developer
1. Read: PHASE_6_BR_ANALYSIS_SUMMARY.md (15 min orientation)
2. Read: PHASE_6_QUICK_REFERENCE.md (30 min; understand requirements)
3. Start coding: Keep PHASE_6_QUICK_REFERENCE.md open; reference others as needed
4. Write tests: Use PHASE_6_TEST_MATRIX.md as checklist

### I'm the QA/Test Engineer
1. Read: PHASE_6_BR_ANALYSIS_SUMMARY.md (15 min context)
2. Review: PHASE_6_TEST_MATRIX.md (20 min; test plan)
3. Read: PHASE_6_BR_ANALYSIS.md → Edge Cases sections (30 min; edge case understanding)
4. Execute: Use test matrix as checklist

### I'm a Code Reviewer
1. Read: PHASE_6_BR_ANALYSIS.md (45 min; understand all rules)
2. Review: PHASE_6_TEST_MATRIX.md (20 min; verify test coverage)
3. Reference: PHASE_6_QUICK_REFERENCE.md (spot-check implementation against templates)

### I Need Quick Answers
→ Use **PHASE_6_QUICK_REFERENCE.md** as lookup:
- What error message for this validation?
- How do I detect approval reset?
- What's the date range logic?
- What are the mobile requirements?

---

## 📋 Document Contents Quick Lookup

### PHASE_6_BR_ANALYSIS.md
**Chapters:**
1. Executive Summary
2. US-6.1: Create Booking Form
   - Applicable BRs (9)
   - Implementation details
   - Edge cases (46)
   - Test matrix
3. US-6.2: Date Picker
   - Applicable BRs (4)
   - Implementation details
   - Edge cases (26)
   - Test matrix
4. US-6.3: Edit Booking
   - Applicable BRs (8)
   - Implementation details
   - Edge cases (36)
   - Test matrix
5. Cross-Cutting Concerns (mobile, German, privacy)
6. Consolidated Test Matrix Summary
7. Implementation Checklist
8. German Copy Reference Sheet

**Best for:** Deep understanding of requirements and edge cases

---

### PHASE_6_TEST_MATRIX.md
**Sections:**
1. Executive Test Summary (40–42 recommended tests)
2. Test Matrix by Category (6 groups):
   - GROUP 1: Form Creation & Submission (10 tests)
   - GROUP 2: Date Picker & Range Logic (10 tests)
   - GROUP 3: Conflict Detection & Error Handling (8 tests)
   - GROUP 4: Edit Booking - Approval Impact (8 tests)
   - GROUP 5: Reopen from Denied (4 tests)
   - GROUP 6: Mobile & Accessibility (4 tests)
3. Test-to-BR Traceability Matrix
4. Recommended Test Execution Order
5. Test Data Setup Requirements
6. Key Test Fixtures (JSON examples)
7. GitHub/CI Integration Checklist

**Best for:** Writing Playwright tests; verification

---

### PHASE_6_QUICK_REFERENCE.md
**Sections:**
1. Pre-Implementation Checklist
2. 13 Critical BRs (quick-lookup table)
3. Form Field Specifications
4. Validation Error Messages (copy-paste ready)
5. Success Messages (copy-paste ready)
6. Dialog Copy (copy-paste ready)
7. Validation Zod Schema Template
8. Date Logic Implementation (correct vs. incorrect)
9. Form Component Architecture
10. Form State Management (React Hook Form template)
11. Mobile-First Checklist
12. Playwright Test Template
13. Testing Checklist
14. Common Mistakes to Avoid (with consequences)
15. Key Files to Review
16. Quick Lookup: BR Finder

**Best for:** During implementation; keep open constantly

---

### PHASE_6_BR_ANALYSIS_SUMMARY.md
**Sections:**
1. What You're Getting (document descriptions)
2. Key Findings (13 BRs, test estimation, critical points, edge cases)
3. Recommended Implementation Sequence (4 phases: Design, Implementation, Verification, Polish)
4. Success Criteria (DoD checklist)
5. Files in This Package
6. How to Use These Documents (6 scenarios)
7. Questions to Ask Yourself
8. Known Gotchas (5 common mistakes)
9. Success Story: Expected Workflow
10. Integration with Other Phases
11. Document Statistics
12. Summary

**Best for:** Orientation and quick overview

---

### PHASE_6_INDEX.md
**This file.**
- Navigation guide
- Quick lookup by role
- Content overview
- Searching tips

---

## 🔍 Find Information By Topic

### Date Validation & Logic

**Question:** "How do I calculate TotalDays correctly?"
→ PHASE_6_QUICK_REFERENCE.md → "Date Logic Implementation" → BR-001 section

**Question:** "What's the overlap detection formula?"
→ PHASE_6_QUICK_REFERENCE.md → "Date Logic Implementation" → BR-002 section

**Question:** "What edge cases exist for dates?"
→ PHASE_6_BR_ANALYSIS.md → "US-6.2: Date Picker" → "Edge Cases to Test" section

**Question:** "How does date picker blocking work?"
→ PHASE_6_BR_ANALYSIS.md → "US-6.2: Date Picker" → "Implementation Details" section

---

### Approval Reset Logic (BR-005)

**Question:** "When do approvals reset on edit?"
→ PHASE_6_BR_ANALYSIS.md → "US-6.3: Edit Booking" → BR-005 entry

**Question:** "How do I detect if dates were extended?"
→ PHASE_6_QUICK_REFERENCE.md → "Date Logic Implementation" → "Detect Date Extend vs. Shorten" section

**Question:** "What about non-date changes?"
→ PHASE_6_BR_ANALYSIS.md → "US-6.3: Edit Booking" → Implementation Details → "Change Detection Logic"

---

### German Copy (BR-011)

**Question:** "What error message for invalid first name?"
→ PHASE_6_QUICK_REFERENCE.md → "Validation Error Messages" → Copy-paste first name error

**Question:** "What's the long stay dialog text?"
→ PHASE_6_QUICK_REFERENCE.md → "Dialog Copy" → Long Stay Confirmation section

**Question:** "Are all German strings exact from spec?"
→ PHASE_6_BR_ANALYSIS.md → "German Copy Reference Sheet" (end of document)

---

### Testing & Edge Cases

**Question:** "How many tests do I need?"
→ PHASE_6_BR_ANALYSIS_SUMMARY.md → "Key Findings" → "Test Estimation" section

**Question:** "What's the test matrix?"
→ PHASE_6_TEST_MATRIX.md → "Test Matrix by Category" (start here)

**Question:** "What edge cases exist for party size?"
→ PHASE_6_BR_ANALYSIS.md → "US-6.1: Create Booking Form" → "Edge Cases to Test" → Party Size section

**Question:** "What are the mobile test requirements?"
→ PHASE_6_QUICK_REFERENCE.md → "Mobile-First Checklist"

---

### Implementation Code

**Question:** "How do I structure the form component?"
→ PHASE_6_QUICK_REFERENCE.md → "Form Component Architecture" section

**Question:** "What's the Zod schema?"
→ PHASE_6_QUICK_REFERENCE.md → "Validation Zod Schema Template" section

**Question:** "How do I handle long stay dialog?"
→ PHASE_6_QUICK_REFERENCE.md → "Form State Management" → onSubmit function

**Question:** "What's a Playwright test look like?"
→ PHASE_6_QUICK_REFERENCE.md → "Playwright Test Template" section

---

### Mobile & Accessibility

**Question:** "What are the mobile requirements?"
→ PHASE_6_QUICK_REFERENCE.md → "Mobile-First Checklist"

**Question:** "Do I need hover states?"
→ PHASE_6_BR_ANALYSIS_SUMMARY.md → "Mobile-First Design" → "No hover dependencies"

**Question:** "How big should tap targets be?"
→ PHASE_6_QUICK_REFERENCE.md → "Mobile-First Checklist" → "44×44pt tap targets"

---

### Common Problems

**Question:** "I think I found a bug, what BR covers this?"
→ PHASE_6_QUICK_REFERENCE.md → "Quick Lookup: Which BR Does This Belong To?" section

**Question:** "What mistakes should I avoid?"
→ PHASE_6_QUICK_REFERENCE.md → "Common Mistakes to Avoid" table

**Question:** "I got an off-by-one error, what's wrong?"
→ PHASE_6_BR_ANALYSIS_SUMMARY.md → "Known Gotchas" → "BR-001: Off-by-one errors"

---

## 🚀 Quick Start (5-Minute Orientation)

1. **What's Phase 6?**
   → Read first paragraph of PHASE_6_BR_ANALYSIS_SUMMARY.md

2. **What are the requirements?**
   → Read "Key Findings" section of PHASE_6_BR_ANALYSIS_SUMMARY.md

3. **How many tests?**
   → Check "Test Estimation" in PHASE_6_BR_ANALYSIS_SUMMARY.md

4. **When do I start?**
   → Follow "Recommended Implementation Sequence" in PHASE_6_BR_ANALYSIS_SUMMARY.md

5. **What do I read first?**
   → Your role determines this; see "Start Here (By Role)" above

---

## 📈 Implementation Roadmap

### Pre-Implementation (Day 1, 2 hours)
```
□ Read PHASE_6_BR_ANALYSIS_SUMMARY.md (15 min)
□ Read PHASE_6_QUICK_REFERENCE.md → Pre-Implementation Checklist (10 min)
□ Complete pre-checklist
□ Read PHASE_6_BR_ANALYSIS.md (45 min)
□ Design test plan
```

### Test Design (Day 1, 2 hours)
```
□ Review PHASE_6_TEST_MATRIX.md → all 44 tests
□ Write Playwright test specs (failing tests)
□ Verify all tests fail (confirms they're real tests)
```

### Implementation (Days 2–3, 6 hours)
```
□ Implement Zod validation schema
□ Implement form components
□ Implement date picker
□ Implement API integration
□ Fix failing tests
□ All tests passing
```

### Verification (Day 4, 2 hours)
```
□ Mobile testing (375px viewport)
□ German copy audit (vs. PHASE_6_QUICK_REFERENCE.md)
□ Self-review vs. DoD checklist
□ Ready for PR
```

---

## 🔗 File Locations

All files are at root of repo:

```
/home/user/btznstn/
├─ PHASE_6_INDEX.md                      ← You are here
├─ PHASE_6_BR_ANALYSIS.md               ← Deep reference
├─ PHASE_6_TEST_MATRIX.md               ← Test plan
├─ PHASE_6_QUICK_REFERENCE.md           ← Developer handbook
└─ PHASE_6_BR_ANALYSIS_SUMMARY.md       ← Executive summary
```

Related spec files (referenced throughout):
```
/home/user/btznstn/
├─ docs/
│   ├─ foundation/
│   │   └─ business-rules.md            ← BR-001 to BR-029
│   ├─ specification/
│   │   ├─ ui-screens.md                ← Form layouts
│   │   ├─ error-handling.md            ← Error messages
│   │   └─ data-model.md                ← Field constraints
│   ├─ implementation/
│   │   └─ phase-6-frontend-booking.md  ← User stories
│   └─ [others]
```

---

## ❓ FAQ

**Q: How do I use these documents together?**
A: They're designed for different purposes:
- **Analysis** = deep understanding
- **Test Matrix** = what to test
- **Quick Reference** = how to implement
- **Summary** = orientation + key findings

Start with Summary, read Analysis for understanding, reference Quick Ref while coding, use Test Matrix for verification.

---

**Q: Can I skip the analysis and just read Quick Reference?**
A: Not recommended. You'll miss critical context about:
- Why each BR matters (implementation impact)
- Edge cases you must test
- German copy sourcing
- Business logic complexity (approval reset, etc.)

Read at least the Summary + BR explanation in Analysis.

---

**Q: What if I disagree with a requirement?**
A: All requirements are traceable to source documents:
- /docs/foundation/business-rules.md (BR-001–029)
- /docs/specification/ui-screens.md (UI/forms)
- /docs/specification/error-handling.md (error messages)
- /docs/specification/data-model.md (field constraints)

Reference the source, ask user for clarification if ambiguous.

---

**Q: How do I know if I'm done?**
A: Check "Success Criteria (Definition of Done)" in PHASE_6_BR_ANALYSIS_SUMMARY.md.

Must complete checklist before submitting PR.

---

**Q: What if I find a bug or missing requirement?**
A: Document it, reference the BR or section, ask user for clarification before fixing.

Never assume or infer requirements beyond what's documented.

---

## 📞 Support

**During Implementation:**
- Keep PHASE_6_QUICK_REFERENCE.md open (constant reference)
- When stuck, search all documents for keyword
- Check "Common Mistakes" section if behavior is wrong
- Review original spec files if still unclear

**If Documentation is Unclear:**
- Check cross-references in all documents
- Review original spec files (docs/specification/)
- Search for specific BR number or term
- Ask user for clarification

---

## ✅ Verification Checklist

Before declaring Phase 6 complete, verify:

- [ ] All 40–42 Playwright tests passing
- [ ] All business rules (BR-001–027) implemented and tested
- [ ] All German copy matches specification exactly
- [ ] Mobile viewport (375px) fully functional
- [ ] No horizontal scroll, ≥44pt tap targets
- [ ] Date calculations correct (inclusive semantics)
- [ ] Conflict detection working
- [ ] Approval reset logic correct (extend → reset, shorten → keep)
- [ ] Form validation complete (all fields per spec)
- [ ] Error handling with proper German copy
- [ ] Edit form features (immutable email, past read-only, reopen)
- [ ] Type safety throughout (TypeScript strict)
- [ ] Code coverage ≥80%
- [ ] Self-review complete (DoD checklist)

---

## 📝 Next Steps

1. **Choose your document** based on your role (see "Start Here" above)
2. **Read the document** in suggested time
3. **Reference the quick reference** while implementing
4. **Use test matrix** while testing
5. **Check summary** for overview and key findings
6. **Return to analysis** for deep dives on specific topics

---

**You have everything needed. Start with PHASE_6_BR_ANALYSIS_SUMMARY.md. Good luck!**
