#!/usr/bin/env python3
"""
Qdrant Memory MCP Server V3.2 - True Two-Stage Retrieval
Provides semantic memory storage with preview/full content separation
Built with FastMCP for proper MCP protocol compliance
"""

import json
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Load environment variables
load_dotenv()

# CRITICAL: Configure logging to stderr (NOT stdout) for stdio transport
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stderr  # Must use stderr for stdio MCP servers
)
logger = logging.getLogger(__name__)

# Configuration from environment
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

# Embedding provider configuration
# Options: "openai", "voyage", "nomic"
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "openai").lower()

# Provider-specific API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

# Embedding model configuration per provider
EMBEDDING_CONFIGS = {
    "openai": {
        "model": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        "dimension": int(os.getenv("EMBEDDING_DIMENSION", "1536")),
        "api_url": "https://api.openai.com/v1/embeddings",
    },
    "voyage": {
        # voyage-3-large (best quality) or voyage-3.5-lite (cost-effective)
        "model": os.getenv("EMBEDDING_MODEL", "voyage-3-large"),
        # Voyage supports Matryoshka: 256, 512, 1024, 2048
        "dimension": int(os.getenv("EMBEDDING_DIMENSION", "1024")),
        "api_url": "https://api.voyageai.com/v1/embeddings",
    },
    "nomic": {
        "model": os.getenv("EMBEDDING_MODEL", "nomic-embed-text-v2-moe"),
        "dimension": int(os.getenv("EMBEDDING_DIMENSION", "768")),
        "api_url": "https://api-atlas.nomic.ai/v1/embedding/text",
    },
}

# Get active embedding config
EMBEDDING_CONFIG = EMBEDDING_CONFIGS.get(EMBEDDING_PROVIDER, EMBEDDING_CONFIGS["openai"])
EMBEDDING_MODEL: str = str(EMBEDDING_CONFIG["model"])
EMBEDDING_DIMENSION: int = int(EMBEDDING_CONFIG["dimension"])

# Role-based collections mapping
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

# Initialize FastMCP server
mcp = FastMCP("memory")

# Global Qdrant client (initialized lazily)
_qdrant_client: Optional[QdrantClient] = None
_embedding_cache: Dict[str, List[float]] = {}


def get_qdrant_client() -> QdrantClient:
    """Get or create Qdrant client (lazy initialization)"""
    global _qdrant_client
    if _qdrant_client is None:
        logger.info(f"Connecting to Qdrant at {QDRANT_URL}")
        _qdrant_client = QdrantClient(url=QDRANT_URL, check_compatibility=False)
        _init_collections(_qdrant_client)
    return _qdrant_client


def _init_collections(client: QdrantClient):
    """Initialize all role-based collections if they don't exist"""
    for role, collection_name in ROLE_COLLECTIONS.items():
        try:
            client.get_collection(collection_name)
            logger.info(f"Collection '{collection_name}' exists")
        except Exception:
            logger.info(f"Creating collection '{collection_name}'")
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=EMBEDDING_DIMENSION,
                    distance=models.Distance.COSINE
                )
            )


