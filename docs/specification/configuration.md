# Configuration

## Overview

System configuration parameters with defaults and notes.

---

## Approver Configuration

### Fixed Approver Parties

**Parameter:** `APPROVER_PARTIES`

**Type:** Array of objects

**Default:**
```json
[
  {
    "name": "Ingeborg",
    "displayName": "Ingeborg",
    "email": "ingeborg@example.com"
  },
  {
    "name": "Cornelia",
    "displayName": "Cornelia",
    "email": "cornelia@example.com"
  },
  {
    "name": "Angelika",
    "displayName": "Angelika",
    "email": "angelika@example.com"
  }
]
```

**Notes:**
- Names fixed (hardcoded: Ingeborg, Cornelia, Angelika)
- Emails editable in database (but not via UI)
- All three required for Confirmed status

---

## Affiliation Configuration

### Affiliation Colors

**Parameter:** `AFFILIATION_COLORS`

**Type:** Object mapping affiliation name to hex color

**Default:**
```json
{
  "Ingeborg": "#C1DBE3",
  "Cornelia": "#C7DFC5",
  "Angelika": "#DFAEB4"
}
```

**Notes:**
- Ingeborg: `#C1DBE3` (light blue)
- Cornelia: `#C7DFC5` (light green)
- Angelika: `#DFAEB4` (light pink)
- Ensure sufficient contrast with text
- Test in light and dark modes

---

## Holiday Configuration

### Holiday Region

**Parameter:** `HOLIDAY_REGION`

**Type:** String

**Default:** `"DE"` (or `"DE-NRW"` or other German state codes)

**Options:**
- `"DE"` - Federal holidays (all of Germany)
- `"DE-BW"` - Baden-Württemberg
- `"DE-BY"` - Bayern
- `"DE-NRW"` - Nordrhein-Westfalen
- (etc., all German state codes)

**Notes:**
- **Global config** (one region for entire app)
- **Optional:** Visual only; hidden if unavailable
- No business logic impact (bookings allowed on holidays)
- Calendar shows holidays for visual context only

---

## Digest Configuration

### Digest Schedule

**Parameter:** `DIGEST_SCHEDULE_DAY` / `DIGEST_SCHEDULE_TIME`

**Type:** Day of week + time of day

**Default:**
- Day: `Sunday`
- Time: `09:00`
- Timezone: `Europe/Berlin`

**Notes:**
- Cron: `0 9 * * 0` (every Sunday at 9 AM)
- Timezone always Europe/Berlin
- Configurable day/time if needed for testing

---

### Digest Inclusion Criteria

**Parameter:** `DIGEST_MIN_AGE_DAYS`

**Type:** Integer (days)

**Default:** `5`

**Notes:**
- Minimum age (in calendar days) before including in digest
- Day-0 rule: Submission date is day 0
- Future-only: Exclude past-dated bookings (`EndDate < today`)
- Order by soonest start date
- Suppress if zero items meet criteria

---

## Rate Limiting

### Daily Submission Limit

**Parameter:** `RATE_LIMIT_SUBMIT_PER_DAY`

**Type:** Integer (requests per day per email)

**Default:** `10`

**Notes:**
- Per requester email address
- Resets at midnight UTC (or Europe/Berlin if preferred)
- Prevents spam/abuse

---

### Per-IP Rate Limit

**Parameter:** `RATE_LIMIT_IP_PER_HOUR`

**Type:** Integer (requests per hour per IP)

**Default:** `30`

**Notes:**
- Applies to all endpoints
- Sliding window or fixed window
- Prevents DoS

---

### Link Recovery Rate Limit

**Parameter:** `RATE_LIMIT_RECOVERY_PER_HOUR`

**Type:** Integer (requests per hour per email)

**Default:** `5`

**Notes:**
- Applies to "Ist das deine Anfrage? Jetzt Link anfordern" flow
- Per email address
- Prevents enumeration attacks

---

### Soft Cooldown

**Parameter:** `SOFT_COOLDOWN_SECONDS`

**Type:** Integer (seconds)

**Default:** `60`

**Notes:**
- Cooldown period after link recovery request
- Per email/IP
- Shows message: "Bitte warte kurz – wir haben dir deinen persönlichen Link gerade erst gesendet."
- Part of BR-021

---

## Token Policy

### Token Expiry

**Parameter:** (N/A - no expiry)

