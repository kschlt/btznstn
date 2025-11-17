# ADR-004: Email Service - Resend

**Status:** Accepted
**Date:** 2025-01-17
**Deciders:** Solution Architect
**Context:** AI-driven development (Claude Code)

---

## Context

We need to choose an email service provider for the Betzenstein booking & approval application. The system must send:

- Transactional emails (booking notifications, approvals, denials)
- German-language emails (informal "du" tone)
- HTML emails with plain-text fallback
- Action links (one-click approve/deny)
- Weekly digest emails (Sunday 09:00)

### Requirements from Specifications

From `docs/specification/notifications.md` and `docs/foundation/business-rules.md`:

- **BR-022:** Email retries (3 attempts, exponential backoff)
- **11 email templates** (submission, approve, deny, cancel, etc.)
- **German copy** (all emails in German)
- **Action links** (signed tokens for approve/deny)
- **Free tier or cheap** (small volume, ~100 emails/day)
- **Easy integration** (simple API for AI to use)

---

## Decision

We will use **Resend** as the email service provider.

---

## Rationale

### 1. Modern & Developer-Friendly (Critical for AI)

**Why this matters:** AI needs simple, clear APIs.

**Resend benefits:**
- ✅ **Simple API** - One endpoint, minimal configuration
- ✅ **Modern** - Built 2023, current best practices
- ✅ **Well-documented** - Excellent docs, AI can reference
- ✅ **Type-safe SDK** - Official Python SDK with types

**Example (AI-friendly):**
```python
import resend

resend.api_key = "re_..."

email = resend.Emails.send({
    "from": "no-reply@betzenstein.app",
    "to": "user@example.com",
    "subject": "Neue Buchungsanfrage",
    "html": "<p>...</p>"
})
```

**Contrast with SendGrid (more complex):**
```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

message = Mail(
    from_email='no-reply@betzenstein.app',
    to_emails='user@example.com',
    subject='Neue Buchungsanfrage',
    html_content='<p>...</p>')

sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
response = sg.send(message)
```

Resend is simpler - fewer steps, less for AI to get wrong.

### 2. React Email (Template Management)

**Benefit:** Build email templates in React (type-safe).

**Resend + React Email:**
- ✅ **Components for emails** - Reusable, maintainable
- ✅ **TypeScript** - Type-safe template props
- ✅ **Preview locally** - See emails during development
- ✅ **AI-friendly** - React is familiar to AI

**Example:**
```tsx
// emails/NewBookingNotification.tsx
import { Html, Text, Link } from '@react-email/components';

interface NewBookingEmailProps {
  approverName: string;
  requesterName: string;
  dateRange: string;
  partySize: number;
  approveLink: string;
  denyLink: string;
}

export default function NewBookingEmail(props: NewBookingEmailProps) {
  return (
    <Html>
      <Text>Hallo {props.approverName},</Text>
      <Text>Es gibt eine neue Buchungsanfrage:</Text>
      <Text>Von: {props.requesterName}</Text>
      <Text>Zeitraum: {props.dateRange}</Text>
      <Text>Teilnehmer: {props.partySize} Personen</Text>
      <Link href={props.approveLink}>Zustimmen</Link>
      <Link href={props.denyLink}>Ablehnen</Link>
    </Html>
  );
}
```

**AI benefit:** AI knows React well. Can generate email templates easily.

### 3. Free Tier & Pricing

**Requirement:** Cheap for small volume.

**Resend pricing:**
- ✅ **Free tier:** 100 emails/day, 3,000/month
- ✅ **Paid tier:** $20/month for 50,000 emails

**Our volume:** ~50-100 emails/day max (notifications, digest).

**Fits free tier** for initial rollout. Can upgrade if needed.

**Comparison:**
- **SendGrid:** 100/day forever free (more generous long-term)
- **Postmark:** 100/month free, then $1.25 per 1,000
- **AWS SES:** $0.10 per 1,000 (cheapest at scale, but complex setup)

**Decision:** Resend free tier sufficient. Simplicity > cost optimization.

### 4. Deliverability

**Requirement:** Emails must reach inbox (not spam).

**Resend:**
- ✅ **Good reputation** - New service, clean IP pools
- ✅ **DKIM/SPF/DMARC** - Automatic setup
- ✅ **Bounce handling** - Automatic
- ✅ **Analytics** - Open rates, bounces (optional tracking)

**Evidence:** Resend is built by Vercel team - high quality standards.

### 5. Integration with FastAPI

**Requirement:** Easy to call from FastAPI async handlers.

