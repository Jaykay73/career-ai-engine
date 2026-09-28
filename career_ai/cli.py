"""
Command-Line Interface (CLI) for Career AI Engine.
Supports hybrid retrieval queries, knowledge base inventory audits,
and edge robotics domain verification.

Usage:
    python -m career_ai.cli stats
    python -m career_ai.cli query "autonomous robotics edge AI"
    python -m career_ai.cli verify-robotics
"""

import sys
import argparse
from pathlib import Path
from career_ai.retrieval.hybrid import hybrid_retriever
from career_ai.services.application_service import ApplicationService
from career_ai.core.logging import get_logger

logger = get_logger("cli")

def cmd_stats(args):
    """Outputs current knowledge base statistics and inventory counts."""
    service = ApplicationService()
    summary = service.get_knowledge_summary()
    print("==================================================")
    print("         CAREER AI ENGINE - KNOWLEDGE STATS       ")
    print("==================================================")
    for k, v in summary.items():
        print(f"  {k:<22}: {v}")
    print("==================================================")

def cmd_query(args):
    """Runs a hybrid search query across canonical knowledge base."""
    query = " ".join(args.terms)
    print(f"\n[+] Searching hybrid index for: '{query}' (top_k={args.top_k})")
    results = hybrid_retriever.search(
        query=query,
        top_k_bm25=args.top_k * 2,
        top_k_vector=args.top_k * 2,
        top_k_rrf=args.top_k
    )
    if not results:
        print("[-] No evidence chunks matched the query.")
        return

    print(f"[✓] Retrieved {len(results)} ranked evidence chunks:\n")
    for r in results:
        print(f"• Rank #{r.rank} [RRF Score: {r.rrf_score:.4f}] | {r.chunk.title} ({r.chunk.section})")
        snippet = r.chunk.text.strip().replace("\n", " ")[:140]
        print(f"  Snippet: {snippet}...\n")

def cmd_verify_robotics(args):
    """Verifies that edge robotics and autonomous mower knowledge is present and searchable."""
    print("==================================================")
    print("     VERIFYING AUTONOMOUS ROBOTICS & EDGE AI      ")
    print("==================================================")
    test_queries = [
        "autonomous lawn mower watchdog heartbeat",
        "YOLOv26n INT8 TFLite edge Raspberry Pi",
        "ATmega microcontroller 500 ms safety fail-safe",
        "MPU6050 IMU ultrasonic sensor fusion"
    ]
    all_passed = True
    for q in test_queries:
        hits = hybrid_retriever.search(query=q, top_k_bm25=5, top_k_vector=5, top_k_rrf=3)
        top_titles = [h.chunk.title for h in hits]
        mower_matched = any("lawn mower" in t.lower() or "intelligent system" in t.lower() for t in top_titles)
        status = "PASSED" if mower_matched else "WARNING"
        if not mower_matched:
            all_passed = False
        print(f"[{status}] Query: '{q}' -> Top Match: {top_titles[0] if top_titles else 'None'}")

    print("--------------------------------------------------")
    if all_passed:
        print("[✓] All robotics and edge AI queries verified successfully!")
    else:
        print("[!] Note: Run 'python scripts/sync_knowledge.py --reindex' to update vector stores.")

def main():
    parser = argparse.ArgumentParser(description="Career AI Engine CLI Operational Tool")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # stats
    subparsers.add_parser("stats", help="Display knowledge base inventory and database statistics")

    # query
    query_parser = subparsers.add_parser("query", help="Execute hybrid BM25 + dense vector search")
    query_parser.add_argument("terms", nargs="+", help="Search query terms")
    query_parser.add_argument("--top-k", "-k", type=int, default=5, help="Number of results (default: 5)")

    # verify-robotics
    subparsers.add_parser("verify-robotics", help="Verify retrieval rankings for robotics and cyber-physical domains")

    args = parser.parse_args()

    if args.command == "stats":
        cmd_stats(args)
    elif args.command == "query":
        cmd_query(args)
    elif args.command == "verify-robotics":
        cmd_verify_robotics(args)

if __name__ == "__main__":
    main()
