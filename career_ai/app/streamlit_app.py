"""
Main Streamlit Application Entry Point for Personal Career AI Engine.
Run with: streamlit run career_ai/app/streamlit_app.py
"""

import streamlit as st
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from career_ai.app.ui.dashboard import render_dashboard
from career_ai.app.ui.job_application import render_job_application
from career_ai.app.ui.knowledge_base import render_knowledge_base
from career_ai.app.ui.generated_applications import render_generated_applications
from career_ai.app.ui.settings import render_settings

# Configure page
st.set_page_config(
    page_title="Career AI Engine — John Aledare",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished, modern look
st.markdown(
    """
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }
    
    /* Metrics card enhancements */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    /* Headers styling */
    h1, h2, h3 {
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    
    /* Expander borders */
    .streamlit-expanderHeader {
        font-weight: 600;
        border-radius: 8px;
    }
    
    /* Custom badge styles */
    .badge-supported {
        background-color: #d1fae5;
        color: #065f46;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-unsupported {
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    /* Sidebar branding */
    .sidebar-brand {
        padding: 10px 0;
        border-bottom: 1px solid rgba(128, 128, 128, 0.2);
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize navigation in session state
if "nav" not in st.session_state:
    st.session_state["nav"] = "📊 Dashboard & Overview"

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🚀 Career AI Engine")
    st.markdown("**John Aledare** — Personal ATS Tailoring & Grounded Retrieval")
    st.markdown("---")

    nav_options = [
        "📊 Dashboard & Overview",
        "💼 Job Application Generator",
        "📚 Knowledge Base Explorer",
        "📂 Generated Applications History",
        "⚙️ Settings & Diagnostics"
    ]

    current_idx = nav_options.index(st.session_state["nav"]) if st.session_state["nav"] in nav_options else 0
    selected_nav = st.radio(
        "Navigation",
        nav_options,
        index=current_idx,
        label_visibility="collapsed"
    )
    st.session_state["nav"] = selected_nav

    st.markdown("---")
    st.caption("🔒 **System Architecture**")
    st.caption("• Lexical: BM25 Okapi")
    st.caption("• Dense Vector: BGE-small-en-v1.5")
    st.caption("• Fusion: Reciprocal Rank Fusion ($k=60$)")
    st.caption("• Verification: Factual Claim Grounding")
    st.caption("• Infrastructure Cost: **$0.00/mo**")

# Route to selected view
if selected_nav == "📊 Dashboard & Overview":
    render_dashboard()
elif selected_nav == "💼 Job Application Generator":
    render_job_application()
elif selected_nav == "📚 Knowledge Base Explorer":
    render_knowledge_base()
elif selected_nav == "📂 Generated Applications History":
    render_generated_applications()
elif selected_nav == "⚙️ Settings & Diagnostics":
    render_settings()
