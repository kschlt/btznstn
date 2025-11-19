# Deployment - CLAUDE Guide

## What's in This Section

This guide helps you **approach production deployment** for the Betzenstein Booking application.

**What you'll find here:**
- How to approach deployment (workflow patterns)
- Critical deployment gotchas (mistakes to avoid)
- Where to find deployment specifications (navigation)
- How deployment relates to business rules

**What you WON'T find here:**
- Specific deployment commands (see [`specifications.md`](specifications.md))
- Exact configuration files (see [`specifications.md`](specifications.md))
- Step-by-step procedures (see Phase 8 user stories in [`/docs/implementation/phase-8-polish.md`](/docs/implementation/phase-8-polish.md))

---

## Where to Find Deployment Information

**Before deploying, read these in order:**

1. **User Stories (WHAT to do):**
   - [`/docs/implementation/phase-8-polish.md`](/docs/implementation/phase-8-polish.md) - US-8.3: Production Deployment
   - Defines acceptance criteria, Gherkin scenarios, what must be verified

2. **Deployment Specifications (WHAT to configure):**
   - [`specifications.md`](specifications.md) - Fly.io commands, Vercel setup, exact configs, environment variables
   - Single source of truth for all deployment specifics

3. **Business Rules (WHY certain patterns required):**
   - [`/docs/foundation/business-rules.md`](/docs/foundation/business-rules.md) - BR-010, BR-012, BR-013, BR-021, BR-022, BR-024, BR-028, BR-029
   - Production deployment must enforce these server-side

4. **Architecture Decisions:**
   - [`/docs/architecture/adr-002-deployment.md`](/docs/architecture/adr-002-deployment.md) - Why Fly.io Frankfurt, why Vercel
   - [`/docs/architecture/technology-stack.md`](/docs/architecture/technology-stack.md) - Deployment stack rationale

---

## Critical Production Business Rules

**These BRs MUST be enforced in production (server-side only):**

| BR | What It Requires | Common Mistake | How to Verify |
|----|------------------|----------------|---------------|
| **BR-010** | Tokens never expire, links always redirect to result page | Returning 404/500 on retry clicks | Click approval link twice, both show success |
| **BR-012** | Rate limits: 10/day email, 30/hour IP, 5/hour recovery | Only client-side limits | API call with >10 bookings/day, 11th rejected |
| **BR-021** | 60-second cooldown on link recovery | No cooldown tracking | Request recovery twice in 60s, second blocked |
| **BR-022** | Email retries: 3 attempts, delays 2s, 4s, 8s | Wrong delays or no retries | Simulate email failure, verify 3 attempts in logs |
| **BR-024** | First-action-wins (approve/deny concurrency) | No SELECT FOR UPDATE | Two approvers click approve simultaneously, one wins |
| **BR-028** | Auto-cleanup: Daily at 00:01 Europe/Berlin | Scheduled in UTC instead | Verify job runs at 00:01 Berlin time, not UTC |
| **BR-029** | First-write-wins (booking creation concurrency) | No transaction isolation | Two users book same dates, first wins |

**Reference:** Full BR details in [`/docs/foundation/business-rules.md`](/docs/foundation/business-rules.md)

---

## Deployment Workflow Pattern

**How to approach deployment (test-first):**

### 1. Pre-Deployment (Local Testing)

**Goal:** Verify production patterns work locally before deploying

**Pattern:**
```
Read Phase 8 specs → Write production tests → Run locally → All pass → Deploy
```

**What to test locally:**
- Rate limiting enforced (backend, not client)
- Background jobs execute at correct time (Europe/Berlin timezone)
- Email retry logic (3 attempts, exponential backoff)
- Concurrency safety (SELECT FOR UPDATE prevents races)
- Token validation (never expires, always redirects)

**How to test:**
- Use production-like environment variables
- Run backend with production config
- Execute background job scheduler manually
- Simulate concurrent requests (multiple API clients)

---

### 2. Infrastructure Setup

**Goal:** Configure deployment platforms before code deployment

**Pattern:**
```
Backend (Fly.io) → Database (Fly.io Postgres) → Email (Resend) → Frontend (Vercel)
```

**Critical gotcha:** Set up in this order (backend needs DB, frontend needs backend URL)

