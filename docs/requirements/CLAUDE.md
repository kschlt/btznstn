# Requirements - CLAUDE Guide

## What's in This Section

What the system must do (user-centric):
- **functional-overview.md** - Core capabilities
- **user-journeys.md** - 8 step-by-step flows (§5.1-5.8)
- **states-and-transitions.md** - State machine (Pending → Confirmed/Denied/Canceled)
- **permissions-matrix.md** - Who can do what
- **acceptance-criteria.md** - Verifiable criteria (UC-001 to UC-008)

## When to Read This

Before implementing features:
- **Always check user-journeys.md** - See the exact flow
- **Always check acceptance-criteria.md** - Know when you're done
- Check states-and-transitions.md - Understand state changes
- Check permissions-matrix.md - Enforce access control

## Key User Journeys

**Most common:**
1. **§5.1:** Create & approve booking (happy path)
2. **§5.2:** Deny booking
3. **§5.3:** Handle denial (requester perspective)
4. **§5.4:** Edit booking dates
5. **§5.7:** Reopen denied booking

**Read the full journey** before implementing - they include effects, prerequisites, and key points.

## State Machine Gotchas

**States:** Pending → Confirmed / Denied / Canceled

**Critical:**
- Only **Pending** and **Confirmed** block dates
- **Denied** frees dates immediately (BR-004)
- **Canceled** is terminal (can't undo)
- From **Denied**, requester can **Reopen** (back to Pending)

**Transitions:**
```
Pending ──[all approve]──> Confirmed
Pending ──[any deny]────> Denied
Denied ──[reopen]───────> Pending
Any ────[cancel]────────> Canceled
```

See state diagram in `states-and-transitions.md`.

## Permissions Matrix

**Quick reference:**

| Action | Requester (own) | Approver | Anyone |
|--------|----------------|----------|---------|
| View Pending/Confirmed | ✓ | ✓ | ✓ (calendar) |
| View Denied | ✓ (own only) | ✗ | ✗ |
| Create | ✓ | ✓ | ✓ |
| Edit dates | ✓ (Pending only) | ✗ | ✗ |
| Cancel | ✓ | ✗ | ✗ |
| Approve/Deny | ✗ | ✓ (Pending only) | ✗ |
| Reopen | ✓ (own Denied) | ✗ | ✗ |

**Full matrix:** See `permissions-matrix.md`

## Acceptance Criteria Format

Each user story has Gherkin scenarios:

```gherkin
Scenario: Description
  Given [precondition]
  When [action]
  Then [expected result]
```

**Use these to write tests** before implementing.

## Linking to Foundation

Requirements reference business rules:
- Date calculations → BR-001
- Approval flow → BR-003
- Edit rules → BR-005
- Self-approval → BR-015

**Always cross-reference** business rules when implementing requirements.

---

**Next:** See [`/docs/specification/`](../specification/) for detailed technical specs (UI, data model, German copy).
