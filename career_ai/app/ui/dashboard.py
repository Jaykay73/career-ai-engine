"""
Dashboard view for Career AI Streamlit Application.
Displays knowledge base statistics, system health, and strict profile constraints.
"""

import streamlit as st
import pandas as pd
from datetime import datetime

from career_ai.services.application_service import application_service
from career_ai.core.config import settings

def render_dashboard():
    st.markdown("## 📊 System Dashboard & Knowledge Status")
    st.markdown("Overview of the local evidence-grounded application engine.")

    # 1. System Summary & Metrics
    try:
        summary = application_service.get_knowledge_summary()
    except Exception as e:
        st.error(f"Error loading knowledge summary: {e}")
        summary = {
            "record_counts": {},
            "total_records": 0,
            "index_metadata": {},
            "embedding_model": settings.embedding_model,
            "llm_provider": settings.llm_provider,
            "latex_available": False
        }

    counts = summary.get("record_counts", {})
    total_records = summary.get("total_records", 0)
    meta = summary.get("index_metadata", {})
    total_chunks = meta.get("chunk_count", meta.get("total_chunks", 0)) if meta else 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Knowledge Records", total_records, delta=f"{len(counts)} categories")
    with col2:
        st.metric("Indexed Chunks", total_chunks, delta="Hybrid RRF Ready")
    with col3:
        status_text = "Ready (DeepSeek)" if settings.deepseek_api_key else "Offline Heuristic"
        st.metric("LLM Provider", settings.llm_provider.upper(), delta=status_text)
    with col4:
        latex_status = "Available" if summary.get("latex_available") else "TeX Source Only"
        st.metric("LaTeX Compiler", latex_status, delta="Safe Fallback Active")

    st.markdown("---")

    # 2. Inviolable Profile Rules & Zero-Fabrication Contract
    with st.expander("🛡️ Inviolable Truth & Hallucination Defense Rules (Active)", expanded=True):
        st.markdown(
            """
            This engine enforces **strict cryptographic-like factual grounding** to protect John Aledare's professional integrity:
            
            1. 🎓 **Degree Integrity Rule**:
               - Representation is strictly: **`Bachelor of Engineering (B.Eng.) in Computer Engineering` — `University of Ilorin` (2021 – 2026)**.
               - **Zero Tolerance**: Never outputs degree classifications, GPAs, or honours classifications (e.g. *Second Class*, *2:2*, *First Class*).
            2. 📜 **Mandatory Certifications Invariant**:
               - All three verified certifications are permanently included on every generated CV:
                 - **Oracle Cloud Infrastructure 2024 Generative AI Certified Professional** (Oracle, 2024)
                 - **Oracle Cloud Infrastructure 2024 AI Foundations Associate** (Oracle, 2024)
                 - **Machine Learning Specialization** (Stanford University & DeepLearning.AI, 2024)
            3. 🚫 **Anti-Scoring Truth Principle**:
               - We **never** invent or compute fake match percentages (e.g. "87% match").
               - Requirements are strictly categorized as `SUPPORTED` (backed by retrieved chunks) or `NOT_SUPPORTED_IN_KNOWLEDGE_BASE` (*"Not represented in current knowledge base"*).
            4. 🔬 **Zero Metric Fabrication**:
               - Bullets follow `ACTION + TECHNICAL METHOD + PURPOSE + RESULT`.
               - Numerical results (e.g. *96.2% ROC-AUC*, *40% latency reduction*) are only included if explicitly verified in the Markdown knowledge base.
            """
        )

    # 3. Knowledge Base Breakdown
    st.markdown("### 📚 Canonical Records Breakdown")
    col_breakdown, col_engine = st.columns([1, 1])

    with col_breakdown:
        if counts:
            df_counts = pd.DataFrame(
                list(counts.items()),
                columns=["Category", "Total Records"]
            )
            df_counts["Category"] = df_counts["Category"].str.capitalize()
            st.dataframe(df_counts, use_container_width=True, hide_index=True)
        else:
            st.info("No records indexed yet. Click below to scan and build index.")

    with col_engine:
        st.markdown(
            f"""
            **Retrieval Engine Specifications**:
            - **Lexical**: BM25 Okapi with custom technical stopword filtering
            - **Dense Vectors**: `BAAI/bge-small-en-v1.5` (384-dimensional cosine similarity)
            - **Vector Store**: Qdrant embedded mode (`data/qdrant_db`)
            - **Fusion**: Reciprocal Rank Fusion ($RRF(d) = \\sum \\frac{{1}}{{k + rank_i(d)}}$, $k={settings.rrf_k}$)
            - **Relational DB**: SQLite (`data/career_ai.db`)
            - **Total Monthly Cloud Cost**: **$0.00** (100% local-first)
            """
        )

    st.markdown("---")

    # 4. Quick Actions
    st.markdown("### ⚡ Quick Operations")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        if st.button("🔄 Rebuild Hybrid Index", use_container_width=True):
            with st.spinner("Rebuilding BM25 & Qdrant vector index..."):
                result = application_service.reindex_knowledge()
                st.success(f"Indexed {result.get('files_indexed', 0)} files ({result.get('chunks_indexed', 0)} chunks) in {result.get('duration_seconds', 0):.2f}s!")
                st.rerun()

    with btn_col2:
        if st.button("💼 New Job Application", use_container_width=True, type="primary"):
            st.session_state["nav"] = "💼 Job Application Generator"
            st.rerun()

    with btn_col3:
        if st.button("📂 View Application History", use_container_width=True):
            st.session_state["nav"] = "📂 Generated Applications History"
            st.rerun()
