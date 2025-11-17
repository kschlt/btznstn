# Business Rules

## Overview

Named business rules that govern system behavior. These rules are referenced throughout the documentation and in implementation.

---

## Date & Booking Rules

### BR-001: Whole-Day Bookings with Inclusive End Date
Whole-day bookings only; **inclusive** end date semantics.

**Calculation:** `total_days = EndDate − StartDate + 1`

**Example:** A booking from Jan 1–3 covers three full days: Jan 1, Jan 2, and Jan 3.

---

### BR-002: No Overlaps with Conflict Summary
**No overlaps** allowed with any **Pending** or **Confirmed** booking.

**Conflict Detection:** System checks for date range intersection before allowing create or edit.

**Conflict Summary:** Shows **first name + status** of conflicting booking.

**User Feedback:** Clear error message indicating which booking conflicts and its status.

---

### BR-014: Past Items Read-Only
No operations allowed when `EndDate < today`.

**Timing:** Flip to past status at **00:00 Europe/Berlin** the day after EndDate.

**Restrictions:**
- No edits
- No approvals/denials
- No cancellations
- No reopen
- Read-only display with visual indicator

---

### BR-026: Future Horizon
Bookings cannot be created too far in advance.

**Rule:** `StartDate ≤ today + FUTURE_HORIZON_MONTHS`

**Default:** 18 months from today

**Config:** FUTURE_HORIZON_MONTHS (configurable)

**Error:** "Anfragen dürfen nur maximal {{MONTHS}} Monate im Voraus gestellt werden."

---

### BR-027: Long Stay Confirmation
Warn user before allowing very long bookings.

**Trigger:** `TotalDays > LONG_STAY_WARN_DAYS`

**Default:** 7 days

**Config:** LONG_STAY_WARN_DAYS (configurable)

**Action:** Show confirmation dialog; proceed only if user confirms.

**Purpose:** Prevent accidental long bookings.

---

### BR-029: First-Write-Wins
**Create/extend** operations are serialized by persisted submission timestamp.

**Scenario:** Two users simultaneously try to book the same free dates.

**Resolution:** The first submission that successfully persists to database wins.

**Effect:** Later submission receives conflict error with details of winning booking.

**Applies to:**
- New booking submissions
- Edit operations that extend date ranges

---

## Approval & Decision Rules

### BR-003: Three Fixed Approvers Required
**Three fixed approvers** (Ingeborg, Cornelia, Angelika) must approve for **Confirmed** status.

**Approval Requirements:**
- All three must Approve for Confirmed
- Any order acceptable
- Affiliation is visual only (does not affect approval requirements)

**Transition to Confirmed:** When third and final approval is received.

---

### BR-004: Denial Handling
Any **Deny** (Pending or Confirmed) with comment → **Denied** status.

**Characteristics:**
- **Non-blocking:** Dates become free immediately
- **Not public:** Hidden from public calendar view
- Only requester may **Reopen** (→ Pending; all approvals reset; re-approval emails sent)
- Only requester may **Cancel** (→ Archive)

**Post-Confirm Deny:**
- Requires warning dialog before allowing
- Still requires comment
- Same Denied status and effects

**While Denied:**
- Approvers cannot act (no approve/deny possible)
- Requester can view, reopen, or cancel only

---

### BR-015: Self-Approval
If requester is one of the three approvers, auto-apply their approval.

**Behavior:**
- Self-approval happens automatically at submission
- Other two approvers must still approve
- Self-approver may Deny while Pending (requires comment, like any denial)

**Example:** If Ingeborg creates a booking, her approval is auto-applied; Cornelia and Angelika must still approve.

---

### BR-024: First-Action-Wins
For concurrent approval/denial actions on same booking.

**Scenario:** Two approvers simultaneously try to act on a booking.

**Resolution:** First action to persist wins.

**User Feedback:** Late action shows **"Schon erledigt"** with context explaining current status.

**Examples:**
- "Schon erledigt. Die Buchung ist bereits bestätigt."
- "Schon erledigt. {{Partei}} hat bereits abgelehnt – die Anfrage ist jetzt abgelehnt (nicht öffentlich)."

---

## Edit & Modification Rules

### BR-005: Edit While Pending with Approval Impact
**All date edits are logged** with diff information.

