# CLAUDE Code Agent Guide

## Welcome!

This is the **Betzenstein Booking & Approval Application** - a complete, implementation-ready project with comprehensive documentation optimized for AI agents like you.

---

## Quick Start

**⚠️ CRITICAL: ALWAYS START HERE ON EVERY SESSION**

**Step 1 - Check Project Status (MANDATORY):**
1. **🎯 FIRST ACTION:** Read [`/project/STATUS.md`](project/STATUS.md) - Where are we now? What's completed? What's in progress?
2. **SECOND:** Review [`/project/BACKLOG.md`](project/BACKLOG.md) - What's the highest priority task right now?
3. **THIRD:** Read current increment file in [`/project/increments/`](project/increments/) - Detailed user story context

**Step 2 - Understand the Project (First Time Only):**
- Read [`/project/README.md`](project/README.md) - Explains the project management structure
- Navigate to [`docs/README.md`](docs/README.md) - Documentation navigation hub
- Check [`/claude/README.md`](claude/README.md) - Detailed AI agent workflow guidance
- Browse [`docs/implementation/README.md`](docs/implementation/README.md) - BDD implementation roadmap

**Step 3 - Get Context for Your Task:**
- Reference section-specific `CLAUDE.md` files in each documentation folder as needed
- Read relevant business rules from [`docs/foundation/business-rules.md`](docs/foundation/business-rules.md)
- Check German copy from [`docs/specification/`](docs/specification/) files

---

## Project Overview

**What:** Booking calendar for whole-day reservations requiring three independent approvals

**Key Features:**
- Email-first access (no login/passwords) via secure token links
- Three fixed approvers: Ingeborg, Cornelia, Angelika
- German-only UI (informal "du" tone)
- Mobile-first design (iPhone 8+ class)
- Privacy by design (emails never displayed, first names only)

**Tech Stack:**
- Backend: FastAPI + Python 3.11+ on Fly.io
- Frontend: Next.js 14 (App Router) on Vercel
- Database: PostgreSQL 15+ on Fly.io
- UI: Shadcn/ui + Tailwind CSS
- Email: Resend

---

## Documentation Structure

This project uses a **layered documentation approach**:

```
/
├── CLAUDE.md                          # This file - main entry point for AI agents
├── README.md                          # Project overview (minimal)
│
├── /claude/                           # CLAUDE Code workflow guidance
│   ├── README.md                      # Detailed agent workflow guide
│   └── documentation-workflow.md      # How to maintain docs
│
└── /docs/                             # Complete project documentation
    ├── README.md                      # Documentation navigation hub
    ├── CLAUDE.md → Each section has its own CLAUDE.md for context
    │
    ├── /foundation/                   # Core concepts (rarely change)
    │   ├── CLAUDE.md                  # Foundation-specific guidance
    │   ├── vision-and-scope.md
    │   ├── personas-and-roles.md
    │   ├── glossary.md
    │   └── business-rules.md          # BR-001 to BR-029
    │
    ├── /requirements/                 # What the system must do
    │   ├── CLAUDE.md                  # Requirements-specific guidance
    │   ├── functional-overview.md
    │   ├── user-journeys.md
    │   ├── states-and-transitions.md
    │   ├── permissions-matrix.md
    │   └── acceptance-criteria.md
    │
    ├── /specification/                # Detailed technical specs
    │   ├── CLAUDE.md                  # Specification-specific guidance
    │   ├── ui-screens.md
    │   ├── notifications.md           # All German email copy
    │   ├── data-model.md
    │   ├── error-handling.md          # All German error messages
    │   └── configuration.md
    │
    ├── /constraints/                  # Boundaries and limits
    │   ├── CLAUDE.md                  # Constraints-specific guidance
    │   ├── non-functional.md
    │   └── technical-constraints.md
    │
    ├── /architecture/                 # Architecture decisions
    │   ├── CLAUDE.md                  # Architecture-specific guidance
    │   ├── README.md
    │   ├── technology-stack.md
    │   └── adr-001-*.md through adr-019-*.md  # Architecture Decision Records (numbered sequentially)
    │
    ├── /design/                       # Detailed design
    │   ├── CLAUDE.md                  # Design-specific guidance
    │   ├── api-specification.md
    │   ├── database-schema.md
    │   ├── authentication-flow.md
    │   ├── component-guidelines.md
    │   └── design-tokens.md
    │
    └── /implementation/               # BDD roadmap
        ├── CLAUDE.md                  # Implementation-specific guidance
        ├── README.md                  # 8-phase BDD plan
        └── phase-0-*.md through phase-8-*.md  # Phase-by-phase details (numbered 0 to 8)
```

