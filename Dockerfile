# ==============================================================================
# FinAlly - Multi-Agent AI Trading Workstation
# Multi-stage production container build (Node.js export -> Python 3.12 / uv)
# ==============================================================================

# Stage 1: Build Next.js Static Export
FROM node:20-slim AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Stage 2: Python 3.12 Runtime with uv
FROM python:3.12-slim AS runner
WORKDIR /app

# Install uv binary from official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Runtime environment settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_HTTP_TIMEOUT=300 \
    FINALLY_DB_PATH=/app/db/finally.db

# Copy backend definition, lockfile, and install production dependencies
COPY backend/pyproject.toml backend/uv.lock backend/README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    for i in 1 2 3 4 5; do uv sync --frozen --no-dev && break || (echo "Retrying uv sync in 5s..." && sleep 5); done

# Copy backend application source
COPY backend/app ./app

# Copy compiled static frontend export
COPY --from=frontend-builder /app/frontend/out ./static

# Ensure database directory exists
RUN mkdir -p /app/db

EXPOSE 8000

CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
