---
name: coder-memory-store
description: Store universal coding patterns into vector database. Auto-invokes after difficult tasks with broadly-applicable lessons. Trigger with "--store" or when user expresses frustration (strong learning signals). Uses true two-stage retrieval with MCP server v2.
---

# Coder Memory Store V3.2 - Clean Vector Architecture

**Purpose**: Extract and store universal coding patterns using intelligent consolidation and true two-stage retrieval.

**When to Use**:
- After solving non-obvious problems with universal lessons
- User says "--store", "--learn", or expresses frustration
- Discovered patterns applicable across projects/frameworks
- Both SUCCESS and FAILURE trajectories (failures often more valuable)

**Selection Criteria**: Most tasks yield 0-1 insights. Be selective but capture strong signals.

---

## EMBEDDED ROLE CONFIGURATION

```yaml
# No external roles.yaml - configuration embedded here
role_collections:
  global:
    universal:
      name: "universal-patterns"
      description: "Cross-domain patterns applicable anywhere"
      common_tags: [architecture, debugging, performance, best-practices]

    backend:
      name: "backend-patterns"
      description: "Backend engineering: APIs, databases, auth, etc."
      common_tags: [api, database, auth, microservices, caching]

    frontend:
      name: "frontend-patterns"
      description: "Frontend engineering: UI, state, components, etc."
      common_tags: [react, vue, ui, components, state-management]

    quant:
      name: "quant-patterns"
      description: "Quantitative finance: trading, risk, backtesting"
      common_tags: [trading, backtesting, risk, portfolio, options]

    devops:
      name: "devops-patterns"
      description: "DevOps: CI/CD, infrastructure, monitoring"
      common_tags: [ci-cd, docker, kubernetes, terraform, monitoring]

    ml:
      name: "ml-patterns"
      description: "Machine learning: models, training, deployment"
      common_tags: [neural-nets, training, embeddings, llm, datasets]

    security:
      name: "security-patterns"
      description: "Security engineering: auth, crypto, vulnerabilities"
      common_tags: [authentication, encryption, vulnerabilities, pentesting]

    mobile:
      name: "mobile-patterns"
      description: "Mobile development: iOS, Android, React Native"
      common_tags: [ios, android, react-native, flutter, mobile-ui]

# Dynamic role detection rules
role_detection:
  keywords:
    backend: [api, database, server, auth, endpoint, orm, queue]
    frontend: [react, vue, component, ui, dom, css, state]
    quant: [trading, backtest, portfolio, risk, option, market]
    devops: [docker, kubernetes, ci, cd, deploy, terraform]
    ml: [model, training, neural, embedding, llm, dataset]
    security: [vulnerability, encryption, pentest, auth, jwt]
    mobile: [ios, android, native, flutter, swift, kotlin]

  default: universal  # When unclear or cross-cutting
```

---

## PHASE 1: Extract Insights

Analyze conversation for **0-3 insights** (usually 0-1).

### Classification
- **Episodic**: Concrete debugging/implementation story with context
- **Procedural**: Repeatable workflow or process
- **Semantic**: Abstract principle or pattern

### Criteria (ALL must be true)
1. **Non-obvious**: Not well-documented standard practice
2. **Universal**: Applies beyond specific project/framework
3. **Actionable**: Provides concrete guidance
4. **Valuable**: Would help future similar situations

### Role Detection
```python
# Scan for keywords to detect appropriate role
detected_role = scan_keywords(task_context, role_detection.keywords)
if not detected_role or multiple_roles_detected:
    use "universal"  # Cross-cutting patterns
```

---

## PHASE 2: Search for Similar (Two-Stage)

### Stage 1: Search for Previews

Use **full formatted text** as query for rich semantic matching:

```python
# Search returns ONLY previews (title + description + metadata)
previews = search_memory(
    query=formatted_memory_text,  # Full text for better matching
    memory_level="global",
    role=detected_role,
    limit=10  # Get more candidates for review
)
```

**Preview format**:
```json
{
  "doc_id": "uuid",
  "title": "Memory title",
  "description": "One line summary",
  "similarity": 0.89,
  "memory_type": "episodic",
  "tags": ["api", "debugging"]
}
```

### Stage 2: Retrieve Full Content (If Needed)

**Intelligent preview analysis** - Decide which need full retrieval:
- High similarity (>0.8) → Likely duplicate, retrieve for MERGE
- Medium similarity (0.6-0.8) → Possibly related, retrieve for UPDATE
- Multiple similar episodic → Retrieve all for GENERALIZE
- Low similarity (<0.6) → Different, no retrieval needed

```python
# Retrieve full content for relevant memories only
if likely_duplicate_or_related:
    full_memories = batch_get_memories(
        doc_ids=[preview.doc_id for preview in relevant_previews],
        memory_level="global",
        role=detected_role
    )
```

---

## PHASE 3: Intelligent Consolidation

### Decision Framework (No Rigid Thresholds)

Review retrieved memories and decide action:

| Signal | Analysis | Action |
|--------|----------|--------|
| **Near-identical content** | Same problem, same solution | **MERGE** - Combine best parts |
| **Same topic, new angle** | Complementary information | **UPDATE** - Enhance existing |
| **Pattern emerges** | 2+ episodic show pattern | **GENERALIZE** - Create semantic |
| **Different domain** | Orthogonal concept | **CREATE** - New memory |

