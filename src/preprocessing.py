"""Data cleaning, preprocessing, and Scikit-learn transformation pipelines.

Ensures zero training-serving skew by encapsulating imputation, scaling,
and encoding into a unified ColumnTransformer and Pipeline.
"""

import logging
from pathlib import Path
from typing import Tuple
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import (
    BINARY_TARGET_COLUMN,
    CATEGORICAL_FEATURES,
    CLEANED_CSV_PATH,
    NUMERICAL_FEATURES,
    RAW_CSV_PATH,
    TARGET_COLUMN,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def clean_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw UCI Heart Disease DataFrame.

    - Replaces '?' missing value markers with NaN.
    - Converts columns to appropriate numeric datatypes.
    - Creates a binary classification target (0: No disease, 1: Disease present).

    Args:
        df: Raw input DataFrame.

    Returns:
        pd.DataFrame: Cleaned and structured DataFrame.
    """
    cleaned = df.copy()

    # Replace '?' and whitespace with NaN
    cleaned = cleaned.replace("?", np.nan)
    cleaned = cleaned.replace(r"^\s*$", np.nan, regex=True)

    # Cast all feature columns to numeric
    for col in NUMERICAL_FEATURES + CATEGORICAL_FEATURES:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    # Ensure target column is numeric
    if TARGET_COLUMN in cleaned.columns:
        cleaned[TARGET_COLUMN] = pd.to_numeric(cleaned[TARGET_COLUMN], errors="coerce").fillna(0).astype(int)
        # Binarize target: 0 -> 0 (Absence), 1-4 -> 1 (Presence)
        cleaned[BINARY_TARGET_COLUMN] = (cleaned[TARGET_COLUMN] > 0).astype(int)

    logger.info(
        f"Data cleaned. Total rows: {len(cleaned)}, "
        f"Missing values found: {cleaned.isna().sum().sum()} across {cleaned.columns[cleaned.isna().any()].tolist()}"
    )
    return cleaned


def load_and_preprocess_data(
    raw_path: Path = RAW_CSV_PATH,
    cleaned_path: Path = CLEANED_CSV_PATH
) -> pd.DataFrame:
    """Load raw dataset from disk, clean it, and persist the cleaned dataset.

    Args:
        raw_path: Path to raw CSV.
        cleaned_path: Path to write cleaned CSV.

    Returns:
        pd.DataFrame: Cleaned dataset.
    """
    if not raw_path.exists():
        from src.data_loader import acquire_dataset
        raw_df = acquire_dataset(raw_output_path=raw_path)
    else:
        raw_df = pd.read_csv(raw_path)

    cleaned_df = clean_raw_data(raw_df)
    cleaned_path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(cleaned_path, index=False)
    logger.info(f"Cleaned dataset saved to: {cleaned_path}")
    return cleaned_df


def get_feature_preprocessor() -> ColumnTransformer:
    """Construct an end-to-end ColumnTransformer for feature transformations.

    - Numerical: Median imputation followed by standard scaling.
    - Categorical: Most frequent imputation followed by one-hot encoding.

    Returns:
        ColumnTransformer: Configured preprocessor object.
    """
    numerical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ]
    )

    return preprocessor


def build_full_pipeline(estimator) -> Pipeline:
    """Create a unified scikit-learn Pipeline bundling preprocessor and estimator.

    Args:
        estimator: A Scikit-learn compatible classifier.

    Returns:
        Pipeline: Complete reproducible inference pipeline.
    """
    preprocessor = get_feature_preprocessor()
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", estimator),
        ]
    )
    return pipeline


def split_features_target(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
    """Separate feature matrix and binary target vector.

    Args:
        df: Input DataFrame.

    Returns:
        Tuple[pd.DataFrame, pd.Series]: (X, y)
    """
    features = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    X = df[features].copy()
    y = df[BINARY_TARGET_COLUMN].copy()
    return X, y


if __name__ == "__main__":
    load_and_preprocess_data()
