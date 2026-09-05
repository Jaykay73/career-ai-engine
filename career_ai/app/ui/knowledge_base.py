"""
Knowledge Base Explorer and Manager View for Career AI Streamlit Application.
Allows exploring, searching, viewing canonical markdown files, and adding new records.
"""

import streamlit as st
import yaml
from pathlib import Path
from typing import Dict, List, Any

from career_ai.core.config import settings
from career_ai.services.application_service import application_service
from career_ai.knowledge.parser import MarkdownParser

CATEGORIES = ["education", "certifications", "skills", "experience", "projects", "publications"]

def render_knowledge_base():
    st.markdown("## 📚 Canonical Knowledge Base Explorer")
    st.markdown(
        "John Aledare's single source of truth. All tailored resumes and cover letters are strictly grounded "
        "in these version-controlled Markdown records. Nothing is ever fabricated."
    )

    tab_explore, tab_add, tab_improve = st.tabs([
        "🔍 Explore & View Records",
        "➕ Add / Edit Canonical Record",
        "💡 Profile Improvement Assistant"
    ])

    kb_dir = settings.knowledge_dir

    # Tab 1: Explore & View Records
    with tab_explore:
        col_cat, col_search = st.columns([1, 2])
        with col_cat:
            selected_cat = st.selectbox("Select Category", CATEGORIES, index=4) # Default to projects
        with col_search:
            search_query = st.text_input("Filter records by keyword / tech", placeholder="e.g. PyTorch, FastAPI, Oracle")

        cat_dir = kb_dir / selected_cat
        if not cat_dir.exists():
            st.info(f"No records found in directory: `{cat_dir}`")
            return

        files = sorted(list(cat_dir.glob("*.md")))
        if not files:
            st.info(f"No markdown records found in {selected_cat}.")
            return

        # Parse and display records
        records = []
        for f in files:
            try:
                meta, body = MarkdownParser.parse_file(f)
                records.append({
                    "meta": meta,
                    "body": body,
                    "file": f,
                    "title": meta.get("title", f.stem.replace("-", " ").title()),
                    "slug": f.stem,
                    "technologies": meta.get("technologies", []),
                    "metrics": meta.get("metrics", []),
                    "links": meta.get("links", {})
                })
            except Exception as e:
                pass

        # Filter by search query if provided
        if search_query.strip():
            q = search_query.lower()
            records = [
                r for r in records
                if q in r["title"].lower()
                or any(q in t.lower() for t in r["technologies"])
                or q in r["body"].lower()
            ]

        st.caption(f"Showing {len(records)} records in `{selected_cat}`")

        for rec in records:
            meta = rec["meta"]
            with st.expander(f"📄 **{rec['title']}** (`{rec['slug']}.md`)", expanded=False):
                c1, c2 = st.columns([2, 1])
                with c1:
                    if meta.get("organization"):
                        st.markdown(f"**Organization / Context**: {meta['organization']}")
                    if meta.get("date_range"):
                        st.markdown(f"**Timeline**: {meta['date_range']}")
                    if meta.get("tagline"):
                        st.markdown(f"**Tagline**: _{meta['tagline']}_")
                    if meta.get("summary"):
                        st.markdown(f"**Summary**: {meta['summary']}")
                with c2:
                    if rec["technologies"]:
                        st.markdown("**Technologies / Skills**:")
                        st.write(", ".join([f"`{t}`" for t in rec["technologies"]]))
                    if rec["metrics"]:
                        st.markdown("**Verified Metrics**:")
                        for m in rec["metrics"]:
                            st.markdown(f"- 📈 `{m}`")
                    if rec["links"]:
                        st.markdown("**Links**:")
                        for k, v in rec["links"].items():
                            st.markdown(f"- [{k}]({v})")

                st.markdown("**Content & Contributions**:")
                st.markdown(rec["body"])
                st.markdown(f"**Source File**: `{rec['file']}`")

    # Tab 2: Add / Edit Record
    with tab_add:
        st.markdown("### ➕ Create New Canonical Record")
        st.markdown(
            "Add verified experience, a new project, or a new certification directly to John's knowledge base. "
            "Once saved, re-index to immediately make it searchable via BM25 and dense vectors."
        )

        with st.form("new_record_form"):
            form_cat = st.selectbox("Category", CATEGORIES, index=4)
            form_title = st.text_input("Title / Name *", placeholder="e.g. Real-Time Distributed Search Engine")
            form_slug = st.text_input("Slug (Filename without .md) *", placeholder="e.g. distributed-search-engine")
            form_org = st.text_input("Organization / Institution", placeholder="e.g. Independent, Company, University")
            form_dates = st.text_input("Date Range", placeholder="e.g. 2024 – Present")
            form_tagline = st.text_input("Tagline / Short Summary", placeholder="e.g. High-throughput distributed search engine in Rust")
            form_tech = st.text_input("Technologies (comma separated)", placeholder="e.g. Python, PyTorch, FastAPI, Docker, Qdrant")
            form_metrics = st.text_input("Verified Metrics (comma separated)", placeholder="e.g. 96.2% ROC-AUC, 40% latency reduction")
            form_repo = st.text_input("GitHub / Repository Link", placeholder="https://github.com/...")
            form_live = st.text_input("Live Demo / Documentation Link", placeholder="https://...")
            form_bullets = st.text_area(
                "Authoritative Bullet Points (one per line, format: ACTION + TECH METHOD + PURPOSE + RESULT)",
                height=150,
                placeholder="Engineered high-throughput RAG search using Qdrant and FastAPI, decreasing retrieval latency by 45%.\nImplemented reciprocal rank fusion algorithm in Python, improving search precision across 10,000 documents."
            )

            submit_new = st.form_submit_button("💾 Save Record to Canonical Knowledge Base")

            if submit_new:
                if not form_title.strip() or not form_slug.strip():
                    st.error("Title and Slug are required fields.")
                else:
                    slug_clean = "".join(c for c in form_slug.lower().replace(" ", "-") if c.isalnum() or c in "-_")
                    target_file = kb_dir / form_cat / f"{slug_clean}.md"
                    target_file.parent.mkdir(parents=True, exist_ok=True)

                    frontmatter = {
                        "title": form_title.strip(),
                        "type": form_cat,
                        "organization": form_org.strip() if form_org.strip() else None,
                        "date_range": form_dates.strip() if form_dates.strip() else None,
                        "tagline": form_tagline.strip() if form_tagline.strip() else None,
                        "technologies": [t.strip() for t in form_tech.split(",") if t.strip()],
                        "metrics": [m.strip() for m in form_metrics.split(",") if m.strip()],
                        "links": {k: v for k, v in [("github", form_repo.strip()), ("live", form_live.strip())] if v}
                    }

                    bullets = [f"- {line.strip()}" for line in form_bullets.splitlines() if line.strip()]
                    body_bullets = "\n".join(bullets)

                    file_content = f"""---
{yaml.dump(frontmatter, sort_keys=False)}---

## Overview
{form_tagline.strip()}

## Key Contributions & Technical Accomplishments
{body_bullets}
"""
                    target_file.write_text(file_content, encoding="utf-8")
                    st.success(f"Successfully created `{target_file}`! Rebuilding index now...")
                    application_service.reindex_knowledge()
                    st.success("Hybrid index updated. Record is now live in the engine.")
                    st.rerun()

    # Tab 3: Profile Improvement Assistant
    with tab_improve:
        st.markdown("### 💡 Profile Improvement & Skill Gap Diagnostics")
        st.markdown(
            "Analyze recurring unrepresented requirements from recent job applications to receive actionable, "
            "zero-BS suggestions on high-value projects or certifications John can build or acquire."
        )

        st.info(
            "**Strategic Recommendation Engine**: When you paste job descriptions into the Job Application Generator, "
            "unrepresented requirements are tracked. Based on current AI/ML Engineer postings, top complementary areas include:  \n"
            "- **Distributed Training**: Ray Train, PyTorch DDP, DeepSpeed on multi-GPU setups.  \n"
            "- **Production MLOps**: MLflow model registry, BentoML / Triton Inference Server deployment.  \n"
            "- **LLM Evaluation**: Ragas, TruLens, DeepEval automated CI/CD testing frameworks."
        )
