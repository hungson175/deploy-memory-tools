# Qdrant Similarity vs Distance Experiment

**Date:** 2026-01-07  
**Location:** `./experiments/dedup_mem/`  
**Purpose:** Empirically determine whether Qdrant uses similarity or distance scoring

## Experiment Overview

This experiment was conducted to definitively answer: **Does Qdrant use similarity scoring (1.0 = identical) or distance scoring (0.0 = identical)?**

## Files Generated

1. **sm-patterns.md** - List of 20 sample memories from universal-patterns collection
2. **qdrant_scoring_test.md** - Detailed experimental results and findings
3. **README.md** - This file

## Methodology

1. Fetched all 91 memories from `universal-patterns` collection
2. Computed pairwise cosine similarities (manual calculation using NumPy)
3. Identified the most similar pair among first 30 memories
4. Queried Qdrant for:
   - Score between Memory A and Memory B (most similar pair)
   - Score between Memory A and itself (self-match)
5. Compared manual cosine similarity with Qdrant's returned scores

## Results Summary

| Test | Score |
|------|-------|
| Manual cosine similarity (A vs B) | 0.775778 |
| Qdrant score (A vs B) | 0.775778 |
| Qdrant score (A vs A - self) | **1.000000** |

## Conclusion

**✅ PROVEN: Qdrant uses SIMILARITY scoring**

### Evidence:
1. Self-match returns score = **1.0** (not 0.0)
2. Qdrant score matches manual cosine similarity **exactly**
3. Higher scores indicate greater similarity

### Key Insight:
- Score of 1.0 = identical vectors
- Score range: [-1, 1] for cosine similarity
- Use `score_threshold` parameter to filter for minimum similarity

## Implications for Deduplication

Based on research in `docs/research/memory-deduplication-strategies.md`:

```python
# Correct usage for finding duplicates
results = client.query_points(
    collection_name='universal-patterns',
    query=vector,
    score_threshold=0.95,  # Only return if similarity >= 0.95
    limit=10
)
```

### Recommended Thresholds:

| Threshold | Interpretation | Action |
|-----------|----------------|--------|
| 0.95+ | Near-exact duplicates | Safe to merge automatically |
| 0.85-0.95 | High similarity | Review recommended |
| 0.70-0.85 | Related content | Probably not duplicates |

## Related Documents

- `/docs/research/memory-deduplication-strategies.md` - Full research on deduplication strategies
- `/docs/research/hindsight_applied.md` - Hindsight paper analysis for procedural memory

## Reproducibility

To reproduce this experiment:

```bash
cd /home/hungson175/dev/deploy-memory-tools
source .venv/bin/activate
cd experiments/dedup_mem
python << 'PYTHON_EOF'
# [Copy the Python script from qdrant_scoring_test.md]
PYTHON_EOF
```

## Next Steps

1. ✅ Confirmed Qdrant uses similarity scoring
2. Implement Option 1 from deduplication strategies (simple k-NN with 0.95 threshold)
3. Add LLM validation layer (Option 2) for production use
