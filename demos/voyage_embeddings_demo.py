#!/usr/bin/env python3
"""
Demo 2: Voyage AI Embeddings (Anthropic's Recommended Partner)

This demo shows how to switch from OpenAI text-embedding-3-small to Voyage AI,
which Anthropic officially recommends for Claude-based applications.

Expected improvements:
- +27% accuracy improvement (66.1% vs 39.2%)
- Better handling of "tricky negatives" for RAG
- Longer context window (16K vs ~8K)
- Matryoshka support for flexible dimensions

Setup:
1. Get API key from https://www.voyageai.com/
2. Set VOYAGE_API_KEY environment variable
3. pip install voyageai
"""

import os
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod

import httpx
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

load_dotenv()


@dataclass
class EmbeddingResult:
    """Result from embedding generation"""
    vector: List[float]
    model: str
    tokens_used: int
    dimensions: int


class EmbeddingProvider(ABC):
    """Abstract base for embedding providers"""

    @abstractmethod
    def embed(self, text: str) -> EmbeddingResult:
        pass

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        pass


class OpenAIEmbedding(EmbeddingProvider):
    """Current: OpenAI text-embedding-3-small"""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.dimensions = 1536

    def embed(self, text: str) -> EmbeddingResult:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {"input": text, "model": self.model}

        with httpx.Client() as client:
            response = client.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()

        return EmbeddingResult(
            vector=result["data"][0]["embedding"],
            model=self.model,
            tokens_used=result["usage"]["total_tokens"],
            dimensions=len(result["data"][0]["embedding"])
        )

    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {"input": texts, "model": self.model}

        with httpx.Client() as client:
            response = client.post(
                "https://api.openai.com/v1/embeddings",
                headers=headers,
                json=data,
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()

        tokens = result["usage"]["total_tokens"] // len(texts)
        return [
            EmbeddingResult(
                vector=item["embedding"],
                model=self.model,
                tokens_used=tokens,
                dimensions=len(item["embedding"])
            )
            for item in result["data"]
        ]


class VoyageAIEmbedding(EmbeddingProvider):
    """
    Voyage AI - Anthropic's recommended embedding partner.

    Models:
    - voyage-3-large: Best quality, 1024 dims (flex to 256/512/2048)
    - voyage-3.5-lite: Good quality, lower cost
    - voyage-code-3: Optimized for code
    - voyage-finance-2: Optimized for finance

    Key advantages:
    - Trained on "tricky negatives" for better RAG accuracy
    - 16K context window (vs OpenAI's ~8K)
    - Matryoshka support for flexible dimensions
    """

    def __init__(
        self,
        model: str = "voyage-3-large",
        output_dimension: Optional[int] = None  # Matryoshka: 256, 512, 1024, 2048
    ):
        self.model = model
        self.api_key = os.getenv("VOYAGE_API_KEY")
        self.output_dimension = output_dimension
        self.base_url = "https://api.voyageai.com/v1/embeddings"

        # Default dimensions by model
        self.default_dims = {
            "voyage-3-large": 1024,
            "voyage-3.5-lite": 1024,
            "voyage-code-3": 1024,
            "voyage-finance-2": 1024,
        }

    def embed(self, text: str) -> EmbeddingResult:
        if not self.api_key:
            raise ValueError("VOYAGE_API_KEY not set. Get one at https://www.voyageai.com/")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "input": text,
            "model": self.model,
            "input_type": "document"  # or "query" for search queries
        }

        # Optional: Matryoshka dimension reduction
        if self.output_dimension:
            data["output_dimension"] = self.output_dimension

        with httpx.Client() as client:
            response = client.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()

        embedding = result["data"][0]["embedding"]
        return EmbeddingResult(
            vector=embedding,
            model=self.model,
            tokens_used=result.get("usage", {}).get("total_tokens", 0),
            dimensions=len(embedding)
        )

    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        if not self.api_key:
            raise ValueError("VOYAGE_API_KEY not set")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "input": texts,
            "model": self.model,
            "input_type": "document"
        }

        if self.output_dimension:
            data["output_dimension"] = self.output_dimension

        with httpx.Client() as client:
            response = client.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()

        tokens = result.get("usage", {}).get("total_tokens", 0) // len(texts)
        return [
            EmbeddingResult(
                vector=item["embedding"],
                model=self.model,
                tokens_used=tokens,
                dimensions=len(item["embedding"])
            )
            for item in result["data"]
        ]


