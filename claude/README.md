# Claude Code Guide for This Repository

## Purpose

This file provides guidance for future Claude Code sessions working on the Betzenstein booking & approval application.

---

## Project Overview

**What This Is:**
A booking and approval system for whole-day reservations requiring three independent approvals (Ingeborg, Cornelia, Angelika). Email-first, zero-login access via secure links. German UI, mobile-first design.

**Key Characteristics:**
- **Access:** Role-by-link (no accounts/passwords)
- **Approval Flow:** Three fixed approvers required
- **States:** Pending → Confirmed/Denied, with Reopen capability
- **Privacy:** First names only; emails never displayed
- **Mobile-First:** iPhone 8 class minimum

---

## Documentation Structure

The repository uses a structured documentation approach optimized for AI readability:

```
/docs/
├── README.md                      # Navigation guide
├── /foundation/                   # Core concepts (rarely change)
│   ├── vision-and-scope.md
│   ├── personas-and-roles.md
│   ├── glossary.md
│   └── business-rules.md
├── /requirements/                 # What the system must do
│   ├── functional-overview.md
│   ├── user-journeys.md
│   ├── states-and-transitions.md
│   ├── permissions-matrix.md
│   └── acceptance-criteria.md
├── /specification/                # Detailed technical specs
│   ├── ui-screens.md
│   ├── notifications.md
│   ├── data-model.md
│   ├── error-handling.md
│   └── configuration.md
└── /constraints/                  # Boundaries and limits
    ├── non-functional.md
    └── technical-constraints.md

/claude/
├── README.md                      # This file
└── documentation-workflow.md      # How to maintain docs
```

---

## How to Use This Documentation

### When Starting a New Task

1. **Read the relevant documentation first:**
   - For user journeys: `docs/requirements/user-journeys.md`
   - For data model: `docs/specification/data-model.md`
   - For business rules: `docs/foundation/business-rules.md`
   - For German copy: `docs/specification/notifications.md` and `docs/specification/error-handling.md`

2. **Check business rules (BR-001 to BR-029):**
   - All rules documented in `docs/foundation/business-rules.md`
   - Reference by number (e.g., "per BR-015")

3. **Verify your understanding:**
   - The documentation is the **source of truth**
   - If unclear, ask the user for clarification
   - Do NOT make assumptions about behavior not documented

---

### For Implementation Tasks

**Before writing code:**
1. Read the acceptance criteria (`docs/requirements/acceptance-criteria.md`)
2. Review the data model (`docs/specification/data-model.md`)
3. Check German UI copy requirements (`docs/specification/notifications.md`, `docs/specification/error-handling.md`)
4. Review relevant business rules (`docs/foundation/business-rules.md`)

**While implementing:**
- Reference line numbers from requirements/specs in your code comments
- Use exact German copy from specifications (no variations)
- Follow the state machine (`docs/requirements/states-and-transitions.md`)
- Implement all validation rules (`docs/specification/data-model.md`)

**After implementing:**
- Verify all acceptance criteria met
- Test German copy displays correctly
- Ensure mobile compatibility (iPhone 8 class minimum)
- Check permissions match matrix (`docs/requirements/permissions-matrix.md`)

---

### For Design/Architecture Tasks

**Refer to:**
- Vision & scope: `docs/foundation/vision-and-scope.md`
- Non-functional requirements: `docs/constraints/non-functional.md`
- Technical constraints: `docs/constraints/technical-constraints.md`
- Data model: `docs/specification/data-model.md`

**Key Principles:**
- Email-first, zero-login
- Privacy by design (emails never shown)
- Mobile-first (touch-friendly, no hover)
- German only UI
- Three fixed approvers
- First-write-wins / first-action-wins concurrency

---

### For Bug Fixes

**Investigation:**
1. Reproduce the issue
2. Check if behavior contradicts documentation
3. If documentation is correct: fix code to match docs
4. If documentation is wrong: update docs AND code

**Never:**
- Assume undocumented behavior is correct
- Change business rules without user approval
- Deviate from German copy specifications

---

## Key Business Rules (Quick Reference)

**Critical Rules to Remember:**

- **BR-001:** Inclusive end date (`TotalDays = End - Start + 1`)
- **BR-002:** No overlaps with Pending/Confirmed
- **BR-003:** Three fixed approvers required
- **BR-004:** Denial is non-blocking, not public; dates free immediately
- **BR-005:** Date edits logged; shorten keeps approvals, extend resets
- **BR-009:** Weekly digest Sunday 09:00, ≥5 days aged, future-only
- **BR-010:** Tokens never expire, no revocation
- **BR-011:** German-only UI
- **BR-015:** Self-approval if requester is approver
- **BR-024:** First-action-wins for concurrent approvals/denials
- **BR-029:** First-write-wins for create/extend operations

**Full list:** See `docs/foundation/business-rules.md`

---

## German Copy Guidelines

**Source of Truth:**
- Notifications: `docs/specification/notifications.md`
- Error messages: `docs/specification/error-handling.md`
- UI screens: `docs/specification/ui-screens.md`

