# User Journeys

## Overview

This document describes the primary user journeys through the booking system, from submission to resolution.

---

## 5.1 Submit & Approve (Happy Path)

### Flow
1. **Requester submits** booking with:
   - First name
   - Email
   - Date range (start/end)
   - Party size (1–MAX_PARTY_SIZE, default 10)
   - Affiliation (Ingeborg, Cornelia, or Angelika)
   - Optional description

2. **System validation:**
   - `StartDate ≤ today + FUTURE_HORIZON_MONTHS` (default 18 months)
   - If `TotalDays > LONG_STAY_WARN_DAYS` (default 7), show confirm dialog
   - Check for conflicts with Pending/Confirmed bookings (first-write-wins, BR-029)

3. **On successful submission:**
   - Booking created in **Pending** state
   - If requester is an approver, **self-approval auto-applied** (BR-015)
   - Notification emails sent to approvers (except self-approver)
   - Dates blocked on calendar

4. **Approvers receive emails:**
   - Each approver clicks action link or uses personal link
   - Each independently **Approves** (any order)

5. **As approvals come in:**
   - **Not final approval:** Requester notified of progress (who's outstanding)
   - **Final approval:** Status → **Confirmed**
   - Requester receives final confirmation email
   - All approvers notified (suppress intermediate from requester's final approver)

### Guards
- **Future horizon:** `StartDate ≤ today + FUTURE_HORIZON_MONTHS`
- **Long stay warning:** If `TotalDays > LONG_STAY_WARN_DAYS`, require confirmation
- **First-write-wins:** Concurrent submissions resolved by persisted timestamp

### Outcomes
- **Success:** Booking Confirmed, visible on public calendar
- **Conflict:** Error with details (first name + status of conflicting booking)
- **Future horizon exceeded:** Error message
- **User declines long stay:** Submission canceled

---

## 5.2 Deny & Resolve (Pending)

### Flow
1. **Booking in Pending state** (awaiting approvals)

2. **Any approver Denies:**
   - Opens Deny form (requires comment)
   - Submits with reason

3. **System transitions to Denied:**
   - Status → **Denied**
   - **Dates free immediately** (non-blocking, BR-004)
   - **Not public** (hidden from public calendar view)
   - Deny email sent to **everyone** (Requester + all three approvers)

4. **Requester options:**
   - **Reopen:** Edit details and resubmit → back to Pending (see Journey 5.7)
   - **Cancel:** Move to Archive (no further notifications to approvers, see 6.4)

5. **While Denied:**
   - Approvers cannot act (no approve/deny possible)
   - Only requester can Reopen or Cancel
   - Dates available for other bookings

### Key Points
- **Any approver can Deny** (doesn't require all three)
- **Comment required** for deny
- **Immediate effect:** Dates freed right away
- **Non-public:** Not visible on public calendar
- **Everyone notified:** All parties informed of denial

### Outcomes
- **Denied:** Requester must Reopen or Cancel
- **Dates freed:** Available for new bookings immediately

---

## 5.3 Post-Confirm Deny (Warning + Comment)

### Flow
1. **Booking in Confirmed state** (all three approved)

2. **Approver initiates Deny:**
   - Clicks Deny action
   - System shows **warning dialog**

3. **Warning Dialog:**
   - **Title:** "Buchung ist bereits bestätigt"
   - **Body:** "Du möchtest eine bereits bestätigte Buchung ablehnen. Bist du sicher? Bitte gib einen kurzen Grund an."
   - **Buttons:**
     - "Abbrechen" (cancel action)
     - "Ja, ablehnen" (proceed with deny)

4. **If approver cancels:**
   - No change to booking
   - Remains Confirmed

5. **If approver proceeds:**
   - Comment form opens (if not already shown)
   - Approver enters reason
   - Submits denial

6. **System transitions to Denied:**
   - Status → **Denied**
   - **Dates free immediately** (non-blocking)
   - **Not public** (hidden from public calendar)
   - Deny email sent to **everyone** (Requester + all three approvers)

7. **Same requester options as 5.2:**
   - Reopen or Cancel

### Key Points
- **Explicit warning required** to prevent accidental denials
- **Comment still required** (same as Pending deny)
- **Same effects as Pending deny** (dates freed, not public, everyone notified)
- **Intentional friction** to protect confirmed bookings

### Outcomes
- **Denied:** Even confirmed bookings can be denied with warning
- **Requester resolves:** Via Reopen or Cancel

---

## 5.4 Edit While Pending

### Prerequisites
- Booking must be in **Pending** state
- Requester must be on their personal link
- Booking must not be past-dated

### Scenario A: Shorten Within Original Bounds

**Example:** Original booking Jan 1–10, edit to Jan 3–8

**Flow:**
1. Requester opens edit dialog
2. Shortens date range (later start or earlier end)
3. Optionally edits other fields (party size, affiliation, description, first name)
4. Submits

**Effects:**
- **Approvals remain unchanged** (existing approvals kept)
- **Date edit logged** in timeline with diff
- Requester notified of successful edit
- No re-approval emails sent

---

### Scenario B: Extend Beyond Original Bounds

**Example:** Original booking Jan 1–10, edit to Dec 30–Jan 12

**Flow:**
1. Requester opens edit dialog
2. Extends date range (earlier start or later end)
3. Optionally edits other fields
4. Submits

**Effects:**
- **All approvals reset to NoResponse**
- **Date edit logged** in timeline with diff
- **Re-approval emails sent** to all three approvers
- Emails show **old→new diff** clearly
- Booking remains Pending, now awaiting fresh approvals

**Validation:**
- Extended dates must not conflict with other Pending/Confirmed bookings
- If conflict, show error (same as create)

---

### Scenario C: Party Size or Affiliation Only

**Example:** Change party size from 3 to 5, or affiliation from Ingeborg to Cornelia

**Flow:**
1. Requester opens edit dialog
2. Changes **only** party size or affiliation (no date changes)
3. Submits

**Effects:**
- **Approvals remain unchanged**
- **Change not logged** in timeline
- Immediately visible in calendar/details
- No notifications sent

---

### Scenario D: First Name Only

**Example:** Change first name from "Anna" to "Anne"

**Flow:**
1. Requester opens edit dialog
2. Changes **only** first name
3. Submits

**Effects:**
- **Approvals never reset** (per BR-025)
- **Not logged** in timeline
- Immediately visible
- No notifications sent

---

### Scenario E: Multiple Field Changes

**Rules Applied in Order:**
1. **If dates extended:** Reset approvals (trumps all other rules)
2. **Else if dates shortened:** Keep approvals, log date edit
3. **Else:** Party size/affiliation/first name changes keep approvals

**Examples:**
- Extend dates + change party size → Reset approvals (date extension trumps)
- Shorten dates + change affiliation → Keep approvals (shorten + non-date change)
- Change party size + first name (no date change) → Keep approvals

---

## 5.5 Cancel (By Requester)

### Prerequisites
- Requester must be the creator
- Requester on their personal link

### Scenario A: Cancel While Pending

**Flow:**
1. Requester views booking details
2. Clicks "Cancel" or "Stornieren"
3. No comment required
4. Confirms cancellation

**Effects:**
- Status → **Canceled**
- Moved to **Archive** (hidden from all views)
- Dates freed immediately
- Notifications sent to: **Requester + all three approvers**
- Result page lists notified names

---

### Scenario B: Cancel While Confirmed

**Flow:**
1. Requester views booking details (status = Confirmed)
2. Clicks "Cancel" or "Stornieren"
3. **Confirmed-Cancel Dialog shows:**
   - **Title:** "Buchung ist bereits bestätigt"
   - **Body:** "Diese Buchung von {{RequesterVorname}} ist bereits von allen bestätigt worden. Bist du sicher, dass du sie stornieren willst? Bitte gib einen kurzen Grund an."
   - **Buttons:** "Abbrechen" / "Ja, stornieren"

4. **If requester cancels dialog:**
   - No change to booking
   - Remains Confirmed

5. **If requester proceeds:**
   - **Comment required** (reason field shown)
   - Requester enters reason
   - Confirms cancellation

**Effects:**
- Status → **Canceled**
- Moved to **Archive**
- Dates freed immediately
- Notifications sent to: **Requester + all three approvers**
- Result page lists notified names
- Comment included in notifications

---

### Scenario C: Cancel While Denied

**Flow:**
1. Requester views denied booking
2. Clicks "Cancel" or "Stornieren"
3. No comment required (booking already denied)
4. Confirms cancellation

**Effects:**
- Status → **Canceled**
- Moved to **Archive**
- Dates already free (were freed on Deny)
- Notification sent to: **Requester only** (approvers already informed by Deny email, per 6.4)
- No comment required

---

### Key Points
- **Approvers cannot cancel** bookings (only requesters)
- **Comment required only for Confirmed** cancellations
- **Canceled is terminal** (no further actions possible)
- **Moved to Archive** (hidden from all user views)

---

## 5.6 Weekly Digest

### Schedule
**Every Sunday at 09:00 Europe/Berlin**

### Per-Approver Process
1. **System identifies items for this approver:**
   - Booking status = **Pending**
   - **This approver's decision = NoResponse**
   - **Age ≥ 5 calendar days** (day-0 rule: submission date is day 0)
   - **Future-only:** Exclude past-dated bookings (`EndDate < today`)

2. **If zero items:**
   - **Digest suppressed** (no email sent)

3. **If one or more items:**
   - Generate digest email
   - **Order by soonest start date**
   - Include for each item:
     - Requester first name
     - Date range (formatted: "01.–05.08.2025")
     - Party size
     - Description (if provided)
     - Days outstanding
     - **One-click Approve** link
     - **Deny (with comment)** link

4. **Approver actions:**
   - **Approve:** Single click, idempotent
   - **Deny:** Opens comment form, requires reason

### Day-0 Rule
**Submission date is day 0:**
- Submitted Sunday → Day 0
- Monday → Day 1
- ...
- Following Friday → Day 5 (included in next Sunday digest)

### Exclusions
- **Past-dated bookings** excluded (even if Pending and NoResponse)
- **Items already decided** by this approver (Approved or Denied)
- **Non-Pending bookings** (Confirmed, Denied, Canceled)

### No Extra Reminders
Weekly digest is the **only** automated reminder. No daily or other recurring reminders.

---

## 5.7 Reopen (From Denied)

### Prerequisites
- Booking must be in **Denied** state
- Requester must be on their personal link

### Flow
1. **Requester views denied booking:**
   - Sees status: "Abgelehnt"
   - Sees comment from approver who denied
   - Options: "Wieder eröffnen" (Reopen) or "Stornieren" (Cancel)

2. **Requester clicks "Wieder eröffnen":**
   - Opens **edit dialog** (same as normal edit)
   - All fields editable:
     - First name
     - Date range (start/end)
     - Party size
     - Affiliation
     - Description

3. **Requester optionally adjusts:**
   - May change dates (address reason for denial)
   - May change description
   - May change party size or affiliation
   - May change first name

4. **Requester submits:**
   - **System validates:**
     - Dates must not conflict with any **Pending** or **Confirmed** booking (BR-018)
     - All other validations (future horizon, long stay warning, etc.)

5. **If validation fails (conflict):**
   - Error shown: must edit dates to avoid conflicts
   - User must adjust and resubmit

6. **If validation succeeds:**
   - Status → **Pending**
   - **All approvals reset to NoResponse** (fresh start)
   - **Re-approval emails sent** to all three approvers
   - If dates changed, emails show diff
   - If other fields changed, shown in email

7. **Booking now Pending:**
   - Follows normal approval flow (Journey 5.1)
   - Dates blocked again
   - Visible on public calendar

### Key Points (BR-018)
- **Reopen guard:** Fails if dates conflict with Pending/Confirmed
- **Fresh start:** All approvals reset, even from previous rounds
- **Diff in emails:** If dates changed, old→new shown
- **Same validation:** Future horizon, long stay, etc. still apply

### Outcomes
- **Success:** Back to Pending, awaiting approvals
- **Conflict:** Must adjust dates before resubmitting
- **Alternative:** Requester may Cancel instead of Reopen

---

## 5.8 Past Items & Auto-Cleanup

### When Items Become Past
**Definition:** `EndDate < today`

**Timing:** Flip to past status at **00:00 Europe/Berlin** the day after EndDate

**Example:**
- Booking end date: Jan 10
- Becomes past: Jan 11 at 00:00

---

### Past Item Restrictions (BR-014)

**Read-Only:**
- No edits allowed
- No approvals/denials
- No cancellations
- No reopen (even if Denied)

**Visual Indicator:**
- Banner or badge: "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."

**View-Only:**
- Details viewable
- Timeline viewable
- No action buttons shown

---

### Auto-Cleanup of Pending Past-Dated Bookings (BR-028)

**Trigger:** Pending booking where `EndDate < today`

**Timing:** At **EndDate+1 00:00 Europe/Berlin**

**Action:**
- Status → **Canceled**
- Moved to **Archive**
- Actor: **System** (automated)

**Notifications:**
- **None sent** (quiet cleanup)

**Purpose:**
- Prevent orphaned past Pending bookings
- Automatic housekeeping
- No manual intervention required

**Timeline Entry:**
- Event: "Canceled"
- Actor: "System"
- Note: "Auto-canceled past-dated pending booking"

---

### Past Confirmed Bookings
- Remain in system (never auto-canceled)
- Never purged from Archive (per BR-013)
- Visible in approver History
- Viewable by requester via personal link

---

## Journey Summary Table

| Journey | Initial State | Final State | Key Actions | Notifications |
|---------|--------------|-------------|-------------|---------------|
| 5.1 Submit & Approve | — | Confirmed | Submit → Approvals | Approvers; requester (progress + final) |
| 5.2 Deny (Pending) | Pending | Denied | Deny (comment) | Everyone |
| 5.3 Post-Confirm Deny | Confirmed | Denied | Deny (warn + comment) | Everyone |
| 5.4 Edit (Pending) | Pending | Pending | Edit (varied effects) | Context-dependent |
| 5.5 Cancel | Pending/Confirmed/Denied | Canceled | Cancel (comment if Confirmed) | Context-dependent |
| 5.6 Weekly Digest | Pending (NoResponse) | — | Remind approvers | Per-approver digest |
| 5.7 Reopen | Denied | Pending | Reopen (reset approvals) | Approvers |
| 5.8 Auto-Cleanup | Pending (past) | Canceled | System auto-cancel | None |
