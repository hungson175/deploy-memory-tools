# Memory Deduplication Experiments

Demo implementations for deduplicating memories in Qdrant vector database.

## Prerequisites

```bash
# Install dependencies (from project root)
cd /home/hungson175/dev/deploy-memory-tools
source .venv/bin/activate
uv pip install hdbscan numpy  # For Option 3
```

## Options

### Option 1: Simple k-NN Deduplication (Recommended for MVP)

**Complexity:** Low | **Accuracy:** Good for near-exact duplicates

```bash
# Dry run - list duplicates without deleting
python option1_simple_knn.py --collection scrum-master-patterns --dry-run

# Execute - delete duplicates
python option1_simple_knn.py --collection scrum-master-patterns --execute

# All collections with custom threshold
python option1_simple_knn.py --all --threshold 0.92 --dry-run
```

### Option 2: Two-Stage Hybrid (Vector + LLM Validation)

**Complexity:** Medium | **Accuracy:** High (reduces false positives from 97% to 3%)

```bash
# Dry run with LLM validation (uses xAI/Grok)
python option2_hybrid_llm.py --collection scrum-master-patterns --dry-run

# Skip LLM validation (fallback to high-threshold only)
python option2_hybrid_llm.py --collection scrum-master-patterns --skip-llm --dry-run

# Execute
python option2_hybrid_llm.py --collection scrum-master-patterns --execute
```

### Option 3: HDBSCAN Clustering

**Complexity:** High | **Accuracy:** Best for finding all duplicate groups

```bash
# Dry run with clustering
python option3_hdbscan.py --collection scrum-master-patterns --dry-run

# With visualization (requires matplotlib)
python option3_hdbscan.py --collection scrum-master-patterns --visualize --viz-output clusters.png

# Adjust clustering sensitivity
python option3_hdbscan.py --collection scrum-master-patterns --min-cluster-size 3 --dry-run
```

## Thresholds Guide

| Threshold | Interpretation | Risk |
|-----------|----------------|------|
| 0.95+ | Near-exact duplicates | Very safe |
| 0.90-0.95 | High similarity | Safe |
| 0.85-0.90 | Moderate similarity | Review recommended |
| <0.85 | Related content | Probably not duplicates |

## Output

All scripts support:
- `--dry-run`: List duplicates without deleting (default)
- `--execute`: Actually delete duplicates
- `--output FILE`: Save report to JSON

## Recommended Workflow

1. **Start with Option 1** at threshold 0.95 (dry-run)
2. Review the output manually
3. If satisfied, run with `--execute`
4. For difficult cases, use Option 2 with LLM validation
5. Use Option 3 for one-time deep cleanup to understand duplicate landscape
