from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .api import api_router
from .db import init_db
from .market import create_market_provider
from .market.cache import PriceCache
from .portfolio.snapshots import portfolio_snapshot_task, record_snapshot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("finally")

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup, background polling/simulation, and shutdown."""
    logger.info("Initializing FinAlly Database...")
    init_db()

    logger.info("Initializing Real-Time Price Cache...")
    cache = PriceCache(history_limit=100)
    provider = create_market_provider(cache)

    app.state.price_cache = cache
    app.state.market_provider = provider

    logger.info("Starting Market Data Provider: %s...", provider.name)
    await provider.start()

    logger.info("Recording initial portfolio valuation snapshot...")
    try:
        record_snapshot(cache, user_id="default")
    except Exception as e:
        logger.warning("Could not record initial snapshot: %s", e)

    logger.info("Spawning 30s background portfolio snapshot task...")
    snapshot_task = asyncio.create_task(
        portfolio_snapshot_task(cache, user_id="default", interval_seconds=30.0)
    )

    yield

    logger.info("Shutting down FinAlly application...")
    snapshot_task.cancel()
    try:
        await snapshot_task
    except asyncio.CancelledError:
        pass

    await provider.stop()
    logger.info("Shutdown complete.")


app = FastAPI(
    title="FinAlly Trading Workstation API",
    version="0.1.0",
    lifespan=lifespan,
)

# Enable CORS for local cross-origin development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router)

# Resolve static files directory (Docker container or local frontend export)
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_CANDIDATES = [
    BASE_DIR / "static",
    BASE_DIR.parent / "frontend" / "out",
]

static_dir: Path | None = None
for candidate in STATIC_CANDIDATES:
    if candidate.exists() and (candidate / "index.html").exists():
        static_dir = candidate
        break

if static_dir:
    logger.info("Serving static frontend export from: %s", static_dir)

    # Mount static assets if _next directory exists
    next_dir = static_dir / "_next"
    if next_dir.exists():
        app.mount("/_next", StaticFiles(directory=str(next_dir)), name="next_static")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

        file_path = static_dir / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        index_file = static_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)

        return JSONResponse(status_code=404, content={"detail": "Not Found"})
else:
    logger.info("No static frontend build found. Running in API-only mode.")

    @app.get("/")
    async def root():
        return {
            "name": "FinAlly Trading Workstation API",
            "status": "online",
            "docs": "/docs",
        }
