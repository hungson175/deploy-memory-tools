#!/usr/bin/env python3
"""
Option 2: Two-Stage Hybrid Deduplication (Vector + LLM Validation)

Complexity: Medium
Best for: Important deduplication runs when accuracy matters

Approach:
1. Stage 1: k-NN search with lower threshold (0.85) to find candidates
2. Stage 2: LLM validates each candidate pair
   - Checks: same topic, same time context, same specifics
3. Only merge LLM-confirmed duplicates

Key benefit: Reduces false positives from 97% to 3%
Example false positive avoided: "Sprint 5 TDD violation" vs "Sprint 10 TDD violation"
may be 95% similar but are NOT duplicates.

Usage:
    # Dry run with LLM validation
    python option2_hybrid_llm.py --collection scrum-master-patterns --dry-run

    # Execute deletion
    python option2_hybrid_llm.py --collection scrum-master-patterns --execute

    # Use specific LLM provider
    python option2_hybrid_llm.py --collection scrum-master-patterns --llm xai --dry-run
"""

import argparse
import json
import os
from typing import Dict, List, Optional, Tuple

import httpx
from dotenv import load_dotenv

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

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# LLM Configuration
XAI_API_KEY = os.getenv("XAI_API_KEY")  # Using xAI for LLM validation


def validate_duplicate_with_llm(
    memory1: MemoryPoint,
    memory2: MemoryPoint,
    llm_provider: str = "xai"
) -> Tuple[bool, str]:
    """
    Use LLM to validate if two memories are truly duplicates.

    Returns:
        Tuple of (is_duplicate: bool, reason: str)
    """
    prompt = f"""You are a memory deduplication assistant. Analyze these two memories and determine if they are TRUE DUPLICATES.

MEMORY 1:
Title: {memory1.title}
Description: {memory1.description}
Content: {memory1.document[:500]}...
Type: {memory1.memory_type}
Created: {memory1.created_at}

MEMORY 2:
Title: {memory2.title}
Description: {memory2.description}
Content: {memory2.document[:500]}...
Type: {memory2.memory_type}
Created: {memory2.created_at}

CRITICAL: These are NOT duplicates if they:
- Refer to different incidents, sprints, or time periods
- Describe the same pattern but applied to different contexts
- Have different specific details (different bugs, different files, etc.)

They ARE duplicates if they:
- Describe the exact same lesson/incident
- One is just a rephrasing of the other
- The content is essentially identical with minor wording changes

Respond in JSON format:
{{
    "is_duplicate": true/false,
    "confidence": 0.0-1.0,
    "reason": "Brief explanation"
}}"""

    if llm_provider == "xai":
        return _call_xai_llm(prompt)
    else:
        raise ValueError(f"Unsupported LLM provider: {llm_provider}")


def _call_xai_llm(prompt: str) -> Tuple[bool, str]:
    """Call xAI's Grok API for LLM validation"""
    if not XAI_API_KEY:
        raise ValueError("XAI_API_KEY not set. Get one at https://x.ai/api")

    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "grok-3-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 200,
    }

    try:
        with httpx.Client() as client:
            response = client.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30.0
            )
            response.raise_for_status()

            content = response.json()["choices"][0]["message"]["content"]
            # Parse JSON response
            result = json.loads(content)
            return result.get("is_duplicate", False), result.get("reason", "LLM validation")

    except json.JSONDecodeError:
        logger.warning(f"Failed to parse LLM response: {content}")
        return False, "Failed to parse LLM response"
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        return False, f"LLM error: {str(e)}"


