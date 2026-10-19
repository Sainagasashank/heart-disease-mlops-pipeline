"""Central configuration module for the Heart Disease MLOps pipeline."""

import os
from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
SCREENSHOTS_DIR = REPORTS_DIR / "screenshots"

# Create directories if they do not exist
for path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, REPORTS_DIR, FIGURES_DIR, SCREENSHOTS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Data Sources
UCI_HEART_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
LOCAL_DATASET_PATH = PROJECT_ROOT / "dataset" / "processed.cleveland.data"
RAW_CSV_PATH = RAW_DATA_DIR / "heart_disease_raw.csv"
CLEANED_CSV_PATH = PROCESSED_DATA_DIR / "heart_disease_cleaned.csv"
MODEL_ARTIFACT_PATH = MODELS_DIR / "heart_disease_pipeline.joblib"

# Feature Names & Schema
COLUMN_NAMES = [
    "age",       # Age in years
    "sex",       # 1 = male, 0 = female
    "cp",        # Chest pain type (1: typical angina, 2: atypical angina, 3: non-anginal, 4: asymptomatic)
    "trestbps",  # Resting blood pressure in mm Hg
    "chol",      # Serum cholesterol in mg/dl
    "fbs",       # Fasting blood sugar > 120 mg/dl (1 = true, 0 = false)
    "restecg",   # Resting ECG results (0 = normal, 1 = ST-T wave abnormality, 2 = LV hypertrophy)
    "thalach",   # Maximum heart rate achieved
    "exang",     # Exercise-induced angina (1 = yes, 0 = no)
    "oldpeak",   # ST depression induced by exercise relative to rest
    "slope",     # Slope of peak exercise ST segment (1 = upsloping, 2 = flat, 3 = downsloping)
    "ca",        # Number of major vessels (0-3) colored by fluoroscopy
    "thal",      # Thalassemia (3 = normal, 6 = fixed defect, 7 = reversible defect)
    "target"     # Diagnosis: 0 = absent (<50% narrowing), 1-4 = present (>50% narrowing)
]

NUMERICAL_FEATURES = ["age", "trestbps", "chol", "thalach", "oldpeak"]
CATEGORICAL_FEATURES = ["sex", "cp", "fbs", "restecg", "exang", "slope", "ca", "thal"]
TARGET_COLUMN = "target"
BINARY_TARGET_COLUMN = "target_binary"

# Modeling & Experiment Tracking
RANDOM_STATE = 42
TEST_SIZE = 0.2
CV_FOLDS = 5
INNER_CV_FOLDS = 3
MLFLOW_EXPERIMENT_NAME = "heart-disease-prediction"
SQLITE_DB_PATH = PROJECT_ROOT / "mlflow.db"
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", f"sqlite:///{SQLITE_DB_PATH.as_posix()}")
