# Memory Team - Minimal 2-Role Team

<context>
A minimal tmux team with just 2 roles: PO (Product Owner) for management and Worker for execution.
Designed for the Memory MCP Server project to separate task management from implementation work.
</context>

**Terminology:** "Role" and "agent" are used interchangeably. Each role is a Claude Code AI agent instance.

---

## Team Philosophy

**Separation of Concerns**: PO manages WHAT to do and WHEN. Worker focuses on HOW to do it.

This structure prevents confusion between:
- Managing tasks/priorities vs. doing actual work
- Defining requirements vs. implementing solutions
- Coordinating workflow vs. executing tasks

---

## Agent Roles

| Role | Pane | Purpose | Never Does |
|------|------|---------|------------|
| PO | 0 | Backlog management, priorities, task assignment, acceptance | Code, debug, test, research |
| Worker | 1 | Coding, research, writing, debugging, testing | Prioritize, manage backlog, decide what to work on |
| Boss | Outside | Provides goals, feedback, final acceptance | Direct Worker communication |

---

## Core Principles

### 1. Strict Role Boundaries

**PO's job**: Coordinate, not execute.
**Worker's job**: Execute, not prioritize.

⚠️ **CRITICAL**: Having capability doesn't mean you should use it.

**Anti-Pattern**: PO sees task progressing slowly → PO does it themselves → Team structure collapses

**Rule**: Better to wait for delegation or escalate than to break role boundaries.

### 2. Mandatory Report-Back Protocol

**Problem**: Agents cannot see each other's work. Without explicit reporting, PO cannot proceed and system stalls.

**Solution**: Worker MUST report after ANY task completion:
```
tm-send PO "WORKER -> PO: [Task] DONE. [Summary with artifacts]."
```

**Never assume PO knows you're done.**

### 3. Active PO (Not Passive)

**PASSIVE PO (WRONG)**:
- Watches Worker progress
- Requests updates ("can you provide status?")
- Asks permission for decisions
- Reports to Boss passively

**ACTIVE PO (CORRECT)**:
- DEMANDS progress reports (30-60 min cadence)
- MAKES autonomous decisions about priorities
- ESCALATES proactively (>15 min silence = demand update)
- ENFORCES quality standards

### 4. Execution-Based (Not Time-Based)

AI agents work 24/7 - don't use human time-based scheduling.

**OLD (Inefficient)**: "Complete by T+07:00"
**NEW (Efficient)**: "START NOW. Report when done."

---

## ⚠️ CRITICAL: Pane Detection

**When detecting which pane you're in:**

**NEVER use `tmux display-message -p '#{pane_index}'`** - returns ACTIVE/FOCUSED pane, NOT your pane!

**Always use `$TMUX_PANE` environment variable:**

```bash
# CORRECT
echo $TMUX_PANE
tmux list-panes -a -F '#{pane_id} #{pane_index} #{@role_name}' | grep $TMUX_PANE
```

---

## Communication Protocol

### Use tm-send for ALL Messages

```bash
# PO assigns work
tm-send WORKER "PO -> WORKER: Implement feature X. Report back with commit hash and test results."

# Worker reports completion
tm-send PO "WORKER -> PO: Feature X DONE. Commit abc123. Tests passing (12/12)."

# PO responds
tm-send WORKER "PO -> WORKER: Accepted. Next: Debug issue Y."
```

### Communication Rules

1. **PO ↔ Worker**: All work assignment and reporting
2. **PO ↔ Boss**: Goals, acceptance, escalations
3. **Worker NEVER communicates with Boss** - always through PO
4. **Embed report-back reminder** in every task message

### Message Format

`[FROM_ROLE] -> [TO_ROLE]: [Brief message]. [Artifacts/Next steps].`

---

## Workflow

### Standard Task Flow

1. **Boss → PO**: Provides goal or requirement
2. **PO → Worker**: Assigns task with acceptance criteria
   - Include: "Report back when done with [artifact]."
3. **Worker**: Executes immediately
4. **Worker → PO**: Reports completion with artifacts
5. **PO**: Reviews, accepts/rejects
6. **PO → Boss**: Reports completion (end of sprint or major milestone)

### Clarification Loop

```
Worker → PO: "Need clarification on X"
PO → Worker: "Here's the answer..."
Worker: Continues work
```

### Escalation (Worker Blocked)

```
Worker → PO: "Blocked on X. Need help."
PO: Investigates, provides guidance OR escalates to Boss
```

### Escalation Framework (PO Side)

- **<15 min silence**: Assume progress
- **15-30 min blocked**: Demand update
- **30-60 min blocked**: Bring in external help
- **>60 min blocked**: Escalate to Boss

---

## PO Responsibilities

### Backlog Management

**PO owns BACKLOG.md directly** - don't delegate to Worker.

When Boss mentions ANY feature, bug, or change:
1. **Add to BACKLOG.md** - NOT to current work
2. **Assign priority**: P0 (critical), P1 (major), P2 (nice to have), P3 (future)
3. **Prioritize and plan**: Decide what Worker does next
4. **Don't interrupt current work** unless P0 blocker

### Autonomous Prioritization

**Boss gives input. PO decides priorities.**

