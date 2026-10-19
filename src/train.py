"""Train, tune, evaluate and track the heart-disease candidate pipelines.

The champion is selected using nested cross-validation on training data. The
held-out test split is evaluated once only and is never a selection signal.
"""

import json
import logging
import os
from itertools import product
from pathlib import Path
from typing import Any, Dict

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from joblib import parallel_backend
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate, train_test_split

from src.config import (CLEANED_CSV_PATH, CV_FOLDS, FIGURES_DIR, INNER_CV_FOLDS,
                        MLFLOW_EXPERIMENT_NAME, MLFLOW_TRACKING_URI, MODEL_ARTIFACT_PATH,
                        MODELS_DIR, RANDOM_STATE, REPORTS_DIR, TEST_SIZE)
from src.evaluate import compute_metrics, plot_confusion_matrix, plot_feature_importance, plot_roc_curve
from src.preprocessing import build_full_pipeline, load_and_preprocess_data, split_features_target

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
SCORING = ["accuracy", "precision", "recall", "f1", "roc_auc"]
GRID_N_JOBS = -1 if os.getenv("MLOPS_GRID_PARALLEL", "1") == "1" else 1


def get_candidate_models() -> Dict[str, Dict[str, Any]]:
    """Return estimators, baseline parameters and Pipeline-valid tuning grids."""
    return {
        "LogisticRegression": {
            "estimator": LogisticRegression(solver="liblinear", max_iter=2000, random_state=RANDOM_STATE),
            "params": {"solver": "liblinear", "max_iter": 2000, "random_state": RANDOM_STATE},
            "param_grid": {"classifier__C": [0.01, 0.03, 0.1, 0.3, 1, 3, 10],
                           "classifier__penalty": ["l1", "l2"],
                           "classifier__class_weight": [None, "balanced"]},
        },
        "RandomForest": {
            "estimator": RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=1),
            "params": {"random_state": RANDOM_STATE, "n_jobs": 1},
            "param_grid": {"classifier__n_estimators": [100, 200], "classifier__max_depth": [3, 5, 8, None],
                           "classifier__min_samples_leaf": [1, 2, 4]},
        },
        "GradientBoosting": {
            "estimator": GradientBoostingClassifier(random_state=RANDOM_STATE),
            "params": {"random_state": RANDOM_STATE},
            "param_grid": {"classifier__n_estimators": [100, 200], "classifier__learning_rate": [0.03, 0.05, 0.1],
                           "classifier__max_depth": [2, 3]},
        },
    }


def _grid_size(param_grid: Dict[str, list]) -> int:
    return len(list(product(*param_grid.values())))


