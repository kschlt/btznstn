# Functional Requirements Overview

## 6.1 Calendar & Conflicts

### Visual Display
- **States:** Show Free, Pending, Denied, Confirmed, Canceled
- **Per-Cell Information:**
  - First name (truncate if long; full in details)
  - Party size ("n Personen" always)
  - Status badge
  - Affiliation color
- **Annotations:**
  - Weekends visually distinct
  - German holidays (global config, optional, visual only; hidden if unavailable)

### Views & Navigation
- **Available Views:**
  - Month (default)
  - Year
  - Week _(planned for later)_
- **Navigation:**
  - Scroll between months
  - "Heute" button (jump to today)
  - Week starts Monday
  - Desktop: keyboard navigation (arrows/Enter/Esc)

### Interactions
- **Single tap/click opens details** (no hover required)
- **No hover-dependent interactions** (mobile-first)
- Large tap targets for mobile usability

### Conflict Detection & Prevention
- **Inclusive end date semantics:** Both start and end dates are part of booking
- **Show total days:** Display calculated total days for each booking
- **No overlaps allowed** with:
  - **Pending** (blocker)
  - **Confirmed** (blocker)
- **Overlaps allowed** with (non-blockers):
  - **Denied** (dates immediately free)
  - **Canceled** (dates immediately free)

### Date Selection
**Drag-Select:**
- Start only on **free day**
- Cannot cross blocked days
- Shows visual feedback during drag

**Date-Picker:**
- Validates at submit
- Shows conflict summary if overlap detected
- Conflict summary includes: **first name + status** of conflicting entry

### Concurrent Submissions (BR-029)
**First-write-wins** conflict resolution:
- Concurrent submissions for same dates resolved by persisted timestamp
- First submission to persist wins
- Later submissions return conflict error with details

---

## 6.2 Create & Edit

### Create Entry - Two Paths

**1. Drag-Select:**
- Select start→end on calendar
- Opens "New Request" with dates prefilled

**2. "Neue Anfrage" Button:**
- Opens form with date picker
- User manually selects dates

### Form Fields

**Required:**
- Requester first name (validation per BR-019)
- Email (validation per §9, immutable after creation)
- Start date
- End date (must be ≥ start date)
- Party size (≥1, ≤MAX_PARTY_SIZE, default 10)
- Affiliation (visual: Ingeborg, Cornelia, or Angelika)

**Optional:**
- Description (plaintext, no links, emojis/newlines allowed, ≤500 chars)

### Multiple Requests Per Requester
- Supported
- Personal link aggregates all requests for that email address
- No limit on number of requests per user (subject to rate limits)

### Edit Rules While Pending

**Shorten Within Original Bounds:**
- Approvals remain unchanged
- Date edit logged in timeline
- Requester notified of change

**Extend (earlier start or later end):**
- All approvals reset to NoResponse
- Re-approval emails sent to all approvers
- Old→new diff shown in emails
- Date edit logged in timeline

**Party Size Only:**
- Approvals remain unchanged
- Change not logged in timeline
- Immediately visible

**Affiliation Only:**
- Approvals remain unchanged
- Change not logged in timeline
- Color updates immediately

**First Name:**
- Allowed anytime (BR-025)
- Never resets approvals
- Not logged in timeline

### Cancel While Pending (BR-006)
- Requester may cancel
- No comment required
- Transitions to Canceled → Archive
- Notifications: Requester + all three approvers

### Restrictions

**No Past-Date Creates/Edits:**
- Past items are read-only (BR-014)
- Past = `EndDate < today` (flip at 00:00 day after EndDate)

**Future Horizon (BR-026):**
- `StartDate ≤ today + FUTURE_HORIZON_MONTHS`
- Default: 18 months
- Error if exceeded

**Long-Stay Confirm (BR-027):**
- If `TotalDays > LONG_STAY_WARN_DAYS` (default 7)
- Show confirmation dialog
- Continue only if user confirms

---

## 6.3 Approvals & Denials

### Approval Requirements (BR-003)
- **Three fixed approvers** must approve for Confirmed
- **Any order** acceptable
- **Approve is idempotent** (repeat shows "Schon erledigt")

### Deny While Pending
**Requirements:**
- Comment required (plaintext, no links, ≤500 chars)

**Effects:**
- Transitions to **Denied**
- **Non-blocking:** Dates become free immediately
- **Not public:** Hidden from public calendar view
- Deny email sent to **everyone** (Requester + all three approvers)

**Requester Options After Deny:**
- **Reopen:** Back to Pending (all approvals reset)
- **Cancel:** Move to Archive

**Approver Restrictions:**
- While Denied, approvers cannot act
- No approve/deny possible until reopened or canceled

### Deny While Confirmed (BR-004 Post-Confirm Deny)

**Warning Dialog Required:**
- **Title:** "Buchung ist bereits bestätigt"
- **Body:** "Du möchtest eine bereits bestätigte Buchung ablehnen. Bist du sicher? Bitte gib einen kurzen Grund an."
- **Buttons:** "Abbrechen" / "Ja, ablehnen"

**Requirements:**
- Comment required (same as Deny while Pending)

**Effects:**
- Same as Deny while Pending
- Transitions to **Denied**
- **Non-blocking:** Dates become free immediately
- **Not public:** Hidden from public calendar
- Deny email sent to **everyone**

