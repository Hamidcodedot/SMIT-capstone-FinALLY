from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import os

import httpx

from .cache import PriceCache
from .interface import MarketDataProvider
from .types import Direction, PricePoint, PriceTick, TICKER_UNIVERSE

MASSIVE_BASE_URL = "https://api.polygon.io"
POLL_INTERVAL = 15.0  # Default free tier 15s interval


class MassiveProvider(MarketDataProvider):
    """Real market data provider using Massive (Polygon.io) REST API."""

    def __init__(self, cache: PriceCache, api_key: str) -> None:
        super().__init__(cache)
        self.api_key = api_key
        self._running = False
        self._task: asyncio.Task | None = None
        self._is_healthy = True
        self._failure_count = 0
        self._last_prices: dict[str, float] = {}

    async def start(self) -> None:
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())

    async def stop(self) -> None:
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    @property
    def is_healthy(self) -> bool:
        return self._is_healthy

    async def get_history(self, ticker: str, limit: int = 100) -> list[PricePoint]:
        if ticker not in TICKER_UNIVERSE:
            return []
        hist = self.cache.history(ticker)
        if hist:
            return hist[-limit:]
        # Attempt lazy historical fetch from polygon aggregates if available
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                url = f"{MASSIVE_BASE_URL}/v2/aggs/ticker/{ticker}/prev?adjusted=true&apiKey={self.api_key}"
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("results", [])
                    if results:
                        close_price = round(float(results[0].get("c", 100.0)), 2)
                        pt = PricePoint(ticker, close_price, datetime.now(timezone.utc))
                        self.cache.seed_history_point(ticker, pt)
                        return [pt]
        except Exception:
            pass
        return []

    async def _poll_loop(self) -> None:
        async with httpx.AsyncClient(timeout=10.0) as client:
            while self._running:
                try:
                    await self._fetch_all(client)
                    self._failure_count = 0
                    self._is_healthy = True
                except Exception:
                    self._failure_count += 1
                    if self._failure_count >= 5:
                        self._is_healthy = False
                await asyncio.sleep(POLL_INTERVAL)

    async def _fetch_all(self, client: httpx.AsyncClient) -> None:
        now = datetime.now(timezone.utc)
        for ticker in TICKER_UNIVERSE:
            url = f"{MASSIVE_BASE_URL}/v2/aggs/ticker/{ticker}/prev?adjusted=true&apiKey={self.api_key}"
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                if results:
                    price = round(float(results[0].get("c", 0.0)), 2)
                    prev_price = self._last_prices.get(ticker, price)
                    self._last_prices[ticker] = price
                    change = round(price - prev_price, 2)
                    direction = (
                        Direction.FLAT
                        if change == 0
                        else (Direction.UP if change > 0 else Direction.DOWN)
                    )
                    pct = round((change / prev_price * 100) if prev_price else 0.0, 2)
                    self.cache.update(
                        PriceTick(
                            ticker=ticker,
                            price=price,
                            prev_price=prev_price,
                            change=change,
                            change_percent=pct,
                            direction=direction,
                            timestamp=now,
                        )
                    )
