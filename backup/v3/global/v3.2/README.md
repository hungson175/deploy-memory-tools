# V3.2 Memory Skills - Clean Vector Architecture

## What's New in V3.2

V3.2 fixes the inconsistencies and messiness in V3 with a cleaner, actually-working implementation:

### Key Improvements
1. **True Two-Stage Retrieval**: MCP server v2 actually implements preview/full separation
2. **Embedded Role Config**: No more duplicate roles.yaml files - config embedded in SKILL.md
3. **Simplified Collections**: Cleaner names (backend vs backend-dev, universal vs coder)
4. **Consistent Terminology**: "global" and "project" levels with role-based collections
5. **Working Implementation**: Everything actually works as documented

---

## Architecture

### Two-Stage Retrieval (Actually Implemented)

```mermaid
graph LR
    A[Search Query] --> B[search_memory]
    B --> C[Returns Previews Only]
    C --> D[Agent Reviews Previews]
    D --> E[get_memory/batch_get]
    E --> F[Full Content Retrieved]
```

**Stage 1: Search** → Lightweight previews (title, description, metadata)
**Stage 2: Retrieve** → Full content for selected memories only

This saves ~80% tokens compared to returning full content in search.

---

## Memory Organization

### Levels and Collections

```yaml
global:                           # Universal patterns
  universal-patterns:            # Cross-domain (was "coder-memory")
  backend-patterns:              # Backend engineering
  frontend-patterns:             # Frontend engineering
  quant-patterns:                # Quantitative finance
  devops-patterns:               # DevOps and infrastructure
  ml-patterns:                   # Machine learning
  security-patterns:             # Security engineering
  mobile-patterns:               # Mobile development

project:                         # Project-specific
  proj-{name}:                   # Auto-created per project
```

### Memory Format (Unchanged)

```markdown
**Title:** <concise title>
**Description:** <one sentence summary>

**Content:** <3-5 sentences: what happened, what tried, what worked/failed, key lesson>

**Tags:** #tag1 #tag2 #success OR #failure
```

---

## MCP Server V2 Tools

### search_memory
Returns **previews only**:
```json
{
  "results": [
    {
      "doc_id": "uuid",
      "title": "Memory Title",
      "description": "One line summary",
      "similarity": 0.89,
      "memory_type": "episodic",
      "tags": ["api", "debugging"],
      "role": "backend"
    }
  ]
}
```

### get_memory
Retrieves **full content**:
```json
{
  "doc_id": "uuid",
  "document": "**Title:** ...\n**Description:** ...\n\n**Content:** ...",
  "metadata": { ... }
}
```

### batch_get_memories
Efficiently retrieve **multiple memories**:
```json
{
  "memories": [
    { "doc_id": "id1", "document": "...", "metadata": {...} },
    { "doc_id": "id2", "document": "...", "metadata": {...} }
  ]
}
```

---

## Skill Design

### Embedded Configuration

Each SKILL.md file contains its own role configuration - no external roles.yaml needed:

```yaml
# Embedded in SKILL.md
role_config:
  global_collections:
    universal: Cross-domain patterns
    backend: Backend engineering
    frontend: Frontend engineering
    quant: Quantitative finance
    devops: DevOps and infrastructure
```

### Dynamic Role Detection

Skills automatically detect the appropriate role from task context:
- API work → backend-patterns
- React/UI → frontend-patterns
- Trading/risk → quant-patterns
- Cross-cutting → universal-patterns

---

## Workflow Examples

### Recall Flow
```
1. Detect task context → "Building REST API"
2. Infer role → "backend"
3. Search → search_memory(query, "global", role="backend")
4. Review previews → Agent analyzes titles/descriptions
5. Retrieve relevant → batch_get_memories([id1, id2, id3])
6. Apply insights → Use retrieved patterns
```