**Resend SDK:**
- ✅ **Python SDK** - `pip install resend`
- ✅ **Async support** - Can use with `httpx` for async calls
- ✅ **Error handling** - Clear exceptions

**Example (FastAPI service):**
```python
# app/services/email_service.py
import resend
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY

class EmailService:
    async def send_booking_notification(
        self,
        to_email: str,
        approver_name: str,
        booking_data: dict
    ):
        try:
            email = resend.Emails.send({
                "from": settings.FROM_EMAIL,
                "to": to_email,
                "subject": f"Neue Buchungsanfrage ({booking_data['date_range']})",
                "html": render_template("new_booking", {
                    "approver_name": approver_name,
                    "booking": booking_data
                })
            })
            logger.info(f"Email sent: {email['id']}")
            return email
        except resend.exceptions.ResendError as e:
            logger.error(f"Email failed: {e}")
            raise
```

### 6. Retry Logic (BR-022)

**Requirement:** 3 retries with exponential backoff.

**Implementation:**
- Resend API handles some retries automatically
- Add custom retry logic in FastAPI for extra reliability

**Example:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def send_email_with_retry(email_data: dict):
    return resend.Emails.send(email_data)
```

**AI benefit:** Standard pattern, AI knows `tenacity` library.

### 7. Testing & Development

**Benefit:** Easy to test without sending real emails.

**Resend:**
- ✅ **Test mode** - API key for testing
- ✅ **Email preview** - See emails before sending
- ✅ **Logs** - See all sent emails in dashboard

**Development:**
```python
# app/core/config.py
class Settings(BaseSettings):
    RESEND_API_KEY: str
    ENVIRONMENT: str = "development"

    def send_email(self, data: dict):
        if self.ENVIRONMENT == "development":
            logger.info(f"[DEV] Would send email: {data}")
            return {"id": "test-id"}
        else:
            return resend.Emails.send(data)
```

---

## Alternatives Considered

### SendGrid

**Pros:**
- Very mature (10+ years)
- Generous free tier (100/day forever)
- Large ecosystem

**Cons:**
- ❌ **More complex API** - More configuration, more steps
- ❌ **Older patterns** - Not as modern as Resend
- ❌ **Heavier SDK** - More dependencies
- ❌ **More features** - Marketing emails, etc. (we don't need)

**Decision:** Resend is simpler for transactional emails.

---

### Postmark

**Pros:**
- Excellent deliverability (best in class)
- Transactional-focused
- Good docs

**Cons:**
- ⚠️ **Smaller free tier** - 100/month (not 100/day)
- ⚠️ **No React Email** - Custom templates
- ⚠️ **Less modern** - Older than Resend

**Decision:** Resend's free tier better, React Email is nice bonus.

---

### AWS SES

**Pros:**
- Cheapest at scale ($0.10 per 1,000)
- Very reliable

**Cons:**
- ❌ **Complex setup** - IAM, SES verification, etc.
- ❌ **More ops work** - Manage bounce handling, etc.
- ❌ **No nice SDK** - boto3 is verbose
- ❌ **More for AI to configure** - Higher error chance

**Decision:** Not worth complexity for small volume.

---

### Mailgun

**Pros:**
- Mature, reliable
- Good pricing

**Cons:**
- ⚠️ **Older** - Not as modern as Resend
- ⚠️ **No React Email** - Custom templates
- ⚠️ **More complex** - Similar to SendGrid

**Decision:** Resend is more modern and simpler.

---

## Consequences

### Positive

✅ **Simple API** - One endpoint, minimal config, AI-friendly
✅ **React Email** - Type-safe templates, preview locally
✅ **Free tier sufficient** - 100/day covers our needs
✅ **Good deliverability** - DKIM/SPF automatic
✅ **Easy testing** - Test mode, logs, preview
✅ **Modern** - Best practices, current standards
✅ **Python SDK** - Official, typed, easy to use

### Negative

⚠️ **Newer service** (2023) - Less proven than SendGrid/Postmark
⚠️ **Smaller free tier long-term** - SendGrid's 100/day forever better if volume grows
⚠️ **Vendor lock-in** (minor) - React Email templates specific to Resend

### Neutral

➡️ **Domain verification** - Need to verify sending domain (standard for all ESPs)
➡️ **API key management** - Need to secure API key (standard)

---

## Implementation Notes

### Setup

1. **Create Resend account** - https://resend.com
2. **Verify domain** - Add DNS records for `betzenstein.app`
3. **Get API key** - Generate API key for production
4. **Install SDK:**
   ```bash
   pip install resend
   ```

### Configuration

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    RESEND_API_KEY: str
    FROM_EMAIL: str = "no-reply@betzenstein.app"
    FROM_NAME: str = "Betzenstein App"

    class Config:
        env_file = ".env"
```

