"""
Unit tests for Autonomous Intelligent Lawn Mower project parsing,
schema validation, and semantic chunking.
"""

import pytest
from pathlib import Path
from career_ai.knowledge.parser import MarkdownParser
from career_ai.knowledge.chunker import SemanticChunker
from career_ai.knowledge.schemas import ProjectSchema

def test_parse_autonomous_lawn_mower_file():
    file_path = Path("knowledge/projects/autonomous-lawn-mower.md")
    assert file_path.exists(), "autonomous-lawn-mower.md must exist in canonical projects"

    metadata, body = MarkdownParser.parse_file(file_path)
    assert isinstance(metadata, dict)
    
    # Validate against strict ProjectSchema
    project = ProjectSchema(**metadata)
    assert "Lawn Mowers" in project.project_name
    assert "YOLOv26n" in project.models or any("YOLOv26n" in m for m in project.models)
    assert any("Raspberry Pi" in t for t in project.technologies)
    assert any("ATmega" in t for t in project.technologies)
    assert any("MPU6050" in t for t in project.technologies)
    assert len(body) > 1000

def test_semantic_chunking_lawn_mower():
    file_path = Path("knowledge/projects/autonomous-lawn-mower.md")
    metadata, body = MarkdownParser.parse_file(file_path)
    chunks = SemanticChunker.chunk_project(metadata, body, file_path)

    assert len(chunks) >= 10, f"Expected at least 10 chunks, got {len(chunks)}"

    chunk_ids = [c.id for c in chunks]
    assert any("overview" in cid for cid in chunk_ids)
    assert any("architecture" in cid for cid in chunk_ids)
    assert any("technologies" in cid for cid in chunk_ids)
    assert any("contributions" in cid for cid in chunk_ids)

    # Check for hardware and safety details in chunk text
    all_chunk_text = " ".join([c.text for c in chunks])
    assert "500 ms" in all_chunk_text or "500ms" in all_chunk_text
    assert "ATmega" in all_chunk_text
    assert "Raspberry Pi" in all_chunk_text
    assert "ultrasonic" in all_chunk_text.lower()

def test_lawn_mower_metrics_and_domains():
    file_path = Path("knowledge/projects/autonomous-lawn-mower.md")
    metadata, body = MarkdownParser.parse_file(file_path)
    project = ProjectSchema(**metadata)

    # Verify metrics
    metrics_str = " ".join(project.metrics)
    assert "95%" in metrics_str
    assert "500 ms" in metrics_str
    assert "kg" in metrics_str

    # Verify domains
    assert "Autonomous Robotics" in project.relevant_domains
    assert any("Edge" in d or "Embedded" in d for d in project.relevant_domains)
