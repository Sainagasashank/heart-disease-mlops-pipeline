# Video Recording Guide & Walkthrough Script
**Course:** AIMLCZG523 - Machine Learning Operations (MLOps) | BITS Pilani  
**Assignment:** Assignment 01  
**Duration:** 3 - 5 Minutes

---

## Video Outline & Timecodes

| Timecode | Section | Visual Focus on Screen | Narration Script Summary |
| :---: | :--- | :--- | :--- |
| **0:00 - 0:45** | **Introduction & Architecture** | Open VS Code / IDE showing project file tree and `README.md` with Mermaid diagram. | *"Hello Professor and evaluators. Today I am presenting my end-to-end MLOps pipeline for heart disease risk prediction on the UCI Cleveland dataset for Assignment 1. Our architecture covers data ingestion, Scikit-learn pipelines, MLflow experiment tracking, Pytest quality gates, GitHub Actions CI/CD, FastAPI containerization, Kubernetes manifests, and Prometheus/Grafana monitoring."* |
| **0:45 - 1:30** | **Data Preprocessing & EDA** | Open `data/processed/heart_disease_cleaned.csv` and show plots in `reports/figures/`. | *"In Task 1, we automated data acquisition with local fallback and resolved the 6 missing values in attributes ca and thal, binarizing the target into absence versus presence. Our EDA plots show a well-balanced distribution with 164 healthy cases and 139 disease cases, and clear diagnostic separation on maximum heart rate and exercise ST depression."* |
| **1:30 - 2:30** | **Model Training & MLflow Tracking** | Run `python -m src.train` in terminal, then show MLflow UI at `http://localhost:5000`. | *"For Tasks 2, 3, and 4, we built an end-to-end ColumnTransformer pipeline with median and mode imputation, standard scaling, and one-hot encoding to eliminate train-serving skew. We benchmarked Logistic Regression, Random Forest, and Gradient Boosting under Stratified 5-Fold Cross-Validation. Logistic Regression achieved 88.52% test accuracy and 0.9665 ROC-AUC. Here in the MLflow UI, all parameters, metrics, confusion matrices, ROC curves, and model artifacts are systematically tracked."* |
| **2:30 - 3:30** | **Automated Testing & CI/CD** | Run `python -m pytest tests/ -v`, then show `.github/workflows/ci.yml`. | *"In Task 5, we enforced a 12-test automated Pytest suite covering data integrity, model inference bounds, an 80% accuracy benchmark gate, and API contracts. All 12 tests pass cleanly. Our GitHub Actions workflow automates linting, test execution, model training verification, and container smoke testing on every push."* |
| **3:30 - 4:15** | **FastAPI Container & Docker Serving** | Run `python scripts/test_serving.py` and show FastAPI Swagger UI at `http://localhost:8000/docs`. | *"In Task 6, we wrapped our model in an asynchronous FastAPI microservice with strict Pydantic schemas, running in a hardened non-root python:3.11-slim Docker container. As demonstrated by running test_serving.py, GET /health returns 200 OK, and POST /predict accepts raw patient attributes and outputs risk classification with confidence scores in under 5 milliseconds."* |
| **4:15 - 5:00** | **Kubernetes & Observability** | Show `k8s/` manifests, `helm/` chart, and Prometheus/Grafana dashboard at `http://localhost:3000`. | *"Finally, in Tasks 7 and 8, we orchestrated high-availability serving using Kubernetes Deployment manifests with 2 replicas, rolling updates, health probes, and Horizontal Pod Autoscaling, supplemented by a Helm chart. Observability is maintained via Prometheus scraping our /metrics endpoint and a pre-configured Grafana dashboard visualizing real-time RPS, latency, and prediction distributions. The complete 10-page formal report is compiled in PDF and Word in the reports/ folder. Thank you!"* |

---

## Step-by-Step Recording Preparation Checklist

1. **Terminal 1 (Model Training & Tests):**
   ```bash
   python -m src.train
   python -m pytest tests/ -v
   ```
2. **Terminal 2 (Launch MLflow UI):**
   ```bash
   mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
   ```
   *Open browser at `http://localhost:5000` to show experiment runs.*
3. **Terminal 3 (Launch API Server):**
   ```bash
   python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000
   ```
   *Open browser at `http://localhost:8000/docs` to show interactive Swagger UI.*
4. **Terminal 4 (Run Endpoint Verification):**
   ```bash
   python scripts/test_serving.py
   ```
5. **Show Report:**
   *Open `reports/MLOps_Assignment_1_Report.pdf` and scroll through the 10 pages.*
