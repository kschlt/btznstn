# Architecture - CLAUDE Guide

## What's in This Section

Architecture decisions and system design:
- **README.md** - System overview, architecture diagram, principles
- **technology-stack.md** - Quick reference of technologies used (with ADR links)
- **adr-001 to ...** - Architecture Decision Records (why we chose each technology)

---

## README.md and technology-stack.md

### Purpose and When to Read

**README.md:**
- **Purpose:** Management-summary style overview of system architecture
- **When to read:** When you need to understand the overall system structure, components, principles, or data flow
- **Contains:** Architecture diagram, system components, key principles, security architecture, deployment architecture
- **Does NOT contain:** Detailed technology rationale (that's in ADRs), comprehensive ADR listings (just references the ADR directory)

**technology-stack.md:**
- **Purpose:** Quick reference table of technologies used in the project
- **When to read:** When you need to quickly see "what technologies are used" without reading ADRs
- **Contains:** Stack summary table with technology names, versions, and ADR links
- **Does NOT contain:** Rationale (that's in ADRs), detailed features, installation instructions, or maintenance-heavy information

### Maintenance Rules

**When updating README.md:**
- ✅ Update if system architecture changes (new components, changed principles)
- ✅ Update if deployment architecture changes
- ✅ Keep it concise - management-summary style, no verbosity
- ❌ Do NOT list all ADRs individually (just reference the ADR directory)
- ❌ Do NOT duplicate ADR content (ADRs contain the detailed rationale)

**When updating technology-stack.md:**
- ✅ Update when a new technology is added (add to table with ADR link)
- ✅ Update when a technology version changes significantly
- ✅ Update when a technology is replaced (remove old, add new with new ADR link)
- ❌ Do NOT add detailed features, installation instructions, or documentation links
- ❌ Do NOT add maintenance-heavy information (env vars, package management, etc.)
- ❌ Do NOT duplicate ADR content (ADRs contain the rationale)

**Key principle:** Both files are summaries that point to ADRs for details. Keep them minimal and long-lasting to reduce maintenance overhead.

---

## ⚠️ CRITICAL: Architecture Decision Records (ADRs) are Immutable Constraints

### ADR Lifecycle and Immutability

**ADRs are the law of this codebase. You MUST follow them.**

#### ADR Status States

**⚠️ CRITICAL: Check filename pattern FIRST, then status, before reading constraints**

**Filename Pattern Check (FAST - saves tokens):**
- Files ending in `-SUPERSEDED.md` → Skip reading constraints, only follow "Superseded by" links
- Files ending in `-DEPRECATED.md` → Skip reading constraints, only follow "Replaced by" links
- Files without suffix → Check status field (proceed to status check)

**Status States:**
- **Proposed** - Under review, NOT binding (do not use as constraint)
- **Accepted** - Active constraint, MUST be followed (use these constraints)
- **Superseded** - Replaced by newer ADR, follow "Superseded by" link to find current decision
- **Deprecated** - No longer applies, follow "Replaced by" link to find current decision

**Status location:** Always at the top of ADR file, right after title

**⚠️ Filename Convention for Superseded/Deprecated ADRs:**
- Superseded ADRs MUST be renamed with `-SUPERSEDED.md` suffix (e.g., `adr-003-database-orm-SUPERSEDED.md`)
- Deprecated ADRs MUST be renamed with `-DEPRECATED.md` suffix (e.g., `adr-005-ui-framework-DEPRECATED.md`)
- This allows LLMs to quickly identify and skip superseded/deprecated ADRs without reading the file (saves tokens/context)
- When superseding/deprecating an ADR, rename the file and update all references to use the new filename

#### Immutability Rule

**Once an ADR status is "Accepted", it CANNOT be altered. It can ONLY be superseded.**

**Why this matters:**
- ADRs create a historical record of decisions
- Changing an ADR destroys the decision history
- Superseding creates a clear evolution trail

**Wrong approach:**
```markdown
❌ Edit ADR-003 to change from PostgreSQL to MySQL
```

**Correct approach:**
```markdown
✅ Create ADR-010: Supersede ADR-003, migrate to MySQL
   Status: Proposed
   Supersedes: ADR-003

✅ Update ADR-003:
   Status: Superseded by ADR-010
   (Keep original decision text unchanged)

✅ Rename ADR-003 file:
   adr-003-database-orm.md → adr-003-database-orm-SUPERSEDED.md
   (Update all references to use new filename)
```

### ⚠️ ONE Decision Per ADR (Fundamental Principle)

**An ADR captures exactly ONE architectural decision, not several.**

**Why this matters:**
- Allows superseding individual decisions without affecting others
- Creates granular evolution trail
- Prevents bundling unrelated choices
- Makes decision boundaries explicit

**How to identify "one decision":**
- Ask: "Can these choices be changed independently?"
- If YES → Separate ADRs
- If NO (choices are inseparable) → One ADR

**Examples:**

**❌ Wrong - Multiple Independent Decisions:**
```markdown
ADR-010: CORS Configuration
- allow_origins = frontend domain
- allow_credentials = true
- allow_methods = ["GET", "POST"]
- allow_headers = ["*"]
```
*Problem: These can be changed independently. allow_credentials is a security policy, allow_methods is an API surface decision, allow_origins is an access control decision.*

**✅ Correct - Separate ADRs:**
```markdown
ADR-010: CORS Allow Credentials (security policy)
ADR-011: CORS Allowed Methods (API surface)
ADR-012: CORS Allowed Origins (access control)
```

**✅ Correct - One Cohesive Decision:**
```markdown
ADR-010: Naive DateTime Storage with Europe/Berlin Assumption
- Store TIMESTAMP WITHOUT TIME ZONE
- All datetimes represent Europe/Berlin local time
```
*Valid: Naive storage REQUIRES a timezone assumption. These are inseparable parts of one strategy.*

**When bundling is acceptable:**
- Multiple tools that form ONE strategy (e.g., "Type Safety Strategy" = mypy + Pydantic + TypeScript + Zod work together)
- Choices that are architecturally inseparable (e.g., naive storage + timezone assumption)
- Trade-off: If one part of the bundle needs changing, the entire ADR must be superseded

**When to split:**
- Choices that could change independently
- Unrelated concerns bundled together
- Different teams/roles would make different parts of the decision

**Before creating an ADR, ask:**
1. What is the ONE architectural decision being made?
2. Could any part of this decision change without affecting the others?
3. If I need to supersede part of this decision later, would I need to supersede all of it?

If answers suggest multiple decisions, create multiple ADRs.

---

## How to Work with ADRs as an AI Agent

### ADR Format: Human Decisions → LLM Constraints

**ADRs document human architectural decisions that become LLM constraints.**

**Workflow:**
1. **Humans make decisions** - Architects choose technologies/patterns
2. **Humans document decisions** - Write ADR to capture the decision
3. **Humans review ADRs** - Verify ADR accurately captures their decision
4. **LLMs read decisions** - Read "Decision" section to understand what constraint to apply
5. **LLMs apply constraints** - Use Decision + Constraints sections to enforce requirements

**Format: Standard ADR structure optimized for LLMs (ADR 2.0):**

1. **Decision** - Human's architectural choice (LLMs MUST read this to understand constraint)
2. **Quick Reference** table - LLMs scan quickly, humans see overview (NEW - LLM optimization)
3. **Rationale** - Human reasoning (decision → constraint → violation) for LLM understanding AND human review
   - Includes alternatives embedded as "Why NOT" violations (LLM-optimized, not separate section)
4. **Consequences** - Standard ADR section, LLM-optimized with MUST/MUST NOT patterns and code examples (only specific pitfalls)
5. **Concrete language** - "MUST" not "should" (LLMs parse better, humans understand clearly)

**Note:** We follow standard ADR patterns (Context, Decision, Rationale, Consequences, References) but optimize them for LLM consumption while remaining human-readable.

**Alternatives handling:** Unlike standard ADRs that may have a separate "Alternatives" section, we embed alternatives in Rationale as "Why NOT" violations. This keeps ADRs concise, action-focused, and reduces LLM confusion about rejected options. Focus on 1-2 key alternatives only.

**Key principle:** The "Decision" section is what humans made - LLMs MUST read it to understand what constraint to apply. Constraints are derived from the Decision.

**Status:** 5/17 ADRs updated (ADR-001, ADR-006, ADR-010, ADR-013, ADR-019). Remaining ADRs are being systematically updated to this format.

### Before Implementing

**ALWAYS check ADRs first - follow this workflow:**

1. **Find relevant ADRs** - Search for ADRs related to your feature
2. **Check filename pattern FIRST** - Files ending in `-SUPERSEDED.md` or `-DEPRECATED.md` can be skipped (only follow links to newer ADRs)
3. **Check status** - Read status field at top of each ADR (if filename doesn't indicate superseded/deprecated)
   - ✅ **"Accepted"** → Use constraints (proceed to step 4)
   - ⚠️ **"Superseded"** → Follow "Superseded by" link, check that ADR's status (skip reading this ADR's constraints)
   - ⚠️ **"Deprecated"** → Follow "Replaced by" link, check that ADR's status (skip reading this ADR's constraints)
   - ⏸️ **"Proposed"** → Skip (not yet binding)
4. **Read Decision section** - This is what humans decided, becomes your constraint
5. **Read Quick Reference** - Determine if ADR is relevant to your work (if present)
6. **Read Consequences section** - Contains MUST/MUST NOT patterns and constraints derived from Decision
7. **Review Rationale** - Understand decision → constraint → violation chain (helps apply constraints correctly)
8. **Apply constraints** - Treat Accepted ADRs as binding requirements based on Decision
9. **Never violate** - If ADR doesn't work, propose superseding ADR first

**Code Examples in ADRs:**
- Only included when showing **specific pitfalls** LLMs might take
- Generic patterns (that LLMs already know) are omitted
- Examples use consistent naming with codebase (no made-up variables)

**Example: Implementing email service**
```
Step 1: Find ADR-004 (Email Service) - filename is `adr-004-email-service.md` (no -SUPERSEDED suffix)
Step 2: Check status = "Accepted" → Use constraints
Step 3: Read Decision section → "Use Resend" (human's decision)
Step 4: Read Quick Reference → Scan constraints quickly
Step 5: Read Consequences section → MUST use Resend, MUST NOT use SendGrid/AWS SES
Step 6: Review Rationale → Understand why alternatives were rejected (violations)
Step 7: Apply constraint → Use Resend in implementation
Step 8: If Resend doesn't work → Propose ADR-011 to supersede ADR-004
```

**Example: Finding database decision**
```
Step 1: Find ADR-003 - filename is `adr-003-database-orm-SUPERSEDED.md` → Skip reading (superseded)
Step 2: Follow "Superseded by" link → ADR-012 (PostgreSQL), ADR-013 (SQLAlchemy), ADR-014 (Alembic), ADR-016 (Fly.io Postgres)
Step 3: Read those ADRs instead (they have "Accepted" status)
```

**Key:** The Decision section tells you what humans chose - that becomes your constraint.

**If you need to deviate from an Accepted ADR:**
1. STOP implementation
2. Document WHY current ADR doesn't work
3. Propose new ADR with clear rationale
4. Get user approval BEFORE proceeding
5. Create new ADR that supersedes old one
6. **Rename superseded ADR file** - Add `-SUPERSEDED.md` suffix (e.g., `adr-003-database-orm.md` → `adr-003-database-orm-SUPERSEDED.md`)
7. **Update all references** - Update all links/references to use the new filename with `-SUPERSEDED.md` suffix

---

## When to Propose a New ADR

### Situations Requiring New ADR

**1. Technology Choice Not Covered**
- Example: Need a background job scheduler (no existing ADR)
- Action: Create ADR-011: Background Job Scheduler (Celery vs APScheduler)

**2. Current ADR Doesn't Work**
- Example: Resend API limits hit, need different provider
- Action: Create ADR-012: Supersede ADR-004, migrate to SendGrid
- **After creating new ADR:** Rename old ADR file to `adr-004-email-service-SUPERSEDED.md` and update all references

**3. New Architectural Pattern Needed**
- Example: Need caching strategy (Redis, in-memory, etc.)
- Action: Create ADR-013: Caching Strategy

**4. Significant Change to Existing Decision**
- Example: Move from SQLAlchemy to Prisma
- Action: Create ADR-014: Supersede ADR-003, switch ORM
- **After creating new ADR:** Rename old ADR file to `adr-003-database-orm-SUPERSEDED.md` and update all references

### Situations NOT Requiring ADR

**Implementation details covered by existing ADRs:**
- Using a specific Pydantic field type (covered by ADR-006)
- Choosing a Shadcn component (covered by ADR-005)
- Writing a specific SQL query (covered by ADR-003)
- Structuring a test file (covered by ADR-009)

**Business logic:**
- How to calculate TotalDays (covered by business rules, not architecture)
- When to reset approvals (BR-005, not architecture)

---

## How to Create a New ADR

### Step 1: Check If ADR Needed

Ask yourself:
- Is this a **technology choice**? (Yes → ADR)
- Is this a **structural pattern**? (Yes → ADR)
- Is this an **implementation detail** within existing ADRs? (No → No ADR)
- Is this **business logic**? (No → Business Rule, not ADR)

### Step 2: Use ADR Template

**⚠️ CRITICAL: ADRs follow standard ADR patterns but are optimized for LLM consumption (ADR 2.0).**

**Standard ADR structure, LLM-optimized:**
- **Standard sections:** Context, Decision, Rationale, Consequences, References (follows common ADR pattern)
- **LLM optimizations:** 
  - Quick Reference table (NEW - helps LLMs scan quickly)
  - MUST/MUST NOT patterns in Consequences (actionable constraints)
  - Decision → constraint → violation chain in Rationale (clear reasoning)
  - Alternatives embedded in Rationale as violations (not separate section - reduces confusion)
- **Dual purpose:** LLM-actionable constraints AND human-reviewable reasoning (standard ADR format)

**Key principle:** We use standard ADR terminology and structure (which LLMs and humans know), but optimize the content within those sections for LLM consumption. Alternatives are embedded in Rationale (not separate) to keep ADRs concise and action-focused.

**File naming:** `adr-{number}-{title}.md`
- Number: Next available
- Title: Kebab-case, descriptive

**Format Requirements (Dual Purpose):**
- **LLM-actionable constraints:** MUST/MUST NOT patterns written so LLMs can parse and apply them
- **Human-reviewable reasoning:** Rationale and context preserved for human architects to review decisions
- **Concrete language:** Use "MUST" not "should" (LLMs parse better, humans understand clearly)
- **No verbosity:** Direct, to-the-point constraints (but preserve reasoning chain)
- **No human-team language:** Remove "learning curve", "team needs to understand" (use constraint language instead)

**What to include (Standard ADR structure, LLM-optimized):**
- ✅ Context (brief - why we need this decision)
- ✅ Decision (clear statement of human's choice)
- ✅ Quick Reference table (NEW - LLM optimization, helps quick scanning)
- ✅ Rationale (decision → constraint → violation chain, LLM-focused)
  - Includes alternatives embedded as "Why NOT" violations (1-2 key alternatives only)
- ✅ Consequences (standard ADR section, LLM-optimized with MUST/MUST NOT patterns)
  - **⚠️ Focus on THIS decision only** - Consequences must describe requirements of THIS decision, not other decisions or specifications
- ✅ Code examples (only specific pitfalls related to THIS decision, not generic patterns)
- ✅ Applies To (which phases/specs this affects)
- ✅ Validation commands (for user story checklists, validating THIS decision)

**What to exclude:**
- ❌ Separate "Alternatives" section (embed in Rationale as violations instead)
- ❌ Human-team language ("team needs to learn", "developers should understand", "learning curve")
- ❌ Human-oriented trade-offs ("learning curve", "team needs training") - ADRs are for LLMs, focus on LLM implementation challenges instead
- ❌ LLM-specific language in Rationale ("LLM-friendly", "for LLM agents", "AI-friendly") - State technical facts only
- ❌ Repetition between Rationale and Consequences - Rationale explains WHY, Consequences lists WHAT. Don't repeat explanations.
- ❌ Implementation checklists (belong in user stories, not ADRs)
- ❌ Vague language ("should", "consider", "might want to")
- ❌ Detailed tutorials (minimal reference examples only)
- ❌ Exhaustive alternative lists (keep to 1-2 key alternatives)

**Template:**
```markdown
# ADR-{number}: {Title}

**Status:** Accepted
**Date:** YYYY-MM-DD
**Deciders:** Solution Architect
**Context:** {Brief trigger}

---

## Context

{2-4 paragraphs: problem, requirements, constraints}

---

## Decision

{1-2 paragraphs: clear statement of human's architectural choice}

---

## Quick Reference

| Constraint | Requirement | Violation |
|------------|-------------|-----------|
| {Constraint 1} | {Requirement} | {What violates it} |
| {Constraint 2} | {Requirement} | {What violates it} |

---

## Rationale

**Why {Chosen Option}:**
- {Reason 1} → **Constraint:** {Derived constraint}
- {Reason 2} → **Constraint:** {Derived constraint}

**Why NOT {Alternative}:**
- {Alternative} uses {pattern} → **Violation:** {Why it violates decision}

---

## Consequences

### MUST (Required)
- {Constraint 1}
- {Constraint 2}

### MUST NOT (Forbidden)
- {Anti-pattern 1}
- {Anti-pattern 2}

### Trade-offs
- {Complexity} - {Mitigation or required discipline}

### Code Examples

```{language}
# ❌ WRONG: {Specific mistake LLMs might make}
{Code showing violation}

# ✅ CORRECT: {How to do it right}
{Code showing correct pattern}
```

### Applies To
- {Which phases this applies to}
- {File patterns: `app/routers/*.py`}

### Validation Commands
- `grep -r "pattern" app/` (should be empty/present)
- {Other validation commands for user story checklists}

**Related ADRs:**
- [ADR-XXX](adr-xxx.md) - {How it relates}

---

## References

**Related ADRs:** ADR-XXX
**Business Rules:** BR-XXX
**Implementation:** {file paths}
```

### Step 3: How to Fill Each Section

**Context:**
- 2-4 paragraphs explaining the problem/requirement
- What triggered this decision?
- What constraints exist?

**Decision:**
- Clear statement of what humans chose
- 1-2 paragraphs maximum
- This is what LLMs will read to understand the constraint

**Quick Reference:**
- Table format: Constraint | Requirement | Violation
- 3-5 key constraints only
- Helps LLMs quickly determine if ADR is relevant

**Rationale:**
- Connect decision → constraint → violation explicitly
- Format: "{Decision} requires {pattern} → **Constraint:** {MUST do X}"
- Format: "{Alternative} uses {pattern} → **Violation:** {Why wrong}"
- **⚠️ CRITICAL: Explain WHY (technical reasons), not benefits** - State technical facts (e.g., "Vitest provides fast execution"), not LLM-specific benefits (e.g., "LLM-friendly"). Don't mention "LLM", "AI", or "agent" in Rationale.
- **⚠️ CRITICAL: Derive high-level constraints only** - Don't list every detailed constraint. Explain the decision and derive 2-4 high-level constraints. Detailed constraints go in Consequences.
- **Alternatives:** Embed in Rationale as "Why NOT" violations (not separate section)
  - Keep to 1-2 key alternatives only (not exhaustive)
  - Frame as violations to establish clear boundaries

**Consequences:**
- Standard ADR section name (follows ADR pattern)
- LLM-optimized: Contains MUST/MUST NOT patterns (derived from Decision and Rationale)
- **⚠️ CRITICAL: Focus on THIS decision only** - Consequences must describe what THIS decision requires, not other decisions or specifications. Each ADR must stand alone. For example:
  - ✅ If choosing FastAPI → consequences about FastAPI requirements (async def, Pydantic, type hints)
  - ❌ NOT about German error messages (specification decision)
  - ❌ NOT about AsyncSession (separate ADR-013 decision)
  - ❌ NOT about business rules (those are separate)
- **⚠️ CRITICAL: List WHAT (constraints), not WHY (reasons)** - Rationale explains WHY. Consequences lists WHAT must be done. Don't repeat explanations from Rationale. Just list constraints.
  - ✅ "MUST use Vitest for frontend unit tests"
  - ❌ "MUST use Vitest for frontend unit tests - Fast test execution (50-200ms)" (repeats Rationale explanation)
- **MUST (Required):** List constraints that THIS decision requires. Use "MUST" language consistently. Don't add explanations - reasoning is in Rationale.
- **MUST NOT (Forbidden):** List anti-patterns that violate THIS decision. Use "MUST NOT" language consistently. Don't add explanations - reasoning is in Rationale.
- **Trade-offs:** ⚠️ **CRITICAL: LLM-focused concerns only** - Trade-offs must describe LLM implementation challenges, not human learning curves. Use "MUST" and "MUST NOT" consistently for LLM-specific directives. Examples:
  - ✅ "Many code examples use Pages Router - MUST use App Router patterns (`app/` directory). MUST NOT use Pages Router patterns (`pages/` directory). Check for `pages/` directory usage."
  - ✅ "Code examples may mix patterns incorrectly - MUST use X. MUST NOT use Y. Verify Z."
  - ❌ "MUST use X not Y" (combines MUST and MUST NOT in one statement - split them)
  - ❌ "You must use X" (too personal, use MUST)
  - ❌ "LLMs must be careful to use X" (meta-language, not direct)
  - ❌ "Learning curve for developers" (human concern, not LLM concern)
  - ❌ "Team needs to understand X" (human concern, not LLM concern)
  - **Key:** Use MUST/MUST NOT consistently throughout Consequences and Trade-offs for LLM-specific directives. Split positive and negative directives into separate MUST and MUST NOT statements.
- **Code Examples:** Only include if showing specific pitfalls LLMs might take related to THIS decision. Generic patterns (LLMs already know) should be omitted. Do NOT include examples that demonstrate other decisions (e.g., don't show German error messages if the decision is about FastAPI).
- **Applies To:** Which phases/files affected by THIS decision
- **Validation Commands:** Commands for validating THIS decision (not other decisions)
- **Related ADRs:** Link to related ADRs, but don't embed their constraints here
- **Do NOT include:** "Related Specifications" section - specifications are separate from architectural decisions

**References:**
- Related ADRs (links to other ADRs that relate to this decision)
- Tools (documentation links for the technology chosen)
- Implementation file paths (where this decision is implemented)
- **Do NOT include:** Business rules, specifications, or other decisions - those are separate concerns

### Step 4: Propose to User

**Don't create ADR file yet. Propose first:**
```
I need to make an architectural decision that isn't covered by existing ADRs:

Decision needed: {Topic}
Current situation: {Context}
Proposed solution: {Your recommendation}
Rationale: {Why}

Should I create ADR-012: {Title}?
```

### Step 5: Create ADR After Approval

Only after user approves, create the ADR file using the template above.

---

## Finding Relevant ADRs

**To find which ADRs apply to your work:**

1. **Check filename pattern** - Files ending in `-SUPERSEDED.md` or `-DEPRECATED.md` can be skipped (only follow links to newer ADRs)
2. **List ADR files** - Use `glob_file_search` or `list_dir` to find all `adr-*.md` files in this directory
3. **Search by topic** - Look for ADRs matching your feature (e.g., "auth" → ADR-019)
4. **Check status** - Only use "Accepted" ADRs as constraints (skip files with `-SUPERSEDED.md` or `-DEPRECATED.md` suffix)
5. **Follow superseded links** - If ADR is superseded, follow link to current decision (don't read the superseded ADR's constraints)

**Remember:** 
- Filename pattern (`-SUPERSEDED.md` or `-DEPRECATED.md`) allows quick identification without reading the file
- Status is at the top of each ADR file (check if filename doesn't indicate superseded/deprecated)
- Always check filename pattern FIRST, then status, before reading constraints

---

## Summary: ADRs are Law

**Critical reminders:**
1. ⚠️ **Check filename pattern FIRST** - Files with `-SUPERSEDED.md` or `-DEPRECATED.md` suffix can be skipped (only follow links)
2. ⚠️ **Check status** - Only use "Accepted" ADRs as constraints (if filename doesn't indicate superseded/deprecated)
3. ⚠️ **Read Decision section** - This is what humans decided, becomes your constraint
4. ⚠️ **ADRs are constraints, not suggestions** - Must follow Accepted ADRs
5. ⚠️ **Never violate an accepted ADR** - Propose superseding ADR if needed
6. ⚠️ **Never alter an accepted ADR** - Only supersede, never edit
7. ⚠️ **Rename when superseding** - Add `-SUPERSEDED.md` suffix and update all references
8. ⚠️ **Propose before creating new ADR** - Get approval first

**If you violate an Accepted ADR, the implementation is wrong. Full stop.**

---

**Next:** See [`/docs/design/`](../design/) for detailed API/DB/component design and [`/docs/implementation/`](../implementation/) to start building.
