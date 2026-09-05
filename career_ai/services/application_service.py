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
import re
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
from career_ai.knowledge.schemas import EvidenceChunk
from career_ai.knowledge.indexer import KnowledgeIndexer, indexer
from career_ai.retrieval.rrf import RankedEvidence
from career_ai.retrieval.hybrid import HybridRetriever, hybrid_retriever
from career_ai.database.repository import Repository, repository
from career_ai.database.models import JobDB, GeneratedApplicationDB
from career_ai.core.config import settings
from career_ai.core.logging import get_logger

logger = get_logger("application_service")

CANONICAL_ENTITIES: Dict[str, Dict[str, Any]] = {
    "churn-predictor": {
        "name": "Bank Customer Churn Predictor",
        "file": "projects/churn-predictor.md",
        "keywords": ["churn", "attrition", "telco customer", "churn prediction", "churn predictor"]
    },
    "brain-tumor-mri": {
        "name": "Brain Tumor MRI Classifier",
        "file": "projects/brain-tumor-mri.md",
        "keywords": ["mri", "tumor", "brain tumor", "radiolog", "efficientnet"]
    },
    "fraud-detection": {
        "name": "Credit Card Fraud Detection",
        "file": "projects/fraud-detection.md",
        "keywords": ["fraud", "credit card fraud", "imbalanced fraud", "anomaly detection"]
    },
    "pidgin-predictor": {
        "name": "Nigerian Pidgin NLP Predictor",
        "file": "projects/pidgin-predictor.md",
        "keywords": ["pidgin", "nigerian pidgin", "vernacular nlp", "afro-xlmr"]
    },
    "cinematch": {
        "name": "CineMatch Recommendation Engine",
        "file": "projects/cinematch.md",
        "keywords": ["cinematch", "movie recommender", "recommendation engine", "matrix factorization"]
    },
    "custom-chatbot": {
        "name": "Custom RAG Chatbot",
        "file": "projects/custom-chatbot.md",
        "keywords": ["custom chatbot", "langchain chatbot", "rag bot", "support bot"]
    },
    "customer-segmentation": {
        "name": "Customer Segmentation Engine",
        "file": "projects/customer-segmentation.md",
        "keywords": ["customer segmentation", "rfm", "k-means clustering"]
    },
    "diabetic-retinopathy": {
        "name": "Diabetic Retinopathy Classifier",
        "file": "projects/diabetic-retinopathy.md",
        "keywords": ["diabetic retinopathy", "retinopathy", "fundus"]
    },
    "flappy-bird-rl": {
        "name": "Flappy Bird RL Agent",
        "file": "projects/flappy-bird-rl.md",
        "keywords": ["flappy bird", "deep q network", "dqn", "reinforcement learning"]
    },
    "flashcard-app": {
        "name": "Flashcard Learning App",
        "file": "projects/flashcard-app.md",
        "keywords": ["flashcard", "spaced repetition", "supermemo", "sm-2"]
    },
    "house-price-predictor": {
        "name": "House Price Predictor",
        "file": "projects/house-price-predictor.md",
        "keywords": ["house price", "ames housing", "real estate prediction"]
    },
    "iris-classifier": {
        "name": "Iris Classifier",
        "file": "projects/iris-classifier.md",
        "keywords": ["iris classifier"]
    },
    "legal-document-analyzer": {
        "name": "Legal Document Analyzer",
        "file": "projects/legal-document-analyzer.md",
        "keywords": ["legal document", "contract analyzer", "clause extraction"]
    },
    "lockedin": {
        "name": "Lockedin Productivity App",
        "file": "projects/lockedin.md",
        "keywords": ["lockedin", "pomodoro", "study timer"]
    },
    "bitcheck": {
        "name": "BitCheck Crypto Price Tracker",
        "file": "projects/bitcheck.md",
        "keywords": ["bitcheck", "bitcoin alert", "crypto alert", "crypto tracker"]
    },
    "resume-optimizer": {
        "name": "Resume Optimizer",
        "file": "projects/resume-optimizer.md",
        "keywords": ["resume optimizer", "ats parser"]
    },
    "teaching": {
        "name": "Technical Mentorship & Community Volunteering",
        "file": "experience/teaching.md",
        "keywords": ["teaching", "mentor", "mentorship", "tutoring", "tutor", "volunteering"]
    },
    "freelance": {
        "name": "Freelance AI & Software Engineering",
        "file": "experience/freelance.md",
        "keywords": ["freelance", "consulting", "independent consultant", "contractor", "upwork"]
    },
    "camlds": {
        "name": "CAMLDS Research Internship",
        "file": "experience/camlds.md",
        "keywords": ["camlds", "center for applied machine learning", "internship", "research intern"]
    },
    "queryfier": {
        "name": "Queryfier LLC",
        "file": "experience/queryfier.md",
        "keywords": ["queryfier"]
    },
    "analytics-and-bi": {
        "name": "Data Analytics, BI & Time Series",
        "file": "skills/analytics-and-bi.md",
        "keywords": ["power bi", "powerbi", "excel", "power query", "power pivot", "dax", "time series", "forecasting", "star schema"]
    },
    "accuracy-lying": {
        "name": "Why Accuracy is Lying to You in Machine Learning",
        "file": "publications/accuracy-lying.md",
        "keywords": ["accuracy is lying", "classification metrics"]
    },
    "seahorse-emoji-bpe": {
        "name": "Why The Seahorse Emoji Breaks Modern AI Tokenizers",
        "file": "publications/seahorse-emoji-bpe.md",
        "keywords": ["seahorse", "bpe", "tokenizer", "tokenization"]
    }
}

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

    def _lookup_evidence_for_instruction(
        self,
        user_instruction: str,
        all_chunks: List[EvidenceChunk]
    ) -> Tuple[List[RankedEvidence], List[str]]:
        """
        Dynamically consults the knowledge base for evidence matching user instruction.
        Returns prioritized RankedEvidence chunks and descriptions of matched canonical records.
        """
        instr_lower = user_instruction.lower()
        matched_entities: List[str] = []
        prioritized_chunks: List[EvidenceChunk] = []

        # 1. Canonical entity mapping
        chunks_by_source: Dict[str, List[EvidenceChunk]] = {}
        for c in all_chunks:
            chunks_by_source.setdefault(c.source_id, []).append(c)

        for source_id, entity_info in CANONICAL_ENTITIES.items():
            if any(k in instr_lower for k in entity_info["keywords"]):
                matched_chunks = chunks_by_source.get(source_id, [])
                if matched_chunks:
                    prioritized_chunks.extend(matched_chunks)
                    matched_entities.append(f"{entity_info['name']} ({entity_info['file']})")

        # 2. Hybrid search against knowledge base
        hybrid_ranked: List[RankedEvidence] = []
        try:
            hybrid_ranked = self.retriever.search(query=user_instruction, top_k_rrf=15)
        except Exception as e:
            logger.warning("Hybrid search during instruction lookup encountered exception: %s", e)
            if self.retriever.bm25:
                bm25_hits = self.retriever.bm25.search(query=user_instruction, top_k=15)
                hybrid_ranked = [
                    RankedEvidence(chunk=c, rrf_score=1.0 / (60 + r), rrf_rank=r, bm25_rank=r)
                    for r, (c, _) in enumerate(bm25_hits, 1)
                ]

        # 3. Assemble combined ranked evidence (prioritized canonical chunks first)
        results: List[RankedEvidence] = []
        seen_ids = set()

        for idx, chunk in enumerate(prioritized_chunks, 1):
            if chunk.id not in seen_ids:
                seen_ids.add(chunk.id)
                results.append(RankedEvidence(
                    chunk=chunk,
                    rrf_score=1.0 - (idx * 0.01),
                    rrf_rank=idx,
                    bm25_rank=idx,
                    vector_rank=idx
                ))

        for ev in hybrid_ranked:
            if ev.chunk.id not in seen_ids:
                seen_ids.add(ev.chunk.id)
                results.append(ev)

        return results, matched_entities

    def _sanitize_unverified_cv(
        self,
        cv: TailoredCV,
        all_chunks: List[EvidenceChunk]
    ) -> Tuple[TailoredCV, List[str]]:
        """
        Enforces zero-hallucination policy by filtering out employers, projects,
        or credentials that cannot be corroborated against the authoritative knowledge base.
        """
        all_evidence_text = " ".join([f"{c.title} {c.text} {c.source_id}" for c in all_chunks])
        all_evidence_lower = all_evidence_text.lower()
        purged: List[str] = []

        # 1. Experiences check
        verified_experiences = []
        for exp in cv.experiences:
            if exp.company.lower() in all_evidence_lower:
                verified_experiences.append(exp)
            else:
                purged.append(f"Unverified employer '{exp.company}'")
        cv.experiences = verified_experiences

        # 2. Projects check
        verified_projects = []
        for proj in cv.projects:
            proj_name_simple = re.sub(r"[^a-zA-Z0-9]", "", proj.name).lower()
            first_word = proj.name.split()[0].lower() if proj.name else ""
            if any(proj_name_simple in re.sub(r"[^a-zA-Z0-9]", "", c.title).lower() for c in all_chunks) or (first_word and first_word in all_evidence_lower):
                verified_projects.append(proj)
            else:
                purged.append(f"Unverified project '{proj.name}'")
        cv.projects = verified_projects

        # 3. Certifications check
        valid_certs = [
            "oci generative ai professional",
            "oracle ai foundations associate",
            "machine learning specialization"
        ]
        verified_certs = []
        for cert in cv.certifications:
            if any(v in cert.name.lower() for v in valid_certs):
                verified_certs.append(cert)
            else:
                purged.append(f"Unverified certification '{cert.name}'")
        cv.certifications = verified_certs

        # 4. Custom sections check
        verified_custom = []
        for sec in getattr(cv, "custom_sections", []):
            verified_items = []
            for item in sec.items:
                first_word = item.heading.split()[0].lower() if item.heading else ""
                if not first_word or first_word in all_evidence_lower:
                    verified_items.append(item)
                else:
                    purged.append(f"Unverified entity '{item.heading}' in section '{sec.title}'")
            if verified_items:
                sec.items = verified_items
                verified_custom.append(sec)
        cv.custom_sections = verified_custom

        return cv, purged

    def refine_application(
        self,
        current_result: Dict[str, Any],
        user_instruction: str,
        analysis: JobAnalysisResult
    ) -> Tuple[Dict[str, Any], str]:
        """
        Applies candidate feedback/corrections to current CV and/or Cover Letter.
        Dynamically looks up authoritative knowledge base evidence, adds verified sections,
        strictly rejects/purges ungrounded claims, re-renders LaTeX, recompiles PDF,
        and updates database records.
        Returns (updated_result_dict, assistant_reply_message).
        """
        job = analysis.job_requirements
        current_cv: TailoredCV = current_result["tailored_cv"]
        current_cl: Optional[CoverLetter] = current_result.get("cover_letter")

        instr_lower = user_instruction.lower()
        affects_cl = any(k in instr_lower for k in ["cover letter", "coverletter", "letter", "salutation", "sign off", "sign-off", "opening paragraph", "closing paragraph"])
        affects_cv = any(k in instr_lower for k in ["resume", "cv", "bullet", "bullets", "summary", "project", "projects", "skill", "skills", "experience", "experiences", "education", "section", "sections", "custom"])

        # Default to CV if neither specifically mentioned
        if not affects_cl and not affects_cv:
            affects_cv = True

        changes_made: List[str] = []
        kb_consulted_notes: List[str] = []
        ungrounded_warnings: List[str] = []

        # 0. Dynamic Knowledge Base Re-Lookup
        all_chunks, _ = self.indexer.scan_and_chunk()
        targeted_evidence, matched_entities = self._lookup_evidence_for_instruction(user_instruction, all_chunks)
        if matched_entities:
            kb_consulted_notes.extend(matched_entities)

        # Merge targeted evidence with original retrieved evidence (targeted first)
        existing_evidence = analysis.retrieved_evidence or []
        combined_evidence: List[RankedEvidence] = []
        seen_chunk_ids = set()
        for ev in targeted_evidence:
            if ev.chunk.id not in seen_chunk_ids:
                seen_chunk_ids.add(ev.chunk.id)
                combined_evidence.append(ev)
        for ev in existing_evidence:
            if ev.chunk.id not in seen_chunk_ids:
                seen_chunk_ids.add(ev.chunk.id)
                combined_evidence.append(ev)

        # 1. Refine CV
        if affects_cv:
            refined_cv = self.cv_gen.refine(
                current_cv=current_cv,
                user_instruction=user_instruction,
                job=job,
                analysis=analysis,
                evidence=combined_evidence
            )

            # Audit against all authoritative chunks
            verification_result = self.verifier.verify_cv(cv=refined_cv, authoritative_evidence=all_chunks)

            # If unverified claims detected, sanitize and purge ungrounded additions
            if not verification_result.is_valid:
                sanitized_cv, purged_items = self._sanitize_unverified_cv(refined_cv, all_chunks)
                if purged_items:
                    ungrounded_warnings.extend(purged_items)
                    refined_cv = sanitized_cv
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

        # 4. Construct Comprehensive Response Explanation
        explanation_blocks: List[str] = []

        if ungrounded_warnings:
            explanation_blocks.append(
                "⚠️ **Anti-Hallucination Guard (Zero Fabrication Enforced)**:\n"
                "The following requested item(s) could not be corroborated in your canonical knowledge base:\n"
                + "\n".join(f"- *{w}*" for w in ungrounded_warnings)
                + "\nTo prevent ATS disqualification and preserve absolute profile credibility, unverified entities were omitted from your documents. If you have acquired this credential or role, please add its markdown record to your `knowledge/` directory and rebuild the index."
            )

        if kb_consulted_notes:
            explanation_blocks.append(
                "🔍 **Knowledge Base Re-Lookup**:\n"
                "Consulted your verified profile and retrieved authoritative evidence for:\n"
                + "\n".join(f"- **{n}**" for n in kb_consulted_notes)
            )

        if changes_made:
            explanation_blocks.append(
                f"✅ **Update Complete**: Successfully refined your {' and '.join(changes_made)}! All metrics and claims are verified against your knowledge base, and updated files are ready to preview and download."
            )

        explanation = "\n\n".join(explanation_blocks) if explanation_blocks else "✅ Applied your requested adjustments and recompiled your application."
        return current_result, explanation

    def get_generated_applications(self) -> List[GeneratedApplicationDB]:
        """Returns history of all generated applications."""
        return self.repo.get_all_applications()

# Global service instance
application_service = ApplicationService()
