# UI Screens & Navigation

## Overview

This document describes all screens, views, and interactions in the booking application.

---

## Calendar View (All Roles)

### Views & Navigation

**Available Views:**
- **Month View** (default)
- **Year View**
- **Week View** _(planned for later)_

**Navigation Controls:**
- Scroll between months (swipe on mobile, arrows on desktop)
- **"Heute"** button - Jump to current date
- Month/Year selector

**Calendar Configuration:**
- **Week starts Monday**
- German locale (de-DE)
- Europe/Berlin timezone

**Desktop-Only Features:**
- Keyboard navigation:
  - Arrow keys: Navigate dates
  - Enter: Open selected date/booking
  - Esc: Close details

---

### Visual Annotations

**Weekends:**
- Visually distinct styling
- Different background color

**Holidays:**
- German holidays displayed (global config)
- **Region configurable:** e.g., "DE" or "DE-NRW"
- **Optional:** Visual only, hidden if unavailable
- No business logic impact (booking allowed on holidays)

---

### Per-Cell Display

Each booking displayed in calendar cell shows:

**First Name:**
- Requester's first name
- Truncate if too long for cell
- Full name shown in details view

**Party Size:**
- Always format: "n Personen"
- Examples: "1 Personen", "5 Personen"
- Displayed even for single person (per BR-016)

**Status Badge:**
- Visual indicator of booking state
- Options: Pending, Confirmed, Denied (not public), Canceled (not public)
- Color-coded for quick recognition

**Affiliation Color:**
- Background or border color per affiliation
- Colors:
  - Ingeborg: `#C1DBE3` (light blue)
  - Cornelia: `#C7DFC5` (light green)
  - Angelika: `#DFAEB4` (light pink)
- Must maintain sufficient contrast with text

---

### Interactions

**Mobile-First:**
- **Single tap/click** opens booking details
- **No hover** required or expected
- Large tap targets (minimum 44×44 points on mobile)
- High contrast for readability

**Desktop Enhancement:**
- Keyboard navigation supported
- Mouse click opens details
- No hover-dependent information

---

### Conflict Visualization

**Drag-Select:**
- **Start only on free day**
- Cannot cross blocked days
- Visual feedback during drag:
  - Selected dates highlighted
  - Blocked dates visually distinguished
  - Clear indication of valid/invalid selection

**Date Picker:**
- Conflict validation at submit
- Blocked dates visually disabled
- Tooltip or indicator on blocked dates

**Conflict Summary Dialog:**
- Shows when submission fails due to conflict
- Displays for each conflicting booking:
  - First name
  - Status (Pending or Confirmed)
- Example: "Dieser Zeitraum überschneidet sich mit einer bestehenden Buchung (Anna – Ausstehend)."

**Blockers (prevent overlap):**
- Pending bookings
- Confirmed bookings

**Non-Blockers (allow overlap):**
- Denied bookings (dates freed immediately)
- Canceled bookings (moved to Archive)

---

## Request Details (Dialog/Page)

### Viewer Access (Public Link)

**Visible Information:**
- First name (full, not truncated)
- Date range (formatted: "01.–05.08.2025")
- Total days
- Party size ("n Personen")
- Description (if provided)
- **Timeline:** Actors + actions only (no comments, no detailed notes)

**Hidden Information:**
- Email addresses (PII)
- Comments from any party
- Internal notes

**States Visible:**
- Pending
- Confirmed

**States Hidden:**
- Denied (not public)
- Canceled (moved to Archive)

---

### Requester Access (Personal Link)

**All Viewer Information Plus:**

**Full Timeline:**
- Submission event
- All approval/denial events (named parties)
- **All date edits** with diffs (old→new)
- Reopen events
- Confirmation events
- Cancellation events

**Comments:**
- Own comments
- All approver comments on this booking

**Actions Available:**

**While Pending:**
- **Edit** button → Opens edit dialog
  - Can modify: dates, party size, affiliation, description, first name
  - Validation per BR-005 rules
- **Cancel** button → Confirms → Canceled (no comment required)

**While Confirmed:**
- **Cancel** button → Shows confirmed-cancel dialog:
  - Title: "Buchung ist bereits bestätigt"
  - Body: "Diese Buchung von {{RequesterVorname}} ist bereits von allen bestätigt worden. Bist du sicher, dass du sie stornieren willst? Bitte gib einen kurzen Grund an."
  - Comment field (required)
  - Buttons: "Abbrechen" / "Ja, stornieren"

**While Denied:**
- Sees status: "Abgelehnt"
- Sees denial comment from approver
- **"Wieder eröffnen"** button → Opens edit dialog (reopen flow)
  - All fields editable
  - Submitting transitions to Pending (approvals reset)
- **"Stornieren"** button → Confirms → Canceled (no extra notification to approvers)

---

### Approver Access (Personal Link)

**All Requester Information Plus:**

**Comments:**
- All comments from all parties on bookings involving them

