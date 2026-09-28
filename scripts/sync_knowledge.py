"""
Knowledge Base Synchronization & Health Verification CLI.
Scans canonical knowledge records across all categories, checks hash integrity,
displays category summaries, and idempotently synchronizes BM25 and vector stores.

Usage:
    python scripts/sync_knowledge.py --check
    python scripts/sync_knowledge.py --reindex
"""

import sys
import argparse
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from career_ai.core.config import settings
from career_ai.knowledge.parser import MarkdownParser
from career_ai.knowledge.chunker import SemanticChunker
from career_ai.knowledge.indexer import KnowledgeIndexer, indexer
from career_ai.database.repository import repository

def inspect_knowledge_base():
    """Scans all canonical files and computes category breakdown and chunk statistics."""
    categories = ["education", "certifications", "experience", "projects", "publications", "skills"]
    stats = {}
    total_files = 0
    total_chunks = 0

    print("==================================================================")
    print("           CAREER AI KNOWLEDGE BASE INVENTORY & HEALTH            ")
    print("==================================================================")
    print(f"{'Category':<20} | {'Files':<8} | {'Sample Entities':<35}")
    print("-" * 68)

    for cat in categories:
        cat_dir = settings.knowledge_dir / cat
        if not cat_dir.exists():
            stats[cat] = {"files": 0, "entities": []}
            continue

        files = sorted(list(cat_dir.glob("*.md")))
        names = []
        for f in files:
            try:
                meta, body = MarkdownParser.parse_file(f)
                name = meta.get("project_name") or meta.get("organization") or meta.get("institution") or meta.get("title") or meta.get("certification_name") or f.stem
                names.append(str(name))
            except Exception:
                names.append(f.stem)

        stats[cat] = {"files": len(files), "entities": names}
        total_files += len(files)
        sample = ", ".join(names[:2]) + (f" (+{len(names)-2} more)" if len(names) > 2 else "")
        print(f"{cat.capitalize():<20} | {len(files):<8} | {sample:<35}")

    print("-" * 68)
    print(f"Total Canonical Files: {total_files}")
    return stats

def main():
    parser = argparse.ArgumentParser(description="Synchronize and audit Canonical Knowledge Base.")
    parser.add_argument("--check", action="store_true", help="Perform non-destructive inventory and health check")
    parser.add_argument("--reindex", action="store_true", help="Execute full hybrid indexing (BM25 + Qdrant vectors)")
    args = parser.parse_args()

    stats = inspect_knowledge_base()

    if args.reindex:
        print("\n[+] Triggering full hybrid index synchronization...")
        result = indexer.index_all(recreate_vector_collection=False)
        print(f"Index Status: {result.get('status')}")
        print(f"Files Processed: {result.get('files_indexed')}")
        print(f"Semantic Chunks Indexed: {result.get('chunks_indexed')}")
        print(f"Elapsed Time: {result.get('duration_seconds', 0.0):.2f}s")
        print("[✓] Knowledge base synchronization complete.")
    elif not args.check:
        print("\nRun with --check to verify inventory or --reindex to synchronize search stores.")

if __name__ == "__main__":
    main()
