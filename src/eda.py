"""Exploratory Data Analysis (EDA) module for UCI Heart Disease Dataset.

Generates professional visualizations including:
1. Target class balance plot
2. Numerical feature distributions (histograms + KDE)
3. Full correlation heatmap
4. Clinical risk factor comparisons (chest pain, ST slope, sex vs. heart disease)
"""

import logging
from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import seaborn as sns  # noqa: E402

from src.config import (  # noqa: E402
    BINARY_TARGET_COLUMN,
    CLEANED_CSV_PATH,
    FIGURES_DIR,
    NUMERICAL_FEATURES,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Set publication-quality style
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 11,
    "figure.titlesize": 16,
})


def plot_class_balance(df: pd.DataFrame, output_dir: Path = FIGURES_DIR) -> Path:
    """Generate and save the binary target class balance bar chart."""
    fig, ax = plt.subplots(figsize=(7, 5))
    counts = df[BINARY_TARGET_COLUMN].value_counts().sort_index()
    labels = ["No Disease (0)", "Disease Present (1)"]
    colors = ["#2b5c8f", "#d9534f"]

    bars = ax.bar(labels, counts.values, color=colors, width=0.55, edgecolor="black", linewidth=1.2)
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            f"{height} ({height / len(df):.1%})",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontweight="bold",
        )

    ax.set_title("UCI Heart Disease Dataset: Target Class Distribution", pad=15)
    ax.set_ylabel("Patient Count")
    ax.set_ylim(0, max(counts.values) * 1.15)
    plt.tight_layout()

    out_path = output_dir / "class_balance.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info(f"Class balance plot saved to {out_path}")
    return out_path


def plot_feature_distributions(df: pd.DataFrame, output_dir: Path = FIGURES_DIR) -> Path:
    """Generate histograms with KDE overlays for all numerical features."""
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    axes = axes.flatten()

    feature_titles = {
        "age": "Age (years)",
        "trestbps": "Resting Blood Pressure (mm Hg)",
        "chol": "Serum Cholesterol (mg/dl)",
        "thalach": "Maximum Heart Rate Achieved (bpm)",
        "oldpeak": "ST Depression (exercise vs rest)",
    }

    for idx, feature in enumerate(NUMERICAL_FEATURES):
        ax = axes[idx]
        sns.histplot(
            data=df,
            x=feature,
            hue=BINARY_TARGET_COLUMN,
            kde=True,
            palette=["#2b5c8f", "#d9534f"],
            ax=ax,
            bins=18,
            edgecolor="black",
            alpha=0.6,
        )
        ax.set_title(feature_titles.get(feature, feature))
        ax.set_xlabel("")
        ax.set_ylabel("Count")

    # Remove extra subplot
    fig.delaxes(axes[5])

    plt.suptitle("Univariate Distributions of Key Numerical Clinical Features", y=1.01)
    plt.tight_layout()

    out_path = output_dir / "feature_distributions.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Feature distributions plot saved to {out_path}")
    return out_path


def plot_correlation_heatmap(df: pd.DataFrame, output_dir: Path = FIGURES_DIR) -> Path:
    """Generate full correlation matrix heatmap."""
    fig, ax = plt.subplots(figsize=(11, 9))
    corr = df.corr()

    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        linewidths=0.7,
        cbar_kws={"shrink": 0.8},
        ax=ax,
        annot_kws={"size": 8},
    )

    ax.set_title("UCI Heart Disease: Feature Correlation Matrix Heatmap", pad=15)
    plt.tight_layout()

    out_path = output_dir / "correlation_heatmap.png"
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
    logger.info(f"Correlation heatmap saved to {out_path}")
    return out_path


def plot_clinical_comparisons(df: pd.DataFrame, output_dir: Path = FIGURES_DIR) -> Path:
    """Generate risk factor comparisons: Chest Pain, ST Slope, and Sex vs Disease."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # 1. Chest Pain Type vs Target
    cp_labels = {1: "Typical\nAngina", 2: "Atypical\nAngina", 3: "Non-anginal\nPain", 4: "Asymptomatic"}
    temp_df = df.copy()
    temp_df["cp_label"] = temp_df["cp"].map(cp_labels)
    sns.countplot(
        data=temp_df,
        x="cp_label",
        hue=BINARY_TARGET_COLUMN,
        palette=["#2b5c8f", "#d9534f"],
        ax=axes[0],
        edgecolor="black",
    )
    axes[0].set_title("Chest Pain Type vs Heart Disease")
    axes[0].set_xlabel("")
    axes[0].set_ylabel("Patient Count")

    # 2. Sex vs Target
    sex_labels = {0: "Female", 1: "Male"}
    temp_df["sex_label"] = temp_df["sex"].map(sex_labels)
    sns.countplot(
        data=temp_df,
        x="sex_label",
        hue=BINARY_TARGET_COLUMN,
        palette=["#2b5c8f", "#d9534f"],
        ax=axes[1],
        edgecolor="black",
    )
    axes[1].set_title("Sex vs Heart Disease")
    axes[1].set_xlabel("")
    axes[1].set_ylabel("Patient Count")

    # 3. ST Slope vs Target
    slope_labels = {1: "Upsloping", 2: "Flat", 3: "Downsloping"}
    temp_df["slope_label"] = temp_df["slope"].map(slope_labels)
    sns.countplot(
        data=temp_df,
        x="slope_label",
        hue=BINARY_TARGET_COLUMN,
        palette=["#2b5c8f", "#d9534f"],
        ax=axes[2],
        edgecolor="black",
    )
    axes[2].set_title("Exercise ST Slope vs Heart Disease")
    axes[2].set_xlabel("")
    axes[2].set_ylabel("Patient Count")

    plt.suptitle("Clinical Risk Factor Breakdown by Heart Disease Presence", y=1.02)
    plt.tight_layout()

    out_path = output_dir / "clinical_comparisons.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    logger.info(f"Clinical comparisons plot saved to {out_path}")
    return out_path


def run_eda(cleaned_data_path: Path = CLEANED_CSV_PATH) -> None:
    """Execute full EDA suite and generate all visualization artifacts."""
    if not cleaned_data_path.exists():
        from src.preprocessing import load_and_preprocess_data
        df = load_and_preprocess_data()
    else:
        df = pd.read_csv(cleaned_data_path)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Executing EDA visualizations...")
    plot_class_balance(df)
    plot_feature_distributions(df)
    plot_correlation_heatmap(df)
    plot_clinical_comparisons(df)
    logger.info("EDA completed successfully! Visualizations saved to reports/figures/")


if __name__ == "__main__":
    run_eda()
