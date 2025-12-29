---
name: coder-memory-recall
description: Retrieve universal coding patterns from vector database using true two-stage retrieval. Auto-invokes before complex tasks or when user says "--recall". Searches relevant role collections based on task context.
---

# Coder Memory Recall V3.2 - Clean Vector Architecture

**Purpose**: Efficiently retrieve relevant patterns using two-stage retrieval (preview → full content).

**When to Use**:
- Before starting complex/unfamiliar tasks
- When encountering technical problems
- User says "--recall" or asks for past patterns
- Need architectural guidance or debugging strategies

**When NOT to Use**:
- Routine/trivial tasks
- Just recalled similar knowledge
- Project-specific questions (use git history)

**Remember**: Search for both #success and #failure - failures often more valuable.

---

## EMBEDDED ROLE CONFIGURATION

```yaml
# Embedded configuration - no external files needed
role_collections:
  global:
    universal:
      name: "universal-patterns"
      description: "Search here for cross-domain patterns"
      query_hints: ["general", "architecture", "debugging", "performance"]

    backend:
      name: "backend-patterns"
      description: "Backend engineering patterns"
      query_hints: ["api", "database", "auth", "server", "microservices"]

    frontend:
      name: "frontend-patterns"
      description: "Frontend engineering patterns"
      query_hints: ["react", "vue", "ui", "component", "state"]

    quant:
      name: "quant-patterns"
      description: "Quantitative finance patterns"
      query_hints: ["trading", "backtest", "risk", "portfolio"]

    devops:
      name: "devops-patterns"
      description: "DevOps and infrastructure patterns"
      query_hints: ["docker", "kubernetes", "ci-cd", "terraform"]

    ml:
      name: "ml-patterns"
      description: "Machine learning patterns"
      query_hints: ["model", "training", "neural", "llm", "embedding"]

    security:
      name: "security-patterns"
      description: "Security engineering patterns"
      query_hints: ["vulnerability", "encryption", "auth", "pentest"]

    mobile:
      name: "mobile-patterns"
      description: "Mobile development patterns"
      query_hints: ["ios", "android", "react-native", "flutter"]

# Role detection from task context
role_detection:
  patterns:
    backend: "api|endpoint|database|server|auth|rest|graphql"
    frontend: "react|vue|component|ui|dom|css|state"
    quant: "trading|backtest|portfolio|risk|market"
    devops: "deploy|docker|kubernetes|ci|cd"
    ml: "model|training|neural|embedding|llm"
    security: "vulnerability|encryption|pentest|jwt"
    mobile: "ios|android|native|flutter|swift"

  multi_role_strategy: "search_all"  # When multiple roles detected
  default_role: "universal"          # When no clear role
```

---

## PHASE 1: Intelligent Query Construction

### Role Detection
```python
# Analyze task context for role keywords
detected_roles = detect_roles_from_context(task_description)

if len(detected_roles) == 0:
    roles_to_search = ["universal"]
elif len(detected_roles) == 1:
    roles_to_search = detected_roles
else:  # Multiple roles detected
    roles_to_search = detected_roles + ["universal"]
```

### Query Building

**Semantic Query** (not just keywords):
```python
# Build 2-3 sentence summary for semantic search
query = build_semantic_query(
    problem_description,
    technical_context,
    desired_outcome
)

# Example output:
# "Implementing rate limiting for REST API to prevent abuse.
#  Need patterns for handling burst traffic and client fairness.
#  Looking for proven approaches that scale."
```

**Memory Type Hints**:
- Starting new implementation? → Focus on procedural/semantic
- Debugging specific issue? → Focus on episodic
- Need architecture guidance? → Focus on semantic
- Unclear? → Search all types

---

## PHASE 2: Two-Stage Retrieval

### Stage 1: Search for Previews

```python
all_previews = []
for role in roles_to_search:
    previews = search_memory(
        query=semantic_query,
        memory_level="global",
        role=role,
        limit=10  # Cast wider net
    )
    all_previews.extend(previews.results)

# Sort by similarity across all roles
all_previews.sort(key=lambda x: x.similarity, reverse=True)
```

**Preview Analysis** (Intelligence, not thresholds):
```python
relevant_previews = []
for preview in all_previews:
    relevance = analyze_preview(
        preview.title,
        preview.description,
        preview.tags,
        task_context
    )
    if relevance.is_relevant:
        relevant_previews.append({
            "preview": preview,
            "relevance_reason": relevance.reason,
            "priority": relevance.priority  # high/medium/low
        })
```

### Stage 2: Retrieve Full Content

**Efficient Batch Retrieval**:
```python
# Group by role for efficient retrieval
by_role = group_by_role(relevant_previews)

full_memories = {}
for role, preview_group in by_role.items():
    doc_ids = [p.preview.doc_id for p in preview_group]

    # Batch retrieve for efficiency
    memories = batch_get_memories(
        doc_ids=doc_ids,
        memory_level="global",
        role=role
    )
    full_memories[role] = memories.memories
```

**Token Efficiency**:
- Search examined: 10-30 previews (~500 tokens)
- Full content retrieved: 3-5 memories (~2000 tokens)
- **Savings: ~80%** vs retrieving all full content

---

## PHASE 3: Relevance Ranking

