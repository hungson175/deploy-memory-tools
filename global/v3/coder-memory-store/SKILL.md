---
name: coder-memory-store
description: Store universal coding patterns and insights into vector database. Use after completing difficult tasks with broadly-applicable lessons that work across ANY project. Use when user says "--coder-store" or "--learn" (you decide which scope, may use both) or after discovering framework-agnostic patterns. ALSO invoke when user expresses strong frustration using trigger words like "fuck", "fucking", "shit", "moron", "idiot", "stupid", "garbage", "useless", "terrible", "wtf", "this is ridiculous", "you're not listening" - these are CRITICAL learning signals for storing failure patterns. Skip for routine work or project-specific details. Auto-invokes based on task completion and user signals.
---

# Coder Memory Store (V3 - Vector-First)

**Purpose**: Extract and store **universal coding patterns** (episodic/procedural/semantic) into Qdrant vector database using role-based collections.

**🔑 KEY ARCHITECTURE CHANGE**: All memory content goes to vector DB. Files store ONLY query guides (ToC). No file-based consolidation - use vector search + LLM validation.

**When to Use**:
- After solving non-obvious bugs with broadly-applicable solutions
- When discovering universal patterns (debugging strategies, architectural insights, framework-agnostic techniques)
- User explicitly says "--coder-store" or "--learn"
- Completed difficult tasks with lessons ANY coding project could benefit from
- **User expresses strong frustration** (trigger words detected) → Store failure pattern

**CRITICAL**: Store BOTH successful AND failed trajectories. Failures are equally important - often MORE valuable than successes.

**When NOT to Use**:
- Routine tasks or standard debugging
- Project-specific configurations (use git history + auto-generated docs)
- Obvious or well-known patterns

**Selection Criteria**: Most conversations yield 0-1 universal insights. Be highly selective.

---

## PHASE 0: Load Role Configuration

Read lightweight configuration files:

1. **Read `./roles.yaml`** (relative path for portability) - Available role-based collections

2. **Identify target role** for new memory:
   - Backend work? → `backend-dev` collection
   - Frontend work? → `frontend-dev` collection
   - Financial/quant work? → `financial-engineer` collection
   - Universal/cross-domain? → `coder` collection
   - Can store to multiple collections if broadly applicable

