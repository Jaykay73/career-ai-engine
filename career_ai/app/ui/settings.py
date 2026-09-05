"""
Settings & Diagnostics View for Career AI Streamlit Application.
Provides configuration inspection, LLM / Retrieval tuning, and LaTeX compilation diagnostics.
"""

import streamlit as st
import shutil
from pathlib import Path

from career_ai.core.config import settings
from career_ai.services.application_service import application_service

def render_settings():
    st.markdown("## ⚙️ System Settings & Environment Diagnostics")
    st.markdown("Inspect and tune configuration, LLM parameters, retrieval hyperparameters, and toolchain diagnostics.")

    tab_llm, tab_retrieval, tab_latex, tab_diagnostics = st.tabs([
        "🤖 LLM & Intelligence",
        "🔍 Hybrid Retrieval & RRF",
        "📄 LaTeX & PDF Compiler",
        "🩺 System Diagnostics"
    ])

    # Tab 1: LLM Settings
    with tab_llm:
        st.markdown("### LLM Configuration")
        st.markdown(
            "The system uses OpenAI-compatible APIs (optimized for **DeepSeek V3 / R1**). "
            "If no API key is set, the engine gracefully falls back to deterministic, offline rule-based heuristic generation."
        )

        llm_col1, llm_col2 = st.columns(2)
        with llm_col1:
            st.text_input("LLM Provider", value=settings.llm_provider, disabled=True)
            st.text_input("Base URL", value=settings.llm_base_url, disabled=True)
        with llm_col2:
            st.text_input("Model Name", value=settings.llm_model, disabled=True)
            masked_key = f"{settings.deepseek_api_key[:6]}...{settings.deepseek_api_key[-4:]}" if settings.deepseek_api_key else "(Not configured - using heuristic fallback)"
            st.text_input("API Key Status", value=masked_key, disabled=True)

        st.info("💡 To update LLM credentials, modify `.env` in the project root and restart the application.")

    # Tab 2: Hybrid Retrieval & RRF
    with tab_retrieval:
        st.markdown("### Hybrid Search Hyperparameters")
        st.markdown(
            "The engine merges lexical BM25 rankings and dense vector cosine similarity via "
            "**Reciprocal Rank Fusion (RRF)**:  \n"
            "$$RRF(d) = \\sum_{m \\in \\{BM25, Vector\\}} \\frac{1}{k + rank_m(d)}$$"
        )

        r_col1, r_col2 = st.columns(2)
        with r_col1:
            st.number_input("RRF Smoothing Parameter ($k$)", value=settings.rrf_k, min_value=1, max_value=200, disabled=True)
            st.text_input("Dense Embedding Model", value=settings.embedding_model, disabled=True)
        with r_col2:
            st.number_input("BM25 Top-K Candidates", value=settings.bm25_top_k, min_value=5, max_value=100, disabled=True)
            st.number_input("Vector Top-K Candidates", value=settings.vector_top_k, min_value=5, max_value=100, disabled=True)

    # Tab 3: LaTeX Compiler Setup
    with tab_latex:
        st.markdown("### LaTeX & PDF Compilation Subsystem")
        pdflatex_path = shutil.which("pdflatex")
        xelatex_path = shutil.which("xelatex")
        latexmk_path = shutil.which("latexmk")

        if pdflatex_path or xelatex_path or latexmk_path:
            st.success(f"✅ Active LaTeX Compiler Detected: `{pdflatex_path or xelatex_path or latexmk_path}`")
            st.markdown("PDFs are automatically compiled directly into the application output folder upon generation.")
        else:
            st.warning("⚠️ No local `pdflatex` or `latexmk` binary found on Windows PATH.")
            st.markdown(
                """
                **How this engine handles this gracefully:**
                - The engine **never crashes or blocks**. It outputs complete, valid, ATS-optimized `.tex` resume and cover letter source files directly to the `output/` directory and UI download buttons.
                - You can compile them immediately in:
                  1. **Overleaf (Free Cloud)**: Go to [overleaf.com](https://www.overleaf.com), create a blank project, and paste or upload the generated `.tex` file.
                  2. **Local Windows Installation (Recommended for 100% offline auto-PDF)**:
                     Run this in your Windows PowerShell terminal:
                     ```powershell
                     winget install MiKTeX.MiKTeX
                     # Or via Chocolatey:
                     # choco install miktex
                     ```
                     After installing, restart your terminal or Streamlit, and PDF compilation will automatically activate!
                """
            )

    # Tab 4: System Diagnostics
    with tab_diagnostics:
        st.markdown("### Storage & Path Health")
        diag_data = {
            "Knowledge Base Directory": str(settings.knowledge_dir),
            "Output Directory": str(settings.output_dir),
            "SQLite Database Path": str(settings.sqlite_db_path),
            "Qdrant DB Path": str(settings.qdrant_path),
            "Templates Directory": str(settings.templates_dir),
            "DeepSeek Enabled": bool(settings.deepseek_api_key),
            "LaTeX pdflatex Available": bool(pdflatex_path)
        }
        for k, v in diag_data.items():
            st.markdown(f"- **{k}**: `{v}`")

        st.markdown("---")
        if st.button("🧪 Trigger Index Verification"):
            with st.spinner("Verifying index integrity..."):
                summary = application_service.get_knowledge_summary()
                st.json(summary)
