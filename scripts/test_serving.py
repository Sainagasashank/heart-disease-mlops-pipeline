"""Fail-fast smoke test for a running local, Docker, or Kubernetes API."""

import json
import sys
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_URL = "http://127.0.0.1:8000"


def _get_json(response: requests.Response, label: str) -> dict:
    if response.status_code != 200:
        raise RuntimeError(f"{label} returned HTTP {response.status_code}: {response.text}")
    return response.json()


def test_api(base_url: str = DEFAULT_URL) -> bool:
    """Validate endpoint status codes and the serving response contract."""
    try:
        root = _get_json(requests.get(f"{base_url}/", timeout=10), "GET /")
        health = _get_json(requests.get(f"{base_url}/health", timeout=10), "GET /health")
        payload = json.loads((PROJECT_ROOT / "sample_patient.json").read_text(encoding="utf-8"))
        prediction = _get_json(requests.post(f"{base_url}/predict", json=payload, timeout=10), "POST /predict")
        metrics = requests.get(f"{base_url}/metrics", timeout=10)
        invalid = payload | {"cp": 9}
        invalid_response = requests.post(f"{base_url}/predict", json=invalid, timeout=10)
        assert root["status"] == "online"
        assert health["model_loaded"] is True
        assert prediction["prediction"] in {0, 1}
        assert 0.0 <= prediction["confidence"] <= 1.0
        assert metrics.status_code == 200
        assert "heart_disease_predictions_total" in metrics.text
        assert invalid_response.status_code == 422
    except (OSError, ValueError, KeyError, AssertionError, requests.RequestException, RuntimeError) as error:
        print(f"SERVING VERIFICATION FAILED: {error}")
        return False
    print("SERVING VERIFICATION PASSED")
    print(json.dumps({"health": health, "prediction": prediction}, indent=2))
    return True


if __name__ == "__main__":
    sys.exit(0 if test_api(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL) else 1)
