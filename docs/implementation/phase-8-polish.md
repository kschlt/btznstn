# Phase 8: Polish & Production

## Goal
Performance optimization, accessibility, and production readiness.

**Duration:** 2-3 days | **Dependencies:** All previous phases

---

## User Stories

### US-8.1: Performance Optimization
```gherkin
Feature: Performance

  Scenario: Fast page load
    Given I am on the calendar page
    When I measure page load time
    Then Time to Interactive should be <3s
    And Lighthouse Performance score should be ≥90

  Scenario: Efficient API queries
    Given bookings are loaded
    When I inspect network requests
    Then N+1 queries should be eliminated (eager loading)
```

### US-8.2: Accessibility (WCAG AA)
```gherkin
Feature: Accessibility

  Scenario: No accessibility violations
    Given I run axe-core on all pages
    Then I should see 0 violations

  Scenario: Keyboard navigation works
    Given I am on the calendar
    When I navigate using only keyboard (Tab, Enter, Esc)
    Then I can access all interactive elements
    And focus indicators are visible

  Scenario: Screen reader compatible
    Given I use a screen reader
    Then all buttons have aria-labels
    And form fields have associated labels
```

### US-8.3: Production Deployment
```gherkin
Feature: Production Deployment

  Scenario: API deployed to Fly.io
    Given I push to main branch
    When GitHub Actions runs
    Then backend should deploy to Fly.io Frankfurt
    And health check should pass

  Scenario: Web deployed to Vercel
    Given I push to main branch
    Then frontend should deploy to Vercel
    And preview URL should be accessible
```

**Tasks:**
- [ ] Optimize database queries (add missing indexes)
- [ ] Add API response caching (if needed)
- [ ] Optimize bundle size (code splitting)
- [ ] Run Lighthouse audits (fix issues)
- [ ] Run axe-core (fix violations)
- [ ] Test keyboard navigation
- [ ] Configure Fly.io production app
- [ ] Configure Vercel production deployment
- [ ] Set up environment variables (production)
- [ ] Test production deployment end-to-end

**Definition of Done:**
- [ ] Lighthouse Performance ≥90
- [ ] Lighthouse Accessibility = 100
- [ ] Zero axe-core violations
- [ ] Production deployment works
- [ ] All tests pass in CI
- [ ] Documentation complete

**Result:** Production-ready application! 🎉
