#!/usr/bin/env python3
"""
Demo 3: Graph-Enhanced Memory with Mem0

This demo shows how to add graph-based memory alongside your existing
vector search for entity relationships and temporal reasoning.

Expected improvements:
- +26% accuracy over baseline
- -91% p95 latency
- 90% token savings
- Entity relationship tracking
- Temporal awareness

Setup:
    pip install mem0ai
    # Optional for graph features:
    # - Neo4j running on localhost:7687
    # - Set NEO4J_URL, NEO4J_USERNAME, NEO4J_PASSWORD

Mem0 provides:
- Vector store (Qdrant, Pinecone, etc.)
- Key-value store (Redis)
- Graph store (Neo4j) for entity relationships
"""

import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

from dotenv import load_dotenv

# Check if mem0 is available
try:
    from mem0 import Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    print("Install mem0: pip install mem0ai")

load_dotenv()


class Mem0GraphDemo:
    """
    Demonstrates Mem0's graph-enhanced memory capabilities.

    Mem0 architecture:
    1. Vector Store - Semantic similarity search (your current approach)
    2. Key-Value Store - Fast lookups by ID
    3. Graph Store - Entity relationships and temporal tracking

    The graph layer enables:
    - Entity extraction and linking
    - Relationship mapping between memories
    - Temporal reasoning (what changed over time)
    - Multi-hop queries (A knows B who works at C)
    """

    def __init__(self, use_graph: bool = True):
        self.use_graph = use_graph

        if not MEM0_AVAILABLE:
            print("Mem0 not installed. Run: pip install mem0ai")
            return

        # Configure Mem0
        config = {
            "version": "v1.1",
            # Vector store configuration (using your existing Qdrant)
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "url": os.getenv("QDRANT_URL", "http://localhost:6333"),
                    "collection_name": "mem0-demo",
                }
            },
            # Embedding configuration
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small",
                    "api_key": os.getenv("OPENAI_API_KEY"),
                }
            },
            # LLM for memory extraction
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-4o-mini",
                    "api_key": os.getenv("OPENAI_API_KEY"),
                }
            },
        }

        # Add graph store if enabled and Neo4j is available
        if use_graph and os.getenv("NEO4J_URL"):
            config["graph_store"] = {
                "provider": "neo4j",
                "config": {
                    "url": os.getenv("NEO4J_URL", "bolt://localhost:7687"),
                    "username": os.getenv("NEO4J_USERNAME", "neo4j"),
                    "password": os.getenv("NEO4J_PASSWORD", "password"),
                }
            }
            print("Graph store enabled (Neo4j)")
        else:
            print("Graph store disabled (set NEO4J_URL to enable)")

        self.memory = Memory.from_config(config)

    def add_memory(
        self,
        content: str,
        user_id: str = "default",
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Add a memory with automatic entity extraction.

        Mem0 automatically:
        1. Extracts entities (people, concepts, tools)
        2. Identifies relationships between entities
        3. Links to existing entities in the graph
        4. Stores temporal metadata
        """
        result = self.memory.add(
            messages=content,
            user_id=user_id,
            metadata=metadata or {}
        )
        return result

    def search_memory(
        self,
        query: str,
        user_id: str = "default",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search memories using hybrid vector + graph retrieval.

        Mem0 combines:
        - Vector similarity for semantic matching
        - Graph traversal for relationship-based retrieval
        - Temporal filtering for time-aware results
        """
        results = self.memory.search(
            query=query,
            user_id=user_id,
            limit=limit
        )
        return results

    def get_all_memories(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """Get all memories for a user"""
        return self.memory.get_all(user_id=user_id)

    def get_memory_history(
        self,
        memory_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get the history of changes for a memory.

        This is unique to graph-enhanced memory - tracks how
        information evolved over time.
        """
        try:
            return self.memory.history(memory_id=memory_id)
        except Exception as e:
            return [{"error": str(e)}]


class SimpleGraphMemory:
    """
    Simplified graph memory implementation without Mem0.

    Shows the core concepts of graph-enhanced memory:
    1. Entity extraction
    2. Relationship mapping
    3. Graph + vector hybrid retrieval
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333"
    ):
        from qdrant_client import QdrantClient
        from qdrant_client.http import models
        import httpx

        self.qdrant = QdrantClient(url=qdrant_url)
        self.collection = "simple-graph-demo"
        self.openai_key = os.getenv("OPENAI_API_KEY")

        # In-memory graph (production: use Neo4j)
        self.entities: Dict[str, Dict] = {}  # entity_id -> {name, type, memories}
        self.relationships: List[Dict] = []  # {source, target, type}

        self._setup_collection()

    def _setup_collection(self):
        from qdrant_client.http import models
        try:
            self.qdrant.get_collection(self.collection)
        except Exception:
            self.qdrant.create_collection(
                collection_name=self.collection,
                vectors_config=models.VectorParams(
                    size=1536,
                    distance=models.Distance.COSINE
                )
            )

    def _get_embedding(self, text: str) -> List[float]:
        import httpx
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        with httpx.Client() as client:
            response = client.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json={"input": text, "model": "text-embedding-3-small"},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]

    def _extract_entities(self, text: str) -> List[Dict[str, str]]:
        """
        Extract entities using LLM.

        In production, use:
        - spaCy NER for speed
        - GPT-4 for accuracy
        - Combination of both
        """
        import httpx

        prompt = f"""Extract entities from this text. Return JSON array with objects having 'name' and 'type' fields.
Types: PERSON, CONCEPT, TOOL, ORGANIZATION, PATTERN

Text: {text}

Return only valid JSON array, no explanation."""

        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }

        with httpx.Client() as client:
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0
                },
                timeout=30.0
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]

        try:
            # Clean up response
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except json.JSONDecodeError:
            return []

    def _extract_relationships(
        self,
        text: str,
        entities: List[Dict]
    ) -> List[Dict[str, str]]:
        """Extract relationships between entities"""
        if len(entities) < 2:
            return []

        import httpx

        entity_names = [e["name"] for e in entities]
        prompt = f"""Given these entities: {entity_names}

And this text: {text}

Extract relationships between entities. Return JSON array with objects having:
- 'source': entity name
- 'target': entity name
- 'type': relationship type (e.g., USES, IMPROVES, PART_OF, RELATED_TO)

Return only valid JSON array."""

        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }

        with httpx.Client() as client:
            response = client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0
                },
                timeout=30.0
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]

        try:
            content = content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except json.JSONDecodeError:
            return []

    def add_memory(self, memory_id: str, content: str, metadata: Dict = None):
        """Add memory with entity extraction and graph building"""
        from qdrant_client.http import models

        # Get embedding
        embedding = self._get_embedding(content)

        # Extract entities
        entities = self._extract_entities(content)
        print(f"Extracted entities: {[e['name'] for e in entities]}")

        # Extract relationships
        relationships = self._extract_relationships(content, entities)
        print(f"Extracted relationships: {relationships}")

        # Update graph
        for entity in entities:
            entity_id = entity["name"].lower().replace(" ", "_")
            if entity_id not in self.entities:
                self.entities[entity_id] = {
                    "name": entity["name"],
                    "type": entity["type"],
                    "memories": []
                }
            self.entities[entity_id]["memories"].append(memory_id)

        for rel in relationships:
            self.relationships.append(rel)

        # Store in vector DB
        self.qdrant.upsert(
            collection_name=self.collection,
            points=[
                models.PointStruct(
                    id=memory_id,
                    vector=embedding,
                    payload={
                        "content": content,
                        "entities": [e["name"] for e in entities],
                        "created_at": datetime.now().isoformat(),
                        **(metadata or {})
                    }
                )
            ]
        )

        return {
            "memory_id": memory_id,
            "entities": entities,
            "relationships": relationships
        }

    def search(
        self,
        query: str,
        limit: int = 5,
        use_graph: bool = True
    ) -> List[Dict]:
        """
        Hybrid search using vector + graph.

        1. Vector search for semantic similarity
        2. Graph expansion for related entities
        3. Boost scores for graph-connected results
        """
        # Vector search
        query_embedding = self._get_embedding(query)
        vector_results = self.qdrant.query_points(
            collection_name=self.collection,
            query=query_embedding,
            limit=limit * 2,  # Fetch more for graph boost
            with_payload=True
        ).points

        if not use_graph:
            return [
                {
                    "id": str(r.id),
                    "content": r.payload.get("content"),
                    "score": r.score,
                    "source": "vector"
                }
                for r in vector_results[:limit]
            ]

        # Extract entities from query
        query_entities = self._extract_entities(query)
        query_entity_names = {e["name"].lower() for e in query_entities}

        # Boost results that share entities with query
        boosted_results = []
        for result in vector_results:
            result_entities = {e.lower() for e in result.payload.get("entities", [])}
            entity_overlap = len(query_entity_names & result_entities)

            # Graph boost: 10% per shared entity
            graph_boost = 1 + (0.1 * entity_overlap)
            boosted_score = result.score * graph_boost

            boosted_results.append({
                "id": str(result.id),
                "content": result.payload.get("content"),
                "score": boosted_score,
                "original_score": result.score,
                "shared_entities": list(query_entity_names & result_entities),
                "source": "hybrid" if entity_overlap > 0 else "vector"
            })

        # Sort by boosted score
        boosted_results.sort(key=lambda x: x["score"], reverse=True)
        return boosted_results[:limit]

    def get_entity_graph(self) -> Dict:
        """Return the current entity graph"""
        return {
            "entities": self.entities,
            "relationships": self.relationships,
            "stats": {
                "entity_count": len(self.entities),
                "relationship_count": len(self.relationships)
            }
        }

    def find_related_memories(self, entity_name: str) -> List[str]:
        """Find all memories connected to an entity"""
        entity_id = entity_name.lower().replace(" ", "_")
        if entity_id in self.entities:
            return self.entities[entity_id]["memories"]
        return []


