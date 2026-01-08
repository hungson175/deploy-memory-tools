# Memory Deduplication Strategies for Qdrant Vector Database

**Research Date:** 2026-01-03
**Status:** Research Complete
**Related Backlog Item:** Memory Deduplication Service

---

## Executive Summary

This document presents research findings on implementing a memory deduplication service for our Qdrant-based memory system. The key insight is that **Qdrant has no built-in deduplication features** - each implementation requires custom logic using similarity search APIs.

We propose three implementation options ranging from simple to sophisticated, with demo code provided in `/experiments/deduplication/`.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Key Research Findings](#key-research-findings)
3. [Qdrant-Specific Capabilities](#qdrant-specific-capabilities)
4. [Three Implementation Options](#three-implementation-options)
5. [Recommended Approach](#recommended-approach)
6. [Sources](#sources)

---

## Problem Statement

Our Qdrant vector database accumulates duplicate memories over time, especially for roles like `scrum-master`. The issues include:

- **Semantic duplicates**: Same lesson expressed differently
- **Near-duplicates**: Minor variations of the same content
- **Exact duplicates**: Identical content stored multiple times
- **Messy metadata**: Inconsistent descriptions and tags across duplicates

Current state observed: Many memories with 85-99% similarity that should be consolidated.

---

## Key Research Findings

### 1. Similarity Detection Best Practices

**Optimal Thresholds** (varies by use case):
| Threshold | Interpretation | Use Case |
|-----------|----------------|----------|
| 0.95+ | Near-exact duplicates | Safe to merge automatically |
| 0.85-0.95 | High similarity | Review recommended |
| 0.70-0.85 | Related content | Probably not duplicates |

**Critical Insight**: Pure vector similarity creates false positives. Two memories like "Sprint 5 TDD violation" and "Sprint 10 TDD violation" may be 95% similar semantically but represent different incidents.

**Solution**: Two-stage hybrid approach:
1. **Stage 1**: Fast vector similarity to find candidates (cosine similarity > 0.85)
2. **Stage 2**: LLM validation to confirm true duplicates (checks context, time, specifics)

This reduced false positives from 97% to 3% in production systems.

### 2. Merge Strategies

**Retention Decision Logic** (in priority order):
1. **Most complete**: Keep the version with richer content
2. **Most recent**: If equal completeness, keep newer
3. **Best metadata**: Prefer entries with proper descriptions, tags

**Merge Process**:
1. Identify duplicate group (all items with similarity > threshold)
2. Select canonical version (most complete/recent)
3. Merge unique metadata from others (combine tags, update description)
4. Delete non-canonical duplicates
5. Re-embed canonical version if content changed

### 3. Clustering Approaches for Duplicate Groups

**Recommended Algorithms**:

| Algorithm | Best For | Complexity |
|-----------|----------|------------|
| **k-NN per item** | Small-medium datasets (<10K) | O(n × k) |
| **HDBSCAN** | Variable density clusters | O(n log n) |
| **Connected Components** | Transitive closure | O(n + edges) |

**For our use case** (~500-2000 memories): k-NN with k=5 per item is sufficient.

### 4. Production System Insights

**Milvus MinHash LSH**: Industry-leading solution for trillion-scale deduplication, but overkill for our use case.

**Pinecone Two-Stage**:
1. Vector similarity for candidate filtering
2. LSH classifier for final determination

**Scheduling Strategies**:
- **Batch (weekly)**: Best for our use case - run during low-activity periods
- **Real-time**: For applications requiring immediate deduplication
- **Hybrid**: Generate flags in real-time, dedupe in batch

---

## Qdrant-Specific Capabilities

### Key Finding: No Built-In Deduplication

> "Each dataset requires individual calibration, so there is no out-of-the-box solution for deduplication." — Qdrant GitHub Discussion #3268

### Recommended Qdrant Workflow

```python
# 1. Scroll through all points
points, offset = client.scroll(collection_name, limit=100, with_vectors=True)

# 2. Batch search for similar vectors
search_queries = [
    models.QueryRequest(
        query=point.vector,
        filter=models.Filter(must_not=[models.HasIdCondition(has_id=[point.id])]),
        limit=5,
        score_threshold=0.85
    )
    for point in points
]
results = client.query_batch_points(collection_name, requests=search_queries)

# 3. Build duplicate groups
# 4. Apply merge logic
# 5. Batch delete duplicates
client.batch_update_points(collection_name, update_operations=[
    models.DeleteOperation(delete=models.PointIdsList(points=duplicate_ids))
])
```

### Key Qdrant APIs for Deduplication

| API | Purpose |
|-----|---------|
| `scroll()` | Iterate through all points with vectors |
| `query_batch_points()` | Batch similarity search (efficient) |
| `batch_update_points()` | Batch delete/update operations |
| `score_threshold` | Filter by minimum similarity |
| `HasIdCondition` | Exclude self-matches |

### Performance Considerations

- **Batch operations**: Always prefer over individual calls
- **Scroll pagination**: Process in batches of 100-500
- **Idempotency**: All Qdrant APIs are idempotent - safe to re-run

---

## Three Implementation Options

### Option 1: Simple k-NN Deduplication (Recommended for MVP)

**Complexity**: Low
**Implementation Time**: 2-3 hours
**Accuracy**: Good for exact/near-exact duplicates

**Approach**:
1. For each memory, find top-5 similar memories (k-NN)
2. If similarity > 0.95, mark as duplicate pair
3. Build duplicate groups using Union-Find
4. Keep most recent in each group, delete others

**Pros**:
- Simple to implement and debug
- Fast execution (~seconds for 1000 memories)
- No external dependencies

**Cons**:
- Fixed threshold may miss some duplicates
- No semantic validation (may merge false positives)

**Best For**: Initial cleanup, regular maintenance

---

### Option 2: Two-Stage Hybrid (Vector + LLM Validation)

**Complexity**: Medium
**Implementation Time**: 4-6 hours
**Accuracy**: High (minimizes false positives)

**Approach**:
1. **Stage 1**: k-NN search with lower threshold (0.85)
2. **Stage 2**: LLM validates each candidate pair
   - Prompt: "Are these two memories describing the same lesson/incident?"
   - LLM checks: same topic, same time context, same specifics
3. Only merge LLM-confirmed duplicates

**Pros**:
- Dramatically reduces false positives (97% → 3%)
- Handles semantic nuance (different wording, same meaning)
- Can merge content intelligently

**Cons**:
- Slower (LLM calls for each candidate pair)
- API costs for LLM calls
- More complex implementation

**Best For**: Important deduplication runs, when accuracy matters

---

### Option 3: Clustering-Based with HDBSCAN

**Complexity**: High
**Implementation Time**: 6-8 hours
**Accuracy**: Best for finding all duplicate groups

**Approach**:
1. Extract all vectors from collection
2. Run HDBSCAN clustering on vectors
3. Each cluster = potential duplicate group
4. Within each cluster, apply merge logic
5. Optionally use LLM to validate large clusters

**Pros**:
- Finds all duplicate groups in one pass
- Handles varying density (some topics have more duplicates)
- Good visualization of duplicate landscape

**Cons**:
- Requires loading all vectors into memory
- More complex parameter tuning
- May create clusters that aren't duplicates

**Best For**: One-time deep cleanup, understanding duplicate distribution

---

## Recommended Approach

### For This Sprint: Option 1 (Simple k-NN)

**Rationale**:
1. Quick to implement and test
2. Solves the immediate "messy database" problem
3. Can be enhanced to Option 2 later

### Implementation Plan

```
experiments/
└── deduplication/
    ├── option1_simple_knn.py      # MVP implementation
    ├── option2_hybrid_llm.py      # Enhanced with LLM validation
    ├── option3_hdbscan.py         # Clustering approach
    └── utils.py                   # Shared utilities
```

### Suggested Workflow

1. **Dry-run mode**: List duplicates without deleting
2. **Review output**: Manually verify a sample
3. **Execute**: Run with deletion enabled
4. **Schedule**: Set up weekly cron job

---

## Memory System Integration

### Existing Infrastructure We Can Leverage

From our MCP server (`src/qdrant_memory_mcp/__main__.py`):

- `get_qdrant_client()`: Lazy client initialization
- `_get_embedding()`: Embedding generation with caching
- `ROLE_COLLECTIONS`: Collection name mapping
- `search_memory()`: Two-stage retrieval (previews then full)
- `delete_memory()`: Safe deletion by ID
- `update_memory()`: Update with re-embedding

### New Components Needed

1. **Deduplication service** (standalone script or MCP tool)
2. **Duplicate detection logic** (similarity + optional LLM)
3. **Merge strategy implementation**
4. **Audit logging** (what was merged/deleted)

---

## Sources

### Qdrant Official
- [Qdrant Search Documentation](https://qdrant.tech/documentation/concepts/search/)
- [Qdrant Filtering Documentation](https://qdrant.tech/documentation/concepts/filtering/)
- [Qdrant Points Documentation](https://qdrant.tech/documentation/concepts/points/)
- [Qdrant Deduplication Discussion #3268](https://github.com/orgs/qdrant/discussions/3268)

### Algorithms & Best Practices
- [Vector Similarity Explained - Pinecone](https://www.pinecone.io/learn/vector-similarity/)
- [Sentence Transformers for Deduplication - Milvus](https://milvus.io/ai-quick-reference/how-can-sentence-transformers-be-used-for-data-deduplication)
- [HDBSCAN Documentation](https://hdbscan.readthedocs.io/en/latest/how_hdbscan_works.html)
- [K-Nearest Neighbors for Similarity Detection](https://zilliz.com/ai-faq/how-do-i-use-embeddings-for-duplicate-detection)

### Production Systems
- [MinHash LSH in Milvus - Zilliz](https://milvus.io/blog/minhash-lsh-in-milvus-the-secret-weapon-for-fighting-duplicates-in-llm-training-data.md)
- [Document Deduplication - Pinecone](https://docs.pinecone.io/docs/document-deduplication)
- [Data Deduplication at Trillion Scale - Zilliz](https://zilliz.com/blog/data-deduplication-at-trillion-scale-solve-the-biggest-bottleneck-of-llm-training)

### Merge Strategies
- [How to Remove Duplicate Contents in Vector Databases - Alibaba Cloud](https://www.alibabacloud.com/blog/how-to-remove-duplicate-and-similar-contents-in-vector-databases_601909)
- [Consolidating Duplicate Records - Oracle](https://docs.oracle.com/en/cloud/saas/customer-data-management/faudm/how-you-consolidate-confirmed-duplicate-records.html)

### Internal Memory References
- Two-Stage Hybrid Deduplication (doc_id: dc6300e3)
- K-Nearest Neighbors for Efficiency (doc_id: 982fbc25)
- Vector Database Full CRUD Required (doc_id: 8fcfafb2)
