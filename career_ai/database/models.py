"""
Database models and dataclasses for SQLite persistence.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import json

@dataclass
class KnowledgeRecordDB:
    id: str
    source_type: str  # project, experience, certification, publication, skill, education
    source_id: str
    title: str
    file_path: str
    section: str
    content_hash: str
    metadata_json: str = "{}"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def metadata(self) -> Dict[str, Any]:
        try:
            return json.loads(self.metadata_json)
        except Exception:
            return {}

@dataclass
class JobDB:
    id: str
    company_name: str
    job_title: str
    company_url: Optional[str] = None
    job_url: Optional[str] = None
    raw_description: str = ""
    parsed_requirements_json: str = "{}"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class GeneratedApplicationDB:
    id: str
    job_id: str
    company_name: str
    job_title: str
    tex_path: str
    pdf_path: Optional[str] = None
    cover_letter_text: Optional[str] = None
    metadata_json: str = "{}"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def metadata(self) -> Dict[str, Any]:
        try:
            return json.loads(self.metadata_json)
        except Exception:
            return {}

@dataclass
class IndexMetadataDB:
    id: str = "current"
    embedding_model: str = ""
    embedding_dim: int = 0
    chunk_count: int = 0
    record_count: int = 0
    index_version: str = "1.0"
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
