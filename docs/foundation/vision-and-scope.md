# Vision & Scope

## Overview

A simple shared **booking calendar** for multi-day, whole-day requests. Every booking requires **three independent approvals** from **Ingeborg, Cornelia, Angelika**.

## Core Vision

Create a booking system that prioritizes:

- **Clarity:** Visual availability, unmistakable statuses, full per-request timeline
- **Email-first:** Act from emails via secure links; no accounts/logins required
- **Conflict prevention:** No overlaps (see blockers); inclusive end-date semantics
- **Denial resolution:** Denied is non-blocking and not public; requester may Reopen or Cancel
- **Privacy:** Public calendar shows first name + description only; emails never shown
- **Mobile simplicity:** Large tap targets, high contrast, no hover; single-tap to details

## Language & UI

- **End-user UI:** German (informal **du** tone; strings may be hardcoded)
- **This documentation:** English for solution/design/engineering/QA handover

## Scope

- **Booking model:** Whole-day bookings only
- **Approvers:** Three fixed approvers (Ingeborg, Cornelia, Angelika)
- **Access model:** Email-first, zero-login (role-by-link)
- **Privacy:** First name only; emails never displayed
- **Mobile target:** Must work smoothly on older/smaller phones (min viewport ≈ iPhone 8 class)

## Readiness

Complete; implementation-ready.

## Key Principles

### Email-First, Zero-Login
- All interactions possible via email links
- No user accounts or login system
- Role determined by secure link tokens
- Personal links aggregate all requests for a user

### Privacy by Design
- Emails are PII, never displayed in UI
- Public calendar shows only first names
- Denied/Canceled bookings not visible publicly
- Comments visible only to relevant parties

### Conflict Prevention
- No overlapping bookings allowed
- Pending and Confirmed bookings block dates
- Denied bookings immediately free dates
- First-write-wins for concurrent submissions

### Mobile-First Experience
- Designed for iPhone 8 class devices and up
- Large touch targets
- High contrast
- No hover-dependent interactions
- Single-tap navigation

## Out of Scope

This system intentionally does NOT include:

- User account management or authentication
- Partial-day or hourly bookings
- Dynamic approver assignment
- Public legal pages (small trusted group; owner accepts risk)
- Formal availability SLA (personal/small-group use)
- Data residency requirements
- Quiet hours for notifications
