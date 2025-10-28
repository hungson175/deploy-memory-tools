# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains **Human-Like Memory Skills for Claude Code** - a file-based memory system that allows Claude to store and recall universal coding patterns and project-specific knowledge across conversations. No vector database or embeddings required - just files, folders, and Claude's intelligence.

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

### Directory Structure

```
deploy-memory-tools/
├── global/                           # Global skills to install
│   ├── coder-memory-store/          # Universal pattern storage
│   │   └── SKILL.md
│   └── coder-memory-recall/         # Universal pattern retrieval
│       └── SKILL.md
├── templates/                        # Templates for project skills
│   ├── project-memory-store/
│   │   └── SKILL.md
│   └── project-memory-recall/
│       └── SKILL.md
├── commands/                         # Claude Code slash commands
│   └── create-project-memory-skills.md
├── install.md                        # Installation instructions
├── QUICKSTART.md                     # Usage guide
└── README.md                         # Quick start guide
```

### Installation Flow

1. User copies this directory to their working project
2. Claude executes `install.md` which:
   - Installs global skills to `~/.claude/skills/`
   - Installs templates to `~/.claude/skills/templates/`
   - Installs `/create-project-memory-skills` command to `~/.claude/commands/`
   - Initializes project memory in current directory's `.claude/skills/`
3. User restarts Claude Code to load skills

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

## Common Commands

### Installation

**Execute the installation**:
```bash
# Install global skills
mkdir -p ~/.claude/skills/coder-memory-store
cp -r global/coder-memory-store/* ~/.claude/skills/coder-memory-store/

mkdir -p ~/.claude/skills/coder-memory-recall
cp -r global/coder-memory-recall/* ~/.claude/skills/coder-memory-recall/

# Install templates
mkdir -p ~/.claude/skills/templates/project-memory-store
cp -r templates/project-memory-store/* ~/.claude/skills/templates/project-memory-store/

mkdir -p ~/.claude/skills/templates/project-memory-recall
cp -r templates/project-memory-recall/* ~/.claude/skills/templates/project-memory-recall/

# Install command
mkdir -p ~/.claude/commands
cp commands/create-project-memory-skills.md ~/.claude/commands/create-project-memory-skills.md

# Initialize project memory (or use /create-project-memory-skills after restart)
mkdir -p .claude/skills/project-memory-store
cp -r ~/.claude/skills/templates/project-memory-store/* .claude/skills/project-memory-store/

mkdir -p .claude/skills/project-memory-recall
cp -r ~/.claude/skills/templates/project-memory-recall/* .claude/skills/project-memory-recall/
```

**CRITICAL: Avoid Nested Directories**:
- WRONG: `cp -r deploy/global/coder-memory-store ~/.claude/skills/` (creates nested dirs)
- CORRECT: `cp -r deploy/global/coder-memory-store/* ~/.claude/skills/coder-memory-store/` (flat structure)

Always verify with `ls` that structure is FLAT after installation.

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

## File References

Key documentation files:
- Installation instructions: `install.md`
- Usage guide: `QUICKSTART.md:1-221`
- Storage skill logic: `global/coder-memory-store/SKILL.md:1-207`
- Recall skill logic: `global/coder-memory-recall/SKILL.md:1-172`
- Command definition: `commands/create-project-memory-skills.md:1-18`

## Success Criteria After Installation

All these files must exist:
- `~/.claude/skills/coder-memory-store/SKILL.md`
- `~/.claude/skills/coder-memory-recall/SKILL.md`
- `~/.claude/skills/templates/project-memory-store/SKILL.md`
- `~/.claude/skills/templates/project-memory-recall/SKILL.md`
- `~/.claude/commands/create-project-memory-skills.md`
- `.claude/skills/project-memory-store/SKILL.md` (in project directory)
- `.claude/skills/project-memory-recall/SKILL.md` (in project directory)
