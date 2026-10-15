"""Model training, hyperparameter tuning, and MLflow experiment tracking module.

Trains and evaluates:
1. Logistic Regression (Regularized baseline)
2. Random Forest Classifier (Ensemble)
3. Gradient Boosting Classifier (Boosting)

Logs parameters, cross-validation metrics, evaluation artifacts, and models to MLflow.
Saves the best-performing end-to-end Pipeline to models/heart_disease_pipeline.joblib.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List
import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split

from src.config import (
    CLEANED_CSV_PATH,
    CV_FOLDS,
    FIGURES_DIR,
    MLFLOW_EXPERIMENT_NAME,
    MLFLOW_TRACKING_URI,
    MODEL_ARTIFACT_PATH,
    MODELS_DIR,
    RANDOM_STATE,
    REPORTS_DIR,
    TEST_SIZE,
)
from src.evaluate import (
    compute_metrics,
    plot_confusion_matrix,
    plot_feature_importance,
    plot_roc_curve,
)
from src.preprocessing import build_full_pipeline, load_and_preprocess_data, split_features_target

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_candidate_models() -> Dict[str, Dict]:
    """Define candidate classification models with tuned hyperparameter sets."""
    return {
        "LogisticRegression": {
            "estimator": LogisticRegression(
                C=0.1,
                solver="liblinear",
                max_iter=1000,
                random_state=RANDOM_STATE,
            ),
            "params": {"C": 0.1, "solver": "liblinear"},
        },
        "RandomForest": {
            "estimator": RandomForestClassifier(
                n_estimators=150,
                max_depth=6,
                min_samples_split=4,
                min_samples_leaf=2,
                random_state=RANDOM_STATE,
            ),
            "params": {
                "n_estimators": 150,
                "max_depth": 6,
                "min_samples_split": 4,
                "min_samples_leaf": 2,
            },
        },
        "GradientBoosting": {
            "estimator": GradientBoostingClassifier(
                n_estimators=100,
                learning_rate=0.05,
                max_depth=3,
                random_state=RANDOM_STATE,
            ),
            "params": {"n_estimators": 100, "learning_rate": 0.05, "max_depth": 3},
        },
    }


def train_and_track_experiments(
    data_path: Path = CLEANED_CSV_PATH,
    tracking_uri: str = MLFLOW_TRACKING_URI,
    experiment_name: str = MLFLOW_EXPERIMENT_NAME,
) -> Dict[str, Any]:
    """Train all candidate models, log to MLflow, and persist the top-performing pipeline."""
    # Ensure dataset is ready
    if not data_path.exists():
        df = load_and_preprocess_data()
    else:
        df = pd.read_csv(data_path)

    X, y = split_features_target(df)
    logger.info(f"Splitting dataset: Total={len(X)}, Test Size={TEST_SIZE}, Random State={RANDOM_STATE}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
    )

    # Set up MLflow
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    logger.info(f"MLflow experiment configured: {experiment_name} at {tracking_uri}")

    models = get_candidate_models()
    results = []
    trained_pipelines = {}

    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    scoring = ["accuracy", "precision", "recall", "f1", "roc_auc"]

    for model_name, config in models.items():
        logger.info(f"\n{'='*25} Training {model_name} {'='*25}")
        estimator = config["estimator"]
        params = config["params"]

        # Build full pipeline (preprocessor + model)
        pipeline = build_full_pipeline(estimator)

        # 1. Stratified Cross-Validation on Training Set
        cv_scores = cross_validate(pipeline, X_train, y_train, cv=cv, scoring=scoring)
        cv_metrics = {f"cv_{metric}_mean": float(np.mean(cv_scores[f"test_{metric}"])) for metric in scoring}
        cv_stds = {f"cv_{metric}_std": float(np.std(cv_scores[f"test_{metric}"])) for metric in scoring}

        # 2. Fit on Full Train Split
        pipeline.fit(X_train, y_train)
        trained_pipelines[model_name] = pipeline

        # 3. Evaluate on Held-out Test Split
        y_pred = pipeline.predict(X_test)
        y_prob = pipeline.predict_proba(X_test)[:, 1]
        test_metrics = compute_metrics(y_test.values, y_pred, y_prob)

        logger.info(
            f"{model_name} Results -> CV Accuracy: {cv_metrics['cv_accuracy_mean']:.3f} | "
            f"Test Accuracy: {test_metrics['accuracy']:.3f} | Test ROC-AUC: {test_metrics['roc_auc']:.3f}"
        )

        # 4. Generate Evaluation Visualizations
        cm_path = plot_confusion_matrix(y_test.values, y_pred, model_name, FIGURES_DIR)
        roc_path, _ = plot_roc_curve(y_test.values, y_prob, model_name, FIGURES_DIR)
        feat_path = plot_feature_importance(pipeline, model_name, FIGURES_DIR)

        # Generate text classification report
        cls_report = classification_report(y_test, y_pred, target_names=["No Disease", "Disease Present"])
        report_file = REPORTS_DIR / f"classification_report_{model_name.lower()}.txt"
        with open(report_file, "w") as f:
            f.write(cls_report)

        # 5. Log Everything to MLflow
        with mlflow.start_run(run_name=model_name):
            # Log params
            mlflow.log_params(params)
            mlflow.log_param("test_size", TEST_SIZE)
            mlflow.log_param("cv_folds", CV_FOLDS)
            mlflow.log_param("random_state", RANDOM_STATE)

            # Log metrics
            for k, v in cv_metrics.items():
                mlflow.log_metric(k, v)
            for k, v in cv_stds.items():
                mlflow.log_metric(k, v)
            for k, v in test_metrics.items():
                mlflow.log_metric(f"test_{k}", v)

            # Log artifacts
            if cm_path and cm_path.exists():
                mlflow.log_artifact(str(cm_path))
            if roc_path and roc_path.exists():
                mlflow.log_artifact(str(roc_path))
            if feat_path and feat_path.exists():
                mlflow.log_artifact(str(feat_path))
            if report_file.exists():
                mlflow.log_artifact(str(report_file))

            # Log model artifact with input example
            sample_input = X_test.iloc[:2]
            mlflow.sklearn.log_model(
                sk_model=pipeline,
                name="model",
                input_example=sample_input,
                serialization_format="cloudpickle",
            )

        # Compile comparison record
        result_record = {
            "Model": model_name,
            "CV Accuracy": round(cv_metrics["cv_accuracy_mean"], 4),
            "CV ROC-AUC": round(cv_metrics["cv_roc_auc_mean"], 4),
            "Test Accuracy": round(test_metrics["accuracy"], 4),
            "Test Precision": round(test_metrics["precision"], 4),
            "Test Recall": round(test_metrics["recall"], 4),
            "Test F1": round(test_metrics["f1"], 4),
            "Test ROC-AUC": round(test_metrics["roc_auc"], 4),
        }
        results.append(result_record)

    # Comparison summary
    results_df = pd.DataFrame(results).sort_values(by="Test ROC-AUC", ascending=False)
    comparison_csv = REPORTS_DIR / "model_comparison.csv"
    comparison_md = REPORTS_DIR / "model_comparison.md"
    results_df.to_csv(comparison_csv, index=False)
    results_df.to_markdown(comparison_md, index=False)

    logger.info(f"\nModel Comparison:\n{results_df.to_string(index=False)}")

    # Select Best Model
    best_model_name = results_df.iloc[0]["Model"]
    best_pipeline = trained_pipelines[best_model_name]
    logger.info(f"\nSelected Best Model: {best_model_name}")

    # Serialize Best Pipeline to disk
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, MODEL_ARTIFACT_PATH)
    logger.info(f"Serialized best pipeline saved to: {MODEL_ARTIFACT_PATH}")

    # Save metadata
    metadata = {
        "best_model_name": best_model_name,
        "metrics": results_df.iloc[0].to_dict(),
        "features": list(X.columns),
    }
    with open(MODELS_DIR / "model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    return metadata


if __name__ == "__main__":
    train_and_track_experiments()
