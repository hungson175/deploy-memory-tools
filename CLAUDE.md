# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains **Human-Like Memory Skills for Claude Code** - a persistent memory system that enables Claude to learn from past experiences, store universal coding patterns, and project-specific knowledge. Currently at **V3.2** (clean vector architecture with true two-stage retrieval). Supports both file-based navigation and optional Qdrant vector search for finding relevant memories.

## Architecture

### Core Concepts

**Memory System Design**:
- Based on Anthropic's Agent Skills architecture (progressive disclosure via file tree)
- Inspired by CoALA research on cognitive memory types (Episodic/Procedural/Semantic)
- File-based storage with automatic consolidation (MERGE/UPDATE/GENERALIZE/CREATE)
- Prevents duplicate garbage through intelligent search and consolidation

**Two-Level Memory Hierarchy**:
1. **Global Skills** (`~/.claude/skills/`) - Universal patterns shared across ALL projects
   - `coder-memory-store/` - Store universal coding patterns
   - `coder-memory-recall/` - Retrieve universal patterns

2. **Project Skills** (`.claude/skills/` per project) - Project-specific knowledge
   - `project-memory-store/` - Store project-specific insights
   - `project-memory-recall/` - Retrieve project-specific insights

**Memory Types**:
- **Episodic**: Concrete events with full context (debugging sessions, implementation stories)
- **Procedural**: Proven workflows and step-by-step processes
- **Semantic**: Distilled principles and patterns abstracted from experience

**Key Features**:
- Stores both successes AND failures (failures often more valuable)
- Auto-consolidation prevents duplicates
- Cross-promotion: project patterns can promote to universal patterns
- Self-refactoring when structure becomes unclear
- Max depth: 2 levels (e.g., `episodic/debugging/`)
- Optional Qdrant vector search enhancement (see Qdrant Integration section)

**Recall-Before-Plan Workflow**:
When starting non-trivial tasks, Claude Code should:
1. **Invoke memory recall FIRST** (using Task tool with subagent_type="general-purpose")
2. **Wait for recall results** before creating task plan
3. **Then use TodoWrite** to create plan informed by recalled memories
4. This prevents forgetting past insights and repeating past mistakes

### Directory Structure

```
deploy-memory-tools/
├── global/                           # Skills to install globally
│   ├── coder-memory-store/          # V3.x storage (legacy - still works)
│   ├── coder-memory-recall/         # V3.x retrieval (legacy - still works)
│   └── v3.2/                        # V3.2 - Current version (recommended)
│       ├── coder-memory-store/      # Two-stage retrieval, embedded config
│       ├── coder-memory-recall/     # Vector search integration
│       └── README.md                # V3.2 architecture details
├── templates/                        # Templates for project skills
│   ├── project-memory-store/        # Legacy template
│   └── project-memory-recall/       # Legacy template
├── commands/                         # Claude Code slash commands
│   └── create-project-memory-skills.md
├── docs/                             # Documentation & design
│   ├── qdrant_memory_design.md      # Vector search integration details
│   ├── crontab_setup.md             # Auto-sync scheduling
│   └── reports/                     # Migration reports
├── qdrant_storage/                   # Persistent vector database
│   └── [collections data]
├── [Development Tools]
│   ├── test_v3.2_system.py          # Full system test suite
│   ├── deploy_v3.2.sh               # Complete deployment script
│   ├── migrate_v3_to_v3.2.py        # Migration from V3 → V3.2
│   ├── migrate_memories.py          # Memory format migration
│   ├── qdrant_memory_mcp_server.py  # V1 MCP server (legacy)
│   ├── qdrant_memory_mcp_server_v2.py # V2 MCP server (current)
│   └── sync_memories.sh             # Manual vector DB sync
├── install.md                        # Legacy installation (V3)
├── QUICKSTART.md                     # Usage guide
└── README.md                         # Getting started
```

