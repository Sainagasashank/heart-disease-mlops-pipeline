"""Pydantic data validation contracts for FastAPI Heart Disease serving API."""

from datetime import datetime, timezone
from pydantic import BaseModel, Field


def get_utc_now_iso() -> str:
    """Return ISO format string of current UTC time."""
    return datetime.now(timezone.utc).isoformat()


class PatientInput(BaseModel):
    """Clinical patient health features required for inference."""

    age: float = Field(..., ge=1, le=120, description="Age in years (1 - 120)")
    sex: float = Field(..., ge=0, le=1, description="Sex (1 = male; 0 = female)")
    cp: float = Field(
        ...,
        ge=1,
        le=4,
        description="Chest pain type (1: typical angina, 2: atypical angina, 3: non-anginal pain, 4: asymptomatic)",
    )
    trestbps: float = Field(..., ge=50, le=260, description="Resting blood pressure in mm Hg (50 - 260)")
    chol: float = Field(..., ge=50, le=600, description="Serum cholesterol in mg/dl (50 - 600)")
    fbs: float = Field(..., ge=0, le=1, description="Fasting blood sugar > 120 mg/dl (1 = true; 0 = false)")
    restecg: float = Field(
        ...,
        ge=0,
        le=2,
        description="Resting ECG (0: normal, 1: ST-T wave abnormality, 2: left ventricular hypertrophy)",
    )
    thalach: float = Field(..., ge=50, le=250, description="Maximum heart rate achieved (50 - 250 bpm)")
    exang: float = Field(..., ge=0, le=1, description="Exercise-induced angina (1 = yes; 0 = no)")
    oldpeak: float = Field(..., ge=0.0, le=10.0, description="ST depression induced by exercise relative to rest")
    slope: float = Field(
        ...,
        ge=1,
        le=3,
        description="Slope of peak exercise ST segment (1: upsloping, 2: flat, 3: downsloping)",
    )
    ca: float = Field(
        ...,
        ge=0,
        le=3,
        description="Number of major vessels (0-3) colored by fluoroscopy",
    )
    thal: float = Field(
        ...,
        description="Thalassemia status (3 = normal; 6 = fixed defect; 7 = reversible defect)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
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
        }
    }


class PredictionOutput(BaseModel):
    """Inference result schema returned by /predict endpoint."""

    prediction: int = Field(..., description="Binary prediction: 0 = Absence, 1 = Presence")
    risk_label: str = Field(..., description="Human-readable risk classification")
    confidence: float = Field(..., description="Model confidence score for the predicted class [0.0 - 1.0]")
    disease_probability: float = Field(..., description="Probability of heart disease presence [0.0 - 1.0]")
    healthy_probability: float = Field(..., description="Probability of heart disease absence [0.0 - 1.0]")
    model_version: str = Field(default="1.0.0", description="Active model artifact version")
    timestamp: str = Field(default_factory=get_utc_now_iso)


class HealthResponse(BaseModel):
    """Liveness & readiness probe response for Kubernetes orchestrators."""

    status: str = "healthy"
    model_loaded: bool = True
    model_name: str
    api_version: str = "1.0.0"
    timestamp: str = Field(default_factory=get_utc_now_iso)
