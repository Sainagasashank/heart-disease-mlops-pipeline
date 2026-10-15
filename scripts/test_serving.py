"""Script to verify running Heart Disease API endpoints (Local / Docker / Kubernetes)."""

import json
import sys
import requests

DEFAULT_URL = "http://localhost:8000"


def test_api(base_url: str = DEFAULT_URL):
    """Test root, health, predict, and metrics endpoints."""
    print(f"Testing API at: {base_url}")

    # 1. Root
    try:
        r_root = requests.get(f"{base_url}/")
        print(f"\n[1/4] GET / -> Status {r_root.status_code}")
        print("  Response:", r_root.json())
    except Exception as e:
        print(f"  Failed: {e}")
        return False

    # 2. Health
    try:
        r_health = requests.get(f"{base_url}/health")
        print(f"\n[2/4] GET /health -> Status {r_health.status_code}")
        print("  Response:", r_health.json())
    except Exception as e:
        print(f"  Failed: {e}")
        return False

    # 3. Predict
    sample_patient = {
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
    try:
        r_pred = requests.post(f"{base_url}/predict", json=sample_patient)
        print(f"\n[3/4] POST /predict -> Status {r_pred.status_code}")
        print("  Payload:", json.dumps(sample_patient))
        print("  Response:", json.dumps(r_pred.json(), indent=2))
    except Exception as e:
        print(f"  Failed: {e}")
        return False

    # 4. Metrics
    try:
        r_metrics = requests.get(f"{base_url}/metrics")
        print(f"\n[4/4] GET /metrics -> Status {r_metrics.status_code}")
        metrics_snippet = "\n".join(r_metrics.text.splitlines()[:5])
        print(f"  Snippet:\n{metrics_snippet}")
    except Exception as e:
        print(f"  Failed: {e}")
        return False

    print("\n>>> All API tests passed successfully! <<<")
    return True


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
    success = test_api(url)
    sys.exit(0 if success else 1)
