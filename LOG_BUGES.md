# Memory System Bug Log

**Date:** 2026-01-13
**Status:** Identified and documented

---

## CRITICAL BUGS (Fix Immediately)

### **BUG #1: KILLER - Nested metadata in universal-patterns breaks retrieval**
**Priority:** P0 - CRITICAL
**Location:** Qdrant database - universal-patterns collection (91 points)

**Problem:**
Old migrated data has NESTED metadata structure instead of FLAT:

```json
// BROKEN (universal-patterns - 91 items)
{
  "document": "...",
  "metadata": {           ← NESTED - WRONG!
    "memory_level": "coder",
    "memory_type": "episodic",
    "file_path": "episodic/episodic.md",
    "skill_root": "coder-memory-store",
    "tags": [...],
    "title": "...",
    "created_at": "...",
    "last_synced": "..."
  },
  "migrated_from": "coder-memory",
  "migration_date": "2025-11-19T07:42:26.523479"
}

// CORRECT (backend-patterns, frontend-patterns, qa-patterns)
{
  "document": "...",
  "memory_type": "episodic",  ← FLAT - CORRECT!
  "role": "backend",
  "title": "...",
  "description": "...",
  "tags": [...],
  "confidence": "high",
  "frequency": 1,
  "created_at": "...",
  "last_synced": "..."
}
```

**Impact:**
- `get_memory()` returns inconsistent structure
- Skills expect flat `title`, `description`, `tags` at root
- Agent gets confused accessing fields
- Search previews might fail for universal-patterns items

**Fix:**
Migrate all 91 items in universal-patterns to flat structure:
1. Extract all nested `metadata.*` fields to root level
2. Remove `metadata` wrapper
3. Add missing `role: "universal"`
4. Add missing `frequency: 1`
5. Ensure `description` field exists (extract from document if needed)

---

### **BUG #2: Missing "qa" role in ROLE_COLLECTIONS**
**Priority:** P0 - CRITICAL
**Location:** `src/qdrant_memory_mcp/__main__.py:72-83`

**Problem:**
Collection `qa-patterns` exists with 2 items, but not defined in ROLE_COLLECTIONS:

```python
ROLE_COLLECTIONS = {
    "universal": "universal-patterns",
    "backend": "backend-patterns",
    "frontend": "frontend-patterns",
    "quant": "quant-patterns",
    "devops": "devops-patterns",
    "ml": "ml-patterns",
    "security": "security-patterns",
    "mobile": "mobile-patterns",
    "ai": "ai-patterns",
    "scrum-master": "scrum-master-patterns",
    # "qa": "qa-patterns",  ← MISSING!
}
```

**Impact:**
- Cannot search `qa-patterns` collection (2 items orphaned)
- Cannot store new QA/testing memories
- `store_memory(metadata={"role": "qa", ...})` returns error

**Fix:**
Add to ROLE_COLLECTIONS:
```python
"qa": "qa-patterns",
```

And add to skills role_mapping:
```
- qa: testing, quality-assurance, test-automation, e2e, unit-tests
```

---

### **BUG #3: Duplicate coder-memory collection**
**Priority:** P1 - HIGH
**Location:** Qdrant database

**Problem:**
```
coder-memory: 91 points
universal-patterns: 91 points
```

Both have exactly 91 points - likely migration duplicates.

**Impact:**
- Wasting storage
- Potential confusion if agent tries to search non-existent collection
- Database bloat

**Fix:**
1. Verify they're duplicates (compare doc_ids)
2. Delete `coder-memory` collection
3. Ensure all needed data is in `universal-patterns`

---

### **BUG #4: Missing description field in old data**
**Priority:** P1 - HIGH
**Location:** universal-patterns collection (potential)

**Problem:**
Old migrated data might not have extracted `description` field:
- Nested data has `metadata.description` OR might be missing entirely
- Two-stage retrieval depends on `description` for previews

**Impact:**
- Search returns "No description" for previews
- Agent can't evaluate relevance without description
- Defeats purpose of two-stage retrieval (60% token savings lost)

**Fix:**
1. Audit all 91 universal-patterns items
2. For items missing `description`:
   - Parse from document text (extract "**Description:**" section)
   - If not in document, generate from first 2-3 sentences of Content
3. Ensure all items have both `title` and `description` at root level

---

## HIGH PRIORITY BUGS (Fix Soon)

### **BUG #5: Migration artifacts polluting data**
**Priority:** P2 - MEDIUM
**Location:** universal-patterns collection

