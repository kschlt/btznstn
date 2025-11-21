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

## Rationale

### Why Resend vs SendGrid vs Mailgun?

**Resend (Chosen):**
- ✅ **Simple API** - `resend.emails.send()` - easy for AI
- ✅ **Modern DX** - Built for developers, not marketing teams
- ✅ **Free tier** - 100 emails/day (enough for us)
- ✅ **React Email support** - Can use JSX for templates (optional)
- ✅ **Fast delivery** - Good reputation

**SendGrid (Rejected):**
- ❌ Complex API (marketing-focused)
- ❌ Cluttered UI (campaigns, analytics overkill)
- ❌ More expensive for simple use case

**Mailgun (Rejected):**
- ❌ More expensive ($35/month minimum)
- ❌ Less modern API

---

## Consequences

### Positive

✅ **Simple integration** - 5 lines of Python code
✅ **Free for our volume** - 100 emails/day, 3000/month
✅ **Good deliverability** - High reputation
✅ **Developer-friendly** - No marketing bloat

### Negative

⚠️ **Newer service** - Less mature than SendGrid/Mailgun (founded 2022)
⚠️ **Vendor lock-in** - API not standard (but simple to migrate)

### Neutral

➡️ **No EU region** - Servers in US (acceptable for email)

---

## Implementation Pattern

### Send Email

```python
import resend
from app.core.config import settings

resend.api_key = settings.resend_api_key

def send_approval_email(to: str, approver_name: str, booking_id: str):
    """Send approval notification email."""
    resend.Emails.send({
        "from": "Betzenstein <noreply@betzenstein.app>",
        "to": to,
        "subject": f"{approver_name} hat zugestimmt",
        "html": "<p>...</p>",  # German template
    })
```

### Configuration

```bash
# .env
RESEND_API_KEY=re_xxx
```

---

## References

**Related ADRs:**
- ADR-001: Backend Framework (FastAPI + Resend integration)

**Business Rules:**
- BR-022: Email retry logic (3 attempts, exponential backoff)

**Tools:**
- [Resend](https://resend.com/)
- [Resend Python SDK](https://github.com/resend/resend-python)

**Templates:**
- [`docs/specification/notifications.md`](../../docs/specification/notifications.md) - All 11 German templates
