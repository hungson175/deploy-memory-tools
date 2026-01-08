#!/usr/bin/env python3
"""
Generate proper 2-3 sentence summaries for metadata description field.
Uses LLM to create meaningful summaries that help understand memories during search review.
"""

import os
import time
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain.chat_models import init_chat_model

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://14.225.192.6:6309")

# Initialize LLM
llm = init_chat_model("grok-4-fast-non-reasoning", model_provider="xai")

DELAY = 0.2  # Rate limiting


def generate_summary(document: str, title: str) -> str:
    """
    Generate a 2-3 sentence summary for the metadata description field.
    This summary helps understand the memory quickly during search review.
    """
    prompt = f"""Generate a 2-3 sentence summary for this coding memory/pattern.
The summary should:
1. Explain the core problem or situation
2. State the key insight or solution
3. Mention when this pattern applies

Title: {title}

Full Content:
{document[:3000]}

Write ONLY the 2-3 sentence summary. No quotes, no prefix, no bullet points."""

    response = llm.invoke(prompt)
    return response.content.strip()


def main():
    client = QdrantClient(url=QDRANT_URL, check_compatibility=False)

    collections = client.get_collections().collections
    total_count = sum(client.get_collection(c.name).points_count for c in collections)

    print(f"Generating summaries for {total_count} points across {len(collections)} collections")
    print(f"Using: grok-4-fast-non-reasoning (xAI)\n")

    processed = 0
    errors = 0

    for coll in collections:
        collection_name = coll.name
        info = client.get_collection(collection_name)

        if info.points_count == 0:
            continue

        print(f"\n{collection_name} ({info.points_count} points)")
        offset = None

        while True:
            results, next_offset = client.scroll(
                collection_name=collection_name,
                limit=50,
                offset=offset,
                with_payload=True,
                with_vectors=True
            )

            for point in results:
                processed += 1
                doc = point.payload.get("document", "")
                title = point.payload.get("title", "")

                # Extract title from document if not in metadata
                if not title:
                    for line in doc.split('\n'):
                        if line.startswith("**Title:**"):
                            title = line.replace("**Title:**", "").strip()
                            break
                        elif line.startswith("# ") and not line.startswith("## "):
                            title = line.replace("# ", "").strip()
                            break

                try:
                    print(f"  [{processed}/{total_count}] {title[:50]}...", end=" ", flush=True)

                    # Generate summary
                    summary = generate_summary(doc, title)

                    # Update metadata
                    new_payload = point.payload.copy()
                    new_payload["description"] = summary
                    if title and "title" not in new_payload:
                        new_payload["title"] = title

                    client.upsert(
                        collection_name=collection_name,
                        points=[
                            models.PointStruct(
                                id=point.id,
                                vector=point.vector,
                                payload=new_payload
                            )
                        ]
                    )
                    print("✓")
                    time.sleep(DELAY)

                except Exception as e:
                    print(f"✗ {e}")
                    errors += 1

            if next_offset is None:
                break
            offset = next_offset

    print(f"\n{'='*60}")
    print(f"COMPLETE")
    print(f"{'='*60}")
    print(f"Processed: {processed}")
    print(f"Errors: {errors}")


if __name__ == "__main__":
    main()