def demo_mem0():
    """Demo using Mem0 (production-ready)"""
    if not MEM0_AVAILABLE:
        print("Skipping Mem0 demo - not installed")
        return

    print("\n" + "="*60)
    print("MEM0 GRAPH-ENHANCED MEMORY DEMO")
    print("="*60)

    demo = Mem0GraphDemo(use_graph=True)

    # Add memories about coding patterns
    memories = [
        "HNSW algorithm is used by Qdrant for approximate nearest neighbor search. It provides logarithmic search time.",
        "Binary quantization reduces memory usage by 24x but requires dimensions >= 1024 for best results.",
        "Cross-encoder re-ranking improves accuracy by 20-35% but adds 200ms latency. Works well with MiniLM models.",
        "Reciprocal Rank Fusion (RRF) combines BM25 and vector search results. k=60 is the standard default.",
        "Voyage AI embeddings are recommended by Anthropic. voyage-3-large achieves best retrieval accuracy.",
    ]

    print("\nAdding memories...")
    for i, memory in enumerate(memories):
        result = demo.add_memory(memory, user_id="demo-user")
        print(f"  Added memory {i+1}: {memory[:50]}...")

    # Search with graph-enhanced retrieval
    print("\nSearching: 'How to improve vector search accuracy?'")
    results = demo.search_memory(
        "How to improve vector search accuracy?",
        user_id="demo-user",
        limit=3
    )

    print("\nResults:")
    for i, result in enumerate(results, 1):
        memory = result.get("memory", result.get("text", ""))
        print(f"  {i}. {memory[:80]}...")

    # Get all memories
    print("\nAll stored memories:")
    all_memories = demo.get_all_memories(user_id="demo-user")
    print(f"  Total: {len(all_memories)} memories")


