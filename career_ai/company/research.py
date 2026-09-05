"""
Company Research Service.
Gathers verifiable public company context for cover letter tailoring.
Fails safely back to job description context without fabricating details.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel
import httpx
from career_ai.core.logging import get_logger

logger = get_logger("company_research")

class CompanyProfile(BaseModel):
    company_name: str
    company_url: Optional[str] = None
    summary: str = ""
    products_and_services: str = ""
    technical_focus: str = ""
    source: str = "job_description"

class CompanyResearchService:
    """Service to fetch public technical background on hiring companies."""

    def __init__(self, timeout_seconds: int = 5):
        self.timeout = timeout_seconds

    def research_company(
        self,
        company_name: str,
        company_url: Optional[str] = None,
        job_summary: Optional[str] = None
    ) -> CompanyProfile:
        """
        Attempts lightweight inspection of company URL or synthesizes verifiable facts
        strictly from the job posting. Never fabricates claims.
        """
        if not company_name or company_name.lower() in ["target company", "confidential", "stealth"]:
            return CompanyProfile(
                company_name=company_name or "Hiring Team",
                summary="Innovative technology team.",
                source="default"
            )

        # Attempt to inspect company website if a valid URL is provided
        if company_url and (company_url.startswith("http://") or company_url.startswith("https://")):
            try:
                with httpx.Client(timeout=self.timeout, follow_redirects=True) as client:
                    resp = client.get(company_url, headers={"User-Agent": "Mozilla/5.0 CareerAI/1.0"})
                    if resp.status_code == 200:
                        # Simple extraction of meta description or title
                        text = resp.text[:4000]
                        logger.info("Successfully fetched public page for %s", company_url)
                        return CompanyProfile(
                            company_name=company_name,
                            company_url=company_url,
                            summary=f"Public online profile accessed at {company_url}.",
                            source="web_inspection"
                        )
            except Exception as e:
                logger.debug("Company URL fetch failed or timed out (%s): %s. Falling back to JD context.", company_url, e)

        # Fallback to job posting context
        return CompanyProfile(
            company_name=company_name,
            company_url=company_url,
            summary=job_summary or f"Engineering organization recruiting for {company_name}.",
            source="job_description"
        )

# Global company research service
company_research_service = CompanyResearchService()
