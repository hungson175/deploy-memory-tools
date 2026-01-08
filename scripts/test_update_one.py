#!/usr/bin/env python3
"""
Test the update logic on ONE memory to verify it works correctly.
"""

import os
import re
import json
from typing import Tuple
from dotenv import load_dotenv
from qdrant_client import QdrantClient
import httpx

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def generate_description(content: str, title: str) -> str:
    """Use OpenAI to generate a one-sentence description from content."""
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""Generate a ONE SENTENCE description (max 20 words) for this coding memory/pattern.
The description should capture the key insight or lesson.

Title: {title}

Content:
{content[:2000]}

Write ONLY the description, nothing else. No quotes, no "Description:" prefix."""

    data = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "temperature": 0.3
    }

    with httpx.Client() as client:
        response = client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()


def parse_document(doc: str) -> Tuple[str, str, str, str]:
    """Parse document to extract title, description, content, tags."""
    title = ""
    description = ""
    content = ""
    tags = ""

    lines = doc.split('\n')

    # Try **Title:** format first
    for i, line in enumerate(lines):
        if line.startswith("**Title:**"):
            title = line.replace("**Title:**", "").strip()
        elif line.startswith("**Description:**"):
            description = line.replace("**Description:**", "").strip()
        elif line.startswith("**Tags:**"):
            tags = line.replace("**Tags:**", "").strip()

    # Try # Title format
    if not title:
        for i, line in enumerate(lines):
            if line.startswith("# ") and not line.startswith("## "):
                title = line.replace("# ", "").strip()
                break

    # Try ## Description format
    if not description:
        for i, line in enumerate(lines):
            if line.startswith("## Description"):
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith("#"):
                        description = lines[j].strip()
                        break
                break

    # Try Title: format (plain)
    if not title:
        for line in lines:
            if line.startswith("Title:"):
                title = line.replace("Title:", "").strip()
                break

    # Try Description: format (plain)
    if not description:
        for line in lines:
            if line.startswith("Description:"):
                description = line.replace("Description:", "").strip()
                break

    # Extract tags
    if not tags:
        tag_pattern = r'#[\w-]+'
        found_tags = re.findall(tag_pattern, doc)
        if found_tags:
            tags = ' '.join(found_tags[-10:])

    content = doc
    return title, description, content, tags


def main():
    # Load first item from missing descriptions
    with open("/home/hungson175/dev/deploy-memory-tools/scripts/missing_descriptions.json", 'r') as f:
        missing = json.load(f)

    if not missing:
        print("No missing descriptions!")
        return

    # Test with first item
    item = missing[0]
    doc_id = item['id']
    collection = item['collection']

    print(f"Testing with: {doc_id}")
    print(f"Collection: {collection}")
    print(f"Title from scan: {item.get('title', 'N/A')}")
    print()

    client = QdrantClient(url=QDRANT_URL, check_compatibility=False)

    # Get full document
    results = client.retrieve(
        collection_name=collection,
        ids=[doc_id],
        with_payload=True,
        with_vectors=False
    )

    if not results:
        print("Not found!")
        return

    point = results[0]
    doc = point.payload.get("document", "")

    print("="*60)
    print("ORIGINAL DOCUMENT:")
    print("="*60)
    print(doc[:1000])
    print("...")
    print()

    # Parse
    title, existing_desc, content, tags = parse_document(doc)

    print("="*60)
    print("PARSED FIELDS:")
    print("="*60)
    print(f"Title: {title}")
    print(f"Existing Description: {existing_desc or '(none)'}")
    print(f"Tags: {tags}")
    print()

    if not existing_desc:
        print("="*60)
        print("GENERATING DESCRIPTION...")
        print("="*60)
        description = generate_description(content, title or "Untitled Memory")
        print(f"Generated: {description}")
    else:
        print("Already has description, skipping generation")


if __name__ == "__main__":
    main()
