---
project_name: "Diabetic Retinopathy Classifier"
short_description: "Automated grading and classification of retina fundus scans for diabetic retinopathy stages with Grad-CAM visual heatmaps."
problem: "Diabetic retinopathy is a leading cause of preventable blindness; scalable screening requires interpretable AI tools that clinicians can audit."
solution: "Built a PyTorch deep learning pipeline utilizing EfficientNet-B0 transfer learning and Grad-CAM visual interpretability to highlight clinical lesions and hemorrhages."
architecture: "PyTorch deep convolutional network with Grad-CAM visualization hooks, custom fundus image preprocessing (circular cropping, Ben Graham's method), and Streamlit web dashboard."
technologies:
  - "PyTorch"
  - "EfficientNet-B0"
  - "Grad-CAM"
  - "Streamlit"
  - "OpenCV"
  - "Python"
programming_languages:
  - "Python"
frameworks:
  - "PyTorch"
  - "OpenCV"
  - "Streamlit"
models:
  - "EfficientNet-B0"
  - "Grad-CAM Heatmaps"
databases: []
infrastructure:
  - "Streamlit Cloud"
exact_contribution: "Implemented image preprocessing pipeline, trained PyTorch classifier, integrated Grad-CAM gradient calculation for visual interpretability, and built interactive demo."
responsibilities:
  - "Automated grading and classification of retina fundus scans for diabetic retinopathy stages."
  - "Includes Grad-CAM visual heatmaps for clinical interpretability and decision verification."
results:
  - "Accurately visualized high-gradient lesion zones using Grad-CAM heatmaps."
metrics: []
github_url: "https://github.com/Jaykay73/Diabetes"
live_demo_url: "https://diabetic-retinopathy-m.streamlit.app"
screenshots: []
challenges: "Subtle microaneurysms and color balance variations across different retinal camera models."
technical_decisions: "Applied Ben Graham's color normalization to standardize lighting across disparate fundus captures."
lessons_learned: "Explainability is essential in medical AI to allow practitioners to verify model attention against genuine pathologies."
deployment_information: "Streamlit Cloud application."
deployment_platform: "Streamlit Cloud"
relevant_domains:
  - "Computer Vision"
  - "Healthcare AI"
  - "Explainable AI (XAI)"
relevant_job_titles:
  - "Computer Vision Engineer"
  - "Machine Learning Engineer"
keywords:
  - "PyTorch"
  - "Grad-CAM"
  - "Computer Vision"
  - "EfficientNet"
  - "Explainable AI"
dates: "2025"
status: "completed"
---

# Diabetic Retinopathy Classifier
Explainable medical vision system for diabetic retinopathy detection featuring Grad-CAM attention heatmaps and PyTorch.
