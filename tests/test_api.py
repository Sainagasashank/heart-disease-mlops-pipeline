"""Integration tests for FastAPI model serving endpoints."""

import pytest
from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)


def test_root_endpoint():
    """Verify that root endpoint returns 200 OK and valid metadata."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "version" in data
    assert "documentation" in data


def test_health_endpoint():
    """Verify that health check endpoint returns 200 OK and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert "model_name" in data


def test_predict_endpoint_valid():
    """Verify /predict endpoint returns correct prediction format with confidence score."""
    payload = {
        "age": 63.0,
        "sex": 1.0,
        "cp": 1.0,
        "trestbps": 145.0,
        "chol": 233.0,
        "fbs": 1.0,
        "restecg": 2.0,
        "thalach": 150.0,
        "exang": 0.0,
        "oldpeak": 2.3,
        "slope": 3.0,
        "ca": 0.0,
        "thal": 6.0,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "prediction" in data
    assert data["prediction"] in (0, 1)
    assert "confidence" in data
    assert 0.0 <= data["confidence"] <= 1.0
    assert "risk_label" in data
    assert "disease_probability" in data
    assert "healthy_probability" in data


def test_predict_endpoint_invalid_payload():
    """Verify /predict endpoint returns 422 Unprocessable Entity for schema violations."""
    # Invalid: age > 120 (violates Pydantic le=120 validator)
    invalid_payload = {
        "age": 150.0,
        "sex": 1.0,
        "cp": 1.0,
        "trestbps": 145.0,
        "chol": 233.0,
        "fbs": 1.0,
        "restecg": 2.0,
        "thalach": 150.0,
        "exang": 0.0,
        "oldpeak": 2.3,
        "slope": 3.0,
        "ca": 0.0,
        "thal": 6.0,
    }
    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 422


def test_metrics_endpoint():
    """Verify that /metrics endpoint exposes Prometheus metrics with 200 OK."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "heart_disease_predictions_total" in response.text
