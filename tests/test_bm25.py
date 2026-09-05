"""
Unit tests for BM25 Okapi lexical retrieval.
"""

import pytest
from career_ai.retrieval.bm25 import BM25Retriever, tokenize
from career_ai.knowledge.schemas import EvidenceChunk

def test_bm25_tokenize():
    tokens = tokenize("FastAPI & Docker for AI/ML Pipelines 100%!")
    assert "fastapi" in tokens
    assert "docker" in tokens
    assert "ai" in tokens
    assert "ml" in tokens
    assert "pipelines" in tokens

def test_bm25_tokenize_and_search():
    retriever = BM25Retriever()
    
    chunks = [
        EvidenceChunk(
            id="chunk_1",
            source_type="project",
            source_id="brain-tumor",
            title="Brain Tumor MRI Classification",
            section="Overview",
            file_path="knowledge/projects/brain-tumor.md",
            text="Built deep learning CNN for brain tumor MRI segmentation using PyTorch and Medical AI pipelines achieving 96.2% ROC-AUC."
        ),
        EvidenceChunk(
            id="chunk_2",
            source_type="project",
            source_id="bitcheck",
            title="BitCheck",
            section="Overview",
            file_path="knowledge/projects/bitcheck.md",
            text="Real-time cryptocurrency analytics using FastAPI, Docker, and Kafka streaming architecture."
        ),
        EvidenceChunk(
            id="chunk_3",
            source_type="experience",
            source_id="queryfier",
            title="Queryfier LLC",
            section="Overview",
            file_path="knowledge/experience/queryfier.md",
            text="Software engineering internship focused on full-stack web development and REST APIs."
        ),
    ]

    retriever.build_index(chunks)
    assert len(retriever.chunks) == 3

    # Search for MRI PyTorch
    results = retriever.search("brain tumor MRI with PyTorch", top_k=2)
    assert len(results) > 0
    top_chunk, score, rank = results[0]
    assert top_chunk.id == "chunk_1"
    assert score > 0
    assert rank == 1

    # Search for crypto FastAPI
    results_crypto = retriever.search("cryptocurrency FastAPI Docker", top_k=2)
    assert len(results_crypto) > 0
    top_chunk_crypto, score_crypto, rank_crypto = results_crypto[0]
    assert top_chunk_crypto.id == "chunk_2"
    assert rank_crypto == 1
