"""Generate evidence-based 10-page PDF and DOCX assignment reports."""

import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from docx import Document
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parent.parent
REPORTS, FIGURES, SHOTS, MODELS = ROOT / "reports", ROOT / "reports" / "figures", ROOT / "reports" / "screenshots", ROOT / "models"
PDF, DOCX, ARCHITECTURE = REPORTS / "MLOps_Assignment_1_Report.pdf", REPORTS / "MLOps_Assignment_1_Report.docx", REPORTS / "architecture.png"


def _identity(name: str) -> str:
    return os.getenv(name, "TO BE FILLED")


def _data():
    comparison = pd.read_csv(REPORTS / "model_comparison.csv")
    tuning = pd.read_csv(REPORTS / "tuning_results.csv")
    metadata = json.loads((MODELS / "model_metadata.json").read_text(encoding="utf-8"))
    return comparison, tuning, metadata


def _architecture() -> None:
    fig, ax = plt.subplots(figsize=(10, 2.4))
    ax.axis("off")
    nodes = [(0.04, "UCI data"), (0.23, "Pipeline +\nnested CV"), (0.43, "MLflow\nSQLite"),
             (0.62, "FastAPI\n/predict /metrics"), (0.82, "Prometheus\nGrafana")]
    for x, text in nodes:
        ax.text(x, .5, text, ha="center", va="center", fontsize=10, bbox={"boxstyle": "round,pad=.5", "fc": "#e8f0fe", "ec": "#285a9f"})
    for x in [.135, .325, .525, .725]:
        ax.annotate("", xy=(x + .07, .5), xytext=(x, .5), arrowprops={"arrowstyle": "->", "lw": 1.5})
    fig.tight_layout()
    fig.savefig(ARCHITECTURE, dpi=160)
    plt.close(fig)


