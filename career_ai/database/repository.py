"""
Repository for SQLite database operations.
"""

from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from career_ai.database.database import db, Database
from career_ai.database.models import (
    KnowledgeRecordDB,
    JobDB,
    GeneratedApplicationDB,
    IndexMetadataDB,
)
from career_ai.core.logging import get_logger

logger = get_logger("repository")

class Repository:
    def __init__(self, database: Optional[Database] = None):
        self.db = database or db

    # --- Knowledge Records ---
    def upsert_knowledge_record(self, record: KnowledgeRecordDB) -> None:
        sql = """
        INSERT INTO knowledge_records 
            (id, source_type, source_id, title, file_path, section, content_hash, metadata_json, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title=excluded.title,
            file_path=excluded.file_path,
            section=excluded.section,
            content_hash=excluded.content_hash,
            metadata_json=excluded.metadata_json,
            updated_at=excluded.updated_at
        """
        with self.db.session() as conn:
            conn.execute(sql, (
                record.id,
                record.source_type,
                record.source_id,
                record.title,
                record.file_path,
                record.section,
                record.content_hash,
                record.metadata_json,
                record.created_at,
                record.updated_at
            ))

    def get_all_records(self) -> List[KnowledgeRecordDB]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM knowledge_records ORDER BY source_type, title")
            rows = cursor.fetchall()
            return [KnowledgeRecordDB(**dict(row)) for row in rows]

    def get_records_by_type(self, source_type: str) -> List[KnowledgeRecordDB]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM knowledge_records WHERE source_type = ?", (source_type,))
            rows = cursor.fetchall()
            return [KnowledgeRecordDB(**dict(row)) for row in rows]

    def count_records_by_type(self) -> Dict[str, int]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT source_type, COUNT(*) as count FROM knowledge_records GROUP BY source_type")
            rows = cursor.fetchall()
            return {row["source_type"]: row["count"] for row in rows}

    def clear_records(self) -> None:
        with self.db.session() as conn:
            conn.execute("DELETE FROM knowledge_records")

    # --- Jobs ---
    def save_job(self, job: JobDB) -> None:
        sql = """
        INSERT INTO jobs (id, company_name, job_title, company_url, job_url, raw_description, parsed_requirements_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            company_name=excluded.company_name,
            job_title=excluded.job_title,
            company_url=excluded.company_url,
            job_url=excluded.job_url,
            raw_description=excluded.raw_description,
            parsed_requirements_json=excluded.parsed_requirements_json
        """
        with self.db.session() as conn:
            conn.execute(sql, (
                job.id,
                job.company_name,
                job.job_title,
                job.company_url,
                job.job_url,
                job.raw_description,
                job.parsed_requirements_json,
                job.created_at
            ))

    def get_job(self, job_id: str) -> Optional[JobDB]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            if row:
                return JobDB(**dict(row))
            return None

    # --- Generated Applications ---
    def save_application(self, app: GeneratedApplicationDB) -> None:
        sql = """
        INSERT INTO generated_applications 
            (id, job_id, company_name, job_title, tex_path, pdf_path, cover_letter_text, metadata_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            tex_path=excluded.tex_path,
            pdf_path=excluded.pdf_path,
            cover_letter_text=excluded.cover_letter_text,
            metadata_json=excluded.metadata_json
        """
        with self.db.session() as conn:
            conn.execute(sql, (
                app.id,
                app.job_id,
                app.company_name,
                app.job_title,
                app.tex_path,
                app.pdf_path,
                app.cover_letter_text,
                app.metadata_json,
                app.created_at
            ))

    def get_all_applications(self) -> List[GeneratedApplicationDB]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM generated_applications ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [GeneratedApplicationDB(**dict(row)) for row in rows]

    def get_application(self, app_id: str) -> Optional[GeneratedApplicationDB]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM generated_applications WHERE id = ?", (app_id,))
            row = cursor.fetchone()
            if row:
                return GeneratedApplicationDB(**dict(row))
            return None

    # --- Index Metadata ---
    def update_index_metadata(self, metadata: IndexMetadataDB) -> None:
        sql = """
        INSERT INTO index_metadata (id, embedding_model, embedding_dim, chunk_count, record_count, index_version, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            embedding_model=excluded.embedding_model,
            embedding_dim=excluded.embedding_dim,
            chunk_count=excluded.chunk_count,
            record_count=excluded.record_count,
            index_version=excluded.index_version,
            updated_at=excluded.updated_at
        """
        with self.db.session() as conn:
            conn.execute(sql, (
                metadata.id,
                metadata.embedding_model,
                metadata.embedding_dim,
                metadata.chunk_count,
                metadata.record_count,
                metadata.index_version,
                metadata.updated_at
            ))

    def get_index_metadata(self) -> Optional[IndexMetadataDB]:
        with self.db.session() as conn:
            cursor = conn.execute("SELECT * FROM index_metadata WHERE id = 'current'")
            row = cursor.fetchone()
            if row:
                return IndexMetadataDB(**dict(row))
            return None

# Global default repository
repository = Repository()
