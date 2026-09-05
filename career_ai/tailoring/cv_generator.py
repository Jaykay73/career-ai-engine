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
    TailoredCertification,
    TailoredCustomSection,
    TailoredCustomSectionItem
)
from career_ai.tailoring.selector import EvidenceSelector, evidence_selector
from career_ai.retrieval.rrf import RankedEvidence
from career_ai.llm.base import LLMProvider
from career_ai.llm.factory import get_llm_provider
from career_ai.llm.prompts import (
    TAILORING_SYSTEM_PROMPT,
    TAILORING_USER_PROMPT,
    CV_REFINEMENT_SYSTEM_PROMPT,
    CV_REFINEMENT_USER_PROMPT
)
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

    def refine(
        self,
        current_cv: TailoredCV,
        user_instruction: str,
        job: JobRequirements,
        analysis: JobAnalysisResult,
        evidence: Optional[List[RankedEvidence]] = None
    ) -> TailoredCV:
        """
        Refines a previously tailored CV based on candidate's feedback.
        Enforces that all invariants and evidence constraints remain strictly preserved.
        """
        logger.info("Refining tailored CV for %s with instruction: %s", job.job_title, user_instruction[:80])

        prioritized_skills = current_cv.skills or self.selector.prioritize_skills(job)
        relevant_pubs = current_cv.publications or self.selector.select_relevant_publications(job, max_publications=3)

        eff_evidence = evidence or analysis.retrieved_evidence
        evidence_text_blocks = []
        for rank, ev in enumerate(eff_evidence[:25], start=1):
            evidence_text_blocks.append(
                f"[Evidence ID: {ev.chunk.id}]\n"
                f"Source: {ev.chunk.title} ({ev.chunk.source_type} / {ev.chunk.section})\n"
                f"Content: {ev.chunk.text}\n"
            )
        evidence_context = "\n".join(evidence_text_blocks)

        prompt = CV_REFINEMENT_USER_PROMPT.format(
            user_instruction=user_instruction,
            job_title=job.job_title,
            company_name=job.company_name,
            current_cv_json=current_cv.model_dump_json(indent=2),
            retrieved_evidence_text=evidence_context
        )

        try:
            refined = self.llm.generate_structured(
                prompt=prompt,
                schema=TailoredCV,
                system_prompt=CV_REFINEMENT_SYSTEM_PROMPT,
                temperature=0.1
            )
            refined = self._enforce_invariants(refined, prioritized_skills, relevant_pubs)
            return refined

        except LLMAuthenticationError:
            logger.warning("LLM key absent during CV refinement. Applying heuristic adjustments.")
            return self._heuristic_refine_cv(current_cv, user_instruction)
        except Exception as e:
            logger.error("LLM CV refinement failed: %s. Using heuristic adjustment.", e)
            return self._heuristic_refine_cv(current_cv, user_instruction)

    def _heuristic_refine_cv(self, current_cv: TailoredCV, user_instruction: str) -> TailoredCV:
        """Heuristically applies common candidate adjustments when offline."""
        cv_copy = current_cv.model_copy(deep=True)
        instr_lower = user_instruction.lower()

        # Check for Power BI / Excel / Analytics emphasis
        if any(k in instr_lower for k in ["power bi", "powerbi", "excel", "power query", "power pivot", "dax", "analytics"]):
            if cv_copy.summary:
                if "Power BI" not in cv_copy.summary:
                    cv_copy.summary = f"Data & AI Engineer with deep expertise in Power BI, advanced Excel modeling, automated ETL, and production machine learning. {cv_copy.summary}"
            bi_skills = ["Power BI", "DAX", "Power Query", "Power Pivot", "Microsoft Excel", "Star Schema Modeling", "KPI Dashboards"]
            has_bi_cat = any("analytics" in c.category_name.lower() or "bi" in c.category_name.lower() for c in cv_copy.skills)
            if not has_bi_cat:
                cv_copy.skills.insert(1, TailoredSkillCategory(category_name="Data Analytics & BI", skills=bi_skills))
            if cv_copy.experiences:
                cv_copy.experiences[0].bullets.insert(
                    0,
                    TailoredBullet(
                        text="Engineered automated business analytics pipelines and interactive Power BI dashboards utilizing DAX measures and Power Query ETL.",
                        evidence_ids=["skill:technical-skills:data_analytics_and_bi"]
                    )
                )

        # Check for Time Series emphasis
        if any(k in instr_lower for k in ["time series", "forecasting", "arima", "sarima"]):
            ts_skills = ["Time Series Modeling", "ARIMA / SARIMA", "Exponential Smoothing (Holt-Winters)", "Forecasting", "Stationarity (ADF/KPSS)"]
            has_ts_cat = any("time series" in c.category_name.lower() or "forecasting" in c.category_name.lower() for c in cv_copy.skills)
            if not has_ts_cat:
                cv_copy.skills.insert(2, TailoredSkillCategory(category_name="Time Series & Forecasting", skills=ts_skills))
            if cv_copy.experiences:
                cv_copy.experiences[0].bullets.append(
                    TailoredBullet(
                        text="Developed time series forecasting and predictive modeling workflows using ARIMA and walk-forward cross-validation.",
                        evidence_ids=["skill:technical-skills:time_series_and_forecasting"]
                    )
                )

        # Check for adding verified Projects
        if any(k in instr_lower for k in ["churn", "attrition", "customer churn"]):
            if not any("churn" in p.name.lower() for p in cv_copy.projects):
                cv_copy.projects.insert(
                    0,
                    TailoredProject(
                        name="Bank Customer Churn Predictor",
                        technologies="Scikit-learn, Gradient Boosting, Streamlit, Pandas, Python",
                        bullets=[
                            TailoredBullet(
                                text="Trained and tuned Gradient Boosting classifiers on banking records to identify customer attrition indicators with actionable feature importance attribution.",
                                evidence_ids=["project:churn-predictor:architecture"]
                            ),
                            TailoredBullet(
                                text="Engineered an interactive Streamlit inference web application providing real-time risk scoring and feature attribution rankings for prospective customers.",
                                evidence_ids=["project:churn-predictor:results"]
                            )
                        ]
                    )
                )

        if any(k in instr_lower for k in ["mri", "brain tumor", "tumor"]):
            if not any("mri" in p.name.lower() or "tumor" in p.name.lower() for p in cv_copy.projects):
                cv_copy.projects.insert(
                    0,
                    TailoredProject(
                        name="Brain Tumor MRI Classifier",
                        technologies="TensorFlow, Keras, EfficientNet-B0, Transfer Learning, Streamlit",
                        bullets=[
                            TailoredBullet(
                                text="Trained deep convolutional transfer learning architecture (EfficientNet-B0) to classify 4 diagnostic brain tumor scan categories with medical data augmentations.",
                                evidence_ids=["project:brain-tumor-mri:architecture"]
                            ),
                            TailoredBullet(
                                text="Applied post-training model quantization for low-latency edge deployment and packaged an interactive diagnostic inference application on Streamlit.",
                                evidence_ids=["project:brain-tumor-mri:results"]
                            )
                        ]
                    )
                )

        if any(k in instr_lower for k in ["fraud", "credit card fraud"]):
            if not any("fraud" in p.name.lower() for p in cv_copy.projects):
                cv_copy.projects.insert(
                    0,
                    TailoredProject(
                        name="Credit Card Fraud Detection",
                        technologies="Scikit-learn, XGBoost, SMOTE, Imbalanced-Learn, Pandas",
                        bullets=[
                            TailoredBullet(
                                text="Implemented anomaly detection pipelines addressing extreme class imbalance using SMOTE and cost-sensitive gradient boosted decision trees.",
                                evidence_ids=["project:fraud-detection:solution"]
                            ),
                            TailoredBullet(
                                text="Optimized precision-recall thresholds to capture fraudulent transactions with high sensitivity while minimizing false-positive alert fatigue.",
                                evidence_ids=["project:fraud-detection:results"]
                            )
                        ]
                    )
                )

        if any(k in instr_lower for k in ["pidgin", "nlp translation", "vernacular"]):
            if not any("pidgin" in p.name.lower() for p in cv_copy.projects):
                cv_copy.projects.insert(
                    0,
                    TailoredProject(
                        name="Nigerian Pidgin NLP Sentiment & Translation",
                        technologies="PyTorch, Hugging Face Transformers, Afro-XLMR, NLP",
                        bullets=[
                            TailoredBullet(
                                text="Fine-tuned transformer models on low-resource Nigerian Pidgin corpora for sentiment classification and vernacular language understanding.",
                                evidence_ids=["project:pidgin-predictor:solution"]
                            ),
                            TailoredBullet(
                                text="Engineered specialized tokenization and preprocessing routines to handle vernacular dialect shifts and code-switching.",
                                evidence_ids=["project:pidgin-predictor:results"]
                            )
                        ]
                    )
                )

        # Check for adding verified Experiences or Custom Sections
        if any(k in instr_lower for k in ["teach", "teaching", "mentor", "mentorship", "tutoring", "tutor"]):
            if "section" in instr_lower or "custom" in instr_lower:
                if not any("teaching" in s.title.lower() or "mentorship" in s.title.lower() for s in cv_copy.custom_sections):
                    cv_copy.custom_sections.append(
                        TailoredCustomSection(
                            title="Teaching & Technical Mentorship",
                            items=[
                                TailoredCustomSectionItem(
                                    heading="Technical Mentorship & Community Volunteering",
                                    subheading="Python & Machine Learning Mentor",
                                    date="2024 -- Present",
                                    bullets=[
                                        TailoredBullet(
                                            text="Organize and lead hands-on technical workshops on Python, data structures, and machine learning fundamentals for aspiring engineers.",
                                            evidence_ids=["experience:teaching:responsibilities"]
                                        ),
                                        TailoredBullet(
                                            text="Provide code reviews, algorithmic debugging guidance, and career mentorship while authoring educational AI guides on Medium.",
                                            evidence_ids=["experience:teaching:achievements"]
                                        )
                                    ]
                                )
                            ]
                        )
                    )
            else:
                if not any("mentorship" in e.company.lower() for e in cv_copy.experiences):
                    cv_copy.experiences.append(
                        TailoredExperience(
                            company="Technical Mentorship & Community Volunteering",
                            role="Python & Machine Learning Mentor",
                            period="2024 -- Present",
                            location="Hybrid",
                            bullets=[
                                TailoredBullet(
                                    text="Organize and lead hands-on technical workshops on Python, data structures, and machine learning fundamentals for aspiring engineers.",
                                    evidence_ids=["experience:teaching:responsibilities"]
                                ),
                                TailoredBullet(
                                    text="Provide code reviews, algorithmic debugging guidance, and career mentorship while authoring educational AI guides on Medium.",
                                    evidence_ids=["experience:teaching:achievements"]
                                )
                            ]
                        )
                    )

        if any(k in instr_lower for k in ["freelance", "consulting", "upwork", "client solutions"]):
            if "section" in instr_lower or "custom" in instr_lower:
                if not any("freelance" in s.title.lower() or "consulting" in s.title.lower() for s in cv_copy.custom_sections):
                    cv_copy.custom_sections.append(
                        TailoredCustomSection(
                            title="Freelance & Consulting",
                            items=[
                                TailoredCustomSectionItem(
                                    heading="Freelance AI & Software Engineering",
                                    subheading="AI Engineer & Technical Consultant",
                                    date="2024 -- Present",
                                    bullets=[
                                        TailoredBullet(
                                            text="Consult with clients on applied AI architecture, RAG pipelines, and automated LLM workflows using FastAPI and modern LLM APIs.",
                                            evidence_ids=["experience:freelance:responsibilities"]
                                        ),
                                        TailoredBullet(
                                            text="Build custom machine learning models, automated data scrapers, and interactive Streamlit web dashboard interfaces.",
                                            evidence_ids=["experience:freelance:achievements"]
                                        )
                                    ]
                                )
                            ]
                        )
                    )
            else:
                if not any("freelance" in e.company.lower() for e in cv_copy.experiences):
                    cv_copy.experiences.append(
                        TailoredExperience(
                            company="Freelance AI & Software Engineering",
                            role="AI Engineer & Technical Consultant",
                            period="2024 -- Present",
                            location="Remote",
                            bullets=[
                                TailoredBullet(
                                    text="Consult with clients on applied AI architecture, RAG pipelines, and automated LLM workflows using FastAPI and modern LLM APIs.",
                                    evidence_ids=["experience:freelance:responsibilities"]
                                ),
                                TailoredBullet(
                                    text="Build custom machine learning models, automated data scrapers, and interactive Streamlit web dashboard interfaces.",
                                    evidence_ids=["experience:freelance:achievements"]
                                )
                            ]
                        )
                    )

        # Check for Publications
        if any(k in instr_lower for k in ["publication", "article", "medium", "seahorse", "bpe", "accuracy"]):
            if any(k in instr_lower for k in ["seahorse", "bpe"]):
                if not any("seahorse" in p.title.lower() for p in cv_copy.publications):
                    cv_copy.publications.insert(
                        0,
                        TailoredPublication(
                            title="Why The Seahorse Emoji Breaks Modern AI Tokenizers",
                            url="https://medium.com/@jermaine73/why-the-seahorse-emoji-breaks-modern-ai-tokenizers-bpe-internals-uncovered-e1896d8b6dae",
                            summary="Technical deep-dive into Byte Pair Encoding (BPE) subword segmentation vulnerabilities."
                        )
                    )
            if any(k in instr_lower for k in ["accuracy", "lying"]):
                if not any("accuracy" in p.title.lower() for p in cv_copy.publications):
                    cv_copy.publications.insert(
                        0,
                        TailoredPublication(
                            title="Why Accuracy is Lying to You in Machine Learning",
                            url="https://medium.com/@jermaine73/why-accuracy-is-lying-to-you-in-machine-learning-and-what-to-use-instead-6178c77727df",
                            summary="Statistical analysis of classification metrics, precision-recall trade-offs, and PR-AUC."
                        )
                    )

        # Check for shortening request
        if any(k in instr_lower for k in ["shorten", "trim", "concise", "brief", "less"]):
            if cv_copy.summary and len(cv_copy.summary.split(".")) > 3:
                cv_copy.summary = ".".join(cv_copy.summary.split(".")[:2]).strip() + "."
            for exp in cv_copy.experiences:
                if len(exp.bullets) > 3:
                    exp.bullets = exp.bullets[:3]

        return self._enforce_invariants(cv_copy, cv_copy.skills, cv_copy.publications)

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
