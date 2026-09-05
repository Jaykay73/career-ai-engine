"""
Structured Pydantic schemas for the Knowledge Base.
Defines strict models for Projects, Experiences, Certifications, Education,
Publications, Skills, and Evidence Chunks.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ProjectSchema(BaseModel):
    project_name: str
    short_description: str
    problem: str = ""
    solution: str = ""
    architecture: str = ""
    technologies: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    models: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    infrastructure: List[str] = Field(default_factory=list)
    exact_contribution: str = ""
    responsibilities: List[str] = Field(default_factory=list)
    results: List[str] = Field(default_factory=list)
    metrics: List[str] = Field(default_factory=list)
    github_url: Optional[str] = None
    live_demo_url: Optional[str] = None
    screenshots: List[str] = Field(default_factory=list)
    challenges: str = ""
    technical_decisions: str = ""
    lessons_learned: str = ""
    deployment_information: str = ""
    deployment_platform: str = ""
    relevant_domains: List[str] = Field(default_factory=list)
    relevant_job_titles: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    dates: str = ""
    status: str = "completed"

class ExperienceSchema(BaseModel):
    organization: str
    job_title: str
    employment_type: str = "Full-time"  # Full-time, Internship, Freelance, Volunteer
    start_date: str
    end_date: str = "Present"
    location: str = "Remote"
    remote: bool = True
    responsibilities: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    infrastructure: List[str] = Field(default_factory=list)
    models: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    measurable_results: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    exact_contributions: str = ""

class EducationSchema(BaseModel):
    institution: str
    degree: str  # e.g., "B.Eng. Computer Engineering"
    field: str = "Computer Engineering"
    start_date: str = "2021"
    end_date: str = "2026"
    location: str = "Ilorin, Nigeria"
    relevant_coursework: List[str] = Field(default_factory=list)
    academic_projects: List[str] = Field(default_factory=list)
    
    # Degree classification must never be stored or output
    @property
    def display_string(self) -> str:
        return f"{self.degree} — {self.institution}"

class CertificationSchema(BaseModel):
    certification_name: str
    issuing_organization: str
    issue_date: str = ""
    credential_url: Optional[str] = None
    credential_id: Optional[str] = None
    description: str = ""
    relevant_topics: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

class PublicationSchema(BaseModel):
    title: str
    url: str
    platform: str = "Medium"
    date: str = ""
    abstract: str = ""
    topics: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    source_url: Optional[str] = None

class SkillCategorySchema(BaseModel):
    category_name: str
    skills: List[str]

class MasterProfile(BaseModel):
    full_name: str = "John Oluwaseun Aledare"
    headline: str = "AI Engineer | Machine Learning Engineer | Applied AI"
    email: str = "aledareoluwaseunjohn@gmail.com"
    location: str = "Nigeria"
    portfolio_url: str = "https://aledare.vercel.app"
    github_url: str = "https://github.com/Jaykay73"
    linkedin_url: str = "https://www.linkedin.com/in/johnaledare"
    medium_url: str = "https://medium.com/@jermaine73"
    twitter_url: Optional[str] = "https://x.com/Jermaine_73"
    
    education: List[EducationSchema] = Field(default_factory=list)
    certifications: List[CertificationSchema] = Field(default_factory=list)
    skills: List[SkillCategorySchema] = Field(default_factory=list)
    experiences: List[ExperienceSchema] = Field(default_factory=list)
    projects: List[ProjectSchema] = Field(default_factory=list)
    publications: List[PublicationSchema] = Field(default_factory=list)

class EvidenceChunk(BaseModel):
    """
    Normalized atomic unit of evidence used for indexing, hybrid retrieval,
    and hallucination verification.
    """
    id: str  # Unique chunk identifier e.g., 'project:bitcheck:architecture'
    source_type: str  # 'project', 'experience', 'certification', 'publication', 'skill', 'education'
    source_id: str  # slug identifier e.g. 'bitcheck'
    title: str  # Parent title e.g. 'BitCheck'
    section: str  # Section name e.g. 'architecture', 'technologies', 'results'
    file_path: str  # Originating markdown file path
    text: str  # Raw content text for semantic and lexical indexing
    metadata: Dict[str, Any] = Field(default_factory=dict)
