# 🚀 Career AI Engine — Personal ATS Tailoring & Grounded Retrieval System

An evidence-grounded, zero-hallucination, ATS-compliant job application generation engine built for **John Aledare**.

Unlike generic chatbot wrappers or resume rewriters, this engine strictly grounds every claim, metric, and bullet point in a verified Markdown knowledge base using **hybrid retrieval (BM25 + Dense Vectors with Reciprocal Rank Fusion)**, enforce adversarial post-generation verification, and compiles publication-grade LaTeX resumes and cover letters.

---

## 🏛️ System Architecture

```
                 ┌────────────────────────────────────────┐
                 │  Canonical Knowledge Base (Markdown)   │
                 │  - 28 Authoritative Markdown Files     │
                 │  - YAML Frontmatter + Structured Chunks│
                 └───────────────────┬────────────────────┘
                                     │
                                     ▼
                ┌──────────────────────────────────────────┐
                │        Hybrid Indexing Pipeline          │
                │  ├── BM25 Okapi Lexical Index (Pickle)   │
                │  ├── BGE-small-en-v1.5 Dense Embeddings  │
                │  └── Embedded Qdrant Vector DB (On-Disk) │
                └────────────────────┬─────────────────────┘
                                     │
         ┌───────────────────────────┴───────────────────────────┐
         │                                                       │
         ▼                                                       ▼
┌──────────────────┐                                   ┌────────────────────┐
│ Job Description  │                                   │ Reciprocal Rank    │
│ Parser & Schema  │                                   │ Fusion (RRF, k=60) │
│ - Requirements   │ ───► Hybrid Retrieval ──────────► │ - Ranked Evidence  │
│ - Tech Stack     │      (BM25 + Qdrant Cosine)       │ - Supported vs     │
│ - Responsibilities                                   │   Unrepresented    │
└──────────────────┘                                   └─────────┬──────────┘
                                                                 │
                                                                 ▼
                                                       ┌────────────────────┐
                                                       │ Tailoring Engine   │
                                                       │ - Role Projection  │
                                                       │ - Dynamic Project  │
                                                       │   & Skill Selection│
                                                       └─────────┬──────────┘
                                                                 │
                                                                 ▼
                                                       ┌────────────────────┐
                                                       │ Adversarial Verifier│
                                                       │ - Metric Grounding │
                                                       │ - Degree Invariant │
                                                       │ - Cert Enforcement │
                                                       └─────────┬──────────┘
                                                                 │
                                                                 ▼
                                                       ┌────────────────────┐
                                                       │ LaTeX Subsystem    │
                                                       │ - Jinja2 ATS Engine│
                                                       │ - pdflatex Compiler│
                                                       │ - Output .tex/.pdf │
                                                       └────────────────────┘
```

---

## 🛡️ Inviolable Truth & Hallucination Defense Rules

This engine enforces strict cryptographic-like factual grounding to protect John Aledare's professional reputation:

1. 🎓 **Degree Integrity Invariant**:
   - Representation is strictly: **`Bachelor of Engineering (B.Eng.) in Computer Engineering` — `University of Ilorin` (2021 – 2026)**.
   - **Zero Tolerance**: Never outputs degree classifications, GPAs, or honours classifications (e.g. *Second Class*, *2:2*, *First Class*).
2. 📜 **Mandatory Certifications Invariant**:
   - All three verified certifications are permanently included on every generated CV:
     - **Oracle Cloud Infrastructure 2024 Generative AI Certified Professional** (Oracle, 2024)
     - **Oracle Cloud Infrastructure 2024 AI Foundations Associate** (Oracle, 2024)
     - **Machine Learning Specialization** (Stanford University & DeepLearning.AI, 2024)
3. 🚫 **Anti-Scoring Truth Principle**:
   - We **never** invent or compute fake match percentages (e.g. *"87% match"*).
   - Requirements are strictly categorized as `SUPPORTED` (backed by retrieved chunks) or `NOT_SUPPORTED_IN_KNOWLEDGE_BASE` (*"Not represented in current knowledge base"*).
