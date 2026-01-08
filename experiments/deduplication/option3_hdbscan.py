#!/usr/bin/env python3
"""
Option 3: Clustering-Based Deduplication with HDBSCAN

Complexity: High
Best for: One-time deep cleanup, understanding duplicate distribution

Approach:
1. Extract all vectors from collection
2. Run HDBSCAN clustering on vectors
3. Each cluster = potential duplicate group
4. Within each cluster, apply merge logic
5. Optionally use LLM to validate large clusters

HDBSCAN (Hierarchical Density-Based Spatial Clustering):
- Automatically finds clusters of varying density
- No need to specify number of clusters
- Robust to noise and outliers
- Good for finding duplicate groups of different sizes

Usage:
    # Dry run (find clusters, list potential duplicates)
    python option3_hdbscan.py --collection scrum-master-patterns --dry-run

    # Execute deletion
    python option3_hdbscan.py --collection scrum-master-patterns --execute

    # Adjust clustering sensitivity
    python option3_hdbscan.py --collection scrum-master-patterns --min-cluster-size 3 --dry-run
"""

import argparse
from typing import Dict, List, Optional

import numpy as np

from utils import (
    DeduplicationReport,
    DuplicateGroup,
    MemoryPoint,
    batch_delete_points,
    get_qdrant_client,
    list_all_collections,
    logger,
    save_report,
    scroll_all_points,
    select_canonical,
    ROLE_COLLECTIONS,
)

# Optional: Import HDBSCAN (needs to be installed)
try:
    import hdbscan
    HDBSCAN_AVAILABLE = True
except ImportError:
    HDBSCAN_AVAILABLE = False
    logger.warning("HDBSCAN not installed. Install with: pip install hdbscan")


def cluster_vectors_hdbscan(
    vectors: np.ndarray,
    min_cluster_size: int = 2,
    min_samples: int = 1,
    cluster_selection_epsilon: float = 0.0,
) -> np.ndarray:
    """
    Cluster vectors using HDBSCAN.

    Args:
        vectors: numpy array of shape (n_samples, n_dimensions)
        min_cluster_size: Minimum points to form a cluster (default: 2)
        min_samples: How conservative the clustering is (default: 1)
        cluster_selection_epsilon: Distance threshold for cluster merging

    Returns:
        Array of cluster labels (-1 = noise/not clustered)
    """
    if not HDBSCAN_AVAILABLE:
        raise ImportError("HDBSCAN not installed. Install with: pip install hdbscan")

    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        cluster_selection_epsilon=cluster_selection_epsilon,
        metric="euclidean",  # For normalized vectors, euclidean works well
        gen_min_span_tree=True,
    )

    labels = clusterer.fit_predict(vectors)
    return labels


