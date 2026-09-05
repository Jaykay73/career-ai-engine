"""
Unit tests for FactualClaimVerifier and Inviolable Profile Rules.
"""

import pytest
from career_ai.tailoring.verifier import FactualClaimVerifier
from career_ai.tailoring.schemas import TailoredCV, TailoredEducation, TailoredCertification, TailoredProject, TailoredBullet
from career_ai.knowledge.schemas import EvidenceChunk

def test_verifier_accepts_valid_cv():
    verifier = FactualClaimVerifier()
    
    # Valid compliant CV
    cv = TailoredCV(
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
        projects=[
            TailoredProject(
                name="Brain Tumor MRI",
                technologies="PyTorch, Python",
                bullets=[TailoredBullet(text="Engineered CNN architecture for brain tumor classification achieving 96.2% ROC-AUC.")]
            )
        ]
    )

    auth_chunks = [
        EvidenceChunk(
            id="c1",
            source_type="project",
            source_id="brain-tumor",
            title="Brain Tumor MRI",
            section="Metrics",
            file_path="knowledge/projects/brain-tumor.md",
            text="Achieved 96.2% ROC-AUC on validation dataset."
        )
    ]

    result = verifier.verify_cv(cv=cv, authoritative_evidence=auth_chunks)
    assert result.is_valid is True
    assert len(result.unsupported_claims) == 0

def test_verifier_rejects_degree_classification():
    verifier = FactualClaimVerifier()
    
    cv = TailoredCV(
        education=TailoredEducation(
            degree="Bachelor of Engineering (B.Eng.) in Computer Engineering (First Class Honours)",
            institution="University of Ilorin",
            period="2021 -- 2026"
        ),
        certifications=[
            TailoredCertification(name="OCI Generative AI Professional", issuer="Oracle", date="2024"),
            TailoredCertification(name="Oracle AI Foundations Associate", issuer="Oracle", date="2024"),
            TailoredCertification(name="Machine Learning Specialization", issuer="Stanford University & DeepLearning.AI", date="2024"),
        ]
    )

    result = verifier.verify_cv(cv=cv, authoritative_evidence=[])
    assert result.is_valid is False
    assert any("degree" in claim.lower() or "first class" in claim.lower() for claim in result.unsupported_claims)

def test_verifier_rejects_unverified_certification():
    verifier = FactualClaimVerifier()
    
    cv = TailoredCV(
        education=TailoredEducation(
            degree="Bachelor of Engineering (B.Eng.) in Computer Engineering",
            institution="University of Ilorin",
            period="2021 -- 2026"
        ),
        certifications=[
            TailoredCertification(name="AWS Certified Solutions Architect", issuer="Amazon", date="2024"),
        ]
    )

    result = verifier.verify_cv(cv=cv, authoritative_evidence=[])
    assert result.is_valid is False
    assert any("unverified certification" in claim.lower() for claim in result.unsupported_claims)

def test_verifier_flags_fabricated_metrics():
    verifier = FactualClaimVerifier()
    
    cv = TailoredCV(
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
        projects=[
            TailoredProject(
                name="Brain Tumor MRI",
                technologies="Python",
                bullets=[TailoredBullet(text="Generated 99.8% precision and reduced cloud expenses by 85%.")]
            )
        ]
    )

    # Empty knowledge base - 99.8% and 85% are not grounded
    result = verifier.verify_cv(cv=cv, authoritative_evidence=[])
    assert result.is_valid is False
    assert len(result.unsupported_claims) > 0
