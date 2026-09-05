"""
Evidence-Grounded Cover Letter Generator.
Synthesizes targeted, company-specific cover letters (250–400 words)
strictly grounded in verified candidate evidence and public company facts.
"""

from typing import Optional, List
from datetime import datetime
from career_ai.jobs.schemas import JobRequirements, JobAnalysisResult
from career_ai.tailoring.schemas import CoverLetter
from career_ai.company.research import CompanyResearchService, company_research_service, CompanyProfile
from career_ai.llm.base import LLMProvider
from career_ai.llm.factory import get_llm_provider
from career_ai.llm.prompts import (
    COVER_LETTER_SYSTEM_PROMPT,
    COVER_LETTER_USER_PROMPT,
    COVER_LETTER_REFINEMENT_SYSTEM_PROMPT,
    COVER_LETTER_REFINEMENT_USER_PROMPT
)
from career_ai.core.logging import get_logger
from career_ai.core.exceptions import LLMAuthenticationError

logger = get_logger("cover_letter")

class CoverLetterGenerator:
    """Generates truth-preserving tailored cover letters."""

    def __init__(
        self,
        llm: Optional[LLMProvider] = None,
        research_service: Optional[CompanyResearchService] = None
    ):
        self._llm = llm
        self.research_service = research_service or company_research_service

    @property
    def llm(self) -> LLMProvider:
        if self._llm is None:
            self._llm = get_llm_provider()
        return self._llm

    def generate(
        self,
        job: JobRequirements,
        analysis: JobAnalysisResult
    ) -> CoverLetter:
        """Generates a company-specific, evidence-backed cover letter."""
        logger.info("Generating cover letter for %s at %s", job.job_title, job.company_name)

        # 1. Gather verified company context
        company_prof = self.research_service.research_company(
            company_name=job.company_name,
            company_url=job.company_url,
            job_summary=job.role_summary
        )

        # 2. Summarize top supported candidate evidence
        evidence_summary_lines = []
        for req in analysis.supported_requirements[:8]:
            evidence_summary_lines.append(f"- Requirement '{req.requirement}' supported by: {', '.join(req.evidence_chunk_ids)}")
        evidence_summary = "\n".join(evidence_summary_lines)

        job_summary = (
            f"Title: {job.job_title}\n"
            f"Company: {job.company_name}\n"
            f"Key Technologies: {', '.join(job.all_target_skills[:10])}\n"
            f"Responsibilities: {'; '.join(job.responsibilities[:3])}"
        )

        prompt = COVER_LETTER_USER_PROMPT.format(
            company_name=job.company_name,
            job_title=job.job_title,
            company_insights=company_prof.summary,
            job_requirements_summary=job_summary,
            candidate_evidence_summary=evidence_summary
        )

        try:
            letter = self.llm.generate_structured(
                prompt=prompt,
                schema=CoverLetter,
                system_prompt=COVER_LETTER_SYSTEM_PROMPT,
                temperature=0.2
            )
            letter.company_name = job.company_name
            letter.position = job.job_title
            letter.job_title = job.job_title
            letter.candidate_name = "John Aledare"
            if not letter.date:
                letter.date = datetime.utcnow().strftime("%B %d, %Y")
            return letter

        except LLMAuthenticationError:
            logger.warning("LLM key absent. Generating structured deterministic cover letter.")
            return self._synthesize_fallback_letter(job, company_prof)
        except Exception as e:
            logger.error("LLM cover letter generation failed: %s. Using fallback letter.", e)
            return self._synthesize_fallback_letter(job, company_prof)

    def refine(
        self,
        current_letter: CoverLetter,
        user_instruction: str,
        job: JobRequirements,
        analysis: JobAnalysisResult
    ) -> CoverLetter:
        """Refines existing cover letter according to candidate instructions."""
        logger.info("Refining cover letter for %s at %s with instruction: %s", job.job_title, job.company_name, user_instruction[:80])

        evidence_summary_lines = []
        for req in analysis.supported_requirements[:8]:
            evidence_summary_lines.append(f"- Requirement '{req.requirement}' supported by: {', '.join(req.evidence_chunk_ids)}")
        evidence_summary = "\n".join(evidence_summary_lines)

        prompt = COVER_LETTER_REFINEMENT_USER_PROMPT.format(
            user_instruction=user_instruction,
            company_name=job.company_name,
            job_title=job.job_title,
            current_cl_json=current_letter.model_dump_json(indent=2),
            candidate_evidence_summary=evidence_summary
        )

        try:
            letter = self.llm.generate_structured(
                prompt=prompt,
                schema=CoverLetter,
                system_prompt=COVER_LETTER_REFINEMENT_SYSTEM_PROMPT,
                temperature=0.2
            )
            letter.company_name = job.company_name
            letter.position = job.job_title
            letter.job_title = job.job_title
            letter.candidate_name = "John Aledare"
            if not letter.date:
                letter.date = current_letter.date or datetime.utcnow().strftime("%B %d, %Y")
            return letter
        except Exception as e:
            logger.error("LLM cover letter refinement failed: %s. Preserving current letter.", e)
            return current_letter

    def _synthesize_fallback_letter(
        self,
        job: JobRequirements,
        company_prof: CompanyProfile
    ) -> CoverLetter:
        """Deterministic cover letter adhering strictly to verified facts."""
        date_str = datetime.utcnow().strftime("%B %d, %Y")
        skills_str = ", ".join(job.all_target_skills[:5]) if job.all_target_skills else "Python, PyTorch, and FastAPI"

        opening = f"I am writing to express my strong interest in the {job.job_title} position at {job.company_name}. With hands-on engineering experience designing and deploying production machine learning microservices and applied AI systems, I am eager to contribute to your engineering team."

        p1 = f"At Queryfier LLC, I architect, train, and deploy production-grade machine learning pipelines for NLP and Computer Vision tasks. My core focus centers on building low-latency asynchronous API inference microservices with FastAPI and enforcing strict schema validation with Pydantic. Prior to Queryfier, at the Centre for Applied Machine Learning and Data Science (CAMLDS), I constructed end-to-end data preprocessing pipelines and trained supervised models using Scikit-learn and TensorFlow."

        p2 = f"Beyond production roles, my open-source projects directly demonstrate scalable AI engineering. In BitCheck, I built an asynchronous multimodal media forensics API utilizing PyTorch, OpenCV, and C2PA cryptographic provenance. Similarly, in LockedIn, I integrated search APIs with structured LLM synthesis to generate verified learning curricula. These systems reflect my dedication to building reliable, high-performance machine learning solutions."

        p3 = f"Given your technical emphasis on {skills_str}, my background in B.Eng. Computer Engineering from the University of Ilorin, alongside certifications in OCI Generative AI and Stanford's Machine Learning Specialization, prepares me to make immediate technical contributions to {job.company_name}."

        closing = f"Thank you for your time and consideration. I welcome the opportunity to discuss how my technical skills and engineering approach align with your upcoming goals at {job.company_name}."

        return CoverLetter(
            company_name=job.company_name,
            position=job.job_title,
            job_title=job.job_title,
            date=date_str,
            recipient_title=f"Hiring Team at {job.company_name}",
            opening=opening,
            body_paragraphs=[p1, p2, p3],
            closing=closing,
            candidate_name="John Aledare",
            evidence_ids=["experience:queryfier:responsibilities", "project:bitcheck:architecture", "project:lockedin:architecture"]
        )

# Global generator
cover_letter_generator = CoverLetterGenerator()
