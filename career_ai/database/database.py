"""
SQLite Database connection and initialization manager.
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Generator, Optional
from career_ai.core.config import settings
from career_ai.core.logging import get_logger

logger = get_logger("database")

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS knowledge_records (
    id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    source_id TEXT NOT NULL,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    section TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    metadata_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_records_source_type ON knowledge_records(source_type);
CREATE INDEX IF NOT EXISTS idx_records_source_id ON knowledge_records(source_id);

CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    company_name TEXT NOT NULL,
    job_title TEXT NOT NULL,
    company_url TEXT,
    job_url TEXT,
    raw_description TEXT NOT NULL,
    parsed_requirements_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS generated_applications (
    id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    company_name TEXT NOT NULL,
    job_title TEXT NOT NULL,
    tex_path TEXT NOT NULL,
    pdf_path TEXT,
    cover_letter_text TEXT,
    metadata_json TEXT DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY(job_id) REFERENCES jobs(id)
);

CREATE TABLE IF NOT EXISTS index_metadata (
    id TEXT PRIMARY KEY,
    embedding_model TEXT NOT NULL,
    embedding_dim INTEGER NOT NULL,
    chunk_count INTEGER NOT NULL,
    record_count INTEGER NOT NULL,
    index_version TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

class Database:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.sqlite_db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_schema()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    @contextmanager
    def session(self) -> Generator[sqlite3.Connection, None, None]:
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_schema(self) -> None:
        """Runs table creation statements."""
        with self.session() as conn:
            conn.executescript(CREATE_TABLES_SQL)
        logger.debug("Database initialized at %s", self.db_path)

# Default global db instance
db = Database()
