# Error & Empty States

## Overview

Complete specification for all error messages and empty states in German (informal "du" tone).

---

## Validation Errors

### Conflict Errors

**Scenario:** Date range overlaps with existing Pending or Confirmed booking

**German Copy:**
```
Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung ({{Vorname}} – {{Status}}).
```

**Examples:**
```
Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung (Anna – Ausstehend).
```

```
Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung (Max – Bestätigt).
```

**Display:**
- Modal/dialog
- Clear heading
- List all conflicting bookings (first name + status)
- Action: User must adjust dates

---

### Future Horizon Exceeded

**Scenario:** Start date is beyond FUTURE_HORIZON_MONTHS (default 18)

**German Copy:**
```
Anfragen dürfen nur maximal {{MONTHS}} Monate im Voraus gestellt werden.
```

**Example (18 months):**
```
Anfragen dürfen nur maximal 18 Monate im Voraus gestellt werden.
```

**Display:**
- Inline error under date field
- Or modal if detected at submit

---

### End Before Start

**Scenario:** End date is before start date

**German Copy:**
```
Ende darf nicht vor dem Start liegen.
```

**Display:**
- Inline error under end date field
- Highlight both date fields
- Prevent submission

---

### Invalid Email

**Scenario:** Email doesn't match validation rules (see data-model.md §9)

**German Copy:**
```
Bitte gib eine gültige E-Mail-Adresse an.
```

**Display:**
- Inline error under email field
- Red border on input
- Show on blur or submit

---

### Comment Required

**Scenario:** User tries to Deny or Cancel (Confirmed) without providing comment

**German Copy:**
```
Bitte gib einen kurzen Grund an.
```

**Display:**
- Inline error under comment field
- Prevent submission until comment provided
- Highlight field

---

### Invalid First Name

**Scenario:** First name contains invalid characters or exceeds length

**German Copy:**
```
Bitte gib einen gültigen Vornamen an (Buchstaben, Leerzeichen, Bindestrich, Apostroph; max. 40 Zeichen).
```

**Display:**
- Inline error under first name field
- Show on blur or submit

---

### Party Size Out of Range

**Scenario:** Party size < 1 or > MAX_PARTY_SIZE (default 10)

**German Copy:**
```
Teilnehmerzahl muss zwischen 1 und {{MAX}} liegen.
```

**Example (MAX=10):**
```
Teilnehmerzahl muss zwischen 1 und 10 liegen.
```

**Display:**
- Inline error under party size field
- Reset to valid value on blur

---

### Party Size Not Integer

**Scenario:** User enters non-integer value for party size

**German Copy:**
```
Bitte gib eine ganze Zahl ein.
```

**Display:**
- Inline error under party size field
- Clear invalid input

---

### Text Too Long

**Scenario:** Description or comment exceeds 500 characters

**German Copy:**
```
Text ist zu lang (max. 500 Zeichen).
```

**Display:**
- Inline error under textarea
- Character counter showing "543/500" (example)
- Red when exceeded

---

### Links Not Allowed

**Scenario:** Description or comment contains http://, https://, www, or mailto:

**German Copy:**
```
Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden.
```

**Display:**
- Inline error under field
- Highlight detected link
- Prevent submission

---

### Past-Dated Item

**Scenario:** User tries to edit, cancel, approve, deny, or reopen past-dated booking

**German Copy:**
```
Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden.
```

**Display:**
- Banner at top of details view
- No action buttons shown
- Read-only mode

---

## Success Messages

### Booking Submitted

**Scenario:** New booking successfully created

**German Copy:**
```
Anfrage gesendet. Du erhältst E-Mails, sobald entschieden wurde.
```

**Display:**
- Toast notification or modal
- Auto-dismiss after 3–5 seconds
- Redirect to booking details or calendar

---

### Cancellation Confirmed (Pending or Confirmed)

**Scenario:** Requester successfully canceled Pending or Confirmed booking

**German Copy:**
```
Anfrage storniert.

Benachrichtigt: {{ListeNamen}}
```

**Example:**
```
Anfrage storniert.

Benachrichtigt: Ingeborg, Cornelia und Angelika.
```

**Display:**
- Modal or result page
- List notified parties
- Return to calendar or overview

---

### Cancellation Confirmed (Denied)

**Scenario:** Requester successfully canceled Denied booking

**German Copy:**
```
Anfrage storniert.
```

**Display:**
- Toast or modal
- No list of notified (approvers already informed by Deny)
- Return to calendar or overview

---

## Result Page Messages (After Action Links)

See `notifications.md` for complete result page copy. Summary:

**Success (Approve not final):**
```
Danke – du hast zugestimmt.
Status: Ausstehend: {{Restparteien}}
```

**Success (Approve final):**
```
Danke – du hast zugestimmt.
Alles bestätigt!
```

