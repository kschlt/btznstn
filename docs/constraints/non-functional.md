# Non-Functional Requirements

## Overview

System-wide quality attributes, performance expectations, and operational characteristics.

---

## Performance

### User Experience

**Goal:** Fast and modern feel

**Expectations:**
- Calendar loads in < 1 second (typical case)
- Booking details open < 500ms
- Form submissions respond < 2 seconds
- No perceived lag on interactions

**Optimizations:**
- Skeleton loading states during fetch
- Optimistic UI updates where safe
- Client-side validation before server round-trip
- Efficient API design (no over-fetching)

---

### Responsiveness

**Requirements:**
- Responsive calendar view (adapts to viewport)
- No horizontal scroll (all content fits width)
- Smooth scrolling and animations
- Touch-friendly interactions on mobile

**Performance Targets:**
- First Contentful Paint (FCP): < 2s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.5s
- Mobile Lighthouse score: > 80

---

## Security

### Authentication

**Model:** Role-by-link (no accounts/passwords)

**Mechanism:**
- Signed tokens (HMAC, JWT, or similar)
- Tokens include: email, role (requester/approver), signature
- No expiry (per BR-010)
- No revocation (per BR-010)

**Security Properties:**
- Tokens cryptographically signed (cannot be forged)
- Long random strings (unguessable)
- HTTPS only (tokens never sent over HTTP)

**Accepted Risks:**
- No token expiry (compromise = permanent access until manual intervention)
- No revocation (lost token = must request new via recovery, but old still works)
- Email-based access (no MFA, no password)

**Mitigation:**
- Rate limiting (prevent brute force)
- Soft cooldown on recovery (prevent enumeration)
- Small trusted group (acceptable risk profile)

---

### Authorization