def find_duplicates_clustering(
    collection_name: str,
    min_cluster_size: int = 2,
    min_samples: int = 1,
    cluster_selection_epsilon: float = 0.0,
) -> DeduplicationReport:
    """
    Find duplicates using HDBSCAN clustering.

    Args:
        collection_name: Name of the collection to scan
        min_cluster_size: Minimum points to form a cluster
        min_samples: How conservative the clustering is
        cluster_selection_epsilon: Distance threshold for cluster merging

    Returns:
        DeduplicationReport with duplicate groups from clusters
    """
    client = get_qdrant_client()

    # Step 1: Get all points with vectors
    logger.info(f"Loading all vectors from: {collection_name}")
    all_points = scroll_all_points(client, collection_name, with_vectors=True)
    logger.info(f"Found {len(all_points)} memories")

    if len(all_points) < 2:
        logger.info("Not enough memories to find duplicates")
        return DeduplicationReport(
            collection=collection_name,
            total_memories=len(all_points),
            duplicate_groups=[],
            memories_to_delete=0,
            dry_run=True,
        )

    point_map: Dict[str, MemoryPoint] = {p.id: p for p in all_points}
    point_ids = [p.id for p in all_points]

    # Step 2: Extract vectors into numpy array
    logger.info("Building vector matrix...")
    vectors = np.array([p.vector for p in all_points])
    logger.info(f"Vector matrix shape: {vectors.shape}")

    # Step 3: Run HDBSCAN clustering
    logger.info(f"Running HDBSCAN (min_cluster_size={min_cluster_size}, "
                f"min_samples={min_samples}, epsilon={cluster_selection_epsilon})")

    labels = cluster_vectors_hdbscan(
        vectors,
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        cluster_selection_epsilon=cluster_selection_epsilon,
    )

    # Count clusters
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)
    logger.info(f"Found {n_clusters} clusters, {n_noise} noise points")

    # Step 4: Build duplicate groups from clusters
    cluster_points: Dict[int, List[str]] = {}
    for idx, label in enumerate(labels):
        if label == -1:  # Noise, skip
            continue
        if label not in cluster_points:
            cluster_points[label] = []
        cluster_points[label].append(point_ids[idx])

    duplicate_groups: List[DuplicateGroup] = []

    for cluster_id, member_ids in cluster_points.items():
        if len(member_ids) <= 1:
            continue  # Not a duplicate group

        members = [point_map[mid] for mid in member_ids]

        # Select canonical version
        canonical = select_canonical(members, point_map)

        # Calculate similarity scores (approximate from vectors)
        canonical_vec = np.array(point_map[canonical.id].vector)
        scores = {}
        for member in members:
            if member.id != canonical.id:
                member_vec = np.array(member.vector)
                # Cosine similarity
                similarity = np.dot(canonical_vec, member_vec) / (
                    np.linalg.norm(canonical_vec) * np.linalg.norm(member_vec)
                )
                scores[member.id] = float(similarity)

        duplicate_ids = [m.id for m in members if m.id != canonical.id]

        group = DuplicateGroup(
            canonical_id=canonical.id,
            duplicate_ids=duplicate_ids,
            similarity_scores=scores,
            reason=f"HDBSCAN cluster {cluster_id}",
        )
        duplicate_groups.append(group)

        logger.info(
            f"Cluster {cluster_id}: Keep '{canonical.title[:50]}...' "
            f"({len(duplicate_ids)} duplicates)"
        )

    memories_to_delete = sum(len(g.duplicate_ids) for g in duplicate_groups)

    return DeduplicationReport(
        collection=collection_name,
        total_memories=len(all_points),
        duplicate_groups=duplicate_groups,
        memories_to_delete=memories_to_delete,
        dry_run=True,
    )


def visualize_clusters(
    all_points: List[MemoryPoint],
    labels: np.ndarray,
    output_path: Optional[str] = None
) -> None:
    """
    Visualize clusters using dimensionality reduction.
    Requires: pip install scikit-learn matplotlib
    """
    try:
        from sklearn.manifold import TSNE
        import matplotlib.pyplot as plt
    except ImportError:
        logger.warning("scikit-learn and matplotlib required for visualization")
        return

    vectors = np.array([p.vector for p in all_points])

    # Reduce to 2D using t-SNE
    logger.info("Running t-SNE for visualization...")
    tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(all_points) - 1))
    vectors_2d = tsne.fit_transform(vectors)

    # Plot
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(
        vectors_2d[:, 0],
        vectors_2d[:, 1],
        c=labels,
        cmap='viridis',
        alpha=0.6,
        s=50
    )
    plt.colorbar(scatter, label='Cluster')
    plt.title(f'Memory Clusters (n={len(all_points)}, clusters={len(set(labels)) - 1})')
    plt.xlabel('t-SNE dimension 1')
    plt.ylabel('t-SNE dimension 2')

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        logger.info(f"Visualization saved to {output_path}")
    else:
        plt.show()


