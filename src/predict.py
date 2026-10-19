"""Inference module for Heart Disease Risk Prediction.

Loads the serialized end-to-end pipeline and serves real-time or batch predictions.
Ensures identical preprocessing between training and production inference.
"""

import logging
from pathlib import Path
from typing import Any, Dict
import joblib
import numpy as np
import pandas as pd

from src.config import MODEL_ARTIFACT_PATH, NUMERICAL_FEATURES, CATEGORICAL_FEATURES

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class HeartDiseasePredictor:
    """Production inference engine for Heart Disease Classifier."""

    def __init__(self, model_path: Path = MODEL_ARTIFACT_PATH):
        """Initialize and load serialized pipeline artifact."""
        self.model_path = model_path
        self.pipeline = self._load_model()
        self.feature_names = NUMERICAL_FEATURES + CATEGORICAL_FEATURES

    def _load_model(self) -> Any:
        """Load joblib pipeline artifact from disk."""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model artifact not found at {self.model_path}. Please execute `python -m src.train` first."
            )
        logger.info(f"Loading pipeline artifact from {self.model_path}...")
        return joblib.load(self.model_path)

    def predict_single(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run inference on a single patient record dictionary.

        Args:
            data: Dictionary of clinical features.

        Returns:
            Dict containing prediction, risk label, confidence, and probabilities.
        """
        df = pd.DataFrame([data])
        # Validate that all required features exist
        missing = [f for f in self.feature_names if f not in df.columns]
        if missing:
            raise ValueError(f"Input data is missing required clinical features: {missing}")

        pred_class = int(self.pipeline.predict(df)[0])
        probabilities = self.pipeline.predict_proba(df)[0]
        confidence = float(probabilities[pred_class])
        risk_probability = float(probabilities[1])

        return {
            "prediction": pred_class,
            "risk_label": "High Risk (Heart Disease Present)" if pred_class == 1 else "Low Risk (No Heart Disease)",
            "confidence": round(confidence, 4),
            "disease_probability": round(risk_probability, 4),
            "healthy_probability": round(float(probabilities[0]), 4),
        }

    def predict_batch(self, df: pd.DataFrame) -> pd.DataFrame:
        """Run batch inference on a pandas DataFrame.

        Args:
            df: DataFrame containing required clinical features.

        Returns:
            pd.DataFrame: Original DataFrame enriched with predictions and probabilities.
        """
        output_df = df.copy()
        output_df["prediction"] = self.pipeline.predict(df)
        probs = self.pipeline.predict_proba(df)
        output_df["disease_probability"] = probs[:, 1]
        output_df["confidence"] = np.max(probs, axis=1)
        output_df["risk_label"] = np.where(
            output_df["prediction"] == 1,
            "High Risk (Heart Disease Present)",
            "Low Risk (No Heart Disease)",
        )
        return output_df


# Module level singleton
_predictor = None


def get_predictor() -> HeartDiseasePredictor:
    """Retrieve or initialize inference engine singleton."""
    global _predictor
    if _predictor is None:
        _predictor = HeartDiseasePredictor()
    return _predictor


if __name__ == "__main__":
    # Sample test inference
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
    predictor = get_predictor()
    result = predictor.predict_single(sample_patient)
    print("Inference Result for Sample Patient:")
    for k, v in result.items():
        print(f"  {k}: {v}")
