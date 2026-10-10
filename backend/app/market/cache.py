from __future__ import annotations

import asyncio
from collections import deque
from typing import TYPE_CHECKING

from .types import PricePoint, PriceTick, TICKER_UNIVERSE

HISTORY_MAXLEN = 100
QUEUE_MAXSIZE = 256


class PriceCache:
    """In-memory shared price cache and SSE broadcaster."""

    def __init__(self, history_limit: int = HISTORY_MAXLEN) -> None:
        self.history_limit = history_limit
        self._latest: dict[str, PriceTick] = {}
        self._history: dict[str, deque[PricePoint]] = {
            t: deque(maxlen=history_limit) for t in TICKER_UNIVERSE
        }
        self._subscribers: set[asyncio.Queue[PriceTick]] = set()

    def update(self, tick: PriceTick) -> None:
        """Update latest price, push to history, and fan out to all subscribers."""
        self._latest[tick.ticker] = tick
        self._history[tick.ticker].append(
            PricePoint(tick.ticker, tick.price, tick.timestamp)
        )
        to_drop: list[asyncio.Queue[PriceTick]] = []
        for q in list(self._subscribers):
            try:
                q.put_nowait(tick)
            except asyncio.QueueFull:
                to_drop.append(q)
        for q in to_drop:
            self._subscribers.discard(q)

    def seed_history_point(self, ticker: str, point: PricePoint) -> None:
        """Append one history point during backfill without updating latest or notifying subscribers."""
        if ticker in self._history:
            self._history[ticker].append(point)

    def seed_history(self, ticker: str, points: list[PricePoint]) -> None:
        """Seed complete history buffer for a ticker."""
        if ticker in self._history:
            self._history[ticker] = deque(points, maxlen=HISTORY_MAXLEN)

    def latest(self, ticker: str) -> PriceTick | None:
        return self._latest.get(ticker)

    def all_latest(self) -> dict[str, PriceTick]:
        return dict(self._latest)

    def history(self, ticker: str) -> list[PricePoint]:
        buf = self._history.get(ticker)
        return list(buf) if buf else []

    get_history = history

    def subscribe(self) -> asyncio.Queue[PriceTick]:
        q: asyncio.Queue[PriceTick] = asyncio.Queue(maxsize=QUEUE_MAXSIZE)
        self._subscribers.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue[PriceTick]) -> None:
        self._subscribers.discard(q)
