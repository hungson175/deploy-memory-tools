#!/usr/bin/env python3
"""
Fix memories with description issues:
1. Reformat documents that have descriptions in wrong format
2. Generate descriptions for those truly missing them

Uses LangChain with xAI grok-4-fast-non-reasoning for description generation.
Uses upsert with regenerated embeddings.
"""

import os
import re
import json
import time
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
import httpx
from langchain.chat_models import init_chat_model

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"

DELAY_BETWEEN_UPDATES = 0.3  # seconds

# Initialize LLM for description generation
llm = init_chat_model("grok-4-fast-non-reasoning", model_provider="xai")


def get_embedding(text: str) -> list[float]:
    """Get embedding from OpenAI."""
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"input": text, "model": EMBEDDING_MODEL}
    with httpx.Client() as client:
        response = client.post(
            "https://api.openai.com/v1/embeddings",
            headers=headers, json=data, timeout=30.0
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]


def generate_description(document: str, title: str) -> str:
    """
    Use xAI grok-4-fast-non-reasoning to generate a one-sentence description.

    Args:
        document: The full memory document content
        title: The extracted title of the memory

    Returns:
        A concise one-sentence description (max 25 words)
    """
    prompt = f"""Generate a ONE SENTENCE description (max 25 words) for this coding memory/pattern.
The description should capture the key insight or lesson learned.

Title: {title}

Document:
{document[:2500]}

Write ONLY the description, nothing else. No quotes, no "Description:" prefix."""

    response = llm.invoke(prompt)
    return response.content.strip()


def extract_all_fields(doc: str) -> dict:
    """Extract title, description, content, tags from any format."""
    lines = doc.split('\n')
    result = {"title": "", "description": "", "content": "", "tags": ""}

    # --- Extract Title ---
    for line in lines:
        if line.startswith("**Title:**"):
            result["title"] = line.replace("**Title:**", "").strip()
            break
        elif line.startswith("**Title**:"):
            result["title"] = line.replace("**Title**:", "").strip()
            break

    if not result["title"]:
        for line in lines:
            if line.startswith("# ") and not line.startswith("## "):
                result["title"] = line.replace("# ", "").strip()
                break

    if not result["title"]:
        for line in lines:
            if line.startswith("Title:"):
                result["title"] = line.replace("Title:", "").strip()
                break

    # --- Extract Description (any format) ---
    for line in lines:
        if line.startswith("**Description:**"):
            result["description"] = line.replace("**Description:**", "").strip()
            break
        elif line.startswith("**Description**:"):
            result["description"] = line.replace("**Description**:", "").strip()
            break

    if not result["description"]:
        for i, line in enumerate(lines):
            if line.startswith("## Description"):
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip() and not lines[j].startswith("#"):
                        result["description"] = lines[j].strip()
                        break
                break

    if not result["description"]:
        for line in lines:
            if line.startswith("Description:"):
                result["description"] = line.replace("Description:", "").strip()
                break

    # --- Extract Tags ---
    for line in lines:
        if line.startswith("**Tags:**"):
            result["tags"] = line.replace("**Tags:**", "").strip()
            break

    if not result["tags"]:
        tag_pattern = r'#[\w-]+'
        found_tags = re.findall(tag_pattern, doc)
        if found_tags:
            seen = set()
            unique_tags = []
            for t in found_tags:
                if t not in seen:
                    seen.add(t)
                    unique_tags.append(t)
            result["tags"] = ' '.join(unique_tags[-15:])

    # --- Extract Content (everything else) ---
    result["content"] = doc

    return result


