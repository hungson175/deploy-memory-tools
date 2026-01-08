#!/usr/bin/env python3
"""
Fix points missing 'description' field in metadata.
Extracts description from document content and adds to metadata.
"""

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://14.225.192.6:6309")


def extract_description(document: str) -> str:
    """Extract description from **Description:** line in document."""
    for line in document.split('\n'):
        if line.startswith("**Description:**"):
            return line.replace("**Description:**", "").strip()
    return ""


def main():
    client = QdrantClient(url=QDRANT_URL, check_compatibility=False)

    collections = client.get_collections().collections
    print(f"Checking {len(collections)} collections for missing metadata description...\n")

    total_fixed = 0
    total_missing = 0

    for coll in collections:
        collection_name = coll.name
        info = client.get_collection(collection_name)

        if info.points_count == 0:
            continue

        missing_in_collection = []
        offset = None

        while True:
            results, next_offset = client.scroll(
                collection_name=collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=True  # Need vectors to upsert
            )

            for point in results:
                # Check if metadata has description
                if "description" not in point.payload or not point.payload.get("description"):
                    doc = point.payload.get("document", "")
                    desc = extract_description(doc)

                    if desc:
                        missing_in_collection.append({
                            "id": point.id,
                            "vector": point.vector,
                            "payload": point.payload,
                            "description": desc
                        })

            if next_offset is None:
                break
            offset = next_offset

        if missing_in_collection:
            print(f"{collection_name}: {len(missing_in_collection)} points missing metadata description")
            total_missing += len(missing_in_collection)

            # Fix them
            for item in missing_in_collection:
                new_payload = item["payload"].copy()
                new_payload["description"] = item["description"]

                client.upsert(
                    collection_name=collection_name,
                    points=[
                        models.PointStruct(
                            id=item["id"],
                            vector=item["vector"],
                            payload=new_payload
                        )
                    ]
                )
                total_fixed += 1

            print(f"  → Fixed {len(missing_in_collection)} points")
        else:
            print(f"{collection_name}: all {info.points_count} points OK ✓")

    print(f"\n{'='*60}")
    print(f"COMPLETE")
    print(f"{'='*60}")
    print(f"Total missing: {total_missing}")
    print(f"Total fixed: {total_fixed}")


if __name__ == "__main__":
    main()
