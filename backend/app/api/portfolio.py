from __future__ import annotations

from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..market.cache import PriceCache
from ..portfolio.trades import execute_trade
from ..portfolio.valuation import get_portfolio, get_portfolio_history
from .deps import get_cache

router = APIRouter(tags=["Portfolio"])


class TradeRequestModel(BaseModel):
    ticker: str = Field(..., description="Ticker symbol")
    quantity: float = Field(..., gt=0, description="Number of shares to trade")
    side: Literal["buy", "sell"] = Field(..., description="Trade side")


@router.get("/portfolio")
async def get_user_portfolio(cache: PriceCache = Depends(get_cache)):
    """Retrieve current portfolio state including cash, positions, valuation, and P&L."""
    return get_portfolio(cache)


@router.post("/portfolio/trade")
async def execute_user_trade(
    req: TradeRequestModel,
    cache: PriceCache = Depends(get_cache),
):
    """Execute a market buy or sell order instantly at current market price."""
    try:
        result = execute_trade(
            cache=cache,
            ticker=req.ticker,
            quantity=req.quantity,
            side=req.side,
        )
        return result
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Internal trade execution error: {err}")


@router.get("/portfolio/history")
async def get_user_portfolio_history():
    """Retrieve portfolio valuation history snapshots for the P&L line chart."""
    return get_portfolio_history()