---

## How to Use This Documentation

### For Understanding the Project

**Start here:**
1. [`docs/foundation/vision-and-scope.md`](docs/foundation/vision-and-scope.md) - What and why
2. [`docs/foundation/business-rules.md`](docs/foundation/business-rules.md) - BR-001 to BR-029
3. [`docs/requirements/user-journeys.md`](docs/requirements/user-journeys.md) - User flows
4. [`docs/architecture/README.md`](docs/architecture/README.md) - System architecture

**Each section has a `CLAUDE.md` file** with specific guidance for working in that area.

### For Implementation

**Follow the BDD roadmap:**
1. [`docs/implementation/README.md`](docs/implementation/README.md) - Overview and approach
2. [`docs/implementation/phase-0-foundation.md`](docs/implementation/phase-0-foundation.md) - Start here
3. Continue through phases sequentially: phase-1, phase-2, phase-3, phase-4, phase-5, phase-6, phase-7, phase-8 (in numerical order)

**Each phase includes:**
- User stories
- Gherkin acceptance criteria
- Test-first approach
- Definition of done

### For Specific Tasks

**Need to work on:**
- **Business logic?** → Read [`docs/foundation/CLAUDE.md`](docs/foundation/CLAUDE.md)
- **User flows?** → Read [`docs/requirements/CLAUDE.md`](docs/requirements/CLAUDE.md)
- **UI/API/DB?** → Read [`docs/specification/CLAUDE.md`](docs/specification/CLAUDE.md)
- **Architecture decisions?** → Read [`docs/architecture/CLAUDE.md`](docs/architecture/CLAUDE.md)
- **Implementation phase?** → Read [`docs/implementation/CLAUDE.md`](docs/implementation/CLAUDE.md)

---

## Critical Information

### Business Rules (BR-001 to BR-029)

**ALWAYS reference business rules** from [`docs/foundation/business-rules.md`](docs/foundation/business-rules.md)

**Most critical (read full text in business-rules.md for complete details):**
- **BR-001:** Inclusive end date calculation (`TotalDays = EndDate - StartDate + 1`). Example: Jan 1 to Jan 3 = 3 days (not 2).
- **BR-002:** No date overlaps allowed with bookings in Pending or Confirmed states. Denied/Canceled bookings do not block dates.
- **BR-003:** Exactly three fixed approvers required: Ingeborg, Cornelia, Angelika (first names only, case-sensitive).
- **BR-004:** Denial does not block dates (frees them immediately). Denied bookings are not visible to public (only requester sees them).
- **BR-005:** Date edits are logged. Shortening dates keeps existing approvals. Extending dates resets all approvals to pending.
- **BR-015:** If requester is also an approver, that approver's approval is automatically granted (self-approval).
- **BR-024:** When multiple approvals/denials happen concurrently, the first one processed wins (race condition handling).
- **BR-029:** When multiple create/extend operations happen concurrently, the first write wins (race condition handling).

### German Copy

**ALL German text MUST come from specifications:**
- Emails: [`docs/specification/notifications.md`](docs/specification/notifications.md)
- Errors: [`docs/specification/error-handling.md`](docs/specification/error-handling.md)
- UI: [`docs/specification/ui-screens.md`](docs/specification/ui-screens.md)

**Rules:**
- Use informal "du" form (not formal "Sie" form) for all user-facing German text
- Date format: `DD.–DD.MM.YYYY` (example: "01.–05.08.2025" means January 1st through January 5th, 2025)
- Party size format: Always use "n Personen" format (example: "1 Person" is wrong, use "1 Person" only if spec says so, otherwise "1 Personen")
- **Never improvise** - copy exact text from specification files, character by character

### State Machine

**Booking states:** Pending → Confirmed/Denied/Canceled

**Critical:**
- Only Pending/Confirmed block dates
- Denied frees dates immediately
- Requester can Reopen Denied bookings
- See [`docs/requirements/states-and-transitions.md`](docs/requirements/states-and-transitions.md)

### Mobile-First

**Design for iPhone 8 first** (375×667px)
- Touch-friendly (44×44pt minimum tap targets)
- No hover dependencies
- Large, clear touch targets
- See [`docs/constraints/technical-constraints.md`](docs/constraints/technical-constraints.md)

---

## Common Workflows

### Starting a New Task

1. **Read the relevant documentation:**
   - Business rules that apply
   - User journeys involved
   - German copy required
   - Acceptance criteria
   - Section-specific `CLAUDE.md`