### Multi-Factor Scoring
```python
def rank_memories(full_memories, task_context):
    scored = []
    for memory in full_memories:
        score = calculate_relevance(
            semantic_similarity=memory.similarity,
            memory_type_match=matches_needed_type(memory.type),
            tag_overlap=count_relevant_tags(memory.tags),
            temporal_relevance=get_recency_weight(memory.created_at),
            outcome_alignment=matches_desired_outcome(memory.tags)
        )
        scored.append((memory, score))

    # Return top 3 most relevant
    return sorted(scored, key=lambda x: x[1], reverse=True)[:3]
```

### Outcome Consideration
- Need proven solution? → Prioritize #success
- Debugging failure? → Prioritize #failure patterns
- Exploring options? → Mix both

---

## PHASE 4: Present Results

### Standard Format
```
🔍 Memory Recall Results

**Query**: <user question or inferred need>
**Roles Searched**: backend, universal
**Previews Examined**: 24
**Memories Retrieved**: 5

---

## 🥇 Most Relevant: [Title]

**Role**: backend-patterns
**Type**: Procedural
**Relevance**: High - Direct pattern match for rate limiting
**Tags**: #backend #api #rate-limiting #success

<Full memory content here>

**Why This Helps**: <1-2 sentences on specific applicability>

---

## 🥈 Relevant: [Title]

[Similar format]

---

## 🥉 Related: [Title]

[Similar format]

---

## 💡 Application Guidance

<2-3 sentences synthesizing insights and suggesting application>

**Token Efficiency**: Saved ~2,400 tokens by retrieving only relevant memories
```

### No Results Format
```
🔍 Memory Recall Results

**Query**: <query>
**Roles Searched**: backend, frontend, universal
**Previews Examined**: 30
**Relevant Found**: 0

No existing patterns match your specific need.

**Suggestions**:
- This might be a novel problem worth storing after solving
- Try broader search terms or different role
- Proceed with first principles and document learnings
```

---

## PHASE 5: Learning Feedback Loop

### Update Recall Metadata
```python
# Track which memories were helpful
for memory in presented_memories:
    update_memory(
        doc_id=memory.doc_id,
        document=memory.document,  # Unchanged
        metadata={
            ...existing,
            "last_recall_time": now(),
            "recall_count": existing.recall_count + 1,
            "helpfulness": track_if_applied()  # Future enhancement
        },
        memory_level="global"
    )
```

### Pattern Recognition
If no relevant memories found but task succeeds:
- Strong signal to store new pattern after completion
- Indicates knowledge gap in memory system

---

## Key V3.2 Improvements

1. **True Two-Stage**: Actually implemented, saves ~80% tokens
2. **Embedded Config**: No external files to maintain
3. **Multi-Role Search**: Searches across relevant roles
4. **Intelligent Ranking**: Context-aware relevance scoring
5. **Efficiency Metrics**: Shows token savings

---

## Workflow Examples

### Example 1: API Development
```
Task: "Implement webhook processing system"

1. Detect roles: ["backend", "universal"]
2. Build query: "Implementing webhook processing system. Need patterns
                 for reliable delivery, retry logic, and event ordering."
3. Search both collections → 18 previews
4. Analyze previews → 4 relevant
5. Retrieve full → 4 memories
6. Rank by relevance → Present top 3
7. Token efficiency: 80% saved
```

### Example 2: Debugging Session
```
Task: "React component re-rendering infinitely"

1. Detect roles: ["frontend"]
2. Build query: "React component stuck in infinite re-render loop.
                 Need debugging patterns for render cycles and state updates."
3. Search frontend-patterns → 12 previews
4. Focus on #failure tags → 3 relevant
5. Retrieve full → 3 memories
6. All 3 are relevant failure patterns
7. Present with emphasis on failure lessons
```

### Example 3: Cross-Domain Architecture
```
Task: "Design event-driven microservices"

1. Detect roles: ["backend", "devops", "universal"]
2. Build query: "Designing event-driven microservice architecture.
                 Need patterns for event sourcing, service communication."
3. Search all three → 35 previews
4. Analyze → 7 relevant across roles
5. Retrieve full → 7 memories
6. Rank → Mix of backend (events) + devops (deploy) + universal (architecture)
7. Present top 3 with cross-domain synthesis
```

---

## Testing This Skill

### Test Two-Stage
```python
# Search should return previews only
result = search_memory("api patterns", "global", role="backend")
assert "doc_id" in result.results[0]
assert "document" not in result.results[0]  # No full content

# Get should return full content
full = get_memory(result.results[0].doc_id, "global", "backend")
assert "document" in full  # Has full content
```

### Test Role Detection
```
"Building REST API" → ["backend"]
"React component styling" → ["frontend"]
"Deploy with Docker" → ["devops"]
"Neural network training" → ["ml"]
"API with React frontend" → ["backend", "frontend", "universal"]
```

### Test Efficiency
```
# Measure tokens
search_tokens = count_tokens(search_results)  # ~500
full_tokens = count_tokens(all_full_memories)  # ~10,000
efficient_tokens = count_tokens(retrieved_only)  # ~2,000
savings = 1 - (search_tokens + efficient_tokens) / full_tokens  # ~75%
```