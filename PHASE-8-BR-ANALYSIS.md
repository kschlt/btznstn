# Phase 8: Polish & Production - Business Rules Analysis

## Executive Summary

Phase 8 Polish & Production focuses on performance optimization, accessibility compliance, and production deployment. While Phase 8 is not feature-heavy (it doesn't implement new business logic), it **enforces compliance with existing business rules** and ensures production-grade quality.

**Key focus:**
- Performance: Eliminate N+1 queries, optimize bundle size, achieve Lighthouse 90+
- Accessibility: WCAG AA compliance, keyboard navigation, screen reader support
- Production: Deploy to Fly.io and Vercel, enforce rate limits, run background jobs reliably

---

## Phase 8 User Stories

### US-8.1: Performance Optimization
### US-8.2: Accessibility (WCAG AA)
### US-8.3: Production Deployment

---

# US-8.1: Performance Optimization

## 1. Applicable Business Rules

### BR-023: Approver Lists (CRITICAL FOR PERFORMANCE)

**Why it matters:**
- Approvers view outstanding and history lists sorted by `LastActivityAt DESC`
- **Without eager loading:** N+1 query problem (1 query per approval, scales with number of items)
- **Without indexes:** Date range queries slow (calendar view, conflict detection)
- **Without pagination:** Loading hundreds of items freezes UI

**Implementation impact:**
- All approver list queries must use `selectinload(Booking.approvals)` to prevent N+1
- All date queries must use indexes on `(start_date, end_date, status)`
- All list endpoints must paginate or infinite-scroll

**Reference:** `docs/foundation/business-rules.md` lines 411-428

---

### BR-010: Tokens and Links (PRODUCTION RELIABILITY)

**Why it matters:**
- Tokens never expire, never revoked → **production must cache user context**
- Action links are idempotent → **endpoints must return result page, never 404/500**
- Links always redirect → **production must handle retry attempts gracefully**

**Implementation impact:**
- API must validate tokens on every request (no session cache needed, but safe to cache user context)
- Approval/deny/cancel endpoints must be idempotent (check current state, return same response)
- Production error handling must never let action links fail

**Reference:** `docs/foundation/business-rules.md` lines 262-272

---

## 2. Performance Requirements

### Backend Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| API Response Time (p95) | <500ms | Per `technical-constraints.md` |
| Calendar Load | <1s | Month view with all bookings |
| List Query | <200ms | Approver outstanding/history |
| Create Booking | <300ms | With email notification |
| Database Query | <100ms | With eager loading |

### Frontend Performance Targets

| Metric | Target | Acceptance Criteria |
|--------|--------|-------------------|
| Time to Interactive (TTI) | <3s | Per US-8.1 Gherkin |
| Lighthouse Performance | ≥90 | Per US-8.1 Gherkin |
| First Contentful Paint (FCP) | <1.5s | Derived from TTI target |
| Largest Contentful Paint (LCP) | <2.5s | Derived from TTI target |
| Cumulative Layout Shift (CLS) | <0.1 | Core Web Vitals |
| Total Bundle Size | <200KB | After code splitting + minification |
| Gzip Size | <60KB | Compressed transfer |

### Query Optimization Checklist

- [ ] Calendar view query (month overlap) uses index on `(start_date, end_date, status)`
- [ ] Approver outstanding/history queries use `selectinload(Booking.approvals)` (no N+1)
- [ ] Conflict detection query uses transaction + index
- [ ] All list queries use `order_by(Booking.last_activity_at.desc())`
- [ ] No missing indexes on foreign keys or commonly filtered columns
- [ ] Database connection pooling configured (recommended: 10-20 connections)

### Code Optimization Checklist

- [ ] Code splitting: Separate bundles for critical path vs. optional features
- [ ] Lazy loading: Calendar view, approval forms, details dialogs
- [ ] Image optimization: Compress affiliation color swatches
- [ ] CSS optimization: Remove unused styles, minify
- [ ] JavaScript optimization: Tree-shake unused dependencies
- [ ] Minification: All JS/CSS minified in production build

---

## 3. Test Plan: Performance

### Backend Performance Tests

**Database Query Performance:**
1. `test_calendar_query_eager_loads_approvals` - Verifies selectinload used, no N+1
2. `test_calendar_query_uses_date_index` - EXPLAIN query plan shows index usage
3. `test_approver_outstanding_query_no_n_plus_one` - Counts SQL statements
4. `test_approver_history_query_no_n_plus_one` - Counts SQL statements
5. `test_conflict_detection_query_response_time` - Benchmark <100ms

**API Response Time Benchmarks:**
6. `test_get_calendar_response_time` - Measure p95 <500ms
7. `test_get_approver_outstanding_response_time` - Measure <200ms
8. `test_post_create_booking_response_time` - Measure <300ms (excluding email)
9. `test_get_booking_details_response_time` - Measure <100ms

### Frontend Performance Tests

**Lighthouse Audits:**
10. `test_lighthouse_performance_score_gte_90` - Run Lighthouse, assert ≥90
11. `test_lighthouse_best_practices` - Run Lighthouse best practices
12. `test_lighthouse_seo` - Run Lighthouse SEO (mobile-first)

**Bundle Size Validation:**
13. `test_bundle_size_gzip_less_than_60kb` - Bundle gzip <60KB
14. `test_main_bundle_has_code_splitting` - Verify chunks split properly
15. `test_calendar_component_lazy_loads` - Lazy load calendar view

**Core Web Vitals:**
16. `test_time_to_interactive_less_than_3s` - Measure TTI <3s
17. `test_first_contentful_paint_less_than_1.5s` - Measure FCP <1.5s
18. `test_largest_contentful_paint_less_than_2.5s` - Measure LCP <2.5s
19. `test_cumulative_layout_shift_less_than_0.1` - Measure CLS <0.1

**Load Test:**
20. `test_api_handles_concurrent_requests_100` - 100 concurrent calendar requests
21. `test_database_connection_pool_under_load` - Verify no connection exhaustion

### Total Performance Tests: ~21

---

## 4. Gherkin Scenarios: US-8.1

```gherkin
Feature: Performance Optimization

  Scenario: Fast page load meets Time to Interactive target
    Given I am on the calendar page
    When I measure page load time
    Then Time to Interactive should be <3s
    And First Contentful Paint should be <1.5s
    And Largest Contentful Paint should be <2.5s

  Scenario: Lighthouse Performance score meets target
    Given I am on the calendar page
    When I run Lighthouse audit (mobile)
    Then Performance score should be ≥90
    And Best Practices score should be ≥90

  Scenario: Efficient API queries prevent N+1 problems
    Given bookings are loaded for approver outstanding list
    When I inspect network requests (SQL query count)
    Then the approver query should be ≤3 SQL statements (main query + approvals + parties)
    And selectinload(Booking.approvals) should be used

  Scenario: Calendar month query uses indexes
    Given the database has 1000+ bookings across multiple months
    When I query calendar for February 2025
    Then the query should use index on (start_date, end_date, status)
    And response time should be <100ms

  Scenario: Bundle size remains under control
    Given the frontend build is minified and gzipped
    When I check the bundle size
    Then main bundle.js gzip should be <60KB
    And chunks are code-split (vendor, main, calendar components separate)

  Scenario: API responses are fast
    Given I make requests to calendar API
    When I measure response times
    Then p95 response time should be <500ms
    And create booking API (excluding email) should be <300ms
    And approver list API should be <200ms
```

---

# US-8.2: Accessibility (WCAG AA)

## 1. Applicable Business Rules

### BR-011: German-Only UI (ACCESSIBILITY MUST PRESERVE LANGUAGE)

**Why it matters:**
- All UI text is German (informal "du")
- Accessibility tools (screen readers, keyboard navigation) must work with German copy
- Error messages, button labels, ARIA labels must all be in German
- Accessibility testing must include German text validation

**Implementation impact:**
- All ARIA labels must be in German
- All error messages must remain in German from spec
- Screen reader testing with German locale
- Keyboard navigation labels in German

**Reference:** `docs/foundation/business-rules.md` lines 291-300; `docs/constraints/technical-constraints.md` lines 51-68

---

### BR-016: Party Size Display (ACCESSIBILITY CONCERN)

**Why it matters:**
- Party size always displays as "n Personen" (even for 1 person)
- Screen readers must accurately read "1 Personen" (grammatically incorrect but spec-required)
- Accessible markup must convey both the number and "Personen" label

**Implementation impact:**
- ARIA labels should clarify: "1 Personen" (1 person)
- Form validation errors must be in German from spec

**Reference:** `docs/foundation/business-rules.md` lines 302-310

---

### BR-019: First Name Validation (ERROR MESSAGE ACCESSIBILITY)

**Why it matters:**
- Validation error: "Bitte gib einen gültigen Vornamen an (Buchstaben, Leerzeichen, Bindestrich, Apostroph; max. 40 Zeichen)."
- Error must be accessible to screen readers (ARIA live region)
- Input field must have proper label and error association

**Implementation impact:**
- Form input must have `<label>` element with `for` attribute
- Error message must have `role="alert"` or aria-live region
- Error must associate with input via `aria-describedby`

**Reference:** `docs/foundation/business-rules.md` lines 330-349

---

### BR-020: Link Detection in Text Fields (ERROR MESSAGE ACCESSIBILITY)

**Why it matters:**
- When user enters link (http://, https://, www, mailto:), error shows:
  - "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden."
- Error must be accessible to screen readers
- User must be able to retry with keyboard only

**Implementation impact:**
- Error message displays in accessible manner (aria-live)
- Form can be corrected and resubmitted with keyboard only

**Reference:** `docs/foundation/business-rules.md` lines 352-368

---

## 2. Accessibility Requirements

### WCAG AA Compliance Checklist

| Criterion | Requirement | Test Method |
|-----------|-----------|------------|
| **1.4.3 Contrast (AA)** | Text ≥4.5:1, UI components ≥3:1 | axe-core contrast checker |
| **1.4.11 Non-Text Contrast (AA)** | UI components ≥3:1 | axe-core, manual inspection |
| **2.1.1 Keyboard** | All functionality via keyboard | Playwright keyboard tests |
| **2.1.2 No Keyboard Trap** | Can tab out of elements | Keyboard navigation test |
| **2.4.3 Focus Order** | Logical tab order | Keyboard test, axe-core |
| **2.4.7 Focus Visible** | Focus indicator always visible | Visual test, CSS validation |
| **3.3.1 Error Identification** | Errors identified to users | Screen reader test |
| **3.3.2 Labels or Instructions** | Form inputs labeled | axe-core, HTML validation |
| **3.3.4 Error Prevention** | Critical actions reversible | Gherkin scenarios |
| **4.1.2 Name, Role, Value** | All interactive elements have accessible names | axe-core, screen reader test |
| **4.1.3 Status Messages** | Status messages announced | axe-core, screen reader test |

### Mobile & Touch Accessibility

| Requirement | Details |
|-----------|---------|
| **Tap Target Size** | Minimum 44×44 points (44×44 CSS px on mobile) |
| **Touch Spacing** | Minimum 8px between interactive elements |
| **Mobile Viewport** | Must work at 375px width (iPhone 8) |
| **No Hover** | No information hidden behind hover states |
| **Swipe Gestures** | Supported but not required for core functionality |

### Keyboard Navigation Checklist

- [ ] Tab key moves through interactive elements in logical order
- [ ] Shift+Tab navigates backwards
- [ ] Enter/Space activates buttons
- [ ] Enter submits forms
- [ ] Esc closes dialogs/modals
- [ ] Arrow keys navigate calendar dates (per BR on desktop enhancements)
- [ ] No keyboard traps (user can always escape)
- [ ] Focus indicator visible at all times (minimum 2px, contrast ≥3:1)
- [ ] Date pickers keyboard accessible (arrow keys, Enter to select)

### Screen Reader Support Checklist

- [ ] All buttons have accessible names (aria-label if icon-only)
- [ ] All form inputs have associated `<label>` elements
- [ ] Form error messages associated with inputs via aria-describedby
- [ ] Status messages announced via aria-live="polite"
- [ ] Calendar structure (table or proper ARIA roles)
- [ ] Affiliation colors not the only indicator (text label needed)
- [ ] Status badges have alt text or aria-label
- [ ] List items properly marked (e.g., `<li>` elements)
- [ ] Links have meaningful text (not "click here")

### Color Contrast Validation

| Element | Minimum Ratio | Test Target |
|---------|-------------|------------|
| **Text on background** | 4.5:1 | All body text, labels |
| **Large text (18pt+)** | 3:1 | Headings |
| **UI components** | 3:1 | Buttons, borders, affiliation colors |
| **Focus indicator** | 3:1 (to adjacent color) | Keyboard focus outline |
| **Affiliation colors** | 4.5:1 with text | Text on Ingeborg/Cornelia/Angelika backgrounds |

**Affiliation Color Contrast (from `ui-screens.md` line 70-75):**
- Ingeborg: `#C1DBE3` (light blue)
- Cornelia: `#C7DFC5` (light green)
- Angelika: `#DFAEB4` (light pink)

**Critical:** Ensure dark text (or light text) on these backgrounds meets 4.5:1 ratio.

---

## 3. Test Plan: Accessibility

### Automated Tests (axe-core)

**Comprehensive Page Coverage:**
1. `test_calendar_page_zero_axe_violations` - Full calendar page (month view)
2. `test_calendar_year_view_zero_axe_violations` - Year view
3. `test_create_booking_form_zero_axe_violations` - Create form
4. `test_edit_booking_form_zero_axe_violations` - Edit form
5. `test_booking_details_viewer_zero_axe_violations` - Details (public)
6. `test_booking_details_requester_zero_axe_violations` - Details (requester)
7. `test_booking_details_approver_zero_axe_violations` - Details (approver)
8. `test_approver_overview_outstanding_zero_axe_violations` - Outstanding tab
9. `test_approver_overview_history_zero_axe_violations` - History tab
10. `test_error_dialog_zero_axe_violations` - Error scenarios

### Keyboard Navigation Tests

**Calendar Navigation:**
11. `test_keyboard_calendar_arrow_keys_navigate_dates` - Arrow keys move selection
12. `test_keyboard_calendar_enter_opens_booking` - Enter opens details
13. `test_keyboard_calendar_escape_closes_details` - Esc closes dialogs

**Form Navigation:**
14. `test_keyboard_form_tab_focuses_all_fields` - Tab navigates through form
15. `test_keyboard_form_shift_tab_reverses` - Shift+Tab goes backward
16. `test_keyboard_form_enter_submits` - Enter submits form
17. `test_keyboard_form_escape_cancels` - Esc cancels form

**Dialog Navigation:**
18. `test_keyboard_dialog_tab_stays_within` - Tab loops within dialog
19. `test_keyboard_dialog_escape_closes` - Esc closes dialog
20. `test_keyboard_no_trap_all_elements_escapable` - No keyboard traps

### Focus & Visual Indicator Tests

**Focus Visibility:**
21. `test_focus_indicator_visible_all_buttons` - All buttons show focus
22. `test_focus_indicator_contrast_ratio_gte_3` - Focus outline ≥3:1 contrast
23. `test_focus_indicator_size_minimum_2px` - Focus outline ≥2px
24. `test_focus_order_logical_calendar_form` - Tab order is logical
25. `test_focus_order_logical_approver_list` - Tab order in list view

### Screen Reader Tests

**Landmark & Semantic Structure:**
26. `test_screen_reader_calendar_has_main_landmark` - <main> tag used
27. `test_screen_reader_form_has_fieldset_legend` - Fieldsets labeled
28. `test_screen_reader_button_labels_present` - All buttons have names
29. `test_screen_reader_form_labels_associated` - Inputs have `<label for>`
30. `test_screen_reader_error_aria_live` - Error messages announced

**Content Accessibility:**
31. `test_screen_reader_party_size_text_label` - "Personen" text readable
32. `test_screen_reader_status_badge_aria_label` - Status announced
33. `test_screen_reader_affiliation_color_not_only_indicator` - Has text label
34. `test_screen_reader_link_text_meaningful` - Links descriptive

### Color Contrast Tests

**Text Contrast:**
35. `test_contrast_body_text_gte_4.5` - All body text ≥4.5:1
36. `test_contrast_heading_text_gte_4.5` - Headings ≥4.5:1
37. `test_contrast_button_text_gte_4.5` - Button text ≥4.5:1
38. `test_contrast_label_text_gte_4.5` - Form labels ≥4.5:1

**Component Contrast:**
39. `test_contrast_button_border_gte_3` - Button border ≥3:1
40. `test_contrast_focus_outline_gte_3` - Focus outline ≥3:1
41. `test_contrast_affiliation_ingeborg_text_gte_4.5` - Ingeborg color + text ≥4.5:1
42. `test_contrast_affiliation_cornelia_text_gte_4.5` - Cornelia color + text ≥4.5:1
43. `test_contrast_affiliation_angelika_text_gte_4.5` - Angelika color + text ≥4.5:1
44. `test_contrast_status_badge_gte_3` - Status badge ≥3:1

### Mobile Accessibility Tests

**Touch Targets:**
45. `test_touch_target_buttons_minimum_44x44` - All buttons ≥44×44pt
46. `test_touch_target_spacing_minimum_8px` - 8px spacing between targets
47. `test_touch_target_form_inputs_44x44` - Form inputs ≥44×44pt
48. `test_touch_target_date_picker_cells_44x44` - Calendar cells ≥44×44pt

**Mobile Viewport:**
49. `test_mobile_viewport_375_renders_correctly` - 375px viewport works
50. `test_mobile_no_horizontal_scroll` - No horizontal scrolling
51. `test_mobile_responsive_text_readable` - Text readable at mobile size

### Lighthouse Accessibility Audit

52. `test_lighthouse_accessibility_score_100` - Lighthouse accessibility = 100

### German Text Accessibility

53. `test_german_aria_labels_present` - ARIA labels in German
54. `test_german_error_messages_accessible` - Error messages from spec, screen-readable
55. `test_german_form_labels_correct` - Form labels match spec

### Total Accessibility Tests: ~55

---

## 4. Gherkin Scenarios: US-8.2

```gherkin
Feature: Accessibility (WCAG AA)

  Scenario: No accessibility violations detected
    Given I run axe-core on the calendar page
    When I scan for violations
    Then I should see 0 violations
    And all elements should pass automated checks

  Scenario: Keyboard navigation works for calendar
    Given I am on the calendar page
    When I navigate using only keyboard (Tab, Arrow keys, Enter, Esc)
    Then I can move between dates with arrow keys
    And I can open booking with Enter
    And I can close details with Esc
    And I never get trapped (can always escape)

  Scenario: Keyboard navigation works for forms
    Given I am on the create booking form
    When I navigate using Tab and Shift+Tab
    Then all form fields are reachable via keyboard
    And I can submit with Enter
    And I can cancel with Esc

  Scenario: Focus indicators are always visible
    Given I navigate with keyboard
    When I move focus to any interactive element
    Then a visible focus outline is shown
    And the outline has contrast ratio ≥3:1

  Scenario: Screen reader compatible buttons
    Given I use a screen reader (NVDA, JAWS, VoiceOver)
    When I navigate the page
    Then all buttons have accessible names
    And icon-only buttons have aria-labels
    And button purpose is clear (e.g., "Approve" not "OK")

  Scenario: Screen reader compatible form fields
    Given I use a screen reader
    When I navigate form inputs
    Then each input has an associated label
    And error messages are announced
    And required fields are marked

  Scenario: Color is not the only indicator
    Given I view status badges and affiliation colors
    When I check if information is conveyed only by color
    Then status is also shown as text (e.g., "Ausstehend", "Bestätigt")
    And affiliation is shown as text, not just color

  Scenario: Text contrast meets WCAG AA standards
    Given I measure color contrast on all text and UI components
    When I compare foreground and background colors
    Then body text has contrast ratio ≥4.5:1
    And UI components have contrast ratio ≥3:1

  Scenario: Touch targets are large enough
    Given I view the page on mobile (375px viewport)
    When I check interactive elements
    Then all buttons are at least 44×44 points
    And spacing between targets is at least 8px
    And tap targets are easy to hit

  Scenario: Page works at 375px width (mobile-first)
    Given I set viewport to iPhone 8 size (375×667px)
    When I interact with the application
    Then all content is accessible
    And no horizontal scrolling is required
    And text remains readable
```

---

# US-8.3: Production Deployment

## 1. Applicable Business Rules

### BR-012: Rate Limits (MUST ENFORCE IN PRODUCTION)

**Why it matters:**
- Submission limit: 10 bookings per day per email
- Per-IP limit: 30 requests per hour per IP
- Recovery limit: 5 link recovery requests per hour per email
- Soft cooldown: 60 seconds on link recovery per email/IP

**Implementation impact:**
- Backend must track and enforce these limits
- All limits configurable via environment variables
- Rate limit exceeded → error with remaining time
- Cooldown period shows neutral message

**Reference:** `docs/foundation/business-rules.md` lines 373-389

---

### BR-021: Soft Cooldown on Link Recovery (RATE LIMIT VARIANT)

**Why it matters:**
- 60-second cooldown on link recovery prevents abuse
- User sees message: "Bitte warte kurz – wir haben dir deinen persönlichen Link gerade erst gesendet."
- No enumeration (don't reveal if email exists)

**Implementation impact:**
- Track last link recovery time per email/IP
- Enforce 60-second cooldown
- Use neutral success message regardless

**Reference:** `docs/foundation/business-rules.md` lines 275-286

---

### BR-022: Email Retries (RELIABLE DELIVERY IN PRODUCTION)

**Why it matters:**
- 3 retry attempts with exponential backoff
- Failures logged with correlation IDs
- Email content consistent across retries
- No automatic cleanup of bounces (log-only)

**Implementation impact:**
- Email service client must have retry logic
- Failed emails logged with timestamp and correlation ID
- Production monitoring for email delivery rates
- No need to track bounce addresses

**Reference:** `docs/foundation/business-rules.md` lines 431-450

---

### BR-024: First-Action-Wins (CONCURRENCY SAFETY IN PRODUCTION)

**Why it matters:**
- Two approvers simultaneously approve/deny same booking
- First to persist wins
- Late action shows "Schon erledigt" message
- Examples: "Schon erledigt. Die Buchung ist bereits bestätigt."

**Implementation impact:**
- Approval/deny endpoints must use database transactions
- SELECT FOR UPDATE pattern (row-level locking)
- Check current booking status, then update approval and potentially status
- Return appropriate message (idempotent)

**Reference:** `docs/foundation/business-rules.md` lines 134-146

---

### BR-028: Auto-Cleanup of Past Pending Bookings (BACKGROUND JOB)

**Why it matters:**
- At EndDate+1 00:00 Europe/Berlin, still-Pending bookings auto-cancel
- Transition to Canceled → Archive
- No notifications sent
- Prevents orphaned past Pending bookings

**Implementation impact:**
- Background job (cron or task scheduler)
- Runs daily at 00:01 Europe/Berlin
- Finds all Pending bookings where EndDate < today
- Transitions to Canceled, moves to Archive
- Logs job execution

**Reference:** `docs/foundation/business-rules.md` lines 227-237

---

### BR-029: First-Write-Wins (CRITICAL CONCURRENCY SAFETY)

**Why it matters:**
- Two users simultaneously try to book same free dates
- First submission to persist wins
- Later submission gets conflict error with details of winning booking

**Implementation impact:**
- Create/extend booking endpoints use transactions
- SERIALIZABLE or READ COMMITTED with conflict detection
- Check date ranges AFTER lock acquired
- Return conflict error with winning booking details

**Reference:** `docs/foundation/business-rules.md` lines 73-85

---

### BR-010: Tokens and Links (PRODUCTION IDEMPOTENCY)

**Why it matters:**
- Tokens never expire, never revoked
- Action links always redirect (never 404 or error)
- Action links are idempotent (repeat shows result page with "Schon erledigt")

**Implementation impact:**
- API must validate tokens on every request (no session cache needed)
- Approval/deny/cancel endpoints check current state, return same response
- No error if already actioned (show "Schon erledigt" with context)
- Production error handling must ensure action links don't break

**Reference:** `docs/foundation/business-rules.md` lines 262-272

---

### BR-013: Archival & Purge (DATA MANAGEMENT IN PRODUCTION)

**Why it matters:**
- Canceled items purged when archived > 1 year
- Past Confirmed NEVER purged (historical record)
- Denied items purged once EndDate < today
- Monthly job runs purge

**Implementation impact:**
- Archive table contains Canceled bookings
- Background job (monthly cron) checks archive dates
- Deletes old Canceled and past Denied records
- Preserves all Confirmed (even old ones)

**Reference:** `docs/foundation/business-rules.md` lines 394-406

---

## 2. Production Deployment Requirements

### Backend Deployment (Fly.io Frankfurt)

| Requirement | Details |
|-----------|---------|
| **Region** | Frankfurt, Germany (EU) |
| **App Name** | TBD (e.g., `betzenstein-api`) |
| **Environment** | Production |
| **Health Check** | GET `/health` → 200 OK |
| **Auto-Scale** | 1-3 instances (scale on CPU >70%) |
| **Database** | PostgreSQL 15+ on Fly.io (co-located) |
| **Secrets** | API_KEY, DATABASE_URL, JWT_SECRET, EMAIL_KEY in Fly.io secrets |
| **Logs** | Fly.io logs (searchable) |
| **Monitoring** | Health check endpoint, error logs |

### Frontend Deployment (Vercel Global)

| Requirement | Details |
|-----------|---------|
| **Git Integration** | GitHub main branch auto-deploy |
| **Environment** | Production |
| **Domain** | TBD (e.g., `betzenstein.vercel.app` or custom) |
| **Preview URLs** | PR previews enabled |
| **Environment Variables** | NEXT_PUBLIC_API_URL (points to Fly.io backend) |
| **Build Command** | `npm run build` |
| **Start Command** | `npm start` (Next.js production server) |
| **Edge Functions** | Rate limiting middleware (optional) |

### Database (Fly.io Postgres)

| Requirement | Details |
|-----------|---------|
| **Version** | PostgreSQL 15+ |
| **Backup** | Daily automated (Fly.io managed) |
| **Replication** | Single region (Frankfurt) |
| **Connection Pooling** | PgBouncer (20-30 connections) |
| **Migrations** | Flyway or Alembic (run on deploy) |
| **Indexes** | All required indexes created during migration |
| **Timezone** | Database in UTC, app converts to Europe/Berlin |

### Email Service (Resend)

| Requirement | Details |
|-----------|---------|
| **Provider** | Resend (or SendGrid/AWS SES alternative) |
| **API Key** | Stored in Fly.io secrets |
| **From Address** | `no-reply@<app-domain>` |
| **Retry Strategy** | 3 attempts, exponential backoff (per BR-022) |
| **Monitoring** | Delivery logs, bounce tracking |
| **Rate Limiting** | Resend rate limits apply (usually 100s per second) |

### Environment Variables (Production)

```ini
# Fly.io Secrets
DATABASE_URL=postgresql://user:pass@db.internal:5432/betzenstein
JWT_SECRET=<secure-random-32-char-string>
RESEND_API_KEY=<resend-api-key>
API_BASE_URL=https://betzenstein-api.fly.dev

# Frontend (public)
NEXT_PUBLIC_API_URL=https://betzenstein-api.fly.dev

# Configuration
TIMEZONE=Europe/Berlin
MAX_PARTY_SIZE=10
FUTURE_HORIZON_MONTHS=18
LONG_STAY_WARN_DAYS=7
RATE_LIMIT_BOOKING_PER_DAY=10
RATE_LIMIT_REQUESTS_PER_HOUR=30
RATE_LIMIT_RECOVERY_PER_HOUR=5
RATE_LIMIT_RECOVERY_COOLDOWN_SECONDS=60

# Monitoring (optional)
SENTRY_DSN=<sentry-project-key>
LOG_LEVEL=info
```

---

## 3. Test Plan: Production Deployment

### Deployment Infrastructure Tests

**Fly.io Backend:**
1. `test_fly_health_check_endpoint_returns_200` - GET /health returns 200 OK
2. `test_fly_database_connected` - Can query database
3. `test_fly_secrets_loaded` - Environment variables present
4. `test_fly_cors_configured` - CORS allows frontend requests

**Vercel Frontend:**
5. `test_vercel_build_succeeds` - Build completes without errors
6. `test_vercel_preview_url_accessible` - Preview URL responds
7. `test_vercel_environment_variables_set` - NEXT_PUBLIC_API_URL correct

**Database Migrations:**
8. `test_database_migration_applied` - All migrations run
9. `test_database_indexes_created` - All indexes exist
10. `test_database_schema_matches_models` - Schema aligned with code

### Rate Limiting Tests (BR-012)

**Booking Submission Rate Limit:**
11. `test_rate_limit_10_bookings_per_day_enforced` - 11th booking rejected
12. `test_rate_limit_error_message_german` - Error in German
13. `test_rate_limit_per_email_not_global` - Limit per email address

**IP-Based Rate Limit:**
14. `test_rate_limit_30_requests_per_hour_enforced` - 31st request rejected
15. `test_rate_limit_per_ip_respected` - Limit per IP address

**Link Recovery Rate Limit (BR-021):**
16. `test_rate_limit_5_recoveries_per_hour_enforced` - 6th recovery rejected
17. `test_cooldown_60_seconds_enforced` - Immediate 2nd request blocked
18. `test_cooldown_message_german` - "Bitte warte kurz..." message shown

### Email Reliability Tests (BR-022)

**Email Delivery:**
19. `test_email_sent_on_booking_creation` - Email delivered
20. `test_email_sent_on_approval` - Email delivered
21. `test_email_sent_on_deny` - Email delivered
22. `test_email_sent_on_cancel` - Email delivered

**Retry Logic:**
23. `test_email_retries_on_temporary_failure` - Resend retries
24. `test_email_logged_with_correlation_id` - Failed emails logged
25. `test_email_content_consistent_across_retries` - Same content, no mutations

### Concurrency Safety Tests (BR-024, BR-029)

**First-Action-Wins (BR-024):**
26. `test_concurrent_approvals_first_wins` - First approval to persist wins
27. `test_late_approval_shows_schon_erledigt` - Late action shows correct message
28. `test_concurrent_approve_deny_deny_wins` - First approve or deny wins
29. `test_approval_uses_select_for_update` - Database locking verified

**First-Write-Wins (BR-029):**
30. `test_concurrent_bookings_same_dates_first_wins` - First booking to persist wins
31. `test_late_booking_gets_conflict_error` - Late booking gets conflict with details
32. `test_create_uses_serializable_transaction` - Transaction isolation level correct
33. `test_booking_creation_transaction_atomic` - All-or-nothing semantics

### Background Job Tests

**Auto-Cleanup (BR-028):**
34. `test_auto_cleanup_runs_daily_at_00_01_berlin` - Job scheduled correctly
35. `test_auto_cleanup_finds_past_pending_bookings` - Query correct
36. `test_auto_cleanup_transitions_to_canceled` - Status updated
37. `test_auto_cleanup_moves_to_archive` - Archive flag set
38. `test_auto_cleanup_no_notifications_sent` - No emails sent

**Archive Purge (BR-013):**
39. `test_purge_deleted_canceled_after_1_year` - 1-year-old Canceled purged
40. `test_purge_keeps_confirmed_forever` - Confirmed never purged
41. `test_purge_deletes_denied_with_past_end_date` - Past Denied purged
42. `test_purge_runs_monthly` - Cron scheduled monthly

**Weekly Digest (BR-009 - existing, ensure production-ready):**
43. `test_weekly_digest_runs_sunday_09_00_berlin` - Cron scheduled
44. `test_weekly_digest_includes_old_no_response_only` - Correct filtering
45. `test_weekly_digest_excludes_past_items` - Past items excluded
46. `test_weekly_digest_ordered_by_start_date` - Correct ordering

### Idempotency Tests (BR-010)

**Action Link Idempotency:**
47. `test_approve_action_link_idempotent` - Multiple clicks return same result
48. `test_deny_action_link_idempotent` - Multiple clicks return same result
49. `test_cancel_action_link_idempotent` - Multiple clicks return same result
50. `test_already_actioned_shows_schon_erledigt_message` - Proper message shown

### End-to-End Smoke Tests

**Critical User Journeys:**
51. `test_smoke_create_booking_end_to_end` - From calendar to confirmation
52. `test_smoke_approver_approve_booking` - From email link to approval
53. `test_smoke_approver_deny_booking` - From email link to denial
54. `test_smoke_requester_edit_booking` - From details to edit confirmation
55. `test_smoke_requester_cancel_booking` - From details to cancellation

### Production Environment Tests

**HTTPS & Security:**
56. `test_https_enforced` - All requests upgrade to HTTPS
57. `test_cors_headers_present` - Cross-origin properly restricted
58. `test_security_headers_present` - HSTS, X-Frame-Options, etc.

**Timezone Handling:**
59. `test_timezone_berlin_for_business_logic` - Past determination uses Europe/Berlin
60. `test_timezone_utc_in_database` - Timestamps stored UTC
61. `test_timezone_berlin_conversion_for_display` - Display converts correctly

**Load & Stability:**
62. `test_production_handles_100_concurrent_calendar_requests` - Scale test
63. `test_production_database_connection_pool_stable` - Connections reused
64. `test_production_error_logging_working` - Errors captured and logged

### Total Production Tests: ~64

---

## 4. Gherkin Scenarios: US-8.3

```gherkin
Feature: Production Deployment

  Scenario: API deployed to Fly.io Frankfurt
    Given I push to main branch
    When GitHub Actions CI completes
    Then backend should deploy to Fly.io
    And health check endpoint GET /health returns 200 OK
    And database connection verified
    And environment variables loaded from Fly.io secrets

  Scenario: Frontend deployed to Vercel
    Given I push to main branch
    When GitHub Actions CI completes
    Then frontend should deploy to Vercel
    And preview URL is accessible
    And NEXT_PUBLIC_API_URL points to production backend
    And bundle is optimized (Lighthouse ≥90)

  Scenario: Rate limiting enforced in production
    Given the booking submission endpoint is deployed
    When I submit more than 10 bookings per day from one email
    Then the 11th booking is rejected
    And error message is in German
    And each email address has its own limit

  Scenario: Rate limiting on link recovery
    Given the link recovery endpoint is deployed
    When I request recovery 6 times in one hour from same email
    Then the 6th request is blocked
    And I see cooldown message: "Bitte warte kurz..."
    And 60-second cooldown is enforced

  Scenario: Email delivery with retries
    Given an email fails to send temporarily
    When the email service retries
    Then up to 3 attempts are made with exponential backoff
    And failed delivery is logged with correlation ID
    And email content remains unchanged across retries

  Scenario: Concurrent approvals are handled safely
    Given two approvers try to approve the same booking simultaneously
    When both requests reach the backend at the same time
    Then the first to persist wins
    And the second sees "Schon erledigt. Die Buchung ist bereits bestätigt."
    And database uses SELECT FOR UPDATE to prevent race conditions

  Scenario: Concurrent bookings are handled safely
    Given two users try to book the same dates simultaneously
    When both requests reach the backend at the same time
    Then the first to persist wins
    And the second sees conflict error with details of winning booking
    And booking creation uses SERIALIZABLE transaction isolation

  Scenario: Auto-cleanup of past pending bookings
    Given a Pending booking with EndDate = yesterday
    When the cleanup job runs at 00:01 Europe/Berlin
    Then the booking transitions to Canceled
    And it moves to Archive
    And no notification email is sent

  Scenario: Archive purge runs monthly
    Given a Canceled booking archived 13 months ago
    When the monthly purge job runs
    Then the old Canceled record is deleted
    And a Confirmed booking (any age) is never deleted
    And a Denied booking with past EndDate is deleted

  Scenario: Idempotent action links from email
    Given I click an approval link from email
    When I click the same link multiple times
    Then the booking is approved on first click
    And subsequent clicks show "Schon erledigt." message (not error)
    And no state is corrupted
```

---

# Test Execution Checklist

## Testing by Phase

### Phase 8.1: Performance (21 tests)

- [ ] **Database Query Performance (5 tests)**
  - Eager loading validation
  - Index usage verification
  - N+1 elimination tests
  - Response time benchmarks
  - Concurrent request handling

- [ ] **API Response Time (4 tests)**
  - Calendar, approver list, create booking, booking details

- [ ] **Lighthouse Audits (3 tests)**
  - Performance ≥90
  - Best Practices ≥90
  - SEO audit

- [ ] **Bundle Size & Code Splitting (3 tests)**
  - Gzip <60KB
  - Code splitting verified
  - Lazy loading tests

- [ ] **Core Web Vitals (5 tests)**
  - TTI <3s, FCP <1.5s, LCP <2.5s, CLS <0.1
  - Load testing

### Phase 8.2: Accessibility (55 tests)

- [ ] **Automated Accessibility (10 tests)**
  - axe-core 0 violations on 10 pages

- [ ] **Keyboard Navigation (10 tests)**
  - Calendar, form, dialog navigation
  - No keyboard traps

- [ ] **Focus & Visual Indicators (5 tests)**
  - Visibility, contrast, size, order

- [ ] **Screen Reader Support (9 tests)**
  - Landmarks, labels, errors, content
  - German text readability

- [ ] **Color Contrast (10 tests)**
  - Text (4.5:1), components (3:1)
  - Affiliation colors on text

- [ ] **Mobile Accessibility (4 tests)**
  - Touch target size, spacing, viewport, scrolling

- [ ] **Lighthouse Accessibility (1 test)**
  - Lighthouse accessibility = 100

- [ ] **German Text Accessibility (3 tests)**
  - ARIA labels, error messages, form labels

### Phase 8.3: Production (64 tests)

- [ ] **Deployment Infrastructure (10 tests)**
  - Fly.io health, Vercel build, database, migrations

- [ ] **Rate Limiting (8 tests)**
  - Booking submission, IP-based, link recovery, cooldown

- [ ] **Email Reliability (6 tests)**
  - Delivery, retries, logging, consistency

- [ ] **Concurrency Safety (8 tests)**
  - First-action-wins, first-write-wins, locking

- [ ] **Background Jobs (13 tests)**
  - Auto-cleanup, archive purge, weekly digest

- [ ] **Idempotency (4 tests)**
  - Action links, "Schon erledigt" messages

- [ ] **Smoke Tests (5 tests)**
  - End-to-end critical journeys

- [ ] **Security & Stability (6 tests)**
  - HTTPS, CORS, security headers, timezone, load test, error logging

## Test Count Summary

| Phase | Category | Count |
|-------|----------|-------|
| **8.1** | Performance | 21 |
| **8.2** | Accessibility | 55 |
| **8.3** | Production | 64 |
| **TOTAL** | All Phase 8 | **140** |

---

# Summary by User Story

## US-8.1: Performance Optimization

| Aspect | Details |
|--------|---------|
| **Applicable BRs** | BR-023 (Approver Lists - query performance) |
| **Key Metrics** | TTI <3s, Lighthouse ≥90, N+1 elimination |
| **Test Count** | 21 (Lighthouse, bundle, Core Web Vitals, load tests) |
| **Critical Path** | Database indexes, eager loading, code splitting, lazy loading |

## US-8.2: Accessibility (WCAG AA)

| Aspect | Details |
|--------|---------|
| **Applicable BRs** | BR-011 (German UI), BR-016 (Party Size), BR-019 (First Name error), BR-020 (Link detection error) |
| **Key Metrics** | axe-core 0 violations, keyboard navigation, screen reader support, 4.5:1 contrast, 44×44pt touch targets |
| **Test Count** | 55 (automated scans, keyboard tests, screen reader, color contrast, mobile, Lighthouse) |
| **Critical Path** | ARIA labels (German), form labels, keyboard focus, color contrast, touch targets |

## US-8.3: Production Deployment

| Aspect | Details |
|--------|---------|
| **Applicable BRs** | BR-010 (Idempotency), BR-012 (Rate limits), BR-013 (Archive purge), BR-021 (Cooldown), BR-022 (Email retries), BR-024 (First-action-wins), BR-028 (Auto-cleanup), BR-029 (First-write-wins) |
| **Key Metrics** | Rate limiting enforced, email delivery reliable, concurrency safe, background jobs reliable |
| **Test Count** | 64 (infrastructure, rate limiting, email, concurrency, background jobs, smoke tests, security) |
| **Critical Path** | Fly.io deployment, database migration, rate limiting, email retries, SELECT FOR UPDATE, background job scheduling |

---

# Implementation Priorities

## Highest Priority (Critical Path)

1. **Performance - Database Indexes** (Phase 8.1)
   - Without indexes, calendar and conflict queries will be slow
   - Creates foundation for all performance gains

2. **Concurrency Safety - SELECT FOR UPDATE** (Phase 8.3)
   - BR-024 and BR-029 require serialization
   - Critical for production safety

3. **Accessibility - ARIA Labels (German)** (Phase 8.2)
   - Screen readers require proper labels
   - All labels must be in German

4. **Rate Limiting Enforcement** (Phase 8.3)
   - Production security depends on this
   - Must be in place before public launch

## Medium Priority

5. **Email Retry Logic** (Phase 8.3)
- Production reliability depends on exponential backoff
- Critical for user trust

6. **Background Job Scheduling** (Phase 8.3)
   - Auto-cleanup and archive purge must run reliably
   - Requires cron or task scheduler setup

7. **Color Contrast Validation** (Phase 8.2)
   - Affiliation colors may need adjustment
   - Required for WCAG AA compliance

## Lower Priority (Polish)

8. **Code Splitting & Bundle Optimization** (Phase 8.1)
   - Improves performance but not blocking
   - Can be added iteratively

9. **Advanced Monitoring** (Phase 8.3)
   - Sentry, error tracking are optional
   - Basic Fly.io logs sufficient for MVP

---

# Notes for Implementation Team

1. **BR-023 is the performance foundation:** All approver list queries must use eager loading. Without this, N+1 queries will dominate performance.

2. **Concurrency requires careful testing:** BR-024 and BR-029 are easy to get wrong. Every concurrent scenario must have a test.

3. **German accessibility is non-negotiable:** All ARIA labels, error messages, and form labels must be in German. No English fallbacks.

4. **Background jobs are critical:** Auto-cleanup (BR-028) and archive purge (BR-013) must run reliably. Test them thoroughly.

5. **Rate limiting is security:** Rate limits (BR-012, BR-021) must be enforced server-side. Client-side limits are not sufficient.

6. **Email idempotency matters:** Action links must be idempotent (BR-010). Test every concurrent scenario.

7. **Lighthouse is a good proxy:** For performance and accessibility, Lighthouse and axe-core catch most issues. Use them as gatekeepers.

---

**Ready to implement Phase 8?** Start with database indexes, then move to rate limiting and background jobs, then accessibility and performance optimization.
