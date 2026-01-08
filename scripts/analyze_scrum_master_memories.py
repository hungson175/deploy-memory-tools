#!/usr/bin/env python3
"""
Analyze Scrum Master memories from Qdrant:
1. Retrieve all 27 memory documents
2. Extract their vectors
3. Calculate 27x27 similarity matrix
4. Write memories to markdown file
5. Write similarity matrix to CSV
"""

import os
import json
from qdrant_client import QdrantClient
from dotenv import load_dotenv
import numpy as np

# Load environment variables
load_dotenv()

# Connect to Qdrant
qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
client = QdrantClient(url=qdrant_url)

# Collection name
COLLECTION = "scrum-master-patterns"

# The 27 doc IDs in order (from the search results)
DOC_IDS = [
    "4136f59b-7e29-497f-b37b-d93e57156663",
    "473fb2e3-b730-415c-bc95-d222675ddef3",
    "27b25a35-11d1-4638-9150-5a654e96b827",
    "eb8bc0e4-4aa4-4dc8-9387-87f57482348f",
    "c6f26289-fad2-42a5-9f21-224311843ee3",
    "f19ac2d3-16fc-4531-83b1-990958274ffa",
    "6fe55403-b5c8-48e7-ab7f-536d3d6cd02f",
    "a34de166-e41c-4e63-a4af-8738ef39ad09",
    "22296283-d131-4099-ad39-ce3c4bf4df93",
    "d28eea2e-924c-4719-8bfa-c3a91bba6c49",
    "08d9a303-0ef8-4843-ae92-00c73a942125",
    "f0da8c6c-05ad-4ccf-a71e-fe99c82c71be",
    "515bc593-26a1-44e8-8b80-739f3ae1604c",
    "92e07250-e546-4d8f-9540-67476a3f8238",
    "747f6877-1c00-4747-bfba-cc101ca5554d",
    "46783d5d-7b4f-4553-9b13-e3f1103e483e",
    "c72188a0-a5fd-4148-a6fb-0e8370167b50",
    "b18838d5-dedf-4f24-813c-7223e1148489",
    "10e9b13b-2610-43d9-b12a-7ee9f71a9cde",
    "286e77c6-4663-4d8c-a9d8-1e92d2dcb575",
    "5619b6e6-4ca2-4f64-9b39-3d64f5ba518f",
    "2e9eaee8-2efa-4135-8697-2734eba27868",
    "b4e46d04-cfd3-4fca-80a0-2ff008074ae9",
    "92a671af-6cfb-42a9-b25e-0cd1f62f79b3",
    "cca6291b-9d48-428c-9f97-dc45b5f81fe1",
    "ba67551e-5e05-4683-b316-db9598d8f796",
    "c98f3641-9320-4eb3-bb59-ac523f06b0b4",
]

print(f"Connecting to Qdrant at {qdrant_url}")
print(f"Collection: {COLLECTION}")
print(f"Retrieving {len(DOC_IDS)} memories...\n")

# Retrieve all points
points = client.retrieve(
    collection_name=COLLECTION,
    ids=DOC_IDS,
    with_vectors=True,
    with_payload=True
)

print(f"Retrieved {len(points)} points")

# Extract vectors and create similarity matrix
vectors = []
memories = []

for point in points:
    vectors.append(point.vector)
    memories.append({
        'id': point.id,
        'payload': point.payload
    })

# Calculate cosine similarity matrix
vectors_array = np.array(vectors)
# Normalize vectors
norms = np.linalg.norm(vectors_array, axis=1, keepdims=True)
normalized_vectors = vectors_array / norms
# Compute similarity matrix (cosine similarity)
similarity_matrix = np.dot(normalized_vectors, normalized_vectors.T)

print(f"\nSimilarity matrix shape: {similarity_matrix.shape}")
print(f"Similarity range: [{similarity_matrix.min():.4f}, {similarity_matrix.max():.4f}]")

# Write memories to markdown file
print("\nWriting memories to markdown...")
with open("research/memory-duplication/all_27_memories.md", "w") as f:
    f.write("# All 27 Scrum Master Memories\n\n")
    f.write(f"Retrieved from Qdrant collection: `{COLLECTION}`\n\n")
    f.write("---\n\n")

    for i, memory in enumerate(memories):
        payload = memory['payload']
        f.write(f"## Memory #{i+1}: {memory['id']}\n\n")

        # Extract metadata
        title = payload.get('title', 'Untitled')
        description = payload.get('description', 'No description')
        memory_type = payload.get('memory_type', 'unknown')
        tags = payload.get('tags', [])
        created_at = payload.get('created_at', 'unknown')

        f.write(f"**Title:** {title}\n\n")
        f.write(f"**Description:** {description}\n\n")
        f.write(f"**Type:** {memory_type}\n\n")
        f.write(f"**Created:** {created_at}\n\n")
        f.write(f"**Tags:** {', '.join(tags)}\n\n")

        # Full document
        document = payload.get('document', 'No document content')
        f.write(f"**Full Document:**\n\n```\n{document}\n```\n\n")
        f.write("---\n\n")

print("✓ Written to: research/memory-duplication/all_27_memories.md")

# Write similarity matrix to CSV
print("\nWriting similarity matrix to CSV...")
with open("research/memory-duplication/similarity_matrix_27x27.csv", "w") as f:
    # Header row with indices
    f.write("ID," + ",".join([f"M{i+1}" for i in range(27)]) + "\n")

    # Data rows
    for i in range(27):
        row_id = f"M{i+1}"
        row_data = [f"{similarity_matrix[i][j]:.4f}" for j in range(27)]
        f.write(row_id + "," + ",".join(row_data) + "\n")

print("✓ Written to: research/memory-duplication/similarity_matrix_27x27.csv")

# Find the most similar pair (excluding diagonal)
print("\nFinding most similar pair...")
max_sim = -1
max_i, max_j = -1, -1

for i in range(27):
    for j in range(i+1, 27):
        if similarity_matrix[i][j] > max_sim:
            max_sim = similarity_matrix[i][j]
            max_i, max_j = i, j

print(f"\nMost similar pair:")
print(f"  Memory #{max_i+1} ({DOC_IDS[max_i]})")
print(f"  Memory #{max_j+1} ({DOC_IDS[max_j]})")
print(f"  Similarity: {max_sim:.4f}")

# Write the most similar pair info to the markdown file
with open("research/memory-duplication/all_27_memories.md", "a") as f:
    f.write(f"\n\n# Most Similar Pair (by Qdrant Vector Similarity)\n\n")
    f.write(f"**Memory #{max_i+1}** and **Memory #{max_j+1}**\n\n")
    f.write(f"- **Memory #{max_i+1} ID:** `{DOC_IDS[max_i]}`\n")
    f.write(f"- **Memory #{max_j+1} ID:** `{DOC_IDS[max_j]}`\n")
    f.write(f"- **Cosine Similarity:** {max_sim:.4f}\n\n")

print("\n✓ Appended most similar pair to all_27_memories.md")
print("\nDone!")
