---
project_name: "LockedIn AI Service — Intelligent Roadmap Generator"
short_description: "Autonomous AI engine generating structured, beginner-to-advanced learning roadmaps by fetching live candidates from search APIs and synthesizing curricula via LLMs."
problem: "Self-directed learners struggle with outdated, fragmented, paywalled, or duplicate tutorials across the web."
solution: "Built a service that queries Tavily and YouTube APIs for live educational resources, filters broken/paywalled links, and synthesizes structured learning stages validated by Pydantic schemas."
architecture: "FastAPI service with Tavily API and YouTube Search API integration, DeepSeek LLM structured synthesis, Pydantic v2 JSON schema validation, and SQLite caching layer."
technologies:
  - "FastAPI"
  - "DeepSeek LLM"
  - "Tavily API"
  - "YouTube Search API"
  - "SQLite"
  - "Pydantic v2"
  - "Python"
programming_languages:
  - "Python"
frameworks:
  - "FastAPI"
  - "Pydantic v2"
models:
  - "DeepSeek LLM"
databases:
  - "SQLite"
infrastructure:
  - "Hugging Face Spaces"
  - "Vercel"
exact_contribution: "Designed and implemented the core roadmap generation logic, resource retrieval and deduplication pipeline, LLM prompt engineering, and SQLite caching layer."
responsibilities:
  - "Developed an automated learning roadmap generator fetching live candidates via Tavily/YouTube and filtering paywalls/duplicates."
  - "Synthesized structured curriculum paths via DeepSeek LLM, validated with Pydantic v2 schemas and cached in SQLite."
results:
  - "Reliable structured JSON output with zero schema violations."
  - "Substantially reduced duplicate resources through heuristic filtering."
metrics: []
github_url: "https://github.com/Jaykay73/LockedIn"
live_demo_url: "https://lockedin4l.vercel.app"
screenshots: []
challenges: "Handling rate limits from search APIs and ensuring the LLM returns strict JSON matching complex nested roadmap models without hallucinations."
technical_decisions: "Adopted Pydantic v2 for high-speed serialization/deserialization and validation; used SQLite caching to eliminate duplicate API search calls for repeated queries."
lessons_learned: "Strict JSON schema enforcement prevents downstream UI parsing crashes when interacting with LLMs."
deployment_information: "FastAPI backend on Hugging Face Spaces; Next.js frontend on Vercel."
deployment_platform: "Hugging Face Spaces / Vercel"
relevant_domains:
  - "Autonomous AI Agents"
  - "LLM Engineering"
  - "EdTech"
  - "API Orchestration"
relevant_job_titles:
  - "AI Engineer"
  - "LLM Engineer"
  - "Backend Engineer"
keywords:
  - "DeepSeek"
  - "FastAPI"
  - "Pydantic"
  - "SQLite"
  - "Tavily"
  - "API Orchestration"
dates: "2025"
status: "completed"
---

# LockedIn AI Service — Intelligent Roadmap Generator
Curriculum generation service using web search APIs, DeepSeek structured generation, and SQLite caching.
