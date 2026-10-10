# ==============================================================================
# FinAlly - Windows Stop Script
# Stops and removes the FinAlly Docker container (preserves database volume)
# ==============================================================================

$Existing = docker ps -aq -f "name=^finally$"
if ($Existing) {
    Write-Host "Stopping and removing FinAlly container..." -ForegroundColor Yellow
    docker stop finally | Out-Null
    docker rm finally | Out-Null
    Write-Host "FinAlly container stopped. Data in ./db is preserved." -ForegroundColor Green
} else {
    Write-Host "No running FinAlly container found." -ForegroundColor Gray
}
