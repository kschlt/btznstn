# Acceptance Criteria

## Overview

Business-verifiable acceptance criteria for each major use case. These criteria define what "done" looks like for implementation.

---

## UC-001: Create Booking

### Criteria

**AC-001.1: Conflict Detection**
- **Given** dates overlap with existing Pending booking
- **When** user submits booking
- **Then** system rejects with conflict error
- **And** error shows conflicting booking's **first name + status**

**AC-001.2: Conflict with Confirmed**
- **Given** dates overlap with existing Confirmed booking
- **When** user submits booking
- **Then** system rejects with conflict error
- **And** error shows conflicting booking's **first name + status**

**AC-001.3: No Conflict with Denied**
- **Given** dates overlap with Denied booking
- **When** user submits booking
- **Then** system accepts submission
- **And** booking created successfully

**AC-001.4: Future Horizon Validation**
- **Given** start date is `> today + FUTURE_HORIZON_MONTHS` (default 18)
- **When** user submits booking
- **Then** system rejects with horizon error
- **And** error message shows maximum months allowed

**AC-001.5: End Before Start Validation**
- **Given** end date is before start date
- **When** user submits booking
- **Then** system rejects with date order error
- **And** error: "Ende darf nicht vor dem Start liegen."

**AC-001.6: Email Validation**
- **Given** email is invalid per §9 validation rules
- **When** user submits booking
- **Then** system rejects with email error
- **And** error: "Bitte gib eine gültige E-Mail-Adresse an."

**AC-001.7: Long Stay Warning**
- **Given** `TotalDays > LONG_STAY_WARN_DAYS` (default 7)
- **When** user submits booking
- **Then** system shows confirmation dialog
- **And** submission continues only if user confirms

**AC-001.8: Successful Submission**
- **Given** all validations pass
- **When** user submits booking
- **Then** system creates booking with status = Pending
- **And** computes `TotalDays = EndDate - StartDate + 1`
- **And** if requester is approver, auto-applies self-approval (BR-015)
- **And** sends notification emails to non-self approvers
- **And** calendar shows booking with "n Personen" display
- **And** dates blocked for future bookings

**AC-001.9: First-Write-Wins Concurrency**
- **Given** two users simultaneously submit bookings for same dates
- **When** both submissions reach server
- **Then** first persisted submission wins
- **And** second submission receives conflict error
- **And** conflict details include winner's first name + status

---

## UC-002: Approve / Deny (Pending)

### Approve Criteria

**AC-002.1: First Approval**
- **Given** booking is Pending with all NoResponse
- **When** one approver clicks Approve
- **Then** that approver's decision → Approved
- **And** booking remains Pending
- **And** requester notified with outstanding list

**AC-002.2: Second Approval**
- **Given** booking has one approval, one NoResponse
- **When** second approver clicks Approve
- **Then** that approver's decision → Approved
- **And** booking remains Pending
- **And** requester notified with last outstanding approver

