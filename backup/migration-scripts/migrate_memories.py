#!/usr/bin/env python3
"""One-time migration script to populate Qdrant from file-based memories."""

import os
import re
import uuid
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "coder-memory"
CODER_MEMORY_PATH = Path.home() / ".claude/skills/coder-memory-store"

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def parse_memories_from_file(file_path: Path) -> List[Dict]:
    """Parse memories from a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split by --- separator
    chunks = re.split(r'\n---\n', content)

    memories = []
    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        # Skip headers (lines starting with #)
        if chunk.startswith('#'):
            continue

        # Extract Title
        title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?=\n)', chunk)
        if not title_match:
            continue

        title = title_match.group(1).strip()

        # Extract Description
        desc_match = re.search(r'\*\*Description:\*\*\s*(.+?)(?=\n)', chunk)
        description = desc_match.group(1).strip() if desc_match else ""

        # Extract Content
        content_match = re.search(r'\*\*Content:\*\*\s*(.+?)(?=\n\*\*Tags:|$)', chunk, re.DOTALL)
        main_content = content_match.group(1).strip() if content_match else ""

        # Extract Tags
        tags_match = re.search(r'\*\*Tags:\*\*\s*(.+?)$', chunk)
        tags_str = tags_match.group(1).strip() if tags_match else ""
        tags = [tag.strip().lstrip('#') for tag in tags_str.split() if tag.startswith('#')]

        # Determine memory type from file path
        if 'episodic' in str(file_path):
            memory_type = 'episodic'
        elif 'procedural' in str(file_path):
            memory_type = 'procedural'
        elif 'semantic' in str(file_path):
            memory_type = 'semantic'
        else:
            memory_type = 'unknown'

        # Build full memory text
        full_text = f"""**Title:** {title}
**Description:** {description}

**Content:** {main_content}

**Tags:** {' '.join(['#' + tag for tag in tags])}"""

        # Relative file path
        rel_path = file_path.relative_to(CODER_MEMORY_PATH)

        memory = {
            'title': title,
            'description': description,
            'content': main_content,
            'full_text': full_text,
            'tags': tags,
            'memory_type': memory_type,
            'file_path': str(rel_path),
        }

        memories.append(memory)

    return memories

def generate_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI."""
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def insert_to_qdrant(memory: Dict) -> bool:
    """Insert memory into Qdrant collection."""
    try:
        # Generate embedding
        print(f"  Generating embedding for: {memory['title'][:50]}...")
        embedding = generate_embedding(memory['full_text'])

        # Prepare payload
        point_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + 'Z'

        payload = {
            'document': memory['full_text'],
            'metadata': {
                'memory_level': 'coder',
                'memory_type': memory['memory_type'],
                'file_path': memory['file_path'],
                'skill_root': 'coder-memory-store',
                'tags': memory['tags'],
                'title': memory['title'],
                'created_at': timestamp,
                'last_synced': timestamp,
            }
        }

        # Insert to Qdrant
        url = f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points"
        data = {
            'points': [{
                'id': point_id,
                'vector': embedding,
                'payload': payload
            }]
        }

        response = requests.put(url, json=data)
        response.raise_for_status()

        print(f"  ✓ Inserted: {point_id}")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("Memory Migration to Qdrant")
    print("=" * 60)
    print()

    # Find all memory files
    memory_files = []
    for memory_type in ['episodic', 'procedural', 'semantic']:
        type_dir = CODER_MEMORY_PATH / memory_type
        if type_dir.exists():
            for md_file in type_dir.glob('*.md'):
                # Skip README files
                if 'README' in md_file.name:
                    continue
                memory_files.append(md_file)

    print(f"Found {len(memory_files)} files to process\n")

    # Parse and insert memories
    total_memories = 0
    success_count = 0

    for file_path in sorted(memory_files):
        print(f"\nProcessing: {file_path.relative_to(CODER_MEMORY_PATH)}")
        memories = parse_memories_from_file(file_path)
        print(f"  Found {len(memories)} memories")

        for memory in memories:
            total_memories += 1
            if insert_to_qdrant(memory):
                success_count += 1

    # Summary
    print()
    print("=" * 60)
    print("Migration Complete")
    print("=" * 60)
    print(f"Total memories: {total_memories}")
    print(f"Successfully inserted: {success_count}")
    print(f"Failed: {total_memories - success_count}")
    print()

    # Verify collection
    response = requests.get(f"{QDRANT_URL}/collections/{COLLECTION_NAME}")
    if response.ok:
        data = response.json()
        points_count = data['result']['points_count']
        print(f"Qdrant collection '{COLLECTION_NAME}' now has {points_count} points")

if __name__ == '__main__':
    main()
