#!/usr/bin/env bash
# Shell script to deploy and verify Kubernetes manifests
set -e

echo "=========================================================="
echo " Heart Disease API: Kubernetes Deployment Walkthrough"
echo "=========================================================="

# Build image
docker build -t heart-disease-api:latest .

# If using minikube: minikube image load heart-disease-api:latest
# If using kind: kind load docker-image heart-disease-api:latest

# Apply manifests
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl apply -f k8s/hpa.yaml

# Rollout status
kubectl rollout status deployment/heart-disease-api --timeout=60s

# Inspect
kubectl get pods -l app=heart-disease-api -o wide
kubectl get service heart-disease-service
kubectl get hpa heart-disease-hpa

echo "Deployment successful! Forward port to test:"
echo "kubectl port-forward svc/heart-disease-service 8000:80"
