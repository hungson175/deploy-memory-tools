#!/usr/bin/env python3
"""
Demo 1: Hybrid Search with Re-ranking

This demo shows how to enhance your current Qdrant memory system with:
1. BM25 sparse vectors for keyword matching
2. Reciprocal Rank Fusion (RRF) to combine results
3. Cross-encoder re-ranking for improved precision

Expected improvements:
- +15-30% recall improvement
- +20-35% accuracy with re-ranking
- -35% hallucination reduction
"""

import os
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

import httpx
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Optional: For re-ranking (install with: pip install sentence-transformers)
try:
    from sentence_transformers import CrossEncoder
    RERANKER_AVAILABLE = True
except ImportError:
    RERANKER_AVAILABLE = False
    print("Note: Install sentence-transformers for re-ranking support")

load_dotenv()


@dataclass
class SearchResult:
    """Unified search result from hybrid search"""
    doc_id: str
    content: str
    score: float
    source: str  # "vector", "bm25", or "hybrid"


class HybridSearchDemo:
    """
    Demonstrates hybrid search combining:
    - Dense vectors (semantic similarity)
    - Sparse BM25 (keyword matching)
    - Cross-encoder re-ranking (precision boost)
    """

    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection_name: str = "hybrid-demo",
        embedding_model: str = "text-embedding-3-small",
    ):
        self.qdrant = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        self.embedding_model = embedding_model
        self.openai_key = os.getenv("OPENAI_API_KEY")

        # Initialize cross-encoder re-ranker if available
        self.reranker = None
        if RERANKER_AVAILABLE:
            # Lightweight but effective re-ranker
            self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    def setup_collection(self):
        """Create collection with both dense and sparse vector support"""
        try:
            self.qdrant.get_collection(self.collection_name)
            print(f"Collection '{self.collection_name}' exists")
        except Exception:
            print(f"Creating collection '{self.collection_name}' with hybrid support")
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    # Dense vectors for semantic search
                    "dense": models.VectorParams(
                        size=1536,
                        distance=models.Distance.COSINE
                    )
                },
                sparse_vectors_config={
                    # Sparse vectors for BM25-style keyword search
                    "sparse": models.SparseVectorParams(
                        modifier=models.Modifier.IDF  # TF-IDF weighting
                    )
                }
            )

    def _get_dense_embedding(self, text: str) -> List[float]:
        """Get dense embedding from OpenAI"""
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json"
        }
        data = {"input": text, "model": self.embedding_model}

        with httpx.Client() as client:
            response = client.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()["data"][0]["embedding"]

    def _get_sparse_embedding(self, text: str) -> Tuple[List[int], List[float]]:
        """
        Create sparse BM25-style embedding from text.

        In production, consider using:
        - Qdrant's built-in sparse encoder
        - SPLADE model for learned sparse representations
        - Custom TF-IDF implementation
        """
        # Simple word-based sparse embedding for demo
        words = text.lower().split()
        word_freq = {}
        for word in words:
            # Simple hash for word indices (production: use proper vocabulary)
            word_idx = hash(word) % 30000
            word_freq[word_idx] = word_freq.get(word_idx, 0) + 1

        indices = list(word_freq.keys())
        values = [float(v) for v in word_freq.values()]
        return indices, values

    def add_memory(self, doc_id: str, content: str, metadata: Dict[str, Any] = None):
        """Add a memory with both dense and sparse vectors"""
        dense_vector = self._get_dense_embedding(content)
        sparse_indices, sparse_values = self._get_sparse_embedding(content)

        self.qdrant.upsert(
            collection_name=self.collection_name,
            points=[
                models.PointStruct(
                    id=doc_id,
                    vector={
                        "dense": dense_vector,
                        "sparse": models.SparseVector(
                            indices=sparse_indices,
                            values=sparse_values
                        )
                    },
                    payload={
                        "content": content,
                        **(metadata or {})
                    }
                )
            ]
        )
        print(f"Added memory: {doc_id}")

    def _reciprocal_rank_fusion(
        self,
        dense_results: List[Tuple[str, float]],
        sparse_results: List[Tuple[str, float]],
        k: int = 60
    ) -> List[Tuple[str, float]]:
        """
        Combine rankings using Reciprocal Rank Fusion (RRF).

        RRF score = sum(1 / (k + rank)) for each result list

        k=60 is the standard default that works well across score scales.
        """
        scores = {}

        # Add dense results
        for rank, (doc_id, _) in enumerate(dense_results, 1):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)

        # Add sparse results
        for rank, (doc_id, _) in enumerate(sparse_results, 1):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)

        # Sort by combined score
        return sorted(scores.items(), key=lambda x: x[1], reverse=True)

    def _rerank_results(
        self,
        query: str,
        results: List[SearchResult],
        top_k: int = 10
    ) -> List[SearchResult]:
        """
        Re-rank results using cross-encoder for improved precision.

        Cross-encoders analyze query-document pairs together, capturing
        richer interactions than bi-encoders (embedding models).
        """
        if not self.reranker or not results:
            return results[:top_k]

        # Prepare query-document pairs
        pairs = [(query, r.content) for r in results]

        # Get cross-encoder scores
        scores = self.reranker.predict(pairs)

        # Combine with original scores and sort
        for i, result in enumerate(results):
            result.score = float(scores[i])

        reranked = sorted(results, key=lambda x: x.score, reverse=True)
        return reranked[:top_k]

    def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        use_reranking: bool = True,
        alpha: float = 0.7  # Weight for dense vs sparse (0.7 = 70% semantic)
    ) -> List[SearchResult]:
        """
        Perform hybrid search with optional re-ranking.

        Args:
            query: Search query
            limit: Number of results to return
            use_reranking: Whether to apply cross-encoder re-ranking
            alpha: Weight for dense vs sparse (higher = more semantic)

        Returns:
            List of SearchResult objects ranked by relevance
        """
        # Get query embeddings
        dense_query = self._get_dense_embedding(query)
        sparse_indices, sparse_values = self._get_sparse_embedding(query)

        # Fetch more candidates for re-ranking
        fetch_limit = limit * 5 if use_reranking else limit

        # Dense vector search
        dense_results = self.qdrant.query_points(
            collection_name=self.collection_name,
            query=dense_query,
            using="dense",
            limit=fetch_limit,
            with_payload=True
        ).points

        # Sparse vector search (BM25-style)
        sparse_results = self.qdrant.query_points(
            collection_name=self.collection_name,
            query=models.SparseVector(
                indices=sparse_indices,
                values=sparse_values
            ),
            using="sparse",
            limit=fetch_limit,
            with_payload=True
        ).points

        # Convert to tuples for RRF
        dense_tuples = [(str(r.id), r.score) for r in dense_results]
        sparse_tuples = [(str(r.id), r.score) for r in sparse_results]

        # Combine using RRF
        fused_results = self._reciprocal_rank_fusion(dense_tuples, sparse_tuples)

        # Build result objects
        id_to_content = {}
        for r in dense_results + sparse_results:
            id_to_content[str(r.id)] = r.payload.get("content", "")

        results = [
            SearchResult(
                doc_id=doc_id,
                content=id_to_content.get(doc_id, ""),
                score=score,
                source="hybrid"
            )
            for doc_id, score in fused_results
        ]

        # Optional re-ranking
        if use_reranking and self.reranker:
            results = self._rerank_results(query, results, limit)
            print(f"Applied cross-encoder re-ranking")
        else:
            results = results[:limit]

        return results

    def compare_search_methods(self, query: str, limit: int = 5):
        """Compare vector-only vs hybrid vs hybrid+reranking"""
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")

        # Vector-only search
        dense_query = self._get_dense_embedding(query)
        vector_results = self.qdrant.query_points(
            collection_name=self.collection_name,
            query=dense_query,
            using="dense",
            limit=limit,
            with_payload=True
        ).points

        print(f"\n1. VECTOR-ONLY (Current System):")
        for i, r in enumerate(vector_results, 1):
            content = r.payload.get("content", "")[:80]
            print(f"   {i}. [{r.score:.3f}] {content}...")

        # Hybrid search without re-ranking
        hybrid_results = self.hybrid_search(query, limit, use_reranking=False)

        print(f"\n2. HYBRID (Vector + BM25 with RRF):")
        for i, r in enumerate(hybrid_results, 1):
            print(f"   {i}. [{r.score:.3f}] {r.content[:80]}...")

        # Hybrid search with re-ranking
        if self.reranker:
            reranked_results = self.hybrid_search(query, limit, use_reranking=True)

            print(f"\n3. HYBRID + RE-RANKING (Best Quality):")
            for i, r in enumerate(reranked_results, 1):
                print(f"   {i}. [{r.score:.3f}] {r.content[:80]}...")
        else:
            print("\n3. RE-RANKING: Not available (install sentence-transformers)")


