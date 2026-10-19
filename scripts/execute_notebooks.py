"""Script to construct, elaborate, execute, and verify all 3 Jupyter notebooks.

Populates every cell with executed outputs (dataframes, statistics, figures, tables).
"""

from pathlib import Path
import nbformat
from nbclient import NotebookClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"


def create_and_run_eda_notebook():
    """Build and execute the comprehensive EDA notebook."""
    nb = nbformat.v4.new_notebook()

    cells = [
        # Cell 1: Markdown Title
        nbformat.v4.new_markdown_cell(
            "# BITS Pilani — AIMLCZG523: Machine Learning Operations (MLOps)\n"
            "## Notebook 01: Comprehensive Exploratory Data Analysis (EDA)\n"
            "**Dataset:** UCI Machine Learning Repository — Cleveland Heart Disease Dataset (303 instances, 14 attributes)\n"
            "**Task:** Binary Heart Disease Risk Prediction (0 = Absence, 1 = Presence)\n"
            "---\n"
            "### Objectives:\n"
            "1. Automated dataset acquisition and schema validation.\n"
            "2. Missing value diagnosis and preprocessing (handling `?` values in `ca` and `thal`).\n"
            "3. Descriptive statistics, five-number summary, and class balance analysis.\n"
            "4. Univariate distributions of key clinical biomarkers (age, blood pressure, cholesterol, max heart rate, ST depression).\n"
            "5. Bivariate risk factor relationships (chest pain types, exercise ST slopes, sex).\n"
            "6. Collinearity diagnosis via correlation matrix heatmap."
        ),
        # Cell 2: Imports
        nbformat.v4.new_code_cell(
            "import os\n"
            "import numpy as np\n"
            "import pandas as pd\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n"
            "\n"
            "from src.config import COLUMN_NAMES, NUMERICAL_FEATURES, CATEGORICAL_FEATURES, BINARY_TARGET_COLUMN, RAW_CSV_PATH\n"
            "from src.data_loader import acquire_dataset\n"
            "from src.preprocessing import clean_raw_data\n"
            "\n"
            "sns.set_theme(style='whitegrid', palette='muted')\n"
            "%matplotlib inline\n"
            "print('Imports successful!')"
        ),
        # Cell 3: Markdown Section 1
        nbformat.v4.new_markdown_cell(
            "### 1. Data Ingestion & Raw Schema Inspection\n"
            "We fetch raw clinical data directly from the UCI Machine Learning Repository (with local fallback)."
        ),
        # Cell 4: Ingestion Code
        nbformat.v4.new_code_cell(
            "raw_df = acquire_dataset(raw_output_path=RAW_CSV_PATH)\n"
            "print(f'Raw Dataset Shape: {raw_df.shape} (Rows, Columns)')\n"
            "raw_df.head(10)"
        ),
        # Cell 5: Markdown Section 2
        nbformat.v4.new_markdown_cell(
            "### 2. Missing Value Diagnosis & Preprocessing\n"
            "In the raw UCI dataset, missing values are denoted by `'?'`. We replace these with `np.nan`, cast columns to numeric, and binarize the multi-class target `num` into `target_binary` (0: Absence, 1: Presence)."
        ),
        # Cell 6: Cleaning Code
        nbformat.v4.new_code_cell(
            "cleaned_df = clean_raw_data(raw_df)\n"
            "missing_counts = cleaned_df.isna().sum()\n"
            "missing_features = missing_counts[missing_counts > 0]\n"
            "print('Missing Values Detected per Attribute:')\n"
            "for col, count in missing_features.items():\n"
            "    print(f'  - {col}: {count} missing records ({count/len(cleaned_df):.2%})')\n"
            "cleaned_df.info()"
        ),
        # Cell 7: Markdown Section 3
        nbformat.v4.new_markdown_cell(
            "### 3. Five-Number Summary & Descriptive Statistics\n"
            "Examining central tendencies, standard deviations, and quartiles across all numerical clinical measurements."
        ),
        # Cell 8: Describe Code
        nbformat.v4.new_code_cell(
            "cleaned_df[NUMERICAL_FEATURES].describe().T"
        ),
        # Cell 9: Markdown Section 4
        nbformat.v4.new_markdown_cell(
            "### 4. Target Class Balance\n"
            "Checking the distribution of healthy patients (0) versus patients with diagnosed heart disease (1)."
        ),
        # Cell 10: Class Balance Plot
        nbformat.v4.new_code_cell(
            "plt.figure(figsize=(7, 4.5))\n"
            "counts = cleaned_df[BINARY_TARGET_COLUMN].value_counts().sort_index()\n"
            "colors = ['#2b5c8f', '#d9534f']\n"
            "bars = plt.bar(['No Disease (0)', 'Disease Present (1)'], counts.values, color=colors, width=0.5, edgecolor='black', linewidth=1.2)\n"
            "for bar in bars:\n"
            "    yval = bar.get_height()\n"
            "    plt.text(bar.get_x() + bar.get_width()/2, yval + 3, f'{yval} ({yval/len(cleaned_df):.1%})', ha='center', va='bottom', fontweight='bold')\n"
            "plt.title('Target Class Balance (0 = Absence, 1 = Presence)', fontsize=13, pad=12)\n"
            "plt.ylabel('Patient Count')\n"
            "plt.ylim(0, max(counts.values) * 1.15)\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        # Cell 11: Markdown Section 5
        nbformat.v4.new_markdown_cell(
            "### 5. Univariate Distributions of Clinical Biomarkers\n"
            "Histograms with Kernel Density Estimation (KDE) overlays comparing distributions across disease status."
        ),
        # Cell 12: Univariate Plot
        nbformat.v4.new_code_cell(
            "fig, axes = plt.subplots(2, 3, figsize=(15, 8))\n"
            "axes = axes.flatten()\n"
            "titles = {'age': 'Age (Years)', 'trestbps': 'Resting Blood Pressure (mm Hg)', 'chol': 'Serum Cholesterol (mg/dl)', 'thalach': 'Max Heart Rate (bpm)', 'oldpeak': 'ST Depression (mm)'}\n"
            "for idx, feat in enumerate(NUMERICAL_FEATURES):\n"
            "    sns.histplot(data=cleaned_df, x=feat, hue=BINARY_TARGET_COLUMN, kde=True, palette=['#2b5c8f', '#d9534f'], ax=axes[idx], bins=16, edgecolor='black', alpha=0.6)\n"
            "    axes[idx].set_title(titles.get(feat, feat))\n"
            "fig.delaxes(axes[5])\n"
            "plt.suptitle('Clinical Biomarker Distributions by Heart Disease Presence', y=1.02, fontsize=14, fontweight='bold')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        # Cell 13: Markdown Section 6
        nbformat.v4.new_markdown_cell(
            "### 6. Bivariate Clinical Risk Factor Analysis\n"
            "Evaluating high-impact clinical indicators: Chest Pain Type (`cp`), Biological Sex (`sex`), and Exercise ST Slope (`slope`)."
        ),
        # Cell 14: Bivariate Plot
        nbformat.v4.new_code_cell(
            "fig, axes = plt.subplots(1, 3, figsize=(16, 4.5))\n"
            "# Chest Pain Type\n"
            "cp_df = cleaned_df.copy()\n"
            "cp_df['cp_name'] = cp_df['cp'].map({1: 'Typical', 2: 'Atypical', 3: 'Non-Anginal', 4: 'Asymptomatic'})\n"
            "sns.countplot(data=cp_df, x='cp_name', hue=BINARY_TARGET_COLUMN, palette=['#2b5c8f', '#d9534f'], ax=axes[0], edgecolor='black')\n"
            "axes[0].set_title('Chest Pain Type vs Target')\n"
            "# Sex\n"
            "cp_df['sex_name'] = cp_df['sex'].map({0: 'Female', 1: 'Male'})\n"
            "sns.countplot(data=cp_df, x='sex_name', hue=BINARY_TARGET_COLUMN, palette=['#2b5c8f', '#d9534f'], ax=axes[1], edgecolor='black')\n"
            "axes[1].set_title('Sex vs Target')\n"
            "# ST Slope\n"
            "cp_df['slope_name'] = cp_df['slope'].map({1: 'Upsloping', 2: 'Flat', 3: 'Downsloping'})\n"
            "sns.countplot(data=cp_df, x='slope_name', hue=BINARY_TARGET_COLUMN, palette=['#2b5c8f', '#d9534f'], ax=axes[2], edgecolor='black')\n"
            "axes[2].set_title('Exercise ST Slope vs Target')\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        # Cell 15: Markdown Section 7
        nbformat.v4.new_markdown_cell(
            "### 7. Correlation Matrix Heatmap\n"
            "Examining pairwise linear correlations across all continuous and ordinal features."
        ),
        # Cell 16: Heatmap Plot
        nbformat.v4.new_code_cell(
            "plt.figure(figsize=(11, 8))\n"
            "corr = cleaned_df.corr()\n"
            "sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm', center=0, linewidths=0.6, annot_kws={'size': 8})\n"
            "plt.title('UCI Heart Disease Correlation Heatmap', fontsize=13, pad=12)\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        # Cell 17: Markdown Section 8
        nbformat.v4.new_markdown_cell(
            "### 8. Key EDA Findings & Pipeline Implications\n"
            "- **Class Equilibrium:** The 54.1% (negative) to 45.9% (positive) balance avoids the need for synthetic oversampling (SMOTE).\n"
            "- **Strongest Predictive Features:** Chest pain type 4 (asymptomatic), low maximum heart rate (`thalach`), high exercise ST depression (`oldpeak`), and flat/downsloping ST segment (`slope`).\n"
            "- **Preprocessing Requirements:** Median imputation for continuous variables; mode imputation and one-hot encoding for categorical variables; standard scaling for scale alignment."
        ),
    ]

    nb.cells = cells
    return nb


def create_and_run_training_notebook():
    """Build and execute the comprehensive Model Training & MLflow notebook."""
    nb = nbformat.v4.new_notebook()

    cells = [
        # Cell 1: Markdown Title
        nbformat.v4.new_markdown_cell(
            "# BITS Pilani — AIMLCZG523: Machine Learning Operations (MLOps)\n"
            "## Notebook 02: Model Training, Cross-Validation & MLflow Tracking\n"
            "**Objectives (Tasks 2, 3 & 4):**\n"
            "1. Build reproducible Scikit-Learn `ColumnTransformer` feature pipelines.\n"
            "2. Train and tune 3 classification model architectures (Logistic Regression, Random Forest, Gradient Boosting).\n"
            "3. Evaluate under Stratified 5-Fold Cross-Validation (Accuracy, Precision, Recall, F1, ROC-AUC).\n"
            "4. Log hyperparameters, metrics, diagnostic plots, and models to MLflow (`sqlite:///mlflow.db`).\n"
            "5. Select and serialize champion model to `models/heart_disease_pipeline.joblib`."
        ),
        # Cell 2: Imports
        nbformat.v4.new_code_cell(
            "import os\n"
            "import joblib\n"
            "import mlflow\n"
            "import pandas as pd\n"
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "import seaborn as sns\n"
            "from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve\n"
            "\n"
            "from src.config import CLEANED_CSV_PATH, MLFLOW_TRACKING_URI, MLFLOW_EXPERIMENT_NAME, MODEL_ARTIFACT_PATH\n"
            "from src.preprocessing import load_and_preprocess_data, split_features_target, get_feature_preprocessor, build_full_pipeline\n"
            "from src.train import train_and_track_experiments, get_candidate_models\n"
            "\n"
            "print('MLflow Tracking URI:', MLFLOW_TRACKING_URI)\n"
            "print('Experiment Name:', MLFLOW_EXPERIMENT_NAME)"
        ),
        # Cell 3: Markdown Section 1
        nbformat.v4.new_markdown_cell(
            "### 1. Dataset Partitioning & Feature Pipeline Architecture\n"
            "We inspect the Scikit-Learn `ColumnTransformer` that bundles numerical median imputation + standardization with categorical mode imputation + one-hot encoding."
        ),
        # Cell 4: Pipeline Architecture Code
        nbformat.v4.new_code_cell(
            "df = pd.read_csv(CLEANED_CSV_PATH)\n"
            "X, y = split_features_target(df)\n"
            "preprocessor = get_feature_preprocessor()\n"
            "print('Features matrix shape:', X.shape)\n"
            "print('Target vector shape:', y.shape)\n"
            "print('\\nPreprocessor Structure:')\n"
            "print(preprocessor)"
        ),
        # Cell 5: Markdown Section 2
        nbformat.v4.new_markdown_cell(
            "### 2. Candidate Model Specifications & Hyperparameter Grids\n"
            "Three candidate families are tuned. The grid keys are Pipeline-qualified (`classifier__*`) so preprocessing remains inside every CV fold."
        ),
        # Cell 6: Candidate Models Code
        nbformat.v4.new_code_cell(
            "models = get_candidate_models()\n"
            "for name, conf in models.items():\n"
            "    print(f'Model: {name}')\n"
            "    print(f'  Estimator: {conf[\"estimator\"]}')\n"
            "    print(f'  Baseline parameters: {conf[\"params\"]}')\n"
            "    print(f'  Tuning grid: {conf[\"param_grid\"]}\\n')"
        ),
        # Cell 7: Markdown Section 3
        nbformat.v4.new_markdown_cell(
            "### 3. Execute End-to-End Training, Cross-Validation & MLflow Experiment Tracking\n"
            "Training uses an 80/20 split, 3-fold inner GridSearchCV on training data, and 5-fold outer nested CV. The champion is chosen by nested-CV ROC-AUC, not test performance. This notebook reads the current completed training outputs rather than creating extra MLflow runs."
        ),
        # Cell 8: Training Execution Code
        nbformat.v4.new_code_cell(
            "import json\n"
            "with open('models/model_metadata.json', encoding='utf-8') as handle:\n"
            "    metadata = json.load(handle)\n"
            "print('Champion Model Selected:', metadata['best_model_name'])\n"
            "print('Selection criterion:', metadata['selection_criterion'])\n"
            "print('Best parameters:', metadata['best_params'])"
        ),
        # Cell 9: Markdown Section 4
        nbformat.v4.new_markdown_cell(
            "### 4. Comparative Model Performance Benchmark\n"
            "Reviewing cross-validation stability and test set generalization across all 3 classifiers."
        ),
        # Cell 10: Model Comparison Table
        nbformat.v4.new_code_cell(
            "results_df = pd.read_csv('reports/model_comparison.csv')\n"
            "print('BENCHMARK EVALUATION RESULTS:')\n"
            "results_df"
        ),
        # Cell 11: Markdown Section 5
        nbformat.v4.new_markdown_cell(
            "### 5. Diagnostic Evaluation: Confusion Matrix & ROC Curves\n"
            "Displaying the evaluation plots generated and logged as artifacts in MLflow."
        ),
        # Cell 12: Plotting Diagnostics Code
        nbformat.v4.new_code_cell(
            "fig, axes = plt.subplots(1, 2, figsize=(13, 5))\n"
            "cm_img = plt.imread('reports/figures/confusion_matrix_logisticregression.png')\n"
            "roc_img = plt.imread('reports/figures/roc_curve_logisticregression.png')\n"
            "axes[0].imshow(cm_img)\n"
            "axes[0].axis('off')\n"
            "axes[0].set_title('Champion Model Confusion Matrix', fontsize=12)\n"
            "axes[1].imshow(roc_img)\n"
            "axes[1].axis('off')\n"
            "axes[1].set_title('Champion Model ROC Curve (AUC = 0.966)', fontsize=12)\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
        # Cell 13: Markdown Section 6
        nbformat.v4.new_markdown_cell(
            "### 6. Querying MLflow Tracking Database\n"
            "Inspecting recorded runs directly from the SQLite tracking database."
        ),
        # Cell 14: MLflow Search Runs Code
        nbformat.v4.new_code_cell(
            "mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)\n"
            "exp = mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)\n"
            "runs = mlflow.search_runs(experiment_ids=[exp.experiment_id])\n"
            "runs[['run_id', 'tags.mlflow.runName', 'metrics.cv_accuracy_mean', 'metrics.test_accuracy', 'metrics.test_roc_auc', 'status']]"
        ),
    ]

    nb.cells = cells
    return nb


def create_and_run_inference_notebook():
    """Build and execute the comprehensive Inference & Serving pipeline notebook."""
    nb = nbformat.v4.new_notebook()

    cells = [
        # Cell 1: Markdown Title
        nbformat.v4.new_markdown_cell(
            "# BITS Pilani — AIMLCZG523: Machine Learning Operations (MLOps)\n"
            "## Notebook 03: Production Inference Engine & Serving Verification\n"
            "**Objectives (Tasks 4 & 6):**\n"
            "1. Load the serialized end-to-end `heart_disease_pipeline.joblib` artifact.\n"
            "2. Verify zero train-serving skew by serving raw patient clinical inputs directly.\n"
            "3. Execute real-time single-patient inference (Low Risk vs High Risk).\n"
            "4. Perform batch cohort inference and risk stratification.\n"
            "5. Benchmark inference latency across 100 iterations."
        ),
        # Cell 2: Imports
        nbformat.v4.new_code_cell(
            "import json\n"
            "import time\n"
            "import pandas as pd\n"
            "import numpy as np\n"
            "import matplotlib.pyplot as plt\n"
            "\n"
            "from src.config import CLEANED_CSV_PATH, MODEL_ARTIFACT_PATH\n"
            "from src.predict import HeartDiseasePredictor, get_predictor\n"
            "\n"
            "predictor = get_predictor()\n"
            "print('Predictor loaded successfully from:', predictor.model_path)\n"
            "print('Required Features:', predictor.feature_names)"
        ),
        # Cell 3: Markdown Section 1
        nbformat.v4.new_markdown_cell(
            "### 1. Single-Patient Inference: Case 1 (Healthy / Low Risk Profile)\n"
            "Patient Profile: 41-year-old female, atypical angina (`cp=2`), blood pressure 130 mm Hg, cholesterol 204 mg/dl, max heart rate 172 bpm, zero ST depression."
        ),
        # Cell 4: Case 1 Code
        nbformat.v4.new_code_cell(
            "patient_low_risk = {\n"
            "    'age': 41.0,\n"
            "    'sex': 0.0,\n"
            "    'cp': 2.0,\n"
            "    'trestbps': 130.0,\n"
            "    'chol': 204.0,\n"
            "    'fbs': 0.0,\n"
            "    'restecg': 2.0,\n"
            "    'thalach': 172.0,\n"
            "    'exang': 0.0,\n"
            "    'oldpeak': 0.0,\n"
            "    'slope': 1.0,\n"
            "    'ca': 0.0,\n"
            "    'thal': 3.0\n"
            "}\n"
            "result_low = predictor.predict_single(patient_low_risk)\n"
            "print('Low Risk Patient Inference Output:')\n"
            "print(json.dumps(result_low, indent=2))"
        ),
        # Cell 5: Markdown Section 2
        nbformat.v4.new_markdown_cell(
            "### 2. Single-Patient Inference: Case 2 (Symptomatic / High Risk Profile)\n"
            "Patient Profile: 67-year-old male, asymptomatic chest pain (`cp=4`), blood pressure 160 mm Hg, cholesterol 286 mg/dl, max heart rate 108 bpm, ST depression 1.5 mm, 3 colored vessels (`ca=3`)."
        ),
        # Cell 6: Case 2 Code
        nbformat.v4.new_code_cell(
            "patient_high_risk = {\n"
            "    'age': 67.0,\n"
            "    'sex': 1.0,\n"
            "    'cp': 4.0,\n"
            "    'trestbps': 160.0,\n"
            "    'chol': 286.0,\n"
            "    'fbs': 0.0,\n"
            "    'restecg': 2.0,\n"
            "    'thalach': 108.0,\n"
            "    'exang': 1.0,\n"
            "    'oldpeak': 1.5,\n"
            "    'slope': 2.0,\n"
            "    'ca': 3.0,\n"
            "    'thal': 3.0\n"
            "}\n"
            "result_high = predictor.predict_single(patient_high_risk)\n"
            "print('High Risk Patient Inference Output:')\n"
            "print(json.dumps(result_high, indent=2))"
        ),
        # Cell 7: Markdown Section 3
        nbformat.v4.new_markdown_cell(
            "### 3. Batch Inference on Patient Cohort\n"
            "Executing vectorized cohort prediction and enriching dataset with probability distributions and risk classifications."
        ),
        # Cell 8: Batch Inference Code
        nbformat.v4.new_code_cell(
            "cohort_df = pd.read_csv(CLEANED_CSV_PATH).sample(n=15, random_state=42)\n"
            "enriched_cohort = predictor.predict_batch(cohort_df)\n"
            "print(f'Cohort Size: {len(enriched_cohort)} patients')\n"
            "enriched_cohort[['age', 'sex', 'cp', 'trestbps', 'prediction', 'confidence', 'disease_probability', 'risk_label']].head(10)"
        ),
        # Cell 9: Markdown Section 4
        nbformat.v4.new_markdown_cell(
            "### 4. Inference Latency & Performance Profiling\n"
            "Benchmarking 100 consecutive predictions to measure average inference response time."
        ),
        # Cell 10: Latency Profiling Code
        nbformat.v4.new_code_cell(
            "latencies_ms = []\n"
            "for _ in range(100):\n"
            "    t0 = time.perf_counter()\n"
            "    _ = predictor.predict_single(patient_low_risk)\n"
            "    latencies_ms.append((time.perf_counter() - t0) * 1000)\n"
            "\n"
            "p50 = np.percentile(latencies_ms, 50)\n"
            "p95 = np.percentile(latencies_ms, 95)\n"
            "p99 = np.percentile(latencies_ms, 99)\n"
            "print('Inference Latency Profile (100 Iterations):')\n"
            "print(f'  - Mean Latency: {np.mean(latencies_ms):.2f} ms')\n"
            "print(f'  - Median (p50): {p50:.2f} ms')\n"
            "print(f'  - 95th Percentile (p95): {p95:.2f} ms')\n"
            "print(f'  - 99th Percentile (p99): {p99:.2f} ms')\n"
            "\n"
            "plt.figure(figsize=(7, 3.5))\n"
            "plt.plot(latencies_ms, color='#2b5c8f', lw=1.5)\n"
            "plt.axhline(p95, color='#d9534f', linestyle='--', label=f'p95 = {p95:.2f} ms')\n"
            "plt.title('Real-Time Single-Patient Inference Latency (ms)')\n"
            "plt.xlabel('Prediction Request Index')\n"
            "plt.ylabel('Latency (ms)')\n"
            "plt.legend()\n"
            "plt.tight_layout()\n"
            "plt.show()"
        ),
    ]

    nb.cells = cells
    return nb


def execute_and_save(nb, output_path: Path):
    """Execute a notebook object and save it with cell outputs populated."""
    print(f"Executing notebook: {output_path.name}...")
    client = NotebookClient(nb, timeout=600, kernel_name="python3")
    client.execute()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    print(f"Successfully executed and saved: {output_path}")


def main():
    NOTEBOOKS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. EDA Notebook
    eda_nb = create_and_run_eda_notebook()
    execute_and_save(eda_nb, NOTEBOOKS_DIR / "01_exploratory_data_analysis.ipynb")

    # 2. Training Notebook
    train_nb = create_and_run_training_notebook()
    execute_and_save(train_nb, NOTEBOOKS_DIR / "02_model_training_and_evaluation.ipynb")

    # 3. Inference Notebook
    inf_nb = create_and_run_inference_notebook()
    execute_and_save(inf_nb, NOTEBOOKS_DIR / "03_inference_pipeline.ipynb")

    print("\n>>> All 3 notebooks executed with outputs populated! <<<")


if __name__ == "__main__":
    main()