class NomicEmbedding(EmbeddingProvider):
    """
    Nomic Embed v2 - Open-source alternative (Apache 2.0).

    Run locally with:
        pip install sentence-transformers
        model = SentenceTransformer('nomic-ai/nomic-embed-text-v2-moe')

    Key advantages:
    - Free (self-hosted)
    - Only 0.55GB model size
    - MoE architecture for efficiency
    - Comparable to text-embedding-3-small
    - Matryoshka support (768→256)
    """

    def __init__(self, use_api: bool = True):
        self.use_api = use_api
        self.api_key = os.getenv("NOMIC_API_KEY")
        self.model_name = "nomic-embed-text-v2-moe"
        self.local_model = None

        if not use_api:
            try:
                from sentence_transformers import SentenceTransformer
                self.local_model = SentenceTransformer(
                    'nomic-ai/nomic-embed-text-v2-moe',
                    trust_remote_code=True
                )
            except ImportError:
                print("Install sentence-transformers for local Nomic embeddings")

    def embed(self, text: str) -> EmbeddingResult:
        if self.local_model:
            # Local inference (free!)
            vector = self.local_model.encode(text).tolist()
            return EmbeddingResult(
                vector=vector,
                model=self.model_name,
                tokens_used=0,  # Local = free
                dimensions=len(vector)
            )

        if self.use_api and self.api_key:
            # Nomic Atlas API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "texts": [text],
                "model": "nomic-embed-text-v2-moe"
            }

            with httpx.Client() as client:
                response = client.post(
                    "https://api-atlas.nomic.ai/v1/embedding/text",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                response.raise_for_status()
                result = response.json()

            return EmbeddingResult(
                vector=result["embeddings"][0],
                model=self.model_name,
                tokens_used=result.get("usage", {}).get("total_tokens", 0),
                dimensions=len(result["embeddings"][0])
            )

        raise ValueError("No Nomic API key or local model available")

    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        if self.local_model:
            vectors = self.local_model.encode(texts).tolist()
            return [
                EmbeddingResult(
                    vector=v,
                    model=self.model_name,
                    tokens_used=0,
                    dimensions=len(v)
                )
                for v in vectors
            ]
        # API batch implementation similar to single embed
        return [self.embed(text) for text in texts]


class EmbeddingBenchmark:
    """Compare embedding providers on sample queries"""

    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.qdrant = QdrantClient(url=qdrant_url)
        self.providers: Dict[str, EmbeddingProvider] = {}

    def add_provider(self, name: str, provider: EmbeddingProvider):
        self.providers[name] = provider

    def benchmark_embeddings(self, texts: List[str]):
        """Compare embedding dimensions, timing, and costs"""
        print("\n" + "="*70)
        print("EMBEDDING PROVIDER COMPARISON")
        print("="*70)

        for name, provider in self.providers.items():
            try:
                import time
                start = time.time()
                result = provider.embed(texts[0])
                elapsed = time.time() - start

                print(f"\n{name}:")
                print(f"  Model: {result.model}")
                print(f"  Dimensions: {result.dimensions}")
                print(f"  Tokens used: {result.tokens_used}")
                print(f"  Latency: {elapsed*1000:.1f}ms")
                print(f"  Sample vector[:5]: {result.vector[:5]}")
            except Exception as e:
                print(f"\n{name}: Error - {e}")

    def create_test_collection(self, name: str, dimensions: int):
        """Create a test collection for a specific dimension"""
        try:
            self.qdrant.get_collection(name)
        except Exception:
            self.qdrant.create_collection(
                collection_name=name,
                vectors_config=models.VectorParams(
                    size=dimensions,
                    distance=models.Distance.COSINE
                )
            )

    def compare_retrieval_quality(
        self,
        documents: List[str],
        queries: List[str],
        ground_truth: Dict[str, List[int]]  # query -> relevant doc indices
    ):
        """
        Compare retrieval quality across providers.

        This is a simplified benchmark. For production evaluation,
        use MTEB benchmark or domain-specific test sets.
        """
        print("\n" + "="*70)
        print("RETRIEVAL QUALITY COMPARISON")
        print("="*70)

        for name, provider in self.providers.items():
            try:
                result = provider.embed(documents[0])
                collection = f"test-{name}"
                self.create_test_collection(collection, result.dimensions)

                # Index documents
                embeddings = provider.embed_batch(documents)
                points = [
                    models.PointStruct(
                        id=i,
                        vector=emb.vector,
                        payload={"content": doc}
                    )
                    for i, (doc, emb) in enumerate(zip(documents, embeddings))
                ]
                self.qdrant.upsert(collection_name=collection, points=points)

                # Evaluate retrieval
                hits = 0
                total = 0

                for query, relevant_indices in ground_truth.items():
                    query_emb = provider.embed(query)
                    results = self.qdrant.query_points(
                        collection_name=collection,
                        query=query_emb.vector,
                        limit=3,
                        with_payload=False
                    ).points

                    retrieved_ids = [r.id for r in results]
                    for idx in relevant_indices:
                        total += 1
                        if idx in retrieved_ids:
                            hits += 1

                recall = hits / total if total > 0 else 0
                print(f"\n{name}:")
                print(f"  Recall@3: {recall:.1%}")
                print(f"  Hits: {hits}/{total}")

            except Exception as e:
                print(f"\n{name}: Error - {e}")


def main():
    """Demo: Compare embedding providers"""

    # Initialize benchmark
    benchmark = EmbeddingBenchmark()

    # Add providers
    benchmark.add_provider("OpenAI (current)", OpenAIEmbedding())

    # Voyage AI - requires VOYAGE_API_KEY
    if os.getenv("VOYAGE_API_KEY"):
        benchmark.add_provider("Voyage-3-large", VoyageAIEmbedding("voyage-3-large"))
        benchmark.add_provider("Voyage-3.5-lite", VoyageAIEmbedding("voyage-3.5-lite"))
        # With Matryoshka dimension reduction
        benchmark.add_provider(
            "Voyage-3-large (512d)",
            VoyageAIEmbedding("voyage-3-large", output_dimension=512)
        )
    else:
        print("\nNote: Set VOYAGE_API_KEY to test Voyage AI embeddings")
        print("Get your key at: https://www.voyageai.com/")

    # Sample texts for comparison
    sample_texts = [
        "The HNSW algorithm provides logarithmic search time for approximate nearest neighbors",
        "Binary quantization reduces memory usage by converting floats to single bits",
        "Cross-encoder re-ranking improves retrieval accuracy but adds latency",
        "Reciprocal Rank Fusion combines multiple search result lists effectively",
        "Contextual retrieval enriches chunks with document-level context",
    ]

    # Compare embedding characteristics
    benchmark.benchmark_embeddings(sample_texts)

    # Test retrieval quality (simple benchmark)
    documents = [
        "Vector databases store embeddings for similarity search",
        "HNSW index enables fast approximate nearest neighbor queries",
        "Binary quantization compresses vectors to reduce memory",
        "Cross-encoders analyze query-document pairs for re-ranking",
        "BM25 provides keyword-based retrieval using term frequency",
    ]

    queries_with_ground_truth = {
        "How to reduce memory usage in vector search?": [2],  # quantization
        "Fast similarity search algorithm": [1],  # HNSW
        "Improve search ranking accuracy": [3],  # cross-encoders
    }

    benchmark.compare_retrieval_quality(
        documents,
        list(queries_with_ground_truth.keys()),
        queries_with_ground_truth
    )

    # Print recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS FOR YOUR MEMORY SYSTEM")
    print("="*70)
    print("""
1. QUICK WIN: Switch to Voyage-3.5-lite
   - Higher accuracy than text-embedding-3-small
   - Similar cost
   - Drop-in replacement

2. BEST QUALITY: Voyage-3-large
   - Highest retrieval accuracy
   - 16K context window
   - Use Matryoshka (512d) to reduce storage

3. ZERO COST: Self-host Nomic Embed v2
   - Apache 2.0 license
   - Only 0.55GB model
   - Run: pip install sentence-transformers
   - Load: SentenceTransformer('nomic-ai/nomic-embed-text-v2-moe')

MIGRATION STEPS:
1. Update embedding function in server.py
2. Reindex existing memories (one-time cost)
3. Adjust vector dimensions if using Matryoshka

Note: Different embedding models create incompatible vectors.
Plan migration carefully or maintain parallel collections.
""")


if __name__ == "__main__":
    main()
