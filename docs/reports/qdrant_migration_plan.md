# Qdrant Migration Plan

**Date:** 2025-10-30
**Status:** Ready to Execute
**Goal:** Migrate all existing file-based memories to Qdrant vector database

---

## Overview

Migrate memories from `~/.claude/skills/coder-memory-store/` to Qdrant collection `coder-memory` with proper metadata structure.

**Key Principle:** Files remain source of truth. Qdrant is supplementary search tool.

---

## Pre-Migration State

### Current File Structure
```
~/.claude/skills/coder-memory-store/
├── SKILL.md
├── episodic/
├── procedural/
└── semantic/
```

### Current Qdrant State
- Collections: `CodingAgent`, `ReasoningBank_c5da3cf9`
- **Action:** Delete all existing collections (clean slate)

---

## Migration Steps

### Step 1: Clean Qdrant Database ✓
**Status:** COMPLETED

**Actions:**
```bash
# Delete existing collections
curl -X DELETE http://localhost:6333/collections/CodingAgent
curl -X DELETE http://localhost:6333/collections/ReasoningBank_c5da3cf9
```

**Result:** Empty Qdrant database

---

### Step 2: Discover Memory Files

**Command:**
```bash
find ~/.claude/skills/coder-memory-store/ -name "*.md" -type f
```

**Expected structure:**
```
~/.claude/skills/coder-memory-store/
├── episodic/*.md
├── procedural/*.md
└── semantic/*.md
```