**What you're configuring:**
- Fly.io app + database (Frankfurt region)
- Resend domain verification (DNS records)
- Vercel project (GitHub integration)
- Environment variables (secrets)

**Where to find specs:** [`specifications.md`](specifications.md) - Section "Infrastructure Setup"

---

### 3. Database Migration

**Goal:** Apply schema changes safely in production

**Pattern:**
```
Backup → Run migration → Verify indexes → Test queries
```

**Critical gotchas:**
- **Timezone:** Database stores UTC, application converts to Europe/Berlin
- **Indexes:** Must create ALL indexes from schema (date ranges, foreign keys, status)
- **Connection pooling:** Configure BEFORE first deploy (prevents connection exhaustion)

**How to verify:**
- Run `\di` in psql to list indexes
- Run EXPLAIN on critical queries (calendar month, approver lists)
- Verify indexes used (not sequential scans)

**Where to find specs:** [`specifications.md`](specifications.md) - Section "Database Setup"

---

### 4. Environment Variables & Secrets

**Goal:** Configure production without hardcoding values

**Pattern:**
```
Secrets (Fly.io) → Public vars (Vercel) → Backend reads → Frontend reads
```

**Critical gotchas:**
- **Never commit:** DATABASE_URL, JWT_SECRET, RESEND_API_KEY
- **Server-side only:** Rate limit configs, email retry configs
- **Public vars:** Only NEXT_PUBLIC_API_URL in frontend

**How to verify:**
- Backend logs show correct timezone (Europe/Berlin)
- API connects to database
- Emails send successfully
- Frontend API calls reach backend

**Where to find specs:** [`specifications.md`](specifications.md) - Section "Environment Variables"

---

### 5. Background Jobs Scheduling

**Goal:** Cron jobs run at correct time in correct timezone

**Pattern:**
```
Define jobs → Schedule with Europe/Berlin timezone → Test execution → Monitor logs
```

**Critical gotchas:**
- **Timezone:** MUST use `pytz.timezone('Europe/Berlin')`, NOT UTC
- **Job failure:** Log execution, don't silently fail
- **Idempotency:** Jobs must be safe to run multiple times

**Jobs required:**
- Auto-cleanup: Daily at 00:01 Berlin time (BR-028)
- Archive purge: Monthly at 02:00 Berlin time (BR-013)
- Weekly digest: Sunday 09:00 Berlin time (BR-009)

**How to verify:**
- Check scheduler logs at job time
- Verify jobs execute (query database for changes)
- Test job manually (call function directly)

**Where to find specs:** [`specifications.md`](specifications.md) - Section "Background Jobs"

---

### 6. Rate Limiting Implementation

**Goal:** Prevent abuse with server-side limits

**Pattern:**
```
Request → Check limit (backend) → Reject if exceeded → Return German error
```

**Critical gotchas:**
- **Server-side ONLY:** Client-side limits can be bypassed
- **Track correctly:** Per email (bookings), per IP (requests), per email (recovery)
- **German errors:** Must use exact copy from [`/docs/specification/error-handling.md`](/docs/specification/error-handling.md)

**Limits to enforce (BR-012):**
- 10 bookings per day per email
- 30 requests per hour per IP
- 5 link recovery requests per hour per email
- 60-second cooldown on link recovery (BR-021)

**How to verify:**
- Submit 11 bookings from same email, 11th rejected
- Make 31 requests from same IP, 31st rejected
- Request recovery twice in 60s, second shows cooldown message

**Where to find specs:** [`specifications.md`](specifications.md) - Section "Rate Limiting"

---

### 7. Email Delivery Setup

**Goal:** Reliable email delivery with retry logic

**Pattern:**
```
Verify domain (DNS) → Configure API key → Implement retry logic → Test delivery
```

**Critical gotchas:**
- **Domain verification:** DNS propagation takes time (up to 48h)
- **Retry logic:** MUST match BR-022 exactly (2s, 4s, 8s delays)
- **Content immutability:** Email content unchanged across retries

**How to verify:**
- Send test email, check Resend dashboard
- Simulate failure, verify 3 retry attempts in logs
- Verify delays match spec (2s, 4s, 8s, not other values)