**AC-002.3: Final Approval**
- **Given** booking has two approvals, one NoResponse
- **When** third approver clicks Approve
- **Then** that approver's decision → Approved
- **And** booking status → Confirmed
- **And** requester receives confirmation email
- **And** all three approvers notified (requester's intermediate suppressed)

**AC-002.4: Approve Idempotent**
- **Given** approver already approved
- **When** approver clicks Approve again
- **Then** system shows "Schon erledigt" result page
- **And** no duplicate notifications sent

---

### Deny Criteria

**AC-002.5: Deny Requires Comment**
- **Given** booking is Pending
- **When** approver clicks Deny without comment
- **Then** system shows error: "Bitte gib einen kurzen Grund an."
- **And** deny action does not proceed

**AC-002.6: Successful Deny**
- **Given** booking is Pending
- **When** approver submits Deny with comment
- **Then** that approver's decision → Denied
- **And** booking status → Denied
- **And** dates immediately free (non-blocking)
- **And** booking hidden from public calendar
- **And** notification sent to **everyone** (Requester + all three approvers)
- **And** email includes deny reason

**AC-002.7: Requester Options After Deny**
- **Given** booking is Denied
- **When** requester views details
- **Then** sees status "Abgelehnt"
- **And** sees deny comment
- **And** sees "Wieder eröffnen" button
- **And** sees "Stornieren" button

---

## UC-003: Deny (Confirmed)

### Criteria

**AC-003.1: Warning Dialog Shows**
- **Given** booking is Confirmed
- **When** approver clicks Deny
- **Then** warning dialog appears
- **And** title: "Buchung ist bereits bestätigt"
- **And** body: "Du möchtest eine bereits bestätigte Buchung ablehnen. Bist du sicher? Bitte gib einen kurzen Grund an."
- **And** buttons: "Abbrechen" / "Ja, ablehnen"

**AC-003.2: User Cancels Warning**
- **Given** warning dialog is open
- **When** user clicks "Abbrechen"
- **Then** dialog closes
- **And** booking remains Confirmed
- **And** no changes made

**AC-003.3: User Confirms Deny**
- **Given** warning dialog is open
- **When** user clicks "Ja, ablehnen"
- **Then** comment form shown (if not already)
- **And** user enters reason
- **And** submits

**AC-003.4: Successful Post-Confirm Deny**
- **Given** user confirmed warning and provided comment
- **When** deny submitted
- **Then** booking status → Denied
- **And** dates immediately free (non-blocking)
- **And** booking hidden from public calendar
- **And** notification sent to **everyone**
- **And** email includes deny reason

---

## UC-004: Edit While Pending

### Shorten Dates

**AC-004.1: Shorten Within Bounds**
- **Given** booking is Pending (e.g., Jan 1–10)
- **And** has existing approvals
- **When** requester shortens dates (e.g., to Jan 3–8)
- **Then** booking dates updated
- **And** existing approvals remain unchanged
- **And** date edit logged in timeline with diff
- **And** requester notified of change
- **And** no re-approval emails sent

---

### Extend Dates

**AC-004.2: Extend Earlier Start**
- **Given** booking is Pending (e.g., Jan 1–10)
- **And** has existing approvals
- **When** requester moves start earlier (e.g., to Dec 28–10)
- **Then** booking dates updated
- **And** all approvals reset to NoResponse
- **And** date edit logged in timeline with diff
- **And** re-approval emails sent to all three approvers
- **And** emails show old→new diff

**AC-004.3: Extend Later End**
- **Given** booking is Pending (e.g., Jan 1–10)
- **And** has existing approvals
- **When** requester moves end later (e.g., to Jan 1–15)
- **Then** booking dates updated
- **And** all approvals reset to NoResponse
- **And** date edit logged in timeline with diff
- **And** re-approval emails sent to all three approvers
- **And** emails show old→new diff

**AC-004.4: Extend with Conflict**
- **Given** booking is Pending
- **When** requester extends dates into conflict with Pending/Confirmed
- **Then** system rejects edit
- **And** shows conflict error with first name + status

---

### Other Edits

**AC-004.5: Party Size Only**
- **Given** booking is Pending with approvals
- **When** requester changes only party size
- **Then** party size updated
- **And** existing approvals remain unchanged
- **And** change not logged in timeline
- **And** immediately visible in calendar/details

**AC-004.6: Affiliation Only**
- **Given** booking is Pending with approvals
- **When** requester changes only affiliation
- **Then** affiliation updated (color changes)
- **And** existing approvals remain unchanged
- **And** change not logged in timeline
- **And** immediately visible

**AC-004.7: First Name Only**
- **Given** booking is Pending with approvals
- **When** requester changes only first name
- **Then** first name updated
- **And** existing approvals never reset
- **And** change not logged in timeline
- **And** immediately visible

---

## UC-005: Cancel (By Requester)

### Cancel Pending

**AC-005.1: Cancel Without Comment**
- **Given** booking is Pending
- **When** requester clicks Cancel and confirms
- **Then** booking status → Canceled
- **And** moved to Archive (hidden)
- **And** dates freed
- **And** notifications sent to: Requester + all three approvers
- **And** result page lists notified names
- **And** no comment required

---

### Cancel Confirmed

**AC-005.2: Confirmed-Cancel Dialog Shows**
- **Given** booking is Confirmed
- **When** requester clicks Cancel
- **Then** dialog appears
- **And** title: "Buchung ist bereits bestätigt"
- **And** body: "Diese Buchung von {{RequesterVorname}} ist bereits von allen bestätigt worden. Bist du sicher, dass du sie stornieren willst? Bitte gib einen kurzen Grund an."
- **And** buttons: "Abbrechen" / "Ja, stornieren"

**AC-005.3: User Cancels Dialog**
- **Given** confirmed-cancel dialog is open
- **When** user clicks "Abbrechen"
- **Then** dialog closes
- **And** booking remains Confirmed

**AC-005.4: Successful Confirmed Cancel**
- **Given** user confirmed and provided comment
- **When** cancel submitted
- **Then** booking status → Canceled
- **And** moved to Archive (hidden)
- **And** dates freed
- **And** notifications sent to: Requester + all three approvers
- **And** result page lists notified names
- **And** comment included in notifications

---

### Cancel Denied

**AC-005.5: Cancel Denied Booking**
- **Given** booking is Denied
- **When** requester clicks Cancel and confirms
- **Then** booking status → Canceled
- **And** moved to Archive (hidden)
- **And** notification sent to: **Requester only**
- **And** approvers not notified (already informed by Deny)
- **And** no comment required

---

## UC-006: Reopen (From Denied)

### Criteria

**AC-006.1: Reopen Without Date Change**
- **Given** booking is Denied
- **When** requester clicks "Wieder eröffnen"
- **And** submits without changing dates
- **Then** booking status → Pending
- **And** all approver decisions → NoResponse
- **And** re-approval emails sent to all three approvers
- **And** dates blocked again
- **And** visible on public calendar

**AC-006.2: Reopen With Date Change**
- **Given** booking is Denied
- **When** requester reopens and changes dates
- **Then** booking status → Pending
- **And** all approver decisions → NoResponse
- **And** re-approval emails sent with date diff (old→new)
- **And** new dates blocked
- **And** visible on public calendar

**AC-006.3: Reopen Conflict Validation (BR-018)**
- **Given** booking is Denied
- **When** requester reopens with dates conflicting Pending/Confirmed
- **Then** system rejects reopen
- **And** shows conflict error: must adjust dates
- **And** user must edit dates to proceed

**AC-006.4: Reopen Success Outcomes**
- **Given** reopen succeeded
- **Then** booking follows normal approval flow
- **And** visible in approver Outstanding lists
- **And** included in weekly digest (if aged ≥5 days)
- **And** dates blocked from other bookings

---

## UC-007: Weekly Digest

### Criteria

**AC-007.1: Inclusion - NoResponse ≥5 Days**
- **Given** booking is Pending with approver = NoResponse
- **And** submission date is ≥5 calendar days ago (day-0 rule)
- **And** booking is future-dated
- **When** digest runs Sunday 09:00 Europe/Berlin
- **Then** booking included in this approver's digest

**AC-007.2: Exclusion - Recent Submission**
- **Given** booking submitted < 5 calendar days ago
- **When** digest runs
- **Then** booking not included

**AC-007.3: Exclusion - Past Dated**
- **Given** booking is past-dated (`EndDate < today`)
- **And** meets age criteria
- **When** digest runs
- **Then** booking not included (future-only)

**AC-007.4: Exclusion - Already Decided**
- **Given** approver already Approved or Denied
- **When** digest runs
- **Then** booking not included for this approver

**AC-007.5: Ordering - Soonest Start**
- **Given** multiple bookings meet inclusion criteria
- **When** digest generated
- **Then** bookings ordered by soonest start date
- **And** earliest start date appears first

**AC-007.6: Suppression - Zero Items**
- **Given** no bookings meet inclusion criteria for this approver
- **When** digest would run
- **Then** digest not sent to this approver

**AC-007.7: Actions Available**
- **Given** digest received
- **When** approver opens email
- **Then** sees each item with:
  - One-click Approve link
  - Deny link (opens comment form)
- **And** clicking Approve → immediate approval (idempotent)
- **And** clicking Deny → comment form → submission

---

## UC-008: Past Items & Auto-Cleanup

### Past Item Restrictions

**AC-008.1: Past Definition**
- **Given** booking end date is Jan 10
- **When** clock reaches Jan 11 00:00 Europe/Berlin
- **Then** booking becomes past-dated

**AC-008.2: Read-Only Access**
- **Given** booking is past-dated
- **When** any actor views booking
- **Then** details viewable
- **And** timeline viewable
- **And** no action buttons shown
- **And** banner: "Dieser Eintrag liegt in der Vergangenheit und kann nicht mehr geändert werden."

**AC-008.3: No Operations**
- **Given** booking is past-dated
- **When** user attempts edit, approve, deny, cancel, or reopen
- **Then** system prevents action
- **And** shows past-dated error

---

### Auto-Cleanup

**AC-008.4: Pending Past-Dated Auto-Cancel**
- **Given** booking is Pending with `EndDate = Jan 10`
- **When** system job runs Jan 11 00:00 Europe/Berlin
- **Then** booking status → Canceled
- **And** moved to Archive
- **And** timeline event: Canceled by System
- **And** no notifications sent

**AC-008.5: Confirmed Past Not Auto-Canceled**
- **Given** booking is Confirmed and past-dated
- **When** system job runs
- **Then** booking remains Confirmed
- **And** not moved to Archive
- **And** kept for history (per BR-013)

**AC-008.6: Denied Past-Dated Handling**
- **Given** booking is Denied and past-dated
- **When** system job runs
- **Then** booking status unchanged (remains Denied)
- **And** purged from database once past (per BR-013)

---

## General System Acceptance Criteria

### Validation

**AC-GEN-001: Email Format**
- **Given** email input
- **When** validated
- **Then** must match validation rules per §9
- **And** reject if invalid with error copy

**AC-GEN-002: First Name Validation (BR-019)**
- **Given** first name input
- **When** validated
- **Then** allow only: letters (incl. diacritics), spaces, hyphen, apostrophe
- **And** trim whitespace
- **And** max 40 characters
- **And** reject if invalid

**AC-GEN-003: Party Size Validation (BR-017)**
- **Given** party size input
- **When** validated
- **Then** must be integer 1 to MAX_PARTY_SIZE (default 10)
- **And** reject if out of range

**AC-GEN-004: Link Detection (BR-020)**
- **Given** description or comment input
- **When** validated
- **Then** reject if contains: http://, https://, www, mailto:
- **And** error: "Links sind hier nicht erlaubt. Bitte Text ohne Links verwenden."

---

### Notifications

**AC-GEN-005: Email Delivery**
- **Given** notification trigger
- **When** email sent
- **Then** retry up to ~3 times with backoff
- **And** log failures with correlation ID
- **And** copy remains consistent across retries

**AC-GEN-006: Email Recipients - Deny**
- **Given** booking is Denied (Pending or Confirmed)
- **When** deny notification sent
- **Then** recipients = Requester + all three approvers
- **And** email includes deny reason

**AC-GEN-007: Email Recipients - Cancel Pending/Confirmed**
- **Given** requester cancels Pending or Confirmed booking
- **When** cancel notification sent
- **Then** recipients = Requester + all three approvers
- **And** result page lists notified names

**AC-GEN-008: Email Recipients - Cancel Denied**
- **Given** requester cancels Denied booking
- **When** cancel notification sent
- **Then** recipient = Requester only
- **And** approvers not notified

---

### Privacy & Access

**AC-GEN-009: Email Never Displayed**
- **Given** any UI screen (calendar, details, timeline)
- **When** user views content
- **Then** no email addresses displayed
- **And** only first names shown

**AC-GEN-010: Denied Not Public**
- **Given** booking is Denied
- **When** viewer accesses public calendar
- **Then** booking not visible
- **And** dates appear free

**AC-GEN-011: Canceled Not Visible**
- **Given** booking is Canceled
- **When** any actor views any screen
- **Then** booking not visible (moved to Archive)

---

### Concurrency

**AC-GEN-012: First-Action-Wins**
- **Given** two approvers act on same booking simultaneously
- **When** both actions reach server
- **Then** first persisted action wins
- **And** second action sees "Schon erledigt" result page
- **And** result page includes context

---

### Calendar Display

**AC-GEN-013: Party Size Display (BR-016)**
- **Given** booking with party size = 1
- **When** displayed on calendar
- **Then** shows "1 Personen" (not "1 Person")

**AC-GEN-014: Party Size Display (BR-016)**
- **Given** booking with party size = 5
- **When** displayed on calendar
- **Then** shows "5 Personen"

---

## Acceptance Testing Notes

### Test Data Setup
- Create three fixed approvers: Ingeborg, Cornelia, Angelika
- Configure affiliation colors per specification
- Set default config values (FUTURE_HORIZON_MONTHS=18, LONG_STAY_WARN_DAYS=7, MAX_PARTY_SIZE=10)

### Test Execution
- All German UI copy must match specification exactly
- Date format: "01.–05.08.2025"
- Mobile testing on iPhone 8 class devices minimum
- Verify email copy matches templates in notifications.md

### Success Criteria
- All AC criteria pass
- No regressions in existing functionality
- German UI displays correctly
- Emails deliver and display correctly
- Mobile experience smooth on target devices
