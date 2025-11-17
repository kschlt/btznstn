# Betzenstein Booking & Approval App — Documentation

## Overview

This documentation provides a complete specification for the Betzenstein booking and approval application. It is structured to be AI-friendly and serves as the foundation for solution design, architecture, and implementation.

**Project:** Booking calendar requiring three independent approvals

**Status:** Requirements complete; implementation-ready

**Language:** End-user UI in German (informal "du" tone); documentation in English

---

## What This Application Does

A shared booking calendar for multi-day, whole-day requests. Every booking requires approval from three fixed approvers (Ingeborg, Cornelia, Angelika). Key features:

- **Email-first access:** No accounts/logins; role-by-link via secure tokens
- **Three-approver workflow:** All three must approve for confirmation
- **Conflict prevention:** No overlapping bookings (Pending/Confirmed)
- **Denial resolution:** Denied bookings free dates immediately; requester can Reopen or Cancel
- **Privacy by design:** First names only; emails never displayed
- **Mobile-first:** Works smoothly on iPhone 8 class devices and up

---

## Documentation Structure

```
/docs/
├── README.md                      # This file (navigation guide)
│
├── /foundation/                   # Core concepts (rarely change)
│   ├── vision-and-scope.md       # Vision, goals, scope, principles
│   ├── personas-and-roles.md     # User personas, capabilities, access
│   ├── glossary.md                # Terms, concepts, definitions
│   └── business-rules.md          # BR-001 to BR-029 (numbered, referenced)
│
├── /requirements/                 # What the system must do
│   ├── functional-overview.md    # Core functional requirements
│   ├── user-journeys.md           # Step-by-step user flows
│   ├── states-and-transitions.md # State machine, transitions
│   ├── permissions-matrix.md      # Role-based permissions
│   └── acceptance-criteria.md     # Verifiable acceptance criteria
│
├── /specification/                # Detailed technical specs
│   ├── ui-screens.md              # Screen layouts, interactions
│   ├── notifications.md           # Email copy, triggers, recipients
│   ├── data-model.md              # Entities, properties, relationships
│   ├── error-handling.md          # Error messages, empty states (German)
│   └── configuration.md           # System configuration parameters
│
└── /constraints/                  # Boundaries and limits
    ├── non-functional.md          # Performance, security, privacy
    └── technical-constraints.md   # Platform, compatibility, tech stack
```

---

## Quick Navigation

### I want to understand...

**...the vision and goals**
→ [`foundation/vision-and-scope.md`](foundation/vision-and-scope.md)

**...who the users are**
→ [`foundation/personas-and-roles.md`](foundation/personas-and-roles.md)

**...key terms and definitions**
→ [`foundation/glossary.md`](foundation/glossary.md)

**...the business rules**
→ [`foundation/business-rules.md`](foundation/business-rules.md)

---

### I want to know how to...

**...submit and approve a booking**
→ [`requirements/user-journeys.md`](requirements/user-journeys.md) §5.1

**...handle denials**
→ [`requirements/user-journeys.md`](requirements/user-journeys.md) §5.2, §5.3

**...edit bookings**
→ [`requirements/user-journeys.md`](requirements/user-journeys.md) §5.4

**...cancel bookings**
→ [`requirements/user-journeys.md`](requirements/user-journeys.md) §5.5

**...reopen denied bookings**
→ [`requirements/user-journeys.md`](requirements/user-journeys.md) §5.7

---

### I want to implement...

**...the user interface**
→ [`specification/ui-screens.md`](specification/ui-screens.md)

**...email notifications**
→ [`specification/notifications.md`](specification/notifications.md)

**...the database**
→ [`specification/data-model.md`](specification/data-model.md)

**...error handling**
→ [`specification/error-handling.md`](specification/error-handling.md)

**...system configuration**
→ [`specification/configuration.md`](specification/configuration.md)

---

### I want to understand...

**...functional requirements**
→ [`requirements/functional-overview.md`](requirements/functional-overview.md)

**...state transitions**
→ [`requirements/states-and-transitions.md`](requirements/states-and-transitions.md)

**...permissions**
→ [`requirements/permissions-matrix.md`](requirements/permissions-matrix.md)

**...acceptance criteria**
→ [`requirements/acceptance-criteria.md`](requirements/acceptance-criteria.md)

---

### I want to know about...

**...performance and security**
→ [`constraints/non-functional.md`](constraints/non-functional.md)

**...technical constraints**
→ [`constraints/technical-constraints.md`](constraints/technical-constraints.md)

**...mobile compatibility**
→ [`constraints/technical-constraints.md`](constraints/technical-constraints.md) (Mobile Device Support section)