**Shorten (within original bounds):**
- Approvals remain unchanged
- Date edit logged in timeline
- Requester notified

**Extend (earlier start or later end):**
- All approvals reset to NoResponse
- Re-approval emails sent to all approvers
- Old→new diff shown in emails
- Date edit logged in timeline

**Party Size Only / Affiliation Only:**
- Approvals remain unchanged
- Changes not logged in timeline

---

### BR-025: First-Name Edit
First name edits allowed anytime.

**Effects:**
- No approval reset (approvals remain)
- Not logged in timeline
- Immediately reflected in displays

**Validation:** Must pass first name validation rules (BR-019).

---

### BR-018: Reopen Guard
Reopen from **Denied** fails if dates conflict with any **Pending** or **Confirmed** booking.

**User Action Required:** User must edit dates in reopen dialog to avoid conflicts before submitting.

**Validation:** Same conflict detection as new booking creation.

---

## Cancel Rules

### BR-006: Cancel While Pending
Requester may cancel Pending booking.

**Action:** Transitions to Canceled → Archive

**Comment:** Not required

**Notifications:** Requester + all three approvers

**Result Page:** Lists notified names

---

### BR-007: Cancel While Confirmed
Requester may cancel Confirmed booking.

**Requirements:**
- Comment required (via confirmed-cancel dialog)
- Dialog shows warning about confirmed status

**Action:** Transitions to Canceled → Archive

**Notifications:** Requester + all three approvers

**Result Page:** Lists notified names

**Dialog Text:**
- **Title:** "Buchung ist bereits bestätigt"
- **Body:** "Diese Buchung von {{RequesterVorname}} ist bereits von allen bestätigt worden. Bist du sicher, dass du sie stornieren willst? Bitte gib einen kurzen Grund an."
- **Buttons:** "Abbrechen" / "Ja, stornieren"

---

### BR-028: Auto-Cleanup of Past Pending Bookings
At **EndDate+1 00:00 Europe/Berlin**, still-Pending bookings are auto-canceled.

**Action:** Transition to Canceled → Archive

**Actor:** System (automated)

**Notifications:** None sent

**Purpose:** Prevent orphaned past Pending bookings.

---

## Notification & Reminder Rules

### BR-009: Weekly Digest
Sunday 09:00 Europe/Berlin, per-approver email.

**Inclusion Criteria:**
- Items where **their party** is **NoResponse**
- Aged **≥5 calendar days** (day-0 rule: submission date is day 0)
- **Future-only** (exclude past-dated items)

**Ordering:** By soonest start date

**Suppression:** If zero items meet criteria, digest is not sent

**Actions Available:**
- Approve: One-click
- Deny: Opens comment form

---

## Token & Access Rules

### BR-010: Tokens and Links
**No expiry:** Tokens never expire

**No revocation:** No mechanism to revoke tokens