**Actions Available:**

**While Pending:**
- **Approve** button (one-click)
  - Idempotent
  - Updates decision → Approved
  - May trigger Confirmed if final approval
- **Deny** button → Opens comment form:
  - Comment field (required, plaintext, no links, ≤500 chars)
  - Submit → Status becomes Denied

**While Confirmed:**
- **Deny** button → Shows warning dialog:
  - Title: "Buchung ist bereits bestätigt"
  - Body: "Du möchtest eine bereits bestätigte Buchung ablehnen. Bist du sicher? Bitte gib einen kurzen Grund an."
  - Comment field (required)
  - Buttons: "Abbrechen" / "Ja, ablehnen"
  - If confirmed → Status becomes Denied

**While Denied:**
- View-only (no action buttons)
- Can see denial comment
- Cannot approve or deny until reopened

---

### Timeline Display

**Logged Events:**
- Submitted (with timestamp, requester)
- Approved (named party, timestamp)
- Denied (named party, timestamp, comment visible to relevant parties)
- **Date edits** (old→new diff, whether approvals reset)
- Confirmed (all three approved, timestamp)
- Canceled (by requester, timestamp, comment if Confirmed)
- Reopened (from Denied, timestamp)

**NOT Logged:**
- Party size edits
- Affiliation edits
- First name edits
- Description edits
- System/digest events (not public-facing)

**Display Format:**
- Chronological order (oldest first)
- Clear actor labels: Requester, [Approver Name], System
- Timestamp in German format
- Diffs for date changes: "01.–05.08. → 03.–08.08."

---

## Approver Overview (Personal Link)

### Two-Tab Interface

**Outstanding Tab:**
- Shows bookings where **this approver = NoResponse**
- Status = Pending
- Action-required list

**History Tab:**
- Shows **all bookings** involving this approver
- **All statuses:** Pending, Confirmed, Denied (not Canceled, moved to Archive)
- Read-only
- Complete audit trail

---

### List Display

**Sorting:**
- By **LastActivityAt desc** (most recent activity first)
- Applies to both Outstanding and History

**Per-Item Display:**
- Requester first name
- Date range (formatted)
- Party size
- Status badge
- Days until start (if future)
- Affiliation color indicator

**Actions (Outstanding Only):**
- **Approve** (one-click, right from list)
- **Deny** (opens comment form)
- **View Details** (tap/click entire row)

**No Actions (History):**
- View-only
- Tap/click row opens details

---

### Infinite Scroll

**Implementation:**
- Load initial batch (e.g., 20 items)
- As user scrolls near bottom, load more
- No pagination controls
- Smooth loading indicator

---

## Create Entry - Two Paths

### Path 1: Drag-Select

**Flow:**
1. User drags on calendar from start date to end date
2. Must start on **free day** (not blocked)
3. Cannot cross blocked days (drag stops at blocker)
4. Visual feedback during drag
5. On release, "New Request" form opens with dates prefilled

**Validation:**
- Start cell must be free
- All cells in range must be free
- If drag crosses blocker, drag truncates or cancels

---

### Path 2: "Neue Anfrage" Button

**Flow:**
1. User clicks "Neue Anfrage" button (always visible)
2. Form opens with date picker
3. User manually selects start and end dates
4. Continues to fill rest of form

---

## Create/Edit Form

### Required Fields

**Requester First Name:**
- Text input
- Validation per BR-019 (letters, diacritics, space, hyphen, apostrophe; max 40; trim)
- Error: "Bitte gib einen gültigen Vornamen an..."

**Email:**
- Email input
- Validation per §9
- **Immutable after creation** (cannot be edited)
- Error: "Bitte gib eine gültige E-Mail-Adresse an."

**Start Date:**
- Date picker
- Must be ≤ `today + FUTURE_HORIZON_MONTHS` (default 18)
- Error if too far: "Anfragen dürfen nur maximal {{MONTHS}} Monate im Voraus gestellt werden."

**End Date:**
- Date picker
- Must be ≥ Start Date
- Error: "Ende darf nicht vor dem Start liegen."

**Party Size:**
- Number input (integer)
- Range: 1 to MAX_PARTY_SIZE (default 10)
- Stepper or dropdown recommended
- Error: "Teilnehmerzahl muss zwischen 1 und {{MAX}} liegen."

**Affiliation:**
- Radio buttons or dropdown
- Options: Ingeborg, Cornelia, Angelika
- Visual color indicator per option

---

### Optional Fields

