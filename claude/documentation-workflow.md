# Documentation Workflow & Maintenance

## Purpose

This guide explains how to maintain and extend the documentation as the project evolves.

---

## Core Principles

### 1. Documentation Drives Development

**Documentation First:**
- Requirements documented before implementation
- Acceptance criteria defined upfront
- German copy specified before UI built
- Data model designed before database schema

**Benefits:**
- Clear expectations
- Fewer misunderstandings
- Easier onboarding
- Better testing

---

### 2. Keep Documentation Synchronized

**Documentation should always reflect reality:**
- Update docs when requirements change
- Update docs when implementation reveals gaps
- Update docs when user provides clarifications
- Never let code and docs drift apart

**Red Flags:**
- Code implements behavior not documented
- Documentation describes features not built
- German copy in code differs from specs
- Business rules changed but docs not updated

---

### 3. Single Source of Truth

**Avoid duplication:**
- Define concepts once (in glossary)
- Reference business rules by number (BR-###)
- Link between documents (don't copy/paste)
- Keep German copy in one place (notifications.md, error-handling.md)

**When to duplicate:**
- Summary tables for quick reference
- Critical warnings repeated for emphasis
- Examples illustrating complex behavior

---

## When to Update Documentation

### Scenario: Requirements Change

**User says:** "Actually, we want four approvers, not three."

**Process:**
1. **Confirm scope** of change with user
2. **Identify affected documents:**
   - `foundation/vision-and-scope.md`
   - `foundation/personas-and-roles.md`
   - `foundation/business-rules.md` (BR-003)
   - `requirements/functional-overview.md`
   - `specification/data-model.md`
   - `specification/notifications.md` (email copy)
3. **Update all affected sections** systematically
4. **Review for consistency** (search for "three" across all docs)
5. **Update this changelog** (if keeping one)
6. **Commit with clear message:** "docs: update approver count from 3 to 4"

---

### Scenario: Implementation Reveals Ambiguity

**During coding, you realize:** "What happens if requester tries to reopen a Canceled booking?"

**Process:**
1. **Check documentation** for this scenario
2. **If not documented:** Ask user for intended behavior
3. **Update documentation** with answer:
   - Add to `requirements/states-and-transitions.md` (transitions)
   - Add to `requirements/permissions-matrix.md` (if permission issue)
   - Add acceptance criteria if needed
4. **Then implement** based on updated docs

---

### Scenario: German Copy Needs Adjustment

**User says:** "This error message sounds too formal, make it friendlier."

**Process:**
1. **Update specification:**
   - Find message in `specification/error-handling.md` or `specification/notifications.md`
   - Replace with new copy
2. **Update code** to use new copy
3. **Document the change** (commit message or changelog)

**Don't:**
- Change copy in code without updating spec
- Create variations of the same message

---

### Scenario: New Feature Added

**User requests:** "Add ability to attach photos to bookings."

**Process:**
1. **Document requirements first:**
   - Update `requirements/functional-overview.md` (new capability)
   - Add user journey to `requirements/user-journeys.md` (if complex)
   - Update `specification/data-model.md` (new fields/tables)
   - Add validation rules
   - Define German copy (`specification/error-handling.md`)
   - Add acceptance criteria
2. **Review constraints:**
   - Check `constraints/technical-constraints.md` (any new deps?)
   - Check `constraints/non-functional.md` (performance impact?)
3. **Document configuration:**
   - Update `specification/configuration.md` (max file size, etc.)
4. **Then implement** based on documentation

---

### Scenario: Bug Fix Reveals Misunderstanding

**Bug:** "Deny button shown on Denied bookings (should be hidden)"

**Process:**
1. **Check documentation:** `requirements/permissions-matrix.md` says approvers can't act on Denied
2. **Documentation is correct** → Fix code to match docs
3. **No doc update needed** (unless adding clarification helps)
4. **If docs were wrong:** Update docs, then fix code

---

## Where to Document What

### Foundation (`/docs/foundation/`)

**Purpose:** Core concepts that rarely change

**Document here:**
- Vision and goals
- Problem being solved
- User personas
- Glossary terms
- Business rules (numbered, referenced elsewhere)

**Don't document here:**
- Implementation details
- Technology choices
- UI copy

---

### Requirements (`/docs/requirements/`)

**Purpose:** What the system must do (user-centric)

**Document here:**
- Functional capabilities
- User journeys (step-by-step flows)
- State transitions
- Role permissions
- Acceptance criteria (verifiable)

**Don't document here:**
- How it's implemented (that's architecture)
- German copy (that's specification)
- Configuration values (that's specification)

---

### Specification (`/docs/specification/`)

**Purpose:** Detailed technical/interface specs

**Document here:**
- UI screen layouts and interactions
- All German copy (notifications, errors, empty states)
- Data model (tables, fields, relationships)
- Validation rules
- Configuration parameters

**Don't document here:**
- Why decisions were made (that's ADRs, future)
- Implementation code structure

---

### Constraints (`/docs/constraints/`)

**Purpose:** Boundaries and limits

**Document here:**
- Non-functional requirements (performance, security, privacy)
- Technical constraints (platform, browser, language)
- Operational limits (SLA, support)

**Don't document here:**
- Specific implementations
- User-facing features

---

## How to Add New Sections

### Adding a New Business Rule

**Process:**
1. Open `docs/foundation/business-rules.md`
2. Find next available number (e.g., BR-030)
3. Add to appropriate category or create new category
4. Include: rule statement, rationale, examples, related rules
5. Update summary table at end
6. Reference this rule in other docs (e.g., "per BR-030")

**Example:**
```markdown
### BR-030: Description Edit Logging

Description edits are NOT logged in timeline.

**Rationale:** Description is cosmetic; doesn't affect approvals or state.

**Related Rules:** BR-005 (date edits ARE logged)
```

---

### Adding a New User Journey

**Process:**
1. Open `docs/requirements/user-journeys.md`
2. Add new section (## 5.X Title)
3. Include:
   - Prerequisites
   - Flow (numbered steps)
   - Effects (what changes)
   - Key points
   - Outcomes
4. Update journey summary table at end
5. Add acceptance criteria in `acceptance-criteria.md`

---

### Adding German Copy

**For notifications:**
1. Open `docs/specification/notifications.md`
2. Add new trigger/template section
3. Include: trigger, recipients, purpose, template, example
4. Update notification summary table

**For errors:**
1. Open `docs/specification/error-handling.md`
2. Add to appropriate category (validation, system, etc.)
3. Include: scenario, German copy, display guidance
4. Update error summary table

---

### Adding Configuration Parameter

**Process:**
1. Open `docs/specification/configuration.md`
2. Add to appropriate section
3. Include: parameter name, type, default, notes
4. Update configuration summary table
5. Add to environment-specific sections if needed

---

## Maintaining Consistency

### Cross-Document Consistency

**Check these relationships:**

| If you change... | Also check... |
|------------------|---------------|
| Business rule | All docs referencing that BR number |
| State transition | `states-and-transitions.md`, `permissions-matrix.md`, user journeys |
| German copy | `notifications.md`, `error-handling.md`, `ui-screens.md` |
| Data model | `business-rules.md`, `functional-overview.md`, user journeys |
| Configuration | `non-functional.md`, `technical-constraints.md` |

---

### Search for Consistency

**Use grep/search across all docs:**
```bash
# Find all references to a business rule
grep -r "BR-015" docs/

# Find all mentions of a term
grep -ri "denied" docs/

# Find all German strings (example)
grep -r "Anfrage" docs/
```

---

### Review Checklist

**Before committing documentation changes:**

- [ ] All affected documents updated
- [ ] Cross-references still valid
- [ ] Tables updated (summaries)
- [ ] Examples consistent with changes
- [ ] No orphaned references
- [ ] German copy matches specification
- [ ] Business rule numbers correct
- [ ] Markdown formatting valid

---

## Documentation Style Guide

### Writing Style

**Tone:**
- Clear and direct
- No unnecessary jargon
- Assume intelligent reader
- Be specific, not vague

**Structure:**
- Use headings (##, ###, ####)
- Use lists for sequences or options
- Use tables for comparisons or matrices
- Use code blocks for examples

---

### Formatting Conventions

**Headings:**
```markdown
# Top Level (Document Title)
## Major Section
### Subsection
#### Detail Level
```

**Lists:**
```markdown
**Ordered (sequences):**
1. First step
2. Second step

**Unordered (options or items):**
- Option A
- Option B

**Nested:**
1. Main point
   - Detail
   - Detail
```

**Tables:**
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value A  | Value B  | Value C  |
```

**Code/Configuration:**
```markdown
Inline code: `variableName`

Block:
```json
{
  "key": "value"
}
```
```

**Emphasis:**
```markdown
**Bold** for important terms
*Italic* for emphasis
`code` for technical terms
```

---

### Cross-References

**Within same document:**
```markdown
See section "State Transitions" below.
```

**Between documents:**
```markdown
See `docs/foundation/business-rules.md` for complete rules list.

Per BR-015, self-approval is auto-applied.

See `requirements/user-journeys.md` §5.4 for edit scenarios.
```

---

### German Copy

**In documentation:**
```markdown
**German Copy:**
```
Bitte gib eine gültige E-Mail-Adresse an.
```

**Example:**
```
Error: "Bitte gib eine gültige E-Mail-Adresse an."
```
```

**Always include:**
- Scenario triggering the copy
- Context (inline error, modal, email, etc.)
- Example if helpful

---

## Version Control

### Commit Messages

**Format:**
```
docs: <short description>

<optional detailed explanation>
```

**Examples:**
```
docs: add business rule BR-030 for description edit logging

docs: update approver count from 3 to 4
Updated all references across foundation, requirements, and specification documents.

docs: clarify reopen conflict validation in BR-018

docs: add German copy for long-stay confirmation dialog
```

---

### When to Commit

**Commit documentation changes:**
- After completing a logical change (e.g., adding new feature docs)
- Before implementing the feature (docs first)
- When fixing documentation errors or ambiguities
- When synchronizing docs with code changes

**Separate commits:**
- Documentation changes separate from code changes (helps review)
- Or combined if small change (e.g., add field to model + update docs)

---

## Documentation Reviews

### Self-Review

**Before finalizing documentation:**
1. Read it from user's perspective (clear?)
2. Check all cross-references (valid?)
3. Verify tables and lists (complete?)
4. Test examples (accurate?)
5. Spell-check (especially German copy)
6. Format-check (Markdown renders correctly)

---

### Peer Review (If Team)

**What to check:**
- Clarity and completeness
- Consistency with existing docs
- Correctness of business logic
- German copy accuracy (native speaker review if possible)
- Technical feasibility

---

## Future Documentation

### Architecture Decision Records (ADRs)

**When to create:**
- After foundation/requirements/specification complete
- When making significant architectural decisions
- Before implementation of complex features

**Where to store:**
- Create `/docs/architecture/` folder
- Each ADR in separate file: `adr-001-database-choice.md`
- Use standard ADR format (context, decision, consequences)

---

### Solution Design Docs

**When to create:**
- After requirements documented
- Before detailed implementation planning
- For complex features or integrations

**Where to store:**
- Create `/docs/design/` folder
- Separate files for major features
- Reference requirements and architecture

---

### Implementation Plans

**When to create:**
- After design finalized
- Before starting development
- For breaking work into increments

**Where to store:**
- Create `/docs/implementation/` folder
- Or use project management tools (GitHub Issues, Jira)
- Link back to requirements and design docs

---

## Keeping Documentation Alive

### Regular Maintenance

**Monthly (or per sprint):**
- Review for outdated content
- Check for broken cross-references
- Update configuration if changed
- Verify German copy still accurate

**After Major Changes:**
- Comprehensive review of affected areas
- Update all cross-references
- Regenerate diagrams if needed
- Update summary tables

---

### Documentation Debt

**Avoid accumulating documentation debt:**
- Update docs immediately when requirements change
- Don't defer "until later" (later never comes)
- Treat docs as part of "done" (not separate)

**If debt accumulates:**
- Schedule dedicated time to update docs
- Prioritize most-used sections first
- Get user feedback on what's confusing

---

## Documentation Quality Metrics

### How to Know Docs Are Good

**Positive signs:**
- New team members can onboard from docs alone
- Implementation matches specs exactly
- Few "what does this mean?" questions
- No code/docs drift
- German copy consistent everywhere

**Warning signs:**
- Code contradicts docs
- Multiple people confused by same section
- Missing sections ("TBD" or "TODO")
- Outdated examples
- Inconsistent terminology

---

## Summary

**Golden Rules:**
1. **Documentation first** (before code)
2. **Keep synchronized** (code + docs)
3. **Single source** (no duplication)
4. **Be specific** (no ambiguity)
5. **Update immediately** (no deferring)
6. **Review thoroughly** (cross-check)
7. **Use structure** (optimize for AI)

**When in doubt:**
- Over-document rather than under-document
- Add examples to clarify complex behavior
- Ask user if uncertain
- Maintain consistency above all

**The goal:**
> Future AI agents (and humans) should be able to understand and implement features correctly using only the documentation, without needing to ask clarifying questions.

Good luck maintaining! 📚
