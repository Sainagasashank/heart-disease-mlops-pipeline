# Heart Disease MLOps Pipeline

End-to-end MLOps assignment project for binary heart-disease prediction using the UCI Cleveland dataset. It includes reproducible training, MLflow tracking, a FastAPI serving API, Docker, local Kubernetes manifests/Helm, Prometheus, Grafana, tests, and CI definitions.

Repository: <https://github.com/Sainagasashank/heart-disease-mlops-pipeline>

## What is included

- Reproducible data acquisition, cleaning, EDA, and a leakage-safe sklearn preprocessing pipeline.
- Logistic Regression, Random Forest, and Gradient Boosting with GridSearchCV and nested cross-validation.
- MLflow parameters, metrics, models, figures, reports, and tuning-result artifacts.
- FastAPI endpoints: `/health`, `/predict`, `/metrics`, and `/docs`.
- Docker image, Kubernetes Deployment/Service/Ingress/HPA, Helm chart, Prometheus, Grafana, GitHub Actions, and Jenkinsfile.

## Requirements

- Python **3.12** for the pinned reproducible environment.
- Docker Desktop for container, Kubernetes, Prometheus, and Grafana commands.
- Docker Desktop Kubernetes enabled for the Kubernetes walkthrough.
- GNU Make is optional on Windows; `Make.ps1` provides equivalent targets.

## Clean setup

### Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
```

If `py -3.12` is unavailable, install Python 3.12 first. Do not train under a different sklearn version and then serve using the Docker image; the pinned Python 3.12 environment prevents model-serialization skew.

### Command runner

On macOS/Linux or Windows with GNU Make:

```powershell
make data
make train
make lint
make test
```

On Windows PowerShell without GNU Make:

```powershell
.\Make.ps1 data
.\Make.ps1 train
.\Make.ps1 lint
.\Make.ps1 test
```

Optionally enable the `make` shorthand in future PowerShell sessions:

```powershell
.\scripts\setup_make_command.ps1
```

## Run the pipeline

```powershell
.\Make.ps1 data       # download/fallback dataset, clean it, and create EDA figures
.\Make.ps1 train      # tune models, evaluate, save model, and log MLflow runs
.\Make.ps1 lint       # strict flake8
.\Make.ps1 test       # pytest suite
```

Generated outputs include `data/processed/heart_disease_cleaned.csv`, `reports/figures/`, `reports/model_comparison.csv`, `reports/tuning_results.csv`, `models/heart_disease_pipeline.joblib`, and `models/model_metadata.json`.

## Modelling protocol

All candidates are a single preprocessing-plus-classifier Pipeline. Numerical features receive median imputation and standard scaling; categorical features receive most-frequent imputation and one-hot encoding with unknown-category handling.

Logistic Regression, Random Forest, and Gradient Boosting are tuned with 3-fold inner `GridSearchCV` on the 80% training partition. A stratified 5-fold outer nested CV estimates accuracy, precision, recall, F1, and ROC-AUC. The champion is selected by nested-CV ROC-AUC, breaking ties on nested-CV accuracy. The held-out 20% test set is evaluated once and is not a selection signal.

## Local API

Terminal 1:

```powershell
.\Make.ps1 serve
```

Terminal 2:

```powershell
.\Make.ps1 docker-test
```

Open Swagger: <http://127.0.0.1:8000/docs>. Send `sample_patient.json` to `/predict`, or use the interactive Swagger form.

## MLflow

```powershell
.\Make.ps1 mlflow-ui
```

Open <http://127.0.0.1:5000>, select **Model training**, then open the `heart-disease-prediction` experiment. The target first runs `scripts/relocate_mlflow.py`, which repairs local artifact URIs after moving the project.

## Docker

```powershell
.\Make.ps1 docker-build
.\Make.ps1 docker-run
.\Make.ps1 docker-test
docker rm -f heart-disease-serving
```

## Kubernetes on Docker Desktop

Enable Kubernetes in Docker Desktop, then use its bundled `kubectl` if needed:

```powershell
$kubectl = "C:\Users\jnvsa\AppData\Local\Programs\DockerDesktop\resources\bin\kubectl.exe"
docker build -t heart-disease-api:verified .
& $kubectl apply -f k8s/deployment.yaml
& $kubectl apply -f k8s/service.yaml
& $kubectl apply -f k8s/ingress.yaml
& $kubectl apply -f k8s/hpa.yaml
& $kubectl rollout status deployment/heart-disease-api --timeout=120s
& $kubectl get pods,svc,hpa,ingress
& $kubectl port-forward service/heart-disease-service 8002:80
```

In a second terminal, verify the deployed service:

```powershell
python scripts/test_serving.py http://127.0.0.1:8002
```

The equivalent Helm chart is in `helm/heart-disease-api/`.

## Monitoring

Copy the safe template only if you want to set local Grafana credentials:

```powershell
Copy-Item .env.example .env
```

Set a non-default `GRAFANA_ADMIN_PASSWORD` in `.env` before any non-local exposure. The `.env` file is ignored by Git.

```powershell
.\Make.ps1 monitoring-up
.\Make.ps1 traffic
```

Open Prometheus at <http://127.0.0.1:9090> and Grafana at <http://127.0.0.1:3000>. Prometheus scrapes `api:8000`; Grafana is provisioned with the Prometheus datasource and the Heart Disease serving dashboard. Stop the stack with `./Make.ps1 monitoring-down`.

## Secrets and identity

No API keys, tokens, private keys, or personal credentials belong in this repository. Keep secrets only in a local `.env` file or in GitHub Actions Secrets. `.env` and `.env.*` are ignored, while `.env.example` is the safe committed template.

To set report identity locally without committing it:

```powershell
$env:REPORT_STUDENT_NAME = "Your Name"
$env:REPORT_STUDENT_ID = "Your ID"
$env:REPORT_STUDENT_EMAIL = "you@example.com"
$env:REPO_URL = "https://github.com/Sainagasashank/heart-disease-mlops-pipeline"
.\Make.ps1 report
```

## Repository layout

```text
src/                         data pipeline, training, evaluation and FastAPI API
test/                        unit and API tests
notebooks/                   EDA, training/evaluation and inference notebooks
scripts/                     serving, traffic, MLflow, report and deployment helpers
models/                      serialized pipeline and metadata
reports/                     figures, comparison/tuning reports, final report and evidence
monitoring/                  Docker Compose, Prometheus and Grafana provisioning
k8s/                         Kubernetes manifests
helm/heart-disease-api/      Helm chart
.github/workflows/ci.yml     GitHub Actions workflow
```

## Evidence and remaining submission actions

The project includes the required code and local deployment/monitoring configuration. Capture real screenshots from your own successful GitHub Actions run, Docker/Kubernetes deployment, Grafana dashboard, MLflow UI, API docs, tests, and Prometheus views in `reports/screenshots/`. See `reports/screenshots/README.md` for filenames. Record the required video after capturing those live results.
