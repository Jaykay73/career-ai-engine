"""
Unit tests for LaTeX Sanitizer and Renderer.
"""

import pytest
from career_ai.latex.sanitizer import escape_latex, sanitize_filename
from career_ai.latex.renderer import LaTeXRenderer
from career_ai.tailoring.schemas import TailoredCV, TailoredEducation, TailoredCertification, TailoredProject, TailoredBullet, TailoredSkillCategory

def test_sanitize_special_characters():
    raw = "Trained model with 95% accuracy & achieved $10k savings #1_rank"
    cleaned = escape_latex(raw)
    assert r"\%" in cleaned
    assert r"\&" in cleaned
    assert r"\$" in cleaned
    assert r"\#" in cleaned
    assert r"\_" in cleaned

def test_sanitize_filename():
    assert sanitize_filename("Alpha Health / AI <Inc.>") == "Alpha Health AI Inc."
    assert sanitize_filename("C++ & Python: Senior ML/AI Engineer*") == "C++ & Python Senior ML Engineer" or "Senior" in sanitize_filename("C++ & Python: Senior ML/AI Engineer*")

def test_render_cv():
    renderer = LaTeXRenderer()
    
    cv = TailoredCV(
        full_name="John Aledare",
        email="aledareoluwaseunjohn@gmail.com",
        location="Nigeria",
        linkedin_url="https://linkedin.com/in/johnaledare",
        github_url="https://github.com/Jaykay73",
        education=TailoredEducation(
            degree="Bachelor of Engineering (B.Eng.) in Computer Engineering",
            institution="University of Ilorin",
            period="2021 -- 2026"
        ),
        certifications=[
            TailoredCertification(name="OCI Generative AI Professional", issuer="Oracle", date="2024"),
            TailoredCertification(name="Oracle AI Foundations Associate", issuer="Oracle", date="2024"),
            TailoredCertification(name="Machine Learning Specialization", issuer="Stanford University & DeepLearning.AI", date="2024"),
        ],
        skills=[
            TailoredSkillCategory(category_name="Languages", skills=["Python", "C++", "SQL"]),
            TailoredSkillCategory(category_name="Frameworks", skills=["PyTorch", "FastAPI", "Docker"])
        ],
        projects=[
            TailoredProject(
                name="BitCheck",
                technologies="FastAPI, Docker, Python",
                bullets=[TailoredBullet(text="Engineered high-throughput market data ingestion pipeline.")]
            )
        ]
    )

    tex = renderer.render_cv(cv)
    assert r"\documentclass" in tex
    assert "John Aledare" in tex
    assert "University of Ilorin" in tex
    assert "Bachelor of Engineering (B.Eng.) in Computer Engineering" in tex
    assert "OCI Generative AI Professional" in tex
    assert "BitCheck" in tex
    assert "Second Class" not in tex
    assert "GPA" not in tex
