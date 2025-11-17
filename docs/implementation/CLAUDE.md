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

## BDD Workflow (Test-First)

**For every feature:**

1. **Write failing tests first**
   - Backend: Pytest (unit + integration)
   - Frontend: Playwright (E2E)

2. **Implement features**
   - Follow specifications
   - Enforce business rules
   - Use exact German copy

3. **Tests pass**
   - All scenarios green
   - Type checks pass (mypy + tsc)
   - Linting passes (ruff + eslint)

4. **Refactor**
   - Clean up code
   - Maintain test coverage

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
Phase 5 (Frontend Calendar)
    ↓
Phase 6 (Frontend Booking)
    ↓
Phase 7 (Approver Interface)
    ↓
Phase 8 (Polish & Production)
```

**Don't skip phases** - each builds on previous.

## Critical Testing Requirements

**Every phase must have:**
- Gherkin scenarios (Given/When/Then)
- Backend tests (pytest)
- Frontend tests (playwright) if UI involved
- ≥80% code coverage target

**Run tests:**
```bash
# Backend
pytest tests/unit/
pytest tests/integration/

# Frontend
npx playwright test
npx playwright test --project="iPhone 8"
```

## Definition of Done (Per Phase)

- [ ] All Gherkin scenarios pass
- [ ] Backend + frontend tests pass
- [ ] Type checks pass (mypy + tsc)
- [ ] Linting passes (ruff + eslint)
- [ ] Code coverage ≥80%
- [ ] German copy matches specs
- [ ] Business rules enforced
- [ ] Mobile tested (375px width)
- [ ] Documentation updated if needed

## Key Implementation Tips

**Before coding:**
- Read the phase document completely
- Understand all user stories
- Review applicable business rules
- Check German copy requirements

**While coding:**
- Write tests first (red → green → refactor)
- Reference business rules in comments (e.g., "# Per BR-001")
- Use exact German copy from specs
- Commit frequently with clear messages

**After coding:**
- Run full test suite
- Check type safety
- Test on mobile viewport
- Review against acceptance criteria

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

**Phases 5-7 (Frontend):**
- Design for 375px first (mobile)
- 44×44pt tap targets
- No hover dependencies
- Use exact German copy from specs

## Parallel Work Opportunities

**Some overlap possible:**
- Phase 5-7 work on different UI areas
- Phase 4 can start while Phase 2-3 finish

**But maintain phase order for core dependencies.**

---

**Ready to start?** Begin with [`phase-0-foundation.md`](phase-0-foundation.md).
