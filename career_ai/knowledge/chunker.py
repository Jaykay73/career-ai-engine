"""
Semantic, section-aware chunker for knowledge base entities.
Avoids naive arbitrary token slicing; preserves document context, parent IDs,
and section provenance.
"""

from typing import List, Dict, Any
from pathlib import Path
from career_ai.knowledge.schemas import EvidenceChunk
from career_ai.knowledge.parser import MarkdownParser
from career_ai.core.logging import get_logger

logger = get_logger("chunker")

class SemanticChunker:
    """Creates structured, verifiable EvidenceChunks from parsed knowledge entities."""

    @classmethod
    def chunk_project(cls, metadata: Dict[str, Any], body: str, file_path: Path) -> List[EvidenceChunk]:
        chunks: List[EvidenceChunk] = []
        source_id = file_path.stem
        title = metadata.get("project_name") or title_from_filename(source_id)

        # 1. Project Overview & Solution Chunk
        desc = metadata.get("short_description") or ""
        sol = metadata.get("solution") or ""
        prob = metadata.get("problem") or ""
        overview_text = f"Project: {title}\nDescription: {desc}"
        if prob:
            overview_text += f"\nProblem Addressed: {prob}"
        if sol:
            overview_text += f"\nSolution: {sol}"
        chunks.append(EvidenceChunk(
            id=f"project:{source_id}:overview",
            source_type="project",
            source_id=source_id,
            title=title,
            section="overview",
            file_path=str(file_path),
            text=overview_text.strip(),
            metadata=metadata
        ))

        # 2. Architecture & Technical Decisions
        arch = metadata.get("architecture") or ""
        tech_dec = metadata.get("technical_decisions") or ""
        if arch or tech_dec:
            arch_text = f"Project: {title} — Architecture & Technical Decisions\n"
            if arch:
                arch_text += f"Architecture: {arch}\n"
            if tech_dec:
                arch_text += f"Technical Decisions: {tech_dec}\n"
            chunks.append(EvidenceChunk(
                id=f"project:{source_id}:architecture",
                source_type="project",
                source_id=source_id,
                title=title,
                section="architecture",
                file_path=str(file_path),
                text=arch_text.strip(),
                metadata=metadata
            ))

        # 3. Technologies, Frameworks & Infrastructure
        techs = metadata.get("technologies") or []
        langs = metadata.get("programming_languages") or []
        fws = metadata.get("frameworks") or []
        models = metadata.get("models") or []
        dbs = metadata.get("databases") or []
        infra = metadata.get("infrastructure") or []
        deploy = metadata.get("deployment_platform") or metadata.get("deployment_information") or ""

        tech_components = []
        if langs:
            tech_components.append(f"Languages: {', '.join(langs)}")
        if fws or models:
            all_fws = list(set(fws + models))
            tech_components.append(f"Frameworks & Models: {', '.join(all_fws)}")
        if techs:
            tech_components.append(f"Technologies: {', '.join(techs)}")
        if dbs:
            tech_components.append(f"Databases: {', '.join(dbs)}")
        if infra:
            tech_components.append(f"Infrastructure: {', '.join(infra)}")
        if deploy:
            tech_components.append(f"Deployment: {deploy}")

        if tech_components:
            tech_text = f"Project: {title} — Tech Stack & Infrastructure\n" + "\n".join(tech_components)
            chunks.append(EvidenceChunk(
                id=f"project:{source_id}:technologies",
                source_type="project",
                source_id=source_id,
                title=title,
                section="technologies",
                file_path=str(file_path),
                text=tech_text.strip(),
                metadata=metadata
            ))

        # 4. Responsibilities, Exact Contributions & Results
        contrib = metadata.get("exact_contribution") or ""
        resps = metadata.get("responsibilities") or []
        results = metadata.get("results") or []
        metrics = metadata.get("metrics") or []

        impact_parts = []
        if contrib:
            impact_parts.append(f"Exact Contribution: {contrib}")
        if resps:
            impact_parts.append("Responsibilities:\n" + "\n".join(f"- {r}" for r in resps))
        if results:
            impact_parts.append("Results:\n" + "\n".join(f"- {r}" for r in results))
        if metrics:
            impact_parts.append("Metrics:\n" + "\n".join(f"- {m}" for m in metrics))

        if impact_parts:
            impact_text = f"Project: {title} — Contributions & Measurable Results\n" + "\n".join(impact_parts)
            chunks.append(EvidenceChunk(
                id=f"project:{source_id}:contributions",
                source_type="project",
                source_id=source_id,
                title=title,
                section="contributions",
                file_path=str(file_path),
                text=impact_text.strip(),
                metadata=metadata
            ))

        # Also incorporate any extra body markdown sections if present
        body_sections = MarkdownParser.extract_sections(body)
        for sec_name, sec_text in body_sections.items():
            if sec_name not in ["overview", "architecture", "technologies", "contributions"] and len(sec_text) > 30:
                chunks.append(EvidenceChunk(
                    id=f"project:{source_id}:{sec_name}",
                    source_type="project",
                    source_id=source_id,
                    title=title,
                    section=sec_name,
                    file_path=str(file_path),
                    text=f"Project: {title} — {sec_name.replace('_', ' ').title()}\n{sec_text}",
                    metadata=metadata
                ))

        return chunks

    @classmethod
    def chunk_experience(cls, metadata: Dict[str, Any], body: str, file_path: Path) -> List[EvidenceChunk]:
        chunks: List[EvidenceChunk] = []
        source_id = file_path.stem
        org = metadata.get("organization") or title_from_filename(source_id)
        role = metadata.get("job_title") or "Professional Experience"
        title = f"{role} at {org}"

        # 1. Experience Overview & Responsibilities Chunk
        resps = metadata.get("responsibilities") or []
        achievements = metadata.get("achievements") or []
        exact_contrib = metadata.get("exact_contributions") or ""
        metrics = metadata.get("measurable_results") or []

        resp_parts = [f"Experience: {role} at {org} ({metadata.get('start_date', '')} – {metadata.get('end_date', 'Present')})"]
        if exact_contrib:
            resp_parts.append(f"Contributions: {exact_contrib}")
        if resps:
            resp_parts.append("Responsibilities:\n" + "\n".join(f"- {r}" for r in resps))
        if achievements:
            resp_parts.append("Achievements:\n" + "\n".join(f"- {a}" for a in achievements))
        if metrics:
            resp_parts.append("Measurable Results:\n" + "\n".join(f"- {m}" for m in metrics))

        chunks.append(EvidenceChunk(
            id=f"experience:{source_id}:responsibilities",
            source_type="experience",
            source_id=source_id,
            title=title,
            section="responsibilities",
            file_path=str(file_path),
            text="\n".join(resp_parts).strip(),
            metadata=metadata
        ))

        # 2. Technologies & Tools used
        techs = metadata.get("technologies") or []
        langs = metadata.get("programming_languages") or []
        fws = metadata.get("frameworks") or []
        infra = metadata.get("infrastructure") or []
        domains = metadata.get("domains") or []

        tech_parts = [f"Experience: {role} at {org} — Technologies & Domains"]
        if langs:
            tech_parts.append(f"Languages: {', '.join(langs)}")
        if fws:
            tech_parts.append(f"Frameworks & ML: {', '.join(fws)}")
        if techs:
            tech_parts.append(f"Technologies: {', '.join(techs)}")
        if infra:
            tech_parts.append(f"Infrastructure & DevOps: {', '.join(infra)}")
        if domains:
            tech_parts.append(f"Domains: {', '.join(domains)}")

        if len(tech_parts) > 1:
            chunks.append(EvidenceChunk(
                id=f"experience:{source_id}:technologies",
                source_type="experience",
                source_id=source_id,
                title=title,
                section="technologies",
                file_path=str(file_path),
                text="\n".join(tech_parts).strip(),
                metadata=metadata
            ))

        # Extra body sections if present
        body_sections = MarkdownParser.extract_sections(body)
        for sec_name, sec_text in body_sections.items():
            if sec_name not in ["overview", "responsibilities", "technologies"] and len(sec_text) > 30:
                chunks.append(EvidenceChunk(
                    id=f"experience:{source_id}:{sec_name}",
                    source_type="experience",
                    source_id=source_id,
                    title=title,
                    section=sec_name,
                    file_path=str(file_path),
                    text=f"Experience: {role} at {org} — {sec_name.replace('_', ' ').title()}\n{sec_text}",
                    metadata=metadata
                ))

        return chunks

    @classmethod
    def chunk_certification(cls, metadata: Dict[str, Any], body: str, file_path: Path) -> List[EvidenceChunk]:
        source_id = file_path.stem
        name = metadata.get("certification_name") or title_from_filename(source_id)
        org = metadata.get("issuing_organization") or ""
        topics = metadata.get("relevant_topics") or []
        desc = metadata.get("description") or body or ""

        text_parts = [f"Certification: {name}"]
        if org:
            text_parts.append(f"Issuer: {org}")
        if metadata.get("issue_date"):
            text_parts.append(f"Date: {metadata.get('issue_date')}")
        if topics:
            text_parts.append(f"Topics & Skills: {', '.join(topics)}")
        if desc:
            text_parts.append(f"Details: {desc}")

        return [EvidenceChunk(
            id=f"certification:{source_id}:details",
            source_type="certification",
            source_id=source_id,
            title=name,
            section="certification",
            file_path=str(file_path),
            text="\n".join(text_parts).strip(),
            metadata=metadata
        )]

    @classmethod
    def chunk_education(cls, metadata: Dict[str, Any], body: str, file_path: Path) -> List[EvidenceChunk]:
        source_id = file_path.stem
        inst = metadata.get("institution", "University of Ilorin")
        deg = metadata.get("degree", "Bachelor of Engineering (B.Eng.) in Computer Engineering")
        cw = metadata.get("relevant_coursework", [])

        # Strictly never output classification
        text_parts = [
            f"Education: {deg} — {inst}",
            f"Period: {metadata.get('start_date', '2021')} – {metadata.get('end_date', '2026')}"
        ]
        if cw:
            text_parts.append(f"Relevant Coursework: {', '.join(cw)}")
        if body:
            text_parts.append(body)

        return [EvidenceChunk(
            id=f"education:{source_id}:degree",
            source_type="education",
            source_id=source_id,
            title=f"{deg} — {inst}",
            section="education",
            file_path=str(file_path),
            text="\n".join(text_parts).strip(),
            metadata=metadata
        )]

    @classmethod
    def chunk_publication(cls, metadata: Dict[str, Any], body: str, file_path: Path) -> List[EvidenceChunk]:
        source_id = file_path.stem
        title = metadata.get("title") or title_from_filename(source_id)
        platform = metadata.get("platform", "Medium")
        abstract = metadata.get("abstract") or body or ""
        topics = metadata.get("topics") or []

        text_parts = [
            f"Publication: \"{title}\"",
            f"Platform: {platform}",
            f"URL: {metadata.get('url', '')}"
        ]
        if topics:
            text_parts.append(f"Topics & Key Concepts: {', '.join(topics)}")
        if abstract:
            text_parts.append(f"Abstract / Summary: {abstract}")

        return [EvidenceChunk(
            id=f"publication:{source_id}:article",
            source_type="publication",
            source_id=source_id,
            title=title,
            section="publication",
            file_path=str(file_path),
            text="\n".join(text_parts).strip(),
            metadata=metadata
        )]

    @classmethod
    def chunk_skills(cls, metadata: Dict[str, Any], body: str, file_path: Path) -> List[EvidenceChunk]:
        chunks: List[EvidenceChunk] = []
        source_id = file_path.stem

        # Check if skills are defined in categories in metadata or markdown sections
        categories = metadata.get("categories", {})
        if categories and isinstance(categories, dict):
            for cat_name, skill_list in categories.items():
                if isinstance(skill_list, list):
                    clean_cat = cat_name.lower().replace(" ", "_")
                    text = f"Technical Skills — {cat_name}: {', '.join(skill_list)}"
                    chunks.append(EvidenceChunk(
                        id=f"skill:{source_id}:{clean_cat}",
                        source_type="skill",
                        source_id=source_id,
                        title=f"Skills: {cat_name}",
                        section=clean_cat,
                        file_path=str(file_path),
                        text=text,
                        metadata={"category": cat_name, "skills": skill_list}
                    ))

        # Also parse body sections
        sections = MarkdownParser.extract_sections(body)
        for sec_name, sec_text in sections.items():
            if sec_text and len(sec_text) > 10:
                chunks.append(EvidenceChunk(
                    id=f"skill:{source_id}:{sec_name}",
                    source_type="skill",
                    source_id=source_id,
                    title=f"Technical Skills: {sec_name.replace('_', ' ').title()}",
                    section=sec_name,
                    file_path=str(file_path),
                    text=f"Skills Category — {sec_name.replace('_', ' ').title()}:\n{sec_text}",
                    metadata=metadata
                ))

        return chunks

def title_from_filename(stem: str) -> str:
    return stem.replace("-", " ").replace("_", " ").title()
