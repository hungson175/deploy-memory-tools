# Qdrant Memory Skills Design

**Date:** 2025-10-30
**Status:** Qdrant populated (72 memories), Skills not yet modified

---

## THE MAIN PRINCIPLE

**Vector search is an ADDITIONAL tool to help find similar memories. They may be wrong/not updated to reality. File-based navigation is the PRIMARY method - it works great and will continue to work.**

**Source of Truth**: Files in `~/.claude/skills/` AND `{project}/.claude/skills/` (always)

**Qdrant Role**:
- Fast semantic lookup helper (supplementary)
- May be wrong/outdated if files changed
- Suggests keywords or file hints
- **Don't trust 100%**

---

## What Qdrant Adds

### Current System (Works Fine)

User: `--coder-recall pytest fixtures`
→ Claude Code navigates files using Grep/Read/Glob
→ Returns relevant memories

### With Qdrant (Optional Enhancement)

User: `--coder-recall pytest fixtures`
→ **Optional**: Try vector search first for file hints
→ Claude Code navigates files (using hints if available)
→ Returns relevant memories

**Key**: Vector search just provides hints. Everything else stays the same.

---

## Qdrant Configuration

### Collections

**Global**: `coder-memory` (72 memories)
**Project**: `proj-{project-name}` (not yet created)

### Metadata Structure

```json
{
  "document": "<full memory text>",
  "metadata": {
    "memory_level": "coder|project",
    "memory_type": "episodic|procedural|semantic",
    "file_path": "episodic/debugging.md",
    "skill_root": "coder-memory-store",
    "tags": ["success", "pytest"],
    "title": "Memory Title",
    "created_at": "2025-10-30T...",
    "last_synced": "2025-10-30T..."
  }
}
```

**IMPORTANT**: Not just `file_path`, but ALL metadata may be stale. Files are source of truth.

---

## Integration Approach

### For Recall Skills

**Add Phase 0** (optional vector search for file hints):

```markdown
## PHASE 0: Try Vector Search (Optional)

If Qdrant available, try semantic search for file hints:
- Construct query (3-8 keywords)
- Call search_doc(query, "coder-memory", limit=5)
- Extract file_path hints from results
- If <3 results or unavailable: Skip to Phase 1

Note: Vector results may be outdated. Verify by reading files.
```

**Keep everything else the same.**

### For Store Skills

**Two enhancements needed:**

**1. In PHASE 2 (Search for Similar Memories)** - Add optional vector search:

```markdown
## PHASE 2: Search for Similar Memories

**Optional**: If Qdrant available, try semantic search first:
- Construct query from new memory (title + key concepts)
- Call search_doc(query, "coder-memory", limit=5)
- Get similar memory hints with file paths

**Then proceed with file-based search** (as before):
- Use Grep to search for keywords (using hints if available)
- Read files with potential matches
- Check similarity
```

**2. In PHASE 4 (Store Memory)** - Add optional dual-write:

```markdown
## PHASE 4: Store Memory

[Existing file write logic]

**Optional**: If Qdrant available, also store to vector DB:
- Generate embedding
- Insert with metadata
- If fails: Warn but continue (file is source of truth)
```

---

## Sync Strategy

**Manual sync** (user runs periodically):

```bash
# Clear and re-populate
curl -X DELETE http://localhost:6333/collections/coder-memory
python3 migrate_memories.py
```

---

## Current Status

### ✅ Done
- Qdrant running (localhost:6333)
- Collection `coder-memory` created
- 72 memories migrated
- Migration script works

### ❌ Not Done
- SKILL.md files not modified
- No Qdrant tools configured (use direct API or ReasoningBank's MCP)
- No project collections yet
- No dual-write in store skills

---

## Next Steps

1. **Test vector search manually** - verify quality before integrating
2. **Choose access method**: Direct API (curl) or ReasoningBank MCP server
3. **Optionally update SKILL.md** - add Phase 0 if testing looks good
4. **Optionally add dual-write** - store to Qdrant after file write

---

## Key Takeaways

1. File-based navigation is primary (works great)
2. Vector search is supplementary (just hints)
3. Files are always source of truth
4. Keep integration minimal
5. Make it optional (doesn't break if unavailable)
6. Trust Claude Code to use intelligently

---

## MCP Server Tools (Full CRUD + Search)

The Qdrant MCP server provides complete CRUD operations plus semantic search:

### 1. **search_memory(query, memory_level, limit=5)**
- Semantic search for similar memories
- Returns file_path hints, similarity scores, titles, metadata
- Collection auto-selected based on memory_level

### 2. **store_memory(document, metadata, memory_level)**
- Insert new memory with rich metadata
- Auto-creates collection if not exists
- Returns document ID and status

### 3. **update_memory(doc_id, document, metadata, memory_level)**
- Update existing memory (for MERGE/UPDATE consolidation)
- Regenerates embedding with new content
- Returns success status

### 4. **get_memory(doc_id, memory_level)**
- Retrieve full memory by ID
- Used for reading existing memory before merging
- Returns document text and metadata

### 5. **delete_memory(doc_id, memory_level)**
- Delete memory by ID (for cleanup or consolidation)
- Returns updated points count
- Used when merging duplicates

**Note**: Update = delete + insert new (Qdrant upserts by ID, regenerating embedding)

**Current state**: Qdrant ready with 72 memories, skills updated to use optional vector search.
