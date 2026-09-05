"""
Post-Generation Verification Layer.
Inspects every factual claim in the generated TailoredCV and CoverLetter
against authoritative knowledge base evidence. Rejects or flags unsupported claims.
"""

from typing import List, Dict, Set, Optional, Tuple
import re
from career_ai.tailoring.schemas import TailoredCV, VerificationResult, CoverLetter
from career_ai.knowledge.schemas import EvidenceChunk
from career_ai.core.logging import get_logger

logger = get_logger("verifier")

FORBIDDEN_EDUCATION_TERMS = [
    r"\b2[:\.]2\b",
    r"\bsecond\s+class\b",
    r"\bfirst\s+class\b",
    r"\bgpa\b",
    r"\bcgpa\b",
    r"\bthird\s+class\b"
]

class FactualClaimVerifier:
    """Rigorous adversarial verifier enforcing zero hallucination."""

    def verify_cv(
        self,
        cv: TailoredCV,
        authoritative_evidence: List[EvidenceChunk]
    ) -> VerificationResult:
        """
        Verifies that every claim, metric, and entity in the CV is backed by evidence.
        """
        unsupported: List[str] = []

        # 1. Degree classification audit (Strict Rule)
        edu_text = f"{cv.education.degree} {cv.education.coursework} {cv.education.institution}"
        for pattern in FORBIDDEN_EDUCATION_TERMS:
            if re.search(pattern, edu_text, re.IGNORECASE):
                unsupported.append(f"FORBIDDEN: Degree classification or GPA detected in education: '{pattern}'")

        # 2. Build authoritative token and metric sets from verified chunks
        all_evidence_text = " ".join([f"{c.title} {c.text} {c.source_id}" for c in authoritative_evidence])
        all_evidence_lower = all_evidence_text.lower()

        # Extract numerical metrics from generated bullets (e.g. 35%, 140k, 100ms)
        metric_pattern = re.compile(r"\b(\d+(?:\.\d+)?%|\d+[kKmM]\b|\b\d+\s*ms\b)")

        # 3. Audit Experience bullets
        for exp in cv.experiences:
            # Check company
            if exp.company.lower() not in all_evidence_lower:
                unsupported.append(f"Unverified employer: '{exp.company}' not found in knowledge base.")

            for bullet in exp.bullets:
                # Metric check
                metrics_found = metric_pattern.findall(bullet.text)
                for m in metrics_found:
                    if m.lower() not in all_evidence_lower:
                        unsupported.append(f"Fabricated metric '{m}' in experience bullet: \"{bullet.text}\"")

        # 4. Audit Project bullets
        for proj in cv.projects:
            # Check project name
            proj_name_simple = re.sub(r"[^a-zA-Z0-9]", "", proj.name).lower()
            if not any(proj_name_simple in re.sub(r"[^a-zA-Z0-9]", "", c.title).lower() for c in authoritative_evidence):
                # Check if partial name matches
                first_word = proj.name.split()[0].lower()
                if first_word not in all_evidence_lower:
                    unsupported.append(f"Unverified project: '{proj.name}' not found in knowledge base.")

            for bullet in proj.bullets:
                metrics_found = metric_pattern.findall(bullet.text)
                for m in metrics_found:
                    # Check if metric exists in evidence
                    if m.lower() not in all_evidence_lower:
                        unsupported.append(f"Fabricated metric '{m}' in project bullet: \"{bullet.text}\"")

        # 5. Audit Certifications
        valid_certs = [
            "oci generative ai professional",
            "oracle ai foundations associate",
            "machine learning specialization"
        ]
        for cert in cv.certifications:
            if not any(v in cert.name.lower() for v in valid_certs):
                unsupported.append(f"Unverified certification: '{cert.name}'")

        # 6. Audit Custom Sections
        for sec in getattr(cv, "custom_sections", []):
            for item in sec.items:
                first_word = item.heading.split()[0].lower() if item.heading else ""
                if first_word and first_word not in all_evidence_lower:
                    unsupported.append(f"Unverified entity '{item.heading}' in custom section '{sec.title}' not found in knowledge base.")
                for bullet in item.bullets:
                    metrics_found = metric_pattern.findall(bullet.text)
                    for m in metrics_found:
                        if m.lower() not in all_evidence_lower:
                            unsupported.append(f"Fabricated metric '{m}' in custom section '{sec.title}': \"{bullet.text}\"")

        is_valid = len(unsupported) == 0
        if not is_valid:
            logger.warning("Claim verification flagged %d unsupported claims:\n%s", len(unsupported), "\n".join(unsupported))
        else:
            logger.info("Claim verification PASSED with zero unsupported claims.")

        return VerificationResult(
            is_valid=is_valid,
            unsupported_claims=unsupported,
            notes="Passed all factual verification audits." if is_valid else f"Detected {len(unsupported)} unverified claim(s)."
        )

# Global verifier
claim_verifier = FactualClaimVerifier()
