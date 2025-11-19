# Project Management

**This is the command center for all work on the Betzenstein Booking Application.**

## 🎯 Purpose

This folder organizes **how we execute the work** defined in the specifications. Think of it as the project management layer that sits on top of the long-living specification.

**Key Principle:**
- **Specifications** (`/docs/`) = Long-living, permanent documentation (what to build)
- **Project Management** (`/project/`) = Work organization, temporary execution tracking (how/when to build)

---

## 📂 Structure

```
/project/
├── README.md           # This file - explains the project management structure
├── STATUS.md           # Strategic view: Where are we now? (snapshot in time)
├── ROADMAP.md          # Tactical view: What increments exist? What's their order?
├── BACKLOG.md          # Operational view: What tasks are pending? What's next?
│
└── /increments/        # Increment-by-increment tracking
    ├── increment-01.md # Increment 1: Backend Core (Phases 0-2)
    ├── increment-02.md # Increment 2: Backend Business Logic (Phases 3-4)
    ├── increment-03.md # Increment 3: Frontend Core (Phases 5-6)
    └── ...
```

---

## 🚀 How to Use This Folder

### For Humans

**Before starting any work:**
1. Read `STATUS.md` - Understand current state
2. Check `BACKLOG.md` - See what's next
3. Open the current increment file - Get detailed context
4. Link to specifications as needed - Get implementation details

**After completing work:**
1. Update increment file - Mark user stories complete
2. Update `STATUS.md` - Update phase completion
3. Update `BACKLOG.md` - Remove completed tasks, add new ones

### For AI Agents (Claude Code)

**First action on ANY task:**
1. ✅ Read `/project/STATUS.md` - Understand where project stands
2. ✅ Read `/project/BACKLOG.md` - Identify current priority
3. ✅ Read current increment file - Get detailed user story context
4. ✅ Link to `/docs/` specifications - Get implementation details
5. ✅ Execute work
6. ✅ Update project files - Mark progress

**This workflow MUST be followed** to ensure AI agents have full context before starting work.

---

## 📊 Three Flight Levels

### Level 1: Strategic (STATUS.md)

**Purpose:** High-level snapshot of project health

**Questions answered:**
- What phases are specified?
- What phases are implemented?
- What's the overall completion percentage?
- What are the critical blockers?
- What's the next milestone?

**Update frequency:** After each phase completion or major milestone

---

### Level 2: Tactical (ROADMAP.md + /increments/)

**Purpose:** Increment planning and dependency management

**Questions answered:**
- What increments exist?
- What phases are in each increment?
- What user stories are in each increment?
- What are the dependencies between increments?
- What's the order of user stories within an increment?

**ROADMAP.md:**
- Lists all increments
- Shows dependencies
- Shows current vs next increment

**/increments/ files:**
- One file per increment (e.g., `increment-01.md`)
- Lists all user stories in order
- Shows status of each user story (✅ Done, 🔄 In Progress, ⏸️ Pending, 🚫 Blocked)
- Links to specifications and business rules
- Tracks definition of done

**Update frequency:** Daily or after each user story completion

---

### Level 3: Operational (BACKLOG.md)

**Purpose:** Task-level work tracking

**Questions answered:**
- What specific tasks need to be done now?
- What's the priority order?
- Are there any sub-tasks within tasks (TODOs within TODOs)?
- What bugs or issues exist?
- What documentation gaps need filling?

**BACKLOG.md sections:**
- 🔥 High Priority (Do This Week)
- 🟡 Medium Priority (Next 2 Weeks)
- 🟢 Low Priority (Future)
- 📝 Documentation TODOs
- 🐛 Bugs / Issues
- 💡 Ideas / Enhancements

**Update frequency:** Daily, as tasks are completed or discovered

---

## 🔗 Relationship to Specifications

### Specifications Live Forever

Files in `/docs/` are **permanent documentation**:
- Business rules (BR-001 to BR-029)
- Architecture decisions (ADRs)
- UI specifications
- Data models
- Error messages (German copy)

**These survive even after features are implemented.**

### Project Management is Temporary

Files in `/project/` track **execution** and will be archived after project completion:
- Increments track implementation phases
- User stories are temporary (done once, then archived)
- Status and roadmap are point-in-time snapshots

**These are throw-away once project is complete.**

### How They Connect

**Example workflow:**

1. **Specification exists:** `/docs/foundation/business-rules.md` defines BR-002 (No overlaps with Pending/Confirmed)

2. **Increment planned:** `/project/increments/increment-01.md` lists US-2.1 (Create Booking)

3. **User story implemented:**
   - Developer reads increment file
   - Increment links to `/docs/design/api-specification.md` for endpoint details
   - Increment links to BR-002 for conflict detection logic
   - Increment links to `/docs/specification/error-handling.md` for German error messages
   - Developer implements, tests pass, marks user story ✅ Complete in increment file

4. **After project completion:**
   - `/docs/` files remain (permanent reference)
   - `/project/` files archived (historical record)

---

## 🎯 Increment Planning Philosophy

### What is an Increment?

An **increment** is a group of related phases that:
- Can be deployed together (potentially)
- Have clear dependencies
- Deliver a cohesive set of functionality
- Build upon previous increments

**Increments ≈ Phases** in this project, but with flexibility:
- Sometimes multiple phases = 1 increment (e.g., Phases 3-4)
- Sometimes 1 phase = 1 increment (e.g., Phase 8)

