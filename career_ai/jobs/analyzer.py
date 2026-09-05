"""
Job Requirements & Evidence Analyzer.
Matches extracted job requirements against the hybrid retrieval engine.
Classifies each requirement strictly as SUPPORTED or NOT_SUPPORTED_IN_KNOWLEDGE_BASE
without match percentages or candidate scoring.
"""

from typing import List, Dict, Set, Optional, Tuple
from career_ai.jobs.schemas import JobRequirements, RequirementAssessment, JobAnalysisResult
from career_ai.retrieval.hybrid import HybridRetriever, hybrid_retriever
from career_ai.retrieval.rrf import RankedEvidence
from career_ai.core.logging import get_logger

logger = get_logger("job_analyzer")

class JobAnalyzer:
    """Evaluates job requirements against verified knowledge base evidence."""

    def __init__(self, retriever: Optional[HybridRetriever] = None):
        self.retriever = retriever or hybrid_retriever

    def analyze(self, requirements: JobRequirements) -> JobAnalysisResult:
        """
        Takes structured JobRequirements, queries the knowledge base,
        and determines support for each requirement with complete provenance.
        """
        supported_list: List[RequirementAssessment] = []
        unsupported_list: List[RequirementAssessment] = []
        all_retrieved_evidence: List[RankedEvidence] = []
        seen_evidence_ids: Set[str] = set()

        # Gather all unique target requirements to assess
        target_items = []
        for s in requirements.all_target_skills:
            target_items.append((s, "skill"))
        for r in requirements.responsibilities[:5]:
            target_items.append((r, "responsibility"))
        if requirements.experience_years_requirement:
            target_items.append((requirements.experience_years_requirement, "experience"))

        for req_text, category in target_items:
            # Query hybrid retriever
            evidence_results = self.retriever.search(
                query=req_text,
                top_k_bm25=10,
                top_k_vector=10,
                top_k_rrf=5
            )

            # Record evidence for global review
            for ev in evidence_results:
                if ev.chunk.id not in seen_evidence_ids:
                    seen_evidence_ids.add(ev.chunk.id)
                    all_retrieved_evidence.append(ev)

            # Determine whether this requirement is supported by the knowledge base
            is_supported, explanation, matching_ids = self._evaluate_support(req_text, category, evidence_results)

            assessment = RequirementAssessment(
                requirement=req_text,
                category=category,
                is_supported=is_supported,
                evidence_chunk_ids=matching_ids,
                explanation=explanation,
                top_evidence=evidence_results[:3]
            )

            if is_supported:
                supported_list.append(assessment)
            else:
                unsupported_list.append(assessment)

        return JobAnalysisResult(
            job_requirements=requirements,
            supported_requirements=supported_list,
            unsupported_requirements=unsupported_list,
            retrieved_evidence=all_retrieved_evidence
        )

    def _evaluate_support(
        self,
        requirement: str,
        category: str,
        evidence: List[RankedEvidence]
    ) -> Tuple[bool, str, List[str]]:
        """
        Determines if a requirement is substantiated by the retrieved evidence.
        The knowledge base is authoritative. If a skill/tool appears in any chunk,
        it is supported.
        """
        req_lower = requirement.lower().strip()
        matched_chunk_ids = []

        # 1. Direct lexical or keyword presence in any retrieved chunk
        for ev in evidence:
            chunk_text = ev.chunk.text.lower()
            chunk_title = ev.chunk.title.lower()

            # Exact phrase or token match
            if req_lower in chunk_text or req_lower in chunk_title:
                matched_chunk_ids.append(ev.chunk.id)

        # 2. Check metadata fields (technologies, skills lists)
        if not matched_chunk_ids:
            for ev in evidence:
                meta = ev.chunk.metadata
                # Check list of skills, technologies, frameworks in metadata
                for field_name in ["skills", "technologies", "programming_languages", "frameworks", "models"]:
                    field_vals = meta.get(field_name, [])
                    if isinstance(field_vals, list):
                        if any(req_lower == str(v).lower() or req_lower in str(v).lower() for v in field_vals):
                            matched_chunk_ids.append(ev.chunk.id)
                            break

        # 3. High cosine vector similarity threshold for conceptual responsibilities
        if not matched_chunk_ids and evidence and category == "responsibility":
            top_hit = evidence[0]
            # If high vector similarity (e.g. cosine score > 0.75 or strong RRF)
            if (top_hit.vector_score is not None and top_hit.vector_score >= 0.78) or top_hit.rrf_score >= 0.025:
                matched_chunk_ids.append(top_hit.chunk.id)

        if matched_chunk_ids:
            return (
                True,
                f"Supported by {len(matched_chunk_ids)} verified knowledge record(s).",
                matched_chunk_ids
            )
        else:
            return (
                False,
                "Not represented in the current knowledge base.",
                []
            )

# Global analyzer
job_analyzer = JobAnalyzer()
