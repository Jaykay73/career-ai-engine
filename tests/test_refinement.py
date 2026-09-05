"""
Tests for AI Refinement Chat feature.
Verifies that user corrections are applied to TailoredCV while preserving all invariants.
"""

import pytest
from pathlib import Path
from career_ai.services.application_service import application_service

SAMPLE_JD = """
Job Title: Senior Data & AI Engineer
Company: CloudData Inc
About:
Looking for an engineer with strong Python, SQL, and data analytics skills.
Responsibilities:
- Build data pipelines and reporting dashboards.
- Train supervised machine learning models.
Requirements:
- Bachelor's degree in Computer Engineering or related field.
- Experience with FastAPI, Scikit-learn, and data visualization tools.
"""

def test_ai_refinement_flow():
    # 1. Analyze and Generate
    analysis = application_service.analyze_job_posting(
        job_description=SAMPLE_JD,
        company_name="CloudData Inc",
        job_title="Senior Data & AI Engineer"
    )
    initial_result = application_service.generate_tailored_application(
        analysis=analysis,
        job_description=SAMPLE_JD,
        company_name_override="CloudData Inc",
        job_title_override="Senior Data & AI Engineer"
    )
    
    assert "tailored_cv" in initial_result
    assert Path(initial_result["tex_path"]).exists()

    # 2. Refine CV with user instruction
    correction_prompt = "Emphasize my Power BI and time series experience in the first experience bullets and summary."
    updated_result, reply_msg = application_service.refine_application(
        current_result=initial_result,
        user_instruction=correction_prompt,
        analysis=analysis
    )

    assert "Applied your corrections" in reply_msg
    assert Path(updated_result["tex_path"]).exists()
    
    refined_tex = Path(updated_result["tex_path"]).read_text(encoding="utf-8")
    
    # Invariant assertions
    assert "University of Ilorin" in refined_tex
    assert "Bachelor of Engineering (B.Eng.) in Computer Engineering" in refined_tex
    assert "OCI Generative AI Professional" in refined_tex
    assert "Oracle AI Foundations Associate" in refined_tex
    assert "Machine Learning Specialization" in refined_tex
    assert "Second Class" not in refined_tex
    assert "GPA" not in refined_tex
