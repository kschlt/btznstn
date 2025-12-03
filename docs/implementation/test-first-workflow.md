# Test-First Development Workflow (Draft)

**Status:** Draft  
**Date:** 2025-01-19  
**Note:** This is a development workflow guide, not an architectural decision. See [CLAUDE.md](CLAUDE.md) for the detailed implementation workflow.

---

## Overview

This document describes the **test-first development (BDD)** approach used in this project. This workflow ensures test coverage before implementation and validates business rules throughout development.

---

## Core Principles

### Test-First Development (BDD)

- **Write tests BEFORE implementation** - Tests define the expected behavior
- **Use Gherkin scenarios** - Each phase has Gherkin scenarios that guide test writing
- **Red-Green-Refactor cycle** - Tests fail initially (red phase), then pass after implementation (green phase)

### Why Test-First?

**Benefits:**
- Ensures test coverage before implementation
- Validates business rules (BR-001 to BR-029) explicitly
- Supports incremental development (test each phase)
- Provides fast feedback
- Enables confident refactoring

**Why NOT Test-After:**
- Test-after approach risks missing edge cases
- Test-after approach may skip business rule validation
- Bugs discovered late in the process (see Phase 1 lessons learned in [CLAUDE.md](CLAUDE.md))

---

## Workflow Requirements

### MUST (Required)

- **MUST write tests before implementation** - Test-first approach ensures test coverage
- **MUST use Gherkin scenarios for business rule validation** - BDD approach validates business rules explicitly
- **MUST write failing tests first (red phase)** - Tests must fail initially, then pass after implementation
- **MUST validate business rules in tests** - Tests must reference BR-001 to BR-029 where applicable

### MUST NOT (Forbidden)

- **MUST NOT write tests after implementation** - Violates test-first approach
- **MUST NOT skip business rule validation in tests** - Business rules must be validated in tests
- **MUST NOT write tests that pass before implementation** - Tests must fail initially (red phase)

---

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Test Order | Write tests before implementation | Write tests after implementation |
| Approach | BDD with Gherkin scenarios | Test-after, no tests |
| Test State | Tests fail initially (red phase) | Tests pass before implementation |
| Coverage | Tests validate business rules | Tests skip business rule validation |

---

## Scope

### Applies To

- **ALL development phases** (Phase 0 through Phase 8)
- **File patterns:**
  - `api/tests/**/*.py` - Backend test files
  - `web/tests/**/*.ts` - Frontend test files
- **Gherkin scenarios:** `docs/implementation/phase-*.md`

---

## Validation

### Verification Commands

- **Verify tests exist before implementation files** - Check git history for test file creation before implementation
- **Check business rule references:**
  - `grep -r "BR-\d\d\d" api/tests/` (should reference business rules in tests)
  - `grep -r "BR-\d\d\d" web/tests/` (should reference business rules in tests)

### Common Pitfalls

- Many code examples show test-after approach - **MUST write tests before implementation**
- Check test file creation dates vs implementation dates to verify test-first approach

---

## Related Documentation

**Testing Frameworks:**
- [ADR-020](../../docs/architecture/adr-020-backend-testing-framework.md) - Backend Testing Framework (Pytest)
- [ADR-021](../../docs/architecture/adr-021-frontend-testing-framework.md) - Frontend Testing Framework (Playwright)
- [ADR-022](../../docs/architecture/adr-022-frontend-unit-component-testing.md) - Frontend Unit/Component Testing

**Test Patterns:**
- [ADR-009](../../docs/architecture/adr-009-test-data-factory-functions.md) - Test Data Factory Functions

**Implementation Workflow:**
- [CLAUDE.md](CLAUDE.md) - Detailed 7-step implementation workflow with role separation
- [README.md](README.md) - BDD workflow overview

**Gherkin Scenarios:**
- `docs/implementation/phase-*.md` - Gherkin scenarios for each phase

---

## Implementation Files

- `api/tests/` - Backend test files (written before implementation)
- `web/tests/` - Frontend test files (written before implementation)

---

## Notes

This workflow is complementary to the detailed implementation workflow described in [CLAUDE.md](CLAUDE.md), which includes the 7-step process with role separation and four-eyes test review.

