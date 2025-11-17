# Foundation - CLAUDE Guide

## What's in This Section

Core concepts and business rules that rarely change:
- **vision-and-scope.md** - What and why
- **personas-and-roles.md** - Who (Requester, Approver)
- **glossary.md** - Terms and definitions
- **business-rules.md** - BR-001 to BR-029 (THE MOST IMPORTANT FILE)

## When to Read This

**Always read `business-rules.md` first** before implementing any feature.

Check other files when:
- You encounter unfamiliar terms → `glossary.md`
- You need to understand user roles → `personas-and-roles.md`
- You're questioning if something is in scope → `vision-and-scope.md`

## Critical Business Rules

**Top gotchas:**
- **BR-001:** Inclusive end date (`TotalDays = End - Start + 1`) - watch for off-by-one errors
- **BR-002:** No overlaps with Pending/Confirmed
- **BR-004:** Denied bookings don't block dates, hidden from public
- **BR-005:** Shortening dates keeps approvals, extending resets them
- **BR-015:** Self-approval if requester is an approver
- **BR-024:** First-action-wins for concurrent approvals (use SELECT FOR UPDATE)
- **BR-029:** First-write-wins for booking creation (check conflicts in transaction)

**Full list:** See `business-rules.md`

## Working with Business Rules

**In code:**
```python
# Per BR-001: Inclusive end date
total_days = (end_date - start_date).days + 1
```

**Always:**
- Reference rules by number (e.g., "per BR-015")
- Test every business rule
- Check which rules apply before implementing

**Never:**
- Implement features that violate business rules
- Update business rules without user approval

## Key Personas

- **Requester:** Creates bookings, can edit/cancel own
- **Approver:** One of 3 fixed (Ingeborg, Cornelia, Angelika)

If requester IS an approver → auto-approve per BR-015.

---

**Next:** See [`/docs/requirements/`](../requirements/) for how these rules manifest in user flows.
