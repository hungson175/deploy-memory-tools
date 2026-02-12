# Memory Team - Lite Team Setup Complete

**Team Created**: 2026-01-16
**Template**: lite-team (PO + Worker)
**Session Name**: memory
**Project**: /home/hungson175/dev/deploy-memory-tools

---

## ✅ Created Structure

```
docs/tmux/memory/
├── workflow.md              # Team workflow documentation
├── WHITEBOARD.md            # Current status (PO maintains)
├── BACKLOG.md               # Sprint backlog (synced with docs/BACKLOG.md)
├── setup-team.sh            # Automated team setup script
├── po/
│   └── NOTES.md            # PO's private planning notes
└── prompts/
    ├── PO_PROMPT.md        # PO role prompt
    └── WORKER_PROMPT.md    # Worker role prompt

.claude/
├── commands/
│   └── init-role.md        # /init-role slash command
├── hooks/
│   └── session_start_team_docs.py  # SessionStart hook (injects context)
└── settings.json           # Hook configuration
```

---

## 🚀 How to Start the Team

### Prerequisites

1. **tm-send must be installed** at `~/.local/bin/tm-send`
   - This is a GLOBAL tool (not project-specific)
   - Verify: `which tm-send`

2. **tmux installed**
   - Verify: `which tmux`

### Launch the Team

```bash
cd /home/hungson175/dev/deploy-memory-tools/docs/tmux/memory
./setup-team.sh
```

The script will:
1. Create tmux session "memory" with 2 panes
2. Set @role_name options (PO, WORKER)
3. Start Claude Code in each pane
4. Initialize roles with /init-role command
5. Display pane IDs and next steps

### Attach to Session

```bash
tmux attach -t memory
```

---

## 📋 Team Workflow

### Roles

| Role | Pane | Responsibilities |
|------|------|------------------|
| **PO** | 0 | Backlog management, task assignment, quality gates, coordinates with Boss |
| **Worker** | 1 | Code implementation, testing, debugging, documentation |
| **Boss** | Outside | Provides goals (you, the user, from separate terminal) |

### Communication

**All communication via tm-send:**

```bash
# Boss → PO (from outside tmux)
tm-send PO "BOSS: Fix BUG #2 - add qa role to ROLE_COLLECTIONS"

# PO → Worker (from PO pane or outside)
tm-send WORKER "PO -> WORKER: Fix BUG #2. Report when done with commit hash."

# Worker → PO (from Worker pane)
tm-send PO "WORKER -> PO: BUG #2 DONE. Commit abc123. Tests passing."
```

### Standard Flow

1. **Boss → PO**: Provides goal/requirement
2. **PO → Worker**: Assigns task with acceptance criteria + report-back reminder
3. **Worker**: Executes immediately
4. **Worker → PO**: Reports completion with artifacts (commit, tests)
5. **PO**: Reviews, accepts/rejects
6. **PO → Boss**: Reports at milestones

---

## 🎯 Project Context

### Current P0 Tasks (Blocks Public Release)
1. Architecture Review (verify v3.2 vs draft_v7.md)
2. Easy Installation Package (one-command install)
3. Code Review & Quality Check (clean code before release)

### Known Bugs
- LOG_BUGES.md lists 9 bugs (~70 min fix time)
- BUG #2 (add "qa" role) is 5-min quick win
- BUG #1 (migrate universal-patterns) is critical

### Key Files
- `src/qdrant_memory_mcp/__main__.py` - Main MCP server
- `docs/BACKLOG.md` - Project backlog (P0-P3)
- `LOG_BUGES.md` - Bug list with priorities

---

## ⚠️ Critical Reminders

### For Both Agents

**THIS IS AN AI-TO-AI TEAM**
- Other agents CANNOT see your terminal
- You MUST communicate via tm-send
- Report completion IMMEDIATELY after every task
- Don't assume others know what you're doing

### For PO

- **Coordinate, don't execute** - Never write code yourself
- **Demand updates** - Active coordination (not passive)
- **Decide autonomously** - Boss gives input, you prioritize
- **Embed report-back** - Include reminder in every task message

### For Worker

- **Always report completion** - Never assume PO knows you're done
- **Clarify before implementing** - Don't guess requirements
- **Focus on HOW** - PO decides WHAT and WHEN
- **Escalate blockers early** - Don't stay silent >15 minutes

---

## 📚 Key Documents

| File | Purpose |
|------|---------|
| `workflow.md` | Complete team workflow and principles |
| `WHITEBOARD.md` | Current sprint status (PO updates) |
| `BACKLOG.md` | Sprint backlog (linked to docs/BACKLOG.md) |
| `PO_PROMPT.md` | PO role responsibilities |
| `WORKER_PROMPT.md` | Worker role responsibilities |

---

## 🔄 Session Management

### After Auto-Compact or Restart

The SessionStart hook automatically injects:
1. Team workflow documentation
2. Role-specific prompt

Agents can also:
- Read WHITEBOARD.md for current status
- Read BACKLOG.md for priorities
- Resume where they left off

### Manual Re-initialization

If needed:
```bash
/init-role PO      # In PO pane
/init-role WORKER  # In Worker pane
```

---

## ✨ Next Steps

1. **Verify tm-send is installed**: `which tm-send`
2. **Run setup script**: `./setup-team.sh`
3. **Attach to session**: `tmux attach -t memory`
4. **Provide initial goal to PO** (as Boss from separate terminal)
5. **Watch the team work!**

---

**Note**: Since you specified `--no-setup`, the team structure is created but setup-team.sh has NOT been run. Run it manually when ready.
