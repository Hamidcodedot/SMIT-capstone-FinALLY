#!/usr/bin/env bash
# ==============================================================================
# FinAlly - macOS / Linux Stop Script
# Stops and removes the FinAlly container while preserving the database
# ==============================================================================
set -e

if [ "$(docker ps -aq -f name=^finally$)" ]; then
    echo "Stopping and removing FinAlly container..."
    docker stop finally >/dev/null 2>&1 || true
    docker rm finally >/dev/null 2>&1 || true
    echo "FinAlly container stopped. Data in ./db is preserved."
else
    echo "No running FinAlly container found."
fi