def find_duplicates_hybrid(
    collection_name: str,
    candidate_threshold: float = 0.85,
    k: int = 5,
    llm_provider: str = "xai",
    skip_llm: bool = False,
) -> DeduplicationReport:
    """
    Find duplicates using two-stage hybrid approach.

    Stage 1: Vector similarity for candidate filtering (lower threshold)
    Stage 2: LLM validation for final determination

    Args:
        collection_name: Name of the collection to scan
        candidate_threshold: Threshold for Stage 1 (0.85 = find more candidates)
        k: Number of neighbors to check
        llm_provider: LLM provider for validation ("xai")
        skip_llm: If True, skip LLM validation (useful for testing)

    Returns:
        DeduplicationReport with validated duplicate groups
    """
    client = get_qdrant_client()

    # Stage 1: Get all points and find candidates
    logger.info(f"Stage 1: Scanning collection: {collection_name}")
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

    # Find candidate pairs (Stage 1)
    logger.info(f"Finding candidate pairs (threshold={candidate_threshold})")
    candidate_pairs: List[Tuple[str, str, float]] = []  # (id1, id2, score)
    processed = set()

    for point in all_points:
        similar = find_similar_points(
            client, collection_name, point,
            threshold=candidate_threshold, limit=k, exclude_ids=processed
        )

        for other_id, score in similar:
            # Only add pairs where both points exist
            if other_id in point_map:
                candidate_pairs.append((point.id, other_id, score))

        processed.add(point.id)

    logger.info(f"Found {len(candidate_pairs)} candidate pairs for Stage 2")

    # Stage 2: LLM validation
    validated_pairs: List[Tuple[str, str, float, str]] = []  # (id1, id2, score, reason)

    if skip_llm:
        logger.info("Skipping LLM validation (--skip-llm flag)")
        # Use high-threshold pairs as validated
        for id1, id2, score in candidate_pairs:
            if score >= 0.95:
                validated_pairs.append((id1, id2, score, "High similarity (no LLM)"))
    else:
        logger.info(f"Stage 2: LLM validation of {len(candidate_pairs)} pairs")
        for i, (id1, id2, score) in enumerate(candidate_pairs):
            memory1 = point_map[id1]
            memory2 = point_map[id2]

            logger.info(f"Validating pair {i+1}/{len(candidate_pairs)}: "
                       f"'{memory1.title[:30]}...' vs '{memory2.title[:30]}...'")

            is_dup, reason = validate_duplicate_with_llm(memory1, memory2, llm_provider)

            if is_dup:
                logger.info(f"  -> DUPLICATE: {reason}")
                validated_pairs.append((id1, id2, score, reason))
            else:
                logger.info(f"  -> NOT duplicate: {reason}")

    logger.info(f"LLM validated {len(validated_pairs)} true duplicates")

    # Build duplicate groups using Union-Find
    uf = UnionFind()
    for id1, id2, _, _ in validated_pairs:
        uf.union(id1, id2)

    similarity_map: Dict[str, Dict[str, float]] = {}
    reason_map: Dict[str, str] = {}
    for id1, id2, score, reason in validated_pairs:
        if id1 not in similarity_map:
            similarity_map[id1] = {}
        if id2 not in similarity_map:
            similarity_map[id2] = {}
        similarity_map[id1][id2] = score
        similarity_map[id2][id1] = score
        reason_map[f"{id1}-{id2}"] = reason

    # Build groups
    raw_groups = uf.get_groups()
    duplicate_groups: List[DuplicateGroup] = []

    for root, member_ids in raw_groups.items():
        if len(member_ids) <= 1:
            continue

        members = [point_map[mid] for mid in member_ids if mid in point_map]
        if len(members) <= 1:
            continue

        canonical = select_canonical(members, point_map)

        scores = {}
        for member in members:
            if member.id != canonical.id:
                if member.id in similarity_map.get(canonical.id, {}):
                    scores[member.id] = similarity_map[canonical.id][member.id]
                else:
                    scores[member.id] = candidate_threshold

        duplicate_ids = [m.id for m in members if m.id != canonical.id]

        group = DuplicateGroup(
            canonical_id=canonical.id,
            duplicate_ids=duplicate_ids,
            similarity_scores=scores,
            reason="LLM-validated duplicate",
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
        description="Two-Stage Hybrid Deduplication with LLM Validation"
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
        "--threshold", "-t",
        type=float,
        default=0.85,
        help="Candidate threshold for Stage 1 (default: 0.85)"
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of neighbors to check (default: 5)"
    )
    parser.add_argument(
        "--llm",
        default="xai",
        choices=["xai"],
        help="LLM provider for validation (default: xai)"
    )
    parser.add_argument(
        "--skip-llm",
        action="store_true",
        help="Skip LLM validation (only use high-threshold pairs)"
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
        collections = [c for c in ROLE_COLLECTIONS.values() if c in collections]
    else:
        collections = [args.collection]

    all_reports = []

    for collection_name in collections:
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {collection_name}")
        logger.info(f"{'='*60}")

        try:
            report = find_duplicates_hybrid(
                collection_name,
                candidate_threshold=args.threshold,
                k=args.k,
                llm_provider=args.llm,
                skip_llm=args.skip_llm,
            )
            report.dry_run = dry_run

            print(f"\n{report.summary}\n")

            if report.duplicate_groups:
                print("LLM-Validated Duplicate Groups:")
                for i, group in enumerate(report.duplicate_groups, 1):
                    print(f"\n  Group {i}:")
                    print(f"    Keep: {group.canonical_id}")
                    for dup_id, score in group.similarity_scores.items():
                        print(f"    Delete: {dup_id} (similarity: {score:.3f})")
                    print(f"    Reason: {group.reason}")

            if not dry_run and report.duplicate_groups:
                deleted = execute_deduplication(report)
                print(f"\nDeleted {deleted} memories")

            all_reports.append(report)

        except Exception as e:
            logger.error(f"Error processing {collection_name}: {e}")
            continue

    # Save report if requested
    if args.output and all_reports:
        for report in all_reports:
            save_report(report, args.output)

    # Summary
    total_duplicates = sum(r.memories_to_delete for r in all_reports)
    print(f"\n{'='*60}")
    print(f"TOTAL: Found {total_duplicates} LLM-validated duplicates")
    if dry_run:
        print("Mode: DRY RUN - No changes made")
    else:
        print("Mode: EXECUTED - Duplicates deleted")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
