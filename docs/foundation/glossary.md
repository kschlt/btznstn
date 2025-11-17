# Glossary

## Core Terms

### Booking / Request
Whole-day date range + PartySize (including requester). Represents a request to reserve specific dates on the shared calendar.

### Party Size
Number of people included in the booking, **including the requester**. Range: 1 to MAX_PARTY_SIZE (default 10). Always displayed as "n Personen" in German UI.

---

## Booking States

### Pending
**Status:** Awaiting all three approvals.

**Characteristics:**
- Blocks calendar dates (no overlaps allowed)
- Visible on public calendar
- Requester can edit or cancel
- Approvers can Approve or Deny
- Default state when booking is submitted

### Denied
**Status:** Any approver has denied the request (with comment).

**Characteristics:**
- **Non-blocking:** Dates become free immediately
- **Not public:** Hidden from public calendar view
- Requester may **Reopen** (back to Pending with reset approvals) or **Cancel**
- While Denied, approvers cannot act
- Can result from denial during Pending or Confirmed state

### Confirmed
**Status:** All three approvers have approved.

**Characteristics:**
- Blocks calendar dates (no overlaps allowed)
- Visible on public calendar
- Requester can cancel (requires comment)
- Approvers can Deny (requires warning + comment)
- Final positive state before potential cancellation

### Canceled
**Status:** Final state after requester cancels (any stage) or after Denied then requester cancels.

**Characteristics:**
- Moves to Archive (hidden from all views)
- Not visible on public calendar
- No further actions possible
- Terminal state

---

## Access & Links

### Personal Link
Magic link tying a requester or approver to their items and actions. Unique per email address, no expiry, resendable.

### Action Link
One-click approve/deny link embedded in emails. Idempotent (repeat actions show "Schon erledigt" with context).

### Global Unlisted URL
Public calendar access URL not indexed by search engines. Shows Pending/Confirmed bookings only. Read-only viewer access.

---

## Notifications

### Weekly Digest
**Schedule:** Sunday 09:00 Europe/Berlin

**Content:** Email to each approver listing their **NoResponse** items aged **≥5 calendar days** (future-only)

**Ordering:** By soonest start date

**Suppression:** If zero items, digest is not sent

**Day-0 Rule:** Age calculated from submission date as calendar days (not hours)

---

## Technical Terms

### LastActivityAt
Timestamp of most recent timeline event for a booking. Drives list sorting (descending) in approver views.

### First-Write-Wins
**Conflict Resolution:** If two create or extend operations contend for the same free dates, the first persisted submission wins; later submissions fail with conflict error.

**Applies to:**
- New booking submissions
- Edit operations that extend date ranges
- Concurrent requests from different users

### NoResponse
**Decision State:** Approver has not yet made a decision (neither Approved nor Denied) for a booking requiring their approval.

**Used in:**
- Weekly digest filtering
- Outstanding items list
- Approval status display

---

## Booking Properties

### Affiliation
Which fixed party a booking is visually associated with (color coding/legend).

**Important:** Visual only. All three approvals are still required regardless of affiliation.

**Options:**
- Ingeborg
- Cornelia
- Angelika

### Description
Optional plaintext field describing the booking purpose.

