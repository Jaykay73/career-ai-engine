"""
Reciprocal Rank Fusion (RRF) implementation.
Fuses multiple ranked lists (BM25 lexical ranking and dense vector ranking)
into a single, robust evidence ranking with explicit provenance.
"""

from typing import List, Dict, Tuple, Optional, Any
from pydantic import BaseModel, Field
from career_ai.knowledge.schemas import EvidenceChunk
from career_ai.core.config import settings
from career_ai.core.logging import get_logger

logger = get_logger("rrf")

class RankedEvidence(BaseModel):
    chunk: EvidenceChunk
    rrf_score: float
    rrf_rank: int
    bm25_rank: Optional[int] = None
    bm25_score: Optional[float] = None
    vector_rank: Optional[int] = None
    vector_score: Optional[float] = None

    def to_debug_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk.id,
            "title": self.chunk.title,
            "source_type": self.chunk.source_type,
            "source_id": self.chunk.source_id,
            "section": self.chunk.section,
            "file_path": self.chunk.file_path,
            "text": self.chunk.text,
            "bm25_rank": self.bm25_rank,
            "bm25_score": round(self.bm25_score, 4) if self.bm25_score is not None else None,
            "vector_rank": self.vector_rank,
            "vector_score": round(self.vector_score, 4) if self.vector_score is not None else None,
            "rrf_score": round(self.rrf_score, 6),
            "rrf_rank": self.rrf_rank,
        }

def compute_rrf(
    bm25_results: List[Tuple[EvidenceChunk, float, int]],
    vector_results: List[Tuple[EvidenceChunk, float, int]],
    k: Optional[int] = None,
    top_k_rrf: Optional[int] = None
) -> List[RankedEvidence]:
    """
    Combines BM25 and vector results using Reciprocal Rank Fusion:
    RRF(d) = sum( 1 / (k + rank_i(d)) ) for each ranking system where d appears.
    
    Ranks are 1-indexed.
    """
    k_val = k if k is not None else settings.rrf_k
    top_n = top_k_rrf if top_k_rrf is not None else settings.top_k_rrf

    chunk_map: Dict[str, EvidenceChunk] = {}
    rrf_scores: Dict[str, float] = {}
    bm25_info: Dict[str, Tuple[int, float]] = {}
    vector_info: Dict[str, Tuple[int, float]] = {}

    # Process BM25 rankings
    for chunk, score, rank in bm25_results:
        cid = chunk.id
        chunk_map[cid] = chunk
        bm25_info[cid] = (rank, score)
        contribution = 1.0 / (k_val + rank)
        rrf_scores[cid] = rrf_scores.get(cid, 0.0) + contribution

    # Process Vector rankings
    for chunk, score, rank in vector_results:
        cid = chunk.id
        chunk_map[cid] = chunk
        vector_info[cid] = (rank, score)
        contribution = 1.0 / (k_val + rank)
        rrf_scores[cid] = rrf_scores.get(cid, 0.0) + contribution

    # Sort candidates by descending RRF score
    sorted_chunk_ids = sorted(
        rrf_scores.keys(),
        key=lambda cid: rrf_scores[cid],
        reverse=True
    )

    ranked_results: List[RankedEvidence] = []
    for rrf_rank, cid in enumerate(sorted_chunk_ids, start=1):
        chunk = chunk_map[cid]
        score = rrf_scores[cid]
        
        b_rank, b_score = bm25_info.get(cid, (None, None))
        v_rank, v_score = vector_info.get(cid, (None, None))

        ranked_results.append(RankedEvidence(
            chunk=chunk,
            rrf_score=score,
            rrf_rank=rrf_rank,
            bm25_rank=b_rank,
            bm25_score=b_score,
            vector_rank=v_rank,
            vector_score=v_score
        ))

        if len(ranked_results) >= top_n:
            break

    return ranked_results
