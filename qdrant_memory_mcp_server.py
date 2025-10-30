#!/usr/bin/env python3
"""MCP server for Memory Skills with Qdrant vector database operations.

Provides memory-specific CRUD + search tools for Claude Code memory skills.
Auto-routes to correct collection based on memory_level (coder vs project).
"""

import os
import re
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from openai import OpenAI
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointIdsList, PointStruct, VectorParams

# Load environment
load_dotenv()

# Configuration
QDRANT_URL = "http://localhost:6333"
EMBEDDING_MODEL = "text-embedding-3-small"
VECTOR_SIZE = 1536

# Initialize clients
qdrant_client = QdrantClient(url=QDRANT_URL)
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Create MCP server
mcp = FastMCP("Memory")


def get_collection_name(memory_level: str) -> str:
    """Get collection name based on memory level.

    Args:
        memory_level: "coder" for global, "project" for current project

    Returns:
        Collection name: "coder-memory" or "proj-{sanitized-name}"
    """
    if memory_level == "coder":
        return "coder-memory"
    elif memory_level == "project":
        # Get current working directory as project name
        project_path = Path.cwd()
        project_name = project_path.name
        # Sanitize: only lowercase alphanumeric + hyphens
        safe_name = re.sub(r'[^a-z0-9]+', '-', project_name.lower()).strip('-')
        return f"proj-{safe_name}"
    else:
        raise ValueError(f"Invalid memory_level: {memory_level}. Must be 'coder' or 'project'")


def ensure_collection_exists(collection_name: str) -> bool:
    """Ensure collection exists, create if not.

    Args:
        collection_name: Name of collection to check/create

    Returns:
        True if collection exists or was created successfully
    """
    try:
        collections = qdrant_client.get_collections().collections
        collection_exists = any(col.name == collection_name for col in collections)

        if not collection_exists:
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            )
        return True
    except Exception as e:
        print(f"Error ensuring collection exists: {e}")
        return False


def generate_embedding(text: str) -> list[float]:
    """Generate embedding using OpenAI.

    Args:
        text: Text to embed

    Returns:
        Embedding vector
    """
    response = openai_client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding


@mcp.tool()
def search_memory(
    query: str,
    memory_level: str,
    limit: int = 5
) -> str:
    """Search for similar memories using semantic search.

    Args:
        query: Search query (2-3 sentence summary of what you're looking for)
        memory_level: "coder" for global memories, "project" for project-specific
        limit: Maximum number of results (default: 5)

    Returns:
        Formatted search results with file paths, similarity scores, and metadata
    """
    try:
        collection_name = get_collection_name(memory_level)

        # Check if collection exists
        if not ensure_collection_exists(collection_name):
            return f"Error: Could not access collection for memory_level '{memory_level}'"

        # Generate embedding for query
        query_embedding = generate_embedding(query)

        # Search
        search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=limit,
            with_payload=True
        )

        if not search_results:
            return f"No memories found in '{collection_name}' (memory_level: {memory_level})"

        # Format results
        results = [f"Found {len(search_results)} similar memories in '{collection_name}':\n"]
        for idx, result in enumerate(search_results, 1):
            payload = result.payload
            metadata = payload.get('metadata', {})
            document = payload.get('document', 'N/A')

            similarity = result.score
            doc_id = result.id
            file_path = metadata.get('file_path', 'unknown')
            title = metadata.get('title', 'Untitled')
            tags = metadata.get('tags', [])
            memory_type = metadata.get('memory_type', 'unknown')

            tags_str = ' '.join([f'#{tag}' for tag in tags]) if tags else ''

            results.append(f"\n{idx}. [Similarity: {similarity:.3f}] {title}")
            results.append(f"   ID: {doc_id}")
            results.append(f"   File: {file_path}")
            results.append(f"   Type: {memory_type}")
            if tags_str:
                results.append(f"   Tags: {tags_str}")
            results.append(f"   Content: {document[:200]}...")
            results.append("")

        return "\n".join(results)

    except Exception as e:
        return f"Error searching memories: {str(e)}"


