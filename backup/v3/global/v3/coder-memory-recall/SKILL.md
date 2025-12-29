---
name: coder-memory-recall
description: Retrieve universal coding patterns from vector database. Use when starting complex tasks, encountering unfamiliar problems, or user says "--coder-recall" or "--recall" (you decide which scope, may use both). Skip for routine tasks or project-specific questions (use project-memory-recall). This Skill auto-invokes based on task context.
---

# Coder Memory Recall (V3 - Vector-First)

**Purpose**: Retrieve **universal coding patterns** from Qdrant vector database using role-based collections.

**🔑 KEY ARCHITECTURE CHANGE**: Files are now **Table of Contents** (query guides only). All actual memory content lives in Qdrant vector database.

**When to Use**:
- Before starting complex, multi-step implementations
- When encountering unfamiliar technical problems
- User explicitly says "--coder-recall" or "--recall"
- Need architectural guidance or debugging strategies

**When NOT to Use**:
- Routine or trivial tasks
- Just recalled similar knowledge recently
- Project-specific questions (use project-memory-recall - git history + auto-generated docs)

**REMEMBER**: Failures are as valuable as successes. Search for both #success and #failure tags.

---

## PHASE 0: Load Query Configuration

Read lightweight configuration files (ToC - ~4KB total):

1. **Read `./roles.yaml`** (relative path for portability) - Available role-based collections

2. **Identify relevant role(s)** from task context:
   - Backend work? → `backend-dev` collection
   - Frontend work? → `frontend-dev` collection
   - Financial/quant work? → `financial-engineer` collection
   - General/cross-domain? → `coder` collection (universal patterns)
   - Unclear? → Query multiple collections

3. **Load query templates** (optional) - Read role-specific README.md for:
   - Common tags for this role
   - Example query patterns
   - Domain-specific keywords

---

## PHASE 1: Construct Vector Query

**Query Construction Strategy** (from recalled patterns):

Use **full 2-3 sentence summary** for semantic search (NOT just keywords):

**If user provided explicit query**:
- Use their question/description as-is

**If inferring from context**:
- Write 2-3 sentence summary of what you're looking for
- Include: problem description, technical terms, desired outcome
- Example: "I need to implement authentication for a REST API using JWT tokens. Looking for patterns on token storage, refresh mechanisms, and secure validation approaches."

**Memory Type Filtering** (use metadata):
- Need specific past experience? → Filter: `memory_type=episodic`
- Need step-by-step process? → Filter: `memory_type=procedural`
- Need general principle/pattern? → Filter: `memory_type=semantic`
- Unclear? → No filter (search all types)

---

## PHASE 2: Query Vector Database

**Required Tool**: `search_memory` from the MCP memory server

For each target role collection:

```
search_memory(
    query="<2-3 sentence summary of what you're looking for>",
    memory_level="coder",  # For global memories
    limit=10
)
```

**Returns**: Lightweight previews with metadata:
- `doc_id` - Document ID for retrieving full content
- `title` - Memory title
- `description` - One sentence summary
- `similarity` - Cosine similarity score (0-1)
- `tags` - User-defined tags (#api, #database, #success, #failure)
- `memory_type` - episodic/procedural/semantic
- `role` - Collection name (backend-dev, frontend-dev, etc.)
- `created_at`, `last_recall_time` - Temporal metadata

**Note**: Full memory content is NOT included (saves tokens). Use `get_memory(doc_id, memory_level)` to retrieve full content for selected memories.

---

## PHASE 3: Filter and Rank Results

**Intelligent Relevance Assessment** (use your judgment, no rigid thresholds):

Review the search result previews and assess relevance based on:
1. **Similarity score** - Higher indicates better semantic match
2. **Memory type match** - Does episodic/procedural/semantic align with current need?
3. **Tag relevance** - Do tags match problem domain and context?
4. **Temporal freshness** - Recent memories may be more relevant for evolving technologies
5. **Title/description match** - Does the preview indicate this memory will help?

**Retrieve Full Content for Promising Memories**:

For memories that appear relevant based on previews, retrieve full content:
```
get_memory(doc_id="<doc_id>", memory_level="coder")
```

**Hybrid Validation** (for critical decisions):
- Vector embeddings can miss temporal/contextual nuances
- Use your intelligence to validate retrieved content:
  - Same time period? (Q1 2024 vs Q1 2025 may differ significantly)
  - Same domain/framework? (React patterns vs Vue patterns)
  - Same granularity? (Debugging specific issue vs architectural principle)

**Select top 3 most relevant memories** after reviewing full content

---

## PHASE 4: Present Results

**Format**:
```
🔍 Coder Memory Recall Results

**Query**: <keywords or user question>
**Collections Searched**: <backend-dev, frontend-dev, coder, etc.>
**Results Found**: <number>

---

## Result 1: [Title]

**Role**: <backend-dev/frontend-dev/financial-engineer/coder>
**Type**: <Episodic/Procedural/Semantic>
**Similarity**: <0.XX>
**Tags**: <#tag1 #tag2 #success|#failure>

<Full memory content>

**Relevance**: <1-2 sentences explaining why this matches query>

---

## Result 2: [Title]

[Same format]

---

## Application Guidance

<2-3 sentences synthesizing results and actionable next steps for current task>
```

**If no relevant results found**:
```
🔍 Coder Memory Recall Results

**Query**: <keywords>
**Collections Searched**: <role(s)>
**Results Found**: 0 relevant memories based on preview assessment

No universal patterns matched your query in vector database.

**Suggestions**:
- Try broader search terms or different role collection
- Check if this is project-specific (use git history + generated docs)
- Proceed with standard approaches and store insights after completion
```

---

## PHASE 5: Update Recall Metadata (Future)

**Not implemented yet** - for V3.1+:

For each retrieved memory, update `last_recall_time` metadata:
```
update_memory(
    doc_id="<memory_id>",
    document="<unchanged content>",
    metadata={
        ...existing metadata,
        "last_recall_time": "<current ISO timestamp>"
    },
    memory_level="coder"
)
```

This enables future forgetting mechanism (>1 month no recall → archival).

---

## Key Differences from V2

| Aspect | V2 | V3 |
|--------|---|-----|
| **Memory source** | Files (progressive disclosure) | Vector DB (direct query) |
| **File system role** | Store content | Store query guides (ToC) |
| **Search method** | Grep + Read (3-5+ file reads) | Single vector query |
| **Cost** | High (file reads expensive) | Low (ToC read ~4KB + vector query) |
| **Role isolation** | None (mixed memories) | Separate collections per role |
| **Execution** | Via Task tool (subagent) | Direct invocation (auto-activated) |

---

## Configuration Files Structure

```
~/.claude/skills/coder-memory-recall/
├── SKILL.md (this file)              # Instructions for recall
├── roles.yaml                         # Available roles/collections
├── backend-dev/
│   └── README.md                      # Query guide for backend role
├── frontend-dev/
│   └── README.md                      # Query guide for frontend role
├── financial-engineer/
│   └── README.md                      # Query guide for quant role
└── coder/
    └── README.md                      # Query guide for universal patterns
```

**Total file size**: ~4KB (constant, doesn't grow with memories)

---

## Notes

- **No progressive disclosure needed** - Vector DB returns full content directly
- **No refactoring mechanism** - Vector DB handles scaling automatically
- **Requires Qdrant MCP server** - V3 has hard dependency (no graceful degradation)
- **Auto-invocation** - Skill activates based on task context (no explicit Task tool call needed)
