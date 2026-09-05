---
project_name: "BitCheck — Multimodal AI Verification API"
short_description: "Multi-signal media forensics API inspecting uploaded images, audio, video frames, and text for AI generation, deepfakes, and digital tampering."
problem: "The proliferation of synthetic media and deepfakes makes it difficult to ascertain digital content authenticity, requiring multi-layered cryptographic and machine learning validation."
solution: "Engineered an asynchronous forensic API combining cryptographic metadata verification, OCR watermark analysis, digital noise profiling, and a deep learning vision classifier with explainability heatmaps."
architecture: "FastAPI asynchronous service orchestrating parallel forensic pipelines: EXIF/XMP chunk inspection, C2PA provenance toolchain, Tesseract OCR for synthetic watermarks, frequency-domain noise analysis, and PyTorch deep neural network inference."
technologies:
  - "PyTorch"
  - "FastAPI"
  - "OpenCV"
  - "Tesseract OCR"
  - "C2PA (c2patool)"
  - "Docker"
  - "Grad-CAM"
  - "Streamlit"
programming_languages:
  - "Python"
frameworks:
  - "PyTorch"
  - "FastAPI"
  - "OpenCV"
models:
  - "Custom PyTorch Classifier (140K images)"
  - "Grad-CAM Explainability"
databases: []
infrastructure:
  - "Docker"
  - "Hugging Face Spaces"
  - "Vercel"
exact_contribution: "Solely designed and implemented the entire Python backend, forensic pipelines, image classifier training and validation on 140,000 samples, Docker packaging, and Grad-CAM visual explainability."
responsibilities:
  - "Engineered a multi-signal forensic verification API analyzing images, audio, and text for AI generation and manipulation."
  - "Integrated metadata extraction, C2PA provenance credentials, OCR watermark scanning, noise forensics, and a custom PyTorch classifier trained on 140K images with Grad-CAM explainability."
  - "Containerized the service with Docker and deployed on Hugging Face Spaces with a Vercel web frontend."
results:
  - "Trained custom image classifier on 140,000 images (70,000 real, 70,000 synthetic)."
  - "Produced real-time visual heatmaps via Grad-CAM highlighting manipulated regions."
metrics:
  - "Trained on 140,000 images dataset (70K real / 70K synthetic)"
github_url: "https://github.com/Jaykay73/bitcheck"
live_demo_url: "https://bitcheckapp.vercel.app"
screenshots: []
challenges: "Balancing computational latency across multi-signal checks (cryptographic, optical, and deep learning) while preventing false positives on heavily compressed social media images."
technical_decisions: "Used asynchronous execution in FastAPI to run optical OCR and metadata checks concurrently with PyTorch tensor preprocessing; utilized Grad-CAM for transparent user-facing explainability."
lessons_learned: "Cryptographic provenance standards like C2PA are robust when present, but fallback deep learning heuristics are necessary when metadata is stripped."
deployment_information: "Docker container deployed on Hugging Face Spaces; frontend hosted on Vercel."
deployment_platform: "Hugging Face Spaces / Vercel"
relevant_domains:
  - "Computer Vision"
  - "Multimodal AI"
  - "Cybersecurity"
  - "Media Forensics"
relevant_job_titles:
  - "Machine Learning Engineer"
  - "Computer Vision Engineer"
  - "AI Engineer"
keywords:
  - "PyTorch"
  - "FastAPI"
  - "OpenCV"
  - "Grad-CAM"
  - "C2PA"
  - "Docker"
  - "Computer Vision"
dates: "2025 – 2026"
status: "completed"
---

# BitCheck — Multimodal AI Verification API
High-performance forensic verification service integrating cryptographic verification (C2PA), optical text extraction, and deep vision models with Grad-CAM explainability.
