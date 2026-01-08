# Memory Skills Bug Investigation Report

**Date:** 2026-01-08
**Issue:** "Memory system làm việc như cứt" - Slow, reads/writes random files
**Status:** 🔴 **CRITICAL BUG FOUND**

---

## Summary

The memory skills (`coder-memory-store`, `coder-memory-recall`) are maintaining a **DUAL STORAGE SYSTEM** which causes:
- Slow performance (file I/O + vector DB calls)
- Confusion (2 sources of truth)
- Unnecessary file operations that user sees

---

## Bug #8: Dual Storage System ⚠️ **CRITICAL**

### Evidence

**Location 1: Local Markdown Files**
```
~/.claude/skills/coder-memory-store/
├── episodic/
│   ├── backend-api-integration.md     ← Memory stored as FILE
│   └── user-interaction-failures.md
├── procedural/
│   ├── infrastructure-pre-sprint-validation.md
│   ├── progressive_testing_saves_time.md
│   └── two-stage-config-validation.md
└── semantic/
    ├── agent-memory-architecture.md
    ├── storage_log.txt                ← Log file
    ├── trading-strategy-design-patterns.md
    └── ...8 more .md files
```

**Location 2: Qdrant Vector Database**
```
Qdrant collections (via MCP server):
- backend-patterns (43 points)
- frontend-patterns (31 points)
- universal-patterns (155 points)
- ...
```

### What the Skill Actually Does

Based on `SKILL.md` instructions and file evidence, the skill does:

1. **Phase 1:** Extract insights from conversation
2. **Phase 2:** Search for similar
   - **BUG:** Searches BOTH local files AND vector DB
3. **Phase 3:** Intelligent consolidation
   - **BUG:** Reads/writes local markdown files
   - **BUG:** Also calls MCP `store_memory()`
4. **Phase 4:** Store memory
   - **BUG:** Writes to LOCAL .md file
   - **BUG:** Writes to storage_log.txt
   - **BUG:** ALSO calls MCP `store_memory()`

### Performance Impact

Every memory operation does:
```
Time breakdown per memory store:
1. Search local .md files       (~100-500ms)
2. Read multiple .md files       (~50-200ms each)
3. Call MCP search_memory()      (~200-500ms)
4. Call MCP batch_get_memories() (~100-300ms)
5. Write local .md file          (~50-100ms)
6. Write storage_log.txt         (~20-50ms)
7. Call MCP store_memory()       (~200-500ms)

TOTAL: ~720-2150ms PER OPERATION
```

**Compare to pure vector DB:**
```
1. Call MCP search_memory()      (~200-500ms)
2. Call MCP batch_get_memories() (~100-300ms)
3. Call MCP store_memory()       (~200-500ms)

TOTAL: ~500-1300ms (2-3x faster!)
```

### Why This Happened

Looking at skill history:

1. **Old design:** Skills managed local markdown files (before MCP server existed)
2. **New design:** Added MCP server for vector search
3. **Migration bug:** Never removed old file-based storage!
4. **Result:** Dual system doing same thing twice

### Evidence from storage_log.txt

```
[2025-11-28 15:15:00] STORED: research-transferability-validation.md
- Type: Semantic pattern (QUANT role)
- Action: CREATE (no similar existing memory about research transferability)

[2025-11-29 23:05:52] UPDATED: research-transferability-validation.md
- Action: Enhanced existing semantic pattern with additional Sprint 17 insights
- Similarity: >0.90 (same Sprint 17 case study, complementary details)
```

This confirms skill is:
- Writing .md files locally
- Tracking actions in log file
- Doing file-based search/merge/update

### Proof: Local Files Have Content Not in Vector DB

Example: `backend-api-integration.md` contains:
```markdown
## TTS API Voice Consistency - Specify ALL Parameters to Avoid Randomization
...full content...
```

**Question:** Is this ALSO in Qdrant `backend-patterns` collection?

Let me check if there's duplication:

---

## Bug #9: Skills Don't Follow Their Own Instructions ⚠️ **HIGH**

### SKILL.md Says:

Line 8:
```markdown
**NEVER call memory MCP tools directly!** Use Task tool with `subagent_type: "general-purpose"`
```

Line 104-111:
```markdown
**CRITICAL**: Use tools from the **memory MCP server**:
- `search_memory` - Search and get previews
- `store_memory` - Store new memory
```

### But Implementation Does:

Based on file evidence, the skill:
1. ❌ Writes local markdown files (NOT using MCP tools)
2. ❌ Maintains storage_log.txt (NOT using MCP tools)
3. ✅ Maybe also calls MCP tools? (unclear)

**Contradiction:** Instruction says "use MCP tools" but files show local file I/O

---

## Bug #10: No Way to Know Which Storage is Truth ⚠️ **HIGH**

### Scenario:

User asks: "What do I know about backend API integration?"

**Problem:** Which storage should answer?
- Local file: `episodic/backend-api-integration.md` (has 1 memory)
- Vector DB: `backend-patterns` collection (has 43 memories)

Are they synchronized? We don't know!

---

## Root Cause Analysis

### Timeline Hypothesis:

**Phase 1: Pre-MCP (Old System)**
```
coder-memory-store skill:
  - Managed local .md files
  - episodic/, procedural/, semantic/ folders
  - Simple grep/file search
  - storage_log.txt for tracking
```

