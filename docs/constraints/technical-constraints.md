# Technical Constraints

## Overview

Technical limitations, platform requirements, and implementation constraints.

---

## Platform Requirements

### Browser Compatibility

**Desktop Browsers (Major versions released 2023+):**
- Chrome/Edge (Chromium): 100+
- Firefox: 100+
- Safari: 15+

**Mobile Browsers:**
- iOS Safari: iOS 13+ (released 2019)
- Chrome for Android: Latest 2 major versions
- Samsung Internet: Latest version

**Why these versions:**
- Modern JavaScript features (ES6+)
- CSS Grid and Flexbox support
- Fetch API and Promises
- No IE11 support required

---

### Mobile Device Support

**Minimum Device Class:**
- iPhone 8 (released 2017) or equivalent Android
- Viewport: ~375×667 logical pixels
- Touch-only input
- Variable network (3G/4G/5G)

**Target Releases:**
- Devices released 2019+ must work smoothly
- Older devices (2017-2018) should work acceptably

**Screen Sizes:**
- Small phones: 320px–414px width
- Tablets: 768px–1024px width
- Desktop: 1024px+ width

---

## Language & Localization

### UI Language

**Requirement:** German only (per BR-011)

**Tone:** Informal "du" (not formal "Sie")

**Implementation:**
- Strings may be hardcoded (no i18n library required initially)
- All user-facing text in German
- Error messages in German
- Email copy in German

**Future Expansion:**
- If other languages needed, refactor to use i18n library (react-i18next, vue-i18n, etc.)
- Extract all strings to translation files
- German remains default

---

### This Documentation

**Language:** English

**Purpose:** Technical/engineering handover

**Audience:** Solution architects, developers, QA engineers

---

## Date & Time Handling

### Timezone

**System Timezone:** Europe/Berlin

**Storage:** UTC in database

**Display:** Convert to Europe/Berlin for user

**Business Logic:** All date-based decisions use Europe/Berlin
- Past-dated determination: 00:00 Europe/Berlin
- Auto-cleanup trigger: EndDate+1 00:00 Europe/Berlin
- Weekly digest: Sunday 09:00 Europe/Berlin

**Implementation:**
- Use timezone library (moment-timezone, date-fns-tz, luxon)
- Store all timestamps as UTC
- Convert for display and business logic
- Never use local browser timezone for decisions

---

### Date Formatting

**Display Format:**
- Single date: `DD.MM.YYYY` (e.g., "05.08.2025")
- Date range: `DD.–DD.MM.YYYY` (e.g., "01.–05.08.2025")
- En-dash (–) for ranges, not hyphen (-)

**Internal Storage:**
- ISO 8601 format (YYYY-MM-DD) in database
- UTC timestamps (ISO 8601 with timezone)

---

### Locale

**Setting:** `de-DE`

**Affects:**
- Date formatting (day.month.year)
- Number formatting (if needed)
- Collation/sorting

**Week Start:**
- Monday (European standard)
- Calendar view reflects this

---

## Data Residency

### No Constraints

**Requirement:** None specified

**Allowed:**
- Any cloud provider (AWS, GCP, Azure, Hetzner, etc.)
- Any region (Europe, US, etc.)
- Single region or multi-region

**Rationale:** Small trusted group; owner accepts risk; no formal GDPR residency requirement enforced.

---

## Email Delivery

### Email Service Provider

**Options:**
- SendGrid
- AWS SES
- Mailgun
- Postmark
- SMTP server

**Requirements:**
- Reliable delivery
- Bounce handling
- Support for transactional emails
- API or SMTP access

**Configuration:**
- SPF/DKIM/DMARC for deliverability
- Verified sender domain
- Monitor delivery rates

---

### Email Constraints

**From Address:**
- `no-reply@<app-domain>`
- No Reply-To header

**Format:**
- HTML primary (dark-mode friendly)
- Plain-text fallback required
- No inline CSS (use embedded or external)

**Links:**
- All links absolute URLs (not relative)
- HTTPS only
- Action links with signed tokens

---

### Delivery Timing

**No Quiet Hours:**
- Emails may send anytime (24/7)
- Including nights, weekends, holidays
- Immediate notification on actions

**Weekly Digest:**
- Specifically Sunday 09:00 Europe/Berlin
- Scheduled via cron or task scheduler

---

## Authentication & Authorization

### No Traditional Login

**Constraint:** No username/password authentication