**Enforcement:**
- Server-side validation of all actions
- Role determined by token type (requester vs approver)
- State checks (e.g., can't approve if already Confirmed)
- Ownership checks (requester can only edit/cancel own bookings)

**No Client-Side Trust:**
- All authorization logic server-side
- Client can't bypass restrictions
- Token validation on every request

---

### Data Protection

**HTTPS Required:**
- All traffic encrypted in transit
- Valid SSL/TLS certificate
- HTTP redirects to HTTPS
- HSTS headers recommended

**Email as PII:**
- Emails never displayed in UI
- Stored securely in database
- Not logged in plaintext
- Normalized (lowercase) for uniqueness

**No Password Storage:**
- No passwords in system
- No bcrypt/hashing needed
- Access via tokens only

---

### Rate Limiting

**Limits (Configurable):**
- Submit: 10 bookings/day/email
- Per-IP: 30 requests/hour/IP
- Recovery: 5 requests/hour/email
- Soft cooldown: 60 seconds on recovery

**Purpose:**
- Prevent spam
- Prevent DoS
- Prevent enumeration attacks (link recovery)

**Implementation:**
- In-memory or Redis-based counters
- Sliding or fixed windows
- Return 429 Too Many Requests when exceeded

---

### Idempotency

**Action Links:**
- All approve/deny/cancel actions idempotent
- Repeat actions show "Schon erledigt" result page
- No duplicate side effects (emails, state changes)

**Concurrent Actions:**
- First-action-wins for approvals/denials (BR-024)
- First-write-wins for create/extend (BR-029)
- Database transactions ensure consistency

---

## Privacy

### Personal Information

**PII Fields:**
- Requester email (hidden, never displayed)
- Approver emails (hidden, never displayed)
- First names (displayed, not considered PII for this use case)

**Public Visibility:**
- Public calendar shows: first name, party size, status, affiliation color
- **Does not show:** emails, comments, detailed timeline

**Private Visibility:**
- Denied bookings not public (hidden from public calendar)
- Canceled bookings in Archive (hidden from all views)

---

### Comments

**Requester Sees:**
- Own comments
- All approver comments on own bookings

**Approver Sees:**
- All comments on bookings involving them

**Viewer Sees:**
- No comments

---

### Link Recovery

**Neutral Success Copy:**
- Same message whether email exists or not
- "Wir haben dir – falls vorhanden – deinen persönlichen Zugangslink erneut gemailt."
- Prevents email enumeration

**Rate Limiting:**
- 5 requests/hour/email
- 60-second soft cooldown
- Prevents brute-force enumeration

---

### Sanitization

**Text Fields (Description, Comments):**
- Plaintext only
- No HTML rendering
- No JavaScript execution
- Links blocked (`http://`, `https://`, `www`, `mailto:`) per BR-020
- Purpose: Prevent XSS, phishing

**Display:**
- Escape HTML entities
- Preserve newlines (convert to `<br>` if rendering in HTML)
- Allow emojis (rendered as-is)

---

## Observability

### User-Visible Audit

**Timeline:**
- All major actions logged (see data-model.md)
- Actors identified (Requester, named Approver, System)
- Timestamps in Europe/Berlin timezone
- Date diffs for edits

**Purpose:**
- Transparency
- Debugging user issues
- Trust-building

---

### Email Logging

**What to Log:**
- All email send attempts (with correlation ID)
- Recipient (hashed for privacy in logs)
- Template/trigger type
- Outcome (success/failure)
- Retry attempts (per BR-022)

**Bounces:**
- Log-only (no user notification)
- Monitor bounce rate
- Investigate high bounce rates

---

### Error Logging

**What to Log:**
- All errors with correlation IDs
- User action context (booking ID, action attempted)
- Timestamp
- Stack trace (server-side only)

**Never Log:**
- Raw email addresses (hash if needed)
- Token values (log token type/ID only)
- Passwords (N/A in this system)

---

### Correlation IDs

**Usage:**
- Every request gets unique correlation ID
- Passed to all logs for that request
- Included in error responses (hidden from user, visible in dev console)
- Helps trace request through system

---

## Localization & Time

### Language

**UI Language:** German only (per BR-011)

**Tone:** Informal "du" (not formal "Sie")

**Strings:** May be hardcoded initially (no i18n infrastructure required)

**This Documentation:** English (technical/engineering handover)

---

### Locale

**Setting:** `de-DE`

**Affects:**
- Date formatting
- Number formatting (if needed)
- Collation (sorting names)

---

### Timezone

**System Timezone:** `Europe/Berlin`

**Storage:** All timestamps in UTC

**Display:** Convert to Europe/Berlin for display

**Business Logic:** All date-based logic uses Europe/Berlin
- Past-dated flip at 00:00 Europe/Berlin
- Auto-cleanup runs at EndDate+1 00:00 Europe/Berlin
- Weekly digest at Sunday 09:00 Europe/Berlin

---

### Holidays

**Configuration:** Global region config (e.g., "DE" or "DE-NRW")

**Source:** German holiday API or static data

**Usage:** Visual calendar annotation only (no business logic)

**If Unavailable:** Hidden gracefully (no error)

---

## Compatibility

### Browser Support

**Desktop:**
- Chrome/Edge (Chromium-based): Latest 2 major versions
- Firefox: Latest 2 major versions
- Safari: Latest 2 major versions

**Mobile:**
- iOS Safari: iOS 13+
- Chrome for Android: Latest 2 major versions
- Samsung Internet: Latest version

**Target Release Years:** 2023+ (devices released 2023 and newer)

---

### Mobile Devices

**Minimum Viewport:**
- Width: ~375px (iPhone 8 class)
- Height: ~667px (iPhone 8 class)

**Must Work Smoothly On:**
- Older/smaller phones (iPhone 8, equivalent Android)
- Touch-only interfaces
- Variable network conditions (3G/4G)

**Optimizations:**
- Large tap targets (≥44×44 points)
- High contrast (readable in sunlight)
- No hover-dependent interactions
- Single-tap to details
- Avoid horizontal scroll

---

### Network Conditions

**Expectations:**
- Works on 3G/4G mobile networks
- Graceful degradation on slow connections
- Loading states during fetch
- Retry logic for failed requests

**Not Required:**
- Offline support (PWA features)
- Background sync

---

## Resilience

### Email Delivery

**Retry Policy (BR-022):**
- ~3 retry attempts
- Exponential backoff (e.g., 2s, 4s, 8s)
- Log failures with correlation IDs

**Failure Handling:**
- Transient failures: Retry automatically
- Permanent failures (bounces): Log-only
- Content consistent across retries

**No Guarantees:**
- Email delivery is best-effort
- User may need to check spam folder
- Recovery link available if email doesn't arrive

---

### Idempotent Actions

**Action Links:**
- Approve/Deny/Cancel links are idempotent
- Repeat clicks safe (no duplicate effects)
- Always redirect to result page

**API Endpoints:**
- Create/Edit endpoints use optimistic locking or first-write-wins
- Idempotency keys if needed for critical operations

---

### Graceful Error Pages

**User-Friendly Errors:**
- Never show stack traces to users
- Clear German copy (see error-handling.md)
- Actionable next steps
- Link to recovery or support

**Logging:**
- Full error details logged server-side
- Correlation IDs for tracing

---

### Data Integrity

**Database Transactions:**
- Use transactions for multi-step operations
- Ensure consistency (approvals + status changes atomic)
- Conflict detection uses appropriate isolation level

**Backups:**
- Regular automated backups
- Test restore procedure
- Retention per backup policy

---

## Availability & SLA

### No Formal SLA

**Context:** Personal/small-group use

**Expectations:**
- Best-effort availability
- No uptime guarantees
- No 24/7 support
- Downtime acceptable for maintenance

**Accepted:** Owner accepts this risk profile for small trusted group.

---

### Maintenance Windows

**Suggested:**
- Announce maintenance via email (if planned)
- Schedule during low-usage times
- Keep downtime minimal (< 1 hour)

---

## Data Residency

**Requirement:** None

**Allowed:** Host anywhere (any cloud provider, any region)

**Note:** No GDPR-specific residency constraint for this small trusted group; owner accepts risk.

---

## Legal & Compliance

### Legal Pages

**Status:** Intentionally omitted

**Reason:** Small trusted group; owner accepts risk

**Not Included:**
- Impressum
- Privacy Policy
- Terms of Service

---

### GDPR

**Applicability:** Likely applies (EU-based users, emails as PII)

**Compliance Approach:**
- Emails never displayed (privacy by design)
- No third-party tracking
- Small group with implicit consent
- Owner accepts risk (no formal DPA, no cookie banner)

**Right to Deletion:**
- Not implemented (no user-facing deletion UI)
- Manual handling if requested (admin deletes booking records)

---

## Operational

### Monitoring

**Recommended:**
- Uptime monitoring (pingdom, UptimeRobot, etc.)
- Error rate alerts
- Email delivery monitoring
- Database health checks

---

### Logging

**What to Log:**
- All API requests (method, path, status, duration)
- All errors (with stack traces, correlation IDs)
- Email send attempts and outcomes
- Timeline events (already in database)

**Log Retention:**
- Application logs: 30 days
- Error logs: 90 days
- Audit logs (timeline): Indefinite (in database)

---

### Alerting

**Suggested Alerts:**
- Error rate > 1% (15-minute window)
- Email delivery failure rate > 5%
- API response time p95 > 2s
- Database connection failures

**Channels:**
- Email to admin
- Slack/Discord webhook (if team)

---

### Deployment

**Strategy:**
- Blue-green or rolling deployment recommended
- Run database migrations before code deploy
- Smoke test after deploy
- Rollback plan

**Automation:**
- CI/CD pipeline (GitHub Actions, GitLab CI, etc.)
- Automated tests (unit, integration)
- Linting and formatting

---

## Performance Summary

| Metric | Target | Notes |
|--------|--------|-------|
| Calendar load | < 1s | Typical case |
| Details open | < 500ms | Fast interaction |
| Form submit response | < 2s | User waits for confirmation |
| FCP | < 2s | First paint |
| LCP | < 2.5s | Largest paint |
| TTI | < 3.5s | Interactive |
| Mobile Lighthouse | > 80 | Performance score |

---

## Security Summary

| Aspect | Implementation |
|--------|----------------|
| Authentication | Signed tokens (no expiry, no revocation) |
| Authorization | Server-side validation, role-by-link |
| HTTPS | Required (all traffic encrypted) |
| Rate Limiting | Submit, IP, recovery limits |
| PII Protection | Emails never displayed |
| Link Recovery | Neutral copy, cooldown, rate limits |
| Sanitization | Plaintext only, block links |
| Idempotency | All action links idempotent |

---

## Privacy Summary

| Data | Visibility |
|------|------------|
| Email addresses | Hidden (PII, never displayed) |
| First names | Public (Pending/Confirmed), hidden (Denied/Canceled) |
| Comments | Role-based (requester/approver), hidden from viewer |
| Denied bookings | Not public (requester + approvers only) |
| Canceled bookings | Archive (hidden from all) |
| Public calendar | First name, party size, status, affiliation |

---

## Implementation Priorities

### Must Have (MVP)
- All functional requirements
- Security (HTTPS, tokens, rate limits)
- Privacy (email hiding, Denied not public)
- Mobile compatibility (iPhone 8 class)
- Email notifications (with retries)
- German UI copy

### Should Have
- Monitoring and alerting
- Error logging with correlation IDs
- Graceful error pages
- Loading states

### Nice to Have
- Advanced analytics
- Performance monitoring (APM)
- A/B testing infrastructure
- Internationalization (future languages)