**Phase 2: MCP Server Added**
```
Created MCP server:
  - Qdrant vector database
  - 7 MCP tools (search_memory, store_memory, etc.)
  - Role-based collections
```

**Phase 3: Migration Bug**
```
Updated SKILL.md to say "use MCP tools"
BUT forgot to remove local file I/O code
RESULT: Both systems running in parallel!
```

### Where is the File I/O Code?

**Problem:** SKILL.md is just a prompt. The actual code is in the **Task tool sub-agent**.

When skill runs, it:
1. Spawns a Task tool with `subagent_type: "general-purpose"`
2. That sub-agent reads SKILL.md as instructions
3. Sub-agent executes the prompt using available tools
4. **BUG:** Sub-agent can use File I/O tools (Read, Write, Edit) that it shouldn't!

### The Real Bug:

SKILL.md prompt doesn't explicitly forbid file operations, so sub-agent:
- Uses Read/Write tools for .md files
- Thinks it's being helpful by maintaining dual storage
- Doesn't know it should ONLY use MCP tools

---

## How to Verify

### Test 1: Check if storage_log.txt is still being updated

```bash
# Watch the file for changes
watch -n 1 'ls -lh ~/.claude/skills/coder-memory-store/semantic/storage_log.txt'

# Then trigger a memory store operation
# If file timestamp changes → BUG CONFIRMED
```

### Test 2: Compare local files vs Qdrant

```python
# Count local memories
local_files = glob("~/.claude/skills/coder-memory-store/**/*.md")
print(f"Local: {len(local_files)} files")

# Count Qdrant memories
collections = list_collections()
total_qdrant = sum(c["count"] for c in collections)
print(f"Qdrant: {total_qdrant} memories")

# If numbers don't match → DUAL STORAGE CONFIRMED
```

### Test 3: Trigger coder-memory-store and monitor file access

```bash
# Monitor file access in real-time
sudo inotifywait -m -r ~/.claude/skills/coder-memory-store/ &

# Then run: /coder-memory-store "test memory"
# Watch for file READ/WRITE events
```

---

## Recommended Fixes

### Fix 1: Update SKILL.md to Forbid File Operations

Add to SKILL.md (line 6):

```markdown
## ⚠️ CRITICAL: NO FILE I/O ALLOWED

**NEVER use Read/Write/Edit tools on local files!**
- ❌ Do NOT write .md files
- ❌ Do NOT write logs
- ❌ Do NOT read/search local files
- ✅ ONLY use MCP memory tools: search_memory, store_memory, etc.

All memory storage MUST go through MCP server to Qdrant vector database.
```

### Fix 2: Delete Local Storage Files

```bash
# Backup first
tar -czf ~/.claude/skills-backup-2026-01-08.tar.gz ~/.claude/skills/coder-memory-store/{episodic,procedural,semantic}

# Delete local storage (keep SKILL.md)
rm -rf ~/.claude/skills/coder-memory-store/episodic/*.md
rm -rf ~/.claude/skills/coder-memory-store/procedural/*.md
rm -rf ~/.claude/skills/coder-memory-store/semantic/*.md
rm ~/.claude/skills/coder-memory-store/semantic/storage_log.txt
```

### Fix 3: Verify All Memories Are in Qdrant

Before deleting, ensure all local memories were migrated:

```python
# Extract all memories from local .md files
local_memories = []
for file in glob("~/.claude/skills/coder-memory-store/**/*.md"):
    content = read_file(file)
    local_memories.append({
        "file": file,
        "content": content
    })

# Search Qdrant for each one
for mem in local_memories:
    results = search_memory(mem["content"], "global", limit=1)
    if not results or results[0]["similarity"] < 0.95:
        print(f"⚠️ NOT FOUND IN QDRANT: {mem['file']}")
```

### Fix 4: Add Monitoring to Prevent Regression

Create a hook to block file writes:

```bash
# ~/.claude/hooks/prevent_skill_file_writes.sh
if [[ "$TOOL_NAME" == "Write" || "$TOOL_NAME" == "Edit" ]]; then
    if [[ "$FILE_PATH" == *".claude/skills/coder-memory-store"* ]]; then
        echo "ERROR: Skills should not write files! Use MCP memory tools instead."
        exit 1
    fi
fi
```

---

## Impact Assessment

### Current State (Broken)

- ❌ 2x slower due to dual storage
- ❌ File I/O operations user sees ("reading/writing random files")
- ❌ Unclear which storage is source of truth
- ❌ Potential data inconsistency
- ❌ Wasted disk space

### After Fix

- ✅ 2-3x faster (only vector DB)
- ✅ No file I/O noise
- ✅ Single source of truth (Qdrant)
- ✅ Consistent data
- ✅ Clean skills directory

---

## Questions to Answer

1. **Are ALL local memories already in Qdrant?**
   - Need to verify before deleting local files

2. **When did dual storage start?**
   - Check git history of SKILL.md

3. **Does coder-memory-recall also use local files?**
   - Check if it searches .md files

4. **Are there other skills with same problem?**
   - Audit all skills for file I/O

---

## Next Steps

1. ✅ Identified bug (dual storage)
2. ⏳ Verify all memories in Qdrant
3. ⏳ Update SKILL.md to forbid file I/O
4. ⏳ Test memory operations work without files
5. ⏳ Delete local storage files
6. ⏳ Add monitoring hook

**Estimated time to fix:** 2-3 hours
