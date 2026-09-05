"""
Markdown and YAML frontmatter parser for canonical knowledge base files.
"""

from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import yaml
import re
from career_ai.core.exceptions import ParsingError
from career_ai.core.logging import get_logger

logger = get_logger("parser")

FRONTMATTER_REGEX = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)

class MarkdownParser:
    """Parses markdown files with optional YAML frontmatter into structured data."""

    @staticmethod
    def parse_file(file_path: Path) -> Tuple[Dict[str, Any], str]:
        """
        Reads a markdown file and separates YAML frontmatter from markdown body.
        Returns (metadata_dict, body_text).
        """
        if not file_path.exists():
            raise ParsingError(f"File not found: {file_path}")

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            raise ParsingError(f"Failed to read file {file_path}: {e}")

        return MarkdownParser.parse_content(content, source_name=str(file_path))

    @staticmethod
    def parse_content(content: str, source_name: str = "raw") -> Tuple[Dict[str, Any], str]:
        """Parses content string into (frontmatter_dict, body_text)."""
        match = FRONTMATTER_REGEX.match(content.strip())
        if match:
            frontmatter_raw, body = match.groups()
            try:
                metadata = yaml.safe_load(frontmatter_raw) or {}
                if not isinstance(metadata, dict):
                    metadata = {}
            except yaml.YAMLError as e:
                logger.warning("YAML parsing failed for %s: %s. Proceeding with empty frontmatter.", source_name, e)
                metadata = {}
            return metadata, body.strip()
        else:
            # If no frontmatter block exists, return empty dict and full text
            return {}, content.strip()

    @staticmethod
    def extract_sections(body: str) -> Dict[str, str]:
        """
        Splits markdown text into named sections based on markdown headers (#, ##, ###).
        Returns a dict of {section_name: section_content}.
        """
        sections: Dict[str, str] = {}
        lines = body.split("\n")
        current_section = "overview"
        current_lines = []

        header_pattern = re.compile(r"^(#{1,4})\s+(.+)$")

        for line in lines:
            header_match = header_pattern.match(line.strip())
            if header_match:
                # Save previous section if it has content
                if current_lines:
                    sections[current_section] = "\n".join(current_lines).strip()
                    current_lines = []
                # Clean up section name
                raw_title = header_match.group(2).strip()
                # e.g. "## 1. Executive Summary" -> "executive_summary"
                clean_name = re.sub(r"^[0-9]+[\.\)]\s*", "", raw_title)
                clean_name = re.sub(r"[^\w\s-]", "", clean_name).strip().lower().replace(" ", "_")
                current_section = clean_name or "section"
            else:
                current_lines.append(line)

        if current_lines:
            sections[current_section] = "\n".join(current_lines).strip()

        return sections
