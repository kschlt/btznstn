# Design - CLAUDE Guide

## What's in This Section

Detailed design specifications:
- **api-specification.md** - Complete REST API contract (endpoints, request/response)
- **database-schema.md** - SQL DDL, indexes, constraints
- **authentication-flow.md** - Token generation and validation flow
- **component-guidelines.md** - UI component patterns and structure
- **design-tokens.md** - Colors, typography, spacing, breakpoints

## When to Read This

During implementation:
- Building API endpoints? → `api-specification.md`
- Creating database? → `database-schema.md`
- Implementing auth? → `authentication-flow.md`
- Building UI components? → `component-guidelines.md`
- Styling UI? → `design-tokens.md`

## API Design

**RESTful structure** - see `api-specification.md` for complete endpoint list

**Key patterns:**
- Versioned: `/api/v1/...`
- Token auth: `?token=xxx` query parameter
- JSON request/response
- Pydantic validation

**Common endpoints:**
```
GET    /api/v1/bookings                 # List (filtered by token)
POST   /api/v1/bookings                 # Create
GET    /api/v1/bookings/{id}            # Get details
PATCH  /api/v1/bookings/{id}            # Edit dates
DELETE /api/v1/bookings/{id}            # Cancel
POST   /api/v1/bookings/{id}/approve    # Approve
POST   /api/v1/bookings/{id}/deny       # Deny
POST   /api/v1/bookings/{id}/reopen     # Reopen
```

## Database Schema

**SQL DDL in `database-schema.md`**

**Key tables:**
```sql
bookings            # Main booking data
approver_parties    # 3 fixed approvers (seed data)
approvals           # Junction: booking × approver
timeline_events     # Audit log
holidays (optional) # German holidays
```

**Critical:**
- Use foreign keys for referential integrity
- Add indexes on: status, date ranges, email queries
- Use CHECK constraints for validation
- Migrations with Alembic

## Authentication Flow

**Token-based, no sessions** - see `authentication-flow.md`

**Token structure:**
```typescript
{
  email: string,
  role: "requester" | "approver",
  booking_id?: string,  // Optional
  iat: timestamp
}
```

**Signed with HMAC-SHA256, never expires (BR-010)**

**Flow:**
1. User creates booking → backend generates requester token → email sent
2. API generates approver tokens → emails sent to 3 approvers
3. User clicks link with token → backend validates → performs action

## Component Guidelines

**See `component-guidelines.md` for patterns**

**Structure:**
```
/components/
├── ui/              # Shadcn base components
├── calendar/        # Calendar-specific
├── booking/         # Booking forms/details
└── approver/        # Approver views
```

**Patterns:**
- Server Components where possible (Next.js App Router)
- Client Components only when needed (forms, interactions)
- Composition over prop drilling

## Design Tokens

**See `design-tokens.md` for complete list**

**Quick reference:**
```typescript
// Colors
colors.primary      // Main brand color
colors.destructive  // Errors, cancel
colors.muted        // Disabled, secondary

// Spacing
space.4            // 1rem (16px)

// Breakpoints
sm: 640px          // Tablet
md: 768px          // Desktop
lg: 1024px         // Large desktop
```

**Mobile-first:** Design for 375px, enhance for larger.

---

**Next:** See [`/docs/implementation/`](../implementation/) to start building with these designs.