**Key Points**:
- **Current Version**: V3.2 (in `global/v3.2/`) - use this for new installations
- **Legacy Versions**: V3 and earlier in `global/` root - still functional but superseded
- **Vector Database**: Qdrant (`qdrant_storage/`) persists across sessions
- The `sample_codes/` directory (if present) contains reference implementations ONLY and has NO effect on this project

### Installation Flow

**Recommended: Use V3.2 with Qdrant vector search**

1. **Prerequisites**: Qdrant running (`docker run -p 6333:6333 qdrant/qdrant`), `.env` with `OPENAI_API_KEY`
2. **Execute**: `./deploy_v3.2.sh` (automated: tests → backup → install → MCP config → optional migration)
3. **Install MCP server**: Updated `~/.config/claude/mcp.json` to include `qdrant-memory-v2`
4. **Restart Claude Code** to load V3.2 skills with vector search enabled

**Alternative: Manual V3.2 Installation**

Follow steps in `global/v3.2/README.md` section "Installation" for step-by-step manual setup.

**Legacy: V3 Installation**

Execute `install.md` for file-based V3 setup (without vector search). Still works but less efficient.

### Memory Storage Format

**CRITICAL: Compact format** (3-5 sentences max per memory):

```
**Title:** <concise title>
**Description:** <one sentence summary>

**Content:** <3-5 sentences covering: what happened, what was tried (including failures), what worked/failed, key lesson>

**Tags:** #tag1 #tag2 #success OR #failure
```

### Consolidation Logic

| Similarity | Action | What Happens |
|-----------|--------|--------------|
| Duplicate | **MERGE** | Combine into stronger entry |
| Related | **UPDATE** | Add new info, show evolution |
| Pattern emerges | **GENERALIZE** | Episodic → Semantic promotion |
| Different | **CREATE** | New file/section |

## V3.2 Improvements (Current Version)

### What Changed from V3

| Aspect | V3 | V3.2 |
|--------|----|----|
| **Two-stage retrieval** | Documented but not implemented | Actually implemented in MCP v2 |
| **Role configuration** | Duplicated in 3 places (roles.yaml files) | Embedded directly in SKILL.md |
| **Collection names** | Inconsistent (coder-memory, backend-dev, etc.) | Clean and simple (universal-patterns, backend-patterns) |
| **MCP tool outputs** | Returns full content for every search | Previews first, full content only when requested |
| **Token efficiency** | High (returns full memories) | ~60% savings with preview-based search |
| **Architecture** | Messy mix of files and configs | Clean, consistent, single-source-of-truth |
| **Status** | Partially functional | Fully working as documented |

### Key V3.2 Features

1. **True Two-Stage Retrieval**:
   - Search returns lightweight previews (title, description, metadata)
   - Agent reviews previews and selects relevant ones
   - Only selected memories retrieved in full (saves ~60% tokens)
   - Zero token waste on full content retrieval

2. **Embedded Configuration**:
   - No external `roles.yaml` files
   - Role config embedded in each SKILL.md
   - Single source of truth per skill
   - Cleaner directory structure

3. **Simplified Collections**:
   - Global: `universal-patterns`, `backend-patterns`, `frontend-patterns`, etc.
   - Project: `proj-{project-name}`
   - Consistent naming across all integrations

4. **Intelligent Consolidation** (Agent-Driven):
   - No rigid thresholds
   - Agent decides MERGE/UPDATE/GENERALIZE/CREATE based on context
   - Better handling of nuanced relationships between memories

### When to Use Each Version

- **New projects**: Always use V3.2 (better architecture, lower costs)
- **Existing V3 deployments**: Run `python3 migrate_v3_to_v3.2.py` to upgrade
- **V3 reference**: Use V3 source in `global/` for backwards compatibility testing only

## Learning Signals & Feedback Recognition

### The Key Principles

1. **I Am The Intelligence**: Not the vector DB, not the search algorithm - Claude decides what matters.

2. **Your Feedback Is My Evolution**: Strong emotional reactions are the strongest learning signals.