**Description:**
- Textarea
- Plaintext only
- No links (http://, https://, www, mailto: blocked per BR-020)
- Emojis allowed
- Newlines allowed
- Max 500 characters
- Error if links: "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden."
- Error if too long: "Text ist zu lang (max. 500 Zeichen)."

---

### Long Stay Confirmation (BR-027)

**Trigger:** If `TotalDays > LONG_STAY_WARN_DAYS` (default 7)

**Dialog:**
- Appears before submission completes
- Message: Confirm intent for long booking
- Buttons: "Abbrechen" / "Bestätigen"
- Only proceeds if user confirms

---

### Conflict Handling

**On Submit:**
- System checks for conflicts with Pending/Confirmed
- If conflict exists:
  - Show error dialog
  - List each conflicting booking: first name + status
  - User must adjust dates and resubmit

---

## Lost Link Entry

### Access Points

**Subtle Text Link:**
- Displayed on:
  - Landing page (calendar view)
  - Booking details page
- Text: "Ist das deine Anfrage? Jetzt Link anfordern"
- Styled as secondary/subtle (not primary CTA)

---

### Recovery Flow

1. **User clicks link**
2. **Popup/modal opens:**
   - Title: "Zugangslink anfordern"
   - Email input field
   - Submit button: "Link senden"
3. **User enters email and submits**
4. **System response:**
   - **Always neutral success** copy (no enumeration)
   - "Wir haben dir – falls vorhanden – deinen persönlichen Zugangslink erneut gemailt. Kommt nichts an? Prüfe die Schreibweise oder deinen Spam-Ordner."
5. **If cooldown active (BR-021):**
   - "Bitte warte kurz – wir haben dir deinen persönlichen Link gerade erst gesendet."

**API Behavior:**
- If email exists, resend existing token (don't generate new)
- If email doesn't exist, still show success (no enumeration)
- Apply 60-second cooldown per email/IP
- Apply rate limit: 5 requests per hour per email

---

## Mobile Considerations

### Minimum Viewport
- **Target:** iPhone 8 class (~375×667 logical pixels)
- Must work smoothly on older/smaller phones
- Test on devices released 2019+

### Mobile-Specific Design

**Large Tap Targets:**
- Minimum 44×44 points
- Adequate spacing between interactive elements

**High Contrast:**
- Text readable in bright sunlight
- Status badges clearly distinguishable

**No Hover:**
- All interactions via tap
- No hover states required
- No hover-dependent information

**Single-Tap Navigation:**
- Tap booking → Opens details
- No long-press required
- No multi-step gestures

**Avoid Horizontal Scroll:**
- All content fits viewport width
- Responsive layout
- Calendar cells adjust to screen size

---

## Desktop Enhancements

### Keyboard Navigation

**Calendar View:**
- Arrow keys: Navigate between dates
- Enter: Open selected booking/date
- Esc: Close details/dialogs
- Tab: Move between interactive elements

**Forms:**
- Standard tab navigation
- Enter to submit
- Esc to cancel

### Mouse Interactions

- Click to select/open
- Drag-select for date ranges
- Hover states (enhancement, not required)

---

## Empty States

**No Bookings in View:**
- Message: "Keine Einträge in diesem Zeitraum."
- Encourage action: "Neue Anfrage" button prominent

**Approver Outstanding - Zero Items:**
- Message: "Keine ausstehenden Anfragen."
- Positive tone

**Approver History - Zero Items:**
- Message: "Noch keine Aktivität."

---

## Loading States

**Calendar Loading:**
- Skeleton UI showing calendar structure
- Animated placeholders for bookings
- Quick load expected (< 1 second)

**Details Loading:**
- Skeleton for booking details
- Fast transition expected

**Infinite Scroll Loading:**
- Spinner at bottom of list
- Smooth loading of additional items

---

## Error States

See `error-handling.md` for complete error copy and scenarios.

---

## Responsive Breakpoints

**Mobile:**
- < 768px
- Single-column layout
- Stacked elements
- Full-width buttons

**Tablet:**
- 768px – 1024px
- May show more calendar weeks
- Optimized tap targets still

**Desktop:**
- > 1024px
- May show sidebar
- Keyboard navigation enabled
- More information density

---

## Accessibility

**Color Contrast:**
- WCAG AA minimum
- Text readable against affiliation colors
- Status badges have sufficient contrast

**Semantic HTML:**
- Proper heading hierarchy
- Button/link semantics
- Form labels associated with inputs

**Focus Indicators:**
- Clear focus outlines
- Keyboard navigation visible

**Screen Reader Support:**
- Alt text for status badges
- ARIA labels where needed
- Logical tab order

---

## Navigation Summary

| Screen | Access | Primary Actions |
|--------|--------|----------------|
| **Calendar (Public)** | Unlisted URL | View, Create, Recover Link |
| **Booking Details (Viewer)** | Via calendar | View |
| **Booking Details (Requester)** | Personal link | View, Edit, Cancel, Reopen |
| **Booking Details (Approver)** | Personal link | View, Approve, Deny |
| **Approver Overview** | Personal link | View Outstanding, View History |
| **Create Form** | Drag-select or button | Submit new booking |
| **Edit Form** | Details → Edit | Modify booking |
| **Reopen Form** | Details → Reopen | Reopen denied booking |
