"""
Generated Applications History View for Career AI Streamlit Application.
Displays historical applications, generated LaTeX resumes, cover letters, and audit trails.
"""

import streamlit as st
import json
from pathlib import Path
from career_ai.services.application_service import application_service

def render_generated_applications():
    st.markdown("## 📂 Generated Applications History")
    st.markdown("Browse, inspect, and download previously generated tailored CVs, cover letters, and verification metadata.")

    try:
        apps = application_service.get_generated_applications()
    except Exception as e:
        st.error(f"Failed to fetch application records from database: {e}")
        apps = []

    if not apps:
        st.info("No applications generated yet. Head over to **Job Application Generator** to tailor your first application!")
        return

    st.caption(f"Total Applications Stored: {len(apps)}")

    for app in apps:
        app_date = str(app.created_at)[:16] if app.created_at else "Recent"
        header_title = f"🏢 **{app.company_name}** — {app.job_title} ({app_date})"

        with st.expander(header_title, expanded=False):
            meta = {}
            if app.metadata_json:
                try:
                    meta = json.loads(app.metadata_json)
                except Exception:
                    pass

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Company**: {app.company_name}")
                st.markdown(f"**Job Title**: {app.job_title}")
            with c2:
                verified_status = "✅ Verified Clean" if meta.get("verified") else "⚠️ Unverified Claims Flagged"
                st.markdown(f"**Verification**: {verified_status}")
                st.markdown(f"**PDF Available**: {'Yes' if app.pdf_path else 'No (.tex source ready)'}")
            with c3:
                st.markdown(f"**Application ID**: `{app.id[:8]}...`")

            st.markdown("---")

            col_resume, col_cl = st.columns(2)

            with col_resume:
                st.markdown("#### 📄 Resume Source")
                tex_file = Path(app.tex_path) if app.tex_path else None
                if tex_file and tex_file.exists():
                    tex_code = tex_file.read_text(encoding="utf-8")
                    st.download_button(
                        label=f"⬇️ Download Resume ({tex_file.name})",
                        data=tex_code,
                        file_name=tex_file.name,
                        mime="text/x-tex",
                        key=f"dl_res_{app.id}"
                    )
                    with st.expander("Preview Resume LaTeX Source"):
                        st.code(tex_code[:1200] + "\n...", language="latex")
                else:
                    st.warning("Resume .tex file not found on disk.")

            with col_cl:
                st.markdown("#### ✉️ Cover Letter")
                if app.cover_letter_text:
                    st.text_area("Cover Letter Text", app.cover_letter_text, height=180, key=f"cl_view_{app.id}")
                else:
                    st.info("No cover letter generated for this record.")

            if meta:
                with st.expander("📊 View Audit & Grounding Metadata"):
                    st.json(meta)
