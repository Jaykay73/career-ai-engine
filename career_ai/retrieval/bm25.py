"""
BM25 Lexical Retrieval implementation using rank_bm25.
Indexes canonical knowledge chunks and produces lexical rankings.
"""

from typing import List, Tuple, Dict, Any, Optional
import re
import pickle
from pathlib import Path
from rank_bm25 import BM25Okapi
from career_ai.knowledge.schemas import EvidenceChunk
from career_ai.core.logging import get_logger

logger = get_logger("bm25")

TECHNICAL_TOKEN_REGEX = re.compile(r"[a-zA-Z0-9]+(?:[-_][a-zA-Z0-9]+)*|c\+\+|[a-zA-Z0-9]+")

def tokenize(text: str) -> List[str]:
    """
    Tokenizes text by lowercasing and extracting alphanumeric and technical terms,
    preserving compound identifiers (e.g., yolo-v26n, tflite, c++, mpu6050).
    """
    raw_tokens = [t.lower() for t in TECHNICAL_TOKEN_REGEX.findall(text)]
    expanded: List[str] = []
    for token in raw_tokens:
        expanded.append(token)
        # If token has hyphens or underscores, also preserve individual subparts
        if "-" in token or "_" in token:
            for subpart in re.split(r"[-_]", token):
                if subpart and subpart != token:
                    expanded.append(subpart)
    return expanded

class BM25Retriever:
    """Manages an in-memory BM25 index of EvidenceChunks with optional persistence."""

    def __init__(self, persistence_path: Optional[Path] = None):
        self.persistence_path = persistence_path
        self.chunks: List[EvidenceChunk] = []
        self.tokenized_corpus: List[List[str]] = []
        self.bm25: Optional[BM25Okapi] = None

    def build_index(self, chunks: List[EvidenceChunk]) -> None:
        """Builds BM25 index from a list of EvidenceChunk objects, including rich metadata."""
        if not chunks:
            logger.warning("Attempted to build BM25 index with empty chunk list.")
            self.chunks = []
            self.tokenized_corpus = []
            self.bm25 = None
            return

        self.chunks = list(chunks)
        # Tokenize each chunk text including title, section, and metadata fields for richer lexical match
        corpus_texts: List[str] = []
        for chunk in self.chunks:
            meta_parts: List[str] = []
            if chunk.metadata:
                for k in ("technologies", "models", "frameworks", "keywords", "relevant_domains", "infrastructure"):
                    val = chunk.metadata.get(k)
                    if isinstance(val, list):
                        meta_parts.extend(str(item) for item in val)
                    elif isinstance(val, str):
                        meta_parts.append(val)
            meta_str = " ".join(meta_parts)
            corpus_texts.append(f"{chunk.title} {chunk.section} {meta_str} {chunk.text}")

        self.tokenized_corpus = [
            tokenize(txt) for txt in corpus_texts
        ]
        self.bm25 = BM25Okapi(self.tokenized_corpus)
        logger.info("BM25 index built with %d documents.", len(self.chunks))

        if self.persistence_path:
            self.save()

    def search(self, query: str, top_k: int = 20) -> List[Tuple[EvidenceChunk, float, int]]:
        """
        Queries BM25 index.
        Returns list of tuples: (chunk, bm25_score, rank) where rank is 1-indexed.
        """
        if not self.bm25 or not self.chunks:
            logger.warning("BM25 index is empty. Returning 0 results.")
            return []

        tokens = tokenize(query)
        if not tokens:
            return []

        scores = self.bm25.get_scores(tokens)
        # Pair each chunk with its score and index
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        results: List[Tuple[EvidenceChunk, float, int]] = []
        rank = 1
        for idx in ranked_indices:
            score = float(scores[idx])
            if score <= 0.0 and rank > 5:
                # Discard zero-score non-matches after the top candidates
                break
            results.append((self.chunks[idx], score, rank))
            rank += 1
            if rank > top_k:
                break

        return results

    def save(self) -> None:
        if not self.persistence_path:
            return
        self.persistence_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.persistence_path, "wb") as f:
            pickle.dump({
                "chunks": self.chunks,
                "tokenized_corpus": self.tokenized_corpus
            }, f)
        logger.debug("BM25 index persisted to %s", self.persistence_path)

    def load(self) -> bool:
        if not self.persistence_path or not self.persistence_path.exists():
            return False
        try:
            with open(self.persistence_path, "rb") as f:
                data = pickle.load(f)
                self.chunks = data.get("chunks", [])
                self.tokenized_corpus = data.get("tokenized_corpus", [])
                if self.tokenized_corpus:
                    self.bm25 = BM25Okapi(self.tokenized_corpus)
                    logger.info("BM25 index loaded with %d documents from %s", len(self.chunks), self.persistence_path)
                    return True
        except Exception as e:
            logger.error("Failed to load BM25 index from %s: %s", self.persistence_path, e)
        return False
