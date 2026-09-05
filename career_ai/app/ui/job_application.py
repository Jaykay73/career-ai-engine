"""
Job Application Generator View for Career AI Streamlit Application.
Allows inputting job postings, performing hybrid evidence retrieval,
inspecting supported vs unrepresented requirements, and generating verified LaTeX applications.
"""

import streamlit as st
import json
from pathlib import Path
from typing import Optional

from career_ai.services.application_service import application_service
from career_ai.jobs.schemas import JobAnalysisResult
from career_ai.core.config import settings

SAMPLE_JOB_TITLE = "Machine Learning Engineer"
SAMPLE_COMPANY = "Alpha Health AI"
SAMPLE_JD = """We are seeking a talented Machine Learning Engineer to build and deploy deep learning pipelines for biomedical imaging and AI-assisted clinical workflows.

Responsibilities:
- Build computer vision models with PyTorch and TensorFlow for medical image segmentation and classification (MRI, retinal imaging).
- Develop LLM applications with LangChain, RAG architecture, and vector databases (Qdrant, Pinecone).
- Design and maintain production REST APIs using FastAPI, Docker, and AWS.
- Collaborate with clinical research teams to evaluate model performance (ROC-AUC, sensitivity, latency).

Requirements:
- Bachelor's degree in Computer Engineering, Computer Science, or related technical field.
- Strong proficiency in Python, PyTorch, Scikit-Learn, and FastAPI.
- Demonstrated experience with Retrieval-Augmented Generation (RAG) and embeddings.
- Hands-on experience with Computer Vision (CNNs, transfer learning, medical imaging).
- Demonstrated experience deploying models with Docker and CI/CD pipelines.
- Experience with Kubernetes or distributed training is a plus.
"""

