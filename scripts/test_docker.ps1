# PowerShell script to build and test Docker container locally
$ErrorActionPreference = "Stop"

$IMAGE_NAME = "heart-disease-api:latest"
$CONTAINER_NAME = "heart-disease-serving"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Building Docker image: $IMAGE_NAME..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
docker build -t $IMAGE_NAME .

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Starting container: $CONTAINER_NAME on port 8000..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
docker rm -f $CONTAINER_NAME 2>$null | Out-Null
docker run -d -p 8000:8000 --name $CONTAINER_NAME $IMAGE_NAME

Write-Host "Waiting 6 seconds for container warmup..."
Start-Sleep -Seconds 6

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " Testing endpoints via test_serving.py..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
python scripts/test_serving.py http://localhost:8000

Write-Host "Container logs:" -ForegroundColor Yellow
docker logs --tail 20 $CONTAINER_NAME

Write-Host "Stopping container..."
docker rm -f $CONTAINER_NAME | Out-Null
Write-Host "Docker verification completed successfully!" -ForegroundColor Green
