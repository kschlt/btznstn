# Phase 6: Web Booking - Developer Quick Reference

**Use this guide as your implementation checklist and quick lookup.**

---

## Before You Start: Pre-Implementation Checklist

**Must complete before writing any code:**

- [ ] Read `docs/foundation/business-rules.md` (all 29 rules, but focus on BR-001–027)
- [ ] Read `docs/implementation/phase-6-frontend-booking.md` (user stories)
- [ ] Read `docs/specification/ui-screens.md` (form layouts, interactions)
- [ ] Read `docs/specification/error-handling.md` (all German error messages)
- [ ] Read `docs/specification/data-model.md` (field constraints)
- [ ] Understand date picker component requirements (Shadcn Calendar or similar)
- [ ] Understand React Hook Form + Zod validation pattern
- [ ] Plan all 40–42 Playwright tests BEFORE coding
- [ ] Review this quick reference document

---

## The 13 Critical Business Rules for Phase 6

### Date & Validation Rules

| BR | Rule | Applies To | Implementation | Test Examples |
|:---|:-----|:----------|:---|:---|
| **BR-001** | Whole-day bookings, **inclusive** end date | US-6.1, 6.2, 6.3 | `TotalDays = EndDate - StartDate + 1` (not ±0) | Jan 1–5 = 5 days |
| **BR-002** | No overlaps with **Pending/Confirmed** | US-6.1, 6.3 | Validate on form submit; show error with first name + status | Overlap → error dialog |
| **BR-005** | **Date extend resets approvals; shorten keeps them** | US-6.3 | Detect change type; if extend → reset; if non-date → keep | Extend start earlier → approvals reset |
| **BR-011** | **German-only UI** | All | All labels, errors, buttons in German; no English | Error: "Bitte gib..." not "Please enter..." |
| **BR-014** | **Past items read-only** | US-6.3 | Cannot edit if EndDate < today; show banner | EndDate < today → no edit button |
| **BR-016** | Party size as "n Personen" | US-6.1, 6.3 | Display format (even 1 = "1 Personen") | UI shows "5 Personen" not "5 people" |
| **BR-017** | **Party size 1–10 (configurable)** | US-6.1, 6.3 | Validate input; error: "zwischen 1 und {{MAX}}" | 0 rejected; 11 rejected |
| **BR-018** | **Reopen guard: no conflicts allowed** | US-6.3 | When reopening denied booking, check dates against Pending/Confirmed | Reopen with conflicting dates → error |
| **BR-019** | **First name: letters, diacritics, space, hyphen, apostrophe; max 40; trim** | US-6.1, 6.3 | Zod regex validation; trim on submit | "Müller" OK; "Anna123" NOT OK |
| **BR-020** | **Block URLs in Description** | US-6.1, 6.3 | Reject: http://, https://, www, mailto: | "Check http://example.com" → error |
| **BR-025** | **First-name edit keeps approvals** | US-6.3 | Detect if only name changed; don't reset | Change first name alone → approvals stay |
| **BR-026** | **Future horizon: start ≤ today + 18 months** | US-6.1, 6.2, 6.3 | Disable dates in picker; validate on form; error: "maximal {{MONTHS}}" | +18 months OK; +19 months NOT OK |
| **BR-027** | **Long stay warning: TotalDays > 7** | US-6.1, 6.3 | Show confirmation dialog; require user confirmation | 8 days → dialog; 7 days → no dialog |

---

## Form Field Specifications

### Create & Edit Forms

```
Required Fields:
  ✓ Requester First Name
    - Validation: BR-019 (regex: letters, diacritics, space, -, ')
    - Max length: 40 characters (enforced in Zod + HTML5)
    - Error: "Bitte gib einen gültigen Vornamen an (Buchstaben, Leerzeichen, Bindestrich, Apostroph; max. 40 Zeichen)."
    - Trim: Yes (remove leading/trailing whitespace)

  ✓ Email
    - Validation: RFC 5322 minimal (can use Zod built-in)
    - Max length: 254 characters
    - In edit form: IMMUTABLE (disabled/hidden)
    - Error: "Bitte gib eine gültige E-Mail-Adresse an."

  ✓ Start Date
    - Validation: Date type, ≤ today + 18 months (BR-026)
    - Cannot be in past (BR-014)
    - Must be ≤ End Date (BR-001)
    - Date picker: disable <today and >+18mo
    - Error: "Anfragen dürfen nur maximal 18 Monate im Voraus gestellt werden."

  ✓ End Date
    - Validation: Date type, ≥ Start Date (BR-001)
    - Error if < Start: "Ende darf nicht vor dem Start liegen."

  ✓ Party Size
    - Validation: Integer, 1 ≤ n ≤ 10 (configurable, BR-017)
    - Not decimal
    - Error: "Teilnehmerzahl muss zwischen 1 und {{MAX}} liegen."
    - Display format: "n Personen" (BR-016)

  ✓ Affiliation
    - Validation: One of Ingeborg | Cornelia | Angelika
    - Visual: Color-coded (Ingeborg: #C1DBE3, Cornelia: #C7DFC5, Angelika: #DFAEB4)

Optional Fields:
  ○ Description
    - Max length: 500 characters (BR-020)
    - Block URLs: http://, https://, www, mailto: (BR-020)
    - Allow: newlines, emoji
    - Error (links): "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden."
    - Error (too long): "Text ist zu lang (max. 500 Zeichen)."
```

