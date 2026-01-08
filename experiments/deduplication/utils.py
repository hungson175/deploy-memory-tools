#!/usr/bin/env python3
"""
Shared utilities for memory deduplication experiments.
Provides connection, embedding, and logging helpers.
"""

import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Load environment from project root
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "voyage").lower()
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "voyage-3.5-lite")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))

# Role collections mapping
ROLE_COLLECTIONS = {
    "universal": "universal-patterns",
    "backend": "backend-patterns",
    "frontend": "frontend-patterns",
    "quant": "quant-patterns",
    "devops": "devops-patterns",
    "ml": "ml-patterns",
    "security": "security-patterns",
    "mobile": "mobile-patterns",
    "ai": "ai-patterns",
    "scrum-master": "scrum-master-patterns",
}


@dataclass
class MemoryPoint:
    """Represents a memory point from Qdrant"""
    id: str
    vector: List[float]
    title: str
    description: str
    document: str
    role: str
    memory_type: str
    tags: List[str]
    created_at: str
    payload: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_qdrant_point(cls, point: models.Record) -> "MemoryPoint":
        """Create from Qdrant point"""
        payload = point.payload or {}
        return cls(
            id=str(point.id),
            vector=list(point.vector) if point.vector else [],
            title=payload.get("title", "Untitled"),
            description=payload.get("description", ""),
            document=payload.get("document", ""),
            role=payload.get("role", "unknown"),
            memory_type=payload.get("memory_type", "unknown"),
            tags=payload.get("tags", []),
            created_at=payload.get("created_at", ""),
            payload=payload,
        )


@dataclass
class DuplicateGroup:
    """Represents a group of duplicate memories"""
    canonical_id: str  # The one to keep
    duplicate_ids: List[str]  # The ones to delete
    similarity_scores: Dict[str, float]  # id -> similarity with canonical
    reason: str = ""  # Why these are duplicates


@dataclass
class DeduplicationReport:
    """Report of deduplication results"""
    collection: str
    total_memories: int
    duplicate_groups: List[DuplicateGroup]
    memories_to_delete: int
    dry_run: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def summary(self) -> str:
        return (
            f"Collection: {self.collection}\n"
            f"Total memories: {self.total_memories}\n"
            f"Duplicate groups found: {len(self.duplicate_groups)}\n"
            f"Memories to delete: {self.memories_to_delete}\n"
            f"Mode: {'DRY RUN' if self.dry_run else 'EXECUTE'}"
        )


def get_qdrant_client() -> QdrantClient:
    """Get Qdrant client connection"""
    logger.info(f"Connecting to Qdrant at {QDRANT_URL}")
    return QdrantClient(url=QDRANT_URL, check_compatibility=False)


def get_embedding(text: str) -> List[float]:
    """Get embedding using Voyage AI"""
    if not VOYAGE_API_KEY:
        raise ValueError("VOYAGE_API_KEY not set")

    headers = {
        "Authorization": f"Bearer {VOYAGE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "input": text,
        "model": EMBEDDING_MODEL,
        "input_type": "document",
    }

    if EMBEDDING_DIMENSION and EMBEDDING_DIMENSION != 1024:
        data["output_dimension"] = EMBEDDING_DIMENSION

    with httpx.Client() as client:
        response = client.post(
            "https://api.voyageai.com/v1/embeddings",
            headers=headers,
            json=data,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]


def scroll_all_points(
    client: QdrantClient,
    collection_name: str,
    with_vectors: bool = True,
    batch_size: int = 100
) -> List[MemoryPoint]:
    """Scroll through all points in a collection"""
    all_points = []
    offset = None

    while True:
        points, offset = client.scroll(
            collection_name=collection_name,
            limit=batch_size,
            with_vectors=with_vectors,
            with_payload=True,
            offset=offset,
        )

        if not points:
            break

        for point in points:
            all_points.append(MemoryPoint.from_qdrant_point(point))

        logger.info(f"Scrolled {len(all_points)} points from {collection_name}")

        if offset is None:
            break

    return all_points


def find_similar_points(
    client: QdrantClient,
    collection_name: str,
    point: MemoryPoint,
    threshold: float = 0.85,
    limit: int = 5,
    exclude_ids: Optional[Set[str]] = None
) -> List[Tuple[str, float]]:
    """Find points similar to a given point above threshold"""
    exclude_ids = exclude_ids or set()
    exclude_ids.add(point.id)

    results = client.query_points(
        collection_name=collection_name,
        query=point.vector,
        limit=limit + len(exclude_ids),
        with_payload=False,
        score_threshold=threshold,
    ).points

    similar = []
    for result in results:
        if str(result.id) not in exclude_ids:
            similar.append((str(result.id), result.score))

    return similar[:limit]


class UnionFind:
    """Union-Find data structure for grouping duplicates"""

    def __init__(self):
        self.parent: Dict[str, str] = {}
        self.rank: Dict[str, int] = {}

    def find(self, x: str) -> str:
        if x not in self.parent:
            self.parent[x] = x
            self.rank[x] = 0
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: str, y: str) -> None:
        px, py = self.find(x), self.find(y)
        if px == py:
            return
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1

    def get_groups(self) -> Dict[str, List[str]]:
        """Get all groups"""
        groups: Dict[str, List[str]] = {}
        for item in self.parent:
            root = self.find(item)
            if root not in groups:
                groups[root] = []
            groups[root].append(item)
        return groups


def select_canonical(
    points: List[MemoryPoint],
    point_map: Dict[str, MemoryPoint]
) -> MemoryPoint:
    """Select the canonical (best) version to keep from a group of duplicates.

    Priority:
    1. Most complete content (longest document)
    2. Has proper description
    3. Most recent
    """
    if len(points) == 1:
        return points[0]

    def score_point(p: MemoryPoint) -> Tuple[int, int, str]:
        doc_len = len(p.document)
        has_desc = 1 if p.description and len(p.description) > 10 else 0
        created = p.created_at or "0000"
        return (doc_len, has_desc, created)

    return max(points, key=score_point)


def batch_delete_points(
    client: QdrantClient,
    collection_name: str,
    point_ids: List[str],
    batch_size: int = 100
) -> int:
    """Delete points in batches"""
    deleted = 0
    for i in range(0, len(point_ids), batch_size):
        batch = point_ids[i:i + batch_size]
        client.delete(
            collection_name=collection_name,
            points_selector=models.PointIdsList(points=batch)
        )
        deleted += len(batch)
        logger.info(f"Deleted {deleted}/{len(point_ids)} points")
    return deleted


def save_report(report: DeduplicationReport, output_path: str) -> None:
    """Save deduplication report to JSON file"""
    data = {
        "collection": report.collection,
        "total_memories": report.total_memories,
        "duplicate_groups": [
            {
                "canonical_id": g.canonical_id,
                "duplicate_ids": g.duplicate_ids,
                "similarity_scores": g.similarity_scores,
                "reason": g.reason,
            }
            for g in report.duplicate_groups
        ],
        "memories_to_delete": report.memories_to_delete,
        "dry_run": report.dry_run,
        "timestamp": report.timestamp,
    }

    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)

    logger.info(f"Report saved to {output_path}")


def list_all_collections(client: QdrantClient) -> List[str]:
    """List all collection names"""
    collections = client.get_collections().collections
    return [c.name for c in collections]
