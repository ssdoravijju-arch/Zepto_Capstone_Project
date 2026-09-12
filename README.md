# Zepto Data & AI Platform — Capstone Project

## Certificate Program in Artificial Intelligence and Machine Learning

This repository contains the complete Zepto Data & AI Platform Capstone Project.  
The project is organized into three modules:

1. Data Pipeline
2. Analytics and Machine Learning
3. AI Support Assistant

## Repository Structure

Zepto_Capstone_Project/
├── data_pipeline/
├── analytics/
├── support_assistant/
├── titanic.csv
└── README.md

---

## Module 1 — Data Pipeline

The `data_pipeline` module implements the data engineering component of the project.

### Main Design
- Data ingestion and transformation pipeline
- SQLite-based structured storage
- Modular and reproducible implementation
- Data validation and processing
- Documentation for running the pipeline

### Run
Refer to the README inside the `data_pipeline/` directory for module-specific instructions.

---

## Module 2 — Analytics and Machine Learning

The `analytics` module contains the exploratory data analysis and machine-learning workflow.

### Main Design
- Exploratory Data Analysis (EDA)
- Data cleaning and preprocessing
- Classification modelling
- Class-imbalance comparison
- Random Forest tuning
- Regression modelling
- Model evaluation and comparison
- Saved deployment-ready pipeline

The Titanic dataset is used for the analytics workflow, with support for a local `titanic.csv` fallback.

### Run
Open and execute the notebooks/files available inside the `analytics/` directory in the documented order.

---

## Module 3 — Support Assistant

The `support_assistant` module implements an AI-powered policy support assistant using retrieval and routing.

### Architecture

Ingestion → Embedding → Retrieval → Generation

### Main Design
- Policy documents stored under `docs/`
- Sentence Transformer embeddings
- ChromaDB vector storage and retrieval
- LangGraph-based intent routing
- Policy questions routed through retrieval
- General questions handled separately
- Structured response validation
- FastAPI `/ask` endpoint
- Docker support

### Run

```bash
cd support_assistant
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 7860

curl -X POST http://127.0.0.1:7860/ask \
-H "Content-Type: application/json" \
-d '{"query":"What is the delivery fee for a small order?"}'
