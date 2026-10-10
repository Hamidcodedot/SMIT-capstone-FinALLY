from __future__ import annotations

import os

from .cache import PriceCache
from .interface import MarketDataProvider
from .simulator import SimulatorProvider


def get_market_data_provider(cache: PriceCache) -> MarketDataProvider:
    """Select provider based on MASSIVE_API_KEY presence at startup."""
    massive_key = os.getenv("MASSIVE_API_KEY", "").strip()
    if massive_key:
        from .massive import MassiveProvider
        return MassiveProvider(cache, massive_key)
    return SimulatorProvider(cache)


create_market_provider = get_market_data_provider

__all__ = [
    "PriceCache",
    "MarketDataProvider",
    "SimulatorProvider",
    "get_market_data_provider",
    "create_market_provider",
]