### Consolidation Actions

#### MERGE (Duplicates)
```python
existing = get_memory(duplicate_id, "global", role)
merged_content = combine_best_parts(existing.document, new_memory)
delete_memory(duplicate_id, "global", role)
store_memory(merged_content, metadata, "global")
```

#### UPDATE (Related)
```python
existing = get_memory(related_id, "global", role)
updated_content = add_new_information(existing.document, new_insights)
update_memory(related_id, updated_content, metadata, "global")
```

#### GENERALIZE (Pattern)
```python
episodic_memories = batch_get_memories(pattern_ids, "global", role)
semantic_pattern = extract_common_pattern(episodic_memories)
store_memory(semantic_pattern, {memory_type: "semantic"}, "global")
# Keep episodic examples, add cross-references
```

#### CREATE (New)
```python
store_memory(new_memory, metadata, "global")
```

---

## PHASE 4: Store Memory

### Format (Enforced Compact)
```markdown
**Title:** <concise, searchable title>
**Description:** <one sentence summary>

**Content:** <3-5 sentences: what happened, what tried, what worked/failed, key lesson>

**Tags:** #<role> #<type> #<outcome> #<domain>
```

### Metadata Structure
```python
metadata = {
    "memory_level": "global",
    "memory_type": "episodic|procedural|semantic",
    "role": detected_role,  # From embedded config
    "tags": ["backend", "api", "rate-limiting", "failure"],
    "title": memory_title,
    "created_at": iso_timestamp,
    "confidence": "high|medium|low",  # How sure about this pattern
    "frequency": 1,  # Times seen (updated on MERGE/UPDATE)
    "last_recall_time": None  # Set on recall
}
```

### Store via MCP V2
```python
result = store_memory(
    document=formatted_memory,
    metadata=metadata,
    memory_level="global"
)
# Returns: {doc_id, status, collection, message}
```

### Cross-Role Storage
If pattern applies to multiple roles:
```python
# Store to primary role
store_memory(doc, {..., "role": "backend"}, "global")

# Also store generalized version to universal
universal_version = generalize_for_broader_application(doc)
store_memory(universal_version, {..., "role": "universal"}, "global")
```

---

## PHASE 5: Dynamic Configuration Updates

### When New Role Emerges
If task doesn't fit existing roles:
```python
# Add new role to embedded config in this file
new_role = {
    "name": f"{domain}-patterns",
    "description": detected_description,
    "common_tags": extracted_tags
}
# Update SKILL.md using Edit tool
edit_skill_file(add_role=new_role)
```

### When New Tags Discovered
```python
# Add to role's common_tags
if tag not in role_config[role].common_tags:
    add_tag_to_role(role, tag)
```

---

## Final Report

### Success Case
```
✅ Memory Storage Complete

**Insight Type**: Episodic - API rate limiting failure
**Role**: backend-patterns
**Similarity Check**: Found 2 related memories
**Action Taken**: MERGED with existing rate-limiting pattern
**Collection**: backend-patterns (247 total memories)

**Key Learning Captured**:
"Exponential backoff with jitter prevents thundering herd"

**Two-Stage Efficiency**:
- Previews reviewed: 10
- Full memories retrieved: 2
- Tokens saved: ~80% vs full retrieval
```

### No Insights Case
```
✅ Storage Analysis Complete

**Insights Found**: 0
**Reason**: Routine debugging - no universal patterns

This was standard work without broadly-applicable lessons.
Patterns specific to this project should be documented in code comments.
```

---

## Strong Learning Signals

### Frustration Detection
User frustration = highest-value learning opportunity:

**Trigger words**: fuck, shit, damn, moron, idiot, stupid, garbage, wtf, "this is ridiculous", "you're not listening"

**Action**: IMMEDIATELY store the failure pattern with full context

**Example**:
```markdown
**Title:** Misunderstood File Context Leading to Wrong Edit
**Description:** User said "fucking moron" when I edited wrong file despite clear context.

**Content:** User requested auth logic update in src/auth.ts but I modified src/utils.ts instead. Failed because I didn't carefully verify file context from user's message. User's strong frustration indicates critical failure pattern. Lesson: Always double-check file paths in user's context before editing.

**Tags:** #universal #episodic #failure #attention #strong-signal
```

---

## Key V3.2 Improvements

1. **Embedded config**: No external roles.yaml to maintain
2. **True two-stage**: Actually saves tokens with preview/full separation
3. **Cleaner collections**: Simple, consistent naming
4. **Dynamic updates**: Config can evolve with usage
5. **Working implementation**: MCP V2 server actually implements this

---

## Testing This Skill

```python
# Test role detection
"Building REST API endpoints" → Should detect "backend"

# Test two-stage retrieval
search_memory("rate limiting", "global", role="backend")
# Should return previews only

get_memory("uuid-from-search", "global", role="backend")
# Should return full content

# Test consolidation
Store similar memory → Should MERGE
Store complementary → Should UPDATE
Store 3 similar episodic → Should GENERALIZE
```