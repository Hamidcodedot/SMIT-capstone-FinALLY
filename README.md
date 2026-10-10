# FinAlly — AI Trading Workstation

An AI-powered real-time trading workstation with a terminal aesthetic: live-streaming market data, a simulated $10,000 portfolio, and an LLM chat copilot that can analyze your positions and execute trades on your behalf.

Capstone project for Saylani Mass IT Training (SMIT) — built using orchestrated AI coding agents following the specifications in `planning/`.

---

## Status

Fully implemented and verified.
- Backend: FastAPI with in-memory price cache, GBM market simulation, SQLite persistence, and LiteLLM OpenRouter integration.
- Frontend: Next.js with TypeScript and Tailwind CSS, built as a static export and served by FastAPI on port 8000.
- Docker: Production multi-stage Dockerfile and docker-compose.
- Testing: Comprehensive test suite across market simulation, portfolio engine, watchlist, and chat copilot.

---

## Architecture Overview

Single container, single port (`8000`), zero CORS complexity:

- **Frontend**: Next.js (TypeScript, Tailwind CSS), static export (`output: 'export'`)
- **Backend**: FastAPI (Python 3.12 managed with `uv`)
- **Database**: SQLite (`db/finally.db`, volume-mounted with lazy initialization)
- **Real-Time Stream**: Server-Sent Events (SSE) at `/api/stream/prices`
- **AI Copilot**: LiteLLM -> OpenRouter (Cerebras fast inference) with structured action execution and offline mock mode
- **Market Data**: Correlated Geometric Brownian Motion (GBM) simulator by default, or Polygon/Massive REST API via `MASSIVE_API_KEY`
- **Persistence**: Atomic transactions for cash balance, holdings, trade logs, and portfolio snapshots

---

## Repository Structure

```
.
├── backend/                  # FastAPI uv project
│   ├── app/
│   │   ├── api/              # REST & SSE routers (prices, portfolio, watchlist, chat, health)
│   │   ├── chat/             # LLM context, OpenRouter client, structured action execution
│   │   ├── db/               # SQLite connection, schema, lazy seeder
│   │   ├── market/           # Cache, GBM simulator, Polygon client, ticker universe
│   │   ├── portfolio/        # Atomic trade execution, valuation, 30s snapshots
│   │   └── watchlist/        # Watchlist CRUD enforcing the 10-ticker universe
│   ├── tests/                # Pytest unit & API integration test suite
│   └── pyproject.toml        # uv project configuration & lockfile
├── frontend/                 # Next.js TypeScript application
│   ├── src/                  # Terminal UI, Recharts sparklines/heatmaps, SSE client
│   └── out/                  # Compiled static SPA export
├── planning/                 # System architecture & specification contracts
├── scripts/                  # Start/stop launch scripts
│   ├── start_windows.ps1     # Windows Docker launch script
│   ├── stop_windows.ps1      # Windows Docker stop script
│   ├── start_mac.sh          # macOS/Linux Docker launch script
│   └── stop_mac.sh           # macOS/Linux Docker stop script
├── test/                     # Playwright E2E testing infrastructure
├── db/                       # Volume mount target for finally.db
├── Dockerfile                # Multi-stage container build
└── docker-compose.yml        # Docker compose configuration
```

---

## Environment Variables

Copy `.env.example` to `.env`:

```bash
# Required for live LLM chat: OpenRouter API key
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Optional: Massive (Polygon.io) API key for real market data
# If unset, the built-in geometric Brownian motion simulator is used
MASSIVE_API_KEY=

# Optional: Set to true for deterministic mock responses (testing/offline)
LLM_MOCK=false
```

---

## Running FinAlly

### Option 1: Docker (Recommended)

**On Windows (PowerShell):**
```powershell
.\scripts\start_windows.ps1
```

**On macOS / Linux:**
```bash
chmod +x ./scripts/*.sh
./scripts/start_mac.sh
```

**Using Docker Compose directly:**
```bash
docker compose up --build
```

Access the workstation in your browser at `http://localhost:8000`.

### Option 2: Local Development (Without Docker)

**1. Start the Backend:**
```bash
cd backend
uv sync --extra dev
uv run uvicorn app.main:app --port 8000
```

**2. Access the Application:**
Once the static export is generated, visit `http://localhost:8000`.
To develop the frontend with hot-reloading:
```bash
cd frontend
npm run dev
```

---

## Running the Test Suite

Run backend unit and API tests with `uv`:

```bash
cd backend
uv run pytest
```

Run Playwright end-to-end tests:

```bash
cd test
npm test
```