---

## Validation Error Messages (Exact German Copy)

**Copy & paste these exactly from specifications—never paraphrase:**

```
Required Field Missing
└─ "Dieses Feld wird benötigt."
   Source: docs/specification/error-handling.md line 460

Invalid First Name
└─ "Bitte gib einen gültigen Vornamen an (Buchstaben, Leerzeichen, Bindestrich, Apostroph; max. 40 Zeichen)."
   Source: docs/specification/error-handling.md line 110–111

Invalid Email
└─ "Bitte gib eine gültige E-Mail-Adresse an."
   Source: docs/specification/error-handling.md line 79

End Before Start
└─ "Ende darf nicht vor dem Start liegen."
   Source: docs/specification/error-handling.md line 63

Party Size Out of Range
└─ "Teilnehmerzahl muss zwischen 1 und {{MAX}} liegen."
   Example: "Teilnehmerzahl muss zwischen 1 und 10 liegen."
   Source: docs/specification/error-handling.md line 124

Party Size Not Integer
└─ "Bitte gib eine ganze Zahl ein."
   Source: docs/specification/error-handling.md line 146

Text Too Long (Description/Comment)
└─ "Text ist zu lang (max. 500 Zeichen)."
   Source: docs/specification/error-handling.md line 160

Links Not Allowed
└─ "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden."
   Source: docs/specification/error-handling.md line 175

Future Horizon Exceeded
└─ "Anfragen dürfen nur maximal {{MONTHS}} Monate im Voraus gestellt werden."
   Example: "Anfragen dürfen nur maximal 18 Monate im Voraus gestellt werden."
   Source: docs/specification/error-handling.md line 42

Date Conflict
└─ "Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung ({{Vorname}} – {{Status}})."
   Example: "Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung (Anna – Ausstehend)."
   Source: docs/specification/error-handling.md line 17

Past-Dated Item
└─ "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."
   Source: docs/specification/error-handling.md line 193
```

---

## Success Messages (Exact German Copy)

```
Booking Created
└─ "Anfrage gesendet. Du erhältst E-Mails, sobald entschieden wurde."
   Source: docs/specification/error-handling.md line 211

Booking Updated (implicit—no specific copy, show success toast)
└─ Suggest: "Buchung aktualisiert."
   Source: Custom (not in spec)

Booking Reopened (implicit—no specific copy)
└─ Show timeline update or inline message
```

---

## Dialog Copy (Exact German)

### Long Stay Confirmation (BR-027)

```
Title:    "Langer Aufenthalt"
Body:     "Diese Anfrage umfasst {{TotalDays}} Tage. Möchtest du fortfahren?"
Buttons:  "Abbrechen" | "Bestätigen"
Source:   docs/specification/error-handling.md line 529–531

Trigger:  TotalDays > LONG_STAY_WARN_DAYS (default 7)
Example:  8 days → dialog; 7 days → no dialog
```

---

## Validation Zod Schema Template

