#!/usr/bin/env python3
"""
Find all memories in Qdrant where descriptions can't be extracted
by the server's _extract_preview() function (requires **Description:** format).
"""

import os
import json
import re
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")


def extract_description_server_style(document: str) -> str:
    """
    Extract description EXACTLY as the server does it.
    Only finds **Description:** format.
    """
    for line in document.split('\n'):
        if line.startswith("**Description:**"):
            return line.replace("**Description:**", "").strip()
    return ""


def extract_description_any_format(document: str) -> str:
    """
    Extract description from any known format:
    - **Description:** format
    - ## Description format
    - Description: format (plain)
    """
    lines = document.split('\n')

    # Try **Description:** format
    for line in lines:
        if line.startswith("**Description:**"):
            return line.replace("**Description:**", "").strip()

    # Try ## Description format
    for i, line in enumerate(lines):
        if line.startswith("## Description"):
            for j in range(i + 1, len(lines)):
                if lines[j].strip() and not lines[j].startswith("#"):
                    return lines[j].strip()
            break

    # Try Description: format (plain)
    for line in lines:
        if line.startswith("Description:"):
            return line.replace("Description:", "").strip()

    return ""


def main():
    client = QdrantClient(url=QDRANT_URL, check_compatibility=False)

    collections = client.get_collections().collections
    print(f"Found {len(collections)} collections\n")

    # Track different categories
    needs_reformat = []  # Has description but wrong format
    truly_missing = []   # No description in any format

    for coll in collections:
        collection_name = coll.name
        info = client.get_collection(collection_name)
        point_count = info.points_count

        if point_count == 0:
            print(f"  {collection_name}: 0 points (empty)")
            continue

        reformat_count = 0
        missing_count = 0
        offset = None

        while True:
            results, next_offset = client.scroll(
                collection_name=collection_name,
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )

            for point in results:
                doc = point.payload.get("document", "")
                server_desc = extract_description_server_style(doc)
                any_desc = extract_description_any_format(doc)

                # Extract title for reference
                title = ""
                for line in doc.split('\n'):
                    if line.startswith("**Title:**"):
                        title = line.replace("**Title:**", "").strip()
                        break
                    elif line.startswith("# ") and not line.startswith("## "):
                        title = line.replace("# ", "").strip()
                        break
                    elif line.startswith("Title:"):
                        title = line.replace("Title:", "").strip()
                        break

                if not server_desc:
                    item = {
                        "id": str(point.id),
                        "collection": collection_name,
                        "title": title or "(no title)",
                        "existing_desc": any_desc[:100] + "..." if len(any_desc) > 100 else any_desc,
                        "doc_preview": doc[:300]
                    }

                    if any_desc:
                        needs_reformat.append(item)
                        reformat_count += 1
                    else:
                        truly_missing.append(item)
                        missing_count += 1

            if next_offset is None:
                break
            offset = next_offset

        total_issues = reformat_count + missing_count
        if total_issues > 0:
            print(f"  {collection_name}: {total_issues}/{point_count} need fixing "
                  f"({reformat_count} reformat, {missing_count} missing)")
        else:
            print(f"  {collection_name}: {point_count} points - all OK ✓")

    print(f"\n{'='*60}")
    print(f"SUMMARY")
    print(f"{'='*60}")
    print(f"Needs reformat (has desc, wrong format): {len(needs_reformat)}")
    print(f"Truly missing (no desc anywhere): {len(truly_missing)}")
    print(f"{'='*60}\n")

    if needs_reformat:
        print("\n--- NEEDS REFORMAT (first 5) ---")
        for item in needs_reformat[:5]:
            print(f"\n[{item['collection']}] {item['title']}")
            print(f"  ID: {item['id']}")
            print(f"  Has: {item['existing_desc']}")

    if truly_missing:
        print("\n--- TRULY MISSING (first 5) ---")
        for item in truly_missing[:5]:
            print(f"\n[{item['collection']}] {item['title']}")
            print(f"  ID: {item['id']}")
            print(f"  Preview: {item['doc_preview'][:150]}...")

    # Save both lists
    output = {
        "needs_reformat": needs_reformat,
        "truly_missing": truly_missing
    }
    output_file = "/home/hungson175/dev/deploy-memory-tools/scripts/description_issues.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved to: {output_file}")


if __name__ == "__main__":
    main()
