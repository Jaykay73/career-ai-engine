"""
Hybrid Retrieval Coordinator.
Executes parallel BM25 lexical and Qdrant dense vector search,
fusing the results via Reciprocal Rank Fusion (RRF).
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from career_ai.retrieval.bm25 import BM25Retriever
from career_ai.retrieval.vector import EmbeddingEngine, QdrantVectorStore, embedding_engine, vector_store
from career_ai.retrieval.rrf import compute_rrf, RankedEvidence
from career_ai.core.config import settings
from career_ai.core.logging import get_logger

logger = get_logger("hybrid")

class HybridRetriever:
    """Coordinates BM25 and dense vector search with Reciprocal Rank Fusion."""

    def __init__(
        self,
        bm25: Optional[BM25Retriever] = None,
        embedder: Optional[EmbeddingEngine] = None,
        vstore: Optional[QdrantVectorStore] = None
    ):
        self.bm25 = bm25 or BM25Retriever(persistence_path=settings.data_dir / "bm25_index.pkl")
        self.embedder = embedder or embedding_engine
        self.vstore = vstore or vector_store

        # Try to load existing BM25 index on initialization
        if not self.bm25.bm25:
            self.bm25.load()

    def search(
        self,
        query: str,
        top_k_bm25: Optional[int] = None,
        top_k_vector: Optional[int] = None,
        top_k_rrf: Optional[int] = None,
        source_type_filter: Optional[str] = None
    ) -> List[RankedEvidence]:
        """
        Executes hybrid retrieval:
        1. BM25 lexical search for query
        2. SentenceTransformers dense query embedding + Qdrant cosine search
        3. Reciprocal Rank Fusion
        4. Optional filtering by source_type (e.g. 'project', 'experience')
        """
        k_bm25 = top_k_bm25 or settings.top_k_bm25
        k_vec = top_k_vector or settings.top_k_vector
        k_rrf = top_k_rrf or settings.top_k_rrf

        # 1. Lexical BM25
        bm25_hits = self.bm25.search(query=query, top_k=k_bm25)

        # 2. Dense Vector Search
        query_vector = self.embedder.embed_query(query)
        vector_hits = self.vstore.search(query_vector=query_vector, top_k=k_vec)

        # 3. Fuse via RRF
        fused = compute_rrf(
            bm25_results=bm25_hits,
            vector_results=vector_hits,
            k=settings.rrf_k,
            top_k_rrf=k_rrf * 2 if source_type_filter else k_rrf
        )

        # 4. Optional source_type filter
        if source_type_filter:
            filtered = [item for item in fused if item.chunk.source_type == source_type_filter]
            return filtered[:k_rrf]

        return fused

    def hybrid_search(self, query: str) -> List[Dict[str, Any]]:
        """Debug helper returning serializable dict of ranked evidence."""
        results = self.search(query)
        return [r.to_debug_dict() for r in results]

# Global singleton
hybrid_retriever = HybridRetriever()
