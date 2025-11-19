#!/usr/bin/env python3
"""
Qdrant Memory MCP Server V2 - True Two-Stage Retrieval
Provides semantic memory storage with preview/full content separation
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
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.shared.exceptions import McpError
from mcp.types import Tool, TextContent
from pydantic import AnyUrl
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize MCP server
server = Server("qdrant-memory-v2")

# Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536

# Role-based collections mapping
ROLE_COLLECTIONS = {
    "global": {
        "universal": "universal-patterns",      # Cross-domain patterns
        "backend": "backend-patterns",          # Backend engineering
        "frontend": "frontend-patterns",        # Frontend engineering
        "quant": "quant-patterns",              # Quantitative finance
        "devops": "devops-patterns",           # DevOps and infrastructure
        "ml": "ml-patterns",                   # Machine learning
        "security": "security-patterns",        # Security engineering
        "mobile": "mobile-patterns",           # Mobile development
    },
    "project": {
        # Project collections are created dynamically with pattern: proj-{sanitized-name}
    }
}

class MemoryServer:
    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL)
        self._embedding_cache = {}
        self._init_collections()

    def _init_collections(self):
        """Initialize all role-based collections if they don't exist"""
        for level, roles in ROLE_COLLECTIONS.items():
            if level == "global":
                for role, collection_name in roles.items():
                    try:
                        self.client.get_collection(collection_name)
                        logger.info(f"Collection '{collection_name}' exists")
                    except Exception:
                        logger.info(f"Creating collection '{collection_name}'")
                        self.client.create_collection(
                            collection_name=collection_name,
                            vectors_config=models.VectorParams(
                                size=EMBEDDING_DIMENSION,
                                distance=models.Distance.COSINE
                            )
                        )

    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding from OpenAI with caching"""
        if text in self._embedding_cache:
            return self._embedding_cache[text]

        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "input": text,
            "model": EMBEDDING_MODEL
        }

        with httpx.Client() as client:
            response = client.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            embedding = response.json()["data"][0]["embedding"]

        # Cache for session
        self._embedding_cache[text] = embedding
        return embedding

    def _get_collection_name(self, memory_level: str, role: str = None) -> str:
        """Get the actual collection name based on memory level and role"""
        if memory_level == "global":
            # For global, use role to determine collection
            if role and role in ROLE_COLLECTIONS["global"]:
                return ROLE_COLLECTIONS["global"][role]
            # Default to universal if no role specified
            return ROLE_COLLECTIONS["global"]["universal"]
        elif memory_level.startswith("proj-"):
            # Direct project collection name
            return memory_level
        else:
            # Legacy format: treat as project name to sanitize
            sanitized = memory_level.lower().replace(" ", "-").replace("_", "-")
            return f"proj-{sanitized}"

    def _extract_preview_from_document(self, document: str) -> Dict[str, str]:
        """Extract title and description from formatted memory document"""
        lines = document.split('\n')
        title = ""
        description = ""

        for line in lines:
            if line.startswith("**Title:**"):
                title = line.replace("**Title:**", "").strip()
            elif line.startswith("**Description:**"):
                description = line.replace("**Description:**", "").strip()

        return {"title": title, "description": description}

    async def search_memory(self, query: str, memory_level: str, limit: int = 10, role: str = None) -> str:
        """
        Search memories - returns ONLY previews (title + description + metadata)
        This is the first stage of two-stage retrieval.
        """
        try:
            collection_name = self._get_collection_name(memory_level, role)

            # Check if collection exists
            try:
                self.client.get_collection(collection_name)
            except Exception:
                return json.dumps({
                    "error": f"Collection '{collection_name}' does not exist",
                    "suggestion": "No memories stored yet for this level/role"
                })

            # Get embedding for query
            query_embedding = self._get_embedding(query)

            # Search in vector DB
            search_results = self.client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=limit,
                with_payload=True,
                with_vectors=False
            )

            if not search_results:
                return json.dumps({"results": [], "message": "No memories found"})

            # Build preview results (NO full content)
            previews = []
            for result in search_results:
                # Extract preview from stored document
                preview = self._extract_preview_from_document(result.payload.get("document", ""))

                preview_data = {
                    "doc_id": str(result.id),
                    "title": preview.get("title", "Untitled"),
                    "description": preview.get("description", "No description"),
                    "similarity": round(result.score, 3),
                    "memory_type": result.payload.get("memory_type", "unknown"),
                    "tags": result.payload.get("tags", []),
                    "role": result.payload.get("role", "unknown"),
                    "created_at": result.payload.get("created_at", "unknown")
                }
                previews.append(preview_data)

            return json.dumps({
                "results": previews,
                "total": len(previews),
                "message": f"Found {len(previews)} memory previews. Use get_memory(doc_id) to retrieve full content."
            }, indent=2)

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return json.dumps({"error": str(e)})

    async def get_memory(self, doc_id: str, memory_level: str, role: str = None) -> str:
        """
        Retrieve full memory content by ID.
        This is the second stage of two-stage retrieval.
        """
        try:
            collection_name = self._get_collection_name(memory_level, role)

            # Retrieve the specific document
            result = self.client.retrieve(
                collection_name=collection_name,
                ids=[doc_id],
                with_payload=True,
                with_vectors=False
            )

            if not result:
                return json.dumps({"error": f"Memory with ID '{doc_id}' not found"})

            point = result[0]
            return json.dumps({
                "doc_id": str(point.id),
                "document": point.payload.get("document", ""),
                "metadata": {
                    k: v for k, v in point.payload.items()
                    if k != "document"
                }
            }, indent=2)

        except Exception as e:
            logger.error(f"Get memory error: {str(e)}")
            return json.dumps({"error": str(e)})

    async def batch_get_memories(self, doc_ids: List[str], memory_level: str, role: str = None) -> str:
        """
        Retrieve multiple memories by IDs in a single call.
        Efficient for retrieving multiple relevant memories after search.
        """
        try:
            collection_name = self._get_collection_name(memory_level, role)

            # Retrieve multiple documents
            results = self.client.retrieve(
                collection_name=collection_name,
                ids=doc_ids,
                with_payload=True,
                with_vectors=False
            )

            memories = []
            for point in results:
                memories.append({
                    "doc_id": str(point.id),
                    "document": point.payload.get("document", ""),
                    "metadata": {
                        k: v for k, v in point.payload.items()
                        if k != "document"
                    }
                })

            return json.dumps({
                "memories": memories,
                "retrieved": len(memories),
                "requested": len(doc_ids)
            }, indent=2)

        except Exception as e:
            logger.error(f"Batch get error: {str(e)}")
            return json.dumps({"error": str(e)})

    async def store_memory(self, document: str, metadata: Dict[str, Any], memory_level: str) -> str:
        """Store a new memory"""
        try:
            # Extract role from metadata for collection routing
            role = metadata.get("role", "universal")
            collection_name = self._get_collection_name(memory_level, role)

            # Ensure collection exists (for project collections)
            if memory_level != "global":
                try:
                    self.client.get_collection(collection_name)
                except Exception:
                    logger.info(f"Creating project collection '{collection_name}'")
                    self.client.create_collection(
                        collection_name=collection_name,
                        vectors_config=models.VectorParams(
                            size=EMBEDDING_DIMENSION,
                            distance=models.Distance.COSINE
                        )
                    )

            # Generate embedding
            embedding = self._get_embedding(document)

            # Generate ID
            doc_id = str(uuid4())

            # Add timestamps
            now = datetime.now().isoformat()
            metadata["created_at"] = metadata.get("created_at", now)
            metadata["last_synced"] = now

            # Store in Qdrant
            self.client.upsert(
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

    async def update_memory(self, doc_id: str, document: str, metadata: Dict[str, Any], memory_level: str) -> str:
        """Update an existing memory (regenerates embedding)"""
        try:
            role = metadata.get("role", "universal")
            collection_name = self._get_collection_name(memory_level, role)

            # Check if document exists
            existing = self.client.retrieve(
                collection_name=collection_name,
                ids=[doc_id]
            )

            if not existing:
                return json.dumps({"error": f"Memory '{doc_id}' not found"})

            # Generate new embedding
            embedding = self._get_embedding(document)

            # Update timestamps
            metadata["last_updated"] = datetime.now().isoformat()
            metadata["last_synced"] = datetime.now().isoformat()

            # Update in Qdrant
            self.client.upsert(
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
                "message": "Memory updated successfully"
            })

        except Exception as e:
            logger.error(f"Update error: {str(e)}")
            return json.dumps({"error": str(e)})

    async def delete_memory(self, doc_id: str, memory_level: str, role: str = None) -> str:
        """Delete a memory by ID"""
        try:
            collection_name = self._get_collection_name(memory_level, role)

            # Delete from Qdrant
            self.client.delete(
                collection_name=collection_name,
                points_selector=models.PointIdsList(points=[doc_id])
            )

            # Get updated count
            collection_info = self.client.get_collection(collection_name)

            return json.dumps({
                "doc_id": doc_id,
                "status": "success",
                "remaining_memories": collection_info.points_count,
                "message": f"Memory deleted successfully"
            })

        except Exception as e:
            logger.error(f"Delete error: {str(e)}")
            return json.dumps({"error": str(e)})

    async def list_collections(self) -> str:
        """List all available collections with their memory counts"""
        try:
            collections = self.client.get_collections().collections

            collection_info = []
            for coll in collections:
                info = self.client.get_collection(coll.name)
                collection_info.append({
                    "name": coll.name,
                    "count": info.points_count,
                    "level": "global" if coll.name in ROLE_COLLECTIONS["global"].values() else "project",
                    "role": next((k for k, v in ROLE_COLLECTIONS["global"].items() if v == coll.name), None)
                })

            return json.dumps({
                "collections": collection_info,
                "total_collections": len(collection_info)
            }, indent=2)

        except Exception as e:
            logger.error(f"List collections error: {str(e)}")
            return json.dumps({"error": str(e)})

# Initialize memory server
memory_server = MemoryServer()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="search_memory",
            description="Search for memories using semantic search. Returns ONLY previews (title + description). Use get_memory() to retrieve full content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (2-3 sentence description of what you're looking for)"
                    },
                    "memory_level": {
                        "type": "string",
                        "description": "Memory level: 'global' or project name (e.g., 'proj-myproject')"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return (default: 10)",
                        "default": 10
                    },
                    "role": {
                        "type": "string",
                        "description": "Role for global memories: universal, backend, frontend, quant, devops, ml, security, mobile",
                        "default": "universal"
                    }
                },
                "required": ["query", "memory_level"]
            }
        ),
        Tool(
            name="get_memory",
            description="Retrieve full memory content by ID. Use after search_memory to get complete details.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Document ID from search results"
                    },
                    "memory_level": {
                        "type": "string",
                        "description": "Memory level: 'global' or project name"
                    },
                    "role": {
                        "type": "string",
                        "description": "Role for global memories (optional if doc_id is unique)"
                    }
                },
                "required": ["doc_id", "memory_level"]
            }
        ),
        Tool(
            name="batch_get_memories",
            description="Retrieve multiple memories by IDs efficiently. Use when you need full content for several memories.",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of document IDs to retrieve"
                    },
                    "memory_level": {
                        "type": "string",
                        "description": "Memory level: 'global' or project name"
                    },
                    "role": {
                        "type": "string",
                        "description": "Role for global memories"
                    }
                },
                "required": ["doc_ids", "memory_level"]
            }
        ),
        Tool(
            name="store_memory",
            description="Store a new memory in the vector database",
            inputSchema={
                "type": "object",
                "properties": {
                    "document": {
                        "type": "string",
                        "description": "Full formatted memory text (Title + Description + Content + Tags)"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Metadata including memory_type, role, tags, title, etc."
                    },
                    "memory_level": {
                        "type": "string",
                        "description": "Memory level: 'global' or project name"
                    }
                },
                "required": ["document", "metadata", "memory_level"]
            }
        ),
        Tool(
            name="update_memory",
            description="Update existing memory (regenerates embedding)",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Document ID to update"
                    },
                    "document": {
                        "type": "string",
                        "description": "New full formatted memory text"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Updated metadata"
                    },
                    "memory_level": {
                        "type": "string",
                        "description": "Memory level"
                    }
                },
                "required": ["doc_id", "document", "metadata", "memory_level"]
            }
        ),
        Tool(
            name="delete_memory",
            description="Delete a memory by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "doc_id": {
                        "type": "string",
                        "description": "Document ID to delete"
                    },
                    "memory_level": {
                        "type": "string",
                        "description": "Memory level"
                    },
                    "role": {
                        "type": "string",
                        "description": "Role for global memories"
                    }
                },
                "required": ["doc_id", "memory_level"]
            }
        ),
        Tool(
            name="list_collections",
            description="List all available memory collections with counts",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle tool calls"""
    try:
        if name == "search_memory":
            result = await memory_server.search_memory(
                query=arguments["query"],
                memory_level=arguments["memory_level"],
                limit=arguments.get("limit", 10),
                role=arguments.get("role", "universal")
            )
        elif name == "get_memory":
            result = await memory_server.get_memory(
                doc_id=arguments["doc_id"],
                memory_level=arguments["memory_level"],
                role=arguments.get("role")
            )
        elif name == "batch_get_memories":
            result = await memory_server.batch_get_memories(
                doc_ids=arguments["doc_ids"],
                memory_level=arguments["memory_level"],
                role=arguments.get("role")
            )
        elif name == "store_memory":
            result = await memory_server.store_memory(
                document=arguments["document"],
                metadata=arguments["metadata"],
                memory_level=arguments["memory_level"]
            )
        elif name == "update_memory":
            result = await memory_server.update_memory(
                doc_id=arguments["doc_id"],
                document=arguments["document"],
                metadata=arguments["metadata"],
                memory_level=arguments["memory_level"]
            )
        elif name == "delete_memory":
            result = await memory_server.delete_memory(
                doc_id=arguments["doc_id"],
                memory_level=arguments["memory_level"],
                role=arguments.get("role")
            )
        elif name == "list_collections":
            result = await memory_server.list_collections()
        else:
            result = json.dumps({"error": f"Unknown tool: {name}"})

        return [TextContent(type="text", text=result)]
    except Exception as e:
        logger.error(f"Tool execution error: {str(e)}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]

async def main():
    """Run the MCP server"""
    logger.info("Starting Qdrant Memory MCP Server V2...")

    # Run server
    async with httpx.AsyncClient() as client:
        await server.run(
            transport=sys.stdin.buffer,
            write_transport=sys.stdout.buffer,
            init_options=InitializationOptions(
                server_name="qdrant-memory-v2",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())