"""Unit tests for ML model pipeline, inference output, and performance benchmarks."""

import joblib
import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from src.config import (
    CLEANED_CSV_PATH,
    MODEL_ARTIFACT_PATH,
    RANDOM_STATE,
    TEST_SIZE,
)
from src.predict import HeartDiseasePredictor, get_predictor
from src.preprocessing import build_full_pipeline, split_features_target


@pytest.fixture(scope="module")
def dataset():
    """Load preprocessed features and target."""
    df = pd.read_csv(CLEANED_CSV_PATH)
    X, y = split_features_target(df)
    return X, y


@pytest.fixture(scope="module")
def trained_pipeline():
    """Load serialized production pipeline."""
    assert MODEL_ARTIFACT_PATH.exists(), "Trained model artifact must exist before running tests."
    return joblib.load(MODEL_ARTIFACT_PATH)


def test_pipeline_smoke_fit(dataset):
    """Ensure pipeline fits on sample subset without raising any exceptions."""
    X, y = dataset
    X_sample, y_sample = X.iloc[:50], y.iloc[:50]
    pipeline = build_full_pipeline(LogisticRegression(solver="liblinear", random_state=RANDOM_STATE))
    pipeline.fit(X_sample, y_sample)

    preds = pipeline.predict(X_sample)
    assert len(preds) == 50
    assert set(preds).issubset({0, 1})


def test_model_inference_output(dataset, trained_pipeline):
    """Verify that predictions match expected binary outputs and valid probability distributions."""
    X, _ = dataset
    preds = trained_pipeline.predict(X)
    probs = trained_pipeline.predict_proba(X)

    # Check predictions
    assert len(preds) == len(X)
    assert set(np.unique(preds)).issubset({0, 1})

    # Check probabilities
    assert probs.shape == (len(X), 2)
    assert np.all(probs >= 0.0) and np.all(probs <= 1.0)
    # Row probabilities sum to ~1.0
    np.testing.assert_allclose(probs.sum(axis=1), np.ones(len(X)), atol=1e-5)


def test_predictor_service():
    """Verify the HeartDiseasePredictor inference engine on sample clinical payload."""
    predictor = get_predictor()
    sample_patient = {
        "age": 55.0,
        "sex": 1.0,
        "cp": 4.0,
        "trestbps": 140.0,
        "chol": 240.0,
        "fbs": 0.0,
        "restecg": 0.0,
        "thalach": 160.0,
        "exang": 0.0,
        "oldpeak": 1.2,
        "slope": 2.0,
        "ca": 0.0,
        "thal": 3.0,
    }
    result = predictor.predict_single(sample_patient)

    assert "prediction" in result
    assert result["prediction"] in (0, 1)
    assert "risk_label" in result
    assert 0.0 <= result["confidence"] <= 1.0
    assert 0.0 <= result["disease_probability"] <= 1.0
    assert 0.0 <= result["healthy_probability"] <= 1.0


def test_model_accuracy_benchmark(dataset, trained_pipeline):
    """Ensure trained model meets or exceeds production accuracy baseline (>= 80%)."""
    X, y = dataset
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    y_pred = trained_pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    assert accuracy >= 0.80, f"Model accuracy ({accuracy:.3f}) fell below the 80% baseline threshold."