@mcp.tool()
def store_memory(
    document: str,
    metadata: Dict[str, Any],
    memory_level: str
) -> str:
    """Insert a new memory into vector database.

    Args:
        document: Full formatted memory text (Title + Description + Content + Tags)
        metadata: Dict with keys: memory_type, file_path, skill_root, tags, title, created_at, last_synced
        memory_level: "coder" for global, "project" for project-specific

    Returns:
        JSON string with document ID and status
    """
    try:
        collection_name = get_collection_name(memory_level)

        # Ensure collection exists
        if not ensure_collection_exists(collection_name):
            return f'{{"error": "Could not access collection for memory_level \'{memory_level}\'"}}'

        # Generate embedding
        embedding = generate_embedding(document)

        # Add memory_level to metadata
        metadata['memory_level'] = memory_level

        # Prepare payload
        payload = {
            'document': document,
            'metadata': metadata
        }

        # Insert
        point_id = str(uuid.uuid4())
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[PointStruct(id=point_id, vector=embedding, payload=payload)]
        )

        # Get collection info
        collection_info = qdrant_client.get_collection(collection_name=collection_name)

        return f'{{"id": "{point_id}", "collection": "{collection_name}", "total_points": {collection_info.points_count}, "status": "success"}}'

    except Exception as e:
        return f'{{"error": "{str(e)}"}}'


@mcp.tool()
def update_memory(
    doc_id: str,
    document: str,
    metadata: Dict[str, Any],
    memory_level: str
) -> str:
    """Update an existing memory (regenerates embedding).

    Args:
        doc_id: Document ID to update
        document: New full formatted memory text
        metadata: Updated metadata dict
        memory_level: "coder" or "project"

    Returns:
        Success message or error
    """
    try:
        collection_name = get_collection_name(memory_level)

        # Check if document exists
        points = qdrant_client.retrieve(
            collection_name=collection_name,
            ids=[doc_id]
        )

        if not points:
            return f"Error: Document ID '{doc_id}' not found in '{collection_name}'"

        # Generate new embedding
        embedding = generate_embedding(document)

        # Add memory_level to metadata
        metadata['memory_level'] = memory_level
        metadata['last_synced'] = datetime.utcnow().isoformat() + 'Z'

        # Prepare payload
        payload = {
            'document': document,
            'metadata': metadata
        }

        # Update (upsert with same ID)
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[PointStruct(id=doc_id, vector=embedding, payload=payload)]
        )

        return f"Successfully updated memory ID: {doc_id} in '{collection_name}'"

    except Exception as e:
        return f"Error updating memory: {str(e)}"


@mcp.tool()
def get_memory(doc_id: str, memory_level: str) -> str:
    """Retrieve a memory by its ID.

    Args:
        doc_id: Document ID to retrieve
        memory_level: "coder" or "project"

    Returns:
        Memory document and metadata, or error message
    """
    try:
        collection_name = get_collection_name(memory_level)

        # Retrieve document
        points = qdrant_client.retrieve(
            collection_name=collection_name,
            ids=[doc_id]
        )

        if not points:
            return f"Error: Document ID '{doc_id}' not found in '{collection_name}'"

        point = points[0]
        payload = point.payload
        document = payload.get('document', 'N/A')
        metadata = payload.get('metadata', {})

        result = f"Memory ID: {doc_id}\n"
        result += f"Collection: {collection_name}\n"
        result += f"File: {metadata.get('file_path', 'unknown')}\n"
        result += f"Type: {metadata.get('memory_type', 'unknown')}\n"
        result += f"Tags: {' '.join(['#' + t for t in metadata.get('tags', [])])}\n"
        result += f"\nDocument:\n{document}"

        return result

    except Exception as e:
        return f"Error retrieving memory: {str(e)}"


@mcp.tool()
def delete_memory(doc_id: str, memory_level: str) -> str:
    """Delete a memory by its ID.

    Args:
        doc_id: Document ID to delete
        memory_level: "coder" or "project"

    Returns:
        Success message with updated points count, or error
    """
    try:
        collection_name = get_collection_name(memory_level)

        # Delete
        qdrant_client.delete(
            collection_name=collection_name,
            points_selector=PointIdsList(points=[doc_id])
        )

        # Get updated collection info
        collection_info = qdrant_client.get_collection(collection_name=collection_name)

        return f"Successfully deleted memory ID: {doc_id} from '{collection_name}'\nTotal points remaining: {collection_info.points_count}"

    except Exception as e:
        return f"Error deleting memory: {str(e)}"


if __name__ == "__main__":
    mcp.run()
