# Human-Like Memory Skills for Claude Code - Quick Start

File-based memory system using progressive disclosure (inspired by Anthropic's Agent Skills architecture). No vector database needed - Claude reads files as needed.

## What You Get

**Global Skills** (shared across all projects):
- `coder-memory-store` - Store universal coding patterns (--coder-store)
- `coder-memory-recall` - Retrieve universal patterns (--coder-recall)

**Project Skills** (per-project templates):
- `project-memory-store` - Store project-specific insights (--project-store)
- `project-memory-recall` - Retrieve project-specific insights (--project-recall)

**Memory Types** (based on CoALA research):
- **Episodic**: Concrete events with full context (what happened, including failures)
- **Procedural**: Proven workflows and how-to steps
- **Semantic**: Distilled principles and patterns

**Key Features**:
- **Stores both successes AND failures** - failures are often more valuable
- **Auto-consolidation** - prevents duplicate garbage (MERGE/UPDATER/GENERALIZE/CREATE)
- **Cross-promotion** - project patterns can promote to universal patterns
- **Self-refactoring** - memories reorganize when structure becomes unclear

## Installation

### Step 1: Install from Your Project Directory

Open Claude Code in your project directory and say:

```
Install the memory skills from the deploy folder - read file install.md
```

Or give Claude this deploy folder and ask it to execute the installation.

### Step 2: What Gets Installed

**Global** (installed to `~/.claude/skills/`):
- `coder-memory-store/`
- `coder-memory-recall/`

**Templates** (installed to `~/.claude/skills/templates/`):
- `project-memory-store/`
- `project-memory-recall/`

**Command** (installed to `~/.claude/commands/`):
- `/create-project-memory-skills` - Creates project-specific memory skills in any project

### Step 3: Initialize Project Memory

In your current project, run:

```
/create-project-memory-skills
```

This copies the templates to `.claude/skills/` in your project.

### Step 4: Restart Claude Code

Restart Claude Code to load the new skills.

## Usage

### Storing Memories

**Universal patterns** (any project can benefit):
```
--coder-store
```

**Project-specific** (THIS codebase only):
```
--project-store
```

**Let Claude decide** (or use both):
```
--learn
```

Claude will:
1. Decide which scope (universal, project, or both)
2. Extract 0-3 insights (most conversations = 0-1)
3. Search for similar existing memories
4. Consolidate (MERGE/UPDATER/GENERALIZE/CREATE)
5. Store with proper organization

### Recalling Memories

**Universal patterns**:
```
--coder-recall [optional: query]
```

**Project-specific**:
```
--project-recall [optional: query]
```

**Let Claude decide** (or search both):
```
--recall [optional: query]
```

Claude will:
1. Decide which scope (universal, project, or both)
2. Search file tree using Grep/Read
3. Return top 3 relevant memories
4. Auto-refactor if structure is messy

### Cross-Promotion

When project patterns become universal:
- Project-memory-store automatically checks if pattern is universal
- If yes: Also stores to coder-memory
- Creates bidirectional references

## Memory Organization

### Global Memory Structure
```
~/.claude/skills/
├── coder-memory-store/
│   ├── SKILL.md
│   ├── episodic/
│   │   └── episodic.md (starts as single file, splits when needed)
│   ├── procedural/
│   │   └── procedural.md
│   └── semantic/
│       └── semantic.md
└── coder-memory-recall/
    └── SKILL.md
```

### Project Memory Structure
```
.claude/skills/
├── project-memory-store/
│   ├── SKILL.md
│   ├── episodic/
│   ├── procedural/
│   └── semantic/
└── project-memory-recall/
    └── SKILL.md
```

### Auto-Organization

- Files split when unrelated info gets stored together
- Max depth: 2 levels (e.g., `episodic/debugging/`)
- Each subdirectory has README.md (overview)
- Claude decides when to reorganize

## Consolidation Logic

| Similarity | Action | What Happens |
|-----------|--------|--------------|
| Duplicate | **MERGE** | Combine into stronger entry |
| Related | **UPDATER** | Add new info, show evolution |
| Pattern emerges | **GENERALIZE** | Episodic → Semantic promotion |
| Different | **CREATE** | New file/section |

## Example Workflow

1. **Debug a complex bug**:
   - Try multiple approaches (some fail, one succeeds)
   - Say `--project-store`
   - Claude extracts episodic memory with ALL attempts (failures + success)

2. **Similar bug happens later in different module**:
   - Say `--project-recall debugging authentication`
   - Claude finds past debugging session
   - Shows what failed and what worked

3. **Third similar bug - pattern emerges**:
   - Claude GENERALIZES: Creates semantic memory from 3 episodic entries
   - "Pattern: Always check token expiry before network retry"
   - References all 3 episodes

4. **Pattern applies to other projects**:
   - Claude cross-promotes to coder-memory (universal)
   - Now available across all your projects

## Tips

- **Be selective**: Most conversations = 0 insights worth storing
- **Include failures**: Tag with #failure - they're more valuable
- **Let Claude organize**: Trust it to split files and create structure
- **Use both scopes**: Project-specific for codebase, universal for patterns
- **Check cross-promotion**: Project patterns that work universally get promoted

## Troubleshooting

**Skills not appearing?**
- Restart Claude Code after installation

**Memories not consolidating?**
- Check that search is finding similar entries
- Claude uses Grep to search - ensure keywords match

**Structure getting messy?**
- Just use recall - it will auto-invoke refactoring if needed

**Want to reorganize manually?**
- Ask Claude to refactor the memory structure
- Or invoke general-purpose agent with refactor task

## Architecture Notes

Based on:
- **Anthropic Agent Skills**: Progressive disclosure via file tree
  - https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- **Langchain Memory article**: Episodic/Procedural/Semantic memory types
  - https://blog.langchain.dev/memory-for-agents/
- **Cognitive science**: Brain-inspired consolidation and reconsolidation

No vector database. No embeddings. Just files, folders, and Claude's intelligence.
