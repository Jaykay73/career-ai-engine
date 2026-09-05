---
project_name: "AI Resume Optimizer & Career Architect"
short_description: "Automated career coach parsing resumes against job descriptions to identify skill gaps and synthesize tailored application assets."
problem: "Job seekers fail to align their existing verified competencies with employer requirements, causing ATS rejection."
solution: "Built a parsing and alignment engine that extracts entities from resumes, compares them against target job descriptions, and uses LLMs to synthesize targeted feedback and cover letters."
architecture: "FastAPI backend running quantized ONNX models for local Named Entity Recognition (NER), Google Gemini 2.0 Flash for text synthesis, and Next.js frontend."
technologies:
  - "Google Gemini 2.0 Flash"
  - "ONNX"
  - "FastAPI"
  - "Next.js"
  - "Docker"
  - "Python"
programming_languages:
  - "Python"
  - "TypeScript"
frameworks:
  - "FastAPI"
  - "Next.js"
models:
  - "ONNX Quantized NER Model"
  - "Gemini 2.0 Flash"
databases: []
infrastructure:
  - "Docker"
  - "Vercel"
exact_contribution: "Architected the backend parsing pipeline, optimized the local NER model with ONNX quantization, and integrated LLM synthesis for tailored cover letters."
responsibilities:
  - "Built an automated career coach parsing resumes with 95% accuracy to identify skill gaps against target job descriptions."
  - "Integrated Gemini 2.0 Flash for tailored cover letter generation and used ONNX quantization for low-latency NER inference."
results:
  - "Achieved 95% resume parsing accuracy on test resumes."
  - "Accelerated token inference using ONNX quantization."
metrics:
  - "95% resume parsing accuracy"
github_url: "https://github.com/Jaykay73/resume-optimizer"
live_demo_url: "https://aicareerarchitect.vercel.app"
screenshots: []
challenges: "Low-latency parsing of diverse PDF layouts and preventing LLM hallucination during cover letter tailoring."
technical_decisions: "Used ONNX model quantization to run local entity extraction with low memory footprint and minimal latency."
lessons_learned: "Local edge models combined with cloud LLMs offer an optimal balance between latency and reasoning power."
deployment_information: "FastAPI Docker container on cloud platform; Next.js frontend on Vercel."
deployment_platform: "Docker / Vercel"
relevant_domains:
  - "NLP"
  - "Career Tech"
  - "Model Quantization"
relevant_job_titles:
  - "Machine Learning Engineer"
  - "AI Engineer"
keywords:
  - "ONNX"
  - "Gemini"
  - "FastAPI"
  - "NLP"
  - "NER"
  - "Quantization"
dates: "2025"
status: "completed"
---

# AI Resume Optimizer & Career Architect
Career tech engine parsing candidate resumes with 95% accuracy, identifying skill gaps, and generating tailored cover letters with Gemini and quantized ONNX models.
