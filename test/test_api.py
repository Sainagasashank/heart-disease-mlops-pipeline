"""FastAPI inference, validation and observability contract tests."""

from fastapi.testclient import TestClient

from src.api.app import app

PAYLOAD = {"age": 63, "sex": 1, "cp": 1, "trestbps": 145, "chol": 233, "fbs": 1,
           "restecg": 2, "thalach": 150, "exang": 0, "oldpeak": 2.3, "slope": 3, "ca": 0, "thal": 6}


def test_root_endpoint():
    with TestClient(app) as client:
        assert client.get("/").status_code == 200


def test_health_reports_loaded_model():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["model_loaded"] is True


def test_predict_returns_valid_response():
    with TestClient(app) as client:
        response = client.post("/predict", json=PAYLOAD)
    assert response.status_code == 200
    assert response.json()["prediction"] in (0, 1)
    assert 0 <= response.json()["confidence"] <= 1


def test_missing_field_is_rejected():
    payload = PAYLOAD.copy()
    del payload["age"]
    with TestClient(app) as client:
        assert client.post("/predict", json=payload).status_code == 422


def test_invalid_cp_is_rejected():
    payload = PAYLOAD | {"cp": 9}
    with TestClient(app) as client:
        assert client.post("/predict", json=payload).status_code == 422


def test_prediction_is_deterministic():
    with TestClient(app) as client:
        first = client.post("/predict", json=PAYLOAD).json()
        second = client.post("/predict", json=PAYLOAD).json()
    assert first["prediction"] == second["prediction"]
    assert first["confidence"] == second["confidence"]


def test_metrics_include_custom_counter_and_latency_histogram():
    with TestClient(app) as client:
        client.post("/predict", json=PAYLOAD)
        response = client.get("/metrics")
    assert "heart_disease_predictions_total" in response.text
    assert "heart_disease_inference_latency_seconds" in response.text


def test_docs_are_available():
    with TestClient(app) as client:
        assert client.get("/docs").status_code == 200


def test_prediction_probabilities_are_bounded():
    with TestClient(app) as client:
        response = client.post("/predict", json=PAYLOAD).json()
    assert 0 <= response["disease_probability"] <= 1
    assert 0 <= response["healthy_probability"] <= 1