def execute_deduplication(report: DeduplicationReport) -> int:
    """Execute the deduplication (delete duplicates)"""
    if not report.duplicate_groups:
        logger.info("No duplicates to delete")
        return 0

    client = get_qdrant_client()

    all_ids_to_delete = []
    for group in report.duplicate_groups:
        all_ids_to_delete.extend(group.duplicate_ids)

    logger.info(f"Deleting {len(all_ids_to_delete)} duplicate memories...")
    deleted = batch_delete_points(client, report.collection, all_ids_to_delete)

    logger.info(f"Deleted {deleted} memories from {report.collection}")
    return deleted


def main():
    parser = argparse.ArgumentParser(
        description="HDBSCAN Clustering-Based Deduplication"
    )
    parser.add_argument(
        "--collection", "-c",
        help="Collection name to scan"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Scan all role collections"
    )
    parser.add_argument(
        "--min-cluster-size",
        type=int,
        default=2,
        help="Minimum points to form a cluster (default: 2)"
    )
    parser.add_argument(
        "--min-samples",
        type=int,
        default=1,
        help="How conservative the clustering is (default: 1)"
    )
    parser.add_argument(
        "--epsilon",
        type=float,
        default=0.0,
        help="Distance threshold for cluster merging (default: 0.0)"
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Generate t-SNE visualization of clusters"
    )
    parser.add_argument(
        "--viz-output",
        help="Save visualization to file (e.g., clusters.png)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List duplicates without deleting (default)"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete duplicates"
    )
    parser.add_argument(
        "--output", "-o",
        help="Save report to JSON file"
    )

    args = parser.parse_args()

    if not HDBSCAN_AVAILABLE:
        print("ERROR: HDBSCAN is not installed.")
        print("Install with: pip install hdbscan")
        return

    if not args.collection and not args.all:
        parser.error("Either --collection or --all is required")

    if args.execute and args.dry_run:
        parser.error("Cannot use both --dry-run and --execute")

    dry_run = not args.execute

    # Determine collections to scan
    if args.all:
        client = get_qdrant_client()
        collections = list_all_collections(client)
        collections = [c for c in ROLE_COLLECTIONS.values() if c in collections]
    else:
        collections = [args.collection]

    all_reports = []

    for collection_name in collections:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {collection_name}")
        logger.info(f"{'='*60}")

        try:
            report = find_duplicates_clustering(
                collection_name,
                min_cluster_size=args.min_cluster_size,
                min_samples=args.min_samples,
                cluster_selection_epsilon=args.epsilon,
            )
            report.dry_run = dry_run

            print(f"\n{report.summary}\n")

            if report.duplicate_groups:
                print("Clusters (Potential Duplicate Groups):")
                for i, group in enumerate(report.duplicate_groups, 1):
                    print(f"\n  Cluster {i}:")
                    print(f"    Keep: {group.canonical_id}")
                    for dup_id, score in group.similarity_scores.items():
                        print(f"    Delete: {dup_id} (similarity: {score:.3f})")
                    print(f"    Reason: {group.reason}")

            if args.visualize:
                # Re-fetch points for visualization
                client = get_qdrant_client()
                all_points = scroll_all_points(client, collection_name, with_vectors=True)
                vectors = np.array([p.vector for p in all_points])
                labels = cluster_vectors_hdbscan(
                    vectors,
                    min_cluster_size=args.min_cluster_size,
                    min_samples=args.min_samples,
                    cluster_selection_epsilon=args.epsilon,
                )
                visualize_clusters(all_points, labels, args.viz_output)

            if not dry_run and report.duplicate_groups:
                deleted = execute_deduplication(report)
                print(f"\nDeleted {deleted} memories")

            all_reports.append(report)

        except Exception as e:
            logger.error(f"Error processing {collection_name}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Save report if requested
    if args.output and all_reports:
        for report in all_reports:
            save_report(report, args.output)

    # Summary
    total_duplicates = sum(r.memories_to_delete for r in all_reports)
    print(f"\n{'='*60}")
    print(f"TOTAL: Found {total_duplicates} duplicates in clusters")
    if dry_run:
        print("Mode: DRY RUN - No changes made")
    else:
        print("Mode: EXECUTED - Duplicates deleted")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