**Implementation:** Role-by-link with signed tokens

**Token Requirements:**
- Cryptographically signed (HMAC, JWT, etc.)
- Include: email, role, signature
- Validate signature on every request
- No expiry (per BR-010)
- No revocation mechanism (per BR-010)

---

### Token Signing

**Algorithm Options:**
- HMAC-SHA256
- JWT with HS256 or RS256
- Similar cryptographic signature scheme

**Secret Management:**
- Store signing secret securely (environment variable, secret manager)
- Rotate periodically (though requires re-issuing all tokens)

**Token Structure (example):**
```
{
  "email": "user@example.com",
  "role": "requester",  // or "approver"
  "issued": "2025-01-15T12:00:00Z"
}
```
Signed and encoded as URL-safe string.

---

### No Session Management

**Constraint:** Stateless authentication

**Benefits:**
- Scalable (no session store)
- Simple (no session expiry logic)
- Resilient (no session loss on server restart)

**Implementation:**
- Validate token on every request
- No server-side session storage
- No cookies (token in URL or header)

---

## Rate Limiting

### Implementation Options

**In-Memory:**
- Simple counters in application memory
- Lost on restart (acceptable for rate limits)
- Single-server only

**Redis:**
- Distributed rate limiting
- Persists across restarts
- Works for multi-server deployments

**Database:**
- Persistent
- Slower than in-memory/Redis
- May impact performance

**Recommendation:** Redis for production, in-memory for simple deployments

---

### Rate Limit Tracking

**Keys:**
- Per email: Hash email for privacy
- Per IP: Use client IP (consider X-Forwarded-For if behind proxy)

**Windows:**
- Sliding window (more accurate, complex)
- Fixed window (simpler, burst-prone)

**Recommendation:** Fixed window (simpler) acceptable for this use case

---

## Database

### Relational Database Required

**Why:**
- Strong ACID guarantees for conflict detection
- Transaction support for state changes
- Complex queries (filters, sorts, joins)

**Options:**
- PostgreSQL (recommended: robust, feature-rich)
- MySQL/MariaDB (acceptable)
- SQLite (dev/test only, not production)

---

### Schema Requirements

**Tables:**
- BOOKING
- APPROVER_PARTY
- APPROVAL
- CANCELLATION (optional, or fields in BOOKING)
- TIMELINE_EVENT
- USER_REQUESTER (optional, or embedded in BOOKING)
- HOLIDAY (optional)

See `data-model.md` for full schema.

---

### Indexing

**Required Indexes:**
- BOOKING: primary key, status, date range, email (unique)
- APPROVAL: primary key, (BookingID, Party) composite
- TIMELINE_EVENT: primary key, BookingID, When

**Purpose:**
- Fast conflict detection (date range queries)
- Efficient filtering (status, NoResponse)
- Quick sorts (LastActivityAt, CreatedAt)

---

### Transactions

**Use Cases:**
- Create booking + approvals atomically
- Update approval + booking status atomically
- Conflict detection (first-write-wins)

**Isolation Level:**
- READ COMMITTED minimum
- SERIALIZABLE for strictest conflict detection (may impact performance)

---

### Backups

**Requirement:** Regular automated backups

**Frequency:**
- Daily full backups
- Continuous WAL archiving (if PostgreSQL)

**Retention:**
- 30 days minimum
- Test restore procedure regularly

---

## API Design

### RESTful API (Suggested)

**Endpoints:**
- `GET /calendar` - Public calendar data
- `GET /bookings/:id` - Booking details
- `POST /bookings` - Create booking
- `PATCH /bookings/:id` - Edit booking
- `POST /bookings/:id/approve` - Approve (approver)
- `POST /bookings/:id/deny` - Deny (approver)
- `DELETE /bookings/:id` - Cancel (requester)
- `POST /bookings/:id/reopen` - Reopen (requester)
- `GET /approver/outstanding` - Outstanding list
- `GET /approver/history` - History list
- `POST /auth/recover-link` - Link recovery

**Authentication:**
- Token in header (e.g., `Authorization: Bearer <token>`)
- Or token in URL query (for action links from email)

**Response Format:**
- JSON
- Consistent error structure (see error-handling.md)

---

### GraphQL (Alternative)

**If Preferred:**
- Single endpoint
- Flexible queries
- May be overkill for this use case

**Tradeoffs:**
- More complex setup
- Better for complex data requirements
- Consider if expanding feature set

