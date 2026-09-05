"""
Core Application Service.
Orchestrates the end-to-end pipeline:
Job Analysis -> Hybrid Retrieval -> Evidence Grounding -> Tailoring ->
Verification -> LaTeX Rendering -> PDF Compilation -> Persistence.
Decoupled completely from Streamlit and ready for FastAPI or CLI interfaces.
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import json
import uuid
from datetime import datetime

from career_ai.jobs.schemas import JobRequirements, JobAnalysisResult
from career_ai.jobs.parser import JobParser, job_parser
from career_ai.jobs.analyzer import JobAnalyzer, job_analyzer
from career_ai.tailoring.schemas import TailoredCV, CoverLetter, VerificationResult
from career_ai.tailoring.cv_generator import CVGenerator, cv_generator
from career_ai.tailoring.cover_letter import CoverLetterGenerator, cover_letter_generator
from career_ai.tailoring.verifier import FactualClaimVerifier, claim_verifier
from career_ai.latex.renderer import LaTeXRenderer, latex_renderer
from career_ai.latex.compiler import LaTeXCompiler, latex_compiler
from career_ai.latex.sanitizer import sanitize_filename
from career_ai.knowledge.indexer import KnowledgeIndexer, indexer
from career_ai.retrieval.hybrid import HybridRetriever, hybrid_retriever
from career_ai.database.repository import Repository, repository
from career_ai.database.models import JobDB, GeneratedApplicationDB
from career_ai.core.config import settings
from career_ai.core.logging import get_logger

logger = get_logger("application_service")

class ApplicationService:
    """Central business logic facade for Career AI engine."""

    def __init__(
        self,
        parser: Optional[JobParser] = None,
        analyzer: Optional[JobAnalyzer] = None,
        cv_gen: Optional[CVGenerator] = None,
        cl_gen: Optional[CoverLetterGenerator] = None,
        verifier: Optional[FactualClaimVerifier] = None,
        renderer: Optional[LaTeXRenderer] = None,
        compiler: Optional[LaTeXCompiler] = None,
        idx: Optional[KnowledgeIndexer] = None,
        retriever: Optional[HybridRetriever] = None,
        repo: Optional[Repository] = None
    ):
        self.parser = parser or job_parser
        self.analyzer = analyzer or job_analyzer
        self.cv_gen = cv_gen or cv_generator
        self.cl_gen = cl_gen or cover_letter_generator
        self.verifier = verifier or claim_verifier
        self.renderer = renderer or latex_renderer
        self.compiler = compiler or latex_compiler
        self.indexer = idx or indexer
        self.retriever = retriever or hybrid_retriever
        self.repo = repo or repository

    # --- Knowledge Operations ---
    def reindex_knowledge(self, recreate_vector: bool = True) -> Dict[str, Any]:
        """Rebuilds BM25 and Qdrant vector index from markdown knowledge directory."""
        logger.info("Service: Rebuilding knowledge index...")
        return self.indexer.index_all(recreate_vector_collection=recreate_vector)

    def get_knowledge_summary(self) -> Dict[str, Any]:
        """Returns statistics on current knowledge base records and index state."""
        counts = self.repo.count_records_by_type()
        meta = self.repo.get_index_metadata()
        meta_dict = None
        if meta:
            meta_dict = {
                "id": meta.id,
                "chunk_count": meta.chunk_count,
                "record_count": meta.record_count,
                "embedding_model": meta.embedding_model,
                "embedding_dim": meta.embedding_dim,
                "updated_at": str(meta.updated_at)
            }
        return {
            "record_counts": counts,
            "total_records": sum(counts.values()),
            "index_metadata": meta_dict,
            "embedding_model": settings.embedding_model,
            "llm_provider": settings.llm_provider,
            "latex_available": self.compiler.is_available()
        }

    # --- Job Analysis & Extraction ---
    def extract_job_metadata(self, job_description: str) -> Dict[str, str]:
        """Auto-extracts role title and company name from raw job posting text."""
        from career_ai.jobs.parser import extract_title_and_company
        title, company = extract_title_and_company(job_description)
        return {"job_title": title, "company_name": company}

    def analyze_job_posting(
        self,
        job_description: str,
        company_name: Optional[str] = None,
        job_title: Optional[str] = None,
        company_url: Optional[str] = None,
        job_url: Optional[str] = None
    ) -> JobAnalysisResult:
        """
        Parses JD text and computes supported vs unrepresented requirements.
        """
        requirements = self.parser.parse(
            job_description=job_description,
            company_name=company_name,
            job_title=job_title,
            company_url=company_url,
            job_url=job_url
        )

        analysis = self.analyzer.analyze(requirements)
        return analysis

    # --- Tailored Application Generation ---
    def generate_tailored_application(
        self,
        analysis: JobAnalysisResult,
        job_description: str,
        company_name_override: Optional[str] = None,
        job_title_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes full generation flow:
        Evidence -> Tailored CV -> Claim Verification -> LaTeX Render -> PDF Compile -> Cover Letter -> Persist.
        """
        job = analysis.job_requirements
        if company_name_override:
            job.company_name = company_name_override
        if job_title_override:
            job.job_title = job_title_override

        app_id = str(uuid.uuid4())
        job_id = str(uuid.uuid4())

        # 1. Retrieve comprehensive evidence
        evidence = analysis.retrieved_evidence

        # 2. Tailor CV
        tailored_cv = self.cv_gen.generate(job=job, analysis=analysis, evidence=evidence)

        # 3. Post-Generation Verification
        # Retrieve all authoritative raw chunks
        all_chunks, _ = self.indexer.scan_and_chunk()
        verification_result = self.verifier.verify_cv(cv=tailored_cv, authoritative_evidence=all_chunks)

        # 4. Render LaTeX CV
        tex_content = self.renderer.render_cv(tailored_cv)

        # 5. Determine Paths & Filenames: "John Aledare <Job Title>.tex" and ".pdf"
        sanitized_company = sanitize_filename(job.company_name) or "Company"
        sanitized_title = sanitize_filename(job.job_title) or "Role"

        job_dir = settings.output_dir / sanitized_company / sanitized_title
        job_dir.mkdir(parents=True, exist_ok=True)

        base_cv_name = f"John Aledare {sanitized_title}"
        tex_path = job_dir / f"{base_cv_name}.tex"
        pdf_path = job_dir / f"{base_cv_name}.pdf"

        # Save .tex file
        tex_path.write_text(tex_content, encoding="utf-8")
        logger.info("Saved generated LaTeX CV to %s", tex_path)

        # 6. Compile PDF if compiler available
        pdf_compiled, compile_msg = self.compiler.compile(tex_content=tex_content, output_pdf_path=pdf_path)

        # 7. Generate Tailored Cover Letter
        cover_letter = self.cl_gen.generate(job=job, analysis=analysis)
        cl_tex_content = self.renderer.render_cover_letter(cover_letter)
        cl_tex_path = job_dir / f"John Aledare Cover Letter {sanitized_company}.tex"
        cl_pdf_path = job_dir / f"John Aledare Cover Letter {sanitized_company}.pdf"
        cl_tex_path.write_text(cl_tex_content, encoding="utf-8")

        cl_compiled, cl_compile_msg = self.compiler.compile(tex_content=cl_tex_content, output_pdf_path=cl_pdf_path)

        # 8. Save Job and Application Records in SQLite
        job_db = JobDB(
            id=job_id,
            company_name=job.company_name,
            job_title=job.job_title,
            company_url=job.company_url,
            job_url=job.job_url,
            raw_description=job_description,
            parsed_requirements_json=job.model_dump_json()
        )
        self.repo.save_job(job_db)

        meta_dict = {
            "verified": verification_result.is_valid,
            "unsupported_claims": verification_result.unsupported_claims,
            "supported_requirements": [r.requirement for r in analysis.supported_requirements],
            "unrepresented_requirements": [r.requirement for r in analysis.unsupported_requirements],
            "selected_projects": [p.name for p in tailored_cv.projects],
            "selected_publications": [p.title for p in tailored_cv.publications],
            "pdf_compiled": pdf_compiled,
            "compiler_message": compile_msg
        }

        # Save application record
        app_db = GeneratedApplicationDB(
            id=app_id,
            job_id=job_id,
            company_name=job.company_name,
            job_title=job.job_title,
            tex_path=str(tex_path),
            pdf_path=str(pdf_path) if pdf_compiled else None,
            cover_letter_text=f"{cover_letter.opening}\n\n" + "\n\n".join(cover_letter.body_paragraphs) + f"\n\n{cover_letter.closing}",
            metadata_json=json.dumps(meta_dict)
        )
        self.repo.save_application(app_db)

        # Also write metadata.json to output directory
        (job_dir / "metadata.json").write_text(json.dumps(meta_dict, indent=2), encoding="utf-8")

        return {
            "application_id": app_id,
            "company_name": job.company_name,
            "job_title": job.job_title,
            "tex_path": tex_path,
            "pdf_path": pdf_path if pdf_compiled else None,
            "pdf_compiled": pdf_compiled,
            "compiler_message": compile_msg,
            "cover_letter_tex_path": cl_tex_path,
            "cover_letter_pdf_path": cl_pdf_path if cl_compiled else None,
            "cover_letter": cover_letter,
            "tailored_cv": tailored_cv,
            "verification_result": verification_result,
            "metadata": meta_dict
        }

    def refine_application(
        self,
        current_result: Dict[str, Any],
        user_instruction: str,
        analysis: JobAnalysisResult
    ) -> Tuple[Dict[str, Any], str]:
        """
        Applies candidate feedback/corrections to current CV and/or Cover Letter,
        re-verifies claims, re-renders LaTeX, recompiles PDF, and updates database records.
        Returns (updated_result_dict, assistant_reply_message).
        """
        job = analysis.job_requirements
        current_cv: TailoredCV = current_result["tailored_cv"]
        current_cl: Optional[CoverLetter] = current_result.get("cover_letter")

        instr_lower = user_instruction.lower()
        affects_cl = any(k in instr_lower for k in ["cover letter", "coverletter", "letter", "salutation", "sign off", "sign-off", "opening paragraph", "closing paragraph"])
        affects_cv = any(k in instr_lower for k in ["resume", "cv", "bullet", "bullets", "summary", "project", "projects", "skill", "skills", "experience", "education"])

        # Default to CV if neither specifically mentioned
        if not affects_cl and not affects_cv:
            affects_cv = True

        changes_made = []

        # 1. Refine CV
        if affects_cv:
            refined_cv = self.cv_gen.refine(
                current_cv=current_cv,
                user_instruction=user_instruction,
                job=job,
                analysis=analysis,
                evidence=analysis.retrieved_evidence
            )
            # Re-verify claims
            all_chunks, _ = self.indexer.scan_and_chunk()
            verification_result = self.verifier.verify_cv(cv=refined_cv, authoritative_evidence=all_chunks)

            # Re-render LaTeX CV
            tex_content = self.renderer.render_cv(refined_cv)
            tex_path = Path(current_result["tex_path"])
            tex_path.write_text(tex_content, encoding="utf-8")

            # Recompile PDF
            pdf_path = Path(current_result["pdf_path"]) if current_result.get("pdf_path") else tex_path.with_suffix(".pdf")
            pdf_compiled, compile_msg = self.compiler.compile(tex_content=tex_content, output_pdf_path=pdf_path)

            current_result["tailored_cv"] = refined_cv
            current_result["tex_path"] = tex_path
            current_result["pdf_path"] = pdf_path if pdf_compiled else None
            current_result["pdf_compiled"] = pdf_compiled
            current_result["verification_result"] = verification_result
            changes_made.append("tailored resume (LaTeX & PDF)")

        # 2. Refine Cover Letter
        if affects_cl and current_cl:
            refined_cl = self.cl_gen.refine(
                current_letter=current_cl,
                user_instruction=user_instruction,
                job=job,
                analysis=analysis
            )
            cl_tex_content = self.renderer.render_cover_letter(refined_cl)
            cl_tex_path = Path(current_result["cover_letter_tex_path"])
            cl_tex_path.write_text(cl_tex_content, encoding="utf-8")

            cl_pdf_path = cl_tex_path.with_suffix(".pdf")
            cl_compiled, _ = self.compiler.compile(tex_content=cl_tex_content, output_pdf_path=cl_pdf_path)

            current_result["cover_letter"] = refined_cl
            current_result["cover_letter_tex_path"] = cl_tex_path
            current_result["cover_letter_pdf_path"] = cl_pdf_path if cl_compiled else None
            changes_made.append("tailored cover letter")

        # 3. Update Database Record
        app_id = current_result.get("application_id")
        if app_id:
            try:
                cl_obj = current_result.get("cover_letter")
                cl_text = f"{cl_obj.opening}\n\n" + "\n\n".join(cl_obj.body_paragraphs) + f"\n\n{cl_obj.closing}" if cl_obj else None
                meta_dict = current_result.get("metadata", {})
                if "verification_result" in current_result:
                    meta_dict["verified"] = current_result["verification_result"].is_valid
                    meta_dict["unsupported_claims"] = current_result["verification_result"].unsupported_claims
                app_db = GeneratedApplicationDB(
                    id=app_id,
                    job_id=str(uuid.uuid4()),
                    company_name=job.company_name,
                    job_title=job.job_title,
                    tex_path=str(current_result["tex_path"]),
                    pdf_path=str(current_result["pdf_path"]) if current_result.get("pdf_compiled") else None,
                    cover_letter_text=cl_text,
                    metadata_json=json.dumps(meta_dict)
                )
                self.repo.save_application(app_db)
            except Exception as e:
                logger.warning("Could not persist updated application to database: %s", e)

        explanation = f"✅ Applied your corrections to your {' and '.join(changes_made)}! All factual claims were re-verified against your knowledge base, and the updated files are ready to preview and download below."
        return current_result, explanation

    def get_generated_applications(self) -> List[GeneratedApplicationDB]:
        """Returns history of all generated applications."""
        return self.repo.get_all_applications()

# Global service instance
application_service = ApplicationService()
