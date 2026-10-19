.PHONY: help all install data train lint test serve docker-build docker-run docker-test mlflow-ui monitoring-up monitoring-down traffic k8s-deploy report clean

PYTHON ?= python

help:
	@echo "Targets: all install data train lint test serve docker-build docker-run docker-test mlflow-ui monitoring-up monitoring-down traffic k8s-deploy report clean"

all: data train lint test

install:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements-dev.txt

data:
	$(PYTHON) -m src.data_loader
	$(PYTHON) -m src.preprocessing
	$(PYTHON) -m src.eda

train:
	$(PYTHON) -m src.train

lint:
	$(PYTHON) -m flake8 src test --max-complexity=10 --max-line-length=127

test:
	$(PYTHON) -m pytest test/ -v

serve:
	$(PYTHON) -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000

docker-build:
	docker build -t heart-disease-api:latest .

docker-run:
	docker run -d -p 8000:8000 --name heart-disease-serving heart-disease-api:latest

docker-test:
	$(PYTHON) scripts/test_serving.py

mlflow-ui:
	$(PYTHON) scripts/relocate_mlflow.py
	$(PYTHON) -m mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000

monitoring-up:
	docker compose -f monitoring/docker-compose.monitoring.yml up --build -d

monitoring-down:
	docker compose -f monitoring/docker-compose.monitoring.yml down

traffic:
	$(PYTHON) scripts/generate_traffic.py

k8s-deploy:
	powershell -ExecutionPolicy Bypass -File scripts/deploy_k8s.ps1

report:
	$(PYTHON) scripts/generate_report.py

clean:
	$(PYTHON) -c "import shutil; from pathlib import Path; [shutil.rmtree(p, ignore_errors=True) for p in Path('.').rglob('__pycache__')]; shutil.rmtree('.pytest_cache', ignore_errors=True)"