### Increment Dependencies

```
Increment 1 (Backend Core)
    ↓
Increment 2 (Backend Business Logic)
    ↓
Increment 3 (Frontend Core) ← also depends on Increment 1
    ↓
Increment 4 (Frontend Approver)
    ↓
Increment 5 (Production)
```

### Why Order Matters

**Example:** You can't implement Phase 6 (Web Booking Forms) before:
- Phase 2 (Booking API endpoints) - Frontend needs backend
- Phase 5 (Web Calendar) - Forms need calendar component
- Playwright configured - Frontend needs test infrastructure

**Increment planning handles this** by grouping and ordering work to respect dependencies.

---

## 🔄 Work Lifecycle

### 1. Planning Phase

- Define increments in `ROADMAP.md`
- Create increment files in `/increments/`
- List user stories in order
- Identify dependencies
- Estimate effort

### 2. Execution Phase

- Update `STATUS.md` with current increment
- Work through `BACKLOG.md` tasks in priority order
- Mark user stories as 🔄 In Progress in increment file
- Link to specifications for implementation details
- Write tests, implement features
- Mark user stories as ✅ Complete

### 3. Review Phase

- Verify all acceptance criteria met
- Update increment file with learnings
- Update `STATUS.md` with phase completion
- Move to next increment

---

## 📌 Key Files Quick Reference

| File | Purpose | Update Frequency | Primary Audience |
|------|---------|------------------|------------------|
| `STATUS.md` | Where are we now? | Weekly / per milestone | Everyone (quick check) |
| `ROADMAP.md` | What's the plan? | Monthly / per increment | Project lead, stakeholders |
| `BACKLOG.md` | What's next? | Daily | Developers, AI agents |
| `increment-XX.md` | Detailed user story tracking | Daily / per story | Developers working on increment |

---

## 🤖 For AI Agents: Critical Instructions

**BEFORE STARTING ANY WORK:**

1. ✅ **Always read `/project/STATUS.md` first** - Understand project state
2. ✅ **Check `/project/BACKLOG.md`** - Confirm task is highest priority
3. ✅ **Read current increment file** - Get user story context
4. ✅ **Link to specifications** - Get implementation details from `/docs/`

**WHILE WORKING:**

5. ✅ **Reference business rules** - Link to BR-XXX as needed
6. ✅ **Use exact German copy** - From `/docs/specification/`
7. ✅ **Follow test-first approach** - Per increment definition of done

**AFTER COMPLETING WORK:**

8. ✅ **Update increment file** - Mark user story ✅ Complete
9. ✅ **Update `BACKLOG.md`** - Remove completed task
10. ✅ **Update `STATUS.md`** - If phase completion changed

**DO NOT:**
- ❌ Start work without reading project status
- ❌ Skip increment file (even if you think you know the task)
- ❌ Guess at specifications (always link to `/docs/`)
- ❌ Forget to update project files after work

---

## 📝 Document Naming Conventions

### Increment Files

**Format:** `increment-XX.md` where XX is zero-padded number

**Examples:**
- `increment-01.md` - Backend Core (Phases 0-2)
- `increment-02.md` - Backend Business Logic (Phases 3-4)
- `increment-03.md` - Frontend Core (Phases 5-6)

### User Story References

**Format:** `US-X.Y` where X = phase number, Y = story number

**Examples:**
- `US-2.1` - Create Booking (Phase 2, Story 1)
- `US-6.3` - Edit Booking (Phase 6, Story 3)

### Status Indicators

| Symbol | Meaning | Usage |
|--------|---------|-------|
| ✅ | Complete | User story or task is done and verified |
| 🔄 | In Progress | Currently being worked on |
| ⏸️ | Pending | Not started, waiting to begin |
| 🚫 | Blocked | Cannot start due to dependency |
| ⚠️ | Issue | Has a problem or needs attention |

---

## 🎓 Example: How a User Story Flows

### US-2.1: Create Booking

**1. Defined in specification:**
- `/docs/implementation/phase-2-booking-api.md` defines the user story
- Links to BR-001, BR-002, BR-029 (business rules)
- Links to `/docs/design/api-specification.md` (endpoint details)
- Links to `/docs/specification/error-handling.md` (German errors)

**2. Planned in increment:**
- `/project/increments/increment-01.md` lists US-2.1 as first story
- Status: ⏸️ Pending initially
- Definition of done checklist provided

**3. Executed:**
- Developer/AI reads increment file
- Changes status to 🔄 In Progress
- Writes tests first (per BDD approach)
- Implements endpoint
- Tests pass, all acceptance criteria met
- Updates status to ✅ Complete

**4. Verified:**
- All tests passing
- German error messages match spec
- BR-001, BR-002, BR-029 enforced
- Type safety verified
- Code coverage ≥80%

**5. Documented:**
- Increment file updated with completion
- Any learnings noted
- Moves to US-2.2 (next story)

---

## 📚 References

**Related documentation:**
- `/CLAUDE.md` - Main AI agent instructions (will reference this folder)
- `/docs/implementation/README.md` - BDD implementation approach
- `/docs/implementation/CLAUDE.md` - Implementation workflow (7 steps)
- `/docs/architecture/README.md` - System architecture overview

---

**This folder is the heartbeat of the project. Keep it updated, and it will guide you to successful completion.**
