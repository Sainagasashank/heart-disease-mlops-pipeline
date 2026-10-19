# Evidence index

Files in this folder are only real captures from local commands. When present, their names map to assignment evidence:

- `03_mlflow_experiment_runs.png` — MLflow experiment run list.
- `03b_mlflow_run_params_metrics.png` — parameters and metrics for a run.
- `03c_mlflow_run_artifacts.png` — MLflow run artifacts.
- `03d_mlflow_compare_runs.png` — comparison view.
- `04_pytest_results.png`, `04b_flake8_lint.png` — terminal-style renders of captured command output.
- `06_api_swagger_docs.png`, `06b_api_predict_response.png`, `06c_serving_verification.png` — running API documentation, request, and smoke check.
- `08_prometheus_targets.png`, `08b_prometheus_request_rate.png`, `08c_prometheus_predictions_by_outcome.png`, `08d_prometheus_latency_p95.png`, `08e_api_request_logs.png` — Prometheus and API-log evidence.

## TO CAPTURE ON OWNER'S MACHINE

The following are intentionally not fabricated. Run these on the target machine and save the stated file names here:

- `05_github_actions_run.png`: push the project, open the successful GitHub Actions run.
- `06d_docker_build_run.png`: run `make docker-build`, `make docker-run`, then `make docker-test`.
- `07_kubernetes_deployment.png`: run `kubectl get pods,svc,hpa` after `helm install heart-disease helm/heart-disease-api`.
- `08f_grafana_dashboard.png`: run `make monitoring-up`, run `make traffic`, then open Grafana at `http://localhost:3000` (admin/admin).