2. **Write tests first** (BDD approach):
   - Backend: `pytest` tests in `api/tests/` directory
     - ⚠️ **MANDATORY:** Read [`api/tests/CLAUDE.md`](api/tests/CLAUDE.md) BEFORE writing any test file
     - Always check `api/tests/utils.py` for existing utility functions before creating new ones
     - Always check `api/tests/fixtures/factories.py` for factory functions before creating manual instances
     - Use factory functions: `make_booking()`, `make_approval()`, `make_user()` (never create instances manually like `Booking(...)`)
     - Use `get_today()` from utils for current date (never use `datetime.now()` or `date.today()` directly)
     - Follow DRY principle: if test code repeats, extract to utility or fixture
   - Frontend: `playwright` E2E tests in `web/` directory
   - Tests MUST fail initially (red phase) before implementation (green phase)

3. **Implement:**
   - Follow architecture patterns
   - Use exact German copy
   - Enforce business rules
   - Match data model

4. **Verify (all must pass):**
   - All tests pass: run `pytest` for backend, `npx playwright test` for frontend
   - Type checks pass: run `mypy app/` for backend, `npm run type-check` for frontend
   - Linting passes: run `ruff check app/` for backend, `npm run lint` for frontend
   - German copy matches specs exactly: compare character-by-character with specification files

### Fixing a Bug

1. **Reproduce the issue**
2. **Check documentation:**
   - Does behavior match business rules?
   - Does implementation match specifications?
3. **Fix the mismatch:**
   - If docs are correct → fix code
   - If docs are wrong → ask user, then update docs AND code
4. **Never assume** undocumented behavior is correct

### Adding a Feature

1. **Document requirements first:**
   - Update relevant sections in `/docs/`
   - Add business rules if needed
   - Define acceptance criteria
   - Specify German copy
2. **Write failing tests**
3. **Implement feature**
4. **Verify against acceptance criteria**

---

## Key Principles

### 1. Documentation is Truth

**The documentation defines behavior** - not assumptions, not "typical" patterns

**Never:**
- Implement undocumented features
- Assume behavior based on "common sense"
- Deviate from specs without user approval

**Always:**
- Read relevant docs first
- Reference business rules by number (e.g., "per BR-015")
- Use exact German copy from specifications
- Ask user if documentation is unclear

### 2. Type Safety Throughout

**Backend:**
- Python type hints on all functions, methods, and variables (no `Any` unless absolutely necessary)
- Mypy strict mode enabled (check with `mypy app/`)
- Pydantic BaseModel validation on all API request/response models (no manual validation)

**Frontend:**
- TypeScript strict mode enabled (check `tsconfig.json` for strict settings)
- Zod schema validation on all form inputs (no manual validation)
- Type-safe API client generated from OpenAPI spec (never manually type API responses)

**Benefit:** Errors caught at compile time, not runtime

### 3. Test-First (BDD)

**Approach (Red-Green-Refactor cycle):**
1. Write failing tests first (Red phase - tests must fail)
2. Implement minimum code to make tests pass (Green phase - tests pass)
3. Verify all tests pass
4. Refactor code while keeping tests passing (Refactor phase - improve code quality)

**Every feature has:**
- Backend pytest tests
- Frontend Playwright E2E tests
- Minimum 80% code coverage target (run `pytest --cov=app` to verify)

### 4. Mobile-First UI

**Design constraints:**
- iPhone 8 class minimum (375px width minimum, 667px height minimum)
- Touch-friendly targets (minimum 44×44 points, which equals 44×44 pixels at 1x scale)
- No hover dependencies (all interactions must work with touch/tap only)
- Works on slow networks (optimize for 3G speeds, minimize initial load)

### 5. Privacy by Design

**Rules (strict enforcement):**
- Email addresses NEVER displayed in UI (not even partially masked like "u***@example.com")
- Denied bookings hidden from public calendar view (only requester can see their own denied bookings)
- Only first names displayed (never last names, never email addresses)
- Token-based access only (no user accounts, no passwords, no login forms)

---

## Anti-Patterns to Avoid

### ❌ Don't: Assume Past Behavior
**Problem:** Making assumptions based on what "typically" happens in booking systems

**Solution:** Only implement what's documented. This system has unique requirements.

### ❌ Don't: Forget Date Inclusivity
**Problem:** Off-by-one errors in date calculations

**Solution:** Always remember BR-001: **inclusive end date**. Formula: `TotalDays = EndDate - StartDate + 1`. Example: January 1 to January 3 covers exactly three days (days 1, 2, and 3). Never use `EndDate - StartDate` without adding 1.

