"""FastAPI Model Serving API for Heart Disease Risk Prediction.

Exposes endpoints:
- GET /: Root metadata
- GET /health: Liveness/Readiness probe for Kubernetes
- POST /predict: Patient risk inference returning prediction and confidence
- GET /metrics: Prometheus metrics endpoint
"""

from contextlib import asynccontextmanager
import json
import logging
import time
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator

from src.api.schemas import HealthResponse, PatientInput, PredictionOutput
from src.predict import get_predictor

# Configure structured logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("heart_disease_api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Warm up and load the trained pipeline into memory at startup."""
    try:
        predictor = get_predictor()
        logger.info(f"Model loaded successfully from {predictor.model_path}")
    except Exception as e:
        logger.error(f"Failed to load model during startup: {e}")
    yield


app = FastAPI(
    title="Heart Disease Prediction API",
    description="Production-ready MLOps API for clinical coronary artery disease risk assessment.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus Custom Metrics
PREDICTION_COUNTER = Counter(
    "heart_disease_predictions_total",
    "Total count of heart disease predictions partitioned by outcome.",
    ["outcome", "risk_label"],
)
PREDICTION_LATENCY = Histogram(
    "heart_disease_inference_latency_seconds",
    "Inference latency distribution in seconds.",
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 1.0],
)

# Initialize standard Prometheus Instrumentator
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/metrics", "/health"],
)
instrumentator.instrument(app)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware for structured request and latency logging."""
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000

    log_payload = {
        "client_ip": request.client.host if request.client else "unknown",
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": round(duration_ms, 2),
    }
    logger.info(f"REQUEST_LOG: {json.dumps(log_payload)}")
    return response


@app.get("/", tags=["General"])
async def root():
    """Root metadata endpoint."""
    return {
        "service": "Heart Disease Prediction Service",
        "status": "online",
        "version": "1.0.0",
        "documentation": "/docs",
        "health_check": "/health",
        "metrics": "/metrics",
    }


@app.get("/health", response_model=HealthResponse, tags=["Observability"])
async def health_check():
    """Liveness and readiness health probe endpoint."""
    try:
        predictor = get_predictor()
        model_name = getattr(predictor.pipeline.named_steps.get("classifier", None), "__class__", type("Unknown")).__name__
        return HealthResponse(
            status="healthy",
            model_loaded=True,
            model_name=model_name,
            api_version="1.0.0",
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unhealthy: {str(e)}",
        )


@app.post("/predict", response_model=PredictionOutput, tags=["Inference"])
async def predict_risk(patient: PatientInput):
    """Serve real-time prediction for patient clinical data.

    Accepts JSON input containing the 13 clinical features.
    Returns prediction (0/1), confidence score, risk classification, and probabilities.
    """
    start_time = time.time()
    try:
        predictor = get_predictor()
        patient_dict = patient.model_dump()
        result = predictor.predict_single(patient_dict)

        latency = time.time() - start_time
        PREDICTION_LATENCY.observe(latency)

        outcome_tag = "disease" if result["prediction"] == 1 else "no_disease"
        PREDICTION_COUNTER.labels(outcome=outcome_tag, risk_label=result["risk_label"]).inc()

        logger.info(
            f"PREDICTION_RESULT: outcome={result['prediction']} "
            f"confidence={result['confidence']} latency_ms={latency*1000:.2f}"
        )

        return PredictionOutput(
            prediction=result["prediction"],
            risk_label=result["risk_label"],
            confidence=result["confidence"],
            disease_probability=result["disease_probability"],
            healthy_probability=result["healthy_probability"],
            model_version="1.0.0",
        )
    except Exception as e:
        logger.error(f"Inference error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}",
        )


@app.get("/metrics", tags=["Observability"])
async def metrics():
    """Expose Prometheus formatted metrics for scraping."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
