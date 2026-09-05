"""
Job Description Parser.
Extracts structured JobRequirements from raw text using the LLM provider,
with robust heuristic and regex extraction for offline/development environments.
"""

from typing import Optional, Tuple
import re
from career_ai.jobs.schemas import JobRequirements
from career_ai.llm.base import LLMProvider
from career_ai.llm.factory import get_llm_provider
from career_ai.llm.prompts import JOB_PARSING_SYSTEM_PROMPT, JOB_PARSING_USER_PROMPT
from career_ai.core.logging import get_logger
from career_ai.core.exceptions import JobAnalysisError, LLMAuthenticationError

logger = get_logger("job_parser")

def extract_title_and_company(text: str) -> Tuple[str, str]:
    """
    Extracts role title and company name from raw job description text
    using high-precision heuristic and regex rules.
    """
    if not text or not text.strip():
        return "Machine Learning Engineer", "Target Company"

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    company: Optional[str] = None
    title: Optional[str] = None

    # 1. Check explicit label patterns (e.g. "Job Title: ...", "Company: ...")
    for line in lines[:20]:
        m_title = re.search(r'^(?:job\s+title|role(?:\s+title)?|position(?:\s+title)?|title)\s*[:\-\|]\s*(.+)$', line, re.I)
        if m_title and not title:
            cand = m_title.group(1).strip()
            # Clean trailing markdown or brackets
            cand = re.sub(r'[\*\#_`]', '', cand).strip()
            if cand:
                title = cand

        m_comp = re.search(r'^(?:company(?:\s+name)?|organization|employer)\s*[:\-\|]\s*(.+)$', line, re.I)
        if m_comp and not company:
            cand = m_comp.group(1).strip()
            cand = re.sub(r'[\*\#_`]', '', cand).strip()
            if cand:
                company = cand

    # 2. Pattern: '<Role> at/@ <Company>' in early lines
    if not title or not company:
        for line in lines[:8]:
            clean_line = re.sub(r'^[#\*\-\s]+', '', line).strip()
            clean_line = re.sub(r'[\*\#_`]', '', clean_line).strip()
            m_at = re.search(r'^(.*?)\s+(?:at|@)\s+([A-Z0-9][A-Za-z0-9\s\.\,&-]{1,40})$', clean_line)
            if m_at:
                cand_title, cand_comp = m_at.group(1).strip(), m_at.group(2).strip()
                if any(k in cand_title.lower() for k in ['engineer', 'scientist', 'developer', 'lead', 'architect', 'researcher', 'manager', 'specialist', 'analyst']):
                    title = title or cand_title
                    company = company or cand_comp
                    break

    # 3. Pattern: '<Company> is hiring/seeking/looking for a <Role>'
    if not title or not company:
        for line in lines[:10]:
            m_hire = re.search(r'^([A-Z0-9][A-Za-z0-9\s\.\,&-]{1,35}?)\s+is\s+(?:hiring|seeking|looking for|searching for)\s+(?:an?|our)?\s*(.*?)$', line, re.I)
            if m_hire:
                cand_c = m_hire.group(1).strip()
                if cand_c.lower() not in ['we', 'who', 'our company', 'the team', 'it']:
                    company = company or cand_c
                cand_t = m_hire.group(2).strip()
                # Clean trailing punctuation
                cand_t = re.sub(r'[\.\:\!].*$', '', cand_t).strip()
                if cand_t and any(k in cand_t.lower() for k in ['engineer', 'scientist', 'developer', 'lead', 'architect', 'researcher', 'specialist']):
                    title = title or cand_t

    # 4. Pattern: 'About <Company>:' or 'About Us - <Company>' or 'At <Company>, we'
    if not company:
        for line in lines[:20]:
            m_about = re.search(r'^(?:about|at|welcome to)\s+([A-Z0-9][A-Za-z0-9\s\.\,&-]{1,35}?)[\s\:\-\,\.]+', line, re.I)
            if m_about:
                cand = m_about.group(1).strip()
                if cand.lower() not in ['the role', 'the job', 'us', 'our team', 'this position', 'you', 'our company', 'work']:
                    company = cand
                    break

    # 5. Fallback title search in top lines
    if not title:
        for line in lines[:6]:
            clean_l = re.sub(r'^[#\*\-\s]+', '', line).strip()
            clean_l = re.sub(r'[\*\#_`]', '', clean_l).strip()
            # remove location / mode tags like (Remote), (Hybrid), etc.
            clean_l = re.sub(r'\s*\((?:remote|hybrid|full[- ]time|part[- ]time|onsite)[^\)]*\)', '', clean_l, flags=re.I).strip()
            if any(k in clean_l.lower() for k in ['engineer', 'scientist', 'developer', 'lead', 'architect', 'researcher', 'manager', 'specialist', 'analyst']):
                if len(clean_l.split()) <= 10:
                    title = clean_l
                    break

    # Clean up any trailing colons or dashes
    final_title = title.strip().rstrip(":-| ") if title else "Machine Learning Engineer"
    final_company = company.strip().rstrip(":-| ") if company else "Target Company"

    return final_title, final_company

