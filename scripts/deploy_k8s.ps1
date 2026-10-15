# Kubernetes Deployment and Verification Script (PowerShell)
# Supports Minikube, Docker Desktop K8s, MicroK8s, Kind, or Cloud (GKE/EKS/AKS)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Heart Disease API: Kubernetes Deployment Walkthrough" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Step 1: Ensure image is available or load into minikube/kind
Write-Host "`n1. Building serving image..." -ForegroundColor Yellow
docker build -t heart-disease-api:latest .

# If minikube is running: minikube image load heart-disease-api:latest
# If kind is running: kind load docker-image heart-disease-api:latest

Write-Host "`n2. Applying Kubernetes Manifests..." -ForegroundColor Yellow
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

Write-Host "`n3. Checking rollout status..." -ForegroundColor Yellow
kubectl rollout status deployment/heart-disease-api --timeout=60s

Write-Host "`n4. Inspecting Pods, Services, and HPA..." -ForegroundColor Yellow
kubectl get pods -l app=heart-disease-api -o wide
kubectl get service heart-disease-service
kubectl get hpa heart-disease-hpa

Write-Host "`n5. Verifying In-Cluster Endpoint via port-forward..." -ForegroundColor Yellow
Write-Host "Run the following in a separate terminal to port-forward:"
Write-Host "  kubectl port-forward svc/heart-disease-service 8000:80" -ForegroundColor Cyan
Write-Host "Then execute:"
Write-Host "  python scripts/test_serving.py http://localhost:8000" -ForegroundColor Green
