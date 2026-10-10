from __future__ import annotations

from fastapi import Request
from ..market import create_market_provider
from ..market.cache import PriceCache
from ..market.interface import MarketDataProvider

_fallback_cache: PriceCache | None = None
_fallback_provider: MarketDataProvider | None = None


def get_cache(request: Request) -> PriceCache:
    if hasattr(request.app.state, "price_cache"):
        return request.app.state.price_cache
    global _fallback_cache
    if _fallback_cache is None:
        _fallback_cache = PriceCache()
    return _fallback_cache


def get_provider(request: Request) -> MarketDataProvider:
    if hasattr(request.app.state, "market_provider"):
        return request.app.state.market_provider
    global _fallback_provider
    if _fallback_provider is None:
        _fallback_provider = create_market_provider(get_cache(request))
    return _fallback_provider
