---
project_name: "Legal Document Analyzer"
short_description: "Contract analysis tool using Retrieval-Augmented Generation (RAG) to parse legal clauses, identify obligations, and score liabilities."
problem: "Reviewing lengthy commercial contracts for hidden liability clauses and indemnity risks is labor-intensive and error-prone."
solution: "Built a RAG system extracting clauses from PDF contracts, computing dense embeddings with SentenceTransformers, and ranking liabilities using cosine similarity."
architecture: "PyPDF text extractor, recursive clause chunker, SentenceTransformers embedding model, cosine similarity vector search, and Streamlit legal dashboard."
technologies:
  - "SentenceTransformers"
  - "PyPDF"
  - "Streamlit"
  - "Cosine Similarity Ranking"
  - "Python"
programming_languages:
  - "Python"
frameworks:
  - "SentenceTransformers"
  - "Streamlit"
models:
  - "Dense Sentence Transformers Embeddings"
databases: []
infrastructure:
  - "Streamlit Cloud"
exact_contribution: "Engineered legal clause chunking, dense vector scoring, and interactive UI for clause exploration."
responsibilities:
  - "Contract analysis tool using RAG to parse clauses, identify obligations, and score legal liabilities using dense chunk embeddings."
results:
  - "Automated extraction and risk categorization of clauses across multi-page agreements."
metrics: []
github_url: "https://github.com/Jaykay73/Legal-Document-Analyser"
live_demo_url: ""
screenshots: []
challenges: "Dense legalese syntax and maintaining context boundaries across multi-paragraph indemnification clauses."
technical_decisions: "Used section-aware clause splitting rather than fixed-token windowing to preserve complete obligations."
lessons_learned: "Semantic chunking based on document structure dramatically reduces retrieval noise in specialized domains like law."
deployment_information: "Streamlit Cloud."
deployment_platform: "Streamlit Cloud"
relevant_domains:
  - "NLP"
  - "RAG"
  - "LegalTech"
  - "Document Analysis"
relevant_job_titles:
  - "AI Engineer"
  - "NLP Engineer"
  - "Machine Learning Engineer"
keywords:
  - "RAG"
  - "SentenceTransformers"
  - "Vector Search"
  - "Legal NLP"
  - "Cosine Similarity"
dates: "2025"
status: "completed"
---

# Legal Document Analyzer
Retrieval-Augmented Generation (RAG) tool analyzing contract clauses and ranking liabilities with dense embeddings.
