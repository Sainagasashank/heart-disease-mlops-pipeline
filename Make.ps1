<#
PowerShell equivalent of the Makefile for Windows hosts without GNU Make.
Usage: .\Make.ps1 train   (or `make train` after running setup_make_command.ps1)
#>
[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Target = "help"
)

$ErrorActionPreference = "Stop"
# MLflow writes non-fatal security notices to stderr. In PowerShell 7, do not
# convert native-program stderr into a terminating PowerShell exception.
$PSNativeCommandUseErrorActionPreference = $false
$ProjectRoot = Split-Path -Parent $PSCommandPath
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$LocalPython312 = Join-Path $ProjectRoot ".python312\python.exe"
$FallbackPython = Join-Path $env:LOCALAPPDATA "Python\pythoncore-3.14-64\python.exe"
$Python = if (Test-Path $VenvPython) { $VenvPython }
elseif (Test-Path $LocalPython312) { $LocalPython312 }
elseif (Test-Path $FallbackPython) { $FallbackPython }
else { "python" }

function Invoke-Python {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Arguments)
    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

Set-Location $ProjectRoot
switch ($Target.ToLowerInvariant()) {
    "help" {
        Write-Host "Targets: all, install, data, train, lint, test, serve, docker-build, docker-run, docker-test, mlflow-ui, monitoring-up, monitoring-down, traffic, k8s-deploy, report, clean"
    }
    "all" { & $PSCommandPath data; & $PSCommandPath train; & $PSCommandPath lint; & $PSCommandPath test }
    "install" { Invoke-Python -m pip install --upgrade pip; Invoke-Python -m pip install -r requirements-dev.txt }
    "data" { Invoke-Python -m src.data_loader; Invoke-Python -m src.preprocessing; Invoke-Python -m src.eda }
    "train" { Invoke-Python -m src.train }
    "lint" { Invoke-Python -m flake8 src test --max-complexity=10 --max-line-length=127 }
    "test" { Invoke-Python -m pytest test/ -v }
    "serve" { Invoke-Python -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000 }
    "docker-build" { docker build -t heart-disease-api:latest . }
    "docker-run" { docker run -d -p 8000:8000 --name heart-disease-serving heart-disease-api:latest }
    "docker-test" { Invoke-Python scripts/test_serving.py }
    "mlflow-ui" { Invoke-Python scripts/relocate_mlflow.py; Invoke-Python -m mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000 }
    "monitoring-up" { docker compose -f monitoring/docker-compose.monitoring.yml up --build -d }
    "monitoring-down" { docker compose -f monitoring/docker-compose.monitoring.yml down }
    "traffic" { Invoke-Python scripts/generate_traffic.py }
    "k8s-deploy" { & powershell -ExecutionPolicy Bypass -File scripts/deploy_k8s.ps1 }
    "report" { Invoke-Python scripts/generate_report.py }
    "clean" {
        Get-ChildItem -Path $ProjectRoot -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue |
            Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath (Join-Path $ProjectRoot ".pytest_cache") -Recurse -Force -ErrorAction SilentlyContinue
    }
    default { throw "Unknown target '$Target'. Run .\Make.ps1 help." }
}