```typescript
import { z } from 'zod';

const BookingFormSchema = z.object({
  requesterFirstName: z
    .string()
    .trim()
    .min(1, 'Dieses Feld wird benötigt.')
    .max(40, 'Bitte gib einen gültigen Vornamen an...')
    .regex(
      /^[a-zA-ZäöüßÄÖÜ\s\-']+$/,
      'Bitte gib einen gültigen Vornamen an...'
    ),

  email: z
    .string()
    .min(1, 'Dieses Feld wird benötigt.')
    .email('Bitte gib eine gültige E-Mail-Adresse an.')
    .max(254),

  startDate: z
    .date()
    .min(new Date(), 'Startdatum liegt in der Vergangenheit.')
    .refine(
      (date) => date <= addMonths(today, 18),
      'Anfragen dürfen nur maximal 18 Monate im Voraus gestellt werden.'
    ),

  endDate: z
    .date()
    .refine(
      function(date) {
        return date >= this.parent.startDate;
      },
      'Ende darf nicht vor dem Start liegen.'
    ),

  partySize: z
    .number()
    .int('Bitte gib eine ganze Zahl ein.')
    .min(1, 'Teilnehmerzahl muss zwischen 1 und 10 liegen.')
    .max(10, 'Teilnehmerzahl muss zwischen 1 und 10 liegen.'),

  affiliation: z
    .enum(['Ingeborg', 'Cornelia', 'Angelika']),

  description: z
    .string()
    .max(500, 'Text ist zu lang (max. 500 Zeichen).')
    .refine(
      (text) => !/(http:\/\/|https:\/\/|www|mailto:)/.test(text),
      'Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden.'
    )
    .optional(),
});

type BookingForm = z.infer<typeof BookingFormSchema>;
```

---

## Date Logic Implementation

### TotalDays Calculation

```typescript
// ✓ CORRECT (BR-001: inclusive end date)
const totalDays = Math.floor(
  (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)
) + 1;

// Examples:
// Jan 1–1: (0 ms) / ... + 1 = 1 day ✓
// Jan 1–2: (86400000 ms) / ... + 1 = 2 days ✓
// Jan 1–5: (345600000 ms) / ... + 1 = 5 days ✓

// ✗ WRONG (off-by-one error)
const totalDays = (endDate - startDate) / (1000 * 60 * 60 * 24); // = 4 for Jan 1–5
```

### Inclusive Date Range Check

```typescript
// ✓ CORRECT (BR-001, BR-002: overlap detection)
function hasOverlap(
  newStart: Date,
  newEnd: Date,
  existingStart: Date,
  existingEnd: Date
): boolean {
  // Overlap if: newStart <= existingEnd AND newEnd >= existingStart
  return newStart <= existingEnd && newEnd >= existingStart;
}

// Examples:
// New: Jan 1–5, Existing: Jan 1–5 → true (overlap) ✓
// New: Jan 1–5, Existing: Jan 6–10 → false (no overlap) ✓
// New: Jan 1–10, Existing: Jan 3–7 → true (overlap) ✓
// New: Jan 5–6, Existing: Jan 1–4 → false (adjacent OK) ✓
```

### Future Horizon Validation

```typescript
// ✓ CORRECT (BR-026: today + 18 months)
function isWithinFutureHorizon(date: Date, months: number = 18): boolean {
  const horizon = addMonths(today, months);
  return date <= horizon;
}

// Must disable in date picker AND validate on submit
```

### Long Stay Detection

```typescript
// ✓ CORRECT (BR-027: threshold = 7 days)
function needsLongStayConfirmation(totalDays: number, threshold: number = 7): boolean {
  return totalDays > threshold; // NOT >= !
}

// Examples:
// 7 days → false (no dialog) ✓
// 8 days → true (show dialog) ✓
```

### Detect Date Extend vs. Shorten (BR-005)

```typescript
// ✓ CORRECT (BR-005: approval reset logic)
function detectDateChangeType(
  oldStart: Date,
  oldEnd: Date,
  newStart: Date,
  newEnd: Date
): 'SHORTENED' | 'EXTENDED' | 'SAME' {
  const startMoved = newStart.getTime() !== oldStart.getTime();
  const endMoved = newEnd.getTime() !== oldEnd.getTime();

  if (!startMoved && !endMoved) return 'SAME';

  const startExtended = newStart < oldStart; // earlier = extended
  const endExtended = newEnd > oldEnd; // later = extended

  if (startExtended || endExtended) {
    return 'EXTENDED'; // Reset approvals per BR-005
  }

  return 'SHORTENED'; // Keep approvals per BR-005
}

// Examples:
// Old: Jan 1–10, New: Jan 3–8 → SHORTENED (keep approvals) ✓
// Old: Jan 1–10, New: Dec 31–10 → EXTENDED (reset approvals) ✓
// Old: Jan 1–10, New: Jan 1–20 → EXTENDED (reset approvals) ✓
// Old: Jan 1–10, New: Jan 1–10 + party size change → SAME (keep approvals) ✓
```

---

## Form Component Architecture

### Recommended Component Structure

