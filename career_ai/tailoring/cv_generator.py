"""
Tailored CV Generator.
Constructs structured TailoredCV models aligned with target job postings
using verified evidence chunks, strict factual guidelines, and LLM synthesis.
"""

from typing import List, Dict, Any, Optional
import json
from career_ai.jobs.schemas import JobRequirements, JobAnalysisResult
from career_ai.tailoring.schemas import (
    TailoredCV,
    TailoredExperience,
    TailoredProject,
    TailoredBullet,
    TailoredSkillCategory,
    TailoredPublication,
    TailoredEducation,
    TailoredCertification
)
from career_ai.tailoring.selector import EvidenceSelector, evidence_selector
from career_ai.retrieval.rrf import RankedEvidence
from career_ai.llm.base import LLMProvider
from career_ai.llm.factory import get_llm_provider
from career_ai.llm.prompts import TAILORING_SYSTEM_PROMPT, TAILORING_USER_PROMPT
from career_ai.core.logging import get_logger
from career_ai.core.exceptions import LLMAuthenticationError

logger = get_logger("cv_generator")

class CVGenerator:
    """Generates truth-preserving tailored CV models for target positions."""

    def __init__(self, llm: Optional[LLMProvider] = None, selector: Optional[EvidenceSelector] = None):
        self._llm = llm
        self.selector = selector or evidence_selector

    @property
    def llm(self) -> LLMProvider:
        if self._llm is None:
            self._llm = get_llm_provider()
        return self._llm

    def generate(
        self,
        job: JobRequirements,
        analysis: JobAnalysisResult,
        evidence: List[RankedEvidence]
    ) -> TailoredCV:
        """Generates an evidence-grounded TailoredCV for the target job."""
        logger.info("Generating tailored CV for %s at %s", job.job_title, job.company_name)

        # 1. Select skills and publications via deterministic selector
        prioritized_skills = self.selector.prioritize_skills(job)
        relevant_pubs = self.selector.select_relevant_publications(job, max_publications=3)

        # 2. Format retrieved evidence for LLM prompt
        evidence_text_blocks = []
        for rank, ev in enumerate(evidence[:25], start=1):
            evidence_text_blocks.append(
                f"[Evidence ID: {ev.chunk.id}]\n"
                f"Source: {ev.chunk.title} ({ev.chunk.source_type} / {ev.chunk.section})\n"
                f"Content: {ev.chunk.text}\n"
            )
        evidence_context = "\n".join(evidence_text_blocks)

        prompt = TAILORING_USER_PROMPT.format(
            job_title=job.job_title,
            company_name=job.company_name,
            job_requirements_json=job.model_dump_json(indent=2),
            retrieved_evidence_text=evidence_context
        )

        try:
            tailored = self.llm.generate_structured(
                prompt=prompt,
                schema=TailoredCV,
                system_prompt=TAILORING_SYSTEM_PROMPT,
                temperature=0.1
            )
            # Guarantee critical invariant constraints
            tailored = self._enforce_invariants(tailored, prioritized_skills, relevant_pubs)
            return tailored

        except LLMAuthenticationError:
            logger.warning("LLM key absent. Synthesizing CV from verified evidence templates.")
            return self._synthesize_fallback_cv(job, prioritized_skills, relevant_pubs)
        except Exception as e:
            logger.error("LLM CV tailoring failed: %s. Using evidence synthesis fallback.", e)
            return self._synthesize_fallback_cv(job, prioritized_skills, relevant_pubs)

    def _enforce_invariants(
        self,
        cv: TailoredCV,
        prioritized_skills: List[TailoredSkillCategory],
        relevant_pubs: List[TailoredPublication]
    ) -> TailoredCV:
        """Enforces inviolable truthfulness and formatting rules."""
        # 1. Absolute degree representation rule: No classification
        cv.education = TailoredEducation(
            institution="University of Ilorin",
            degree="Bachelor of Engineering (B.Eng.) in Computer Engineering",
            period="2021 -- 2026",
            location="Ilorin, Nigeria",
            coursework="Data Structures & Algorithms, Computer Architecture, Operating Systems, Intelligent Systems, Signal Processing, Software Engineering."
        )

        # 2. Certifications rule: All 3 verified certifications MUST always be present
        cv.certifications = [
            TailoredCertification(name="OCI Generative AI Professional", issuer="Oracle", date="2024"),
            TailoredCertification(name="Oracle AI Foundations Associate", issuer="Oracle", date="2024"),
            TailoredCertification(name="Machine Learning Specialization", issuer="Stanford University & DeepLearning.AI", date="2024")
        ]

        # 3. Use prioritized skills if LLM truncated skills
        if not cv.skills or len(cv.skills) < 4:
            cv.skills = prioritized_skills

        # 4. Publications
        if not cv.publications and relevant_pubs:
            cv.publications = relevant_pubs

        # 5. Core Contact Details
        cv.full_name = "John Aledare"
        cv.email = "aledareoluwaseunjohn@gmail.com"
        cv.portfolio_url = "https://aledare.vercel.app"
        cv.github_url = "https://github.com/Jaykay73"
        cv.linkedin_url = "https://linkedin.com/in/johnaledare"

        return cv

    def _synthesize_fallback_cv(
        self,
        job: JobRequirements,
        prioritized_skills: List[TailoredSkillCategory],
        relevant_pubs: List[TailoredPublication]
    ) -> TailoredCV:
        """Deterministic fallback CV synthesized directly from verified evidence."""
        # Professional Experiences
        exp_queryfier = TailoredExperience(
            company="Queryfier LLC",
            role="Machine Learning Engineer",
            period="Jan 2026 -- Present",
            location="Remote",
            bullets=[
                TailoredBullet(
                    text="Architect, train, and deploy production-grade machine learning models for NLP and Computer Vision tasks.",
                    evidence_ids=["experience:queryfier:responsibilities"]
                ),
                TailoredBullet(
                    text="Construct end-to-end data preprocessing and continuous training pipelines using Scikit-learn, TensorFlow, and PyTorch.",
                    evidence_ids=["experience:queryfier:responsibilities"]
                ),
                TailoredBullet(
                    text="Build low-latency asynchronous API inference microservices with FastAPI and interactive validation interfaces using Streamlit.",
                    evidence_ids=["experience:queryfier:responsibilities"]
                ),
                TailoredBullet(
                    text="Enforce schema validation (Pydantic v2), containerize services with Docker, and implement real-time model monitoring.",
                    evidence_ids=["experience:queryfier:responsibilities"]
                )
            ]
        )

        exp_camlds = TailoredExperience(
            company="Centre for Applied Machine Learning and Data Science (CAMLDS)",
            role="Machine Learning Engineer Intern & Python Tutor",
            period="Mar 2025 -- Dec 2025",
            location="On-site",
            bullets=[
                TailoredBullet(
                    text="Developed and evaluated supervised and unsupervised machine learning pipelines for text classification and computer vision.",
                    evidence_ids=["experience:camlds:responsibilities"]
                ),
                TailoredBullet(
                    text="Built and deployed web demo prototypes using Streamlit and FastAPI for model validation.",
                    evidence_ids=["experience:camlds:responsibilities"]
                ),
                TailoredBullet(
                    text="Mentored junior interns and led hands-on tutoring sessions in Python, NumPy, Pandas, Scikit-learn, and neural networks.",
                    evidence_ids=["experience:camlds:responsibilities"]
                )
            ]
        )

        # Projects tailored to the job
        projects = [
            TailoredProject(
                name="BitCheck -- Multimodal AI Verification API",
                technologies="PyTorch, FastAPI, OpenCV, Tesseract, C2PA, Docker",
                bullets=[
                    TailoredBullet(
                        text="Engineered a multi-signal forensic verification API analyzing images, audio, and text for AI generation and manipulation.",
                        evidence_ids=["project:bitcheck:architecture", "project:bitcheck:contributions"]
                    ),
                    TailoredBullet(
                        text="Integrated metadata extraction, C2PA provenance credentials, OCR watermark scanning, noise forensics, and a custom PyTorch classifier trained on 140K images with Grad-CAM explainability.",
                        evidence_ids=["project:bitcheck:architecture", "project:bitcheck:contributions"]
                    ),
                    TailoredBullet(
                        text="Containerized the service with Docker and deployed on Hugging Face Spaces with a Vercel web frontend.",
                        evidence_ids=["project:bitcheck:technologies"]
                    )
                ]
            ),
            TailoredProject(
                name="AI Resume Optimizer & Career Architect",
                technologies="Gemini 2.0 Flash, ONNX, FastAPI, Next.js, Docker",
                bullets=[
                    TailoredBullet(
                        text="Built an automated career coach parsing resumes with 95% accuracy to identify skill gaps against target job descriptions.",
                        evidence_ids=["project:resume-optimizer:overview", "project:resume-optimizer:contributions"]
                    ),
                    TailoredBullet(
                        text="Integrated Gemini 2.0 Flash for tailored cover letter generation and used ONNX quantization for low-latency NER inference.",
                        evidence_ids=["project:resume-optimizer:architecture"]
                    )
                ]
            ),
            TailoredProject(
                name="LockedIn AI Service -- Intelligent Roadmap Generator",
                technologies="FastAPI, DeepSeek LLM, Tavily API, YouTube API, SQLite, Pydantic",
                bullets=[
                    TailoredBullet(
                        text="Developed an automated learning roadmap generator fetching live candidates via Tavily/YouTube and filtering paywalls/duplicates.",
                        evidence_ids=["project:lockedin:overview", "project:lockedin:contributions"]
                    ),
                    TailoredBullet(
                        text="Synthesized structured curriculum paths via DeepSeek LLM, validated with Pydantic v2 schemas and cached in SQLite.",
                        evidence_ids=["project:lockedin:architecture"]
                    )
                ]
            ),
            TailoredProject(
                name="CineMatch API -- Vector Recommendation Engine",
                technologies="FastAPI, FAISS, SentenceTransformers, Pandas, TMDB API",
                bullets=[
                    TailoredBullet(
                        text="Developed a semantic movie recommendation engine using MiniLM dense embeddings and FAISS vector similarity for sub-100ms retrieval.",
                        evidence_ids=["project:cinematch:overview", "project:cinematch:technologies"]
                    )
                ]
            )
        ]

        summary = f"AI and Machine Learning Engineer specializing in production-grade model serving, low-latency APIs (FastAPI), deep learning (PyTorch, TensorFlow), and RAG vector search architectures. Driven to deliver robust, evidence-backed AI systems for {job.company_name}."

        cv = TailoredCV(
            headline=f"AI Engineer | Machine Learning Engineer — {job.job_title}",
            summary=summary,
            skills=prioritized_skills,
            experiences=[exp_queryfier, exp_camlds],
            projects=projects,
            publications=relevant_pubs
        )
        return self._enforce_invariants(cv, prioritized_skills, relevant_pubs)

# Global generator
cv_generator = CVGenerator()