**...German copy requirements**
→ [`specification/notifications.md`](specification/notifications.md) + [`specification/error-handling.md`](specification/error-handling.md)

---

## Key Reference Points

### Business Rules (BR-001 to BR-029)

All business rules are documented in [`foundation/business-rules.md`](foundation/business-rules.md). They are numbered for easy reference throughout the documentation.

**Critical rules:**
- **BR-001:** Inclusive end date
- **BR-002:** No overlaps
- **BR-003:** Three fixed approvers
- **BR-004:** Denial handling
- **BR-005:** Edit impact on approvals
- **BR-009:** Weekly digest
- **BR-010:** Token policy (no expiry, no revocation)
- **BR-015:** Self-approval
- **BR-024:** First-action-wins
- **BR-029:** First-write-wins

---

### German Copy

All German copy (UI text, emails, errors) is specified in:
- **Email notifications:** [`specification/notifications.md`](specification/notifications.md)
- **Error messages:** [`specification/error-handling.md`](specification/error-handling.md)
- **UI screens:** [`specification/ui-screens.md`](specification/ui-screens.md)

**Tone:** Informal "du" (not "Sie")

**Date format:** `DD.–DD.MM.YYYY` (e.g., "01.–05.08.2025")

---

### State Machine

The booking lifecycle is documented in [`requirements/states-and-transitions.md`](requirements/states-and-transitions.md).

**States:**
- **Pending** → Awaiting approvals (blocks dates)
- **Confirmed** → All approved (blocks dates)
- **Denied** → Any deny (non-blocking, not public)
- **Canceled** → Terminal state (Archive)

**Diagram:** See state diagram in states-and-transitions.md

---

### Data Model

Complete data model in [`specification/data-model.md`](specification/data-model.md).

**Core entities:**
- BOOKING
- APPROVER_PARTY (3 fixed)
- APPROVAL (per approver, per booking)
- TIMELINE_EVENT (audit log)

---

## For Different Audiences

### For Claude Code AI Agents

**Start here:** [`/claude/README.md`](../claude/README.md)

This guide explains:
- How to use this documentation
- Key business rules quick reference
- Common pitfalls
- German copy guidelines
- Quick start checklist

**Workflow guide:** [`/claude/documentation-workflow.md`](../claude/documentation-workflow.md)

---

### For Solution Architects

**Read first:**
1. [`foundation/vision-and-scope.md`](foundation/vision-and-scope.md) — Understand the vision
2. [`requirements/functional-overview.md`](requirements/functional-overview.md) — Core requirements
3. [`constraints/non-functional.md`](constraints/non-functional.md) — Quality attributes
4. [`constraints/technical-constraints.md`](constraints/technical-constraints.md) — Platform constraints

**Then design:**
- Architecture patterns
- Technology stack
- Deployment strategy
- Security approach

---

### For Developers

**Read first:**
1. [`foundation/glossary.md`](foundation/glossary.md) — Learn the terminology
2. [`foundation/business-rules.md`](foundation/business-rules.md) — Understand the rules
3. [`requirements/user-journeys.md`](requirements/user-journeys.md) — See the flows
4. [`specification/data-model.md`](specification/data-model.md) — Database schema

**During implementation:**
- Reference [`requirements/acceptance-criteria.md`](requirements/acceptance-criteria.md)
- Use exact German copy from [`specification/notifications.md`](specification/notifications.md) and [`specification/error-handling.md`](specification/error-handling.md)
- Follow state machine in [`requirements/states-and-transitions.md`](requirements/states-and-transitions.md)

---

### For QA Engineers

**Read first:**
1. [`requirements/user-journeys.md`](requirements/user-journeys.md) — Test scenarios
2. [`requirements/acceptance-criteria.md`](requirements/acceptance-criteria.md) — Verification criteria
3. [`specification/error-handling.md`](specification/error-handling.md) — Error scenarios

**Test focus:**
- All user journeys (§5.1–5.8)
- All acceptance criteria (UC-001 to UC-008)
- German copy correctness
- Mobile compatibility (iPhone 8 class minimum)
- State transitions
- Permissions enforcement

---

### For Product Owners

**Read first:**
1. [`foundation/vision-and-scope.md`](foundation/vision-and-scope.md) — Vision and scope
2. [`foundation/personas-and-roles.md`](foundation/personas-and-roles.md) — Users
3. [`requirements/user-journeys.md`](requirements/user-journeys.md) — User experience
4. [`specification/ui-screens.md`](specification/ui-screens.md) — UI specification

**For prioritization:**
- All requirements are documented and ready
- Acceptance criteria define "done"
- Configuration options available for tuning

---

## Document Relationships

### Foundation → Requirements

