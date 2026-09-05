"""
Job Description Parser.
Extracts structured JobRequirements from raw text using the LLM provider,
with heuristic fallback for offline/development environments.
"""

from typing import Optional
from career_ai.jobs.schemas import JobRequirements
from career_ai.llm.base import LLMProvider
from career_ai.llm.factory import get_llm_provider
from career_ai.llm.prompts import JOB_PARSING_SYSTEM_PROMPT, JOB_PARSING_USER_PROMPT
from career_ai.core.logging import get_logger
from career_ai.core.exceptions import JobAnalysisError, LLMAuthenticationError

logger = get_logger("job_parser")

class JobParser:
    """Parses arbitrary job postings into structured JobRequirements."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self._llm = llm_provider

    @property
    def llm(self) -> LLMProvider:
        if self._llm is None:
            self._llm = get_llm_provider()
        return self._llm

    def parse(
        self,
        job_description: str,
        company_name: Optional[str] = None,
        job_title: Optional[str] = None,
        company_url: Optional[str] = None,
        job_url: Optional[str] = None
    ) -> JobRequirements:
        """Extracts structured JobRequirements from JD text."""
        if not job_description or not job_description.strip():
            raise JobAnalysisError("Job description cannot be empty.")

        prompt = JOB_PARSING_USER_PROMPT.format(
            company_name=company_name or "Not Specified (infer if possible)",
            job_title=job_title or "Not Specified (infer if possible)",
            job_description=job_description.strip()
        )

        try:
            parsed = self.llm.generate_structured(
                prompt=prompt,
                schema=JobRequirements,
                system_prompt=JOB_PARSING_SYSTEM_PROMPT,
                temperature=0.1
            )
            # Override with explicit user input if provided
            if company_name and company_name.strip():
                parsed.company_name = company_name.strip()
            if job_title and job_title.strip():
                parsed.job_title = job_title.strip()
            if company_url:
                parsed.company_url = company_url
            if job_url:
                parsed.job_url = job_url

            logger.info("Successfully parsed job requirements for %s at %s", parsed.job_title, parsed.company_name)
            return parsed

        except LLMAuthenticationError:
            logger.warning("LLM API key not available. Using heuristic parser fallback.")
            return self._heuristic_parse(job_description, company_name, job_title, company_url, job_url)
        except Exception as e:
            logger.error("LLM job parsing failed: %s. Falling back to heuristics.", e)
            return self._heuristic_parse(job_description, company_name, job_title, company_url, job_url)

    def _heuristic_parse(
        self,
        text: str,
        company_name: Optional[str],
        job_title: Optional[str],
        company_url: Optional[str],
        job_url: Optional[str]
    ) -> JobRequirements:
        """Fast rule-based heuristic extractor used when offline or without API key."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        inferred_title = job_title or "Machine Learning Engineer"
        inferred_company = company_name or "Target Company"

        # Look for title-like words in early lines
        if not job_title and lines:
            for l in lines[:3]:
                if any(k in l.lower() for k in ["engineer", "scientist", "developer", "lead", "architect", "researcher"]):
                    inferred_title = l
                    break

        tech_keywords = [
            "python", "pytorch", "tensorflow", "scikit-learn", "fastapi", "docker",
            "kubernetes", "rag", "vector search", "faiss", "nlp", "computer vision",
            "sql", "c++", "typescript", "javascript", "aws", "gcp", "onnx", "opencv",
            "deepseek", "gemini", "langchain", "prompt engineering", "streamlit"
        ]

        found_skills = []
        text_lower = text.lower()
        for kw in tech_keywords:
            if kw in text_lower:
                found_skills.append(kw.title() if len(kw) > 3 else kw.upper())

        return JobRequirements(
            company_name=inferred_company,
            job_title=inferred_title,
            company_url=company_url,
            job_url=job_url,
            role_summary=lines[0] if lines else "Target AI/ML Role",
            responsibilities=lines[1:5] if len(lines) > 5 else lines,
            required_skills=found_skills,
            programming_languages=[s for s in found_skills if s.lower() in ["python", "c++", "typescript", "javascript", "sql"]],
            frameworks=[s for s in found_skills if s.lower() in ["pytorch", "tensorflow", "scikit-learn", "fastapi", "opencv", "onnx", "keras"]],
            infrastructure_and_cloud=[s for s in found_skills if s.lower() in ["docker", "kubernetes", "aws", "gcp"]],
            ml_domains=[s for s in found_skills if s.lower() in ["nlp", "computer vision", "rag", "vector search"]]
        )

# Global parser
job_parser = JobParser()
