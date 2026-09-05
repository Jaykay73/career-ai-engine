"""
CLI Script to rebuild the BM25 lexical index and Qdrant dense vector index.
Usage:
    python scripts/rebuild_index.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from career_ai.knowledge.indexer import indexer

def main():
    print("==================================================")
    print("      REBUILDING CAREER AI HYBRID INDEX          ")
    print("==================================================")
    result = indexer.index_all(recreate_vector_collection=True)
    print(f"Status: {result.get('status')}")
    print(f"Files Indexed: {result.get('files_indexed')}")
    print(f"Chunks Indexed: {result.get('chunks_indexed')}")
    print(f"Duration: {result.get('duration_seconds', 0):.2f}s")
    print("Index rebuild complete.")

if __name__ == "__main__":
    main()
