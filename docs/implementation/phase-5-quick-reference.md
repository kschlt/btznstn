# Phase 5 Quick Reference: Business Rules at a Glance

## The 9 Critical BRs for Frontend Calendar

### For Calendar Display (US-5.1)
| BR | What | Watch For |
|----|----|-----------|
| **BR-001** | Inclusive end dates (Jan 1-5 = 5 days, not 4) | Multi-month bookings must appear in ALL overlapping months |
| **BR-002** | No overlaps (Pending/Confirmed block dates, Denied doesn't) | Show visual distinction between booked vs denied |
| **BR-004** | Denied hidden from public, visible to requester | Privacy critical - test denied booking hidden from public link |
| **BR-011** | German only (Mo-So headers, DD.–DD.MM.YYYY format) | Use en-dash not hyphen; Month names German |
| **BR-014** | Past items read-only (after 00:00 Berlin time) | Boundary: ending today is NOT past; ending yesterday IS past |
| **BR-016** | Party size "n Personen" (even 1 person) | Never show "1 Person" or "Guest" |
| **BR-026** | Future horizon (18 months max by default) | Don't allow navigation/display beyond 18-month limit |
| **BR-027** | Long stay warning (>7 days) | Optional visual indicator for bookings >LONG_STAY_WARN_DAYS |

### For Navigation (US-5.2)
| BR | What | Watch For |
|----|----|-----------|
| **BR-011** | German UI ("Heute" button, German month names) | All navigation labels must be German |
| **BR-014** | Past months show readonly state | Visual indicator for past months |
| **BR-026** | Limit navigation to future horizon | Can't navigate beyond 18 months out |

### For Booking Details (US-5.3)
| BR | What | Watch For |
|----|----|-----------|
| **BR-001** | Correct total days calculation (end - start + 1) | Single day = 1 day, not 0 |
| **BR-004** | Denied hidden from public, visible to requester | Check viewer role before showing denied |
| **BR-011** | German UI (date format, status badges, buttons) | All text must be German with exact wording |
| **BR-014** | Past bookings read-only (no action buttons) | Show "Vergangen" indicator for past bookings |
| **BR-016** | Party size "n Personen" | Consistency with calendar display |
| **BR-023** | Timeline sorted chronologically | Events in order, named actors, show actions |

---

## German Copy Essentials

### Status Badges
- Pending: **"Ausstehend"**
- Confirmed: **"Bestätigt"**
- Denied: **"Abgelehnt"** (hidden from public)
- Canceled: **"Storniert"** (hidden from public, archived)

### Weekday Headers
**"Mo Di Mi Do Fr Sa So"** (week starts Monday)

### Buttons
- Next: "Nächster Monat" or ">"
- Previous: "Vorheriger Monat" or "<"
- Today: **"Heute"**
- Edit: "Bearbeiten"
- Cancel: "Stornieren"
- Approve: "Zustimmen"
- Deny: "Ablehnen"
- Reopen: "Wieder eröffnen"

### Date Format
**"DD.–DD.MM.YYYY"** with en-dash (–) not hyphen
- Example: "01.–05.08.2025"
- Single day: "15.01.2025" (no range)

### Empty States
- No bookings: **"Keine Einträge in diesem Zeitraum."**
- Past indicator: **"Vergangen"**

---

## Mobile Requirements (375px iPhone 8+)

✓ Tap targets ≥44×44 pt
✓ No horizontal scroll
✓ No hover dependencies
✓ Touch-friendly spacing
✓ High contrast (WCAG AA)

---

## Test Count by User Story

| Story | Tests | Key Focus |
|-------|-------|-----------|
| **US-5.1** | 23 | Date ranges, privacy, German text, mobile |
| **US-5.2** | 12 | Navigation, boundaries, German labels |
| **US-5.3** | 17 | Privacy, timeline, past state, German UI |
| **TOTAL** | **52** | Playwright E2E tests |

---

## Pre-Implementation Checklist

Before coding, verify:

- [ ] You've read all 9 applicable BRs (above)
- [ ] You understand inclusive end date: end - start + 1
- [ ] You know denied bookings are HIDDEN from public
- [ ] You know past bookings are READ-ONLY (timezone: Berlin)
- [ ] All German copy comes from `docs/specification/ui-screens.md`
- [ ] Date format uses en-dash: "01.–05.08.2025"
- [ ] Party size ALWAYS "n Personen" (even for 1)
- [ ] Affiliation colors: Ingeborg=#C1DBE3, Cornelia=#C7DFC5, Angelika=#DFAEB4
- [ ] Tests for mobile 375px viewport
- [ ] Tests for accessibility (WCAG AA, focus, keyboard nav)

---

## Common Mistakes to Avoid

❌ **Off-by-one dates**
✓ Use inclusive calculation: total = end - start + 1

❌ **Showing denied bookings publicly**
✓ Filter by role: `if (denied && !isRequester) hide`

❌ **English month/weekday names**
✓ Use German locale: Januar, Februar, Mo, Di, etc.

❌ **Hyphen instead of en-dash**
✓ "01.–05.08.2025" not "01-05.08.2025"

❌ **"1 Person" instead of "1 Personen"**
✓ Always use "n Personen" format

❌ **Hover-only interactions on mobile**
✓ All interactions via tap/click, no hover required

❌ **Wrong timezone (UTC instead of Berlin)**
✓ All date logic in Europe/Berlin timezone

---

## Implementation Order

1. **US-5.1: Calendar Display** (Day 1)
   - Write 23 tests first
   - Implement month view, date filtering, booking cards

2. **US-5.2: Navigation** (Day 2)
   - Write 12 tests first
   - Implement next/prev/today buttons, keyboard nav

3. **US-5.3: Booking Details** (Day 3)
   - Write 17 tests first
   - Implement details modal, timeline, access control

4. **Polish** (Day 4)
   - Fix test failures
   - Run type-check, linting, accessibility audit

---

**See full analysis:** [`phase-5-br-analysis.md`](phase-5-br-analysis.md)