def format_document(title: str, description: str, content: str, tags: str) -> str:
    """
    Format document in the standard **Title:**/**Description:** format.
    Cleans up old formatting artifacts from content.
    """
    clean_lines = []
    skip_patterns = [
        r'^\*\*Title\*?\*?:',
        r'^\*\*Description\*?\*?:',
        r'^\*\*Content\*?\*?:',
        r'^\*\*Tags\*?\*?:',
        r'^## Description\s*$',
        r'^Title:',
        r'^Description:',
    ]

    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        skip = False

        # Skip title lines (various formats)
        if title and title in line:
            if any(re.match(p, line) for p in [r'^\*\*Title', r'^# ', r'^Title:']):
                skip = True

        # Skip description section headers
        if line.strip() == "## Description":
            skip = True
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i < len(lines):
                i += 1
            continue

        for pattern in skip_patterns[:5]:
            if re.match(pattern, line):
                skip = True
                break

        if not skip:
            clean_lines.append(line)
        i += 1

    clean_content = '\n'.join(clean_lines).strip()

    while '\n\n\n' in clean_content:
        clean_content = clean_content.replace('\n\n\n', '\n\n')

    if len(clean_content) > 2000:
        clean_content = clean_content[:2000] + "\n...(truncated)"

    return f"""**Title:** {title}
**Description:** {description}

**Content:** {clean_content}

**Tags:** {tags}"""


def main():
    # Load issues
    with open("/home/hungson175/dev/deploy-memory-tools/scripts/description_issues.json", 'r') as f:
        data = json.load(f)

    needs_reformat = data.get("needs_reformat", [])
    truly_missing = data.get("truly_missing", [])

    print(f"Needs reformat: {len(needs_reformat)}")
    print(f"Truly missing: {len(truly_missing)}")
    print(f"Total: {len(needs_reformat) + len(truly_missing)}")
    print(f"Using LLM: grok-4-fast-non-reasoning (xAI)\n")

    client = QdrantClient(url=QDRANT_URL, check_compatibility=False)

    stats = {"reformatted": 0, "generated": 0, "errors": 0, "skipped": 0}

    all_items = [(item, "reformat") for item in needs_reformat] + \
                [(item, "generate") for item in truly_missing]

    for idx, (item, action_type) in enumerate(all_items, 1):
        doc_id = item["id"]
        collection = item["collection"]

        print(f"\n[{idx}/{len(all_items)}] {action_type.upper()}: {item['title'][:50]}...")
        print(f"  Collection: {collection}, ID: {doc_id[:8]}...")

        try:
            results = client.retrieve(
                collection_name=collection,
                ids=[doc_id],
                with_payload=True,
                with_vectors=False
            )

            if not results:
                print(f"  ✗ Not found")
                stats["errors"] += 1
                continue

            point = results[0]
            doc = point.payload.get("document", "")
            metadata = {k: v for k, v in point.payload.items() if k != "document"}

            fields = extract_all_fields(doc)

            if doc.startswith("**Title:**") and "**Description:**" in doc:
                print(f"  ✓ Already correct format, skipping")
                stats["skipped"] += 1
                continue

            title = fields["title"] or f"Memory {doc_id[:8]}"
            tags = fields["tags"]

            if action_type == "reformat":
                description = fields["description"]
                if not description:
                    print(f"  ! Expected description but none found, generating with Grok...")
                    description = generate_description(doc, title)
                    action_type = "generate"
            else:
                print(f"  Generating description with Grok...")
                description = generate_description(doc, title)

            print(f"  Description: {description[:60]}...")

            new_doc = format_document(title, description, fields["content"], tags)

            print(f"  Generating embedding...")
            embedding = get_embedding(new_doc)

            if "title" not in metadata or not metadata["title"]:
                metadata["title"] = title

            client.upsert(
                collection_name=collection,
                points=[
                    models.PointStruct(
                        id=doc_id,
                        vector=embedding,
                        payload={"document": new_doc, **metadata}
                    )
                ]
            )

            if action_type == "reformat":
                stats["reformatted"] += 1
            else:
                stats["generated"] += 1

            print(f"  ✓ Updated")
            time.sleep(DELAY_BETWEEN_UPDATES)

        except Exception as e:
            print(f"  ✗ Error: {e}")
            stats["errors"] += 1

    print(f"\n{'='*60}")
    print(f"COMPLETE")
    print(f"{'='*60}")
    print(f"Reformatted: {stats['reformatted']}")
    print(f"Generated descriptions: {stats['generated']}")
    print(f"Skipped (already OK): {stats['skipped']}")
    print(f"Errors: {stats['errors']}")


if __name__ == "__main__":
    main()
