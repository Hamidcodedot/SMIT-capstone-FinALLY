from __future__ import annotations

from datetime import datetime, timezone
from fastapi import APIRouter, Depends

from ..market.interface import MarketDataProvider
from .deps import get_provider

router = APIRouter(tags=["System"])


@router.get("/health")
async def health_check(provider: MarketDataProvider = Depends(get_provider)):
    """System health check endpoint for container probes."""
    return {
        "status": "ok",
        "provider": provider.name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
