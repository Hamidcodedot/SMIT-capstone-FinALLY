from __future__ import annotations

import asyncio
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from ..market.cache import PriceCache
from ..market.types import TICKER_UNIVERSE
from .deps import get_cache

router = APIRouter(tags=["Market Data"])


@router.get("/stream/prices")
async def stream_prices(cache: PriceCache = Depends(get_cache)):
    """Server-Sent Events endpoint pushing live real-time price updates for all tickers."""
    async def event_generator():
        queue = cache.subscribe()
        try:
            while True:
                tick = await queue.get()
                yield f"data: {tick.to_json()}\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            cache.unsubscribe(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/prices/{ticker}/history")
async def get_price_history(ticker: str, cache: PriceCache = Depends(get_cache)):
    """Return rolling in-memory price history buffer for initial chart/sparkline rendering."""
    clean_ticker = ticker.strip().upper()
    if clean_ticker not in TICKER_UNIVERSE:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown ticker '{clean_ticker}'. Supported: {', '.join(TICKER_UNIVERSE)}",
        )

    history = cache.get_history(clean_ticker)
    return [
        {"ticker": pt.ticker, "price": pt.price, "timestamp": pt.timestamp}
        for pt in history
    ]
