from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from ..db.connection import get_db
from ..market.cache import PriceCache
from .valuation import get_portfolio

logger = logging.getLogger(__name__)


def record_snapshot(cache: PriceCache, user_id: str = "default") -> float:
    """Calculate and persist a portfolio valuation snapshot."""
    portfolio = get_portfolio(cache, user_id=user_id)
    total_val = portfolio["total_value"]
    now_iso = datetime.now(timezone.utc).isoformat()

    with get_db() as conn:
        conn.execute(
            "INSERT INTO portfolio_snapshots (id, user_id, total_value, recorded_at) VALUES (?, ?, ?, ?)",
            (str(uuid.uuid4()), user_id, total_val, now_iso),
        )
    return total_val


async def portfolio_snapshot_task(
    cache: PriceCache,
    user_id: str = "default",
    interval_seconds: float = 30.0,
) -> None:
    """Background task that periodically records portfolio snapshots for the P&L chart."""
    logger.info("Portfolio snapshot background task started (interval: %ss)", interval_seconds)
    try:
        while True:
            await asyncio.sleep(interval_seconds)
            try:
                record_snapshot(cache, user_id=user_id)
            except Exception as e:
                logger.error("Error recording periodic portfolio snapshot: %s", e)
    except asyncio.CancelledError:
        logger.info("Portfolio snapshot background task stopped")
        raise
