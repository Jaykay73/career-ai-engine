"""
Unit tests for Markdown knowledge parser and frontmatter extraction.
"""

import pytest
from pathlib import Path
from career_ai.knowledge.parser import MarkdownParser

def test_parse_education_file():
    file_path = Path("knowledge/education/university-of-ilorin.md")
    assert file_path.exists(), "Education file should exist"
    
    metadata, body = MarkdownParser.parse_file(file_path)
    assert isinstance(metadata, dict)
    assert metadata.get("institution") == "University of Ilorin"
    assert "Computer Engineering" in metadata.get("degree", "")
    assert metadata.get("end_date") == "2026"
    assert len(body) > 0

def test_parse_certifications():
    cert_files = list(Path("knowledge/certifications").glob("*.md"))
    assert len(cert_files) == 3, "There should be exactly 3 certified files"
    
    names = set()
    for f in cert_files:
        metadata, body = MarkdownParser.parse_file(f)
        assert "certification_name" in metadata
        names.add(metadata["certification_name"])
        
    # Check that all 3 canonical certifications are parsed
    assert any("Generative AI" in n for n in names)
    assert any("AI Foundations" in n for n in names)
    assert any("Machine Learning" in n for n in names)

def test_parse_project():
    file_path = Path("knowledge/projects/bitcheck.md")
    assert file_path.exists()
    
    metadata, body = MarkdownParser.parse_file(file_path)
    assert "BitCheck" in metadata.get("project_name", "")
    assert "Python" in metadata.get("programming_languages", [])
    assert "FastAPI" in metadata.get("frameworks", [])
    
    sections = MarkdownParser.extract_sections(body)
    assert len(sections) > 0

def test_extract_title_and_company():
    from career_ai.jobs.parser import extract_title_and_company

    # 1. Labeled headers
    jd1 = """
    Job Title: Senior Machine Learning Engineer
    Company: Alpha Health AI
    Responsibilities:
    Build medical AI pipelines...
    """
    t1, c1 = extract_title_and_company(jd1)
    assert t1 == "Senior Machine Learning Engineer"
    assert c1 == "Alpha Health AI"

    # 2. 'Role at Company' format
    jd2 = """
    Lead AI Research Scientist at DeepMind
    Location: London, UK
    About the team:
    We are advancing artificial general intelligence...
    """
    t2, c2 = extract_title_and_company(jd2)
    assert t2 == "Lead AI Research Scientist"
    assert c2 == "DeepMind"

    # 3. 'Company is hiring a Role' format
    jd3 = """
    Stripe is looking for a Senior Computer Vision Engineer
    About Stripe:
    Stripe powers online payments...
    """
    t3, c3 = extract_title_and_company(jd3)
    assert "Computer Vision Engineer" in t3
    assert c3 == "Stripe"

    # 4. 'About Company' format
    jd4 = """
    Machine Learning Engineer (Remote)
    About Anthropic:
    Anthropic is an AI safety research company...
    """
    t4, c4 = extract_title_and_company(jd4)
    assert t4 == "Machine Learning Engineer"
    assert c4 == "Anthropic"
