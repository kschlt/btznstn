# ADR-004: Email Service

**Status:** Accepted
**Date:** 2025-01-17
**Deciders:** Solution Architect
**Context:** Need transactional email for notifications

---

## Context

Need email service for:
- Transactional emails (booking notifications, approvals, denials)
- German-language templates (11 templates)
- Action links (one-click approve/deny with tokens)
- Weekly digest (Sunday 09:00)
- Retry logic (BR-022: 3 attempts, exponential backoff)
- Low volume (~100 emails/day)

---

## Decision

Use **Resend** as the email service provider.

---

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| Email Service | Resend API | SendGrid, Mailgun, AWS SES |
| API Pattern | `resend.Emails.send()` | Complex marketing APIs |
| API Key | Resend API key from config | Hardcoded keys |
| SDK | Resend Python SDK | Direct HTTP calls |

---

## Rationale

**Why Resend:**
- Resend provides simple API (`resend.Emails.send()`) → **Constraint:** MUST use Resend API (not SendGrid/Mailgun)
- Resend built for developers → **Constraint:** MUST use simple API pattern (no marketing-focused complexity)
- Resend free tier covers our volume → **Constraint:** MUST use Resend free tier (100 emails/day)

**Why NOT SendGrid:**
- SendGrid uses complex marketing-focused API → **Violation:** Complex API violates simplicity requirement and increases implementation complexity
- SendGrid requires more expensive plans → **Violation:** Higher cost violates free tier requirement

---

## Consequences

### MUST (Required)

- MUST use Resend API (`resend.Emails.send()`) - Resend's simple API pattern, developer-friendly
- MUST use Resend Python SDK - Official SDK provides proper error handling and type safety
- MUST configure Resend API key via environment variable - API key must come from configuration, not hardcoded

### MUST NOT (Forbidden)

- MUST NOT use SendGrid/Mailgun/AWS SES - Violates Resend decision
- MUST NOT make direct HTTP calls to Resend API - Must use official Python SDK
- MUST NOT hardcode API keys - Must use configuration management

### Trade-offs

- Newer service - Resend is less mature than SendGrid/Mailgun (founded 2022). Mitigation: Simple API reduces risk, easy to migrate if needed.
- Vendor lock-in - API not standard. Mitigation: Simple API makes migration straightforward if needed.

### Applies To

- ALL email service implementation (Phase 4, 5, 6, 7, 8)
- File patterns: `app/services/email_service.py`
- Email service configuration: `app/core/config.py`

### Validation Commands

- `grep -r "sendgrid\|mailgun\|ses" app/` (should be empty - must use Resend)
- `grep -r "resend.Emails.send\|from resend" app/services/` (should be present)
- `grep -r "RESEND_API_KEY" app/core/config.py` (should be present)

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - Backend Framework (FastAPI + Resend integration)

---

## References

**Related ADRs:**
- [ADR-001](adr-001-backend-framework.md) - Backend Framework (FastAPI + Resend integration)

**Tools:**
- [Resend](https://resend.com/)
- [Resend Python SDK](https://github.com/resend/resend-python)

**Implementation:**
- `app/services/email_service.py` - Email service implementation
- `app/core/config.py` - Resend API key configuration