3. **Failures > Successes**: Learn more from what frustrates users than what works smoothly.

4. **Adaptation Over Storage**: Better to adapt behavior than store everything.

5. **Your Patterns Matter Most**: Learning user-specific style > generic best practices.

### Trigger Words for Strong Learning Signals

When users express strong emotions (especially frustration or anger), these are **CRITICAL learning signals** that something went wrong and should be stored as episodic memory. Recognize these trigger words:

**Profanity & Curses**:
- fuck, fucking, shit, damn, hell, crap, bastard, asshole, bitch
- wtf, omfg, ffs, jfc

**Expressions of Frustration**:
- moron, idiot, stupid, dumb, garbage, trash, useless, terrible
- awful, horrible, worst, sucks, broken, failed, disaster

**Strong Negative Emotions**:
- hate, angry, frustrated, pissed, annoyed, irritated
- disappointed, pathetic, ridiculous, absurd

**Emotional Outbursts**:
- "are you kidding me", "seriously?", "what the hell"
- "this is ridiculous", "this makes no sense", "why would you"
- "that's not what I asked", "you're not listening"

**Action on Detection**:
When these trigger words appear in user feedback:
1. **Immediately recognize** this as a high-value learning moment
2. **Store as episodic memory** with full context of what went wrong
3. **Include both the failed approach AND what was tried** - failures are more valuable than successes
4. **Tag with #failure and #strong-signal** for future reference
5. **Be selective** - still apply the 0-3 insights rule, but prioritize these moments

**Example Episodic Memory**:
```
**Title:** Claude Misunderstood File Context Leading to Wrong Implementation
**Description:** User said "you fucking moron" when Claude edited wrong file despite clear context.

**Content:** User requested updating authentication logic in src/auth.ts but Claude modified src/utils.ts instead. Failed because: didn't carefully read which file user was referring to. User's strong emotional reaction (profanity) indicated critical failure. Key lesson: Always verify file context before making changes, especially when user provides specific file names. Strong user emotions = immediate signal to store this failure pattern.

**Tags:** #failure #strong-signal #episodic #file-context #attention-to-detail
```

## Development Workflow

### Testing & Validation

**Run V3.2 system tests** (validates two-stage retrieval, Qdrant integration):
```bash
# Prerequisites: Qdrant running on localhost:6333, .env with OPENAI_API_KEY
python3 test_v3.2_system.py
```

**Full deployment with tests** (includes backup, installation, migration):
```bash
# Backs up existing skills, installs V3.2, updates MCP config, optionally migrates from V3
./deploy_v3.2.sh
```

### Common Commands

**Install V3.2 (Current Version)**:
```bash
# Quick install (manual steps)
mkdir -p ~/.claude/skills
cp -r global/v3.2/coder-memory-store ~/.claude/skills/
cp -r global/v3.2/coder-memory-recall ~/.claude/skills/

# Install MCP server v2 (for Qdrant integration)
mkdir -p ~/scripts
cp qdrant_memory_mcp_server_v2.py ~/scripts/
chmod +x ~/scripts/qdrant_memory_mcp_server_v2.py
```

**Migrate from V3 to V3.2**:
```bash
# Automatic migration (remaps collections, preserves all memories)
python3 migrate_v3_to_v3.2.py

# Inspect results
tail -n 50 /tmp/v3.2_migration.log
```

**Sync Qdrant with file system** (recreates vector database from current files):
```bash
./sync_memories.sh
# Check: tail -n 20 sync.log
```

**CRITICAL: Avoid Nested Directories** during manual installation:
- WRONG: `cp -r global/v3.2/coder-memory-store ~/.claude/skills/` (creates nested dirs)
- CORRECT: `cp -r global/v3.2/coder-memory-store/* ~/.claude/skills/coder-memory-store/` (flat structure)

Always verify with `ls ~/.claude/skills/` that structure is FLAT after installation.

### Usage Commands

Users interact with skills via special flags:

