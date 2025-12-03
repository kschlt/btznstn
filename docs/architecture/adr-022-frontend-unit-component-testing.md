# ADR-022: Frontend Unit/Component Testing Framework

**Status:** Accepted
**Date:** 2025-01-19
**Deciders:** Solution Architect
**Context:** Need unit and component testing framework for Next.js frontend code

---

## Context

Need testing framework for frontend code that:
- Tests TypeScript/JavaScript logic (utilities, models, API client)
- Tests React Client Components in isolation
- Validates API client integration with backend
- Provides fast test execution for iterative development
- Works with Next.js App Router
- Supports TypeScript
- Provides clear error messages for debugging

---

## Decision

Use **Vitest + React Testing Library** for frontend unit and component testing.

---

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Test Runner | Vitest | Jest, manual testing |
| Component Testing | React Testing Library | Enzyme, manual testing, testing implementation details |
| Test Structure | Arrange-Act-Assert pattern | Unstructured tests |
| Query Methods | Accessible queries (getByRole, getByLabelText) | getByTestId, querySelector |
| TypeScript | Native TypeScript support | JavaScript-only testing |
| Speed | Fast test execution (<200ms) | Slow test runners (>500ms) |

---

## Rationale

**Why Vitest + React Testing Library:**
- Vitest provides fast test execution (50-200ms vs Jest's 500-2000ms) and native TypeScript/ESM support → **Constraint:** MUST use Vitest for frontend unit tests
- React Testing Library tests user behavior with accessible queries → **Constraint:** MUST use React Testing Library for component testing

**Why NOT Jest:**
- Jest is slower than Vitest (500-2000ms vs 50-200ms) → **Violation:** Slower tests violate fast test execution requirement
- Jest has limited ESM support → **Violation:** Limited ESM support violates modern module system requirement

**Why NOT Enzyme:**
- Enzyme tests implementation details → **Violation:** Testing implementation details violates user-centric testing requirement, breaks when implementation changes

---

## Consequences

### MUST (Required)

- MUST use Vitest for frontend unit tests
- MUST use React Testing Library for component testing
- MUST use accessible queries (getByRole, getByLabelText, getByText)
- MUST use Arrange-Act-Assert pattern
- MUST test API client integration
- MUST test utility functions and models
- MUST write descriptive test names

### MUST NOT (Forbidden)

- MUST NOT use Jest for frontend unit tests
- MUST NOT use implementation detail queries (getByTestId, querySelector)
- MUST NOT skip component testing
- MUST NOT skip API client testing
- MUST NOT test implementation details

### Trade-offs

- Many code examples use Jest - MUST use Vitest. MUST NOT use Jest. Check for Jest imports in test files.
- Code examples may use getByTestId - MUST use accessible queries (getByRole, getByLabelText). MUST NOT use getByTestId. Check for test-id queries.
- Code examples may test implementation details - MUST test user behavior. MUST NOT test internal state or implementation. Check for component state assertions.

### Code Examples

```typescript
// ❌ WRONG: Using Jest
import { describe, it, expect } from '@jest/globals'

// ❌ WRONG: Testing implementation details
test('button has disabled prop', () => {
  const { container } = render(<BookingForm />)
  const button = container.querySelector('button')
  expect(button?.getAttribute('disabled')).toBe('')
})

// ❌ WRONG: Using test-id queries
test('submit button works', () => {
  render(<BookingForm />)
  const button = screen.getByTestId('submit-button')  // Implementation detail
  fireEvent.click(button)
})

// ✅ CORRECT: Testing user behavior with accessible queries
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, test, expect } from 'vitest'

test('submit button disabled when email invalid', () => {
  // Arrange
  render(<BookingForm />)
  
  // Act
  const emailInput = screen.getByLabelText('Email')
  fireEvent.change(emailInput, { target: { value: 'invalid-email' } })
  
  // Assert
  const submitButton = screen.getByRole('button', { name: /submit/i })
  expect(submitButton).toBeDisabled()
})
```

**Note:** Only include examples showing specific pitfalls. Generic patterns (LLMs already know) should be omitted.

### Applies To

- ALL frontend unit tests (all phases)
- ALL frontend Client Component tests (Phase 5, 6, 7, 8)
- File patterns: `web/**/*.test.ts`, `web/**/*.test.tsx`, `web/**/*.spec.ts`, `web/**/*.spec.tsx`
- Note: Server Components must be tested with Playwright E2E (see ADR-021)

### Validation Commands

- `grep -r "jest\|@testing-library/jest" web/` (should be empty - must use Vitest)
- `grep -r "getByTestId\|querySelector" web/**/*.test.*` (should be empty - must use accessible queries)
- `npm run test` (must pass - runs Vitest)
- `npm run test:coverage` (coverage report)
- `npm run test:watch` (watch mode for iterative development)

**Related ADRs:**
- [ADR-002](adr-002-frontend-framework.md) - Frontend Framework (Next.js)
- [ADR-006](adr-006-type-safety.md) - Type Safety (TypeScript strict mode)
- [ADR-021](adr-021-frontend-testing-framework.md) - Frontend UI/E2E Testing Framework (Playwright)

**Workflow:**
- [Test-First Workflow](../../docs/implementation/test-first-workflow.md) - Test-first development approach (BDD)

---

## References

**Related ADRs:**
- [ADR-002](adr-002-frontend-framework.md) - Frontend Framework (Next.js)
- [ADR-006](adr-006-type-safety.md) - Type Safety (TypeScript strict mode)
- [ADR-021](adr-021-frontend-testing-framework.md) - Frontend UI/E2E Testing Framework (Playwright)

**Workflow:**
- [Test-First Workflow](../../docs/implementation/test-first-workflow.md) - Test-first development approach (BDD)

**Tools:**
- [Vitest](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react/)

**Implementation:**
- `web/vitest.config.ts` - Vitest configuration
- `web/**/*.test.ts` - Unit test files
- `web/**/*.test.tsx` - Component test files

