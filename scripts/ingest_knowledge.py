"""
CLI Script to ingest a new knowledge markdown file or batch of files.
Usage:
    python scripts/ingest_knowledge.py path/to/record.md [--reindex]
"""

import sys
import argparse
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from career_ai.knowledge.parser import MarkdownParser
from career_ai.knowledge.indexer import indexer
from career_ai.core.config import settings

def main():
    parser = argparse.ArgumentParser(description="Ingest a new Markdown record into the Canonical Knowledge Base.")
    parser.add_argument("file_path", help="Path to markdown file to ingest")
    parser.add_argument("--category", "-c", choices=["education", "certifications", "skills", "experience", "projects", "publications"],
                        help="Target category if not auto-detected from frontmatter")
    parser.add_argument("--reindex", "-r", action="store_true", default=True,
                        help="Immediately rebuild hybrid search index after ingestion (default: True)")
    args = parser.parse_args()

    src_file = Path(args.file_path)
    if not src_file.exists():
        print(f"Error: Source file '{src_file}' does not exist.")
        sys.exit(1)

    # Validate file parsing
    metadata, body = MarkdownParser.parse_file(src_file)
    if not metadata and not body:
        print(f"Error: Could not parse '{src_file}'. Ensure valid YAML frontmatter.")
        sys.exit(1)

    cat = args.category or metadata.get("type", "projects")
    dest_dir = settings.knowledge_dir / cat
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / src_file.name

    shutil.copy2(src_file, dest_file)
    print(f"Successfully copied record to '{dest_file}'.")

    if args.reindex:
        print("Rebuilding hybrid search index (BM25 + Qdrant vectors)...")
        res = indexer.index_all(recreate_vector_collection=False)
        print(f"Indexed {res.get('chunks_indexed', 0)} chunks across {res.get('files_indexed', 0)} files.")

if __name__ == "__main__":
    main()