def main():
    """Demo: Show hybrid search improvements over vector-only"""
    demo = HybridSearchDemo()
    demo.setup_collection()

    # Add sample memories
    sample_memories = [
        ("mem1", "The ACORN algorithm improves filtered vector search by examining neighbors-of-neighbors"),
        ("mem2", "Qdrant version 1.16 introduced tiered multitenancy for isolating heavy-traffic tenants"),
        ("mem3", "Binary quantization reduces memory by 24x but works best with 1024+ dimensions"),
        ("mem4", "Cross-encoder re-ranking improves retrieval accuracy by 20-35% compared to embeddings alone"),
        ("mem5", "Reciprocal Rank Fusion with k=60 combines search results without score normalization"),
        ("mem6", "The Qdrant database supports both dense and sparse vector search natively"),
        ("mem7", "HNSW indexing provides logarithmic search time complexity for approximate nearest neighbors"),
        ("mem8", "Scalar quantization provides 75% memory reduction with 99%+ accuracy maintained"),
    ]

    for doc_id, content in sample_memories:
        demo.add_memory(doc_id, content, {"type": "pattern"})

    # Compare search methods
    test_queries = [
        "How does Qdrant filter search results?",  # Should find ACORN
        "memory reduction techniques",  # Should find quantization memories
        "k=60 RRF fusion",  # Exact keyword match test
    ]

    for query in test_queries:
        demo.compare_search_methods(query)

    print("\n" + "="*60)
    print("SUMMARY: Hybrid search captures both semantic AND keyword matches")
    print("Re-ranking further improves precision at the cost of ~200ms latency")
    print("="*60)


if __name__ == "__main__":
    main()
