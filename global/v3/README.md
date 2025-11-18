# V3 Memory Skills - Vector-First Architecture

## Overview

This directory contains V3 memory skills that implement **vector-first architecture** with files as lightweight query guides (Table of Contents).

**Key Change**: All memory content lives in Qdrant vector database. Files store ONLY configuration and query instructions (~4KB total, constant size).

---

## Files

```
global/v3/
├── README.md (this file)                    # Overview
├── roles.yaml                                # Role/collection configuration (template)
├── coder-memory-recall/
│   ├── SKILL.md                             # Recall skill implementation
│   └── roles.yaml                           # Role config (copied for relative reference)
└── coder-memory-store/
    ├── SKILL.md                             # Store skill implementation
    └── roles.yaml                           # Role config (copied for relative reference)
```

**Note**: `roles.yaml` is copied into each skill directory to enable relative path references for portability. The file is updated dynamically by Claude Code when new roles or tags are discovered during memory operations.

---

## Architecture Changes from V2

| Aspect | V2 | V3 |
|--------|---|-----|
| **Memory storage** | Files (actual content) | Vector DB (actual content) |
| **File system** | Progressive disclosure tree | Query guides (ToC) |
| **Search** | Grep + Read (3-5+ files) | Single vector query |
| **Role isolation** | None (mixed) | Separate collections |
| **Cost** | High (file reads expensive) | Low (ToC + vector query) |
| **Dependencies** | Optional (graceful degradation) | Required (Qdrant MCP) |

---

## Role-Based Collections

V3 uses separate Qdrant collections for different roles:

- **`coder-memory`** - Universal patterns (framework/project-agnostic)
- **`backend-dev`** - Backend engineering (APIs, databases, auth, etc.)
- **`frontend-dev`** - Frontend engineering (React, UI, state management, etc.)
- **`financial-engineer`** - Quantitative finance (trading, backtesting, risk, etc.)

**Benefits**:
- Clean memory isolation per domain
- Prevents cross-role pollution
- Targeted recalls (search only relevant collection)

---

## Memory Format (Unchanged)

**CRITICAL**: Compact format enforced (3-5 sentences MAX)

```
**Title:** <concise title>
**Description:** <one sentence summary>

**Content:** <3-5 sentences covering: what happened, what was tried (including failures), what worked/failed, key lesson>

**Tags:** #tag1 #tag2 #success OR #failure
```

---

## Recall Operation (Simplified)

**V2** (Progressive Disclosure):
1. Read SKILL.md
2. Read README.md in memory type directory
3. Use Grep to search keywords
4. Read targeted files (3-5+ reads)
5. Extract top 3 memories

**V3** (Vector-First):
1. Read SKILL.md + roles.yaml (~4KB total)
2. Identify role from task context
3. Construct 2-3 sentence semantic query
4. Query vector DB with role filter via MCP memory server
5. Get top 10 results (previews: title + summary)
6. Select relevant memories and retrieve full content via get_memory()

**Cost savings**: ~4KB ToC read + lightweight vector search vs 3-5+ heavy file reads

---

## Store Operation (Simplified)

**V2** (File-Based Consolidation):
1. Extract insights
2. Grep search for similar memories
3. Read files with potential matches
4. MERGE/UPDATE/GENERALIZE/CREATE via file edits
5. Dual-write to Qdrant (optional)

**V3** (Vector-Based Consolidation):
1. Extract insights
2. Query vector DB with full memory text via MCP memory server
3. Agent reviews search results and decides action using intelligence (no fixed thresholds)
4. MERGE/UPDATE/GENERALIZE/CREATE via MCP memory tools
5. No file writes (except rare query guide updates)

**Consolidation Decisions** (Agent uses judgment):
- **MERGE**: Near-duplicate content covering same experience
- **UPDATE**: Related memory on same topic needing enhancement
- **GENERALIZE**: Pattern emerges from 2+ similar episodic memories
- **CREATE**: Different topic or orthogonal approach

Agent decides based on semantic similarity, contextual match, and content overlap - no rigid thresholds.

---

## MCP Tools Required

V3 requires the **MCP memory server** (Qdrant-backed) with these tools:

- `search_memory(query, memory_level, limit)` - Semantic search returning lightweight previews (title + summary only, like Google search)
- `get_memory(doc_id, memory_level)` - Retrieve full content for selected memories
- `store_memory(document, metadata, memory_level)` - Create new memory
- `update_memory(doc_id, document, metadata, memory_level)` - Update existing (regenerates embedding)
- `delete_memory(doc_id, memory_level)` - Remove duplicates

**Two-Stage Retrieval Architecture**:
1. `search_memory()` returns previews with {doc_id, title, description, similarity, tags}
2. Agent reviews previews and decides which memories are relevant
3. `get_memory()` retrieves full content only for selected memories

This approach minimizes token usage and gives the agent control over what to retrieve.

---

## Migration from V2

**Before installing V3**:

1. **Backup V2 skills**: `~/.claude/backup/skills/memory/`
2. **Migrate memories to vector DB**: Read all V2 files, classify by role, insert into Qdrant new collections (roles)
3. **Replace V2 with V3**: Copy V3 skills to `~/.claude/skills/`
4. **Restart Claude Code**: Load new skills

**Migration script** (to be implemented):
```bash
# Read all memories from V2 file-based storage
# Classify each by role (backend-dev, frontend-dev, etc.)
# Insert into appropriate Qdrant collection
# Verify migration success
```

---

## Testing V3 Skills

**Test Recall**:
1. User says "--recall" or starts complex task
2. Skill should auto-invoke
3. Query vector DB with role filter
4. Return relevant memories

**Test Store**:
1. Complete difficult task with non-obvious solution
2. User says "--learn" or skill auto-invokes
3. Extract 0-3 insights
4. Search vector DB for similar memories
5. Consolidate (MERGE/UPDATE/GENERALIZE/CREATE)
6. Store to appropriate collection(s)

---

## Future Enhancements (V3.1+)

- **Forgetting mechanism**: Track `last_recall_time`, archive memories >30 days no recall
- **Cross-promotion automation**: Auto-promote role-specific → universal `coder` collection when pattern detected
- **Custom UI**: Build web interface for memory browsing/visualization
- **Export/backup**: Periodic vector DB → markdown files for backup

---

## Notes

- **No graceful degradation**: V3 requires Qdrant (hard dependency)
- **File size constant**: ~4KB regardless of memory count (vs V2's linear growth)
- **Auto-invocation**: Skills activate based on task context (no explicit Task tool call)
- **Compact format critical**: 3-5 sentences enforced to prevent vector DB bloat
- **Hybrid validation**: Vector similarity + LLM context check for accurate consolidation

---

## References

- V3 Architecture Review: `docs/v3/review_v3.03.md`
- V2 Implementation: `~/.claude/backup/skills/memory/`
- Qdrant Integration: `docs/qdrant_memory_design.md`