3. **Dynamic Role/Tag Management**:
   - **If new role needed** (task doesn't fit existing roles):
     - Create new role entry in `./roles.yaml`
     - Define collection name (sanitize role name)
     - Add common_tags for new role
     - Update roles.yaml using Edit tool
   - **If new tags discovered** (using tags not in common_tags):
     - Add to appropriate role's common_tags array in `./roles.yaml`
     - This helps future memory operations and queries

---

## PHASE 1: Extract Insights

Analyze conversation and extract **0-3 insights** (most yield 0-1).

**Classify each as**:
- **Episodic**: Concrete events (debugging session, implementation story) with full context
- **Procedural**: Repeatable workflow or step-by-step process
- **Semantic**: General principle or pattern (abstracted from experience)

**Extraction Criteria** (ALL must be true):
1. **Non-obvious**: Not standard practice or well-documented
2. **Universal**: Applies across multiple projects/languages/frameworks
3. **Actionable**: Provides concrete guidance for future situations
4. **Generalizable**: Can be abstracted beyond specific codebase

**Reject**:
- Project-specific details (use git history + generated docs)
- Routine work or obvious patterns
- Standard practices already well-known

**Determine target role and memory type** for each insight.

---

## PHASE 2: Search for Similar Memories

For each extracted insight:

**Step 1: Construct semantic query**

Use **full formatted memory text** (Title + Description + Content) for rich semantic matching:

```
**Title:** <concise title>
**Description:** <one sentence summary>

**Content:** <3-5 sentences covering: what happened, what was tried, what worked/failed, key lesson>

**Tags:** #tag1 #tag2 #success OR #failure
```

**Step 2: Query vector database via MCP memory server**

Use the `search_memory` tool from the MCP memory server:

```
search_memory(
    query="<full formatted memory text>",
    memory_level="coder",
    limit=10
)
```

**Returns**: Lightweight previews with {doc_id, title, description, similarity, tags}
- Does NOT return full content (saves tokens)
- Agent reviews previews to decide relevance

**Step 3: Review search results using intelligence**

Analyze returned previews and use your judgment to assess similarity:
- **Semantic similarity**: How similar is the core concept?
- **Contextual match**: Same problem domain, framework, time period?
- **Content overlap**: Based on title/description, likely redundant or complementary?
- **Outcome type**: Both successes, both failures, or mixed approaches?

For memories that appear similar, retrieve full content using `get_memory(doc_id, memory_level="coder")` to make informed consolidation decision.

**Trust your intelligence**: You understand context better than any fixed threshold.

---

## PHASE 3: Consolidation Decision

**Intelligent Decision Making** (Claude uses judgment, no fixed thresholds):

Review search results and retrieved full content. Decide the best action based on:
- **Semantic similarity**: Core concept overlap
- **Contextual match**: Same problem domain, framework, time period
- **Content overlap**: Redundant information vs. complementary details
- **Outcome type**: Both successes, both failures, or mixed

**Available Actions**:

| Action | When to Use | Implementation |
|--------|------------|----------------|
| **MERGE** | Near-duplicate content covering same experience | Combine into stronger entry, delete old |
| **UPDATE** | Related memory on same topic needing enhancement | Update existing, regenerate embedding |
| **GENERALIZE** | Pattern emerges from 2+ similar episodic memories | Create semantic memory from pattern |
| **CREATE** | Different topic or orthogonal approach | Store as new independent memory |

**Consolidation Actions**:

### MERGE (duplicate or very similar):
1. **Retrieve existing memory** using `get_memory(doc_id, memory_level="coder")`
2. **Combine content**:
   - Eliminate redundancy
   - Keep unique details from both
   - If contradictory: Add "**Previous Approach:**" and tag #reconsolidated
3. **Delete old memory**: `delete_memory(doc_id, memory_level="coder")`
4. **Store merged version**: `store_memory(...)` with combined content

### UPDATE (related, same topic):
1. **Retrieve existing memory**
2. **Update content inline**:
   - If alternative approach: Add cross-reference
   - If contradicts: Show evolution with "**Previous approach:**"
3. **Update memory**: `update_memory(doc_id, document, metadata, memory_level="coder")`
   - This regenerates embedding with new content

### GENERALIZE (pattern emerges from 2+ episodic):
1. **Extract common pattern** from similar episodic memories
2. **Create semantic memory** with generalized pattern
3. **Store semantic memory** to `coder` collection (universal) AND role collection
4. **Reference episodic examples** in semantic memory content
5. **Optionally update episodic entries** with cross-reference to semantic pattern

### CREATE (different topic):
1. **Store as new memory**: `store_memory(...)`
2. **No file updates needed** (all content in vector DB)

---

## PHASE 4: Store Memory to Vector Database

**CRITICAL: Use COMPACT format (3-5 sentences MAX)**

**Universal Format**:
```
**Title:** <concise title>
**Description:** <one sentence summary>

**Content:** <3-5 sentences covering: what happened, what was tried (including failures), what worked/failed, key lesson>

**Tags:** #tag1 #tag2 #success OR #failure
```

**Formatting Rules**:
- Content MUST be 3-5 sentences (not paragraphs, not lists)
- Include both failures and successes in Content if relevant
- Tag with memory type: #episodic OR #procedural OR #semantic
- Tag with role if role-specific: #backend #frontend #financial
- Tag with outcome: #success OR #failure

**Execute Storage**:
```
store_memory(
    document="<full formatted memory text>",
    metadata={
        "memory_level": "coder",
        "memory_type": "<episodic|procedural|semantic>",
        "role": "<backend-dev|frontend-dev|financial-engineer|coder>",
        "file_path": "<role/subdomain/topic>",  # Reference only, no actual file
        "skill_root": "coder-memory-store",
        "tags": ["<tag1>", "<tag2>", "<success|failure>"],
        "title": "<memory title>",
        "created_at": "<ISO timestamp>",
        "last_synced": "<ISO timestamp>",
        "last_recall_time": null  # Will be set on first recall
    },
    memory_level="coder"
)
```

**Cross-Collection Storage** (if universally applicable):

If pattern applies to both specific role AND universal coder collection:
1. Store to role collection (`backend-dev`, etc.)
2. Also store generalized version to `coder` collection
3. Add bidirectional references in content

**No File Writes Needed** - All content goes to vector DB only!

---

## PHASE 5: Optional - Update Query Guides

**Only if new role/tags added** (rare):

1. Check if role exists in `roles.yaml`
2. If new role: Add to `roles.yaml`
3. If new common tags for role: Update role's README.md with tag suggestions

**File updates are minimal** (~few KB, infrequent)

---

## Final Report

**Format**:
```
✅ Coder Memory Storage Complete

**Insights Extracted**: <number> universal patterns
  - Episodic: <number>
  - Procedural: <number>
  - Semantic: <number>

**Storage Actions**:
  - Created new memories: <number>
  - Updated existing memories: <number>
  - Merged duplicates: <number>
  - Generalized patterns: <number>

**Collections Updated**:
  - backend-dev: <number>
  - frontend-dev: <number>
  - financial-engineer: <number>
  - coder (universal): <number>

**Quality Check**:
  - ✓ All insights are universal (framework/project-agnostic)
  - ✓ All insights are non-obvious
  - ✓ Compact format enforced (3-5 sentences per memory)
  - ✓ Duplicates eliminated via vector search + LLM validation
```

**If 0 insights extracted**:
```
✅ Coder Memory Storage Complete

**Insights Extracted**: 0 (conversation contained routine work or project-specific details)

Consider using git history + auto-generated docs for project-specific insights.
```

---

## Key Differences from V2

| Aspect | V2 | V3 |
|--------|---|-----|
| **Memory storage** | Files (MERGE/UPDATE via file edits) | Vector DB (MERGE/UPDATE via MCP tools) |
| **Consolidation** | File-based (read + edit files) | Vector-based (search_memory + LLM validation) |
| **Deduplication** | Grep search + file comparison | Semantic similarity + hybrid validation |
| **File writes** | Every memory → file writes | Rare (only query guide updates) |
| **Role isolation** | None (mixed in single dir) | Separate collections per role |
| **Execution** | Via Task tool (subagent) | Direct invocation (auto-activated) |
| **Cross-promotion** | Manual file copying | Store to multiple collections |

---

## MCP Tools Required

Tools from the **MCP memory server** (Qdrant-backed):

- `search_memory(query, memory_level, limit)` - Semantic search returning previews (title + summary)
- `get_memory(doc_id, memory_level)` - Retrieve full content for selected memories
- `store_memory(document, metadata, memory_level)` - Create new memory
- `update_memory(doc_id, document, metadata, memory_level)` - Update existing (regenerates embedding)
- `delete_memory(doc_id, memory_level)` - Remove duplicates

---

## Configuration Files Structure

```
~/.claude/skills/coder-memory-store/
├── SKILL.md (this file)              # Instructions for storage
├── roles.yaml                         # Available roles/collections
├── backend-dev/
│   └── README.md                      # Common tags for backend role
├── frontend-dev/
│   └── README.md                      # Common tags for frontend role
├── financial-engineer/
│   └── README.md                      # Common tags for quant role
└── coder/
    └── README.md                      # Common tags for universal patterns
```

**Total file size**: ~4KB (constant, doesn't grow with memories)

---

## Notes

- **No progressive disclosure** - All content in vector DB
- **No file-based consolidation** - Use vector search + LLM validation instead
- **Requires Qdrant MCP server** - V3 has hard dependency
- **Auto-invocation** - Skill activates based on task completion and user signals
- **Compact format enforced** - 3-5 sentences MAX to prevent bloat in vector DB