---

## Web Framework

### Framework Options

**React, Vue, Svelte, or similar:**
- Modern reactive framework
- Component-based
- Good mobile support

**Plain JavaScript:**
- Also acceptable for simple use case
- May be harder to maintain as features grow

**Recommendation:** Use modern framework for better maintainability

---

### Mobile-First Design

**Approach:**
- Design for mobile viewport first
- Enhance for larger screens (progressive enhancement)
- Touch-first interactions
- No hover dependencies

**CSS:**
- CSS Grid and Flexbox for layouts
- Media queries for responsive breakpoints
- No horizontal scroll

**JavaScript:**
- Avoid hover events
- Use click/tap events
- Large tap targets (44×44 points minimum)

---

## Hosting & Deployment

### Hosting Options

**Cloud Providers:**
- AWS (EC2, ECS, Lambda)
- Google Cloud (Compute Engine, Cloud Run)
- Azure (App Service, Functions)
- Hetzner, DigitalOcean, etc.

**Platform-as-a-Service:**
- Heroku
- Render
- Railway
- Fly.io

**No Constraints:** Any reliable hosting acceptable

---

### Deployment Requirements

**HTTPS Required:**
- Valid SSL/TLS certificate
- All traffic over HTTPS
- HTTP redirects to HTTPS

**Environment Variables:**
- Configuration via environment variables
- Secret management for sensitive values
- No secrets in code

**CI/CD:**
- Automated tests on commit/PR
- Automated deployment on merge (optional)
- Manual approval for production (optional)

---

### Scaling Considerations

**Current Scale:**
- Small trusted group
- Low traffic expected
- Single server likely sufficient

**Future Scaling:**
- Horizontal scaling (multiple app servers)
- Database replication (read replicas if needed)
- Redis for distributed rate limiting/caching
- CDN for static assets (optional)

---

## Third-Party Services

### Required

**Email Service:**
- SendGrid, AWS SES, Mailgun, etc.
- Transactional email support

### Optional

**Holiday API:**
- Public holiday data for Germany
- API or static dataset
- Gracefully handle unavailability

**Monitoring:**
- Sentry (error tracking)
- LogRocket (session replay)
- Google Analytics (usage, if desired)

---

## Testing

### Test Levels

**Unit Tests:**
- Business logic (validation, state transitions)
- Pure functions
- Utilities

**Integration Tests:**
- API endpoints
- Database interactions
- Email sending

**End-to-End Tests:**
- Critical user journeys (submit, approve, deny, cancel)
- Mobile viewport testing
- Cross-browser testing (Playwright, Cypress)

---

### Test Data

**Test Approvers:**
- Use test email addresses (Mailtrap, etc.)
- Same names (Ingeborg, Cornelia, Angelika)
- Test tokens generated

**Test Bookings:**
- Various date ranges (past, present, future)
- Various states (Pending, Confirmed, Denied, Canceled)
- Conflict scenarios

---

## Accessibility

### WCAG AA Compliance (Target)

**Requirements:**
- Color contrast ≥ 4.5:1 (text)
- Color contrast ≥ 3:1 (UI components)
- Keyboard navigable
- Screen reader compatible
- Focus indicators visible

**Testing:**
- Automated (axe, Lighthouse)
- Manual (keyboard navigation)
- Screen reader (NVDA, JAWS, VoiceOver)

---

## Legal & Compliance

### No Legal Pages

**Constraint:** Intentionally omitted

**Reason:** Small trusted group; owner accepts risk

**Not Required:**
- Impressum
- Privacy Policy
- Terms of Service
- Cookie banner

---

### GDPR Considerations

**Applicability:** Likely applies (EU users, emails as PII)

**Minimal Compliance Approach:**
- Emails never displayed (privacy by design)
- No third-party tracking (unless monitoring added)
- Small group with implicit consent
- Owner accepts risk (no formal DPA)

**Right to Deletion:**
- Not implemented via UI
- Manual handling if requested (admin deletes records)

---

## Development Constraints

### No IE11 Support

**Explicitly NOT Supported:**
- Internet Explorer 11 or older
- Rationale: End-of-life, modern features unavailable

**Polyfills:**
- Not required for modern browsers
- Can use latest JavaScript (ES6+)

---

### Modern JavaScript

