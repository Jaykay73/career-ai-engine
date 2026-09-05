---
project_name: "Brain Tumor MRI Classifier"
short_description: "Deep learning medical vision classifier distinguishing Glioma, Meningioma, Pituitary tumors, and Healthy scans with mobile edge quantization."
problem: "Early brain tumor screening requires fast, accessible radiological triage tools in clinical settings."
solution: "Trained an EfficientNetB0 convolutional neural network via transfer learning with medical data augmentations and INT8 quantization for edge inference."
architecture: "TensorFlow/Keras EfficientNetB0 pipeline, transfer learning on MRI slices, post-training quantization, and Streamlit diagnostic web app."
technologies:
  - "TensorFlow"
  - "Keras"
  - "EfficientNet-B0"
  - "Transfer Learning"
  - "Model Quantization"
  - "Streamlit"
  - "Python"
programming_languages:
  - "Python"
frameworks:
  - "TensorFlow"
  - "Keras"
  - "Streamlit"
models:
  - "EfficientNet-B0 (Transfer Learning)"
databases: []
infrastructure:
  - "Streamlit Cloud"
exact_contribution: "Trained multi-class transfer learning model on MRI dataset, evaluated confusion matrix, applied quantization for low-latency inference, and deployed Streamlit app."
responsibilities:
  - "Trained deep learning medical vision classifiers using transfer learning with Grad-CAM visual heatmaps for clinical interpretability."
  - "Applied model quantization for edge deployment on mobile applications and interactive Streamlit web apps."
results:
  - "Successfully classified four diagnostic classes (Glioma, Meningioma, Pituitary, Normal)."
  - "Reduced model parameter size for edge deployment via quantization."
metrics: []
github_url: "https://github.com/Jaykay73/MRI-Scan"
live_demo_url: "https://mri-scan.streamlit.app"
screenshots: []
challenges: "Preventing overfitting on high-dimensional radiological scans and handling class imbalance."
technical_decisions: "Utilized EfficientNetB0 compound scaling architecture to achieve high validation accuracy while keeping compute lightweight."
lessons_learned: "Careful data normalization and augmentation are critical when working with sensitive clinical imaging."
deployment_information: "Streamlit Cloud deployment."
deployment_platform: "Streamlit Cloud"
relevant_domains:
  - "Medical Imaging"
  - "Computer Vision"
  - "Deep Learning"
  - "Healthcare AI"
relevant_job_titles:
  - "Computer Vision Engineer"
  - "Machine Learning Engineer"
keywords:
  - "TensorFlow"
  - "EfficientNet"
  - "Computer Vision"
  - "Medical Imaging"
  - "Quantization"
dates: "2025"
status: "completed"
---

# Brain Tumor MRI Classifier
Deep learning medical vision classifier utilizing EfficientNetB0 transfer learning and INT8 quantization for brain tumor detection.
