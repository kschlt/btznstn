# Constraints - CLAUDE Guide

## What's in This Section

Boundaries and limits:
- **non-functional.md** - Performance, security, privacy, reliability
- **technical-constraints.md** - Platform, browsers, mobile, language

## When to Read This

Check constraints when:
- Choosing implementation approach
- Making performance decisions
- Adding dependencies
- Designing for mobile

## Key Constraints

### Mobile-First (Critical)

**Must support:** iPhone 8 class (375×667px, iOS 12+)

**Requirements:**
- 375px minimum width
- 44×44pt tap targets
- No hover dependencies
- Touch-friendly interactions
- Works on slow networks

**Test on:** iPhone 8 viewport in Playwright

### Performance Targets

- API response: < 500ms (p95)
- Calendar load: < 1s
- Email delivery: < 5s

**Not strict SLAs** - best effort for small group.

### Browser Support

**Required:**
- Safari (iOS + macOS)
- Chrome (desktop + Android)
- Firefox (desktop)

**Not required:**
- IE11
- Opera Mini

### Language & Locale

**German only:**
- No English fallback
- German error messages
- German email templates
- Informal "du" tone

**Locale:** de-DE for date/number formatting

### Privacy

**Critical constraints:**
- Emails **never displayed** in UI (PII)
- Denied bookings **hidden from public**
- First names only
- No analytics/tracking without consent

### Security

**Requirements:**
- HTTPS only
- Token-based auth (HMAC-SHA256)
- Rate limiting (10 bookings/day/email)
- Input validation (Pydantic + Zod)
- SQL injection prevention (ORM)
- XSS prevention (React escaping)

**No formal penetration testing** for small trusted group.

### Deployment

**Platforms:**
- Backend: Fly.io (Frankfurt region)
- Frontend: Vercel (global CDN)
- Database: Fly.io Postgres (co-located with backend)
- Email: Resend

**No multi-region** - single region (Frankfurt) is sufficient.

---

**Next:** See [`/docs/architecture/`](../architecture/) for how these constraints influenced tech stack decisions.