### Self-Approval/Deny (BR-015)
If requester is one of the three approvers:
- **Self-approval auto-applied** at submission
- Other two approvers must still approve
- Self-approver may **Deny** while Pending (requires comment)

### First-Action-Wins Concurrency (BR-024)
**Scenario:** Multiple approvers act simultaneously

**Resolution:**
- First action to persist wins
- Later actions show **"Schon erledigt"** with context

**Examples:**
- "Schon erledigt. Die Buchung ist bereits bestätigt."
- "Schon erledigt. {{Partei}} hat bereits abgelehnt – die Anfrage ist jetzt abgelehnt (nicht öffentlich)."

---

## 6.4 Notifications & Reminders

### Email Triggers & Recipients

| Event | Recipients | Details |
|-------|-----------|---------|
| **Submission** | Approvers (except self-approver) | Ask for decision |
| **Approve (not final)** | Requester | Show who's outstanding |
| **Final approval** | Requester + All approvers | Suppress requester's "last approver" intermediate |
| **Deny (Pending or Confirmed)** | **Requester + All three approvers** | Include reason; state now Denied |
| **Cancel (Pending)** | **Requester + All three approvers** | Confirm cancel; list notified |
| **Cancel (Confirmed)** | **Requester + All three approvers** | Confirm cancel; list notified |
| **Cancel (Denied)** | **Requester only** | Approvers already informed by Deny |
| **Edit: Shorten** | Requester | Acknowledge change |
| **Edit: Extend** | Approvers | Re-approval required; show diff |
| **Reopen** | Approvers | Re-approval required; include diffs |

### Weekly Digest (BR-009)
**Schedule:**
- Sunday 09:00 Europe/Berlin

**Content:**
- Per-approver email
- Lists **their** NoResponse items
- Aged **≥5 calendar days** (day-0 rule: submission date is day 0)
- **Future-only** (exclude past-dated)
- Ordered by **soonest start date**

**Suppression:**
- If zero items meet criteria, digest not sent

**Actions:**
- Approve: One-click link
- Deny: Opens comment form

### No Extra Reminders
Beyond weekly digest, no additional automated reminders sent.

### Action-Link Result Page
After clicking action link in email:
- **Success:** Confirmation message with current status
- **Already done:** "Schon erledigt" with context
- **Error:** Fallback message with link to open app

See `docs/specification/notifications.md` for complete email copy and result page text.

---

## 6.5 Roles, Access & Privacy

### No Login System
- **Role-by-link:** Role determined by link type (requester vs approver vs viewer)
- **Emails never shown** in any UI
- **Trust-by-entry:** No email verification before first submission

### Public Calendar (Global Unlisted URL)
**Access:**
- Via global unlisted URL (not indexed by search engines)
- No authentication required

**Visibility:**
- Shows **Pending** and **Confirmed** bookings
- **Denied** and **Canceled** hidden from public view
- Displays: first name, party size, status badge, affiliation color

**Restrictions:**
- Cannot see comments
- Cannot see email addresses
- Cannot create or edit
- Read-only

### Comments Visibility
**Requester:**
- Own comments
- All approver comments on own bookings

**Approvers:**
- All comments on bookings involving them

**Viewers:**
- No comment access

### Lost Link Recovery
**Entry Point:**
- Subtle text link: "Ist das deine Anfrage? Jetzt Link anfordern"
- Available on landing and details pages

**Flow:**
- Opens popup to enter email
- Resends **personal link** if email exists
- Shows neutral success copy (no enumeration)
- Subject to cooldown (BR-021)

**Cooldown (BR-021):**
- 60 seconds per email/IP
- Neutral message: "Bitte warte kurz – wir haben dir deinen persönlichen Link gerade erst gesendet."

**No Enumeration:**
- Same success message whether email exists or not
- "Wir haben dir – falls vorhanden – deinen persönlichen Zugangslink erneut gemailt."

### Archive
**Hidden Storage:**
- Contains Canceled bookings
- Not visible to any end user
- No UI for viewing archive

**Purpose:**
- Data retention per BR-013
- Audit trail
- Purged per archival policy

---

## 6.6 Roles & Permissions Matrix

| Role | State | View | Create | Edit | Approve | Deny | Cancel | Reopen |
|------|-------|------|--------|------|---------|------|--------|--------|
| **Requester** | Pending (own) | ✓ | ✓ | **✓** (per BR-005) | — | — | **✓** | — |
| **Requester** | Confirmed (own) | ✓ | — | — | — | — | **✓ (comment required)** | — |
| **Requester** | Denied (own) | ✓ | — | Edit via reopen | — | — | **✓** | **✓** |
| **Approver** | Pending (involving) | ✓ | — | — | **✓** | **✓ (comment)** | — | — |
| **Approver** | Confirmed (involving) | ✓ | — | — | — | **✓ (warn + comment)** | — | — |
| **Viewer** | Public (Pending/Confirmed) | ✓ (no comments) | — | — | — | — | — | — |

**Key:**
- ✓ = Allowed
- — = Not allowed
- Conditions in parentheses

**Important Notes:**
- Denied state: Not visible to Viewers (not public)
- Canceled state: Not visible to anyone (moved to Archive)
- Approvers cannot cancel bookings (only requesters can)
- Viewers have read-only access to public Pending/Confirmed bookings
