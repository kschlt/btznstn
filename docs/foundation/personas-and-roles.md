# Personas & Roles

## Overview

The system has three primary personas, each with specific capabilities and access patterns.

## Personas

### Requester

**Description:** Proposes bookings and manages their own requests.

**Capabilities:**
- Create new booking requests with date range, party size, description, and affiliation
- Edit own Pending bookings (with specific rules)
- Cancel own bookings (Pending: no comment required; Confirmed: comment required)
- Reopen Denied bookings back to Pending status (resets all approvals)
- View timeline of all actions on their bookings
- Receive email notifications for approval decisions

**Special Cases:**
- If requester is also one of the three approvers, **self-approval is auto-applied**
- Other two approvers must still approve
- Requester may Deny their own Pending booking in their approver role (comment required)

**Access:**
- Via personal link sent to their email
- Personal link aggregates all their booking requests
- No login required

---

### Approver (Fixed)

**Description:** One of three fixed decision-makers: **Ingeborg**, **Cornelia**, **Angelika**.

**Capabilities:**
- Approve bookings while Pending (one-click from email or via app)
- Deny bookings while Pending (requires comment)
- Deny Confirmed bookings (requires warning confirmation + comment)
- View all bookings they're involved in (Outstanding + History)
- Access comments from all parties
- Receive weekly digest of outstanding approvals

**Constraints:**
- **Cannot cancel** bookings (only requesters can cancel)
- **Cannot edit** booking details
- **First decisive action wins** - if booking already processed, see "Schon erledigt" message

**Decision Rules:**
- All three approvers must Approve for Confirmed status
- Any single Deny transitions to Denied status
- Approvals are independent (any order)
- Deny on Confirmed requires explicit warning dialog

**Access:**
- Via personal link tied to their approver email
- Action links in emails for one-click approve
- Deny action requires opening comment form

---

### Viewer (Unlisted)

**Description:** Anyone with the global unlisted URL (not indexed by search engines).

**Capabilities:**
- View public calendar with bookings
- See first name, party size, status, affiliation color for each booking
- Open details for Pending and Confirmed bookings
- Navigate between months/year views

**Restrictions:**
- **Cannot see Denied or Canceled bookings** (hidden from public view)
- **Cannot see comments** from any party
- **Cannot see email addresses**
- **Cannot create or edit** bookings
- Read-only access

**Access:**
- Via global unlisted URL
- No personal identification
- No authentication required

---

## Affiliation

**Definition:** Which fixed party a booking is visually associated with (color coding in calendar legend).

**Important:** Affiliation is **visual only**. All three approvers (Ingeborg, Cornelia, Angelika) are **still required to approve** regardless of affiliation.

**Visual Representation:**
- Each affiliation has a distinct color
- Displayed in calendar cells
- Shown in booking details
- Included in legend

**Configuration:**
- Ingeborg: `#C1DBE3`
- Cornelia: `#C7DFC5`
- Angelika: `#DFAEB4`

---

## Role Access Summary

| Capability | Requester | Approver | Viewer |
|-----------|-----------|----------|--------|
| View public calendar | ✓ | ✓ | ✓ |
| View own bookings | ✓ | — | — |
| View comments | Own only | All | — |
| Create booking | ✓ | ✓ | — |
| Edit booking | Own (Pending) | — | — |
| Approve | — | ✓ | — |
| Deny | — | ✓ | — |
| Cancel | Own | — | — |
| Reopen (from Denied) | Own | — | — |

---

## Access Patterns

### Personal Links
- Unique per email address
- No expiry
- Resendable via "Lost my link" flow
- Role determined by link type (requester vs approver)

### Action Links
- One-time use intent, but idempotent
- Embedded in notification emails
- Direct approve/deny actions
- Redirect to result page after action

### Global Unlisted URL
- Same URL for all viewers
- Not indexed by search engines
- No authentication
- Read-only public calendar view
