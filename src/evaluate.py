"""Evaluation and metric plotting module for Heart Disease Classification models."""

import logging
from pathlib import Path
from typing import Any, Dict, Tuple
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import seaborn as sns  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from src.config import FIGURES_DIR  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> Dict[str, float]:
    """Compute comprehensive classification evaluation metrics.

    Args:
        y_true: Ground truth binary labels.
        y_pred: Predicted binary labels.
        y_prob: Predicted probability for positive class.

    Returns:
        Dict[str, float]: Dictionary of computed metric values.
    """
    metrics = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, y_prob)),
    }
    return metrics


def plot_confusion_matrix(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    model_name: str,
    output_dir: Path = FIGURES_DIR
) -> Path:
    """Generate and persist confusion matrix heatmap.

    Args:
        y_true: Ground truth labels.
        y_pred: Predicted labels.
        model_name: Identifier for the model.
        output_dir: Directory where the plot will be saved.

    Returns:
        Path: Path to the generated plot image.
    """
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        cbar=False,
        xticklabels=["No Disease (0)", "Disease (1)"],
        yticklabels=["No Disease (0)", "Disease (1)"],
        ax=ax,
        annot_kws={"size": 13, "weight": "bold"},
    )
    ax.set_title(f"Confusion Matrix: {model_name}", pad=12)
    ax.set_xlabel("Predicted Label")
    ax.set_ylabel("True Label")
    plt.tight_layout()

    out_path = output_dir / f"confusion_matrix_{model_name.lower().replace(' ', '_')}.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path


def plot_roc_curve(
    y_true: np.ndarray,
    y_prob: np.ndarray,
    model_name: str,
    output_dir: Path = FIGURES_DIR
) -> Tuple[Path, float]:
    """Generate and persist ROC curve plot.

    Args:
        y_true: Ground truth labels.
        y_prob: Predicted probabilities for positive class.
        model_name: Identifier for the model.
        output_dir: Destination directory.

    Returns:
        Tuple[Path, float]: (Plot path, calculated AUC value)
    """
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    auc_val = float(roc_auc_score(y_true, y_prob))

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, color="#2b5c8f", lw=2.5, label=f"{model_name} (AUC = {auc_val:.3f})")
    ax.plot([0, 1], [0, 1], color="grey", lw=1.5, linestyle="--", label="Random Classifier")
    ax.set_xlim([-0.02, 1.02])
    ax.set_ylim([-0.02, 1.05])
    ax.set_xlabel("False Positive Rate (1 - Specificity)")
    ax.set_ylabel("True Positive Rate (Sensitivity)")
    ax.set_title(f"ROC Curve: {model_name}", pad=12)
    ax.legend(loc="lower right")
    plt.tight_layout()

    out_path = output_dir / f"roc_curve_{model_name.lower().replace(' ', '_')}.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path, auc_val


def plot_feature_importance(
    pipeline: Any,
    model_name: str,
    output_dir: Path = FIGURES_DIR
) -> Path:
    """Extract and plot feature importances or model coefficients.

    Args:
        pipeline: Trained Scikit-learn Pipeline.
        model_name: Identifier for the model.
        output_dir: Output directory.

    Returns:
        Path: Path to saved plot.
    """
    classifier = pipeline.named_steps["classifier"]
    preprocessor = pipeline.named_steps["preprocessor"]

    feature_names = []
    try:
        feature_names = preprocessor.get_feature_names_out()
    except Exception:
        feature_names = [f"feat_{i}" for i in range(25)]

    importance_values = None
    title = f"Feature Importance: {model_name}"

    if hasattr(classifier, "feature_importances_"):
        importance_values = classifier.feature_importances_
    elif hasattr(classifier, "coef_"):
        importance_values = np.abs(classifier.coef_[0])
        title = f"Absolute Feature Coefficients: {model_name}"

    if importance_values is None or len(importance_values) != len(feature_names):
        return None

    # Sort top 15 features
    indices = np.argsort(importance_values)[::-1][:15]
    top_features = [feature_names[i] for i in indices]
    top_values = [importance_values[i] for i in indices]

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(x=top_values, y=top_features, hue=top_features, palette="viridis", legend=False, ax=ax)
    ax.set_title(title, pad=12)
    ax.set_xlabel("Importance Metric")
    plt.tight_layout()

    out_path = output_dir / f"feature_importance_{model_name.lower().replace(' ', '_')}.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    return out_path
