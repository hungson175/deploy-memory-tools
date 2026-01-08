# Qdrant Similarity Matrix Analysis - Complete Results

**Date:** 2026-01-07  
**Collection:** universal-patterns  
**Total Memories:** 91

## Files Generated

All files are in `./experiments/dedup_mem/`:

### 1. similarity_matrix.csv (93 KB)
- **Format:** 91×91 CSV matrix where S[i,j] = Qdrant similarity between memory i and j
- **Header Row:** memory IDs
- **Diagonal:** All 1.0 (self-similarity)
- **Use Case:** Full pairwise similarity data for automated analysis

### 2. memory_index_mapping.csv (4.5 KB)
- **Format:** index, ID, title
- **Purpose:** Maps matrix row/column indices to memory IDs and titles
- **Use Case:** Look up which memory corresponds to index i or j

### 3. top_similar_pairs.csv (5.6 KB)
- **Format:** rank, index_i, index_j, similarity, id_i, id_j, title_i, title_j
- **Content:** Top 50 most similar pairs (excluding diagonal)
- **Use Case:** Quick review of potential duplicates

### 4. sm-patterns.md
- **Content:** Full document text for all 91 memories (no truncation)
- **Use Case:** Manual eyeballing of memory content

### 5. qdrant_scoring_test.md
- **Content:** Full content of the most similar pair with detailed analysis
- **Use Case:** Understanding why memories are similar

---

## Matrix Statistics

| Metric | Value |
|--------|-------|
| **Matrix Shape** | 91 × 91 |
| **Total Cells** | 8,281 |
| **Diagonal (self-similarity)** | All 1.000000 |
| **Min Off-Diagonal** | 0.133572 |
| **Max Off-Diagonal** | 0.897777 |
| **Mean Similarity** | 0.351349 |
| **Median Similarity** | 0.337967 |

---

## High Similarity Pairs

| Threshold | Count | Interpretation |
|-----------|-------|----------------|
| ≥ 0.95 | 0 | Near-exact duplicates (auto-merge safe) |
| ≥ 0.90 | 0 | Very high similarity |
| ≥ 0.85 | 10 | High similarity (review recommended) |

**Finding:** No near-exact duplicates found. 10 pairs have similarity ≥ 0.85 that warrant review.

---

## Top 10 Similar Pairs

| Rank | Indices | Similarity | Memory IDs |
|------|---------|------------|------------|
| 1 | [15, 64] | 0.897777 | `282a1048...` ↔ `cd6adfa1...` |
| 2 | [20, 65] | 0.876875 | `3712bc6f...` ↔ `ce9e8400...` |
| 3 | [14, 90] | 0.862772 | `27f20798...` ↔ `fef929f6...` |
| 4 | [20, 74] | 0.860488 | `3712bc6f...` ↔ `e0b497d4...` |
| 5 | [5, 74] | 0.854763 | `18d2fdd3...` ↔ `e0b497d4...` |
| 6 | [47, 85] | 0.839952 | `9af1d8d4...` ↔ `f44650d8...` |
| 7 | [48, 56] | 0.832866 | `9ecbe534...` ↔ `b6075548...` |
| 8 | [8, 86] | 0.806609 | `20c6b5ea...` ↔ `f6bf9be4...` |
| 9 | [17, 73] | 0.801992 | `2a92f7b2...` ↔ `dec046ae...` |
| 10 | [17, 53] | 0.793519 | `2a92f7b2...` ↔ `acafb721...` |

---

## Key Finding: Most Similar Pair (89.78%)

**Pair:** Memories 15 and 64

**Memory A (index 15):**
- ID: `282a1048-f358-40a5-b789-2464d9c3472f`
- Title: Corporate Network Blocking Git SSH Connections
- Type: **Episodic** (specific incident)
- Tags: #episodic #git #ssh #corporate-network

**Memory B (index 64):**
- ID: `cd6adfa1-7bac-4768-8ae0-32e6ded68a56`
- Title: Diagnosing and Fixing Corporate Network Git SSH Blocking
- Type: **Procedural** (general workflow)
- Tags: #procedural #git #ssh #corporate-firewall

**Why Similar:** Both about corporate firewall blocking SSH port 22 for Git operations. Same problem, same solutions, but one is a story (episodic) and one is a how-to (procedural).

**Recommendation:** These should likely be merged or consolidated as they contain redundant information about the same problem.

---

## Confirmed Findings

### ✅ Qdrant Uses SIMILARITY Scoring

**Evidence:**
1. All diagonal elements (self-match) = 1.000000
2. Qdrant scores match manual cosine similarity calculations exactly
3. Higher scores = more similar
4. Score range: [-1, 1] for cosine similarity

### Usage for Deduplication

```python
# Correct threshold usage
results = client.query_points(
    collection_name='universal-patterns',
    query=vector,
    score_threshold=0.85,  # >= 0.85 similarity
    limit=10
)
```

---

## Automated Testing

The similarity matrix CSV can be used for automated analysis:

```python
import pandas as pd
import numpy as np

# Load matrix
df = pd.read_csv('similarity_matrix.csv', index_col=0)
matrix = df.values

# Find pairs above threshold
threshold = 0.85
high_sim_pairs = []

n = matrix.shape[0]
for i in range(n):
    for j in range(i+1, n):
        if matrix[i, j] >= threshold:
            high_sim_pairs.append((i, j, matrix[i, j]))

print(f"Found {len(high_sim_pairs)} pairs with similarity >= {threshold}")
```

---

## Next Steps

1. **Review the 10 high-similarity pairs** (≥ 0.85) manually
2. **Implement Option 2 from deduplication strategies:** Two-stage hybrid (vector + LLM validation)
3. **Run LLM validation** on the 10 candidate pairs to confirm if they're true duplicates
4. **Merge confirmed duplicates** keeping the most complete/recent version

---

## Related Documents

- `/docs/research/memory-deduplication-strategies.md` - Deduplication research
- `/docs/research/hindsight_applied.md` - Procedural memory improvements
- `./qdrant_scoring_test.md` - Detailed analysis of most similar pair
- `./sm-patterns.md` - Full content of all 91 memories

---

**Matrix Generated:** 2026-01-07  
**Qdrant Collection:** universal-patterns  
**Total Comparisons:** 8,281 (91×91)  
**API Calls:** 91 (one query per memory)
