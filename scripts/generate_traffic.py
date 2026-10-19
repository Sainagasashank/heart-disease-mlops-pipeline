"""Generate valid and intentionally invalid inference traffic for observability."""

import argparse
import sys
import time
from pathlib import Path

import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.config import CLEANED_CSV_PATH, CATEGORICAL_FEATURES, NUMERICAL_FEATURES  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000")
    parser.add_argument("--count", type=int, default=30)
    parser.add_argument("--delay", type=float, default=0.05)
    args = parser.parse_args()
    data = pd.read_csv(CLEANED_CSV_PATH)
    features = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    successes = 0
    for index in range(args.count):
        if index % 10 == 9:
            response = requests.post(f"{args.url}/predict", json={"age": 50}, timeout=10)
            expected = 422
        else:
            row = data.iloc[index % len(data)][features]
            payload = {key: float(value) for key, value in row.items()}
            response = requests.post(f"{args.url}/predict", json=payload, timeout=10)
            expected = 200
        if response.status_code != expected:
            print(f"request {index + 1}: expected {expected}, got {response.status_code}: {response.text}")
            return 1
        successes += 1
        time.sleep(args.delay)
    print(f"Generated {successes} requests against {args.url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
