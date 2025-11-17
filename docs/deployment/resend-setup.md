# Resend Email Service Setup

## Overview

This guide walks you through setting up Resend for transactional email delivery in the Betzenstein Booking application.

**When needed:** Before implementing Phase 4 (Email Integration)

**Prerequisites:** Valid email address for account creation

---

## Manual Setup Steps

### 1. Create Resend Account

1. Go to [https://resend.com/signup](https://resend.com/signup)
2. Sign up with your email address
3. Verify your email address
4. Complete account setup

### 2. Get API Key

1. Log in to [https://resend.com/](https://resend.com/)
2. Navigate to **API Keys** in the left sidebar
3. Click **Create API Key**
4. Name it: `Betzenstein Production` (or `Betzenstein Dev` for development)
5. Set permissions: **Sending access**
6. Click **Add**
7. **IMPORTANT:** Copy the API key immediately (it won't be shown again)
8. Store it securely (password manager or secrets vault)

**API Key format:** `re_xxxxxxxxxxxxxxxxxxxxxxxxxx`

### 3. Configure Environment Variable

Add the API key to your backend environment:

**Development (`.env`):**
```bash
RESEND_API_KEY=re_your_api_key_here
```

**Production (Fly.io):**
```bash
flyctl secrets set RESEND_API_KEY=re_your_api_key_here
```

### 4. Verify Domain (Optional for Production)

**For production use**, verify your sending domain:

1. In Resend dashboard, go to **Domains**
2. Click **Add Domain**
3. Enter your domain (e.g., `betzenstein.app`)
4. Add the provided DNS records to your domain registrar
5. Wait for verification (usually 5-30 minutes)

**For development**, you can send from `onboarding@resend.dev` (100 emails/day limit)

---

## Integration Checklist

Before implementing Phase 4, ensure:

- [ ] Resend account created and verified
- [ ] API key generated and stored securely
- [ ] Environment variable configured (`RESEND_API_KEY`)
- [ ] (Production) Domain verified for sending
- [ ] Free tier limits understood (100 emails/day, or 3000/month on paid)

---

## Phase 4 Implementation Notes

**Mock Service (Phase 0-3):**
- Currently using a file-based mock email service
- Emails logged to `backend/logs/emails/` (console in development)
- No actual emails sent

**Real Service (Phase 4+):**
- Replace mock service with Resend SDK
- All German email templates in `docs/specification/notifications.md`
- Retry logic per BR-022 (3 attempts with exponential backoff)
- **TODO:** Remove all mock email code when switching to Resend

---

## Resend SDK Usage

**Installation:**
```bash
# Already in requirements.txt, but for reference:
pip install resend
```

**Basic Example:**
```python
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

# Send email
resend.Emails.send({
    "from": "buchung@betzenstein.app",
    "to": "approver@example.com",
    "subject": "Neue Anfrage wartet auf Zustimmung",
    "html": email_html_content,
})
```

**Full implementation** will be done in Phase 4 according to the email specifications.

---

## Troubleshooting

**Issue:** API key not working
- **Solution:** Verify key is correctly copied (no extra spaces)
- **Solution:** Check that key hasn't been revoked in Resend dashboard

**Issue:** Emails not sending
- **Solution:** Check free tier limits (100/day)
- **Solution:** Verify `from` address matches verified domain

**Issue:** Emails going to spam
- **Solution:** Verify domain (adds SPF/DKIM records)
- **Solution:** Use verified domain instead of `onboarding@resend.dev`

---

## Cost Considerations

**Free Tier:**
- 100 emails/day
- 3,000 emails/month
- All features included

**Paid Tier (if needed):**
- $20/month for 10,000 emails
- $0.002 per email after that

**Estimated usage for Betzenstein:**
- ~5-10 bookings/week = ~20-40 emails/week = 80-160 emails/month
- Well within free tier limits

---

## Related Documentation

- [Notifications Specification](../specification/notifications.md) - All German email templates
- [BR-022: Email Retries](../foundation/business-rules.md#br-022-email-retries)
- [Phase 4: Email Integration](../implementation/phase-4-email-integration.md)

---

## Summary

✅ **Account created** → Sign up at resend.com
✅ **API key obtained** → Generate in dashboard
✅ **Environment configured** → Add `RESEND_API_KEY`
✅ **Ready for Phase 4** → Implement Resend SDK integration

**Next:** Proceed with Phase 4 implementation when ready.
