---
project_name: "CineMatch API — Vector Movie Recommendation Engine"
short_description: "Content-based semantic movie search and vibe-based discovery using dense vector embeddings and FAISS similarity search."
problem: "Traditional keyword search fails to capture nuanced narrative themes, mood, and semantic context in movie descriptions."
solution: "Generated 384-dimensional dense vector embeddings of movie plots using SentenceTransformers, indexed in FAISS for sub-100ms similarity retrieval."
architecture: "FastAPI endpoint with FAISS vector index, SentenceTransformers (all-MiniLM-L6-v2), Pandas data pipelines, and TMDB API synchronization."
technologies:
  - "FastAPI"
  - "FAISS"
  - "SentenceTransformers (all-MiniLM-L6-v2)"
  - "Pandas"
  - "TMDB API"
  - "Python"
programming_languages:
  - "Python"
frameworks:
  - "FastAPI"
  - "FAISS"
  - "SentenceTransformers"
models:
  - "all-MiniLM-L6-v2 (384-dim dense embeddings)"
databases:
  - "FAISS Index"
infrastructure:
  - "Vercel"
exact_contribution: "Implemented embedding generation pipeline, FAISS vector index creation and tuning, and FastAPI endpoint for low-latency similarity queries."
responsibilities:
  - "Developed a semantic movie recommendation engine using MiniLM dense embeddings and FAISS vector similarity for sub-100ms retrieval."
results:
  - "Delivered sub-100ms vector similarity query responses."
  - "Enabled vibe-based semantic queries beyond simple title/actor keyword searches."
metrics:
  - "Sub-100ms similarity retrieval latency"
  - "384-dimensional vector embeddings"
github_url: "https://github.com/Jaykay73/CineMatch"
live_demo_url: "https://aether-match.vercel.app"
screenshots: []
challenges: "Handling memory overhead and real-time query vectorization under low-compute server constraints."
technical_decisions: "Selected all-MiniLM-L6-v2 for its strong balance of semantic fidelity and embedding speed."
lessons_learned: "Vector normalisation is crucial for fast inner product (IP) to match cosine similarity."
deployment_information: "Vercel backend/frontend deployment."
deployment_platform: "Vercel"
relevant_domains:
  - "Recommendation Systems"
  - "Vector Search"
  - "Information Retrieval"
  - "NLP"
relevant_job_titles:
  - "Machine Learning Engineer"
  - "Search / Retrieval Engineer"
  - "Data Scientist"
keywords:
  - "FAISS"
  - "SentenceTransformers"
  - "Vector Search"
  - "Embeddings"
  - "Cosine Similarity"
  - "FastAPI"
dates: "2025"
status: "completed"
---

# CineMatch API — Vector Movie Recommendation Engine
Semantic recommendation engine utilizing SentenceTransformers embeddings and FAISS vector similarity search for sub-100ms retrieval.
