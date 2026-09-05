---
project_name: "Nigerian Pidgin Next-Word Predictor"
short_description: "Dual-model real-time language modeling system predicting next words in Nigerian Pidgin English, balancing deep neural network accuracy and statistical n-gram speed."
problem: "Low-resource languages such as Nigerian Pidgin lack robust commercial language models and real-time typing assistive tools."
solution: "Trained a deep LSTM recurrent neural network alongside a Trigram statistical model with keystroke debouncing for real-time inference over an interactive UI."
architecture: "PyTorch LSTM model for deep contextual modeling combined with a Trigram lookup model for microsecond fallback; FastAPI API and Streamlit UI with debounce handlers."
technologies:
  - "PyTorch"
  - "LSTM"
  - "Trigram Statistical Models"
  - "FastAPI"
  - "Streamlit"
  - "Docker"
programming_languages:
  - "Python"
frameworks:
  - "PyTorch"
  - "FastAPI"
  - "Streamlit"
models:
  - "Custom PyTorch LSTM"
  - "Trigram Statistical Model"
databases: []
infrastructure:
  - "Hugging Face Spaces"
  - "Streamlit Cloud"
exact_contribution: "Collected and preprocessed text corpora, trained LSTM and Trigram models in PyTorch, built the FastAPI endpoint, and deployed interactive Streamlit frontend."
responsibilities:
  - "Designed a dual-model real-time next-word predictor for Nigerian Pidgin English balancing deep LSTM accuracy and Trigram speed."
  - "Deployed model backend on Hugging Face Spaces with keystroke debouncing on Streamlit UI."
results:
  - "Delivered responsive typing predictions without lagging the UI."
metrics: []
github_url: "https://github.com/Jaykay73/nextword-pidgin"
live_demo_url: "https://nextword-pidgin.streamlit.app"
screenshots: []
challenges: "Irregular orthography, slang variations, and limited standardized text data in Nigerian Pidgin."
technical_decisions: "Combined neural sequence modeling with fast n-gram lookups to ensure immediate suggestions during rapid typing."
lessons_learned: "Data cleaning and tokenization strategies heavily dominate performance in low-resource NLP tasks."
deployment_information: "Backend on Hugging Face Spaces, frontend on Streamlit Cloud."
deployment_platform: "Hugging Face Spaces / Streamlit Cloud"
relevant_domains:
  - "NLP"
  - "Low-Resource Language Modeling"
  - "Sequence Modeling"
relevant_job_titles:
  - "NLP Engineer"
  - "Machine Learning Engineer"
keywords:
  - "PyTorch"
  - "LSTM"
  - "NLP"
  - "Language Modeling"
  - "FastAPI"
  - "Streamlit"
dates: "2025"
status: "completed"
---

# Nigerian Pidgin Next-Word Predictor
Real-time sequence modeling and low-resource language prediction engine combining PyTorch LSTMs and statistical Trigrams.
