from __future__ import annotations

from abc import ABC, abstractmethod

from .cache import PriceCache
from .types import PricePoint


class MarketDataProvider(ABC):
    """Abstract base class for market data providers (Simulator or Massive)."""

    def __init__(self, cache: PriceCache) -> None:
        self.cache = cache

    @abstractmethod
    async def start(self) -> None:
        """Start the provider and background tick production."""
        pass

    @property
    def name(self) -> str:
        return self.__class__.__name__.lower().replace("provider", "")

    @abstractmethod
    async def stop(self) -> None:
        """Stop provider background tasks gracefully."""
        pass

    @property
    @abstractmethod
    def is_healthy(self) -> bool:
        """Return provider health status."""
        pass

    @abstractmethod
    async def get_history(self, ticker: str, limit: int = 100) -> list[PricePoint]:
        """Fetch historical buffer points for the given ticker."""
        pass
