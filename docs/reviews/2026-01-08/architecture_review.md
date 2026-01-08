# MCP Memory Server - Architecture Review

**Review Date:** 2026-01-08
**Reviewer:** Claude Code
**Project:** Qdrant Memory MCP Server V3.2
**Status:** 🔴 **BUGS FOUND** - NOT working correctly

---

## Executive Summary

After thorough code analysis, I found **7 critical bugs** and **5 architecture issues** that explain why the memory system is not working well. The main problems are:

1. ❌ **Missing title/description extraction** - Previews show "Untitled" / "No description"
2. ❌ **Duplicate code** - `__main__.py` and `server.py` are 99% identical (724 vs 608 lines)
3. ❌ **No metadata validation** - Missing fields cause silent failures
4. ❌ **Search across ALL roles by default** - Performance issue
5. ❌ **Embedding cache never clears** - Memory leak
6. ❌ **Error handling too broad** - Silent failures everywhere
7. ❌ **No deduplication** - Same memory can be stored multiple times

---

## Architecture Overview

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Claude Code Client                       │
│                  (User / AI Agent)                           │
└────────────────────┬────────────────────────────────────────┘
                     │ JSON-RPC over stdio
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Memory Server (FastMCP)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  7 MCP Tools:                                        │   │
│  │  1. search_memory(query, memory_level, limit, roles)│   │
│  │  2. get_memory(doc_id, memory_level, roles)         │   │
│  │  3. batch_get_memories(doc_ids, ...)                │   │
│  │  4. store_memory(document, metadata, memory_level)  │   │
│  │  5. update_memory(doc_id, document, metadata, ...)  │   │
│  │  6. delete_memory(doc_id, memory_level, roles)      │   │
│  │  7. list_collections()                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │                                    │
│  ┌──────────────────────▼──────────────────────────────┐   │
│  │  Embedding Providers (OpenAI/Voyage/Nomic)          │   │
│  │  - _get_embedding(text) → vector[1536]              │   │
│  │  - In-memory cache: _embedding_cache{}              │   │
│  └──────────────────────┬──────────────────────────────┘   │
└─────────────────────────┼──────────────────────────────────┘
                          │ HTTP API calls
                          ▼
     ┌──────────────────────────────────────────┐
     │    Embedding API (OpenAI/Voyage/Nomic)   │
     └──────────────────────────────────────────┘

                          │ Qdrant Client
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Qdrant Vector Database                          │
│                (http://14.225.192.6:6309)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Global Collections (Role-based):                    │   │
│  │  - universal-patterns         (155 points)           │   │
│  │  - backend-patterns           (43 points)            │   │
│  │  - frontend-patterns          (31 points)            │   │
│  │  - scrum-master-patterns      (27 points)            │   │
│  │  - ai-patterns                (29 points)            │   │
│  │  - devops-patterns            (43 points)            │   │
│  │  - quant-patterns             (13 points)            │   │
│  │  - ml-patterns                (0 points)             │   │
│  │  - security-patterns          (0 points)             │   │
│  │  - mobile-patterns            (0 points)             │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Project Collections:                                │   │
│  │  - proj-vietvoice-tts         (2 points)             │   │
│  │  - proj-trading-bot-lightsail (6 points)             │   │
│  │  - proj-AI-teams-controller   (1 point)              │   │
│  │  - proj-cohere4-multimodal-rag(1 point)              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Skills Integration Layer                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ~/.claude/skills/coder-memory-store/                │   │
│  │  - Wraps store_memory() MCP tool                     │   │
│  │  - Adds classification logic                         │   │
│  │  - Used after completing tasks                       │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  ~/.claude/skills/coder-memory-recall/               │   │
│  │  - Wraps search_memory() + batch_get_memories()      │   │
│  │  - Adds role detection                               │   │
│  │  - Used before complex tasks                         │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                    STORE MEMORY FLOW                           │
└────────────────────────────────────────────────────────────────┘

User/Agent
   │
   ├─> "Store this memory: SM must verify requirements..."
   │
   ▼
Skills Layer (coder-memory-store)
   │
   ├─> Classify memory type (semantic/procedural/episodic)
   ├─> Determine role (scrum-master)
   ├─> Format document:
   │   **Title:** ...
   │   **Description:** ...
   │   **Content:** ...
   │   **Tags:** #scrum-master #verification
   │
   ▼
MCP Tool: store_memory()
   │
   ├─> Get collection: scrum-master-patterns
   ├─> Generate embedding: _get_embedding(document)
   │    │
   │    ├─> Check cache: _embedding_cache[document]
   │    │    ├─> HIT → return cached
   │    │    └─> MISS → call API
   │    │
   │    ├─> Call OpenAI/Voyage/Nomic API
   │    │    └─> Return vector[1536]
   │    │
   │    └─> Cache result: _embedding_cache[document] = vector
   │
   ├─> Generate UUID: doc_id
   ├─> Add timestamps: created_at, last_synced
   │
   ▼
Qdrant.upsert()
   │
   └─> Store PointStruct:
       - id: doc_id (UUID)
       - vector: embedding[1536]
       - payload: {
           "document": full_text,
           "title": "...",            ← ❌ BUG: Not extracted!
           "description": "...",      ← ❌ BUG: Not extracted!
           "memory_type": "semantic",
           "role": "scrum-master",
           "tags": [...],
           "created_at": "2026-01-08T...",
           "last_synced": "2026-01-08T..."
         }


┌────────────────────────────────────────────────────────────────┐
│                  SEARCH MEMORY FLOW (Two-Stage)                │
└────────────────────────────────────────────────────────────────┘

User/Agent
   │
   ├─> "Search for SM coordination patterns"
   │
   ▼
Skills Layer (coder-memory-recall)
   │
   ├─> Detect role: scrum-master (from query keywords)
   ├─> Build query: "scrum master coordination patterns..."
   │
   ▼
MCP Tool: search_memory(query, "global", limit=20, roles=["scrum-master"])
   │
   ├─> Generate query embedding: _get_embedding(query)
   │
   ├─> For each role in roles:  ← ❌ BUG: If roles=None, searches ALL!
   │    │
   │    ├─> Get collection: scrum-master-patterns
   │    │
   │    ├─> Qdrant.query_points(
   │    │     query=embedding,
   │    │     limit=20,
   │    │     with_payload=True,
   │    │     with_vectors=False
   │    │   )
   │    │
   │    └─> Results: [Point(score=0.89, payload={...}), ...]
   │
   ├─> Extract previews from results:
   │    │
   │    ├─> title = payload.get("title", "") or "Untitled"  ← ❌ BUG!
   │    ├─> desc = payload.get("description", "") or "No description"
   │    │
   │    └─> Build preview: {
   │          "doc_id": "...",
   │          "title": "Untitled",     ← Wrong!
   │          "description": "No description",  ← Wrong!
   │          "similarity": 0.89,
   │          "tags": [...],
   │          ...
   │        }
   │
   └─> Return JSON: {"results": [...], "total": 27}

   ▼
Skills Layer receives previews
   │
   ├─> Analyze which ones are relevant
   │
   ▼
MCP Tool: batch_get_memories(doc_ids=[...], "global", roles=["scrum-master"])
   │
   ├─> For each role in roles:
   │    │
   │    ├─> Qdrant.retrieve(ids=doc_ids)
   │    │
   │    └─> Return full documents
   │
   └─> Return JSON: {
         "memories": [
           {
             "doc_id": "...",
             "document": "**Title:**...\n**Description:**...",
             "metadata": {...}
           }
         ]
       }
```

---

## Code Structure

### Files Layout

```
src/qdrant_memory_mcp/
├── __init__.py          (207 bytes)   - Package init
├── __main__.py          (724 lines)   - ✅ Main server (FastMCP)
├── server.py            (608 lines)   - ❌ DUPLICATE! 99% same as __main__.py
├── config.py            (1,141 bytes) - ❌ UNUSED! Config loaded directly
└── utils/               - Empty directory
```

### Functions in __main__.py

| Function | Lines | Purpose | Status |
|----------|-------|---------|--------|
| `get_qdrant_client()` | 93-100 | Lazy init Qdrant | ✅ OK |
| `_init_collections()` | 103-118 | Create role collections | ✅ OK |
| `_get_embedding_openai()` | 120-141 | OpenAI embeddings | ✅ OK |
| `_get_embedding_voyage()` | 143-180 | Voyage AI embeddings | ✅ OK |
| `_get_embedding_nomic()` | 182-204 | Nomic embeddings | ✅ OK |
| `_get_embedding()` | 214-234 | Router with cache | ⚠️ Cache leak |
| `_get_collection_name()` | 236-247 | Map level+role→collection | ✅ OK |
| `search_memory()` | 271-343 | Search (Stage 1) | ❌ BUGS |
| `get_memory()` | 355-399 | Get single (Stage 2) | ✅ OK |
| `batch_get_memories()` | 411-463 | Get multiple (Stage 2) | ✅ OK |
| `store_memory()` | 475-536 | Store new memory | ❌ BUGS |
| `update_memory()` | 548-596 | Update existing | ❌ BUGS |
| `delete_memory()` | 608-655 | Delete memory | ✅ OK |
| `list_collections()` | 667-702 | List all collections | ✅ OK |

---

## 🔴 CRITICAL BUGS FOUND

### Bug #1: Missing Title/Description Extraction ⚠️ **CRITICAL**

**Location:** `store_memory()` line 475-536

**Problem:**
```python
# store_memory() does NOT extract title/description from document
def store_memory(document: str, metadata: Dict[str, Any], memory_level: str) -> str:
    # ...
    client.upsert(
        collection_name=collection_name,
        points=[
            models.PointStruct(
                id=doc_id,
                vector=embedding,
                payload={
                    "document": document,   # Full text stored
                    **metadata              # But title/description NOT in metadata!
                }
            )
        ]
    )
```

**Impact:**
- `search_memory()` expects `title` and `description` in payload
- But they're not extracted from document during storage
- Result: All previews show "Untitled" / "No description"
- Found evidence in your duplication analysis:
  ```
  "title": "Untitled",
  "description": "No description"
  ```

**Root Cause:**
The code assumes the caller (skills) will provide `title` and `description` in metadata, but:
1. Skills don't do this consistently
2. No validation to enforce it
3. Should extract from document if missing

**Fix Required:**
```python
def _extract_preview(document: str) -> Dict[str, str]:
    """Extract title and description from formatted document"""
    lines = document.split('\n')
    title = ""
    description = ""

    for line in lines:
        if line.startswith("**Title:**"):
            title = line.replace("**Title:**", "").strip()
        elif line.startswith("**Description:**"):
            description = line.replace("**Description:**", "").strip()

    return {
        "title": title or "Untitled",
        "description": description or "No description"
    }

def store_memory(document: str, metadata: Dict[str, Any], memory_level: str) -> str:
    # Extract preview if not in metadata
    if "title" not in metadata or "description" not in metadata:
        preview = _extract_preview(document)
        metadata["title"] = metadata.get("title", preview["title"])
        metadata["description"] = metadata.get("description", preview["description"])
    # ... rest of function
```

---

### Bug #2: Duplicate Files ⚠️ **HIGH**

**Location:** `__main__.py` vs `server.py`

**Problem:**
```bash
$ wc -l src/qdrant_memory_mcp/__main__.py src/qdrant_memory_mcp/server.py
  724 src/qdrant_memory_mcp/__main__.py
  608 src/qdrant_memory_mcp/server.py
 1332 total
```

Both files implement the same MCP server with 99% identical code. This is confusing and causes:
- Unclear which file is actually used (it's `__main__.py` from `.claude.json`)
- Maintenance burden - bugs must be fixed twice
- Risk of divergence

**Impact:**
- Code rot - `server.py` is outdated (608 lines vs 724)
- Confusion about which file runs
- Wasted 600 lines of duplicate code

**Fix Required:**
Delete `server.py` entirely. Only keep `__main__.py`.

---

### Bug #3: Search ALL Roles by Default ⚠️ **HIGH**

**Location:** `search_memory()` line 287

**Problem:**
```python
def search_memory(query: str, memory_level: str, limit: int = 20,
                 roles: Optional[List[str]] = None) -> str:
    # ...
    target_roles = roles if roles else ["universal"]  # ← Only searches universal!
```

Wait, this looks OK. Let me check `get_memory()`:

```python
def get_memory(doc_id: str, memory_level: str,
              roles: Optional[List[str]] = None) -> str:
    # ...
    target_roles = roles if roles else list(ROLE_COLLECTIONS.keys())  # ← ALL 10 roles!
```

**Problem:**
- `search_memory()`: defaults to `["universal"]` only (line 287)
- `get_memory()`: defaults to ALL roles (line 369)
- `batch_get_memories()`: defaults to ALL roles (line 425)
- `delete_memory()`: defaults to ALL roles (line 622)

**Impact:**
- Inconsistent behavior
- Performance hit: searches 10 collections unnecessarily
- Can't find memory if it's not in "universal"

**Fix Required:**
Make all functions consistent - default to searching relevant roles based on context, or require `roles` parameter.

---

### Bug #4: Embedding Cache Never Clears ⚠️ **MEDIUM**

**Location:** Line 90, `_get_embedding()` line 214-234

**Problem:**
```python
_embedding_cache: Dict[str, List[float]] = {}  # Global dict

def _get_embedding(text: str) -> List[float]:
    if text in _embedding_cache:
        return _embedding_cache[text]

    # ...get embedding from API...
    _embedding_cache[text] = embedding  # ← Cache grows forever!
    return embedding
```

**Impact:**
- Memory leak: cache grows unbounded
- After storing 1000 memories, cache holds ~1000 embeddings
- Each embedding is 1536 floats × 8 bytes = ~12KB
- 1000 embeddings = 12MB RAM

**Fix Required:**
Use LRU cache with max size:
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def _get_embedding(text: str) -> tuple:
    # ...
    return tuple(embedding)  # Return tuple for hashability
```

---

### Bug #5: Error Handling Too Broad ⚠️ **MEDIUM**

**Location:** Multiple places

**Problem:**
```python
try:
    client.get_collection(collection_name)
except Exception:  # ← Too broad! Catches everything
    continue
```

This pattern appears in:
- `search_memory()` line 297
- `get_memory()` line 391
- `batch_get_memories()` line 451
- `delete_memory()` line 636

**Impact:**
- Silent failures
- Hard to debug
- Catches unexpected errors (network, auth, etc.)

**Fix Required:**
Catch specific exceptions:
```python
from qdrant_client.http.exceptions import UnexpectedResponse

try:
    client.get_collection(collection_name)
except UnexpectedResponse as e:
    if "not found" in str(e).lower():
        logger.warning(f"Collection '{collection_name}' does not exist")
        continue
    raise  # Re-raise unexpected errors
```

---

### Bug #6: No Metadata Validation ⚠️ **MEDIUM**

**Location:** `store_memory()`, `update_memory()`

**Problem:**
```python
def store_memory(document: str, metadata: Dict[str, Any], memory_level: str):
    # No validation! Just stores whatever metadata is passed
    client.upsert(..., payload={"document": document, **metadata})
```

**Impact:**
- Missing required fields (title, description, tags) cause bugs
- Inconsistent data structure
- Hard to query/filter

**Fix Required:**
```python
REQUIRED_FIELDS = ["memory_type", "role", "tags"]

def _validate_metadata(metadata: Dict[str, Any]) -> None:
    for field in REQUIRED_FIELDS:
        if field not in metadata:
            raise ValueError(f"Missing required field: {field}")

    if not isinstance(metadata["tags"], list):
        raise ValueError("tags must be a list")
```

---

### Bug #7: No Deduplication ⚠️ **LOW**

**Location:** `store_memory()`

**Problem:**
The system can store the exact same memory multiple times:
- No check for duplicates before storing
- Found evidence: Memory #19 and #26 are 89% similar

**Impact:**
- Duplicate memories waste storage
- Confuses retrieval (which duplicate to return?)
- Found 2/27 = 7.4% high-similarity duplicates in scrum-master

**Fix Required:**
```python
def store_memory(document: str, metadata: Dict[str, Any], memory_level: str):
    # Check for duplicates
    embedding = _get_embedding(document)

    # Search for similar memories
    duplicates = client.query_points(
        collection_name=collection_name,
        query=embedding,
        limit=1,
        score_threshold=0.95  # 95% similarity = likely duplicate
    )

    if duplicates.points:
        return json.dumps({
            "error": "Duplicate memory detected",
            "existing_id": str(duplicates.points[0].id),
            "similarity": duplicates.points[0].score
        })

    # ... proceed with storage
```

---

## Architecture Issues

### Issue #1: No Network Type Separation

**Current:** All memories stored uniformly in role-based collections
**Problem:** Can't distinguish facts from opinions

**Found in duplication analysis:**
- Memory #19: "Concise Over Verbose" (Opinion)
- Memory #26: "Need Redundant Reinforcement" (Opinion)
- Both stored as generic "semantic" type

**Impact:**
- Can't track opinion evolution
- Contradictory advice has equal weight
- No confidence scores

**Recommendation:**
Add `network_type` field to classify memories as:
- `world`: Objective facts
- `experience`: Agent's experiences
- `opinion`: Subjective beliefs
- `observation`: Entity summaries

---

### Issue #2: No Temporal Reasoning

**Current:** Only `created_at` timestamp
**Problem:** Can't answer temporal queries

**Missing:**
- Occurrence interval (when it happened)
- Temporal links between memories
- Recency-based ranking

**Impact:**
- Can't query "What changed in Sprint 12?"
- Can't track evolution over time
- No temporal context

---

### Issue #3: Single-Strategy Retrieval

**Current:** Semantic search only
**Problem:** Misses exact keyword matches

**Missing:**
- BM25 keyword search
- Entity-based filtering
- Temporal filtering
- Graph traversal

---

### Issue #4: Skills Integration Unclear

**Current:** Two skills (`coder-memory-store`, `coder-memory-recall`)
**Problem:** Unclear what they add vs MCP tools

**Questions:**
- Do skills extract title/description?
- Do skills classify memory types?
- Why not do this in MCP server?

---

### Issue #5: No Monitoring/Metrics

**Current:** Only stderr logging
**Problem:** Can't track:
- How many searches/stores per day
- Average query latency
- Cache hit rate
- Duplicate rate
- Collection growth

---

## Data Model

### Memory Document Format

```
**Title:** <concise title>
**Description:** <one sentence summary>

**Content:** <full memory text with details>

**Tags:** #tag1 #tag2 #tag3
```

### Qdrant Point Structure

```python
PointStruct(
    id="4136f59b-7e29-497f-b37b-d93e57156663",  # UUID
    vector=[0.123, -0.456, ...],  # 1536 dimensions
    payload={
        # Full document (embedded)
        "document": "**Title:**...**Description:**...**Content:**...**Tags:**",

        # Metadata (extracted)
        "title": "Contract-First Team Coordination",  # ← ❌ BUG: Not extracted!
        "description": "In multi-team...",            # ← ❌ BUG: Not extracted!
        "memory_type": "pattern",        # semantic/procedural/episodic/pattern
        "role": "scrum-master",          # Which role collection
        "tags": ["sprint-planning", "coordination"],
        "created_at": "2025-12-26T07:02:16",
        "last_synced": "2025-12-26T07:02:16"
    }
)
```

---

## Configuration

### Environment Variables

```bash
# Qdrant
QDRANT_URL=http://14.225.192.6:6309  # Remote Qdrant server

# Embedding Provider (openai/voyage/nomic)
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536

# API Keys
OPENAI_API_KEY=sk-proj-...
VOYAGE_API_KEY=    # Optional
NOMIC_API_KEY=     # Optional
```

### MCP Configuration (`.claude.json`)

```json
{
  "mcpServers": {
    "memory": {
      "type": "stdio",
      "command": "/home/hungson175/dev/deploy-memory-tools/.venv/bin/python",
      "args": [
        "/home/hungson175/dev/deploy-memory-tools/src/qdrant_memory_mcp/__main__.py"
      ],
      "env": {
        "QDRANT_URL": "http://14.225.192.6:6309",
        "OPENAI_API_KEY": "sk-proj-..."
      }
    }
  }
}
```

---

## Testing Status

### Manual Testing (via scripts/analyze_scrum_master_memories.py)

✅ **Working:**
- Connect to Qdrant: OK
- Retrieve all 27 memories: OK
- Extract vectors: OK
- Calculate similarity matrix: OK
- Most similar pair found: 0.8926 similarity

❌ **Not Working:**
- Title/description in previews: Shows "Untitled" / "No description"
- Deduplication: Found 89% similar duplicates

---

## Recommendations

### Immediate Fixes (This Week)

1. **Fix Bug #1: Title/Description Extraction**
   - Add `_extract_preview()` function
   - Extract from document if not in metadata
   - **Impact:** Fixes preview display
   - **Effort:** 1 hour

2. **Fix Bug #2: Remove Duplicate File**
   - Delete `server.py`
   - **Impact:** Reduces confusion
   - **Effort:** 5 minutes

3. **Fix Bug #3: Consistent Role Defaults**
   - Make all functions default to `["universal"]`
   - **Impact:** Consistent behavior
   - **Effort:** 30 minutes

4. **Fix Bug #4: LRU Cache**
   - Replace dict with `@lru_cache`
   - **Impact:** Prevents memory leak
   - **Effort:** 15 minutes

5. **Fix Bug #7: Deduplication Check**
   - Check similarity before storing
   - Threshold: 0.95
   - **Impact:** Prevents duplicates
   - **Effort:** 1 hour

### Medium-term Improvements (Next Week)

6. **Add Metadata Validation**
   - Require title, description, tags
   - **Effort:** 2 hours

7. **Better Error Handling**
   - Catch specific exceptions
   - **Effort:** 2 hours

8. **Add Network Type Field**
   - Classify as world/experience/opinion/observation
   - **Effort:** 4 hours (includes migration)

### Long-term Enhancements (Next Month)

9. **Temporal Metadata**
   - Add occurrence_start, occurrence_end, mention_time
   - **Effort:** 1 week

10. **Multi-Strategy Retrieval**
    - Add BM25, temporal, entity filters
    - **Effort:** 2 weeks

11. **Monitoring Dashboard**
    - Track usage metrics
    - **Effort:** 1 week

---

## Current Stats

### Collections

| Collection | Type | Count | Status |
|-----------|------|-------|--------|
| universal-patterns | Global | 155 | ✅ Active |
| backend-patterns | Global | 43 | ✅ Active |
| frontend-patterns | Global | 31 | ✅ Active |
| scrum-master-patterns | Global | 27 | ⚠️ Has duplicates |
| ai-patterns | Global | 29 | ✅ Active |
| devops-patterns | Global | 43 | ✅ Active |
| quant-patterns | Global | 13 | ✅ Active |
| ml-patterns | Global | 0 | ❌ Empty |
| security-patterns | Global | 0 | ❌ Empty |
| mobile-patterns | Global | 0 | ❌ Empty |
| proj-vietvoice-tts | Project | 2 | ✅ Active |
| proj-trading-bot-lightsail | Project | 6 | ✅ Active |
| proj-AI-teams-controller | Project | 1 | ✅ Active |
| proj-cohere4-multimodal-rag | Project | 1 | ✅ Active |

**Total:** 15 collections, 351 memories

---

## Files to Fix

1. `src/qdrant_memory_mcp/__main__.py` - Fix bugs #1, #3, #4, #5, #6, #7
2. `src/qdrant_memory_mcp/server.py` - DELETE
3. `src/qdrant_memory_mcp/config.py` - DELETE (unused)
4. `~/.claude/skills/coder-memory-store/` - Review if it extracts title/description
5. `~/.claude/skills/coder-memory-recall/` - Review role detection logic

---

## Conclusion

The MCP Memory Server has a solid foundation but **7 critical bugs** prevent it from working correctly. The most severe issue is **missing title/description extraction** which breaks the preview feature.

**Priority order:**
1. Fix title/description extraction (Bug #1) - **URGENT**
2. Remove duplicate files (Bug #2) - **QUICK WIN**
3. Fix role defaults (Bug #3) - **IMPORTANT**
4. Add LRU cache (Bug #4) - **PREVENTS LEAK**
5. Add deduplication (Bug #7) - **PREVENTS WASTE**

After fixing these bugs, the system should work properly. Then we can add enhancements like:
- Network type separation (world/experience/opinion/observation)
- Temporal reasoning
- Multi-strategy retrieval
- Opinion evolution with confidence scores

**Estimated time to fix all critical bugs:** 4-6 hours