def demo_simple_graph():
    """Demo using simple graph implementation"""
    print("\n" + "="*60)
    print("SIMPLE GRAPH MEMORY DEMO")
    print("="*60)

    demo = SimpleGraphMemory()

    # Add memories with entity extraction
    memories = [
        ("mem1", "HNSW algorithm provides logarithmic search time for vector databases like Qdrant"),
        ("mem2", "Binary quantization reduces memory by converting float vectors to single bits"),
        ("mem3", "Cross-encoder re-ranking uses BERT to analyze query-document pairs together"),
        ("mem4", "Voyage AI embeddings are trained on tricky negatives for better RAG accuracy"),
        ("mem5", "Anthropic recommends Voyage AI as their official embedding partner for Claude"),
    ]

    print("\nAdding memories with entity extraction...")
    for mem_id, content in memories:
        print(f"\n--- {mem_id} ---")
        result = demo.add_memory(mem_id, content)

    # Show entity graph
    print("\n" + "-"*40)
    print("ENTITY GRAPH:")
    graph = demo.get_entity_graph()
    print(f"Entities: {graph['stats']['entity_count']}")
    print(f"Relationships: {graph['stats']['relationship_count']}")

    for entity_id, data in list(graph["entities"].items())[:5]:
        print(f"  - {data['name']} ({data['type']}): {len(data['memories'])} memories")

    # Compare vector-only vs hybrid search
    query = "What embedding models does Anthropic recommend?"
    print(f"\n{'='*40}")
    print(f"Query: {query}")
    print("="*40)

    print("\n1. VECTOR-ONLY SEARCH:")
    vector_results = demo.search(query, limit=3, use_graph=False)
    for r in vector_results:
        print(f"   [{r['score']:.3f}] {r['content'][:60]}...")

    print("\n2. HYBRID (VECTOR + GRAPH) SEARCH:")
    hybrid_results = demo.search(query, limit=3, use_graph=True)
    for r in hybrid_results:
        boost_info = f" (entities: {r.get('shared_entities', [])})" if r.get('shared_entities') else ""
        print(f"   [{r['score']:.3f}] {r['content'][:60]}...{boost_info}")

    # Find memories by entity
    print("\n" + "-"*40)
    print("ENTITY-BASED RETRIEVAL:")
    entity = "Voyage AI"
    related = demo.find_related_memories(entity)
    print(f"Memories about '{entity}': {related}")