**Storing memories**:
- `--coder-store` - Store universal patterns
- `--project-store` - Store project-specific insights
- `--learn` - Let Claude decide scope (may use both)

**Recalling memories**:
- `--coder-recall [query]` - Retrieve universal patterns
- `--project-recall [query]` - Retrieve project-specific insights
- `--recall [query]` - Let Claude decide scope (may search both)

**Creating project memory skills**:
- `/create-project-memory-skills` - Copy templates to `.claude/skills/` in current project

## Important Implementation Notes

1. **Memory Structure Initialization**: Skills must check if memory directories exist and initialize them with single files (`episodic.md`, `procedural.md`, `semantic.md`) in each memory type directory.

2. **File Organization**: When files become "too long" with unrelated info, split into subdirectories with topic names. Each subdirectory gets a README.md as overview. Max depth is 2 levels.

3. **Search Strategy**: Use Grep to search for keywords, then Read to load promising files. Follow progressive disclosure: read READMEs first, then specific files.

4. **Consolidation**: Always search for similar memories before storing. Use MERGE/UPDATE/GENERALIZE/CREATE actions to prevent duplicates.

5. **Cross-Promotion**: When project-memory-store identifies universal patterns, it should also store to coder-memory-store with bidirectional references.

6. **Recall Execution**: coder-memory-recall and project-memory-recall MUST be executed using Task tool with subagent_type="general-purpose" to avoid polluting main context.

7. **Self-Maintenance**: Recall skills automatically trigger refactoring if memory structure becomes messy (>5 file reads to find relevant memories, duplicates found, unrelated content mixed).

## Code Organization & Development Patterns

### Key Files to Understand

**V3.2 Implementation** (current recommended version):
- `global/v3.2/README.md` - Architecture decisions and design rationale
- `global/v3.2/coder-memory-store/SKILL.md` - Two-stage storage with embedded config
- `global/v3.2/coder-memory-recall/SKILL.md` - Vector search + file-based fallback
- `docs/qdrant_memory_design.md` - Detailed MCP server implementation

**Development & Testing**:
- `test_v3.2_system.py` - Full integration test suite (requires Qdrant + OpenAI API)
- `deploy_v3.2.sh` - Production deployment script (tests → backup → install)
- `migrate_v3_to_v3.2.py` - Collection remapping and memory migration
- `qdrant_memory_mcp_server_v2.py` - MCP server implementation (two-stage retrieval)

**Compatibility & Migration**:
- `global/v3/` - Legacy V3 implementation (file-based, no MCP server)
- `qdrant_memory_mcp_server.py` - Legacy MCP server v1 (for reference)
- `migrate_memories.py` - Memory format conversions (if needed)

### Design Patterns

1. **Memory Consolidation**:
   - Search for similar memories BEFORE storing
   - Agent decides: MERGE (duplicate) vs UPDATE (related) vs GENERALIZE (pattern) vs CREATE (new)
   - Always preserve failure context - failures are more valuable than successes

2. **Two-Stage Retrieval** (V3.2):
   - Phase 1: `search_memory()` returns previews (title, description, metadata)
   - Phase 2: Agent selects relevant ones → `batch_get_memories()` fetches full content
   - Benefit: 60% token savings on irrelevant memories

3. **Role-Based Organization**:
   - Each skill detects task context (API work → backend, React → frontend, trading → quant)
   - Collections organized by role for focused recalls
   - Prevents dilution when searching (100 memories vs 1000+)

4. **Progressive Disclosure**:
   - Start with README (overview)
   - Then read specific files (episodic/debugging/, procedural/testing/, etc.)
   - Load full memories only when relevant (lazy loading principle)

### When Developing Changes

- **Test first**: `python3 test_v3.2_system.py` to ensure Qdrant connectivity
- **Backup before deploy**: `./deploy_v3.2.sh` creates automatic backups
- **Migration testing**: `python3 migrate_v3_to_v3.2.py` validates collection mapping
- **Vector sync**: `./sync_memories.sh` ensures Qdrant stays in sync with files
- **MCP integration**: Test via Claude Code using memory recall/store flags

