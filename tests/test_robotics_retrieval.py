"""
Unit tests for Robotics and Edge AI BM25 and Hybrid Retrieval Ranking.
"""

import pytest
from pathlib import Path
from career_ai.retrieval.bm25 import BM25Retriever
from career_ai.retrieval.rrf import compute_rrf
from career_ai.knowledge.parser import MarkdownParser
from career_ai.knowledge.chunker import SemanticChunker

@pytest.fixture(scope="module")
def mower_chunks():
    file_path = Path("knowledge/projects/autonomous-lawn-mower.md")
    meta, body = MarkdownParser.parse_file(file_path)
    return SemanticChunker.chunk_project(meta, body, file_path)

def test_bm25_retrieval_robotics_query(mower_chunks):
    retriever = BM25Retriever()
    retriever.build_index(mower_chunks)

    # 1. Query for fail-safe safety watchdog
    results = retriever.search("ATmega microcontroller watchdog heartbeat 500 ms", top_k=5)
    assert len(results) > 0
    top_chunk, score, rank = results[0]
    assert score > 0.0
    assert "lawn-mower" in top_chunk.source_id
    assert any(term in top_chunk.text.lower() for term in ["watchdog", "atmega", "heartbeat", "safety"])

def test_bm25_retrieval_edge_cv(mower_chunks):
    retriever = BM25Retriever()
    retriever.build_index(mower_chunks)

    # 2. Query for edge computer vision and quantization
    results = retriever.search("YOLOv26n INT8 TFLite edge Raspberry Pi", top_k=5)
    assert len(results) > 0
    top_chunk, score, rank = results[0]
    assert score > 0.0
    assert any(term in top_chunk.text.lower() for term in ["yolo", "tflite", "int8", "raspberry"])

def test_sensor_fusion_query(mower_chunks):
    retriever = BM25Retriever()
    retriever.build_index(mower_chunks)

    # 3. Query for IMU and ultrasonic sensor fusion
    results = retriever.search("MPU6050 IMU ultrasonic sensors obstacle avoidance", top_k=5)
    assert len(results) > 0
    top_chunk, score, rank = results[0]
    assert score > 0.0
    assert any(term in top_chunk.text.lower() for term in ["mpu6050", "ultrasonic", "obstacle", "sensors"])

def test_rrf_scoring_with_mower(mower_chunks):
    # Mock BM25 and Vector results
    top_chunk = mower_chunks[0]
    other_chunk = mower_chunks[1]

    bm25_res = [(top_chunk, 12.5, 1), (other_chunk, 8.2, 2)]
    vec_res = [(top_chunk, 0.92, 1), (other_chunk, 0.85, 2)]

    fused = compute_rrf(bm25_results=bm25_res, vector_results=vec_res, k=60)
    assert len(fused) == 2
    assert fused[0].chunk.id == top_chunk.id
    assert fused[0].rrf_rank == 1
    assert fused[0].rrf_score > fused[1].rrf_score
