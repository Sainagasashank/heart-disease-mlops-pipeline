"""Data acquisition module for Heart Disease UCI dataset.

Provides automated download from the UCI Machine Learning Repository
with seamless offline fallback to the local dataset directory.
"""

import logging
import urllib.request
from pathlib import Path
import pandas as pd

from src.config import (
    COLUMN_NAMES,
    LOCAL_DATASET_PATH,
    RAW_CSV_PATH,
    UCI_HEART_URL,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def acquire_dataset(url: str = UCI_HEART_URL, raw_output_path: Path = RAW_CSV_PATH) -> pd.DataFrame:
    """Download or load the UCI Cleveland Heart Disease dataset.

    Args:
        url: Remote URL for the processed Cleveland dataset.
        raw_output_path: Destination path for saving the acquired raw CSV.

    Returns:
        pd.DataFrame: Acquired DataFrame with designated column names.
    """
    raw_output_path.parent.mkdir(parents=True, exist_ok=True)
    df = None

    # Try downloading from UCI repository
    logger.info(f"Attempting to download dataset from {url}...")
    try:
        # Download raw content
        urllib.request.urlretrieve(url, raw_output_path)
        # Re-read with proper column names and save with headers
        df = pd.read_csv(raw_output_path, header=None, names=COLUMN_NAMES)
        df.to_csv(raw_output_path, index=False)
        logger.info(f"Successfully downloaded {len(df)} records from UCI Repository.")
    except Exception as e:
        logger.warning(f"Download from remote failed ({e}). Falling back to local dataset...")
        if LOCAL_DATASET_PATH.exists():
            df = pd.read_csv(LOCAL_DATASET_PATH, header=None, names=COLUMN_NAMES)
            df.to_csv(raw_output_path, index=False)
            logger.info(f"Successfully loaded {len(df)} records from local source: {LOCAL_DATASET_PATH}")
        else:
            raise FileNotFoundError(
                f"Neither remote URL ({url}) nor local fallback ({LOCAL_DATASET_PATH}) was accessible."
            )

    logger.info(f"Raw dataset shape: {df.shape}")
    return df


if __name__ == "__main__":
    acquire_dataset()
