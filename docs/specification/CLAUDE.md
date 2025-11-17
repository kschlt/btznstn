# Specification - CLAUDE Guide

## What's in This Section

Detailed technical specs for implementation:
- **ui-screens.md** - All screens and interactions
- **notifications.md** - All German email templates
- **data-model.md** - Complete database schema
- **error-handling.md** - All German error messages
- **configuration.md** - System parameters

## When to Read This

During implementation:
- Building UI? → `ui-screens.md`
- Sending emails? → `notifications.md`
- Creating database? → `data-model.md`
- Showing errors? → `error-handling.md`
- Adding config? → `configuration.md`

## German Copy - Critical

**ALL German text comes from this section.**

**Sources:**
- Emails: `notifications.md`
- Errors: `error-handling.md`
- UI labels: `ui-screens.md`

**Rules:**
- Use **exact copy** from specs (no variations, no improvising)
- Informal "du" (not "Sie")
- Date format: `DD.–DD.MM.YYYY` (e.g., "01.–05.08.2025")
- Party size: "n Personen" (even for 1 person)

**Example:**
```typescript
// ✓ Correct - exact copy from spec
<ErrorMessage>Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung.</ErrorMessage>

// ✗ Wrong - paraphrased
<ErrorMessage>Diese Daten überschneiden sich.</ErrorMessage>
```

## Data Model Gotchas

**Core entities:**
- **BOOKING** - Main table (status, dates, requester)
- **APPROVER_PARTY** - 3 fixed rows (seed data)
- **APPROVAL** - 3 per booking (junction table)
- **TIMELINE_EVENT** - Audit log

**Key points:**
- `RequesterEmail` stored but **never exposed in API responses** (privacy - BR-013)
- Use `RequesterFirstName` for display
- `Status` enum: Pending, Confirmed, Denied, Canceled
- `TotalDays` is calculated, not stored
- Foreign keys enforce relationships

**See `data-model.md` for complete schema with constraints.**

## Email Templates

**All emails in `notifications.md` include:**
- Trigger (when sent)
- Recipients (who gets it)
- German subject line
- German body with action links
- Token placeholders

**Critical:**
- Links include secure tokens
- Tokens never expire (BR-010)
- Retry 3 times with exponential backoff (BR-022)

## Error Messages

**From `error-handling.md`:**

**Validation errors:**
- Date in past
- End before start
- Invalid email
- Missing required fields

**Business logic errors:**
- Booking conflicts (BR-002)
- Already actioned (BR-024)
- Permission denied

**System errors:**
- Email send failure
- Database error

**All have German text** - use exact copy from spec.

## UI Screens

**Main screens:**
- Public Calendar (Month/Year views)
- Create Booking Form
- Edit Booking Form
- Booking Details
- Approver Overview
- Approver History

**Mobile-first:**
- Design for 375px width (iPhone 8)
- 44×44pt tap targets minimum
- No hover dependencies

**See `ui-screens.md` for complete layouts and interactions.**

---

**Next:** See [`/docs/architecture/`](../architecture/) for tech stack decisions and [`/docs/implementation/`](../implementation/) to start building.