def render_job_application():
    st.markdown("## 💼 Job Application Generator")
    st.markdown(
        "Paste a job description below. The engine extracts requirements, performs hybrid BM25 + Vector retrieval "
        "with Reciprocal Rank Fusion against John Aledare's canonical knowledge base, and outputs an evidence-grounded ATS-tailored application."
    )

    # Pre-fill sample button
    col_prefill, col_clear = st.columns([2, 8])
    with col_prefill:
        if st.button("📋 Load Sample JD", help="Loads a sample Machine Learning Engineer job description"):
            st.session_state["input_job_title"] = SAMPLE_JOB_TITLE
            st.session_state["input_company"] = SAMPLE_COMPANY
            st.session_state["input_jd"] = SAMPLE_JD
            st.session_state.pop("analysis_result", None)
            st.session_state.pop("generation_result", None)
            st.rerun()

    # Form inputs
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            job_title = st.text_input(
                "Job Title *",
                value=st.session_state.get("input_job_title", ""),
                placeholder="e.g. Senior Machine Learning Engineer"
            )
        with c2:
            company_name = st.text_input(
                "Company Name *",
                value=st.session_state.get("input_company", ""),
                placeholder="e.g. Alpha Health AI"
            )

        c3, c4 = st.columns(2)
        with c3:
            company_url = st.text_input(
                "Company Website / Careers URL (optional)",
                value=st.session_state.get("input_company_url", ""),
                placeholder="https://alphahealth.ai"
            )
        with c4:
            job_url = st.text_input(
                "Job Posting URL (optional)",
                value=st.session_state.get("input_job_url", ""),
                placeholder="https://linkedin.com/jobs/view/..."
            )

        jd_text = st.text_area(
            "Job Description (Raw Text) *",
            value=st.session_state.get("input_jd", ""),
            height=240,
            placeholder="Paste complete job description text here..."
        )

    # Step 1: Analyze Job Posting Action
    analyze_col, _ = st.columns([2, 6])
    with analyze_col:
        analyze_btn = st.button("🔍 Step 1: Analyze & Match Evidence", type="primary", use_container_width=True)

    if analyze_btn:
        if not jd_text.strip():
            st.error("Please provide job description text to analyze.")
            return

        with st.spinner("Extracting requirements and performing BM25 + Dense Hybrid RRF Retrieval..."):
            try:
                analysis = application_service.analyze_job_posting(
                    job_description=jd_text,
                    company_name=company_name.strip() or None,
                    job_title=job_title.strip() or None,
                    company_url=company_url.strip() or None,
                    job_url=job_url.strip() or None
                )
                st.session_state["analysis_result"] = analysis
                st.session_state["last_jd"] = jd_text
                st.session_state.pop("generation_result", None)
                st.success("Job Analysis & Evidence Grounding Complete!")
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")
                return

    # Render Analysis Results if available
    analysis: Optional[JobAnalysisResult] = st.session_state.get("analysis_result")
    if analysis:
        st.markdown("---")
        st.markdown(f"### 📋 Requirements & Evidence Analysis: **{analysis.job_requirements.job_title}** at **{analysis.job_requirements.company_name}**")

        # Metric summary
        total_reqs = len(analysis.supported_requirements) + len(analysis.unsupported_requirements)
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total Extracted Requirements", total_reqs)
        with m2:
            st.metric("🟢 Supported in Knowledge Base", len(analysis.supported_requirements))
        with m3:
            st.metric("🟡 Not Represented in KB", len(analysis.unsupported_requirements))

        # Evidence Display Tabs
        project_chunks = [e for e in analysis.retrieved_evidence if e.chunk.source_type == "project"]
        tab_supp, tab_unsupp, tab_projects = st.tabs([
            f"🟢 Supported ({len(analysis.supported_requirements)})",
            f"🟡 Not Represented ({len(analysis.unsupported_requirements)})",
            f"🏆 Relevant Projects ({len(project_chunks)})"
        ])

        with tab_supp:
            st.markdown("Requirements with verifiable evidence found via BM25 + Vector RRF:")
            for idx, req in enumerate(analysis.supported_requirements):
                with st.expander(f"✅ {req.requirement}", expanded=(idx < 2)):
                    st.markdown(f"**Category**: `{req.category}` | **Evidence Chunks**: `{len(req.top_evidence)}`")
                    for e in req.top_evidence[:3]:
                        st.markdown(f"- **[{e.chunk.source_type.upper()}] {e.chunk.title}** (RRF Score: `{e.rrf_score:.4f}`)")
                        st.caption(f"_{e.chunk.text[:220]}..._")

        with tab_unsupp:
            st.markdown(
                "> **Zero-Fabrication Guarantee**: The items below are not documented in John's canonical knowledge base. "
                "The engine will **not** invent experience or inflate claims to cover these gaps."
            )
            for req in analysis.unsupported_requirements:
                st.warning(f"🟡 **Not represented**: {req.requirement}")

        with tab_projects:
            st.markdown("Top project evidence ranked by semantic relevance to this job posting:")
            seen_projects = set()
            for e in project_chunks:
                if e.chunk.source_id not in seen_projects:
                    seen_projects.add(e.chunk.source_id)
                    st.markdown(f"- **{e.chunk.title}** (RRF Score: `{e.rrf_score:.4f}`)")
                    st.caption(f"File: `knowledge/projects/{e.chunk.source_id}.md`")

        st.markdown("---")

        # Step 2: Generate Application
        st.markdown("### 🚀 Step 2: Generate Tailored LaTeX Application")
        st.markdown("Generates an ATS-compliant resume (`.tex` / `.pdf`), tailored cover letter, and runs factual claim verification.")

        gen_col1, _ = st.columns([2, 6])
        with gen_col1:
            gen_btn = st.button("✨ Generate Verified Application", type="primary", use_container_width=True)

        if gen_btn:
            with st.spinner("Generating tailored CV, rendering LaTeX, and executing factual claim verification..."):
                try:
                    result = application_service.generate_tailored_application(
                        analysis=analysis,
                        job_description=st.session_state.get("last_jd", jd_text),
                        company_name_override=company_name.strip() or None,
                        job_title_override=job_title.strip() or None
                    )
                    st.session_state["generation_result"] = result
                    st.success("Tailored Application Generated & Verified Successfully!")
                except Exception as e:
                    st.error(f"Generation failed: {str(e)}")
                    return

    # Render Generation Results if available
    gen_result = st.session_state.get("generation_result")
    if gen_result:
        st.markdown("---")
        st.markdown("### 📦 Generated Application Package")

        verification = gen_result.get("verification_result")
        if verification and verification.is_valid:
            st.success("🛡️ **Factual Claim Verification Passed!** All bullet points and claims are grounded in John's verified knowledge base.")
        elif verification:
            st.warning(f"⚠️ Verification Notes: {len(verification.unsupported_claims)} claims flagged for human review.")

        # Tabs for CV, Cover Letter, Traceability
        cv_tab, cl_tab, trace_tab, raw_tab = st.tabs([
            "📄 Tailored Resume (.tex / .pdf)",
            "✉️ Tailored Cover Letter",
            "🔍 Grounded Evidence Traceability",
            "⚙️ Application Metadata"
        ])

        with cv_tab:
            tex_path = Path(gen_result["tex_path"])
            if tex_path.exists():
                tex_content = tex_path.read_text(encoding="utf-8")
                c_dl1, c_dl2 = st.columns(2)
                with c_dl1:
                    st.download_button(
                        label="⬇️ Download Resume LaTeX (.tex)",
                        data=tex_content,
                        file_name=tex_path.name,
                        mime="text/x-tex",
                        use_container_width=True
                    )
                with c_dl2:
                    if gen_result.get("pdf_compiled") and gen_result.get("pdf_path") and Path(gen_result["pdf_path"]).exists():
                        with open(gen_result["pdf_path"], "rb") as f:
                            st.download_button(
                                label="⬇️ Download Resume PDF (.pdf)",
                                data=f.read(),
                                file_name=Path(gen_result["pdf_path"]).name,
                                mime="application/pdf",
                                use_container_width=True
                            )
                    else:
                        st.info("ℹ️ Local `pdflatex` not detected. Download the `.tex` file to compile with Overleaf, MiKTeX, or TeX Live.")

                st.markdown(f"**Saved to**: `{tex_path}`")
                st.code(tex_content, language="latex", line_numbers=True)

        with cl_tab:
            cl_tex_path = Path(gen_result["cover_letter_tex_path"])
            cover_letter = gen_result.get("cover_letter")
            if cover_letter:
                st.markdown(f"**Company**: {cover_letter.company_name} | **Role**: {cover_letter.job_title}")
                st.markdown(f"_{cover_letter.opening}_")
                for para in cover_letter.body_paragraphs:
                    st.markdown(para)
                st.markdown(f"_{cover_letter.closing}_")
                st.markdown(f"**{cover_letter.sign_off}**,  \nJohn Aledare")

            if cl_tex_path.exists():
                cl_tex = cl_tex_path.read_text(encoding="utf-8")
                st.download_button(
                    label="⬇️ Download Cover Letter LaTeX (.tex)",
                    data=cl_tex,
                    file_name=cl_tex_path.name,
                    mime="text/x-tex"
                )

        with trace_tab:
            st.markdown("#### Evidence Traceability Matrix")
            st.markdown("Every project, skill, and bullet point in the generated resume links back to its verified source in the Markdown knowledge base:")
            tailored_cv = gen_result.get("tailored_cv")
            if tailored_cv:
                st.markdown("##### Included Projects:")
                for proj in tailored_cv.projects:
                    st.markdown(f"**{proj.name}** (`knowledge/projects/{proj.slug}.md`)")
                    for b in proj.bullet_points:
                        st.markdown(f"- {b}")

        with raw_tab:
            st.json(gen_result.get("metadata", {}))
