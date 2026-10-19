"""Training and evaluation contracts."""

import joblib
import numpy as np
import pandas as pd

from src.config import CLEANED_CSV_PATH, MODEL_ARTIFACT_PATH
from src.evaluate import compute_metrics
from src.preprocessing import build_full_pipeline, split_features_target
from src.train import get_candidate_models


def test_compute_metrics_known_values():
    metrics = compute_metrics(np.array([0, 1, 1, 0]), np.array([0, 1, 0, 0]), np.array([.1, .9, .4, .2]))
    assert metrics["accuracy"] == 0.75
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 0.5
    assert metrics["f1"] == 2 / 3
    assert metrics["roc_auc"] == 1.0


def test_every_tuning_grid_key_is_valid_for_pipeline():
    for config in get_candidate_models().values():
        params = build_full_pipeline(config["estimator"]).get_params()
        assert set(config["param_grid"]).issubset(params)


def test_candidate_grids_have_required_sizes():
    grids = get_candidate_models()
    assert len(grids["LogisticRegression"]["param_grid"]["classifier__C"]) == 7
    assert len(grids["RandomForest"]["param_grid"]["classifier__n_estimators"]) == 2
    assert len(grids["GradientBoosting"]["param_grid"]["classifier__max_depth"]) == 2


def test_serialized_model_predicts_binary():
    model = joblib.load(MODEL_ARTIFACT_PATH)
    data = pd.read_csv(CLEANED_CSV_PATH)
    X, _ = split_features_target(data)
    assert set(model.predict(X).tolist()) <= {0, 1}


def test_serialized_model_probabilities_are_valid():
    model = joblib.load(MODEL_ARTIFACT_PATH)
    data = pd.read_csv(CLEANED_CSV_PATH)
    X, _ = split_features_target(data)
    probabilities = model.predict_proba(X.iloc[:5])
    assert np.allclose(probabilities.sum(axis=1), 1.0)
