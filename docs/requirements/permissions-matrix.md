# Permissions Matrix

## Overview

This document defines who can do what in the system, organized by role and booking state.

---

## Role Definitions

### Requester
Person who created the booking. Authenticated via personal link tied to their email.

### Approver
One of three fixed approvers: Ingeborg, Cornelia, or Angelika. Authenticated via personal link tied to their approver email.

### Viewer
Anyone with the global unlisted URL. No authentication. Read-only access.

---

## Permissions by Role & State

### Requester Permissions

| Action | Pending (Own) | Confirmed (Own) | Denied (Own) | Canceled (Own) |
|--------|--------------|----------------|-------------|----------------|
| **View details** | ✓ | ✓ | ✓ | — |
| **View timeline** | ✓ | ✓ | ✓ | — |
| **View comments** | ✓ Own + approvers' | ✓ Own + approvers' | ✓ Own + approvers' | — |
| **Create booking** | N/A | N/A | N/A | N/A |
| **Edit dates (shorten)** | ✓ Keep approvals | — | — | — |
| **Edit dates (extend)** | ✓ Reset approvals | — | — | — |
| **Edit party size** | ✓ Keep approvals | — | — | — |
| **Edit affiliation** | ✓ Keep approvals | — | — | — |
| **Edit first name** | ✓ Never reset | — | — | — |
| **Edit description** | ✓ Keep approvals | — | — | — |
| **Reopen (via edit)** | — | — | ✓ Reset approvals | — |
| **Cancel (no comment)** | ✓ | — | ✓ | — |
| **Cancel (with comment)** | — | ✓ Required | — | — |
| **Approve** | — | — | — | — |
| **Deny** | — | — | — | — |

**Notes:**
- Edit operations only allowed while Pending (except Reopen from Denied)
- Reopen from Denied uses same edit dialog
- Canceled bookings hidden (moved to Archive)

---

### Approver Permissions

| Action | Pending | Confirmed | Denied | Canceled |
|--------|---------|-----------|--------|----------|
| **View details** | ✓ | ✓ | ✓ | — |
| **View timeline** | ✓ | ✓ | ✓ | — |
| **View comments** | ✓ All | ✓ All | ✓ All | — |
| **Create booking** | N/A | N/A | N/A | N/A |
| **Edit** | — | — | — | — |
| **Approve** | ✓ One-click | — | — | — |
| **Deny (comment)** | ✓ Required | — | — | — |
| **Deny (warn+comment)** | — | ✓ Required | — | — |
| **Cancel** | — | — | — | — |
| **Reopen** | — | — | — | — |

**Notes:**
- Approvers can view all bookings they're involved in (any state except Canceled)
- Approvers cannot cancel or edit bookings (only requesters can)
- While Denied, approvers cannot approve or deny (must wait for Reopen or Cancel)
- Canceled bookings hidden from all views

---

### Viewer Permissions

| Action | Pending | Confirmed | Denied | Canceled |
|--------|---------|-----------|--------|----------|
| **View on calendar** | ✓ | ✓ | — | — |
| **View details** | ✓ Limited | ✓ Limited | — | — |
| **View timeline** | ✓ Actions only | ✓ Actions only | — | — |
| **View comments** | — | — | — | — |
| **View email addresses** | — | — | — | — |
| **Create booking** | — | — | — | — |
| **Edit** | — | — | — | — |
| **Approve/Deny** | — | — | — | — |
| **Cancel** | — | — | — | — |

**Notes:**
- Viewers see first name, party size, status badge, affiliation color
- Denied and Canceled bookings not visible to viewers
- Timeline shows actors + actions only (no comments, no detailed notes)
- No access to PII (email addresses hidden)

---

## Special Cases

### Self-Approval (BR-015)
When requester is also one of the three approvers:

**At Submission:**
- Requester's approval auto-applied
- Other two approvers must still approve
- Requester receives approver notifications (as if separate person)

**While Pending:**
- Requester can Deny in approver role (requires comment)
- Self-deny transitions booking to Denied (like any denial)

**Permissions:**
- Has both Requester and Approver capabilities
- Can edit (as Requester) and deny (as Approver)
- Cannot approve again (already auto-applied)

---

### Past-Dated Bookings (BR-014)
When `EndDate < today` (flip at 00:00 day after EndDate):

**All Roles:**
- View-only access
- No actions allowed (edit, approve, deny, cancel, reopen)
- Timeline and details viewable
- Visual indicator: "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."

**Exception:**
- System auto-cleanup (Pending past-dated → Canceled at EndDate+1 00:00)

---

## Action-Specific Permissions

### Create Booking

**Who:** Anyone with any role (Requester, Approver, or Viewer with knowledge of app URL)

**Requirements:**
- Provide valid email address
- Provide first name
- Select future date range
- Select party size (1–MAX_PARTY_SIZE)
- Select affiliation
- Optional description

**Validation:**
- No conflicts with Pending/Confirmed bookings
- Within future horizon (≤ FUTURE_HORIZON_MONTHS)
- Long stay confirmation if needed
- First-write-wins concurrency

---

### Approve

**Who:** Approvers only (Ingeborg, Cornelia, Angelika)

**When:** Booking status = Pending

**Requirements:**
- Authenticated via approver personal link or action link
- Booking not past-dated
- This approver's decision currently = NoResponse

**Effects:**
- Decision → Approved
- If not final: Requester notified of progress
- If final (3rd approval): Status → Confirmed, everyone notified

**Idempotent:**
- Repeat approve shows "Schon erledigt"

---

### Deny