def _table(frame: pd.DataFrame, style: ParagraphStyle) -> Table:
    values = [list(frame.columns)] + [[str(value)[:44] for value in row] for row in frame.astype(object).values]
    table = Table(values, repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a365d")),
                               ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("GRID", (0, 0), (-1, -1), .25, colors.grey),
                               ("FONTSIZE", (0, 0), (-1, -1), 6.6), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f8fc")])]))
    return table


def build_pdf_report() -> None:
    REPORTS.mkdir(exist_ok=True)
    _architecture()
    comparison, tuning, metadata = _data()
    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"], textColor=colors.HexColor("#1a365d"), leading=25)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=9, leading=13, spaceAfter=6)
    head = ParagraphStyle("head", parent=styles["Heading1"], textColor=colors.HexColor("#1a365d"), fontSize=15)
    story = []

    pages = [
        ("AIMLCZG523 MLOps Assignment 01", [
            "End-to-End Reproducible Heart Disease Prediction Pipeline", f"Student name: {_identity('REPORT_STUDENT_NAME')}",
            f"Roll number: {_identity('REPORT_STUDENT_ID')}", f"Email: {_identity('REPORT_STUDENT_EMAIL')}",
            f"Repository: {_identity('REPO_URL')}", "This report is generated from the current model outputs and evidence files."]),
        ("1. Setup and installation", ["Create a clean Python 3.12 virtual environment, then run <code>pip install -r requirements-dev.txt</code>.",
            "Primary commands: <code>make data</code>, <code>make train</code>, <code>make test</code>, <code>make serve</code>.",
            "Container workflow: <code>make docker-build</code> then <code>make docker-run</code>. Kubernetes and Helm commands are provided for an owner-operated cluster.",
            "Monitoring: <code>make monitoring-up</code>; use <code>make traffic</code> to generate requests."]),
        ("2. EDA and preprocessing", ["The Cleveland dataset has 303 records. Raw '?' values are converted to missing values.",
            "Numerical variables use median imputation and standard scaling; categorical variables use most-frequent imputation and one-hot encoding. The same Pipeline is saved and served, avoiding training-serving skew."]),
        ("3. Model selection and nested tuning", ["Three candidates are tuned with GridSearchCV on an 80% training split. A 3-fold inner CV selects parameters within each outer fold; five outer folds estimate generalization. The held-out 20% test split is evaluated once.",
            f"Champion: <b>{metadata['best_model_name']}</b>. Selection criterion: {metadata['selection_criterion']}"]),
        ("4. Experiment tracking", ["MLflow records baseline and best parameters, inner-CV and test metrics, figures, reports, tuning result CSVs and the input-example model artifact.",
            "Run <code>python scripts/relocate_mlflow.py</code> before <code>make mlflow-ui</code> after moving the project. The script makes artifact locations portable."]),
        ("5. Quality assurance and CI/CD", ["Pytest covers cleaning, preprocessing, grid validity, metrics, model inference, API validation/determinism and Prometheus metrics. Flake8 is enforced without exit-zero.",
            "GitHub Actions and Jenkins use Python 3.12, run lint/test/coverage, train artifacts, and use a health polling loop before the container prediction smoke test."]),
        ("6. Serving and deployment", ["FastAPI exposes /health, /predict, /metrics and /docs. Input contracts reject invalid payloads. The Dockerfile uses python:3.12-slim, pinned requirements, a non-root user and curl health check.",
            "Kubernetes manifests and the Helm chart are supplied. Their execution is owner-operated and should be evidenced on the target cluster."]),
        ("7. Monitoring and logging", ["The compose stack runs API, Prometheus and Grafana. Prometheus scrapes api:8000 in compose; prometheus.local.yml is for a host-running API. Grafana provisioning supplies a default Prometheus datasource.",
            "The API emits REQUEST_LOG and PREDICTION_RESULT lines, exposes request metrics, a prediction-outcome counter, and an inference latency histogram."]),
        ("8. Evidence and limitations", ["Embedded screenshots are used only when the corresponding captured PNG exists. Docker, Kubernetes, GitHub Actions and Grafana execution are procedures until run by the owner.",
            "No claim of image size, cluster deployment, or container endpoint success is made without a captured local run."]),
        ("9. Repository link and conclusion", [f"Repository URL: {_identity('REPO_URL')}",
            "The project provides reproducible specifications, nested-CV selection, portable experiment metadata, testing, CI/CD definitions, container/deployment manifests and monitoring configuration. Owner tasks: fill identity/repository details, execute external platforms, record video and upload the repository."]),
    ]
    for index, (heading, paragraphs) in enumerate(pages):
        story.append(Paragraph(heading, title if index == 0 else head))
        if index == 0:
            story.append(Spacer(1, .15 * inch)); story.append(Image(str(ARCHITECTURE), width=6.7 * inch, height=1.6 * inch))
        if index == 3:
            story.append(_table(tuning, body))
            story.append(Spacer(1, 8)); story.append(_table(comparison, body))
        for paragraph in paragraphs:
            story.append(Paragraph(paragraph, body))
        for filename in ["03_mlflow_experiment_runs.png", "04_pytest_results.png", "06_api_swagger_docs.png", "08_prometheus_targets.png"]:
            image = SHOTS / filename
            if image.exists() and index in (4, 5, 6, 7):
                story.append(Image(str(image), width=5.7 * inch, height=3.2 * inch))
        if index < len(pages) - 1:
            story.append(PageBreak())
    SimpleDocTemplate(str(PDF), pagesize=letter, leftMargin=45, rightMargin=45, topMargin=45, bottomMargin=42).build(story)


def build_docx_report() -> None:
    comparison, tuning, metadata = _data()
    document = Document()
    document.add_heading("AIMLCZG523 MLOps Assignment 01", 0)
    document.add_paragraph(f"Student: {_identity('REPORT_STUDENT_NAME')} | ID: {_identity('REPORT_STUDENT_ID')} | Repo: {_identity('REPO_URL')}")
    for heading, content in [("Modelling", metadata["selection_criterion"]), ("Tuning results", tuning.to_markdown(index=False)),
                             ("Comparison", comparison.to_markdown(index=False)), ("Setup", "pip install -r requirements-dev.txt; make data train test serve"),
                             ("Monitoring", "make monitoring-up; make traffic"), ("Owner tasks", "Run external platform deployment/evidence and fill identity details.")]:
        document.add_page_break(); document.add_heading(heading, 1); document.add_paragraph(content)
    document.save(str(DOCX))


if __name__ == "__main__":
    build_pdf_report()
    build_docx_report()
    print(f"Generated {PDF} and {DOCX}")