## File References

Key documentation files:
- **Getting Started**: `README.md`, `QUICKSTART.md:1-50`
- **V3.2 Architecture**: `global/v3.2/README.md:1-100`
- **Installation**: `install.md` (V3), `deploy_v3.2.sh` (V3.2 automated)
- **Storage Logic**: `global/v3.2/coder-memory-store/SKILL.md`
- **Recall Logic**: `global/v3.2/coder-memory-recall/SKILL.md`
- **MCP Design**: `docs/qdrant_memory_design.md`
- **Command**: `commands/create-project-memory-skills.md`

## Qdrant Integration (Recommended)

**Status**: V3.2 fully integrated with Qdrant MCP server v2. Two-stage retrieval implemented and tested.

**Architecture**:
- **Service**: Runs on localhost:6333 as persistent Docker container
- **Collections**:
  - **Global**: `universal-patterns`, `backend-patterns`, `frontend-patterns`, `quant-patterns`, `devops-patterns`, `ml-patterns`, `security-patterns`, `mobile-patterns`
  - **Project**: `proj-{sanitized-project-name}`
- **Vector Model**: OpenAI text-embedding-3-small (1536 dimensions, Cosine similarity)
- **Metadata Fields**: memory_level, memory_type, file_path, skill_root, tags, title, created_at, last_synced

**MCP Server V2 Tools** (via `~/.config/claude/mcp.json`):
- `search_memory(query, level, role?)` → Returns previews only (saves 60% tokens)
- `get_memory(doc_id, level, role?)` → Full content retrieval
- `batch_get_memories(doc_ids, level, role?)` → Efficient multi-fetch

**Key Principle**:
- **Source of Truth**: Files in `~/.claude/skills/` and `{project}/.claude/skills/` (always)
- **Qdrant Role**: Search optimization index (may be slightly stale)
- **Fallback**: Skills work perfectly if Qdrant unavailable (slower file-based search)
- **Query Strategy**: Use full context/memory text (not just keywords) for better semantic matching

**Sync Strategy** (keeps Qdrant in sync with files):
- **Automatic**: Crontab job runs Monday 11AM to recreate vector database
  - Setup: `bash docs/crontab_setup.md`
  - Check logs: `tail -n 20 sync.log`
- **Manual**: `./sync_memories.sh` triggers immediate full sync
- **Optional Dual-Write**: Skills can update Qdrant on store (Phase 4), but file writes are primary

**Reference**: See `docs/qdrant_memory_design.md` for implementation details, MCP protocol, and role-based collection strategy.

---

## Success Criteria After Installation

### After V3.2 Installation (Recommended)

These files and services must exist:
- **Skills**: `~/.claude/skills/coder-memory-store/SKILL.md` (V3.2)
- **Skills**: `~/.claude/skills/coder-memory-recall/SKILL.md` (V3.2)
- **MCP Server**: `~/scripts/qdrant_memory_mcp_server_v2.py` (installed and executable)
- **MCP Config**: `~/.config/claude/mcp.json` contains `qdrant-memory-v2` server entry
- **Vector DB**: `qdrant_storage/` directory exists (may be empty, will populate on first use)
- **Services**: Qdrant running on `localhost:6333` (verify: `curl http://localhost:6333/collections`)

### After Project Initialization

In your project directory:
- `.claude/skills/project-memory-store/SKILL.md` (created via `/create-project-memory-skills`)
- `.claude/skills/project-memory-recall/SKILL.md` (created via `/create-project-memory-skills`)

### After Migration (V3 → V3.2)

Run `python3 migrate_v3_to_v3.2.py` to verify:
- Legacy V3 memories preserved
- Collections renamed (coder-memory → universal-patterns, etc.)
- Qdrant populated from migrated memories
- Check logs: `/tmp/v3.2_migration.log`