**Resend existing:** On recovery request, resend existing token (don't generate new)

**Action links idempotent:** Repeat actions show result page with "Schon erledigt" message

**Always redirect:** Action links always redirect to result page (never error in email click)

---

### BR-021: Soft Cooldown on Link Recovery
60-second cooldown per email/IP on link recovery requests.

**User Feedback:** Neutral success copy (don't reveal if email exists)

**Message during cooldown:** "Bitte warte kurz – wir haben dir deinen persönlichen Link gerade erst gesendet."

**Purpose:**
- Prevent abuse
- Rate limiting
- Protect against enumeration

---

## Localization & UI Rules

### BR-011: German-Only UI
UI displayed in **German only**.

**Tone:** Informal "du" form

**Strings:** May be hardcoded (no i18n infrastructure required initially)

**This Documentation:** English (for technical/engineering handover)

---

### BR-016: Party Size Display
Always show **"n Personen"** format (even for 1 person).

**Examples:**
- 1 person: "1 Personen"
- 5 people: "5 Personen"

**Note:** Grammatically "1 Person" would be correct, but spec requires "1 Personen" for consistency.

---

### BR-017: Maximum Party Size
Party size must be within range.

**Range:** `1 ≤ PartySize ≤ MAX_PARTY_SIZE`

**Default:** MAX_PARTY_SIZE = 10

**Config:** MAX_PARTY_SIZE (configurable)

**Validation:** On create and edit forms

**Error:** "Teilnehmerzahl muss zwischen 1 und {{MAX}} liegen."

---

## Validation Rules

### BR-019: First Name Validation
Valid characters and constraints for requester first name.

**Allowed:**
- Letters (including diacritics: ä, ö, ü, ß, etc.)
- Spaces
- Hyphen (-)
- Apostrophe (')

**Processing:**
- Trimmed (leading/trailing whitespace removed)

**Constraints:**
- Maximum 40 characters
- No emojis
- No newlines
- Must not be empty after trimming

**Error:** "Bitte gib einen gültigen Vornamen an (Buchstaben, Leerzeichen, Bindestrich, Apostroph; max. 40 Zeichen)."

---

### BR-020: Link Detection in Text Fields
Block URLs in Description and Comment fields.

**Blocked Patterns:**
- `http://`
- `https://`
- `www`
- `mailto:`

**Fields Affected:**
- Description (optional field in booking)
- Comments (required for Deny, Cancel-Confirmed)

**Purpose:** Prevent spam and phishing

**Error:** "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden."

---

## Rate Limiting Rules

### BR-012: Rate Limits
Configurable rate limits to prevent abuse.

**Submission Limit:**
- 10 bookings per day per email address

**Per-IP Limit:**
- 30 requests per hour per IP address

**Recovery Limit:**
- 5 link recovery requests per hour per email address

**Soft Cooldown:**
- 60 seconds on link recovery per email/IP (see BR-021)

**All Configurable:** Values can be adjusted via configuration.

---

## Archival & Data Management Rules

### BR-013: Archival & Purge
Archive is hidden storage for Canceled bookings.

**Archive Purge (Monthly Job):**
- Canceled items: Purged when **archived > 1 year**
- Past Confirmed: **Never purged** (kept as history)
- Denied items: Purged once **EndDate < today**

**Purpose:**
- Maintain data hygiene
- Preserve historical Confirmed bookings
- Remove stale Denied and old Canceled items

---

## Approver View Rules

### BR-023: Approver Lists
Approvers have two view buckets.

**Outstanding:**
- Items where **this approver** = NoResponse
- Status = Pending
- Sorted by **LastActivityAt desc** (most recent activity first)

**History:**
- **All items** involving this approver
- **Includes all statuses:** Pending, Confirmed, Denied, Canceled
- Sorted by **LastActivityAt desc**
- Read-only

**Purpose:**
- Outstanding: Action-required items
- History: Complete audit trail of involvement

---

## Email & Retry Rules

### BR-022: Email Retries
Email delivery attempts with retry logic.

**Retry Strategy:**
- Approximately 3 retry attempts
- Exponential backoff between retries
- Failures logged (with correlation IDs)

**Copy Consistency:**
- Email content must remain consistent across retries
- Variables resolved once before retry attempts

**Bounces:**
- Log-only (no user notification)
- No automatic cleanup of bounced addresses

**Purpose:** Handle transient email delivery failures gracefully.

---

## Summary Table

| Rule | Category | Key Concept |
|------|----------|-------------|
| BR-001 | Dates | Inclusive end date |
| BR-002 | Dates | No overlaps |
| BR-003 | Approval | Three fixed approvers |
| BR-004 | Approval | Denial handling |
| BR-005 | Edit | Edit impact on approvals |
| BR-006 | Cancel | Cancel Pending |
| BR-007 | Cancel | Cancel Confirmed |
| BR-009 | Notifications | Weekly digest |
| BR-010 | Access | Token policy |
| BR-011 | UI | German only |
| BR-012 | Security | Rate limits |
| BR-013 | Data | Archival & purge |
| BR-014 | Dates | Past items read-only |
| BR-015 | Approval | Self-approval |
| BR-016 | UI | Party size display |
| BR-017 | Validation | Max party size |
| BR-018 | Edit | Reopen guard |
| BR-019 | Validation | First name validation |
| BR-020 | Validation | Link detection |
| BR-021 | Access | Soft cooldown |
| BR-022 | Notifications | Email retries |
| BR-023 | UI | Approver lists |
| BR-024 | Approval | First-action-wins |
| BR-025 | Edit | First-name edit |
| BR-026 | Dates | Future horizon |
| BR-027 | Validation | Long stay warning |
| BR-028 | Data | Auto-cleanup |
| BR-029 | Dates | First-write-wins |