4. 🔬 **Zero Metric Fabrication**:
   - Bullets follow `ACTION + TECHNICAL METHOD + PURPOSE + RESULT`.
   - Numerical results (e.g. *96.2% ROC-AUC*, *40% latency reduction*) are only included if explicitly verified in the Markdown knowledge base.

---

## 💰 Zero-Cost Infrastructure Blueprint ($0.00/Month)

The entire application runs **100% locally** on consumer hardware with zero recurring monthly cloud fees:

| Component | Technology | Cost | Deployment |
| :--- | :--- | :--- | :--- |
| **Embeddings** | `BAAI/bge-small-en-v1.5` (384-dim) | **$0.00** | Local CPU via PyTorch / SentenceTransformers |
| **Vector DB** | Qdrant (Embedded mode) | **$0.00** | Local disk storage in `data/qdrant_db/` |
| **Lexical Search** | BM25 Okapi (`rank_bm25`) | **$0.00** | In-memory with binary serialization in `data/` |
| **Relational DB** | SQLite (`career_ai.db`) | **$0.00** | Local ACID storage in `data/career_ai.db` |
| **LLM (Optional)** | DeepSeek V3 / R1 via OpenAI API | **Pay-per-use** or **$0.00** | Pluggable API or deterministic offline heuristic fallback |
| **LaTeX Subsystem** | MiKTeX / TeX Live / Overleaf | **$0.00** | Local subprocess or free web compilation |

---

## ⚡ Quickstart Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.11 Windows 64-bit)
- Git

### 2. Installation
```powershell
# Clone or open the repository
cd c:\Users\Admin\Desktop\Job

# Create and activate virtual environment (optional if using global)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy `.env.example` to `.env`:
```powershell
cp .env.example .env
```
Key configuration settings in `.env`:
```ini
# DeepSeek API (Optional - engine falls back to deterministic heuristic mode if empty)
DEEPSEEK_API_KEY=
LLM_PROVIDER=deepseek
LLM_MODEL=deepseek-chat
LLM_BASE_URL=https://api.deepseek.com/v1

# Hybrid Retrieval & RRF
RRF_K=60
BM25_TOP_K=20
VECTOR_TOP_K=20
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5

# Storage
DATA_DIR=data
OUTPUT_DIR=output
KNOWLEDGE_DIR=knowledge
```

### 4. Build the Hybrid Index
Scan and index all 28+ canonical knowledge records:
```powershell
python scripts/rebuild_index.py
```

### 5. Launch the Streamlit Web Application
```powershell
streamlit run career_ai/app/streamlit_app.py
```
Open your browser at `http://localhost:8501`.

---

## 🖥️ Streamlit Multi-Page UI Features

1. **📊 Dashboard & Overview**:
   - Live knowledge base record counts across 6 categories (Education, Experience, Projects, Certifications, Skills, Publications).
   - Total indexed chunks count and vector dimension.
   - Status indicators for Qdrant, BM25, SQLite, and LaTeX compilation.
   - Active Inviolable Truth Rules summary.

2. **💼 Job Application Generator**:
   - One-click sample job description loader.
   - Input fields for Job Title, Company Name, and Job Description.
   - **Step 1: Analyze & Match Evidence**:
     - Extracts requirements and splits them into `🟢 Supported in Knowledge Base` and `🟡 Not Represented in Knowledge Base`.
     - Displays retrieved evidence chunks, similarity scores, and RRF rankings.
   - **Step 2: Generate Verified Application**:
     - Executes adversarial claim verification.
     - Provides ready-to-use `.tex` download button and compiled `.pdf` download button.
     - Displays formatted Cover Letter and complete Evidence Traceability Matrix.

3. **📚 Knowledge Base Explorer**:
   - Filter and search John's canonical markdown files by keyword or technology.
   - Expand cards to view verified metrics, dates, and bullet points.
   - **Add New Record**: GUI form to create a new markdown file and automatically reindex the database.
   - **Profile Improvement Assistant**: Suggests strategic skills and projects to pursue based on industry demand.

