"""Data cleaning and preprocessing contract tests."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from src.config import CATEGORICAL_FEATURES, CLEANED_CSV_PATH, NUMERICAL_FEATURES
from src.preprocessing import build_full_pipeline, clean_raw_data, split_features_target


def test_clean_raw_data_replaces_question_mark():
    raw = pd.DataFrame({"age": [50], "ca": ["?"], "thal": ["?"], "target": [1]})
    cleaned = clean_raw_data(raw)
    assert np.isnan(cleaned.loc[0, "ca"])
    assert np.isnan(cleaned.loc[0, "thal"])
    assert cleaned.loc[0, "target_binary"] == 1


def test_cleaned_data_has_binary_target():
    data = pd.read_csv(CLEANED_CSV_PATH)
    _, target = split_features_target(data)
    assert set(target.unique()) <= {0, 1}


def test_preprocessor_imputes_nan_and_standardizes_numeric_block():
    data = pd.read_csv(CLEANED_CSV_PATH)
    X, y = split_features_target(data)
    X = X.copy()
    X.loc[X.index[:3], "chol"] = np.nan
    pipeline = build_full_pipeline(LogisticRegression(solver="liblinear"))
    pipeline.fit(X, y)
    transformed = pipeline.named_steps["preprocessor"].transform(X)
    assert np.isfinite(transformed).all()
    numeric = transformed[:, :len(NUMERICAL_FEATURES)]
    assert abs(float(numeric[:, 0].mean())) < 1e-10


def test_one_hot_columns_are_binary():
    data = pd.read_csv(CLEANED_CSV_PATH)
    X, y = split_features_target(data)
    pipeline = build_full_pipeline(LogisticRegression(solver="liblinear"))
    pipeline.fit(X, y)
    transformed = pipeline.named_steps["preprocessor"].transform(X)
    categorical = transformed[:, len(NUMERICAL_FEATURES):]
    assert set(np.unique(categorical)) <= {0.0, 1.0}


def test_unseen_category_does_not_crash_inference():
    data = pd.read_csv(CLEANED_CSV_PATH)
    X, y = split_features_target(data)
    pipeline = build_full_pipeline(LogisticRegression(solver="liblinear"))
    pipeline.fit(X, y)
    unseen = X.iloc[[0]].copy()
    unseen["thal"] = 99
    assert pipeline.predict(unseen)[0] in (0, 1)


def test_feature_schema_has_expected_blocks():
    assert len(NUMERICAL_FEATURES) == 5
    assert len(CATEGORICAL_FEATURES) == 8


def test_cleaned_dataset_has_303_rows():
    assert len(pd.read_csv(CLEANED_CSV_PATH)) == 303
