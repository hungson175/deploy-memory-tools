#!/usr/bin/env python3
"""
Migration script: OpenAI embeddings (1536d) → Voyage AI embeddings (1024d)

This script:
1. Exports all memories from all collections
2. Deletes old collections (1536 dimension)
3. Re-creates collections with new dimension (1024)
4. Re-imports all memories with Voyage embeddings
"""

import json
import os
import sys
import time
from typing import List, Dict, Any

import httpx
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Load environment
load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "voyage-3.5-lite")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))

# Role-based collections (from __main__.py)
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
}


def get_voyage_embedding(text: str) -> List[float]:
    """Get embedding from Voyage AI"""
    headers = {
        "Authorization": f"Bearer {VOYAGE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "input": text,
        "model": EMBEDDING_MODEL,
        "input_type": "document",
    }

    with httpx.Client() as client:
        response = client.post(
            "https://api.voyageai.com/v1/embeddings",
            headers=headers,
            json=data,
            timeout=60.0
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]


def export_all_memories(client: QdrantClient) -> Dict[str, List[Dict]]:
    """Export all memories from all collections"""
    print("\n=== EXPORTING ALL MEMORIES ===")

    collections = client.get_collections().collections
    all_memories = {}
    total_count = 0

    for coll in collections:
        collection_name = coll.name
        try:
            info = client.get_collection(collection_name)
            count = info.points_count

            if count == 0:
                print(f"  {collection_name}: 0 memories (skipping)")
                continue

            print(f"  {collection_name}: {count} memories")

            # Scroll through all points
            memories = []
            offset = None

            while True:
                result = client.scroll(
                    collection_name=collection_name,
                    limit=100,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )

                points, next_offset = result

                for point in points:
                    memories.append({
                        "id": str(point.id),
                        "payload": point.payload
                    })

                if next_offset is None:
                    break
                offset = next_offset

            all_memories[collection_name] = memories
            total_count += len(memories)

        except Exception as e:
            print(f"  {collection_name}: Error - {e}")

    print(f"\nTotal exported: {total_count} memories from {len(all_memories)} collections")
    return all_memories


def delete_collections(client: QdrantClient, collection_names: List[str]):
    """Delete specified collections"""
    print("\n=== DELETING OLD COLLECTIONS ===")

    for name in collection_names:
        try:
            client.delete_collection(name)
            print(f"  Deleted: {name}")
        except Exception as e:
            print(f"  {name}: Error - {e}")


def create_collections(client: QdrantClient, collection_names: List[str]):
    """Create collections with new dimension"""
    print(f"\n=== CREATING COLLECTIONS (dimension={EMBEDDING_DIMENSION}) ===")

    for name in collection_names:
        try:
            client.create_collection(
                collection_name=name,
                vectors_config=models.VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=models.Distance.COSINE
                )
            )
            print(f"  Created: {name}")
        except Exception as e:
            print(f"  {name}: Error - {e}")


def reimport_memories(client: QdrantClient, all_memories: Dict[str, List[Dict]]):
    """Re-import memories with new Voyage embeddings"""
    print("\n=== RE-IMPORTING WITH VOYAGE EMBEDDINGS ===")

    total_imported = 0
    total_failed = 0

    for collection_name, memories in all_memories.items():
        if not memories:
            continue

        print(f"\n  {collection_name}: {len(memories)} memories")

        for i, memory in enumerate(memories):
            try:
                payload = memory["payload"]
                document = payload.get("document", "")

                if not document:
                    print(f"    [{i+1}/{len(memories)}] Skipping (no document)")
                    continue

                # Get new Voyage embedding
                embedding = get_voyage_embedding(document)

                # Upsert with new embedding
                client.upsert(
                    collection_name=collection_name,
                    points=[
                        models.PointStruct(
                            id=memory["id"],
                            vector=embedding,
                            payload=payload
                        )
                    ]
                )

                total_imported += 1
                print(f"    [{i+1}/{len(memories)}] OK: {payload.get('title', 'Untitled')[:50]}")

                # Rate limiting (Voyage has rate limits)
                time.sleep(0.1)

            except Exception as e:
                total_failed += 1
                print(f"    [{i+1}/{len(memories)}] FAILED: {e}")

    print(f"\n=== MIGRATION COMPLETE ===")
    print(f"  Imported: {total_imported}")
    print(f"  Failed: {total_failed}")


def main():
    print("=" * 60)
    print("MIGRATION: OpenAI → Voyage AI Embeddings")
    print("=" * 60)
    print(f"Qdrant URL: {QDRANT_URL}")
    print(f"Voyage Model: {EMBEDDING_MODEL}")
    print(f"New Dimension: {EMBEDDING_DIMENSION}")
    print("=" * 60)

    if not VOYAGE_API_KEY:
        print("ERROR: VOYAGE_API_KEY not set!")
        sys.exit(1)

    # Test Voyage API
    print("\nTesting Voyage API...")
    try:
        test_embedding = get_voyage_embedding("test")
        print(f"  OK! Got embedding with {len(test_embedding)} dimensions")
    except Exception as e:
        print(f"  FAILED: {e}")
        sys.exit(1)

    # Connect to Qdrant
    print(f"\nConnecting to Qdrant at {QDRANT_URL}...")
    client = QdrantClient(url=QDRANT_URL, timeout=60)

    # Step 1: Export all memories
    all_memories = export_all_memories(client)

    if not all_memories:
        print("\nNo memories to migrate!")
        sys.exit(0)

    # Save backup to file
    backup_file = "migration_backup.json"
    with open(backup_file, "w") as f:
        json.dump(all_memories, f, indent=2)
    print(f"\nBackup saved to: {backup_file}")

    # Step 2: Delete old collections
    delete_collections(client, list(all_memories.keys()))

    # Step 3: Create new collections
    create_collections(client, list(all_memories.keys()))

    # Step 4: Re-import with Voyage embeddings
    reimport_memories(client, all_memories)

    print("\nDone! Your memories are now using Voyage AI embeddings.")


if __name__ == "__main__":
    main()
