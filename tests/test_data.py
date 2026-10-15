"""Unit tests for dataset acquisition, integrity, and preprocessing."""

import numpy as np
import pandas as pd
import pytest

from src.config import (
    BINARY_TARGET_COLUMN,
    CATEGORICAL_FEATURES,
    CLEANED_CSV_PATH,
    COLUMN_NAMES,
    NUMERICAL_FEATURES,
    RAW_CSV_PATH,
    TARGET_COLUMN,
)
from src.data_loader import acquire_dataset
from src.preprocessing import clean_raw_data, load_and_preprocess_data, split_features_target


def test_acquire_dataset():
    """Verify raw dataset acquisition loads 303 rows and 14 columns."""
    df = acquire_dataset(raw_output_path=RAW_CSV_PATH)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 303
    assert list(df.columns) == COLUMN_NAMES


def test_clean_raw_data():
    """Verify that clean_raw_data properly handles '?' and binarizes target."""
    raw_df = pd.read_csv(RAW_CSV_PATH)
    cleaned_df = clean_raw_data(raw_df)

    # Check shape
    assert len(cleaned_df) == 303
    # Check that missing value '?' is converted to NaN
    assert not (cleaned_df == "?").any().any()

    # Check binary target creation
    assert BINARY_TARGET_COLUMN in cleaned_df.columns
    unique_targets = set(cleaned_df[BINARY_TARGET_COLUMN].unique())
    assert unique_targets.issubset({0, 1})

    # Check multi-class to binary mapping logic: 0 -> 0, >0 -> 1
    zero_mask = cleaned_df[TARGET_COLUMN] == 0
    assert (cleaned_df.loc[zero_mask, BINARY_TARGET_COLUMN] == 0).all()
    pos_mask = cleaned_df[TARGET_COLUMN] > 0
    assert (cleaned_df.loc[pos_mask, BINARY_TARGET_COLUMN] == 1).all()


def test_split_features_target():
    """Ensure feature-target split produces correct shapes and types."""
    df = pd.read_csv(CLEANED_CSV_PATH)
    X, y = split_features_target(df)

    expected_features = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    assert list(X.columns) == expected_features
    assert len(X) == len(y)
    assert len(X) == 303
    assert set(y.unique()).issubset({0, 1})