**Success (Deny):**
```
Erledigt – du hast abgelehnt.
Die Anfrage ist jetzt abgelehnt und nicht mehr öffentlich sichtbar.
```

**Already Done (Denied first):**
```
Schon erledigt.
{{Partei}} hat bereits abgelehnt – die Anfrage ist jetzt abgelehnt (nicht öffentlich).
```

**Already Done (Generic):**
```
Schon erledigt.
Aktueller Stand: {{StatusDescription}}
```

Examples:
- "Die Buchung ist bereits bestätigt."
- "Diese Anfrage ist bereits storniert."

---

## Empty States

### No Bookings in Calendar View

**Scenario:** No bookings visible in current month/year view

**German Copy:**
```
Keine Einträge in diesem Zeitraum.
```

**Display:**
- Centered message in calendar area
- "Neue Anfrage" button prominent
- Encourage action

---

### Approver Outstanding - Zero Items

**Scenario:** Approver has no outstanding (NoResponse) items

**German Copy:**
```
Keine ausstehenden Anfragen.
```

**Display:**
- Positive, reassuring tone
- Maybe icon (checkmark)
- Switch to History tab suggested

---

### Approver History - Zero Items

**Scenario:** Approver has no history (never involved in any booking)

**German Copy:**
```
Noch keine Aktivität.
```

**Display:**
- Neutral tone
- Explains that items will appear once approvals happen

---

### Search/Filter No Results

**Scenario:** Search or filter returns no bookings (if search feature implemented)

**German Copy:**
```
Keine Ergebnisse gefunden.
```

**Display:**
- Suggest clearing filters
- Or adjusting search terms

---

## System Errors

### Invalid or Used Link

**Scenario:** User clicks personal or action link that's invalid or already used (though links don't expire per BR-010)

**German Copy:**
```
Der Link ist ungültig oder bereits verwendet.
```

**Display:**
- Error page
- Link to "Zugangslink anfordern" (recovery)
- Explain next steps

---

### Booking Already Canceled

**Scenario:** User tries to act on booking that's already canceled (moved to Archive)

**German Copy:**
```
Diese Anfrage wurde storniert.
```

**Display:**
- Result page or modal
- Return to calendar/overview

---

### Action Not Allowed

**Scenario:** User tries action not permitted for their role or booking state

**German Copy:**
```
Diese Aktion ist für deine Rolle nicht verfügbar.
```

**Display:**
- Modal or banner
- Explain why (if helpful)
- Return to safe view

---

### Network Error (Client-Side)

**Scenario:** API request fails due to network issue

**German Copy:**
```
Bitte erneut versuchen – die Aktion wurde noch nicht gespeichert.
```

**Display:**
- Toast or banner
- Retry button
- Preserve user input if form

---

### General Server Error (Fallback)

**Scenario:** Unexpected server error (500, etc.)

**German Copy:**
```
Uups – da lief was schief.

Bitte öffne die App und führe die Aktion dort aus.

[Zur App öffnen]
```

**Display:**
- Error page (for action links)
- Or modal (for in-app actions)
- Provide app link
- Log error with correlation ID

---

## Form-Specific Errors

### Required Field Missing

**Scenario:** User tries to submit form with required field empty

**German Copy:**
```
Dieses Feld wird benötigt.
```

**Display:**
- Inline error under field
- Red border on input
- Prevent submission

---

### Form Validation Summary

**Scenario:** Multiple validation errors on submit

**German Copy:**
```
Bitte korrigiere die markierten Fehler.
```

**Display:**
- Banner at top of form
- Scroll to first error
- Highlight all error fields

---

## Link Recovery Errors

### Cooldown Active

**Scenario:** User requests link recovery during 60s cooldown (BR-021)

**German Copy:**
```
Bitte warte kurz – wir haben dir deinen persönlichen Link gerade erst gesendet.
```

**Display:**
- Modal or toast
- Countdown timer (optional)
- OK button

---

### Link Recovery Success (Generic)

**Scenario:** User submits email for link recovery (neutral copy, no enumeration)

**German Copy:**
```
Wir haben dir – falls vorhanden – deinen persönlichen Zugangslink erneut gemailt.

Kommt nichts an? Prüfe die Schreibweise oder deinen Spam-Ordner.
```

**Display:**
- Modal
- Positive but neutral
- Close button

---

## Dialog-Specific Copy

### Long Stay Confirmation

**Trigger:** TotalDays > LONG_STAY_WARN_DAYS (default 7)

**German Dialog:**
- **Title:** (not specified in original, suggest:) "Langer Aufenthalt"
- **Body:** (not specified in original, suggest:) "Diese Anfrage umfasst {{TotalDays}} Tage. Möchtest du fortfahren?"
- **Buttons:** "Abbrechen" / "Bestätigen"

---

### Confirmed-Cancel Dialog

**Trigger:** Requester tries to cancel Confirmed booking

