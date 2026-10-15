.PHONY: help install data train test serve docker-build docker-run k8s-deploy report clean

PYTHON := python

help:
	@echo "Heart Disease MLOps Workflow Commands:"
	@echo "  make install      Install production and development dependencies"
	@echo "  make data         Acquire and preprocess UCI Heart Disease dataset"
	@echo "  make train        Train models, evaluate CV, and log to MLflow"
	@echo "  make test         Execute Pytest unit and integration test suite"
	@echo "  make serve        Start FastAPI server locally on port 8000"
	@echo "  make docker-build Build production Docker image"
	@echo "  make docker-run   Run Docker container locally on port 8000"
	@echo "  make k8s-deploy   Deploy manifests to Kubernetes cluster"
	@echo "  make report       Generate 10-page PDF and DOCX academic reports"
	@echo "  make clean        Remove cache files, compiled binaries, and temporary logs"

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements-dev.txt

data:
	$(PYTHON) -m src.data_loader
	$(PYTHON) -m src.preprocessing
	$(PYTHON) -m src.eda

train:
	$(PYTHON) -m src.train

test:
	$(PYTHON) -m pytest tests/ -v

serve:
	$(PYTHON) -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000

docker-build:
	docker build -t heart-disease-api:latest .

docker-run:
	docker run -d -p 8000:8000 --name heart-disease-serving heart-disease-api:latest

k8s-deploy:
	kubectl apply -f k8s/deployment.yaml
	kubectl apply -f k8s/service.yaml
	kubectl apply -f k8s/ingress.yaml
	kubectl apply -f k8s/hpa.yaml

report:
	$(PYTHON) scripts/generate_report.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