**Problem:**
Old migrated data has useless fields:
```json
{
  "migrated_from": "coder-memory",        ← Not needed
  "migration_date": "2025-11-19...",      ← Not needed
  "metadata": {
    "memory_level": "coder",              ← Removed feature
    "file_path": "episodic/episodic.md",  ← File-based artifact
    "skill_root": "coder-memory-store"    ← Not needed
  }
}
```

**Impact:**
- Database bloat
- Confuses debugging
- Wastes embedding storage

**Fix:**
During Bug #1 migration, remove these fields:
- `migrated_from`
- `migration_date`
- `metadata.memory_level`
- `metadata.file_path`
- `metadata.skill_root`

---

### **BUG #6: Empty collections wasting resources**
**Priority:** P2 - MEDIUM
**Location:** Qdrant database

**Problem:**
```
devops-patterns: 0 points
mobile-patterns: 0 points
ml-patterns: 0 points
security-patterns: 0 points
github-search-general: 0 points
github-search-phaser-games: 0 points
coder-memory-backup-v3: 0 points
```

**Impact:**
- Wasted collection overhead
- Clutter in database
- MCP server iterates over empty collections during search

**Fix:**
1. Keep role-based patterns (devops, mobile, ml, security) - will be used later
2. Delete non-memory collections:
   - `github-search-general`
   - `github-search-phaser-games`
   - `coder-memory-backup-v3`

---

### **BUG #7: MirMir-Queries collection (428 points) - wrong database?**
**Priority:** P2 - MEDIUM
**Location:** Qdrant database

**Problem:**
```
MirMir-Queries: 428 points
```

This doesn't match any memory pattern. Looks like it belongs to a different project.

**Impact:**
- Pollutes memory database
- Search might accidentally hit this collection
- Wasted storage

**Fix:**
1. Investigate what MirMir-Queries is
2. If not related to memory system, delete or move to separate Qdrant instance
3. If related, rename to match pattern: `mirmir-patterns` or similar

---

## LOW PRIORITY BUGS (Cleanup)

### **BUG #8: Unused Pydantic imports**
**Priority:** P3 - LOW
**Location:** `src/qdrant_memory_mcp/__main__.py`

**Problem:**
We removed `SearchMemoryInput` BaseModel but might still import:
```python
from pydantic import BaseModel, Field
```

Check if FastMCP needs these or if they're unused.

**Impact:**
- Code cleanliness only
- Tiny memory overhead

**Fix:**
```bash
# Check if BaseModel/Field used elsewhere
grep -n "BaseModel\|Field" src/qdrant_memory_mcp/__main__.py
# Remove if unused
```

---

### **BUG #9: Weak error messaging in store_memory**
**Priority:** P3 - LOW
**Location:** `__main__.py:498-499`

**Problem:**
```python
if not collection_name:
    return json.dumps({"error": f"Unknown role '{role}'. Valid roles: {list(ROLE_COLLECTIONS.keys())}"})
```

Silent failure - no logging, just JSON error return.

**Impact:**
- Debugging harder
- No visibility in logs when agent passes bad role

**Fix:**
```python
if not collection_name:
    logger.error(f"Invalid role '{role}' provided. Valid roles: {list(ROLE_COLLECTIONS.keys())}")
    return json.dumps({"error": f"Unknown role '{role}'. Valid roles: {list(ROLE_COLLECTIONS.keys())}"})
```

---

## PRIORITY ORDER FOR FIXING

1. **BUG #2** - Add "qa" role (5 min) ⚡ QUICK WIN
2. **BUG #1** - Migrate universal-patterns to flat structure (30 min) 🔥 CRITICAL
3. **BUG #4** - Ensure all items have description field (15 min during #1)
4. **BUG #5** - Clean migration artifacts (5 min during #1)
5. **BUG #3** - Delete duplicate coder-memory collection (2 min)
6. **BUG #7** - Investigate/delete MirMir-Queries (10 min)
7. **BUG #6** - Delete non-memory collections (2 min)
8. **BUG #8** - Remove unused imports (1 min)
9. **BUG #9** - Add logging to error paths (5 min)

**Estimated total fix time:** ~70 minutes

---

## Testing Checklist (After Fixes)

- [ ] Search universal-patterns returns flat metadata
- [ ] Search qa-patterns works
- [ ] Store to qa role works
- [ ] All 91+ memories have title + description
- [ ] No migration artifacts in payload
- [ ] Only memory-related collections exist
- [ ] MCP server starts without errors
- [ ] Skills can search and retrieve successfully

---

## Notes

- Original issue: Agent couldn't find memories because `memory_level` parameter confusion
- Root cause: Memory system had both "global/project" concept AND role-based collections
- Solution: Removed `memory_level` entirely, use only role-based collections
- This bug log documents data cleanup needed after architectural change
