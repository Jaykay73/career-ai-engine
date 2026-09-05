"""
Deterministic mathematical tests for Reciprocal Rank Fusion (RRF).
"""

import pytest
from career_ai.retrieval.rrf import compute_rrf
from career_ai.knowledge.schemas import EvidenceChunk

def test_rrf_formula_calculation():
    k = 60
    chunk_a = EvidenceChunk(id="doc_a", source_type="project", source_id="a", title="Doc A", section="sec", file_path="a.md", text="Text A")
    chunk_b = EvidenceChunk(id="doc_b", source_type="project", source_id="b", title="Doc B", section="sec", file_path="b.md", text="Text B")
    chunk_c = EvidenceChunk(id="doc_c", source_type="project", source_id="c", title="Doc C", section="sec", file_path="c.md", text="Text C")

    # Document A is rank 1 in BM25, rank 2 in Vector
    # Document B is rank 2 in BM25, rank 1 in Vector
    # Document C is rank 3 in BM25, not in Vector
    bm25_list = [
        (chunk_a, 10.0, 1),
        (chunk_b, 8.0, 2),
        (chunk_c, 5.0, 3),
    ]
    vector_list = [
        (chunk_b, 0.95, 1),
        (chunk_a, 0.90, 2),
    ]

    fused = compute_rrf(bm25_results=bm25_list, vector_results=vector_list, k=k)

    expected_score_a = (1.0 / (k + 1)) + (1.0 / (k + 2))
    expected_score_b = (1.0 / (k + 2)) + (1.0 / (k + 1))
    expected_score_c = 1.0 / (k + 3)

    fused_dict = {item.chunk.id: item for item in fused}

    assert pytest.approx(fused_dict["doc_a"].rrf_score, rel=1e-5) == expected_score_a
    assert pytest.approx(fused_dict["doc_b"].rrf_score, rel=1e-5) == expected_score_b
    assert pytest.approx(fused_dict["doc_c"].rrf_score, rel=1e-5) == expected_score_c

    # A and B have equal combined scores, both must be higher than C
    assert fused_dict["doc_a"].rrf_score > fused_dict["doc_c"].rrf_score
    assert fused_dict["doc_b"].rrf_score > fused_dict["doc_c"].rrf_score

def test_rrf_empty_lists():
    fused = compute_rrf(bm25_results=[], vector_results=[], k=60)
    assert fused == []

def test_rrf_single_source():
    k = 60
    chunk_x = EvidenceChunk(id="x", source_type="project", source_id="x", title="Doc X", section="sec", file_path="x.md", text="Text X")
    bm25_list = [(chunk_x, 5.0, 1)]
    fused = compute_rrf(bm25_results=bm25_list, vector_results=[], k=k)
    assert len(fused) == 1
    assert pytest.approx(fused[0].rrf_score, rel=1e-5) == (1.0 / (k + 1))
