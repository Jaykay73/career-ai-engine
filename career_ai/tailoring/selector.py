"""
Evidence-Grounded Entity Selector.
Selects the most relevant projects, experiences, skills, and publications
for a target job using hybrid retrieval scores while strictly preserving verified facts.
"""

from typing import List, Dict, Set, Optional, Tuple, Any
from career_ai.jobs.schemas import JobRequirements
from career_ai.retrieval.hybrid import HybridRetriever, hybrid_retriever
from career_ai.retrieval.rrf import RankedEvidence
from career_ai.database.repository import repository, Repository
from career_ai.tailoring.schemas import (
    TailoredSkillCategory,
    TailoredPublication,
    TailoredProject,
    TailoredBullet,
    TailoredExperience
)
from career_ai.core.logging import get_logger

logger = get_logger("selector")

class EvidenceSelector:
    """Selects and prioritizes verified candidate assets aligned with target job requirements."""

    def __init__(self, retriever: Optional[HybridRetriever] = None, repo: Optional[Repository] = None):
        self.retriever = retriever or hybrid_retriever
        self.repo = repo or repository

    def select_relevant_projects(
        self,
        job: JobRequirements,
        min_projects: int = 3,
        max_projects: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieves and ranks projects based on hybrid retrieval against the job title,
        summary, and required skills.
        """
        query = f"{job.job_title} {job.role_summary} {' '.join(job.all_target_skills)}"
        project_hits = self.retriever.search(
            query=query,
            top_k_bm25=30,
            top_k_vector=30,
            top_k_rrf=20,
            source_type_filter="project"
        )

        # Group hits by project source_id and aggregate RRF scores
        project_scores: Dict[str, float] = {}
        project_chunks: Dict[str, List[RankedEvidence]] = {}

        for hit in project_hits:
            pid = hit.chunk.source_id
            project_scores[pid] = project_scores.get(pid, 0.0) + hit.rrf_score
            project_chunks.setdefault(pid, []).append(hit)

        # Fallback to standard showcase projects if too few returned
        preferred_order = ["bitcheck", "resume-optimizer", "lockedin", "cinematch", "pidgin-predictor", "brain-tumor-mri", "diabetic-retinopathy", "fraud-detection"]
        for p in preferred_order:
            if p not in project_scores:
                project_scores[p] = 0.001

        # Sort projects by relevance score
        sorted_pids = sorted(project_scores.keys(), key=lambda p: project_scores[p], reverse=True)
        selected_pids = sorted_pids[:max_projects]

        selected_projects = []
        for pid in selected_pids:
            chunks = project_chunks.get(pid, [])
            selected_projects.append({
                "project_id": pid,
                "score": project_scores[pid],
                "evidence_chunks": chunks
            })

        logger.info("Selected %d projects for job %s: %s", len(selected_projects), job.job_title, selected_pids)
        return selected_projects

    def select_relevant_publications(
        self,
        job: JobRequirements,
        max_publications: int = 3
    ) -> List[TailoredPublication]:
        """
        Retrieves publications most relevant to the target job domains (e.g. LLM, metrics, vision).
        """
        query = f"{job.job_title} {' '.join(job.ml_domains)} {' '.join(job.all_target_skills)}"
        pub_hits = self.retriever.search(
            query=query,
            top_k_bm25=15,
            top_k_vector=15,
            top_k_rrf=10,
            source_type_filter="publication"
        )

        selected_pubs: List[TailoredPublication] = []
        seen_titles = set()

        for hit in pub_hits:
            meta = hit.chunk.metadata
            title = meta.get("title") or hit.chunk.title
            if title in seen_titles:
                continue
            seen_titles.add(title)

            selected_pubs.append(TailoredPublication(
                title=title,
                url=meta.get("url", ""),
                summary=meta.get("abstract") or hit.chunk.text,
                platform=meta.get("platform", "Artificial Intelligence in Plain English (Medium)"),
                evidence_id=hit.chunk.id
            ))

            if len(selected_pubs) >= max_publications:
                break

        return selected_pubs

    def prioritize_skills(self, job: JobRequirements) -> List[TailoredSkillCategory]:
        """
        Organizes technical skills, prioritizing skills explicitly requested by the job
        to appear first within their category.
        """
        target_skills_lower = {s.lower() for s in job.all_target_skills}

        # Canonical skills taxonomy
        base_categories = [
            ("Languages", ["Python (Proficient)", "C++", "JavaScript (ES6+)", "TypeScript", "SQL (PostgreSQL, SQLite)"]),
            ("Frameworks & Libraries", ["PyTorch", "TensorFlow", "Scikit-learn", "ONNX / ONNX Runtime", "Keras", "OpenCV", "Hugging Face Transformers", "Model Quantization (INT8 / FP16)", "Transfer Learning"]),
            ("NLP, LLMs & RAG", ["SentenceTransformers", "FAISS", "Pinecone", "RAG Pipelines", "LangChain", "DeepSeek LLM", "Gemini 2.0 Flash", "Vector Search", "Prompt Engineering", "LLM Evaluation", "Agentic Workflows", "NER", "Tokenization"]),
            ("Computer Vision & Forensics", ["Computer Vision", "EfficientNet-B0", "OpenCV", "Tesseract OCR", "C2PA Content Credentials", "Grad-CAM Explainability", "Metadata Forensics (EXIF/XMP)"]),
            ("Backend & DevOps", ["FastAPI", "Docker", "Kubernetes", "Linux", "AWS", "GCP", "Vercel", "Hugging Face Spaces", "Streamlit", "Git / GitHub Actions CI/CD", "REST APIs", "Node.js", "Flask"]),
            ("Frontend & Tools", ["React 19", "Next.js", "Streamlit", "Tailwind CSS", "Framer Motion", "Jupyter Notebooks"])
        ]

        tailored_categories: List[TailoredSkillCategory] = []
        for cat_name, skill_list in base_categories:
            # Sort skills: ones requested in target_skills come first
            prioritized = sorted(
                skill_list,
                key=lambda s: any(t in s.lower() for t in target_skills_lower),
                reverse=True
            )
            tailored_categories.append(TailoredSkillCategory(category_name=cat_name, skills=prioritized))

        return tailored_categories

# Global selector
evidence_selector = EvidenceSelector()