Business rules (foundation) are referenced throughout requirements:
- **BR-001** → Date calculations in user journeys
- **BR-003** → Approval flow in functional overview
- **BR-005** → Edit rules in user journeys

### Requirements → Specification

Requirements drive specifications:
- User journeys → UI screens (where actions happen)
- States → Data model (status field)
- Functional overview → Configuration (parameters)

### Specification → Constraints

Specifications bounded by constraints:
- UI screens → Mobile compatibility (technical constraints)
- Notifications → Email delivery (non-functional)
- Data model → Database choice (technical constraints)

---

## What's NOT in This Documentation

This documentation covers business requirements, specifications, and constraints. Future phases will add:

**Architecture:**
- Architecture Decision Records (ADRs)
- System design diagrams
- Component structure

**Implementation:**
- Code organization
- API design details
- Testing strategy
- Deployment procedures

**Project Management:**
- Roadmap and milestones
- Sprint planning
- Issue tracking

---

## Versioning & Updates

**Current Version:** 1.0 (Initial documentation)

**How to update:**
See [`/claude/documentation-workflow.md`](../claude/documentation-workflow.md) for:
- When to update documentation
- How to maintain consistency
- Where to document new features
- Commit message conventions

---

## Documentation Quality

**This documentation is:**
- ✅ **Complete:** All requirements documented
- ✅ **Unambiguous:** Clear, specific behavior
- ✅ **Verifiable:** Acceptance criteria defined
- ✅ **Traceable:** Business rules numbered
- ✅ **AI-friendly:** Structured for parsing
- ✅ **Implementation-ready:** Sufficient detail to build

---

## Getting Started

### If you're new to this project:

1. **Read:** [`foundation/vision-and-scope.md`](foundation/vision-and-scope.md)
2. **Understand:** [`foundation/glossary.md`](foundation/glossary.md)
3. **Explore:** [`requirements/user-journeys.md`](requirements/user-journeys.md)
4. **Deep dive:** Your role-specific sections (above)

### If you're implementing:

1. **Start:** [`/claude/README.md`](../claude/README.md) (if AI agent)
2. **Read:** Relevant requirements and specifications
3. **Reference:** Business rules and German copy
4. **Build:** Following documented specifications
5. **Verify:** Against acceptance criteria

### If you're testing:

1. **Understand:** [`requirements/user-journeys.md`](requirements/user-journeys.md)
2. **Test:** [`requirements/acceptance-criteria.md`](requirements/acceptance-criteria.md)
3. **Verify:** German copy from specifications
4. **Check:** Mobile compatibility requirements

---

## Questions?

**If documentation is unclear:**
- Check cross-references to related sections
- Review examples and tables
- Search for keywords across all docs
- Ask the project owner for clarification

**If documentation seems wrong:**
- Verify against business rules
- Check with project owner
- Update documentation once confirmed
- Follow [`/claude/documentation-workflow.md`](../claude/documentation-workflow.md)

---

## Summary

This documentation provides everything needed to understand, design, implement, and test the Betzenstein booking application. It is:

- **Foundation-first:** Core concepts defined
- **Requirement-driven:** User needs specified
- **Specification-detailed:** Implementation guidance
- **Constraint-aware:** Boundaries clear
- **AI-optimized:** Structured for understanding

**Start reading, start building!** 🚀

---

## Quick Links

| Topic | Document |
|-------|----------|
| **Vision** | [vision-and-scope.md](foundation/vision-and-scope.md) |
| **Users** | [personas-and-roles.md](foundation/personas-and-roles.md) |
| **Terms** | [glossary.md](foundation/glossary.md) |
| **Rules** | [business-rules.md](foundation/business-rules.md) |
| **Features** | [functional-overview.md](requirements/functional-overview.md) |
| **Journeys** | [user-journeys.md](requirements/user-journeys.md) |
| **States** | [states-and-transitions.md](requirements/states-and-transitions.md) |
| **Permissions** | [permissions-matrix.md](requirements/permissions-matrix.md) |
| **Acceptance** | [acceptance-criteria.md](requirements/acceptance-criteria.md) |
| **UI** | [ui-screens.md](specification/ui-screens.md) |
| **Emails** | [notifications.md](specification/notifications.md) |
| **Data** | [data-model.md](specification/data-model.md) |
| **Errors** | [error-handling.md](specification/error-handling.md) |
| **Config** | [configuration.md](specification/configuration.md) |
| **Performance** | [non-functional.md](constraints/non-functional.md) |
| **Platform** | [technical-constraints.md](constraints/technical-constraints.md) |
| **Claude Guide** | [/claude/README.md](../claude/README.md) |
| **Workflow** | [/claude/documentation-workflow.md](../claude/documentation-workflow.md) |
