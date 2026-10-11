"""
Unit tests for SupplyPilot project parsing, schema validation,
agentic retrieval tokenization, and Streamlit configuration readiness.
"""

import pytest
from pathlib import Path
from career_ai.knowledge.parser import MarkdownParser
from career_ai.knowledge.chunker import SemanticChunker
from career_ai.knowledge.schemas import ProjectSchema, CANONICAL_DOMAINS
from career_ai.retrieval.bm25 import tokenize, BM25Retriever
from career_ai.core.config import settings

def test_parse_supply_pilot_project():
    file_path = Path("knowledge/projects/supply-pilot.md")
    assert file_path.exists(), "supply-pilot.md must exist in canonical projects"

    metadata, body = MarkdownParser.parse_file(file_path)
    assert isinstance(metadata, dict)

    # Validate against strict ProjectSchema
    project = ProjectSchema(**metadata)
    assert "SupplyPilot" in project.project_name
    assert any("LangGraph" in t for t in project.technologies)
    assert any("FastAPI" in t for t in project.technologies)
    assert any("Next.js" in t for t in project.technologies)
    assert len(body) > 1000

def test_supply_pilot_metrics_and_domains():
    file_path = Path("knowledge/projects/supply-pilot.md")
    metadata, body = MarkdownParser.parse_file(file_path)
    project = ProjectSchema(**metadata)

    # Verify metrics
    metrics_str = " ".join(project.metrics)
    assert "5-stage" in metrics_str
    assert "$50,000" in metrics_str
    assert "100%" in metrics_str

    # Verify domain alignment
    assert "Agentic AI & Decision Support" in CANONICAL_DOMAINS
    assert "Agentic AI & Decision Support" in project.relevant_domains

def test_semantic_chunking_supply_pilot():
    file_path = Path("knowledge/projects/supply-pilot.md")
    metadata, body = MarkdownParser.parse_file(file_path)
    chunks = SemanticChunker.chunk_project(metadata, body, file_path)

    assert len(chunks) >= 8, f"Expected at least 8 chunks, got {len(chunks)}"

    chunk_ids = [c.id for c in chunks]
    assert any("overview" in cid for cid in chunk_ids)
    assert any("architecture" in cid for cid in chunk_ids)
    assert any("technologies" in cid for cid in chunk_ids)
    assert any("contributions" in cid for cid in chunk_ids)

    # Check for core axioms and mechanisms in chunk text
    all_chunk_text = " ".join([c.text for c in chunks])
    assert "deterministic" in all_chunk_text.lower()
    assert "langgraph" in all_chunk_text.lower()
    assert "cascade" in all_chunk_text.lower()

def test_bm25_agentic_tokenization():
    tokens = tokenize("LangGraph agentic SOP RAG with 21 CFR Part 11 and HITL sign-off")
    assert "langgraph" in tokens
    assert "agent" in tokens
    assert "sop" in tokens
    assert "hitl" in tokens
    assert "cfr" in tokens
    assert "21cfr11" in tokens

def test_streamlit_config_and_properties():
    # Verify backward-compatible property aliases
    assert hasattr(settings, "llm_base_url")
    assert hasattr(settings, "llm_model")
    assert hasattr(settings, "bm25_top_k")
    assert hasattr(settings, "vector_top_k")
    assert hasattr(settings, "qdrant_path")

    # Verify paths exist
    assert settings.knowledge_dir.exists()
    assert settings.output_dir.exists()

    # Verify root streamlit entry point exists
    root_app = Path("streamlit_app.py")
    assert root_app.exists()
    assert root_app.is_file()
