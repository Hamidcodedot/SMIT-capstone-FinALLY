#!/usr/bin/env bash
# ==============================================================================
# FinAlly - macOS / Linux Launch Script
# Starts the FinAlly Docker container on http://localhost:8000
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "FinAlly - AI Trading Workstation Launcher"

# 1. Ensure .env exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "Copying .env.example to .env..."
        cp .env.example .env
    else
        echo "Creating default .env..."
        echo -e "LLM_MOCK=true\nOPENROUTER_API_KEY=\nMASSIVE_API_KEY=" > .env
    fi
fi

# 2. Ensure db folder exists
mkdir -p db

# 3. Stop existing container if present
if [ "$(docker ps -aq -f name=^finally$)" ]; then
    echo "Stopping existing finally container..."
    docker stop finally >/dev/null 2>&1 || true
    docker rm finally >/dev/null 2>&1 || true
fi

# 4. Build Docker image
echo "Building Docker image (finally)..."
docker build -t finally .

# 5. Run container
echo "Starting FinAlly container on port 8000..."
docker run -d --name finally -v "$(pwd)/db:/app/db" -p 8000:8000 --env-file .env finally

echo "FinAlly is now running at: http://localhost:8000"

# Open browser if supported
if command -v open >/dev/null 2>&1; then
    sleep 2
    open "http://localhost:8000"
elif command -v xdg-open >/dev/null 2>&1; then
    sleep 2
    xdg-open "http://localhost:8000"
fi