4. **📂 Generated Applications History**:
   - Browse all past tailored applications stored in SQLite.
   - Download past resumes (`.tex`), cover letters, and inspect audit metadata.

5. **⚙️ Settings & Diagnostics**:
   - Inspect LLM parameters, RRF $k$, and system paths.
   - Check local LaTeX compiler status and instructions.

---

## 📄 LaTeX & PDF Compilation

The engine generates clean, ATS-optimized LaTeX source files based on the battle-tested Jake Gutierrez resume template.

### Compiling on Windows:
If `pdflatex` is installed on your Windows PATH, the engine will automatically compile `.pdf` files into `output/<Company>/<Role>/`.

If `pdflatex` is not yet installed:
1. **Free Cloud Option**: Download the `.tex` file from the Streamlit UI or `output/` folder and paste it into [Overleaf](https://www.overleaf.com). It compiles in 1 second.
2. **Local Windows Installation**:
   ```powershell
   winget install MiKTeX.MiKTeX
   # Or via Chocolatey:
   # choco install miktex
   ```
   After installing, restart your terminal, and PDF compilation will automatically activate.

---

## 🧪 Automated Test Suite

Run the full automated test suite covering parsing, BM25, RRF math, factual verifier invariants, LaTeX rendering, and end-to-end pipeline:

```powershell
pytest -v
```

Test coverage includes:
- `tests/test_parser.py`: Markdown and YAML frontmatter parsing.
- `tests/test_bm25.py`: Lexical tokenization, stopword handling, and score ranking.
- `tests/test_rrf.py`: Deterministic mathematical proof of the Reciprocal Rank Fusion formula ($RRF(d) = \sum \frac{1}{k + rank_i(d)}$).
- `tests/test_verifier.py`: Adversarial verification rejecting degree classifications, missing certifications, and fabricated metrics.
- `tests/test_latex.py`: Jinja2 template rendering and LaTeX character escaping.
- `tests/test_end_to_end.py`: Complete ApplicationService workflow from JD to `.tex`.

---

## 🔮 Future Architecture Blueprint: Decoupled FastAPI + React

The core engine is built with clean architectural decoupling:
- `career_ai/services/application_service.py` is completely independent of Streamlit.
- It can be wrapped in a FastAPI backend with zero changes to business logic:

```python
# Blueprint for FastAPI router
from fastapi import FastAPI, HTTPException
from career_ai.services.application_service import application_service

api = FastAPI(title="Career AI API")

@api.get("/api/knowledge/summary")
def get_summary():
    return application_service.get_knowledge_summary()

@api.post("/api/jobs/analyze")
def analyze_job(payload: JobAnalysisRequest):
    return application_service.analyze_job_posting(payload.jd_text, payload.company, payload.title)

@api.post("/api/applications/generate")
def generate_app(payload: JobGenerationRequest):
    analysis = application_service.analyze_job_posting(payload.jd_text, payload.company, payload.title)
    return application_service.generate_tailored_application(analysis, payload.jd_text)
```

A modern React/Next.js frontend can connect to these endpoints for production multi-user deployments.

---

## 👤 Candidate Profile

**John Oluwaseun Aledare**  
- **Role**: AI Engineer / Machine Learning Engineer
- **Education**: Bachelor of Engineering (B.Eng.) in Computer Engineering — University of Ilorin (2021 – 2026)
- **Certifications**:
  - Oracle Cloud Infrastructure 2024 Generative AI Certified Professional (Oracle, 2024)
  - Oracle Cloud Infrastructure 2024 AI Foundations Associate (Oracle, 2024)
  - Machine Learning Specialization (Stanford University & DeepLearning.AI, 2024)
- **Portfolio**: [aledare.vercel.app](https://aledare.vercel.app)
- **GitHub**: [github.com/Jaykay73](https://github.com/Jaykay73)
- **LinkedIn**: [linkedin.com/in/johnaledare](https://linkedin.com/in/johnaledare)