**German Dialog:**
- **Title:** "Buchung ist bereits bestätigt"
- **Body:** "Diese Buchung von {{RequesterVorname}} ist bereits von allen bestätigt worden. Bist du sicher, dass du sie stornieren willst? Bitte gib einen kurzen Grund an."
- **Comment Field:** (required, plaintext, ≤500 chars)
- **Buttons:** "Abbrechen" / "Ja, stornieren"

---

### Post-Confirm Deny Dialog

**Trigger:** Approver tries to deny Confirmed booking

**German Dialog:**
- **Title:** "Buchung ist bereits bestätigt"
- **Body:** "Du möchtest eine bereits bestätigte Buchung ablehnen. Bist du sicher? Bitte gib einen kurzen Grund an."
- **Comment Field:** (required, plaintext, ≤500 chars)
- **Buttons:** "Abbrechen" / "Ja, ablehnen"

---

## Loading States

### Calendar Loading

**German Copy:**
```
Laden...
```

**Display:**
- Skeleton UI showing calendar structure
- Animated placeholders
- Should be fast (< 1 second)

---

### Details Loading

**German Copy:**
```
Laden...
```

**Display:**
- Skeleton for booking details
- Spinner or animated bars

---

### Infinite Scroll Loading

**German Copy:**
```
Weitere Einträge laden...
```

**Display:**
- Spinner at bottom of list
- Smooth append of new items

---

## Error Handling Best Practices

### User-Friendly Language
- Informal "du" tone
- Avoid technical jargon
- Clear actionable steps

### Contextual Help
- Explain why error occurred (when helpful)
- Suggest how to fix
- Provide relevant links (recovery, support)

### Visual Hierarchy
- Errors stand out (red, icons)
- Success messages positive (green, checkmarks)
- Neutral messages calm (blue, info icons)

### Accessibility
- Error messages associated with form fields (aria-describedby)
- Focus management (move to first error)
- Screen reader announcements for dynamic errors

### Logging & Debugging
- Log all errors server-side with correlation IDs
- Include context (user action, booking ID, timestamp)
- Never expose sensitive info in error messages

---

## Error Summary Table

| Scenario | German Copy | Display |
|----------|-------------|---------|
| **Conflict** | "Dieser Zeitraum überschneidet sich..." | Modal with details |
| **Future horizon** | "Anfragen dürfen nur maximal {{MONTHS}} Monate..." | Inline or modal |
| **End before start** | "Ende darf nicht vor dem Start liegen." | Inline |
| **Invalid email** | "Bitte gib eine gültige E-Mail-Adresse an." | Inline |
| **Comment required** | "Bitte gib einen kurzen Grund an." | Inline |
| **Invalid first name** | "Bitte gib einen gültigen Vornamen an..." | Inline |
| **Party size range** | "Teilnehmerzahl muss zwischen 1 und {{MAX}} liegen." | Inline |
| **Not integer** | "Bitte gib eine ganze Zahl ein." | Inline |
| **Text too long** | "Text ist zu lang (max. 500 Zeichen)." | Inline |
| **Links not allowed** | "Links sind hier nicht erlaubt..." | Inline |
| **Past-dated** | "Dieser Eintrag liegt in der Vergangenheit..." | Banner |
| **Booking submitted** | "Anfrage gesendet. Du erhältst E-Mails..." | Toast |
| **Cancel confirmed** | "Anfrage storniert. Benachrichtigt: ..." | Modal |
| **No bookings** | "Keine Einträge in diesem Zeitraum." | Centered |
| **No outstanding** | "Keine ausstehenden Anfragen." | Centered |
| **Invalid link** | "Der Link ist ungültig..." | Error page |
| **Already canceled** | "Diese Anfrage wurde storniert." | Modal |
| **Action not allowed** | "Diese Aktion ist für deine Rolle nicht verfügbar." | Modal |
| **Network error** | "Bitte erneut versuchen..." | Toast |
| **Server error** | "Uups – da lief was schief..." | Error page |
| **Required field** | "Dieses Feld wird benötigt." | Inline |
| **Cooldown active** | "Bitte warte kurz..." | Modal |
| **Link recovery** | "Wir haben dir – falls vorhanden..." | Modal |

---

## Implementation Notes

### Error State Management
- Validate on blur and submit
- Clear errors on field change
- Preserve user input on error
- Focus first error field

### Error Response Format (API)
```json
{
  "error": {
    "code": "CONFLICT",
    "message": "Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung (Anna – Ausstehend).",
    "details": {
      "conflictingBooking": {
        "firstName": "Anna",
        "status": "Pending"
      }
    }
  }
}
```

### Client-Side Validation
- Validate before submit (reduce round trips)
- But always validate server-side (never trust client)
- Use same validation rules client/server

### Retry Logic
- Network errors: Auto-retry with exponential backoff
- Idempotent operations: Safe to retry
- Non-idempotent: Warn user before retry
