from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from ..market.cache import PriceCache
from ..watchlist.service import add_to_watchlist, get_watchlist, remove_from_watchlist
from .deps import get_cache

router = APIRouter(tags=["Watchlist"])


class WatchlistAddRequest(BaseModel):
    ticker: str = Field(..., description="Ticker symbol to add")


@router.get("/watchlist")
async def get_user_watchlist(cache: PriceCache = Depends(get_cache)):
    """Retrieve user watchlist with live pricing and metrics."""
    return get_watchlist(cache)


@router.post("/watchlist")
async def add_ticker_to_watchlist(
    req: WatchlistAddRequest,
    cache: PriceCache = Depends(get_cache),
):
    """Add a ticker from the 10-symbol universe to the watchlist."""
    try:
        return add_to_watchlist(req.ticker, cache)
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))


@router.delete("/watchlist/{ticker}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_ticker_from_watchlist(ticker: str):
    """Remove a ticker from the watchlist."""
    remove_from_watchlist(ticker)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
