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
        "Paste any raw job description below. The engine automatically detects the **Role / Job Title** and **Company Name**, "
        "retrieves grounded evidence from John Aledare's canonical knowledge base via BM25 + Dense Vectors (RRF), "
        "and generates a tailored ATS resume and cover letter."
    )

    # 1. Primary Input: Job Description Textarea
    jd_text = st.text_area(
        "📋 Job Description (Paste raw text here) *",
        value=st.session_state.get("input_jd", ""),
        height=260,
        placeholder="Paste full job posting text here (from LinkedIn, Indeed, Greenhouse, Lever, etc.)..."
    )

    # Action Toolbar
    col_analyze, col_detect, col_sample, col_clear = st.columns([3, 2, 2, 1])

    with col_sample:
        if st.button("📋 Load Sample JD", use_container_width=True, help="Loads a sample Machine Learning Engineer job posting"):
            st.session_state["input_jd"] = SAMPLE_JD
            metadata = application_service.extract_job_metadata(SAMPLE_JD)
            st.session_state["input_job_title"] = metadata.get("job_title", SAMPLE_JOB_TITLE)
            st.session_state["input_company"] = metadata.get("company_name", SAMPLE_COMPANY)
            st.session_state.pop("analysis_result", None)
            st.session_state.pop("generation_result", None)
            st.rerun()

    with col_detect:
        if st.button("⚡ Extract Role & Company", use_container_width=True, help="Auto-extracts company name and job title from the text"):
            if jd_text.strip():
                metadata = application_service.extract_job_metadata(jd_text)
                st.session_state["input_job_title"] = metadata.get("job_title", "")
                st.session_state["input_company"] = metadata.get("company_name", "")
                st.session_state["input_jd"] = jd_text
                st.success(f"Extracted: **{metadata.get('job_title')}** at **{metadata.get('company_name')}**")
                st.rerun()
            else:
                st.warning("Please paste a job description first.")

    with col_clear:
        if st.button("🧹 Clear", use_container_width=True, help="Clears the current input"):
            st.session_state.pop("input_jd", None)
            st.session_state.pop("input_job_title", None)
            st.session_state.pop("input_company", None)
            st.session_state.pop("input_company_url", None)
            st.session_state.pop("input_job_url", None)
            st.session_state.pop("analysis_result", None)
            st.session_state.pop("generation_result", None)
            st.rerun()

    with col_analyze:
        analyze_btn = st.button("🔍 Step 1: Analyze & Match Evidence", type="primary", use_container_width=True)

    # 2. Extracted / Inferred Role & Company (Editable)
    # Auto-extract if text is present and fields are empty
    if jd_text.strip() and not st.session_state.get("input_job_title"):
        auto_meta = application_service.extract_job_metadata(jd_text)
        st.session_state["input_job_title"] = auto_meta.get("job_title", "")
        st.session_state["input_company"] = auto_meta.get("company_name", "")

    st.markdown("##### 🏢 Role & Company (Auto-Extracted)")
    c1, c2 = st.columns(2)
    with c1:
        job_title = st.text_input(
            "Role / Job Title",
            value=st.session_state.get("input_job_title", ""),
            placeholder="Auto-detected from job text (e.g. Senior Machine Learning Engineer)"
        )
    with c2:
        company_name = st.text_input(
            "Company Name",
            value=st.session_state.get("input_company", ""),
            placeholder="Auto-detected from job text (e.g. Alpha Health AI)"
        )

    # Optional URLs expander
    with st.expander("🔗 Additional Job Links (Optional)", expanded=False):
        c3, c4 = st.columns(2)
        with c3:
            company_url = st.text_input(
                "Company Website URL",
                value=st.session_state.get("input_company_url", ""),
                placeholder="https://company.com"
            )
        with c4:
            job_url = st.text_input(
                "Job Posting URL",
                value=st.session_state.get("input_job_url", ""),
                placeholder="https://linkedin.com/jobs/view/..."
            )

    # Step 1: Analyze Execution
    if analyze_btn:
        if not jd_text.strip():
            st.error("Please paste a job description into the box above.")
            return

        with st.spinner("Extracting requirements and performing BM25 + Dense Hybrid RRF Retrieval..."):
            try:
                analysis = application_service.analyze_job_posting(
                    job_description=jd_text,
                    company_name=company_name.strip() or None,
                    job_title=job_title.strip() or None,
                    company_url=company_url.strip() if 'company_url' in locals() and company_url else None,
                    job_url=job_url.strip() if 'job_url' in locals() and job_url else None
                )
                # Sync back extracted values to session state
                st.session_state["input_job_title"] = analysis.job_requirements.job_title
                st.session_state["input_company"] = analysis.job_requirements.company_name
                st.session_state["analysis_result"] = analysis
                st.session_state["last_jd"] = jd_text
                st.session_state.pop("generation_result", None)
                st.success(f"Matched evidence for **{analysis.job_requirements.job_title}** at **{analysis.job_requirements.company_name}**!")
                st.rerun()
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
                    st.session_state.pop("refinement_messages", None)
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

        # --- Interactive AI Refinement Chatbox ---
        st.markdown("#### 💬 Refine with AI Before Downloading")
        st.caption("Tell the AI what to change, rephrase, or emphasize (e.g. *'Highlight my Power BI and time series work in the first bullet'*, *'Shorten the summary'*, *'Focus more on data analytics'*).")

        eff_title = gen_result.get("job_title", "Target Role")
        eff_comp = gen_result.get("company_name", "Target Company")

        if "refinement_messages" not in st.session_state or not st.session_state["refinement_messages"]:
            st.session_state["refinement_messages"] = [
                {
                    "role": "assistant",
                    "content": f"I have tailored your resume and cover letter for **{eff_title}** at **{eff_comp}**. If you would like any adjustments, rewording, or specific technical emphasis before downloading, tell me below!"
                }
            ]

        chat_container = st.container(height=260, border=True)
        with chat_container:
            for msg in st.session_state["refinement_messages"]:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        user_correction = st.chat_input("Send correction or adjustment to the LLM (e.g., 'Emphasize Power BI in Queryfier bullets')...")
        if user_correction:
            st.session_state["refinement_messages"].append({"role": "user", "content": user_correction})
            with st.spinner("Applying corrections, re-verifying claims, and updating LaTeX / PDF..."):
                try:
                    updated_result, reply_msg = application_service.refine_application(
                        current_result=gen_result,
                        user_instruction=user_correction,
                        analysis=analysis
                    )
                    st.session_state["generation_result"] = updated_result
                    st.session_state["refinement_messages"].append({"role": "assistant", "content": reply_msg})
                    st.rerun()
                except Exception as e:
                    err = f"Correction failed: {str(e)}"
                    st.session_state["refinement_messages"].append({"role": "assistant", "content": f"⚠️ {err}"})
                    st.error(err)

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
                role_name = getattr(cover_letter, "job_title", None) or getattr(cover_letter, "position", "Target Role")
                sign_off_val = getattr(cover_letter, "sign_off", "Sincerely")
                st.markdown(f"**Company**: {cover_letter.company_name} | **Role**: {role_name}")
                st.markdown(f"_{cover_letter.opening}_")
                for para in cover_letter.body_paragraphs:
                    st.markdown(para)
                st.markdown(f"_{cover_letter.closing}_")
                st.markdown(f"**{sign_off_val}**,  \nJohn Aledare")

            c_cl1, c_cl2 = st.columns(2)
            with c_cl1:
                if cl_tex_path.exists():
                    cl_tex = cl_tex_path.read_text(encoding="utf-8")
                    st.download_button(
                        label="⬇️ Download Cover Letter LaTeX (.tex)",
                        data=cl_tex,
                        file_name=cl_tex_path.name,
                        mime="text/x-tex",
                        use_container_width=True
                    )
            with c_cl2:
                cl_pdf_path = gen_result.get("cover_letter_pdf_path")
                if cl_pdf_path and Path(cl_pdf_path).exists():
                    with open(cl_pdf_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Cover Letter PDF (.pdf)",
                            data=f.read(),
                            file_name=Path(cl_pdf_path).name,
                            mime="application/pdf",
                            use_container_width=True
                        )

        with trace_tab:
            st.markdown("#### Evidence Traceability Matrix")
            st.markdown("Every project, skill, and bullet point in the generated resume links back to its verified source in the Markdown knowledge base:")
            tailored_cv = gen_result.get("tailored_cv")
            if tailored_cv:
                st.markdown("##### Included Projects:")
                for proj in tailored_cv.projects:
                    st.markdown(f"**{proj.name}** (`{proj.technologies}`)")
                    for b in getattr(proj, "bullets", []):
                        ev_str = f" *(Evidence: {', '.join(b.evidence_ids)})*" if b.evidence_ids else ""
                        st.markdown(f"- {b.text}{ev_str}")

        with raw_tab:
            st.json(gen_result.get("metadata", {}))