**Default:** No expiry

**Notes:**
- Tokens never expire (per BR-010)
- Accepted risk for simplicity
- Personal and action links valid indefinitely

---

### Token Revocation

**Parameter:** (N/A - no revocation)

**Default:** No revocation mechanism

**Notes:**
- Tokens cannot be revoked (per BR-010)
- Resend existing token on recovery (don't generate new)
- Accepted risk for small trusted group

---

### Token Idempotency

**Parameter:** (Behavior, not configurable)

**Default:** All action links idempotent

**Notes:**
- Repeat actions show "Schon erledigt" result page
- Never error on repeat click
- Always redirect to result page

---

## Archive Policy

### Archive Retention

**Parameter:** `ARCHIVE_RETENTION_YEARS`

**Type:** Integer (years)

**Default:** `1`

**Notes:**
- Canceled items purged when archived > ARCHIVE_RETENTION_YEARS
- **Past Confirmed items never purged** (kept for history)
- **Denied items purged once EndDate < today**
- Monthly purge job (per BR-013)

---

## Auto-Cleanup

### Past-Dated Pending Auto-Cancel

**Parameter:** `AUTO_CLEANUP_ENABLED`

**Type:** Boolean

**Default:** `true`

**Notes:**
- At EndDate+1 00:00 Europe/Berlin
- Pending bookings where EndDate < today → Canceled → Archive
- Actor: System
- No notifications sent (per BR-028)
- Daily job

---

## Email Configuration

### Email Headers

**Parameter:** `EMAIL_FROM_NAME` / `EMAIL_FROM_ADDRESS`

**Type:** String

**Default:**
- From Name: `"Betzenstein App"`
- From Address: `"no-reply@<app-domain>"`

**Notes:**
- No Reply-To header
- Configure SPF/DKIM/DMARC for deliverability

---

### Email Format

**Parameter:** (Behavior, not configurable)

**Default:**
- HTML primary (dark-mode friendly)
- Plain-text fallback required

**Notes:**
- Test HTML in major email clients
- Ensure dark mode compatibility
- Plain-text should be readable

---

### Email Retry Policy

**Parameter:** `EMAIL_RETRY_ATTEMPTS` / `EMAIL_RETRY_BACKOFF`

**Type:** Integer (attempts) + backoff strategy

**Default:**
- Attempts: `~3`
- Backoff: Exponential (e.g., 2s, 4s, 8s)

**Notes:**
- Retry on transient failures (per BR-022)
- Log failures with correlation IDs
- Content consistent across retries
- Bounces: log-only (no user notification)

---

## Public Access

### Global Unlisted URL

**Parameter:** `PUBLIC_CALENDAR_URL`

**Type:** String (URL path)

**Default:** (Generated, e.g., `/calendar` or `/c/<unique-id>`)

**Notes:**
- **Unlisted** (not indexed by search engines)
- Same URL for all viewers (no authentication)
- Shows Pending/Confirmed only
- Denied/Canceled hidden

---

## Booking Constraints

### Maximum Party Size

**Parameter:** `MAX_PARTY_SIZE`

**Type:** Integer

**Default:** `10`

**Notes:**
- Minimum: 1 (at least requester)
- Maximum: MAX_PARTY_SIZE (configurable)
- Validation on create/edit (per BR-017)
- Error: "Teilnehmerzahl muss zwischen 1 und {{MAX}} liegen."

---

### Long Stay Warning Days

**Parameter:** `LONG_STAY_WARN_DAYS`

**Type:** Integer (days)

**Default:** `7`

**Notes:**
- If TotalDays > LONG_STAY_WARN_DAYS, show confirmation dialog (per BR-027)
- Prevents accidental long bookings
- User can confirm to proceed

---

### Future Horizon Months

**Parameter:** `FUTURE_HORIZON_MONTHS`

**Type:** Integer (months)

**Default:** `18`

**Notes:**
- Maximum advance booking period (per BR-026)
- Rule: `StartDate ≤ today + FUTURE_HORIZON_MONTHS`
- Error: "Anfragen dürfen nur maximal {{MONTHS}} Monate im Voraus gestellt werden."

---

## Email Validation

### Maximum Email Length

**Parameter:** `EMAIL_MAX_LEN`

**Type:** Integer (characters)

**Default:** `254`

**Notes:**
- Per RFC 5321 (standard max email length)
- Configurable if needed
- Validation per §9 rules

---

## Localization & Time

### Locale

**Parameter:** `LOCALE`

**Type:** String (BCP 47 language tag)

**Default:** `"de-DE"`

**Notes:**
- German only (per BR-011)
- Informal "du" tone
- Strings may be hardcoded (no i18n infrastructure initially)

---

### Timezone

**Parameter:** `TIMEZONE`

**Type:** String (IANA timezone)

**Default:** `"Europe/Berlin"`

**Notes:**
- All date/time operations use Europe/Berlin
- Store timestamps in UTC
- Convert to Europe/Berlin for display and business logic
- Past-dated flip at 00:00 Europe/Berlin

---

### Week Start Day

**Parameter:** `WEEK_START_DAY`

**Type:** String or Integer

**Default:** `"Monday"` (or `1` if 0-indexed from Sunday)

**Notes:**
- Week starts Monday (European standard)
- Calendar view displays accordingly

---

### Date Display Format

**Parameter:** `DATE_FORMAT`

**Type:** String (format pattern)

**Default:** `"DD.–DD.MM.YYYY"` (for ranges) or `"DD.MM.YYYY"` (for single dates)

**Example:** `"01.–05.08.2025"`

**Notes:**
- German date format (day.month.year)
- En-dash (–) for ranges, not hyphen (-)
- Consistent across all displays and emails

---

## Availability & SLA

### Formal Availability SLA

**Parameter:** (N/A)

**Default:** **No formal SLA**

**Notes:**
- Personal/small-group use
- Best-effort availability
- No uptime guarantees
- Accepted for this use case

---

## Data Residency

### Data Residency Requirements

**Parameter:** (N/A)

**Default:** No constraint

**Notes:**
- Can be hosted anywhere
- No GDPR-specific residency requirement for this small trusted group
- Owner accepts risk

---

## Quiet Hours

### Email Quiet Hours

**Parameter:** (N/A)

**Default:** None

**Notes:**
- Emails may send anytime (including nights, weekends, holidays)
- No quiet hours restriction
- Immediate notification on all actions

---

## Legal Pages

### Legal Pages (Impressum, Privacy, Terms)

**Parameter:** (N/A)

**Default:** Intentionally omitted

**Notes:**
- Small trusted group
- Owner accepts risk
- No public legal pages required for this use case

---

## Configuration Summary Table

| Parameter | Default | Configurable | Notes |
|-----------|---------|--------------|-------|
| `APPROVER_PARTIES` | Ingeborg, Cornelia, Angelika | Yes (DB) | Fixed names; emails editable |
| `AFFILIATION_COLORS` | See above | Yes | Ensure contrast |
| `HOLIDAY_REGION` | `"DE"` or state code | Yes | Global; optional; visual only |
| `DIGEST_SCHEDULE_DAY` | `Sunday` | Yes | Cron day |
| `DIGEST_SCHEDULE_TIME` | `09:00` | Yes | Europe/Berlin |
| `DIGEST_MIN_AGE_DAYS` | `5` | Yes | Day-0 rule |
| `RATE_LIMIT_SUBMIT_PER_DAY` | `10` | Yes | Per email |
| `RATE_LIMIT_IP_PER_HOUR` | `30` | Yes | Per IP |
| `RATE_LIMIT_RECOVERY_PER_HOUR` | `5` | Yes | Per email |
| `SOFT_COOLDOWN_SECONDS` | `60` | Yes | Per email/IP |
| Token Expiry | None | No | Per BR-010 |
| Token Revocation | None | No | Per BR-010 |
| `ARCHIVE_RETENTION_YEARS` | `1` | Yes | Canceled items only |
| `AUTO_CLEANUP_ENABLED` | `true` | Yes | Past Pending → Canceled |
| `EMAIL_FROM_NAME` | `"Betzenstein App"` | Yes | Display name |
| `EMAIL_FROM_ADDRESS` | `no-reply@<domain>` | Yes | Sender address |
| `EMAIL_RETRY_ATTEMPTS` | `~3` | Yes | With backoff |
| `PUBLIC_CALENDAR_URL` | Generated | Yes | Unlisted |
| `MAX_PARTY_SIZE` | `10` | Yes | Per BR-017 |
| `LONG_STAY_WARN_DAYS` | `7` | Yes | Per BR-027 |
| `FUTURE_HORIZON_MONTHS` | `18` | Yes | Per BR-026 |
| `EMAIL_MAX_LEN` | `254` | Yes | RFC standard |
| `LOCALE` | `"de-DE"` | No | German only |
| `TIMEZONE` | `"Europe/Berlin"` | No | Fixed |
| `WEEK_START_DAY` | `Monday` | No | European |
| `DATE_FORMAT` | `DD.–DD.MM.YYYY` | No | German |
| Availability SLA | None | No | Best-effort |
| Data Residency | No constraint | No | Any location |
| Quiet Hours | None | No | 24/7 emails |
| Legal Pages | Omitted | No | Small group risk |

---

## Environment-Specific Configuration

### Development

**Suggested Overrides:**
- `RATE_LIMIT_*`: Higher or disabled for testing
- `DIGEST_SCHEDULE_TIME`: More frequent for testing
- `EMAIL_*`: Use test email service (Mailtrap, etc.)
- `AUTO_CLEANUP_ENABLED`: Maybe disabled for debugging

---

### Staging

**Suggested Overrides:**
- Similar to production
- Maybe separate email domain (staging.example.com)
- Lower rate limits if sharing resources

---

### Production

**Configuration:**
- All defaults as specified
- Production email service (reliable ESP)
- Monitoring and alerting enabled
- Backups configured

---

## Configuration Management

### Storage

**Options:**
1. Environment variables (for sensitive values like emails, API keys)
2. Configuration file (JSON, YAML)
3. Database (for runtime-editable values like approver emails)

**Recommended:**
- Environment variables: Email service credentials, domain
- Database: Approver emails, affiliation colors, rate limits
- Code constants: Non-sensitive defaults (locale, timezone, date format)

### Deployment

- Use secret management for sensitive config (e.g., Vault, AWS Secrets Manager)
- Version control configuration files (exclude secrets)
- Document all parameters and defaults
- Provide example `.env.example` file

### Runtime Changes

**Can be changed without code deploy:**
- Approver emails (DB update)
- Rate limits (DB update or config reload)
- Affiliation colors (DB update)
- Holiday region (config reload)

**Require code deploy:**
- Locale, timezone, date format (hardcoded)
- Token policy (hardcoded per BR-010)
- Core business rules

---

## Testing Configuration

### Test Data

**Suggested Config for Tests:**
- `MAX_PARTY_SIZE`: 3 (smaller for faster tests)
- `FUTURE_HORIZON_MONTHS`: 6 (smaller range)
- `DIGEST_MIN_AGE_DAYS`: 1 (faster testing)
- `SOFT_COOLDOWN_SECONDS`: 1 (faster tests)
- `RATE_LIMIT_*`: High or disabled

### Mock Services

- Email service: Use mock or test inbox
- Holiday API: Mock or use test data
- Clock: Mock for time-based tests (past-dated, auto-cleanup)

---

## Monitoring Configuration

### Metrics to Track

- Booking creation rate
- Approval/denial rates
- Email delivery success rate
- Error rates by type
- API response times
- Conflict detection rate

### Alerts

- Email delivery failure rate > 5%
- Error rate > 1%
- API response time > 2s
- Database connection issues
- Auto-cleanup failures

---

## Security Configuration

### Token Signing

**Parameter:** `TOKEN_SECRET`

**Type:** String (secret key)

**Notes:**
- Use strong random key (e.g., 256-bit)
- Rotate periodically (though requires re-issuing all tokens)
- Store securely (environment variable, secret manager)

### HTTPS

**Requirement:** Mandatory

**Notes:**
- All traffic over HTTPS
- No HTTP allowed (redirect to HTTPS)
- Valid SSL/TLS certificate

### CORS

**Configuration:** If API and frontend on different domains

**Notes:**
- Whitelist specific origins
- Don't use wildcard (*) in production

---

## Implementation Notes

### Configuration Precedence

Recommended order (highest to lowest priority):
1. Environment variables (runtime overrides)
2. Database values (runtime-editable)
3. Configuration file (deployment-specific)
4. Code defaults (fallback)

### Validation

- Validate all configuration on startup
- Fail fast if required config missing or invalid
- Log configuration (sanitized, no secrets) on startup

### Documentation

- Document all parameters in code (comments)
- Provide example configuration files
- Maintain this specification document as single source of truth