class JobParser:
    """Parses arbitrary job postings into structured JobRequirements."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self._llm = llm_provider

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

        # Auto-extract title and company if not provided
        auto_title, auto_company = extract_title_and_company(job_description)
        eff_title = job_title.strip() if (job_title and job_title.strip()) else auto_title
        eff_company = company_name.strip() if (company_name and company_name.strip()) else auto_company

        prompt = JOB_PARSING_USER_PROMPT.format(
            company_name=eff_company,
            job_title=eff_title,
            job_description=job_description.strip()
        )

        try:
            parsed = self.llm.generate_structured(
                prompt=prompt,
                schema=JobRequirements,
                system_prompt=JOB_PARSING_SYSTEM_PROMPT,
                temperature=0.1
            )
            # Ensure effective names are applied
            parsed.company_name = eff_company
            parsed.job_title = eff_title
            if company_url:
                parsed.company_url = company_url
            if job_url:
                parsed.job_url = job_url

            logger.info("Successfully parsed job requirements for %s at %s", parsed.job_title, parsed.company_name)
            return parsed

        except LLMAuthenticationError:
            logger.warning("LLM API key not available. Using heuristic parser fallback.")
            return self._heuristic_parse(job_description, eff_company, eff_title, company_url, job_url)
        except Exception as e:
            logger.error("LLM job parsing failed: %s. Falling back to heuristics.", e)
            return self._heuristic_parse(job_description, eff_company, eff_title, company_url, job_url)

    def _heuristic_parse(
        self,
        text: str,
        company_name: Optional[str],
        job_title: Optional[str],
        company_url: Optional[str],
        job_url: Optional[str]
    ) -> JobRequirements:
        """Fast rule-based heuristic extractor used when offline or without API key."""
        auto_title, auto_company = extract_title_and_company(text)
        inferred_title = job_title or auto_title
        inferred_company = company_name or auto_company

        lines = [line.strip() for line in text.split("\n") if line.strip()]

        tech_keywords = [
            "python", "pytorch", "tensorflow", "scikit-learn", "fastapi", "docker",
            "kubernetes", "rag", "vector search", "faiss", "nlp", "computer vision",
            "sql", "c++", "typescript", "javascript", "aws", "gcp", "onnx", "opencv",
            "deepseek", "gemini", "langchain", "prompt engineering", "streamlit", "qdrant",
            "power bi", "powerbi", "excel", "power query", "power pivot", "dax",
            "time series", "forecasting", "data analytics", "business intelligence", "arima", "sarima"
        ]

        display_names = {
            "power bi": "Power BI",
            "powerbi": "Power BI",
            "excel": "Microsoft Excel",
            "power query": "Power Query",
            "power pivot": "Power Pivot",
            "dax": "DAX",
            "time series": "Time Series Modeling",
            "forecasting": "Forecasting",
            "data analytics": "Data Analytics",
            "business intelligence": "Business Intelligence",
            "arima": "ARIMA",
            "sarima": "SARIMA",
            "sql": "SQL",
            "c++": "C++",
            "aws": "AWS",
            "gcp": "GCP",
            "onnx": "ONNX",
            "opencv": "OpenCV",
            "nlp": "NLP",
            "rag": "RAG",
            "faiss": "FAISS",
            "qdrant": "Qdrant",
        }

        found_skills = []
        text_lower = text.lower()
        for kw in tech_keywords:
            if kw in text_lower:
                name = display_names.get(kw, kw.title() if len(kw) > 3 else kw.upper())
                if name not in found_skills:
                    found_skills.append(name)

        return JobRequirements(
            company_name=inferred_company,
            job_title=inferred_title,
            company_url=company_url,
            job_url=job_url,
            role_summary=lines[0] if lines else f"{inferred_title} at {inferred_company}",
            responsibilities=lines[1:6] if len(lines) > 5 else lines,
            required_skills=found_skills,
            programming_languages=[s for s in found_skills if s.lower() in ["python", "c++", "typescript", "javascript", "sql", "dax"]],
            frameworks=[s for s in found_skills if s.lower() in [
                "pytorch", "tensorflow", "scikit-learn", "fastapi", "opencv", "onnx", "keras",
                "power bi", "power query", "power pivot", "microsoft excel", "excel"
            ]],
            infrastructure_and_cloud=[s for s in found_skills if s.lower() in ["docker", "kubernetes", "aws", "gcp"]],
            ml_domains=[s for s in found_skills if s.lower() in [
                "nlp", "computer vision", "rag", "vector search",
                "time series modeling", "forecasting", "data analytics", "business intelligence", "arima", "sarima"
            ]]
        )

    @property
    def llm(self) -> LLMProvider:
        if self._llm is None:
            self._llm = get_llm_provider()
        return self._llm

# Global parser
job_parser = JobParser()