**Where to find specs:** [`specifications.md`](specifications.md) - Section "Email Service (Resend)"

---

### 8. Deploy & Verify

**Goal:** Deploy code and verify production behavior

**Pattern:**
```
Deploy backend → Run smoke tests → Deploy frontend → Run E2E tests → Monitor
```

**What to verify (conceptual):**
- Health check returns 200 OK
- Database queries use indexes (fast response times)
- Rate limiting enforced
- Background jobs execute at correct time
- Emails deliver successfully
- Concurrency safety (no race conditions)

**How to verify:**
- Run smoke tests (create booking, approve, deny)
- Check logs for errors
- Monitor response times (p95 <500ms)
- Test concurrent operations (two approvers approve simultaneously)

**Where to find specs:** [`specifications.md`](specifications.md) - Section "Production Checklist"

---

## Common Deployment Gotchas

### 1. Timezone Confusion (BR-028, BR-009)

**Mistake:** Scheduling jobs in UTC instead of Europe/Berlin

**Why it's wrong:**
- "Daily at 00:01" means 00:01 Berlin time, not UTC
- UTC midnight ≠ Berlin midnight (1-2 hour difference depending on DST)

**Correct pattern:**
- Always use `pytz.timezone('Europe/Berlin')` for job scheduler
- Database stores UTC, application converts to Berlin for business logic
- "Past determination" uses Europe/Berlin (not UTC)

**How to catch:**
- Test job execution manually at expected time
- Check logs show Berlin time, not UTC

---

### 2. Client-Side Rate Limiting (BR-012)

**Mistake:** Only enforcing rate limits in frontend, not backend

**Why it's wrong:**
- Users can bypass client checks (browser dev tools, direct API calls)
- Security MUST be server-side

**Correct pattern:**
- Backend checks limits BEFORE database operations
- Return 429 status code with German error message
- Frontend shows limit (UX only, not security)

**How to catch:**
- Make API calls directly (bypass frontend)
- Submit >10 bookings via curl or Postman
- Verify 11th request rejected by backend

---

### 3. Email Retry Delays (BR-022)

**Mistake:** Using wrong delays (1s, 2s, 4s) or linear backoff

**Why it's wrong:**
- BR-022 specifies exact delays: 2s, 4s, 8s
- Too short → overloads email service
- Wrong pattern → not compliant with spec

**Correct pattern:**
- Delays array: `[2, 4, 8]` seconds
- Exponential backoff (each doubles)
- 3 attempts total (initial + 2 retries)

**How to catch:**
- Simulate email failure, check logs for delay times
- Verify "retry in 2s", "retry in 4s", "failed after 8s"

---

### 4. SELECT FOR UPDATE Missing (BR-024, BR-029)

**Mistake:** Not locking rows during concurrent operations

**Why it's wrong:**
- Two approvers click approve → both think they're first → data corruption
- Two users book same dates → both think it's free → double-booking

**Correct pattern:**
- Use `SELECT FOR UPDATE` to lock booking row
- Check state after lock acquired
- Update atomically within transaction

**How to catch:**
- Test concurrent approvals (Playwright with Promise.all)
- Verify one succeeds, other sees "Schon erledigt"
- Check database: only one approval recorded

---

### 5. Token Expiration (BR-010 Violation)

**Mistake:** Implementing token expiration or revoking tokens

**Why it's wrong:**
- BR-010: "Tokens never expire, never revoked"
- Users must be able to click approval link anytime
- Action links always redirect to result page (not 404/500)

**Correct pattern:**
- No expiration check in token validation
- Idempotent: second click shows success page, not error
- Even years later, token still works

**How to catch:**
- Click approval link, then click again → both show success
- Wait 24 hours, click link → still works
- Check code: no expiration logic

---

### 6. Deadlocks in Concurrent Operations

**Mistake:** Locking rows in inconsistent order

**Why it's wrong:**
- Transaction A locks booking then approvals
- Transaction B locks approvals then booking
- → Deadlock, database aborts one transaction

**Correct pattern:**
- ALWAYS lock in same order: booking → approvals → parties
- Document lock order in code comments
- Test concurrent operations

**How to catch:**
- Run concurrent approval tests
- Check logs for deadlock errors
- Verify no "deadlock detected" messages

