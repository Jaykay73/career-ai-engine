"""
LaTeX Renderer using Jinja2.
Renders TailoredCV and CoverLetter into ATS-optimized LaTeX documents.
Applies escaping to protect against LaTeX syntax errors.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import jinja2
from career_ai.tailoring.schemas import TailoredCV, CoverLetter
from career_ai.latex.sanitizer import escape_latex, sanitize_filename
from career_ai.core.config import settings
from career_ai.core.logging import get_logger

logger = get_logger("renderer")

class LaTeXRenderer:
    """Renders structured models into valid LaTeX source using Jinja2 templates."""

    def __init__(self, templates_dir: Optional[Path] = None):
        self.templates_dir = templates_dir or settings.templates_dir
        self.env = jinja2.Environment(
            block_start_string='((*',
            block_end_string='*))',
            variable_start_string='(((',
            variable_end_string=')))',
            comment_start_string='((#',
            comment_end_string='#))',
            loader=jinja2.FileSystemLoader(str(self.templates_dir)),
            autoescape=False
        )

    def render_cv(self, cv: TailoredCV) -> str:
        """Renders TailoredCV to .tex string with proper LaTeX character escaping."""
        template = self.env.get_template("master_resume.tex")

        # Create an escaped copy of data
        data = cv.model_dump()

        # Sanitize scalar string fields
        data["headline"] = escape_latex(data.get("headline", ""))
        if data.get("summary"):
            data["summary"] = escape_latex(data["summary"])

        # Education
        if "education" in data:
            data["education"]["degree"] = escape_latex(data["education"].get("degree", ""))
            data["education"]["institution"] = escape_latex(data["education"].get("institution", ""))
            data["education"]["coursework"] = escape_latex(data["education"].get("coursework", ""))

        # Certifications
        if "certifications" in data:
            for cert in data["certifications"]:
                cert["name"] = escape_latex(cert.get("name", ""))
                cert["issuer"] = escape_latex(cert.get("issuer", ""))

        # Skills
        if "skills" in data:
            for cat in data["skills"]:
                cat["category_name"] = escape_latex(cat.get("category_name", ""))
                cat["skills"] = [escape_latex(s) for s in cat.get("skills", [])]
                cat["skills_str"] = ", ".join(cat["skills"])

        # Experiences
        if "experiences" in data:
            for exp in data["experiences"]:
                exp["company"] = escape_latex(exp.get("company", ""))
                exp["role"] = escape_latex(exp.get("role", ""))
                exp["location"] = escape_latex(exp.get("location", ""))
                for b in exp.get("bullets", []):
                    b["text"] = escape_latex(b.get("text", ""))

        # Projects
        if "projects" in data:
            for proj in data["projects"]:
                proj["name"] = escape_latex(proj.get("name", ""))
                proj["technologies"] = escape_latex(proj.get("technologies", ""))
                for b in proj.get("bullets", []):
                    b["text"] = escape_latex(b.get("text", ""))

        # Publications
        if "publications" in data:
            for pub in data["publications"]:
                pub["title"] = escape_latex(pub.get("title", ""))
                pub["summary"] = escape_latex(pub.get("summary", ""))

        rendered = template.render(**data)
        logger.info("Successfully rendered LaTeX CV (%d characters)", len(rendered))
        return rendered

    def render_cover_letter(self, letter: CoverLetter) -> str:
        """Renders CoverLetter to .tex string."""
        template = self.env.get_template("cover_letter_template.tex")
        data = letter.model_dump()

        data["company_name"] = escape_latex(data.get("company_name", ""))
        data["position"] = escape_latex(data.get("position", ""))
        data["recipient_title"] = escape_latex(data.get("recipient_title", ""))
        data["opening"] = escape_latex(data.get("opening", ""))
        data["closing"] = escape_latex(data.get("closing", ""))
        data["body_paragraphs"] = [escape_latex(p) for p in data.get("body_paragraphs", [])]

        rendered = template.render(**data)
        logger.info("Successfully rendered LaTeX Cover Letter (%d characters)", len(rendered))
        return rendered

# Global renderer
latex_renderer = LaTeXRenderer()