### ❌ Don't: Paraphrase German Copy
**Problem:** Translating or improvising German text

**Solution:** Use **exact copy** from specifications. No variations.

### ❌ Don't: Display Email Addresses
**Problem:** Showing emails in UI violates privacy principle

**Solution:** Email addresses are PII (Personally Identifiable Information), never displayed anywhere in UI. Only first names are shown. If you need to identify users, use first name + booking ID, never email address.

### ❌ Don't: Skip Business Rules
**Problem:** Implementing features without checking applicable business rules

**Solution:** Always review [`docs/foundation/business-rules.md`](docs/foundation/business-rules.md) first.

---

## Getting Help

### If Documentation is Unclear

1. Check cross-references to related sections
2. Look for examples in the same document
3. Search for keywords across all docs (Ctrl+F / Cmd+F)
4. Read section-specific `CLAUDE.md` files
5. **Ask the user for clarification** (don't guess)

### If You Encounter Conflicts

1. **Between docs:** Ask user which is correct, then update both
2. **Code vs docs:** Trust docs, fix code (unless docs are clearly wrong)
3. **Ambiguous requirements:** Ask user, document answer

### What to Include When Asking

- What you're trying to implement
- What the documentation says (quote it)
- What's unclear or ambiguous
- What you've already tried
- Reference specific files and line numbers

---

## Quality Checklist

**Before considering work complete:**

- [ ] All acceptance criteria met
- [ ] Business rules followed (BR-001 to BR-029)
- [ ] German copy matches specifications exactly
- [ ] Tests pass (backend + frontend)
- [ ] Type checks pass (mypy + tsc)
- [ ] Linting passes (ruff + eslint)
- [ ] Mobile tested (375px width minimum)
- [ ] Permissions enforced correctly
- [ ] Privacy rules respected (no email display)
- [ ] Documentation still accurate (update if needed)

---

## Implementation Readiness

### ✅ Ready to Start

This project has:
- Complete business requirements
- All user journeys documented
- Data model fully specified
- German copy for all UI text
- Architecture decisions documented
- 8-phase BDD implementation roadmap
- Test-first approach defined

### 🎯 Start Here

**To begin implementation:**

1. Read [`docs/implementation/README.md`](docs/implementation/README.md)
2. Start with Phase 0: [`docs/implementation/phase-0-foundation.md`](docs/implementation/phase-0-foundation.md)
3. Follow the BDD workflow: Tests → Implementation → Verification
4. Reference section `CLAUDE.md` files as you work

---

## Helpful Commands

**Backend (run from `api/` directory):**
```bash
# Run all tests
cd api && pytest

# Run with coverage report
cd api && pytest --cov=app

# Type check (checks app/ directory)
cd api && mypy app/

# Lint (checks app/ directory)
cd api && ruff check app/
```

**Frontend (run from `web/` directory):**
```bash
# Run all E2E tests
cd web && npx playwright test

# Run in headed mode (see browser)
cd web && npx playwright test --headed

# Type check (checks TypeScript files)
cd web && npm run type-check

# Lint (checks JavaScript/TypeScript files)
cd web && npm run lint
```

**Git:**
```bash
# Check current status
git status

# Commit changes
git add . && git commit -m "feat: description"

# Push to remote
git push -u origin <branch-name>
```

---

## Summary

**Remember:**
- 📚 **Documentation is truth** (not assumptions)
- 🇩🇪 **German UI only** (informal "du", exact copy from specs)
- 📱 **Mobile-first** (iPhone 8 class minimum)
- 🔒 **Privacy by design** (no email display)
- 👥 **Three fixed approvers** (Ingeborg, Cornelia, Angelika)
- 📅 **Inclusive end dates** (BR-001)
- ⚡ **First-wins concurrency** (BR-024, BR-029)
- ✅ **Test-first** (BDD with Gherkin)
- 🎯 **Type safety** (catch errors early)

**When in doubt:**
1. Read the docs
2. Check section `CLAUDE.md`
3. Ask the user
4. Don't assume

---

## Next Steps

**New to this project?**
→ Read [`claude/README.md`](claude/README.md) for detailed workflow guidance

**Ready to implement?**
→ Start at [`docs/implementation/README.md`](docs/implementation/README.md)

**Working on a specific section?**
→ Check that section's `CLAUDE.md` file for context

**Need to maintain docs?**
→ See [`claude/documentation-workflow.md`](claude/documentation-workflow.md)

---

**Good luck building! The documentation is comprehensive, the architecture is sound, and the roadmap is clear. You have everything you need to succeed.**