def _get_embedding_openai(text: str) -> List[float]:
    """Get embedding from OpenAI API"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not set in environment")

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {"input": text, "model": EMBEDDING_MODEL}

    api_url: str = str(EMBEDDING_CONFIG["api_url"])
    with httpx.Client() as client:
        response = client.post(
            api_url,
            headers=headers,
            json=data,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]


def _get_embedding_voyage(text: str) -> List[float]:
    """
    Get embedding from Voyage AI (Anthropic's recommended partner).

    Benefits over OpenAI:
    - +27% accuracy improvement (66.1% vs 39.2%)
    - Trained on "tricky negatives" for better RAG
    - 16K context window (vs ~8K)
    - Matryoshka support for flexible dimensions
    """
    if not VOYAGE_API_KEY:
        raise ValueError("VOYAGE_API_KEY not set. Get one at https://www.voyageai.com/")

    headers = {
        "Authorization": f"Bearer {VOYAGE_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "input": text,
        "model": EMBEDDING_MODEL,
        "input_type": "document",  # or "query" for search queries
    }

    # Optional: Matryoshka dimension reduction
    if EMBEDDING_DIMENSION and EMBEDDING_DIMENSION != 1024:
        data["output_dimension"] = EMBEDDING_DIMENSION

    api_url: str = str(EMBEDDING_CONFIG["api_url"])
    with httpx.Client() as client:
        response = client.post(
            api_url,
            headers=headers,
            json=data,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()["data"][0]["embedding"]


def _get_embedding_nomic(text: str) -> List[float]:
    """Get embedding from Nomic AI (open-source alternative)"""
    nomic_api_key = os.getenv("NOMIC_API_KEY")
    if not nomic_api_key:
        raise ValueError("NOMIC_API_KEY not set. Get one at https://atlas.nomic.ai/")

    headers = {
        "Authorization": f"Bearer {nomic_api_key}",
        "Content-Type": "application/json"
    }
    data = {"texts": [text], "model": EMBEDDING_MODEL}

    api_url: str = str(EMBEDDING_CONFIG["api_url"])
    with httpx.Client() as client:
        response = client.post(
            api_url,
            headers=headers,
            json=data,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()["embeddings"][0]


# Embedding provider router
_EMBEDDING_PROVIDERS = {
    "openai": _get_embedding_openai,
    "voyage": _get_embedding_voyage,
    "nomic": _get_embedding_nomic,
}


def _get_embedding(text: str) -> List[float]:
    """
    Get embedding using configured provider with caching.

    Supported providers (set via EMBEDDING_PROVIDER env var):
    - openai: text-embedding-3-small (default)
    - voyage: voyage-3-large (Anthropic's recommended partner, +27% accuracy)
    - nomic: nomic-embed-text-v2-moe (open-source)
    """
    if text in _embedding_cache:
        return _embedding_cache[text]

    provider_fn = _EMBEDDING_PROVIDERS.get(EMBEDDING_PROVIDER)
    if not provider_fn:
        raise ValueError(f"Unknown embedding provider: {EMBEDDING_PROVIDER}. "
                        f"Supported: {list(_EMBEDDING_PROVIDERS.keys())}")

    embedding = provider_fn(text)
    _embedding_cache[text] = embedding
    return embedding

# ============================================================================
# MCP Tools - Using FastMCP decorators
# ============================================================================

@mcp.tool(
    name="search_memory",
    annotations={
        "title": "Search Memory",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
def search_memory(query: str, roles: Optional[List[str]] = None, limit: int = 20) -> str:
    """
    Search for memories using semantic search. Returns ONLY previews (title + description).
    Use get_memory() to retrieve full content.

    Args:
        query: Search query (2-3 sentence description of what you're looking for)
        roles: List of roles to search (e.g., ["backend", "frontend", "universal"])
        limit: Maximum results to return (default: 20)

    Returns:
        JSON string with preview results
    """
    try:
        client = get_qdrant_client()
        target_roles = roles if roles else ["universal"]
        all_results = []

        query_embedding = _get_embedding(query)

        for role in target_roles:
            collection_name = ROLE_COLLECTIONS.get(role)

            if not collection_name:
                logger.warning(f"Unknown role '{role}', skipping")
                continue

            try:
                client.get_collection(collection_name)
            except Exception:
                logger.warning(f"Collection '{collection_name}' does not exist, skipping")
                continue

            search_results = client.query_points(
                collection_name=collection_name,
                query=query_embedding,
                limit=limit,
                with_payload=True,
                with_vectors=False
            ).points
            all_results.extend(search_results)

        if not all_results:
            return json.dumps({"results": [], "message": "No memories found"})

        previews = []
        for result in all_results:
            # Use metadata fields directly (not extracted from document)
            title = result.payload.get("title", "") or "Untitled"
            description = result.payload.get("description", "") or "No description"

            preview_data = {
                "doc_id": str(result.id),
                "title": title,
                "description": description,
                "similarity": round(result.score, 3),
                "memory_type": result.payload.get("memory_type", "unknown"),
                "tags": result.payload.get("tags", []),
                "role": result.payload.get("role", "unknown"),
                "created_at": result.payload.get("created_at", "unknown")
            }
            previews.append(preview_data)

        previews.sort(key=lambda x: x["similarity"], reverse=True)
        previews = previews[:limit]

        return json.dumps({
            "results": previews,
            "total": len(previews),
            "message": f"Found {len(previews)} memory previews. Use get_memory(doc_id) to retrieve full content."
        }, indent=2)

    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="get_memory",
    annotations={
        "title": "Get Memory",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
def get_memory(doc_id: str, roles: Optional[List[str]] = None) -> str:
    """
    Retrieve full memory content by ID. Use after search_memory to get complete details.

    Args:
        doc_id: Document ID from search results
        roles: Roles to search in (optional, will try all if not specified)

    Returns:
        JSON string with full memory content
    """
    try:
        client = get_qdrant_client()
        target_roles = roles if roles else list(ROLE_COLLECTIONS.keys())

        for role in target_roles:
            collection_name = ROLE_COLLECTIONS.get(role)
            if not collection_name:
                continue

            try:
                result = client.retrieve(
                    collection_name=collection_name,
                    ids=[doc_id],
                    with_payload=True,
                    with_vectors=False
                )

                if result:
                    point = result[0]
                    return json.dumps({
                        "doc_id": str(point.id),
                        "document": point.payload.get("document", ""),
                        "metadata": {
                            k: v for k, v in point.payload.items()
                            if k != "document"
                        }
                    }, indent=2)
            except Exception:
                continue

        return json.dumps({"error": f"Memory with ID '{doc_id}' not found in any collection"})

    except Exception as e:
        logger.error(f"Get memory error: {str(e)}")
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="batch_get_memories",
    annotations={
        "title": "Batch Get Memories",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
def batch_get_memories(doc_ids: List[str], roles: Optional[List[str]] = None) -> str:
    """
    Retrieve multiple memories by IDs efficiently. Use when you need full content for several memories.

    Args:
        doc_ids: List of document IDs to retrieve
        roles: Roles to search in (optional, will try all if not specified)

    Returns:
        JSON string with all retrieved memories
    """
    try:
        client = get_qdrant_client()
        target_roles = roles if roles else list(ROLE_COLLECTIONS.keys())
        all_memories = []
        found_ids = set()

        for role in target_roles:
            collection_name = ROLE_COLLECTIONS.get(role)
            if not collection_name:
                continue

            try:
                results = client.retrieve(
                    collection_name=collection_name,
                    ids=doc_ids,
                    with_payload=True,
                    with_vectors=False
                )

                for point in results:
                    if str(point.id) not in found_ids:
                        memory_data = {
                            "doc_id": str(point.id),
                            "document": point.payload.get("document", ""),
                            "metadata": {
                                k: v for k, v in point.payload.items()
                                if k != "document"
                            }
                        }
                        all_memories.append(memory_data)
                        found_ids.add(str(point.id))
            except Exception:
                continue

        return json.dumps({
            "memories": all_memories,
            "retrieved": len(all_memories),
            "requested": len(doc_ids)
        }, indent=2)

    except Exception as e:
        logger.error(f"Batch get memories error: {str(e)}")
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="store_memory",
    annotations={
        "title": "Store Memory",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
def store_memory(document: str, metadata: Dict[str, Any]) -> str:
    """
    Store a new memory in the vector database.

    Args:
        document: Full formatted memory text (Title + Description + Content + Tags)
        metadata: Metadata including memory_type, role, tags, title, description, frequency

    Returns:
        JSON string with storage confirmation
    """
    try:
        client = get_qdrant_client()
        role = metadata.get("role", "universal")
        collection_name = ROLE_COLLECTIONS.get(role)

        if not collection_name:
            return json.dumps({"error": f"Unknown role '{role}'. Valid roles: {list(ROLE_COLLECTIONS.keys())}"})

        embedding = _get_embedding(document)
        doc_id = str(uuid4())

        now = datetime.now().isoformat()
        metadata["created_at"] = metadata.get("created_at", now)
        metadata["last_synced"] = now

        client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=doc_id,
                    vector=embedding,
                    payload={
                        "document": document,
                        **metadata
                    }
                )
            ]
        )

        return json.dumps({
            "doc_id": doc_id,
            "status": "success",
            "collection": collection_name,
            "message": f"Memory stored successfully in '{collection_name}'"
        })

    except Exception as e:
        logger.error(f"Store error: {str(e)}")
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="update_memory",
    annotations={
        "title": "Update Memory",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
def update_memory(doc_id: str, document: str, metadata: Dict[str, Any]) -> str:
    """
    Update existing memory (regenerates embedding).

    Args:
        doc_id: Document ID to update
        document: New full formatted memory text
        metadata: Updated metadata

    Returns:
        JSON string with update confirmation
    """
    try:
        client = get_qdrant_client()
        role = metadata.get("role", "universal")
        collection_name = ROLE_COLLECTIONS.get(role)

        if not collection_name:
            return json.dumps({"error": f"Unknown role '{role}'. Valid roles: {list(ROLE_COLLECTIONS.keys())}"})

        embedding = _get_embedding(document)

        now = datetime.now().isoformat()
        metadata["last_updated"] = now
        metadata["last_synced"] = now

        client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=doc_id,
                    vector=embedding,
                    payload={
                        "document": document,
                        **metadata
                    }
                )
            ]
        )

        return json.dumps({
            "doc_id": doc_id,
            "status": "success",
            "collection": collection_name,
            "message": f"Memory updated successfully in '{collection_name}'"
        })

    except Exception as e:
        logger.error(f"Update error: {str(e)}")
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="delete_memory",
    annotations={
        "title": "Delete Memory",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
def delete_memory(doc_id: str, roles: Optional[List[str]] = None) -> str:
    """
    Delete a memory by ID.

    Args:
        doc_id: Document ID to delete
        roles: Roles to search in (optional, will try all if not specified)

    Returns:
        JSON string with deletion confirmation
    """
    try:
        client = get_qdrant_client()
        target_roles = roles if roles else list(ROLE_COLLECTIONS.keys())
        deleted = False
        collection_used = None

        for role in target_roles:
            collection_name = ROLE_COLLECTIONS.get(role)
            if not collection_name:
                continue

            try:
                client.delete(
                    collection_name=collection_name,
                    points_selector=models.PointIdsList(points=[doc_id])
                )
                deleted = True
                collection_used = collection_name
                break
            except Exception:
                continue

        if not deleted:
            return json.dumps({"error": f"Memory with ID '{doc_id}' not found in any collection"})

        collection_info = client.get_collection(collection_used)

        return json.dumps({
            "doc_id": doc_id,
            "status": "success",
            "remaining_memories": collection_info.points_count,
            "collection": collection_used,
            "message": "Memory deleted successfully"
        })

    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        return json.dumps({"error": str(e)})


@mcp.tool(
    name="list_collections",
    annotations={
        "title": "List Collections",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
def list_collections() -> str:
    """
    List all available memory collections with counts.

    Returns:
        JSON string with collection information
    """
    try:
        client = get_qdrant_client()
        collections = client.get_collections().collections

        collection_info = []
        for coll in collections:
            info = client.get_collection(coll.name)

            is_global = coll.name in ROLE_COLLECTIONS.values()
            role = None
            if is_global:
                role = next((k for k, v in ROLE_COLLECTIONS.items() if v == coll.name), None)

            collection_info.append({
                "name": coll.name,
                "count": info.points_count,
                "level": "global" if is_global else "project",
                "role": role
            })

        return json.dumps({
            "collections": collection_info,
            "total_collections": len(collection_info)
        }, indent=2)

    except Exception as e:
        logger.error(f"List collections error: {str(e)}")
        return json.dumps({"error": str(e)})


# ============================================================================
# Server Startup
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting Qdrant Memory MCP Server V3.3 (FastMCP)")
    logger.info(f"Qdrant URL: {QDRANT_URL}")
    logger.info(f"Embedding Provider: {EMBEDDING_PROVIDER}")
    logger.info(f"Embedding Model: {EMBEDDING_MODEL}")
    logger.info(f"Embedding Dimension: {EMBEDDING_DIMENSION}")

    # Log API key status based on provider
    if EMBEDDING_PROVIDER == "openai":
        logger.info(f"OpenAI API Key: {'Set' if OPENAI_API_KEY else 'NOT SET'}")
    elif EMBEDDING_PROVIDER == "voyage":
        logger.info(f"Voyage API Key: {'Set' if VOYAGE_API_KEY else 'NOT SET'}")
    elif EMBEDDING_PROVIDER == "nomic":
        nomic_key = os.getenv("NOMIC_API_KEY")
        logger.info(f"Nomic API Key: {'Set' if nomic_key else 'NOT SET'}")

    mcp.run()