```
<BookingFormDialog />
  ├─ <BookingForm />
  │   ├─ <FormField> (First Name)
  │   ├─ <FormField> (Email)
  │   ├─ <FormField> (Start Date)
  │   │   └─ <DatePicker /> (uses Shadcn Calendar)
  │   ├─ <FormField> (End Date)
  │   │   └─ <DatePicker />
  │   ├─ <FormField> (Party Size)
  │   ├─ <FormField> (Affiliation Radio)
  │   ├─ <FormField> (Description Textarea)
  │   └─ <SubmitButton />
  ├─ <LongStayDialog /> (BR-027)
  ├─ <ConflictDialog /> (BR-002)
  └─ <SuccessToast />

<DatePicker />
  ├─ Calendar display (month view, week starts Monday)
  ├─ Disabled states (past dates, future >18mo, blocked dates)
  ├─ Visual indicators (blocked dates, selected range)
  ├─ Navigation (arrows, "Heute" button)
  └─ Format output as "DD.MM.YYYY"
```

### Form State Management (React Hook Form)

```typescript
const form = useForm<BookingForm>({
  resolver: zodResolver(BookingFormSchema),
  defaultValues: {
    requesterFirstName: '',
    email: '',
    startDate: new Date(),
    endDate: new Date(),
    partySize: 1,
    affiliation: 'Ingeborg',
    description: '',
  },
  mode: 'onBlur', // Validate on blur, not on every change
});

// On submit:
async function onSubmit(data: BookingForm) {
  // 1. Validate all fields (Zod already done)
  // 2. Calculate TotalDays
  const totalDays = calculateTotalDays(data.startDate, data.endDate);

  // 3. Check long stay (BR-027)
  if (totalDays > 7) {
    setShowLongStayDialog(true);
    return; // Wait for confirmation
  }

  // 4. Submit to API
  try {
    const response = await submitBooking(data);
    // 5. Show success message
    setSuccessMessage('Anfrage gesendet. Du erhältst E-Mails, sobald entschieden wurde.');
    // 6. Redirect to booking details
    router.push(`/booking/${response.token}`);
  } catch (error) {
    // 7. Handle API errors (conflicts, etc.)
    if (error.code === 'CONFLICT') {
      setShowConflictDialog(true);
      setConflictDetails(error.details);
    } else {
      setErrorMessage(error.message);
    }
  }
}
```

---

## Mobile-First Checklist

**Test all of these on 375×667px viewport (iPhone 8):**

- [ ] Form fits without horizontal scroll
- [ ] Input fields are 44×44pt tap targets minimum
- [ ] Buttons are 44×44pt tap targets minimum
- [ ] Date picker calendar cells are large enough to tap
- [ ] No hover states (all interactions touch-friendly)
- [ ] Dialog boxes are readable at 375px
- [ ] Error messages display inline and visible
- [ ] Keyboard appears and doesn't obstruct form
- [ ] Touch targets have adequate spacing (no accidental taps)
- [ ] Textarea is easily scrollable on mobile

---

## Playwright Test Template

```typescript
import { test, expect } from '@playwright/test';

test.describe('Booking Form (US-6.1)', () => {
  test('should submit valid booking and show success message', async ({ page }) => {
    // 1. Navigate to calendar
    await page.goto('/');

    // 2. Open form
    await page.click('button:has-text("Neue Anfrage")');
    await expect(page.locator('[role="dialog"]')).toBeVisible();

    // 3. Fill form
    await page.fill('input[name="requesterFirstName"]', 'Anna');
    await page.fill('input[name="email"]', 'anna@example.com');

    // 4. Select dates via picker
    await page.click('input[name="startDate"]');
    await page.click('button:has-text("1")'); // Click day 1
    await page.click('input[name="endDate"]');
    await page.click('button:has-text("5")'); // Click day 5

    // 5. Fill remaining fields
    await page.fill('input[name="partySize"]', '4');
    await page.click('input[value="Ingeborg"]');
    await page.fill('textarea[name="description"]', 'Sommerferien');

    // 6. Submit
    await page.click('button:has-text("Anfrage gesendet")');

    // 7. Verify success
    await expect(page.locator('text=Anfrage gesendet. Du erhältst E-Mails')).toBeVisible();

    // 8. Verify redirect
    await expect(page).toHaveURL(/\/booking\//);
  });

  test('should show error for overlapping booking dates', async ({ page }) => {
    // Setup: Existing Pending booking Aug 1–5

    await page.goto('/');
    await page.click('button:has-text("Neue Anfrage")');

    // Fill form with overlapping dates
    await page.fill('input[name="requesterFirstName"]', 'Bob');
    await page.fill('input[name="email"]', 'bob@example.com');
    await page.click('input[name="startDate"]'); // Aug 1 (overlaps)
    await page.click('button:has-text("1")');
    await page.click('input[name="endDate"]'); // Aug 5 (overlaps)
    await page.click('button:has-text("5")');

    // Submit
    await page.click('button:has-text("Anfrage senden")');

    // Verify conflict error
    await expect(page.locator('text=überschneidet sich mit')).toBeVisible();
    await expect(page.locator('text=Anna')).toBeVisible(); // Conflicting requester
    await expect(page.locator('text=Ausstehend')).toBeVisible(); // Status
  });
});
```

