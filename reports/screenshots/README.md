# Screenshot Evidence Guide for Reporting

This directory contains visual execution evidence for the BITS Pilani AIMLCZG523 Assignment 01 submission.

## Required Screenshots Checklist

1. **`01_eda_visualizations.png`**:
   - High-resolution target class balance, feature distribution histograms, and correlation matrix.
   - *Source:* Generated in `reports/figures/`.

2. **`02_model_training_comparison.png`**:
   - Model comparison table in terminal or MLflow UI showing Logistic Regression (88.52% Test Acc, 0.9665 ROC-AUC), Random Forest, and Gradient Boosting.

3. **`03_mlflow_tracking_ui.png`**:
   - MLflow UI showing runs under the `heart-disease-prediction` experiment, logged parameters, metrics, and confusion matrix artifacts.
   - *Command to launch:* `mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000`

4. **`04_pytest_test_results.png`**:
   - Terminal execution of `python -m pytest tests/ -v` displaying 12 passing unit & integration tests.

5. **`05_github_actions_pipeline.png`**:
   - GitHub Actions workflow run passing all stages: Linting & Unit Testing, Model Training & Benchmark, and Docker Verification.

6. **`06_docker_container_run.png`**:
   - Docker build and container execution serving FastAPI on port 8000.
   - Execution of `python scripts/test_serving.py` with 200 OK responses across `/`, `/health`, `/predict`, and `/metrics`.

7. **`07_kubernetes_deployment.png`**:
   - Output of `kubectl get pods -l app=heart-disease-api -o wide`, `kubectl get service heart-disease-service`, and `kubectl get hpa heart-disease-hpa`.

8. **`08_prometheus_grafana_dashboard.png`**:
   - Live Grafana dashboard visualising RPS, 95th percentile latency, and real-time positive vs negative heart disease predictions.