### Store Flow
```
1. Extract insight → "API rate limiting pattern discovered"
2. Detect role → "backend"
3. Search similar → search_memory(full_text, "global", role="backend")
4. Review previews → Check for duplicates/updates
5. Retrieve if needed → get_memory(similar_id) for MERGE/UPDATE
6. Consolidate → MERGE/UPDATE/GENERALIZE/CREATE
7. Store/Update → store_memory() or update_memory()
```

---

## Consolidation Intelligence

### Agent-Driven Decisions (No Thresholds)

The agent reviews search results and decides based on:
- **Semantic overlap**: Core concepts match?
- **Context alignment**: Same domain/timeframe?
- **Complementary vs Redundant**: New details or repetition?
- **Pattern emergence**: Multiple instances showing pattern?

### Actions

| Action | When | How |
|--------|------|-----|
| **MERGE** | Near-duplicate, same experience | Combine, delete old |
| **UPDATE** | Related, needs enhancement | Add new info, regenerate |
| **GENERALIZE** | Pattern from 2+ episodic | Create semantic |
| **CREATE** | Different/orthogonal | New independent memory |

---

## Installation

### 1. Install MCP Server V2
```bash
# Copy new server
cp qdrant_memory_mcp_server_v2.py ~/scripts/
chmod +x ~/scripts/qdrant_memory_mcp_server_v2.py

# Update Claude MCP config (~/.config/claude/mcp.json)
{
  "servers": {
    "qdrant-memory-v2": {
      "command": "python",
      "args": ["~/scripts/qdrant_memory_mcp_server_v2.py"]
    }
  }
}
```

### 2. Install V3.2 Skills
```bash
# Remove old V3 skills
rm -rf ~/.claude/skills/coder-memory-*

# Install V3.2
cp -r global/v3.2/coder-memory-store ~/.claude/skills/
cp -r global/v3.2/coder-memory-recall ~/.claude/skills/

# Restart Claude Code
```

---

## Testing

### Test Two-Stage Retrieval
```python
# Should return previews only
search_memory("API rate limiting patterns", "global", role="backend")

# Should return full content
get_memory("uuid-from-search", "global", role="backend")
```

### Test Consolidation
```python
# Store similar memory
store_memory(doc1, meta1, "global")
store_memory(doc2_similar, meta2, "global")

# Search should find both
search_memory(doc1, "global")

# Agent decides MERGE/UPDATE
# Then consolidates appropriately
```

---

## Migration from V3

### Automatic Migration
```bash
python migrate_v3_to_v3.2.py
```

This script:
1. Reads V3 collections
2. Maps to new simplified names
3. Preserves all memories
4. Updates metadata format

### Manual Migration
If needed, memories are compatible - just update collection names:
- `coder-memory` → `universal-patterns`
- `backend-dev` → `backend-patterns`
- `frontend-dev` → `frontend-patterns`
- `financial-engineer` → `quant-patterns`

---

## Key Differences from V3

| Aspect | V3 | V3.2 |
|--------|----|----|
| **Two-stage retrieval** | Documented but not implemented | Actually implemented in MCP v2 |
| **roles.yaml** | Duplicated 3x | Embedded in SKILL.md |
| **Collection names** | Inconsistent | Clean and simple |
| **MCP tools** | Returns full content | Preview/full separation |
| **Architecture** | Messy mix | Clean and consistent |
| **Working?** | Partially | Fully functional |

---

## Design Principles

1. **Simplicity**: Fewer moving parts, clearer naming
2. **Consistency**: Same patterns throughout
3. **Efficiency**: True two-stage saves tokens
4. **Intelligence**: Agent decides, not thresholds
5. **Pragmatism**: Actually works as documented

---

## Future (V4.0)

Potential enhancements:
- **Graph relationships**: Link related memories
- **Temporal decay**: Weighted by recency/frequency
- **Cross-role patterns**: Detect universality
- **Memory chains**: Episodic → Procedural → Semantic evolution
- **Undo/rollback**: Consolidation history