**Exclude:** `SKILL.md` (not a memory, it's the skill definition)

---

### Step 3: Parse Memory Format

**Expected Memory Format in Files:**
```markdown
**Title:** <concise title>
**Description:** <one sentence summary>

**Content:** <3-5 sentences covering: what happened, what was tried, what worked/failed, key lesson>

**Tags:** #tag1 #tag2 #success OR #failure
```

**Parsing Strategy:**
1. Read each `.md` file
2. Extract sections using regex/string matching
3. Identify memory type from file path (episodic/procedural/semantic)
4. Extract tags from `**Tags:**` line
5. Build memory document

**Edge Cases:**
- Files may contain multiple memories (separated by `---` or headers)
- Some files may not follow exact format
- Missing fields (handle gracefully)

---

### Step 4: Create Qdrant Collection

**Collection Name:** `coder-memory`

**Configuration:**
```json
{
  "vectors": {
    "size": 1536,
    "distance": "Cosine"
  }
}
```

**Embedding Model:** OpenAI text-embedding-3-small (1536 dimensions)

**API Call:**
```bash
curl -X PUT http://localhost:6333/collections/coder-memory \
  -H "Content-Type: application/json" \
  -d '{
    "vectors": {
      "size": 1536,
      "distance": "Cosine"
    }
  }'
```

---

### Step 5: Build Memory Documents

**For Each Parsed Memory:**

**Document Structure:**
```python
{
  "content": "<Full memory text: Title + Description + Content + Tags>",
  "metadata": {
    "memory_level": "coder",
    "memory_type": "episodic|procedural|semantic",
    "file_path": "episodic/debugging.md",
    "skill_root": "coder-memory-store",
    "tags": ["success", "pytest", "testing"],
    "title": "<extracted title>",
    "created_at": "<ISO timestamp>",
    "last_synced": "<ISO timestamp>"
  }
}
```

**Content Field Format:**
```
**Title:** <title>
**Description:** <description>

**Content:** <content>

**Tags:** <tags>
```

**Metadata Fields:**
- `memory_level`: Always `"coder"` (global memories)
- `memory_type`: Derived from directory (`episodic`/`procedural`/`semantic`)
- `file_path`: Relative to `~/.claude/skills/coder-memory-store/` (e.g., `"episodic/debugging.md"`)
- `skill_root`: Always `"coder-memory-store"`
- `tags`: Parsed from `**Tags:**` line (array of strings without `#`)
- `title`: Extracted from `**Title:**`
- `created_at`: Current timestamp (ISO 8601)
- `last_synced`: Current timestamp (ISO 8601)

---

### Step 6: Generate Embeddings & Insert

**For Each Memory Document:**

1. **Generate Embedding:**
   ```python
   from openai import OpenAI
   client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

   response = client.embeddings.create(
       input=memory_content,
       model="text-embedding-3-small"
   )
   embedding = response.data[0].embedding
   ```

2. **Insert to Qdrant:**
   ```bash
   curl -X PUT http://localhost:6333/collections/coder-memory/points \
     -H "Content-Type: application/json" \
     -d '{
       "points": [{
         "id": "<uuid>",
         "vector": <embedding>,
         "payload": {
           "document": "<content>",
           "metadata": {<metadata>}
         }
       }]
     }'
   ```

**ID Generation:** Use `uuid.uuid4()` for each memory

---

### Step 7: Verification

**After Migration:**

1. **Count Check:**
   ```bash
   # Files
   find ~/.claude/skills/coder-memory-store/ -name "*.md" -type f | wc -l

   # Qdrant
   curl http://localhost:6333/collections/coder-memory
   # Check "points_count" field
   ```

2. **Sample Search:**
   ```python
   # Search for a known memory
   search_doc("pytest fixtures", "coder-memory", limit=5)
   # Verify results make sense
   ```

3. **Metadata Validation:**
   ```bash
   # Get a random point and check metadata structure
   curl http://localhost:6333/collections/coder-memory/points/scroll
   ```

---

## Expected Results

**Metrics:**
- Total files: ~10-30 (estimate based on typical memory bank)
- Total memories: May be more than files (some files contain multiple memories)
- Collection: `coder-memory` created
- Points: All memories inserted with embeddings

**Success Criteria:**
- ✅ All `.md` files processed
- ✅ Collection `coder-memory` exists
- ✅ Point count matches memory count
- ✅ Metadata fields present and correct
- ✅ Sample searches return relevant results

---

## Error Handling

**Possible Issues:**

1. **Parse Failures:**
   - Log file path and continue
   - Store raw content if format doesn't match

2. **Embedding API Errors:**
   - Retry with exponential backoff
   - Skip if persistent failure (log for manual review)

3. **Qdrant Insert Errors:**
   - Log error and memory details
   - Continue with remaining memories

4. **Missing Fields:**
   - Use defaults:
     - Title: "Untitled Memory"
     - Description: First 100 chars of content
     - Tags: []

---

## Rollback Plan

**If Migration Fails:**

1. **Qdrant State:**
   - Delete `coder-memory` collection
   - Restart from Step 1

2. **File System:**
   - No changes made (read-only operation)
   - Files remain intact

**Backup (Optional):**
```bash
tar -czf ~/.claude/skills/coder-memory-store-backup-$(date +%Y%m%d).tar.gz \
  ~/.claude/skills/coder-memory-store/
```

---

## Post-Migration

**Next Steps:**

1. **Test Searches:**
   - Try various semantic queries
   - Verify results against file contents

2. **Update SKILL.md:**
   - Add Qdrant search as optional tool
   - Document collection name and usage

3. **Periodic Sync:**
   - Set up manual sync process
   - Document sync procedure

---

## Technical Details

### Collection Configuration

**Name:** `coder-memory`

**Vector Config:**
```json
{
  "vectors": {
    "size": 1536,
    "distance": "Cosine"
  }
}
```

**Payload Schema:**
```json
{
  "document": "string (full memory text)",
  "metadata": {
    "memory_level": "string (coder|project)",
    "memory_type": "string (episodic|procedural|semantic)",
    "file_path": "string (relative path)",
    "skill_root": "string (coder-memory-store)",
    "tags": "array of strings",
    "title": "string",
    "created_at": "string (ISO 8601)",
    "last_synced": "string (ISO 8601)"
  }
}
```

### Dependencies

**Environment Variables:**
```bash
OPENAI_API_KEY=<your-key>
QDRANT_URL=http://localhost:6333
```

**Python Libraries:**
```python
openai>=2.3.0
qdrant-client>=1.15.1
python-dotenv>=1.1.1
```

**Running Services:**
- Qdrant on port 6333
- OpenAI API accessible

---

## Execution Log Template

```
Migration Started: <timestamp>

Step 1: Clean Qdrant ✓
  - Deleted CodingAgent collection
  - Deleted ReasoningBank_c5da3cf9 collection

Step 2: Discover Files ✓
  - Found X files in episodic/
  - Found Y files in procedural/
  - Found Z files in semantic/
  - Total: N files

Step 3: Parse Memories ✓
  - Successfully parsed: M memories
  - Parse failures: P (see log)

Step 4: Create Collection ✓
  - Created coder-memory collection
  - Vector size: 1536, Distance: Cosine

Step 5: Generate Embeddings & Insert ✓
  - Generated embeddings: M
  - Inserted points: M
  - Failures: Q (see log)

Step 6: Verification ✓
  - Expected memories: M
  - Qdrant points: M
  - Sample search: PASS

Migration Completed: <timestamp>
Duration: <duration>
```

---

## Notes

- This is a **one-time migration** for initial population
- Future updates will be manual syncs by user
- Files remain the source of truth
- Qdrant is supplementary search tool only
- No automatic sync in first version (keep it simple)

---

## Status

**Ready to Execute:** YES

**Prerequisites Met:**
- ✅ Qdrant running on port 6333
- ✅ OpenAI API key configured
- ✅ Memory files exist at `~/.claude/skills/coder-memory-store/`
- ✅ MCP server available (for future use)

**Waiting on:** User confirmation to proceed
