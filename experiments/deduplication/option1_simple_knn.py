#!/usr/bin/env python3
"""
Option 1: Simple k-NN Deduplication (MVP)

Complexity: Low
Best for: Initial cleanup, regular maintenance

Approach:
1. For each memory, find top-5 similar memories (k-NN)
2. If similarity > threshold, mark as duplicate pair
3. Build duplicate groups using Union-Find
4. Keep most complete/recent in each group, delete others

Usage:
    # Dry run (list duplicates without deleting)
    python option1_simple_knn.py --collection scrum-master-patterns --dry-run

    # Execute (delete duplicates)
    python option1_simple_knn.py --collection scrum-master-patterns --execute

    # All collections
    python option1_simple_knn.py --all --dry-run
"""

import argparse
import sys
from datetime import datetime
from typing import Dict, List

from utils import (
    DeduplicationReport,
    DuplicateGroup,
    MemoryPoint,
    UnionFind,
    batch_delete_points,
    find_similar_points,
    get_qdrant_client,
    list_all_collections,
    logger,
    save_report,
    scroll_all_points,
    select_canonical,
    ROLE_COLLECTIONS,
)


def find_duplicates_knn(
    collection_name: str,
    threshold: float = 0.95,
    k: int = 5,
) -> DeduplicationReport:
    """
    Find duplicates using k-NN approach.

    Args:
        collection_name: Name of the collection to scan
        threshold: Similarity threshold (0.95 = near-exact duplicates)
        k: Number of neighbors to check

    Returns:
        DeduplicationReport with duplicate groups found
    """
    client = get_qdrant_client()

    # Step 1: Scroll through all points
    logger.info(f"Scanning collection: {collection_name}")
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

    # Build point map for quick lookup
    point_map: Dict[str, MemoryPoint] = {p.id: p for p in all_points}

    # Step 2: Find similar pairs using k-NN
    logger.info(f"Finding similar pairs (threshold={threshold}, k={k})")
    uf = UnionFind()
    similarity_map: Dict[str, Dict[str, float]] = {}  # id -> {other_id -> score}
    processed = set()

    for point in all_points:
        similar = find_similar_points(
            client, collection_name, point,
            threshold=threshold, limit=k, exclude_ids=processed
        )

        for other_id, score in similar:
            # Union the pair
            uf.union(point.id, other_id)

            # Record similarity
            if point.id not in similarity_map:
                similarity_map[point.id] = {}
            if other_id not in similarity_map:
                similarity_map[other_id] = {}
            similarity_map[point.id][other_id] = score
            similarity_map[other_id][point.id] = score

        processed.add(point.id)

    # Step 3: Build duplicate groups
    raw_groups = uf.get_groups()
    duplicate_groups: List[DuplicateGroup] = []

    for root, member_ids in raw_groups.items():
        if len(member_ids) <= 1:
            continue  # Not a duplicate group

        members = [point_map[mid] for mid in member_ids if mid in point_map]
        if len(members) <= 1:
            continue

        # Select canonical version
        canonical = select_canonical(members, point_map)

        # Build similarity scores for the group
        scores = {}
        for member in members:
            if member.id != canonical.id:
                # Get similarity with canonical
                if member.id in similarity_map.get(canonical.id, {}):
                    scores[member.id] = similarity_map[canonical.id][member.id]
                elif canonical.id in similarity_map.get(member.id, {}):
                    scores[member.id] = similarity_map[member.id][canonical.id]
                else:
                    scores[member.id] = threshold  # Default to threshold

        duplicate_ids = [m.id for m in members if m.id != canonical.id]

        group = DuplicateGroup(
            canonical_id=canonical.id,
            duplicate_ids=duplicate_ids,
            similarity_scores=scores,
            reason=f"k-NN similarity >= {threshold}",
        )
        duplicate_groups.append(group)

        logger.info(
            f"Group: Keep '{canonical.title[:50]}...' "
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
        description="Simple k-NN Deduplication for Qdrant Memory"
    )
    parser.add_argument(
        "--collection", "-c",
        help="Collection name to scan (e.g., 'scrum-master-patterns')"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Scan all role collections"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=0.95,
        help="Similarity threshold (default: 0.95 for near-exact)"
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of neighbors to check (default: 5)"
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

    if not args.collection and not args.all:
        parser.error("Either --collection or --all is required")

    if args.execute and args.dry_run:
        parser.error("Cannot use both --dry-run and --execute")

    dry_run = not args.execute

    # Determine collections to scan
    if args.all:
        client = get_qdrant_client()
        collections = list_all_collections(client)
        # Filter to only role collections that exist
        collections = [c for c in ROLE_COLLECTIONS.values() if c in collections]
    else:
        collections = [args.collection]

    all_reports = []

    for collection_name in collections:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {collection_name}")
        logger.info(f"{'='*60}")

        try:
            report = find_duplicates_knn(
                collection_name,
                threshold=args.threshold,
                k=args.k,
            )
            report.dry_run = dry_run

            print(f"\n{report.summary}\n")

            if report.duplicate_groups:
                print("Duplicate groups found:")
                for i, group in enumerate(report.duplicate_groups, 1):
                    print(f"\n  Group {i}:")
                    print(f"    Keep: {group.canonical_id}")
                    for dup_id, score in group.similarity_scores.items():
                        print(f"    Delete: {dup_id} (similarity: {score:.3f})")

            if not dry_run and report.duplicate_groups:
                deleted = execute_deduplication(report)
                print(f"\nDeleted {deleted} memories")

            all_reports.append(report)

        except Exception as e:
            logger.error(f"Error processing {collection_name}: {e}")
            continue

    # Save combined report if requested
    if args.output and all_reports:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for i, report in enumerate(all_reports):
            output_path = args.output.replace(".json", f"_{report.collection}_{timestamp}.json")
            save_report(report, output_path)

    # Summary
    total_duplicates = sum(r.memories_to_delete for r in all_reports)
    print(f"\n{'='*60}")
    print(f"TOTAL: Found {total_duplicates} duplicates across {len(all_reports)} collections")
    if dry_run:
        print("Mode: DRY RUN - No changes made")
        print("Run with --execute to delete duplicates")
    else:
        print("Mode: EXECUTED - Duplicates deleted")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