**Important:**
- Use informal "du" (not "Sie")
- Date format: `DD.–DD.MM.YYYY` (e.g., "01.–05.08.2025")
- Party size always: "n Personen" (even for 1 person)
- Use exact copy from specs (don't improvise)

---

## Common Pitfalls

### Pitfall 1: Assuming Past Behavior
**Problem:** Making assumptions based on what "typically" happens in booking systems

**Solution:** Only implement what's documented. This system has unique requirements (e.g., Denied is non-blocking, no token expiry).

---

### Pitfall 2: Forgetting Mobile-First
**Problem:** Designing for desktop, then trying to adapt to mobile

**Solution:** Design for iPhone 8 class first (375×667px). Large tap targets (44×44pt), no hover dependencies.

---

### Pitfall 3: Ignoring Date Inclusivity
**Problem:** Off-by-one errors in date calculations

**Solution:** Always remember BR-001: **inclusive end date**. Jan 1–3 covers three days (1, 2, 3).

---

### Pitfall 4: Not Using Exact German Copy
**Problem:** Paraphrasing or translating English copy to German

**Solution:** Use exact copy from `docs/specification/notifications.md` and `docs/specification/error-handling.md`.

---

### Pitfall 5: Displaying Email Addresses
**Problem:** Showing emails in UI (violates privacy principle)

**Solution:** Emails are PII, never displayed. Only first names shown.

---

## Working with This Documentation

### It's Optimized for AI

**Structure:**
- Clear headings and sections
- Tables for complex data
- Lists for sequential information
- Mermaid diagrams for visual relationships
- Cross-references between documents

**How to Read:**
- Start with `docs/README.md` for navigation
- Use Ctrl+F / Cmd+F to search within documents
- Follow cross-references (e.g., "see BR-015")
- Read entire relevant section (don't skip context)

---

### When Documentation is Unclear

**If you encounter ambiguity:**
1. Check related documents (cross-references)
2. Look for examples in the same document
3. Check business rules for governing principles
4. **Ask the user for clarification** (don't guess)

**Never:**
- Assume behavior based on "common sense"
- Fill in gaps with "typical" patterns
- Deviate from documented specs without approval

---

## Future Development Phases

**This documentation covers:**
- Complete business requirements (ready for implementation)
- All user journeys and acceptance criteria
- Data model and validation rules
- UI specifications and German copy
- Configuration and constraints

**Future phases (not yet documented):**
- Architecture Decision Records (ADRs)
- Solution design documentation
- Implementation planning and breakdown
- Incremental roadmap
- Code scaffolding and structure

**When working on future phases:**
- Create new documentation in appropriate locations
- Reference this foundation documentation
- Follow patterns established here
- Keep documentation synchronized with code

---

## Maintaining Documentation

See `claude/documentation-workflow.md` for detailed guidance on:
- When to update documentation
- How to add new sections
- Where to document new features
- How to keep docs synchronized with code

---

## Documentation Philosophy

**Principles:**
1. **Single source of truth:** Documentation defines behavior
2. **AI-friendly:** Structured for easy parsing and understanding
3. **Comprehensive:** Everything needed for implementation
4. **Unambiguous:** Clear, specific, verifiable
5. **Traceable:** Business rules numbered, references throughout

**Quality Checks:**
- Is this behavior documented? (If not, don't implement it)
- Does code match docs? (If not, fix the mismatch)
- Are German strings exact? (If not, use spec copy)
- Are all business rules followed? (Check BR-001 to BR-029)

---

## Quick Start Checklist

**Before starting any task:**

- [ ] Read relevant documentation sections
- [ ] Check business rules that apply
- [ ] Note German copy requirements
- [ ] Review acceptance criteria
- [ ] Understand state transitions
- [ ] Check permissions matrix
- [ ] Verify mobile requirements
- [ ] Note any constraints

**During implementation:**

- [ ] Reference docs in code comments
- [ ] Use exact German copy from specs
- [ ] Follow state machine precisely
- [ ] Implement all validations
- [ ] Handle all error cases
- [ ] Test on mobile viewport

**After implementation:**

- [ ] All acceptance criteria met
- [ ] German copy correct
- [ ] Mobile tested (375px width min)
- [ ] Permissions enforced
- [ ] Business rules followed
- [ ] Documentation still accurate (update if needed)

---

## Getting Help

**If stuck:**
1. Re-read relevant documentation section
2. Check cross-references and related docs
3. Search for keywords across all docs
4. Review examples and tables
5. **Ask the user** (provide specific question with context)

**What to include when asking:**
- What you're trying to implement
- What the documentation says (quote it)
- What's unclear or ambiguous
- What you've already tried

---

## Summary

**Remember:**
- **Documentation is truth** (not assumptions)
- **German UI only** (informal "du")
- **Mobile-first** (iPhone 8 class min)
- **Privacy by design** (no email display)
- **Three fixed approvers** (Ingeborg, Cornelia, Angelika)
- **Inclusive end dates** (BR-001)
- **First-wins concurrency** (BR-024, BR-029)

**When in doubt:**
- Read the docs
- Ask the user
- Don't assume

Good luck building! 🚀
