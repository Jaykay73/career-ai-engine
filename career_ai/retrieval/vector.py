"""
Vector Retrieval implementation using SentenceTransformers and Qdrant.
Supports local embedded disk storage (no Docker required) and remote Qdrant.
"""

from typing import List, Tuple, Dict, Any, Optional
import os
import uuid
import warnings
import numpy as np
from pathlib import Path

# Clean terminal output for local HF Hub caching
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
warnings.filterwarnings("ignore", message=".*embeddings.position_ids.*")

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    UpdateStatus
)
from sentence_transformers import SentenceTransformer
from career_ai.knowledge.schemas import EvidenceChunk
from career_ai.core.config import settings
from career_ai.core.logging import get_logger
from career_ai.core.exceptions import EmbeddingError, RetrievalError

logger = get_logger("vector")

# Namespace UUID for deterministic Qdrant point IDs based on chunk id string
CAREER_AI_NAMESPACE = uuid.uuid5(uuid.NAMESPACE_DNS, "career-ai.local")

def chunk_id_to_uuid(chunk_id: str) -> str:
    """Generates a deterministic UUID string from an arbitrary chunk ID string."""
    return str(uuid.uuid5(CAREER_AI_NAMESPACE, chunk_id))

class EmbeddingEngine:
    """Encapsulates SentenceTransformer model for dense embedding generation."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.embedding_model
        self._model: Optional[SentenceTransformer] = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info("Loading SentenceTransformer model: %s", self.model_name)
            try:
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                raise EmbeddingError(f"Failed to load embedding model '{self.model_name}': {e}")
        return self._model

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Generates L2-normalized embeddings for a list of texts."""
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)
        try:
            embeddings = self.model.encode(
                texts,
                show_progress_bar=False,
                normalize_embeddings=True,
                convert_to_numpy=True
            )
            return embeddings.astype(np.float32)
        except Exception as e:
            raise EmbeddingError(f"Failed to embed texts: {e}")

    def embed_query(self, query: str) -> List[float]:
        """Embeds a single query string, returning normalized float vector."""
        if not query.strip():
            return [0.0] * self.dimension
        try:
            emb = self.model.encode(
                query,
                normalize_embeddings=True,
                convert_to_numpy=True
            )
            return emb.astype(float).tolist()
        except Exception as e:
            raise EmbeddingError(f"Failed to embed query: {e}")

class QdrantVectorStore:
    """Manages dense vector indexing and cosine similarity search in Qdrant."""

    def __init__(
        self,
        collection_name: Optional[str] = None,
        storage_path: Optional[Path] = None,
        host: Optional[str] = None,
        port: Optional[int] = None
    ):
        self.collection_name = collection_name or settings.qdrant_collection
        self.host = host if host is not None else settings.qdrant_host
        self.port = port if port is not None else settings.qdrant_port
        self.storage_path = storage_path or settings.qdrant_storage_path

        self._client: Optional[QdrantClient] = None

    @property
    def client(self) -> QdrantClient:
        if self._client is None:
            if self.host:
                logger.info("Connecting to remote Qdrant at %s:%s", self.host, self.port or 6333)
                self._client = QdrantClient(host=self.host, port=self.port or 6333)
            else:
                # Embedded local disk mode
                self.storage_path.mkdir(parents=True, exist_ok=True)
                logger.info("Initializing embedded local Qdrant at %s", self.storage_path)
                self._client = QdrantClient(path=str(self.storage_path))
        return self._client

    def ensure_collection(self, vector_dim: int, recreate: bool = False) -> None:
        """Ensures the target collection exists with Cosine distance metric."""
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            
            if exists and recreate:
                logger.info("Recreating Qdrant collection '%s'", self.collection_name)
                self.client.delete_collection(self.collection_name)
                exists = False

            if not exists:
                logger.info("Creating Qdrant collection '%s' with dim=%d", self.collection_name, vector_dim)
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE)
                )
        except Exception as e:
            raise RetrievalError(f"Failed to ensure Qdrant collection '{self.collection_name}': {e}")

    def upsert_chunks(self, chunks: List[EvidenceChunk], embeddings: np.ndarray) -> None:
        """Upserts chunks and their corresponding embeddings into Qdrant."""
        if not chunks:
            return
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match.")

        dim = embeddings.shape[1]
        self.ensure_collection(vector_dim=dim, recreate=False)

        points = []
        for chunk, vector in zip(chunks, embeddings):
            point_id = chunk_id_to_uuid(chunk.id)
            payload = {
                "chunk_id": chunk.id,
                "source_type": chunk.source_type,
                "source_id": chunk.source_id,
                "title": chunk.title,
                "section": chunk.section,
                "file_path": chunk.file_path,
                "text": chunk.text,
                "metadata": chunk.metadata
            }
            points.append(PointStruct(id=point_id, vector=vector.tolist(), payload=payload))

        # Batch upsert in chunks of 100
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            res = self.client.upsert(collection_name=self.collection_name, points=batch)
            if res.status != UpdateStatus.COMPLETED:
                logger.warning("Batch upsert completed with status: %s", res.status)

        logger.info("Upserted %d points into Qdrant collection '%s'", len(points), self.collection_name)

    def search(self, query_vector: List[float], top_k: int = 20) -> List[Tuple[EvidenceChunk, float, int]]:
        """
        Performs cosine similarity search against Qdrant collection.
        Returns list of (EvidenceChunk, cosine_score, rank) tuples (1-indexed rank).
        """
        try:
            if hasattr(self.client, "query_points"):
                response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_vector,
                    limit=top_k
                )
                results = response.points
            else:
                results = self.client.search(
                    collection_name=self.collection_name,
                    query_vector=query_vector,
                    limit=top_k
                )
        except Exception as e:
            logger.error("Qdrant search error: %s", e)
            return []

        scored_chunks: List[Tuple[EvidenceChunk, float, int]] = []
        for rank, hit in enumerate(results, start=1):
            p = hit.payload or {}
            chunk = EvidenceChunk(
                id=p.get("chunk_id", str(hit.id)),
                source_type=p.get("source_type", "unknown"),
                source_id=p.get("source_id", "unknown"),
                title=p.get("title", ""),
                section=p.get("section", ""),
                file_path=p.get("file_path", ""),
                text=p.get("text", ""),
                metadata=p.get("metadata", {})
            )
            scored_chunks.append((chunk, float(hit.score), rank))

        return scored_chunks

# Global instances
embedding_engine = EmbeddingEngine()
vector_store = QdrantVectorStore()