**Features Allowed:**
- ES6+ (arrow functions, destructuring, async/await)
- Promises and Fetch API
- CSS Grid and Flexbox
- No transpilation needed for target browsers

---

### Dependencies

**Keep Minimal:**
- Avoid bloated dependencies
- Evaluate bundle size impact
- Prefer tree-shakeable libraries

**Security:**
- Regular dependency updates
- Automated security scanning (npm audit, Dependabot)
- Pin major versions

---

## Operational Constraints

### No 24/7 Support

**Constraint:** No dedicated on-call support

**Acceptable:**
- Best-effort availability
- Email-based support
- Response time: within 1-2 business days

---

### Maintenance Windows

**Allowed:**
- Scheduled downtime for maintenance
- Announce via email if possible
- Prefer low-usage times (nights, weekends)

---

### Monitoring & Alerting

**Minimal Setup:**
- Uptime monitoring (UptimeRobot, etc.)
- Error rate alerts (email)
- Email delivery monitoring

**Optional:**
- Advanced APM (New Relic, Datadog)
- Log aggregation (Loggly, Papertrail)
- Performance monitoring

---

## Summary Tables

### Browser Compatibility

| Platform | Minimum Version | Target Releases |
|----------|-----------------|-----------------|
| Chrome/Edge | 100+ | 2023+ |
| Firefox | 100+ | 2023+ |
| Safari (macOS) | 15+ | 2021+ |
| iOS Safari | iOS 13+ | 2019+ |
| Chrome (Android) | Latest 2 versions | 2023+ |

---

### Mobile Devices

| Device Class | Viewport | Support Level |
|-------------|----------|---------------|
| iPhone 8 | 375×667 | Must work smoothly |
| Small phones | 320×640+ | Should work |
| Tablets | 768×1024 | Must work smoothly |
| Desktop | 1024+ | Must work smoothly |

---

### Technology Recommendations

| Component | Recommendation | Alternatives |
|-----------|----------------|--------------|
| Database | PostgreSQL | MySQL, MariaDB |
| API Framework | Node.js (Express) or Python (FastAPI) | Ruby (Rails), Go, Java |
| Web Framework | React, Vue, or Svelte | Plain JS |
| Email Service | SendGrid or AWS SES | Mailgun, Postmark |
| Hosting | Heroku, Render, AWS | Any reliable host |
| Rate Limiting | Redis | In-memory, DB |

---

### Required vs. Optional Features

| Feature | Required | Optional | Notes |
|---------|----------|----------|-------|
| German UI | ✓ | — | Per BR-011 |
| Email notifications | ✓ | — | Core feature |
| Weekly digest | ✓ | — | Per BR-009 |
| Holidays display | — | ✓ | Visual only |
| Legal pages | — | — | Intentionally omitted |
| Monitoring | — | ✓ | Recommended |
| Analytics | — | ✓ | Optional |

---

## Implementation Priorities

### Phase 1: MVP
- Core booking CRUD
- Approval flow (3 approvers)
- Email notifications
- Conflict detection
- Mobile-responsive UI
- German copy

### Phase 2: Polish
- Weekly digest
- Link recovery
- Loading states
- Error handling
- Holiday display (optional)

### Phase 3: Operations
- Monitoring and alerting
- Performance optimization
- Advanced error tracking
- Backups and disaster recovery

---

## Technology Stack (Example)

**API:**
- Node.js + Express (or Python + FastAPI)
- PostgreSQL
- Redis (rate limiting, optional caching)
- JWT for tokens

**Web:**
- React (or Vue/Svelte)
- CSS Modules or Tailwind CSS
- Fetch API for HTTP requests
- Date-fns or Luxon for date handling

**Email:**
- SendGrid or AWS SES
- Handlebars for templates

**Hosting:**
- Heroku or Render (simple PaaS)
- Or AWS/GCP for more control

**Monitoring:**
- Sentry (errors)
- UptimeRobot (uptime)
- LogDNA (logs, optional)

**CI/CD:**
- GitHub Actions
- Automated tests
- Deploy on merge to main

---

## Non-Requirements

**Explicitly NOT Required:**
- Offline support / PWA
- Real-time updates (WebSockets)
- Mobile native apps (iOS/Android)
- Multiple languages (German only)
- Advanced analytics/reporting
- Export features (PDF, CSV)
- Integrations (calendar sync, etc.)
- User profiles/avatars
- Commenting system (beyond deny/cancel comments)
- Attachments/file uploads