**Constraints:**
- Maximum 500 characters
- Plaintext only (no links)
- Emojis and newlines allowed
- Links blocked (http(s)://, www, mailto:)

### Total Days
Calculated field: `EndDate - StartDate + 1`

Inclusive end-date semantics (both start and end dates are part of the booking).

---

## Date Concepts

### Inclusive End Date
The end date is **included** in the booking period. A booking from Jan 1-3 covers three full days: Jan 1, Jan 2, and Jan 3.

### Past Item
**Definition:** Booking where `EndDate < today`

**Timing:** Flips to past at **00:00** Europe/Berlin the day after EndDate

**Restrictions:**
- Read-only (no edits, no actions)
- No operations allowed
- Visual indicator shown

### Future Horizon
**Definition:** Maximum advance booking period

**Default:** 18 months from today

**Rule:** `StartDate ≤ today + FUTURE_HORIZON_MONTHS`

**Config:** FUTURE_HORIZON_MONTHS

---

## Operations

### Reopen
**Action:** Requester transitions a Denied booking back to Pending status.

**Effects:**
- All approvals reset to NoResponse
- Re-approval emails sent to all approvers
- If dates changed, diff shown in emails
- Dates are re-validated for conflicts

**Constraint:** Fails if dates conflict with any Pending/Confirmed booking (user must edit first)

### Edit (While Pending)

**Shorten:** Reduce date range within original bounds
- **Approvals:** Remain unchanged
- **Notification:** Requester informed
- **Audit:** Date edit logged

**Extend:** Expand date range (earlier start or later end)
- **Approvals:** Reset to NoResponse
- **Notification:** Re-approval emails with old→new diff
- **Audit:** Date edit logged

**Party Size / Affiliation Only:** Change party size or affiliation without date changes
- **Approvals:** Remain unchanged
- **Audit:** Not logged

**First Name:** Change requester first name
- **Approvals:** Never reset
- **Audit:** Not logged

### Cancel

**By Requester (Pending):**
- Transitions to Canceled → Archive
- No comment required
- Notifies: Requester + all three approvers

**By Requester (Confirmed):**
- Requires comment (confirmed-cancel dialog)
- Transitions to Canceled → Archive
- Notifies: Requester + all three approvers

**By Requester (Denied):**
- Transitions to Canceled → Archive
- Notifies: Requester only (approvers already informed by Deny)

**Note:** Approvers cannot cancel bookings.

---

## System Concepts

### Archive
Hidden storage for Canceled bookings. Not visible to any end user (requester, approver, or viewer).

**Purge Policy:**
- Canceled items purged monthly when archived > 1 year
- Past Confirmed never purged
- Denied items purged once EndDate < today

### Auto-Cleanup
**Trigger:** Pending booking where EndDate < today

**Action:** At EndDate+1 00:00 Europe/Berlin, auto-cancel to Archive

**Actor:** System

**Notifications:** None sent

### Timeline Event
Audit record of actions on a booking.

**Logged Actions:**
- Submitted
- Approved (by named party)
- Denied (by named party)
- Date edits (with diffs and approval impact)
- Confirmed (all approvals received)
- Canceled (by requester)
- Reopened (from Denied)

**Not Logged:**
- Party size edits
- Affiliation edits
- First name edits
- Description edits
- Digest events (internal)
- System events (not public-facing)

### Actor Types
- **Requester:** Person who created the booking
- **Approver:** One of the three fixed approvers (Ingeborg, Cornelia, Angelika)
- **System:** Automated actions (e.g., auto-cleanup)

---

## Configuration Terms

### Blockers
Booking states that prevent overlapping date ranges:
- Pending
- Confirmed

### Non-Blockers
Booking states that do NOT prevent overlapping date ranges (dates are immediately free):
- Denied
- Canceled

### Long Stay Warning
**Trigger:** TotalDays > LONG_STAY_WARN_DAYS (default 7)

**Action:** Show confirmation dialog before allowing submission

**Purpose:** Prevent accidental long bookings

---

## Rate Limiting

### Submission Limit
Default: 10 bookings per day per email address

### IP Rate Limit
Default: 30 requests per hour per IP address

### Recovery Limit
Default: 5 link recovery requests per hour per email address

### Soft Cooldown
60-second cooldown on link recovery per email/IP. Shows neutral "please wait" message during cooldown period.

---

## Email & Privacy

### PII (Personally Identifiable Information)
Email addresses are considered PII in this system and are:
- Never displayed in any UI
- Stored securely
- Normalized (lowercase) for uniqueness
- Immutable once set
- Hidden from viewers
- Hidden from other requesters

### Email Validation
**Rules:**
- Trimmed (no leading/trailing spaces)
- No spaces within email
- Exactly one `@` symbol
- Non-empty local part (before @)
- Domain contains at least one dot
- TLD is 2-24 letters
- Maximum length: 254 characters (configurable)

**Example regex (non-normative):** `^[^\s@]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,24}$`

### Mistyped Email Policy
If requester enters wrong email:
- Cannot edit email (immutable)
- Must create new booking with correct email
- Original booking blocks dates until:
  - Approver denies it (on request), or
  - Auto-cancels once past (EndDate+1 00:00)

---

## German UI Terms

### Requester First Name Validation
**Allowed:**
- Letters (including diacritics: ä, ö, ü, etc.)
- Spaces
- Hyphen (-)
- Apostrophe (')

**Constraints:**
- Trimmed
- Maximum 40 characters
- No emojis
- No newlines

### Comment Fields
Used for Deny and Cancel (Confirmed) operations.

**Constraints:**
- Plaintext only
- No links (http(s)://, www, mailto: blocked)
- Emojis and newlines allowed
- Maximum 500 characters
- Required when specified by business rules

### Status Display Terms (German)
- **Pending:** "Ausstehend"
- **Denied:** "Abgelehnt"
- **Confirmed:** "Bestätigt"
- **Canceled:** "Storniert"

### Party Size Display
Always: "n Personen" (even for 1 person: "1 Person" would be grammatically correct but system uses "1 Personen" for consistency per spec)

**Note:** The spec says "always" use "n Personen" format.