### Email Service

```python
# app/services/email_service.py
import resend
from tenacity import retry, stop_after_attempt, wait_exponential

class EmailService:
    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def send(self, to: str, subject: str, html: str):
        return resend.Emails.send({
            "from": f"{settings.FROM_NAME} <{settings.FROM_EMAIL}>",
            "to": to,
            "subject": subject,
            "html": html,
            "text": self.html_to_text(html)  # Plain-text fallback
        })

    def html_to_text(self, html: str) -> str:
        # Strip HTML tags for plain-text version
        # Use html2text library or simple regex
        ...
```

### Email Templates

**Option 1: React Email (Recommended)**
```tsx
// emails/NewBooking.tsx
export default function NewBookingEmail(props) {
  return (
    <Html lang="de">
      <Head />
      <Body style={{ fontFamily: 'Arial, sans-serif' }}>
        <Container>
          <Text>Hallo {props.approverName},</Text>
          <Text>Es gibt eine neue Buchungsanfrage:</Text>
          <Section>
            <Text><strong>Von:</strong> {props.requesterName}</Text>
            <Text><strong>Zeitraum:</strong> {props.dateRange}</Text>
            <Text><strong>Teilnehmer:</strong> {props.partySize} Personen</Text>
          </Section>
          <Button href={props.approveLink}>Zustimmen</Button>
          <Button href={props.denyLink}>Ablehnen (mit Grund)</Button>
        </Container>
      </Body>
    </Html>
  );
}
```

**Option 2: Jinja2 Templates (Simpler)**
```html
<!-- templates/new_booking.html -->
<html>
<body style="font-family: Arial, sans-serif;">
  <p>Hallo {{ approver_name }},</p>
  <p>Es gibt eine neue Buchungsanfrage:</p>
  <ul>
    <li><strong>Von:</strong> {{ requester_name }}</li>
    <li><strong>Zeitraum:</strong> {{ date_range }}</li>
    <li><strong>Teilnehmer:</strong> {{ party_size }} Personen</li>
  </ul>
  <a href="{{ approve_link }}" style="...">Zustimmen</a>
  <a href="{{ deny_link }}" style="...">Ablehnen (mit Grund)</a>
</body>
</html>
```

**Recommendation:** Start with Jinja2 (simpler), upgrade to React Email if templates become complex.

### Weekly Digest (BR-009)

```python
# app/tasks/weekly_digest.py
from app.services.email_service import EmailService
from app.repositories.booking_repository import BookingRepository

async def send_weekly_digest():
    """Run every Sunday at 09:00 Europe/Berlin."""
    for approver in APPROVERS:
        outstanding = await booking_repo.get_outstanding_for_approver(
            approver_email=approver.email,
            min_age_days=5,
            future_only=True
        )

        if not outstanding:
            # Suppress if zero items (BR-009)
            continue

        await email_service.send(
            to=approver.email,
            subject="Ausstehende Anfragen – Wochenübersicht",
            html=render_template("weekly_digest", {
                "approver_name": approver.name,
                "outstanding_count": len(outstanding),
                "bookings": outstanding
            })
        )
```

**Scheduling:** Use APScheduler or Celery Beat (decided in implementation phase).

---

## Validation

### Test Email Send

```python
# Test in Python REPL
import resend
resend.api_key = "re_..."

email = resend.Emails.send({
    "from": "no-reply@betzenstein.app",
    "to": "test@example.com",
    "subject": "Test Email",
    "html": "<p>Hallo, dies ist ein Test.</p>"
})

print(email)  # Should print: {'id': 'xxx'}
```

### Check Logs

Visit Resend dashboard → Logs → See sent email.

### Check Deliverability

Send test email to Gmail, check:
- ✅ Arrives in inbox (not spam)
- ✅ DKIM/SPF pass (view email headers)
- ✅ HTML renders correctly
- ✅ Plain-text fallback works

---

## References

- [Resend Documentation](https://resend.com/docs)
- [Resend Python SDK](https://github.com/resendlabs/resend-python)
- [React Email](https://react.email/)
- [Tenacity (Retry Library)](https://tenacity.readthedocs.io/)
- Notification Spec: `docs/specification/notifications.md`
- Business Rules: `docs/foundation/business-rules.md` (BR-009, BR-022)

---

## Related ADRs

- [ADR-001: API Framework](adr-001-backend-framework.md) - FastAPI integration
- [ADR-007: Deployment Strategy](adr-007-deployment.md) - Environment variables

---

## Changelog

- **2025-01-17:** Initial decision - Resend chosen for email service