---

## Verification Checklist (Conceptual)

**Before going live, verify these patterns (not specific steps):**

### Infrastructure
- [ ] Backend deployed to Frankfurt region (EU data residency)
- [ ] Database in same region as backend (low latency)
- [ ] Frontend on global CDN (fast worldwide)
- [ ] HTTPS enforced (all HTTP redirects)

### Business Rules
- [ ] Rate limiting enforced server-side (BR-012)
- [ ] Token validation never expires (BR-010)
- [ ] Background jobs scheduled in Europe/Berlin timezone (BR-028, BR-009)
- [ ] Email retries match spec (2s, 4s, 8s) (BR-022)
- [ ] Concurrency safety implemented (BR-024, BR-029)

### Data & Security
- [ ] Database indexes created (date ranges, foreign keys)
- [ ] Secrets not committed to git (DATABASE_URL, JWT_SECRET, API keys)
- [ ] CORS configured (allow frontend origin only)
- [ ] Security headers present (HSTS, X-Frame-Options)

### Monitoring & Reliability
- [ ] Health check endpoint works
- [ ] Error logging configured
- [ ] Email delivery monitored
- [ ] Background job execution logged
- [ ] Response times meet targets (p95 <500ms)

**Where to find detailed checklist:** [`specifications.md`](specifications.md) - Section "Production Checklist"

---

## How to Debug Production Issues

### Issue Pattern: "Emails not delivering"

**Diagnosis approach:**
1. Check Resend dashboard (delivery status, bounces)
2. Verify domain DNS records (TXT, MX)
3. Check API key correct
4. Review retry logs (3 attempts, correct delays)
5. Test with different email provider (not just Gmail)

**Where to find details:** [`specifications.md`](specifications.md) - Section "Email Delivery Setup"

---

### Issue Pattern: "Background jobs not running"

**Diagnosis approach:**
1. Check scheduler logs (job scheduled?)
2. Verify timezone (Europe/Berlin, not UTC)
3. Test job function directly (bypass scheduler)
4. Check cron syntax (hour, minute, day_of_week)
5. Ensure scheduler started in main app

**Where to find details:** [`specifications.md`](specifications.md) - Section "Background Jobs"

---

### Issue Pattern: "Rate limiting bypassed"

**Diagnosis approach:**
1. Verify backend enforcement (not just frontend)
2. Test with direct API calls (curl/Postman)
3. Check rate limit storage (Redis or in-memory)
4. Verify counters reset correctly (daily/hourly)
5. Test with >10 bookings from same email

**Where to find details:** [`specifications.md`](specifications.md) - Section "Rate Limiting"

---

### Issue Pattern: "Concurrent operations corrupted data"

**Diagnosis approach:**
1. Check SELECT FOR UPDATE used
2. Verify transaction isolation level
3. Test concurrent operations (two approvers)
4. Check lock order consistent
5. Review logs for deadlock errors

**Where to find details:** [`specifications.md`](specifications.md) - Section "Concurrency Safety"

---

## Summary: HOW to Approach Deployment

**Workflow:**
1. Read Phase 8 user stories (WHAT must be done)
2. Read specifications.md (WHAT to configure)
3. Test production patterns locally first
4. Deploy infrastructure (Fly.io, Resend, Vercel)
5. Configure environment variables & secrets
6. Run database migrations & verify indexes
7. Deploy code (backend first, then frontend)
8. Verify critical patterns (rate limiting, concurrency, jobs, emails)
9. Monitor production (logs, errors, response times)

**Critical patterns to verify:**
- Server-side rate limiting (BR-012)
- Europe/Berlin timezone for jobs (BR-028, BR-009)
- Email retry with exact delays (BR-022)
- SELECT FOR UPDATE for concurrency (BR-024, BR-029)
- Token never expires (BR-010)

**Where to find specifics:**
- User stories: [`/docs/implementation/phase-8-polish.md`](/docs/implementation/phase-8-polish.md)
- Deployment specs: [`specifications.md`](specifications.md)
- Business rules: [`/docs/foundation/business-rules.md`](/docs/foundation/business-rules.md)

**Next step:** Read [`specifications.md`](specifications.md) for exact deployment commands and configurations.