---

## Testing Checklist

**Before submitting Phase 6 PR:**

- [ ] All 40–42 Playwright tests passing
- [ ] All validation errors match German copy exactly (no typos)
- [ ] Date calculations correct (inclusive end date, TotalDays)
- [ ] Conflict detection works (Pending + Confirmed)
- [ ] Long stay dialog appears at >7 days
- [ ] Email immutable in edit form
- [ ] Past bookings read-only
- [ ] Date extend resets approvals (edit flow)
- [ ] Approval unchanged for non-date edits
- [ ] Mobile: 375px viewport works smoothly
- [ ] Mobile: tap targets ≥44×44pt
- [ ] No horizontal scroll on mobile
- [ ] Keyboard navigation works on desktop
- [ ] Affiliation colors display correctly
- [ ] Form pre-fills correctly in edit mode
- [ ] Reopen dialog guides user to adjust conflicting dates

---

## Common Mistakes to Avoid

| Mistake | Consequence | Prevention |
|:--------|:-----------|:-----------|
| Off-by-one in `TotalDays` (use `end - start` not `+1`) | Jan 1–5 shows 4 days not 5 | Always use formula: `(end - start) + 1` |
| English text in form | Violates BR-011 | Copy all text from spec exactly |
| Display "1 Person" instead of "1 Personen" | Violates BR-016 | Always use "n Personen" even for 1 |
| Allow selection of past dates in picker | Violates BR-014 | Disable dates < today in date picker |
| Forget to reset approvals on date extend | Violates BR-005 | Detect change type and follow approval rules |
| Show conflict error, no user recovery path | Poor UX | Allow user to adjust dates and resubmit |
| Validate only client-side, not server-side | Security issue | Server must validate all inputs |
| Emit long stay dialog at ≥7 days not >7 | Off-by-one | Dialog only if TotalDays **>** 7 |
| Email editable in edit form | Data integrity issue | Disable/hide email in edit form (immutable) |
| No conflict check when reopening denied booking | Violates BR-018 | Check dates against Pending/Confirmed on reopen |

---

## Key Files to Review

**Documentation:**
- `docs/foundation/business-rules.md` - All 29 rules (focus on 13 above)
- `docs/specification/error-handling.md` - All German error messages
- `docs/specification/ui-screens.md` - Form layouts, date picker, interactions
- `docs/specification/data-model.md` - Field constraints and validation rules

**Implementation References (from previous phases):**
- `app/api/bookings.py` - Booking creation endpoint (Phase 2)
- `app/models/booking.py` - Booking model with constraints (Phase 1)
- Frontend calendar component (Phase 5) - Use DatePicker from same codebase

**Tests:**
- `tests/e2e/booking-form.spec.ts` - Playwright tests you'll write
- `tests/unit/validation.test.ts` - Zod schema unit tests (optional)

---

## Quick Lookup: Which BR Does This Belong To?

**"User sees form field..."** → BR-011 (German UI)
**"Date can't be in past..."** → BR-014 + BR-026
**"End date before start..."** → BR-001
**"Can't book same dates..."** → BR-002
**"Edit date but keep approvals..."** → BR-005 (shorten) vs. reset (extend)
**"Can't select >18 months..."** → BR-026
**"Warn if >7 days..."** → BR-027
**"Block http:// in text..."** → BR-020
**"First name has special chars..."** → BR-019
**"Party size 1–10..."** → BR-017
**"Show '5 Personen'..."** → BR-016
**"First name edit doesn't reset approvals..."** → BR-025
**"Can't reopen if new conflicts..."** → BR-018

---

**Good luck! Reference this document constantly during implementation. When in doubt about a requirement, trace it back to the original spec.**