**Who:** Approvers only

**When:** Booking status = Pending or Confirmed

**Requirements:**
- Authenticated via approver personal link
- Booking not past-dated
- **Comment required** (plaintext, no links, ≤500 chars)
- If Confirmed, **warning dialog confirmation required**

**Effects:**
- Decision → Denied
- Status → Denied
- Dates immediately free (non-blocking)
- Hidden from public calendar
- Notification to **everyone** (Requester + all three approvers)

---

### Edit

**Who:** Requester only (creator of booking)

**When:** Booking status = Pending (or Denied via Reopen)

**Requirements:**
- Authenticated via requester personal link
- Booking not past-dated
- If extending dates, no conflicts with Pending/Confirmed
- If Reopen from Denied, conflict check applies (BR-018)

**Effects:** Vary by edit type (see BR-005, Journey 5.4)

---

### Cancel

**Who:** Requester only

**When:** Booking status = Pending, Confirmed, or Denied

**Requirements:**
- Authenticated via requester personal link
- If Confirmed, **comment required** via confirmed-cancel dialog
- Booking not past-dated

**Effects:**
- Status → Canceled
- Moved to Archive
- Dates freed (if not already)
- Notifications vary by prior state

**Notifications:**
- Pending: Requester + all three approvers
- Confirmed: Requester + all three approvers
- Denied: Requester only

---

### Reopen

**Who:** Requester only

**When:** Booking status = Denied

**Requirements:**
- Authenticated via requester personal link
- Booking not past-dated
- If dates changed, no conflicts with Pending/Confirmed (BR-018)

**Effects:**
- Status → Pending
- All approver decisions → NoResponse (reset)
- Re-approval emails sent to all three approvers
- Dates blocked again
- Visible on public calendar

---

## View Permissions Detail

### Public Calendar (Viewer, Unlisted URL)

**Can See:**
- Pending bookings: first name, party size, status badge, affiliation color
- Confirmed bookings: same as Pending
- Calendar annotations: weekends, holidays (if configured)

**Cannot See:**
- Denied bookings (hidden)
- Canceled bookings (moved to Archive)
- Email addresses (PII)
- Comments from any party
- Full timeline details

---

### Requester Personal Link

**Can See:**
- All own bookings (Pending, Confirmed, Denied)
- Full details: dates, party size, description, affiliation, first name
- Full timeline: all events, actors, actions, date diffs
- Own comments + all approver comments on own bookings
- Current approval status (who's approved, who's outstanding)

**Cannot See:**
- Other requesters' bookings (unless also viewing public calendar)
- Canceled bookings (moved to Archive)
- Email addresses (including own, system doesn't display)

---

### Approver Personal Link

**Can See:**

**Outstanding Tab:**
- All Pending bookings where this approver = NoResponse
- Full details for each
- All comments
- Action buttons (Approve one-click, Deny with comment)

**History Tab:**
- All bookings involving this approver (Pending, Confirmed, Denied)
- Full details for each
- All comments
- Full timeline
- Read-only (no action buttons in History)

**Cannot See:**
- Canceled bookings (moved to Archive)
- Bookings not involving this approver (no visibility into other approval sets)

---

## Email & Privacy Permissions

### Email Addresses (PII)

**Stored:**
- Requester email (immutable, normalized lowercase)
- Approver emails (fixed set of three)

**Never Displayed:**
- In any UI (requester, approver, viewer)
- On public calendar
- In booking details
- In timeline

**Only Used For:**
- Sending notifications
- Authenticating personal links (token tied to email)
- Uniqueness validation

---

### Comments

**Requester Can See:**
- Own comments (if any)
- Approver comments on own bookings (Deny reasons, Cancel reasons)

**Approver Can See:**
- All comments on bookings involving them
- Deny reasons from other approvers
- Cancel reasons from requesters

**Viewer Cannot See:**
- Any comments from any party

---

## Rate Limiting (BR-012)

### Applies to All Roles

**Submission:**
- 10 bookings per day per email address

**Per-IP:**
- 30 requests per hour per IP

**Link Recovery:**
- 5 requests per hour per email address
- 60-second soft cooldown per email/IP

---

## Permission Enforcement

### Authentication
- **Personal links:** Signed tokens, no expiry, no revocation
- **Action links:** One-time intent, idempotent, redirect to result page
- **Viewer:** No authentication (unlisted URL)

### Authorization
- Role determined by link type (requester vs approver)
- No session management
- Stateless token validation

### Validation
- State checks (can't approve if already Confirmed)
- Ownership checks (requester can only edit/cancel own bookings)
- Timing checks (no actions on past-dated bookings)
- Conflict checks (first-write-wins, reopen guard)

---

## Permissions Summary Table

| Capability | Requester | Approver | Viewer |
|-----------|-----------|----------|--------|
| View public calendar | ✓ | ✓ | ✓ |
| View own bookings | ✓ All states | — | — |
| View involved bookings | — | ✓ All states | — |
| View comments | ✓ Own + approvers' | ✓ All | — |
| View email addresses | — | — | — |
| Create booking | ✓ | ✓ | — |
| Edit booking | ✓ Own (Pending) | — | — |
| Approve | — | ✓ (Pending) | — |
| Deny (Pending) | — | ✓ Comment | — |
| Deny (Confirmed) | — | ✓ Warn+comment | — |
| Cancel | ✓ Own | — | — |
| Reopen | ✓ Own (from Denied) | — | — |
| Access Archive | — | — | — |

**Legend:**
- ✓ = Allowed
- — = Not allowed
- Conditions in parentheses
