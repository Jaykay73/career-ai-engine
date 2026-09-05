"""
Tailored Candidate Profile, CV, Cover Letter, and Verification Schemas.
Enforces evidence IDs attached to all factual claims and strict formatting rules.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class TailoredBullet(BaseModel):
    text: str
    evidence_ids: List[str] = Field(default_factory=list)

class TailoredProject(BaseModel):
    name: str
    technologies: str  # e.g., "PyTorch, FastAPI, OpenCV, Tesseract, Docker"
    bullets: List[TailoredBullet]
    evidence_ids: List[str] = Field(default_factory=list)

class TailoredExperience(BaseModel):
    company: str
    role: str
    period: str
    location: str
    bullets: List[TailoredBullet]
    evidence_ids: List[str] = Field(default_factory=list)

class TailoredSkillCategory(BaseModel):
    category_name: str  # e.g. "Languages", "Frameworks & Libraries", "NLP, LLMs & RAG", etc.
    skills: List[str]

class TailoredPublication(BaseModel):
    title: str
    url: str
    summary: str
    platform: str = "Artificial Intelligence in Plain English (Medium)"
    evidence_id: Optional[str] = None

class TailoredEducation(BaseModel):
    institution: str = "University of Ilorin"
    degree: str = "Bachelor of Engineering (B.Eng.) in Computer Engineering"
    period: str = "2021 -- 2026"
    location: str = "Ilorin, Nigeria"
    coursework: str = "Data Structures & Algorithms, Computer Architecture, Operating Systems, Intelligent Systems, Signal Processing, Software Engineering."
    # Note: Degree classification is forbidden.

class TailoredCertification(BaseModel):
    name: str
    issuer: str
    date: str = "2024"

class TailoredCustomSectionItem(BaseModel):
    heading: str
    subheading: Optional[str] = ""
    date: Optional[str] = ""
    bullets: List[TailoredBullet] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)

class TailoredCustomSection(BaseModel):
    title: str  # e.g., "Teaching & Mentorship", "Freelance & Consulting", "Leadership & Open Source"
    items: List[TailoredCustomSectionItem] = Field(default_factory=list)

class TailoredCV(BaseModel):
    full_name: str = "John Aledare"
    headline: str = "AI Engineer | Machine Learning Engineer"
    email: str = "aledareoluwaseunjohn@gmail.com"
    portfolio_url: str = "https://aledare.vercel.app"
    github_url: str = "https://github.com/Jaykay73"
    linkedin_url: str = "https://linkedin.com/in/johnaledare"
    summary: Optional[str] = None
    
    education: TailoredEducation = Field(default_factory=TailoredEducation)
    certifications: List[TailoredCertification] = Field(default_factory=lambda: [
        TailoredCertification(name="OCI Generative AI Professional", issuer="Oracle", date="2024"),
        TailoredCertification(name="Oracle AI Foundations Associate", issuer="Oracle", date="2024"),
        TailoredCertification(name="Machine Learning Specialization", issuer="Stanford University & DeepLearning.AI", date="2024")
    ])
    skills: List[TailoredSkillCategory] = Field(default_factory=list)
    experiences: List[TailoredExperience] = Field(default_factory=list)
    projects: List[TailoredProject] = Field(default_factory=list)
    publications: List[TailoredPublication] = Field(default_factory=list)
    custom_sections: List[TailoredCustomSection] = Field(default_factory=list)

class CoverLetter(BaseModel):
    company_name: str
    position: str = ""
    job_title: Optional[str] = None
    date: str = ""
    recipient_title: str = "Hiring Team"
    opening: str = ""
    body_paragraphs: List[str] = Field(default_factory=list)
    closing: str = ""
    sign_off: str = "Sincerely"
    candidate_name: str = "John Aledare"
    evidence_ids: List[str] = Field(default_factory=list)

    def model_post_init(self, __context: Any) -> None:
        if self.job_title and not self.position:
            self.position = self.job_title
        elif self.position and not self.job_title:
            self.job_title = self.position

class VerificationResult(BaseModel):
    is_valid: bool
    unsupported_claims: List[str] = Field(default_factory=list)
    notes: str = ""