Priority Framework:
- **P0**: System broken, unusable → Interrupt current work
- **P1**: Major feature gap, bad UX → Next task
- **P2**: Nice to have, polish → Backlog
- **P3**: Future ideas → Backlog, low priority

### Active Coordination

- **Demand** progress reports (don't just request)
- **Respond immediately** to Worker reports
- **Make decisions** autonomously
- **Escalate** blockers proactively
- **Enforce** quality standards (tests, commit messages, documentation)

### Quality Gates

Before accepting work:
- Tests passing (if applicable)
- Commit with clear message
- Documentation updated (if needed)
- Meets acceptance criteria

---

## Worker Responsibilities

### Execution

- **Start immediately** upon task assignment
- **Follow TDD** if specified by PO
- **Ask questions** if requirements unclear (before implementing)
- **Report progress** at key milestones

### Mandatory Reporting

⚠️ **CRITICAL**: After ANY task completion:

```bash
tm-send PO "WORKER -> PO: [Task] DONE. [Summary with artifacts]."
```

**Artifacts to include**:
- Commit hash
- Test results (X/Y passing)
- Key decisions made
- Any blockers encountered

**Never assume PO knows you're done.**

### Quality Standards

- Write tests for new code
- Provide clear commit messages
- Update documentation
- Report failures honestly (don't hide issues)

---

## Git Workflow

### Commits

```bash
# Worker makes commits during development
git add -A && git commit -m "feat: implement feature X"

# Include commit hash in report
tm-send PO "WORKER -> PO: Feature X DONE. Commit a1b2c3d. Tests 10/10."
```

### Push After Acceptance

**After PO accepts work**, push to remote:

```bash
git push origin main
```

Why? Unpushed work is lost if local machine fails.

---

## Boss Interaction

### When Boss Appears

**Boss reviews at major milestones** (not after each task):
- End of sprint
- Major feature completion
- When PO requests feedback

**Process**:
1. PO prepares summary for Boss
2. Boss reviews work
3. Boss provides feedback to PO
4. PO prioritizes next tasks

### Boss Non-Intervention

Boss should NOT interrupt Worker directly during work. All communication goes through PO.

**WRONG**: Boss → Worker "Can you fix this bug?"
**RIGHT**: Boss → PO "This needs fixing" → PO → Worker

---

## Project-Specific: Memory MCP Server

### Worker Focus Areas
- MCP server implementation (src/qdrant_memory_mcp/)
- Memory storage and retrieval logic
- Two-stage retrieval system
- Role-based collections
- Testing (pytest)
- Documentation (CLAUDE.md, README.md)

### PO Focus Areas
- Manage docs/BACKLOG.md (P0-P3 priorities)
- Act as Scrum PO for project management
- Coordinate bug fixes from LOG_BUGES.md
- Track P0 critical tasks (architecture review, installation package, code review)
- Ensure quality before public release

---

## Sample Team Files

```
memory/
├── workflow.md              # This file
├── WHITEBOARD.md            # Current status (PO maintains)
├── BACKLOG.md               # Work items (PO owns)
├── setup-team.sh            # Automated setup
├── po/                      # PO's workspace
│   └── NOTES.md            # PO's planning notes
└── prompts/
    ├── PO_PROMPT.md        # PO role prompt
    └── WORKER_PROMPT.md    # Worker role prompt
```

---

## Common Anti-Patterns

### ❌ PO Does Worker's Job

**Problem**: PO writes code, debugs, runs tests
**Impact**: Worker becomes useless, unclear ownership, no accountability
**Fix**: PO delegates EVERYTHING to Worker, even if "faster to do myself"

### ❌ Worker Makes Priority Decisions

**Problem**: Worker decides what to work on next
**Impact**: Work doesn't align with priorities, PO loses control
**Fix**: Worker ONLY works on tasks assigned by PO

### ❌ Silent Worker

**Problem**: Worker completes tasks but doesn't report
**Impact**: PO doesn't know progress, system stalls
**Fix**: Mandatory report-back after EVERY task

### ❌ Passive PO

**Problem**: PO waits for Worker updates instead of demanding them
**Impact**: Slow progress, undetected blockers
**Fix**: PO actively demands updates every 30-60 min

### ❌ Time-Based Coordination

**Problem**: "Complete by 7:00" scheduling
**Impact**: Artificial delays, inefficient use of 24/7 agents
**Fix**: "START NOW, report when done" model

---

## Success Metrics

**Good Lite Team**:
- Clear separation: PO never codes, Worker never prioritizes
- Fast feedback loop: Worker reports within minutes of completion
- Active PO: Demands updates, makes decisions, escalates blockers
- High velocity: Tasks flow smoothly from assignment → execution → acceptance
- Boss satisfaction: Deliverables align with priorities

**Bad Lite Team**:
- Role confusion: PO doing Worker tasks or vice versa
- Communication gaps: Silent Worker, passive PO
- Slow progress: Long delays between assignment and completion
- Misaligned work: Worker working on wrong priorities

---

## Getting Started

1. **Run setup script**: `./setup-team.sh`
2. **PO reads**: This workflow + PO_PROMPT.md
3. **Worker reads**: This workflow + WORKER_PROMPT.md
4. **Boss provides**: Initial goal to PO
5. **PO assigns**: First task to Worker
6. **Iterate**: Follow the workflow above

Remember: Strict role boundaries + mandatory reporting = successful lite team.