def main():
    print("""
GRAPH-ENHANCED MEMORY DEMO

This demo shows how to add graph capabilities to your memory system:

1. Mem0 (Production) - Full-featured memory layer with:
   - Vector store (Qdrant)
   - Graph store (Neo4j)
   - Automatic entity extraction
   - 26% accuracy improvement

2. Simple Graph (Demo) - Shows core concepts:
   - LLM-based entity extraction
   - In-memory graph storage
   - Hybrid vector + graph search

Requirements:
- pip install mem0ai (for Mem0)
- Neo4j running (for graph features)
- OPENAI_API_KEY set
""")

    # Run simple graph demo (no extra dependencies)
    demo_simple_graph()

    # Run Mem0 demo if available
    if MEM0_AVAILABLE:
        demo_mem0()

    print("\n" + "="*60)
    print("RECOMMENDATIONS FOR YOUR MEMORY SYSTEM")
    print("="*60)
    print("""
1. START SIMPLE: Use entity extraction to build a graph alongside vectors
   - Extract entities with GPT-4o-mini (fast, cheap)
   - Store relationships in a simple data structure
   - Boost vector scores based on entity overlap

2. PRODUCTION: Adopt Mem0 for full graph capabilities
   - pip install mem0ai
   - Configure with your Qdrant + Neo4j
   - Benefits: 26% accuracy, 91% lower latency, temporal tracking

3. ADVANCED: Use Graphiti for real-time knowledge graphs
   - Better for frequently changing data
   - Temporal awareness built-in
   - Near-constant latency at any scale

KEY INSIGHT: Graph memory captures entity relationships that
pure vector search misses. Example:
- Query: "What does Anthropic recommend?"
- Vector: Might miss "Voyage AI" if query doesn't mention embeddings
- Graph: Finds Anthropic -> recommends -> Voyage AI relationship
""")


if __name__ == "__main__":
    main()
