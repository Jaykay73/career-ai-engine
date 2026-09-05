"""
End-to-end pipeline test.
"""

import pytest
from pathlib import Path
from career_ai.services.application_service import ApplicationService

SAMPLE_JD = """
Job Title: AI Engineer
Company: InnovateTech
About:
We are looking for an AI Engineer to design and deploy NLP and RAG pipelines.
Responsibilities:
- Build RAG applications with vector databases (Qdrant) and LLMs.
- Develop REST APIs with FastAPI and Docker.
Requirements:
- Bachelor's degree in Computer Engineering or related discipline.
- Strong Python, PyTorch, and FastAPI experience.
- Knowledge of vector search and hybrid retrieval.
"""

def test_full_pipeline():
    service = ApplicationService()
    
    # 1. Summary
    summary = service.get_knowledge_summary()
    assert summary["total_records"] > 0
    
    # 2. Analyze
    analysis = service.analyze_job_posting(
        job_description=SAMPLE_JD,
        company_name="InnovateTech",
        job_title="AI Engineer"
    )
    assert len(analysis.supported_requirements) > 0
    assert len(analysis.retrieved_evidence) > 0
    
    # 3. Generate
    result = service.generate_tailored_application(
        analysis=analysis,
        job_description=SAMPLE_JD,
        company_name_override="InnovateTech",
        job_title_override="AI Engineer"
    )
    
    assert Path(result["tex_path"]).exists()
    assert Path(result["cover_letter_tex_path"]).exists()
    
    # Invariant assertions
    tex_content = Path(result["tex_path"]).read_text(encoding="utf-8")
    assert "University of Ilorin" in tex_content
    assert "Bachelor of Engineering (B.Eng.) in Computer Engineering" in tex_content
    assert "OCI Generative AI Professional" in tex_content
    assert "Oracle AI Foundations Associate" in tex_content
    assert "Machine Learning Specialization" in tex_content
    assert "Second Class" not in tex_content
    assert "GPA" not in tex_content
