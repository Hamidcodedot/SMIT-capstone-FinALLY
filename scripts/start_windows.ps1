# ==============================================================================
# FinAlly - Windows Launch Script
# Starts the FinAlly Docker container on http://localhost:8000
# ==============================================================================

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "FinAlly - AI Trading Workstation Launcher" -ForegroundColor Cyan

# 1. Ensure .env exists
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Write-Host "Copying .env.example to .env..." -ForegroundColor Yellow
        Copy-Item ".env.example" ".env"
    } else {
        Write-Host "Creating default .env..." -ForegroundColor Yellow
        Set-Content -Path ".env" -Value "LLM_MOCK=true`nOPENROUTER_API_KEY=`nMASSIVE_API_KEY="
    }
}

# 2. Ensure db folder exists
if (-not (Test-Path "db")) {
    New-Item -ItemType Directory -Path "db" | Out-Null
}

# 3. Stop and remove any existing container
$Existing = docker ps -aq -f "name=^finally$"
if ($Existing) {
    Write-Host "Stopping existing finally container..." -ForegroundColor Yellow
    docker stop finally | Out-Null
    docker rm finally | Out-Null
}

# 4. Build Docker image
Write-Host "Building Docker image (finally)..." -ForegroundColor Cyan
docker build -t finally .

# 5. Run container
Write-Host "Starting FinAlly container on port 8000..." -ForegroundColor Green
docker run -d --name finally -v finally-data:/app/db -p 8000:8000 --env-file .env finally

Write-Host "FinAlly is now running at: http://localhost:8000" -ForegroundColor Green

# Optional: Open browser
Start-Sleep -Seconds 2
Start-Process "http://localhost:8000"