def train_and_track_experiments(data_path: Path = CLEANED_CSV_PATH,
                                tracking_uri: str = MLFLOW_TRACKING_URI,
                                experiment_name: str = MLFLOW_EXPERIMENT_NAME) -> Dict[str, Any]:
    """Tune each candidate and persist the nested-CV-selected champion."""
    df = pd.read_csv(data_path) if data_path.exists() else load_and_preprocess_data()
    X, y = split_features_target(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
    inner_cv = StratifiedKFold(n_splits=INNER_CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    outer_cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    results, tuning_rows, fitted = [], [], {}

    for model_name, config in get_candidate_models().items():
        logger.info("Tuning %s", model_name)
        pipeline = build_full_pipeline(config["estimator"])
        grid = GridSearchCV(pipeline, config["param_grid"], scoring="roc_auc", cv=inner_cv,
                            n_jobs=GRID_N_JOBS, refit=True, return_train_score=False)
        # Keep outer folds serial so each inner GridSearchCV can safely use
        # its required n_jobs=-1 without nested-process oversubscription.
        # `n_jobs=-1` remains on GridSearchCV; this backend cap prevents
        # oversubscription on Windows where each liblinear fit is inexpensive.
        with parallel_backend("threading", n_jobs=1):
            nested = cross_validate(grid, X_train, y_train, cv=outer_cv, scoring=SCORING, n_jobs=1)
            grid.fit(X_train, y_train)
        cv_metrics = {f"cv_{metric}_{suffix}": float(getattr(np, suffix)(nested[f"test_{metric}"]))
                      for metric in SCORING for suffix in ("mean", "std")}
        best_pipeline = grid.best_estimator_
        fitted[model_name] = best_pipeline
        best_params = dict(grid.best_params_)
        best_params_text = json.dumps(best_params, default=str, sort_keys=True)
        y_pred = best_pipeline.predict(X_test)
        y_prob = best_pipeline.predict_proba(X_test)[:, 1]
        test_metrics = compute_metrics(y_test.to_numpy(), y_pred, y_prob)
        cm_path = plot_confusion_matrix(y_test.to_numpy(), y_pred, model_name, FIGURES_DIR)
        roc_path, _ = plot_roc_curve(y_test.to_numpy(), y_prob, model_name, FIGURES_DIR)
        feature_path = plot_feature_importance(best_pipeline, model_name, FIGURES_DIR)
        report_path = REPORTS_DIR / f"classification_report_{model_name.lower()}.txt"
        report_path.write_text(classification_report(y_test, y_pred, target_names=["No Disease", "Disease Present"]),
                               encoding="utf-8")
        tuning_path = REPORTS_DIR / f"tuning_cv_results_{model_name.lower()}.csv"
        pd.DataFrame(grid.cv_results_).to_csv(tuning_path, index=False)

        with mlflow.start_run(run_name=model_name):
            mlflow.log_params({f"baseline_{key}": value for key, value in config["params"].items()})
            mlflow.log_params({f"best_{key}": value for key, value in best_params.items()})
            mlflow.log_params({"tuning_method": "GridSearchCV nested cross-validation",
                               "grid_candidates": _grid_size(config["param_grid"]), "test_size": TEST_SIZE,
                               "cv_folds_outer": CV_FOLDS, "cv_folds_inner": INNER_CV_FOLDS,
                               "random_state": RANDOM_STATE})
            mlflow.log_metric("best_inner_cv_roc_auc", float(grid.best_score_))
            mlflow.log_metrics(cv_metrics)
            mlflow.log_metrics({f"test_{key}": value for key, value in test_metrics.items()})
            for artifact in [cm_path, roc_path, feature_path, report_path, tuning_path]:
                if artifact and artifact.exists():
                    mlflow.log_artifact(str(artifact))
            mlflow.sklearn.log_model(best_pipeline, artifact_path="model", input_example=X_test.iloc[:2])

        row = {"Model": model_name, "Grid Size": _grid_size(config["param_grid"]),
               "Best Inner-CV AUC": round(float(grid.best_score_), 4), "Best Params": best_params_text,
               **{key.replace("cv_", "CV ").replace("_", " ").title(): round(value, 4)
                  for key, value in cv_metrics.items()},
               **{f"Test {key.replace('_', ' ').title()}": round(value, 4)
                  for key, value in test_metrics.items()}}
        results.append(row)
        tuning_rows.append({"Model": model_name, "Grid Size": _grid_size(config["param_grid"]),
                            "Best Inner-CV AUC": round(float(grid.best_score_), 4), "Best Params": best_params_text})

    results_df = pd.DataFrame(results).sort_values(by=["CV Roc Auc Mean", "CV Accuracy Mean"],
                                                   ascending=False).reset_index(drop=True)
    tuning_df = pd.DataFrame(tuning_rows).sort_values("Best Inner-CV AUC", ascending=False)
    for stem, frame in [("model_comparison", results_df), ("tuning_results", tuning_df)]:
        frame.to_csv(REPORTS_DIR / f"{stem}.csv", index=False)
        (REPORTS_DIR / f"{stem}.md").write_text(frame.to_markdown(index=False), encoding="utf-8")
    champion = str(results_df.iloc[0]["Model"])
    joblib.dump(fitted[champion], MODEL_ARTIFACT_PATH)
    selected = next(row for row in tuning_rows if row["Model"] == champion)
    metadata = {"best_model_name": champion,
                "selection_criterion": "Highest nested-CV ROC-AUC; tie-breaker nested-CV accuracy. "
                                       "Held-out test metrics are not used.",
                "best_params": json.loads(selected["Best Params"]), "metrics": results_df.iloc[0].to_dict(),
                "features": list(X.columns),
                "test_set_note": "GradientBoosting can have higher test accuracy but is not selected from test metrics."}
    (MODELS_DIR / "model_metadata.json").write_text(json.dumps(metadata, indent=2, default=str), encoding="utf-8")
    logger.info("Selected %s using nested-CV ROC-AUC", champion)
    return metadata


if __name__ == "__main__":
    train_and_track_experiments()
