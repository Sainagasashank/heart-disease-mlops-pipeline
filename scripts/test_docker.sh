#!/usr/bin/env bash
# Shell script to build and test Docker container locally
set -e

IMAGE_NAME="heart-disease-api:latest"
CONTAINER_NAME="heart-disease-serving"

echo "=========================================================="
echo " Building Docker image: ${IMAGE_NAME}..."
echo "=========================================================="
docker build -t ${IMAGE_NAME} .

echo "=========================================================="
echo " Starting container: ${CONTAINER_NAME} on port 8000..."
echo "=========================================================="
docker rm -f ${CONTAINER_NAME} 2>/dev/null || true
docker run -d -p 8000:8000 --name ${CONTAINER_NAME} ${IMAGE_NAME}

echo "Waiting for container warmup..."
sleep 6

echo "=========================================================="
echo " Testing endpoints via test_serving.py..."
echo "=========================================================="
python scripts/test_serving.py http://localhost:8000

echo "Container logs:"
docker logs --tail 20 ${CONTAINER_NAME}

echo "Stopping container..."
docker rm -f ${CONTAINER_NAME}
echo "Docker verification completed successfully!"
