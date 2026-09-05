"""
Knowledge Base Indexing Pipeline.
Idempotently processes canonical markdown documents, produces semantic chunks,
populates SQLite metadata, constructs BM25 index, computes dense embeddings,
and updates Qdrant collection.
"""

from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import hashlib
import json
from datetime import datetime

from career_ai.knowledge.schemas import EvidenceChunk
from career_ai.knowledge.parser import MarkdownParser
from career_ai.knowledge.chunker import SemanticChunker
from career_ai.retrieval.bm25 import BM25Retriever
from career_ai.retrieval.vector import EmbeddingEngine, QdrantVectorStore, embedding_engine, vector_store
from career_ai.retrieval.hybrid import hybrid_retriever
from career_ai.database.models import KnowledgeRecordDB, IndexMetadataDB
from career_ai.database.repository import repository, Repository
from career_ai.core.config import settings
from career_ai.core.logging import get_logger

logger = get_logger("indexer")

class KnowledgeIndexer:
    """Manages full index synchronization from canonical Markdown to SQLite, BM25, and Qdrant."""

    def __init__(
        self,
        repo: Optional[Repository] = None,
        embedder: Optional[EmbeddingEngine] = None,
        vstore: Optional[QdrantVectorStore] = None,
        bm25: Optional[BM25Retriever] = None
    ):
        self.repo = repo or repository
        self.embedder = embedder or embedding_engine
        self.vstore = vstore or vector_store
        self.bm25 = bm25 or hybrid_retriever.bm25

    def scan_and_chunk(self, base_dir: Optional[Path] = None) -> Tuple[List[EvidenceChunk], List[KnowledgeRecordDB]]:
        """
        Recursively scans directory for markdown files and parses them into EvidenceChunks.
        """
        search_dir = base_dir or settings.knowledge_dir
        if not search_dir.exists():
            logger.warning("Knowledge directory %s does not exist.", search_dir)
            return [], []

        md_files = sorted(list(search_dir.glob("**/*.md")))
        logger.info("Found %d markdown files in %s", len(md_files), search_dir)

        all_chunks: List[EvidenceChunk] = []
        all_db_records: List[KnowledgeRecordDB] = []

        for fpath in md_files:
            try:
                metadata, body = MarkdownParser.parse_file(fpath)
                parent_dir = fpath.parent.name.lower()
                stem = fpath.stem
                
                # Determine source type
                if parent_dir in ["projects", "project"]:
                    source_type = "project"
                    chunks = SemanticChunker.chunk_project(metadata, body, fpath)
                elif parent_dir in ["experience", "experiences"]:
                    source_type = "experience"
                    chunks = SemanticChunker.chunk_experience(metadata, body, fpath)
                elif parent_dir in ["certifications", "certification"]:
                    source_type = "certification"
                    chunks = SemanticChunker.chunk_certification(metadata, body, fpath)
                elif parent_dir in ["education"]:
                    source_type = "education"
                    chunks = SemanticChunker.chunk_education(metadata, body, fpath)
                elif parent_dir in ["publications", "publication"]:
                    source_type = "publication"
                    chunks = SemanticChunker.chunk_publication(metadata, body, fpath)
                elif parent_dir in ["skills", "skill"]:
                    source_type = "skill"
                    chunks = SemanticChunker.chunk_skills(metadata, body, fpath)
                else:
                    source_type = "general"
                    chunks = [EvidenceChunk(
                        id=f"general:{stem}:body",
                        source_type="general",
                        source_id=stem,
                        title=metadata.get("title", stem),
                        section="general",
                        file_path=str(fpath),
                        text=body,
                        metadata=metadata
                    )]

                all_chunks.extend(chunks)

                # Create primary DB record for file
                full_content = fpath.read_text(encoding="utf-8")
                content_hash = hashlib.sha256(full_content.encode("utf-8")).hexdigest()
                rec = KnowledgeRecordDB(
                    id=f"{source_type}:{stem}",
                    source_type=source_type,
                    source_id=stem,
                    title=metadata.get("title") or metadata.get("project_name") or metadata.get("organization") or metadata.get("certification_name") or stem,
                    file_path=str(fpath),
                    section="root",
                    content_hash=content_hash,
                    metadata_json=json.dumps(metadata)
                )
                all_db_records.append(rec)

            except Exception as e:
                logger.error("Error processing knowledge file %s: %s", fpath, e)

        return all_chunks, all_db_records

    def index_all(self, base_dir: Optional[Path] = None, recreate_vector_collection: bool = True) -> Dict[str, Any]:
        """
        Executes full indexing workflow:
        1. Scan & chunk Markdown
        2. Upsert SQLite records
        3. Build & persist BM25 index
        4. Generate embeddings
        5. Upsert to Qdrant
        6. Record index metadata
        """
        start_time = datetime.utcnow()
        logger.info("Starting knowledge indexing...")

        chunks, db_records = self.scan_and_chunk(base_dir)
        if not chunks:
            logger.warning("No chunks generated. Indexing aborted.")
            return {"status": "empty", "chunks": 0, "records": 0}

        # 1. Update SQLite records
        for rec in db_records:
            self.repo.upsert_knowledge_record(rec)

        # 2. Build and persist BM25
        self.bm25.build_index(chunks)

        # 3. Vector Embeddings and Qdrant
        texts = [f"{c.title}\n{c.text}" for c in chunks]
        embeddings = self.embedder.embed_texts(texts)

        # Ensure collection and upsert
        self.vstore.ensure_collection(vector_dim=self.embedder.dimension, recreate=recreate_vector_collection)
        self.vstore.upsert_chunks(chunks=chunks, embeddings=embeddings)

        # 4. Save metadata
        meta = IndexMetadataDB(
            embedding_model=self.embedder.model_name,
            embedding_dim=self.embedder.dimension,
            chunk_count=len(chunks),
            record_count=len(db_records),
            index_version="1.0",
            updated_at=datetime.utcnow().isoformat()
        )
        self.repo.update_index_metadata(meta)

        duration = (datetime.utcnow() - start_time).total_seconds()
        summary = {
            "status": "success",
            "files_indexed": len(db_records),
            "chunks_indexed": len(chunks),
            "embedding_model": self.embedder.model_name,
            "embedding_dim": self.embedder.dimension,
            "duration_seconds": round(duration, 2),
            "timestamp": meta.updated_at
        }
        logger.info("Indexing completed successfully: %s", summary)
        return summary

# Global indexer
indexer = KnowledgeIndexer()
