# Changelog

All notable changes to Career AI Engine will be documented in this file.

## [1.2.0] - 2026-10-11

### Added
- **Streamlit Cloud Ready Entrypoint**: Added root `streamlit_app.py` wrapper enabling automatic, zero-configuration discovery on Streamlit Community Cloud.
- **Streamlit Configuration & Secrets**: Added `.streamlit/config.toml` (modern enterprise theme, headless server mode) and `.streamlit/secrets.toml.example` template.
- **Cloud Secrets Auto-Detection**: Integrated `st.secrets` detection into Pydantic `Settings` to automatically load `DEEPSEEK_API_KEY` when running on Streamlit Cloud.
- **Streamlit Debian Dependencies (`packages.txt`)**: Added `texlive-latex-base` and recommended font packages for automated cloud LaTeX PDF compilation.
- **SupplyPilot Canonical Project Knowledge**: Ingested complete canonical documentation for **SupplyPilot** (`knowledge/projects/supply-pilot.md` and `SUPPLY_PILOT_PROJECT_DOCUMENTATION.md`), highlighting LangGraph multi-step reasoning, SOP RAG, Jev risk scoring, and deterministic invariant supremacy.
- **Domain Taxonomy Expansion**: Added `Agentic AI & Decision Support` and `Operations Research & Supply Chain Systems` to `CANONICAL_DOMAINS`.
- **Automated Test Suite**: Added `tests/test_supply_pilot.py` testing schema compliance, agentic tokenization, metric verification, and Streamlit environment health.

### Changed
- **Dependencies (`requirements.txt`)**: Pinned `pandas>=2.0.0` and `numpy>=1.24.0` ensuring seamless installation on Streamlit Cloud without missing package errors.
- **BM25 Lexical Retrieval**: Added domain synonym expansions for `langgraph`, `sop`, `cfr`, `hitl`, and `supplypilot` to maximize lexical recall on operations research roles.
- **Factual Claim Verifier**: Expanded metric validation regex to verify monetary amounts (e.g. `$50,000` sign-off threshold) and multi-stage simulation counts (e.g. `5-stage` cascade).
- **Evidence Selector**: Registered `supply-pilot` in preferred showcase projects with automatic boosting for agentic AI and operations job descriptions.
- **Application Service Entities**: Added `supply-pilot` and `autonomous-lawn-mower` to `CANONICAL_ENTITIES` dictionary.
- **Configuration Compatibility**: Added property aliases (`llm_base_url`, `llm_model`, `bm25_top_k`, `vector_top_k`, `qdrant_path`) to ensure 100% crash-free navigation in Streamlit diagnostics.

## [1.1.0] - 2026-09-28

### Added
- **Autonomous Intelligent Lawn Mower Canonical Record**: Ingested complete 988-line engineering specification for the autonomous robotic lawn mower project (`knowledge/projects/autonomous-lawn-mower.md`).
- **Cyber-Physical & Robotics Skills Taxonomy**: Added embedded systems, microcontroller interfacing, IMU sensor fusion, and edge AI hardware categories to `knowledge/skills/technical-skills.md` and master `knowledge_base.md`.
- **Domain Taxonomy Schemas**: Expanded `JobRequirements` and `ProjectSchema` to explicitly recognize `Autonomous Robotics`, `Cyber-Physical Systems`, and `Edge AI / Embedded Systems`.
- **CLI Operational Tooling**: Implemented `career_ai.cli` with subcommands (`stats`, `query`, `verify-robotics`) and standalone `scripts/sync_knowledge.py` for automated inventory verification and search store synchronization.
- **Master LaTeX Resume**: Added `Aledare-John-AI-Engineer-Updated.tex` reflecting John's latest engineering profile, medical ML projects, and Medium publications.
- **Automated Unit Tests**: Added `tests/test_robotics_parser.py` and `tests/test_robotics_retrieval.py` testing schema compliance, section extraction, and hybrid ranking.

### Changed
- **BM25 Lexical Retrieval**: Enhanced tokenizer with technical compound word support (`re.compile(r"[a-zA-Z0-9]+(?:[-_][a-zA-Z0-9]+)*|c\+\+|[a-zA-Z0-9]+")`) and added metadata keyword/technology token inclusion for superior precision on hardware acronyms.
- **Factual Claim Verifier**: Expanded metric validation regex and normalized whitespace/hyphens to verify cyber-physical tolerances (e.g. `500 ms` watchdog heartbeat, `4–5 kg` payload, `12V` DC motors) without false hallucination alerts.
- **Role-Aligned Experience Selector**: Added keyword relevance boost for robotics, embedded, and IoT roles, surfacing cyber-physical projects for matching hardware job descriptions.
- **Jinja2 LaTeX Templates**: Updated `templates/master_resume.tex` and `TailoredProject` schemas to render verified Live Demo and GitHub repository links in project headings.
- **Documentation**: Updated `README.md` with complete architectural blueprints, 33 canonical records, and CLI instructions.

---

## [1.0.0] - 2026-09-05

### Added
- Initial release of Career AI Engine.
- Hybrid BM25 Okapi and dense vector search (BGE-small-en-v1.5 + embedded Qdrant) with Reciprocal Rank Fusion ($k=60$).
- Adversarial factual claim verifier with inviolable truth invariants (degree privacy, mandatory certifications, zero metric fabrication).
- Multi-page Streamlit web application with real-time AI refinement chatbox and interactive application dashboard.
- Jinja2 LaTeX templating and safe pdflatex subprocess compilation engine.
