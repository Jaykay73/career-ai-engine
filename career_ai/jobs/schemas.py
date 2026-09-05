"""
Job Requirements & Requirement Assessment Pydantic Schemas.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from career_ai.retrieval.rrf import RankedEvidence

class JobRequirements(BaseModel):
    company_name: str = "Target Company"
    job_title: str = "Machine Learning Engineer"
    company_url: Optional[str] = None
    job_url: Optional[str] = None
    role_summary: str = ""
    responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    infrastructure_and_cloud: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    ml_domains: List[str] = Field(default_factory=list)
    education_requirements: List[str] = Field(default_factory=list)
    experience_years_requirement: Optional[str] = None
    location_and_work_mode: Optional[str] = None
    soft_skills: List[str] = Field(default_factory=list)

    @property
    def all_target_skills(self) -> List[str]:
        """Aggregates all unique technical skills, frameworks, and languages."""
        combined = (
            self.required_skills +
            self.preferred_skills +
            self.programming_languages +
            self.frameworks +
            self.infrastructure_and_cloud +
            self.databases +
            self.ml_domains
        )
        # Deduplicate preserving order
        seen = set()
        deduped = []
        for s in combined:
            s_clean = s.strip()
            if s_clean and s_clean.lower() not in seen:
                seen.add(s_clean.lower())
                deduped.append(s_clean)
        return deduped

class RequirementAssessment(BaseModel):
    requirement: str
    category: str = "skill"  # skill, language, framework, responsibility, experience, education
    is_supported: bool
    evidence_chunk_ids: List[str] = Field(default_factory=list)
    explanation: str = ""
    top_evidence: List[RankedEvidence] = Field(default_factory=list)

class JobAnalysisResult(BaseModel):
    job_requirements: JobRequirements
    supported_requirements: List[RequirementAssessment] = Field(default_factory=list)
    unsupported_requirements: List[RequirementAssessment] = Field(default_factory=list)
    retrieved_evidence: List[RankedEvidence] = Field(default_factory=list)
