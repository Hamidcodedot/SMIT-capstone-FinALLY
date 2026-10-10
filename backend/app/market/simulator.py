from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
import math
import random

from .cache import HISTORY_MAXLEN, PriceCache
from .interface import MarketDataProvider
from .sim_config import (
    EVENT_MAGNITUDE_RANGE,
    EVENT_PROBABILITY,
    FactorLoadings,
    TICKER_CONFIG,
)
from .types import Direction, PricePoint, PriceTick, TICKER_UNIVERSE

TICK_INTERVAL = 0.5  # seconds
DT_YEARS = TICK_INTERVAL / (365 * 24 * 60 * 60)  # tick interval expressed in years for GBM


def gbm_step(price: float, mu: float, sigma: float, dt_years: float, z: float) -> float:
    """Discretized Euler-Maruyama step of Geometric Brownian Motion."""
    drift = (mu - 0.5 * (sigma ** 2)) * dt_years
    diffusion = sigma * math.sqrt(dt_years) * z
    return price * math.exp(drift + diffusion)


def draw_ticker_shock(
    rng: random.Random,
    z_market: float,
    z_sector: float,
    loadings: FactorLoadings,
) -> float:
    """Generate a variance-preserving shock based on market, sector, and idiosyncratic noise."""
    z_idio = rng.gauss(0, 1)
    return (
        loadings.market * z_market
        + loadings.sector * z_sector
        + loadings.idio * z_idio
    )


def maybe_apply_event(rng: random.Random, price: float) -> float:
    """Occasionally trigger a sudden 2-5% price jump for realistic market surprises."""
    if rng.random() >= EVENT_PROBABILITY:
        return price
    magnitude = rng.uniform(*EVENT_MAGNITUDE_RANGE)
    sign = rng.choice((1, -1))
    return price * (1.0 + sign * magnitude)


class SimulatorProvider(MarketDataProvider):
    """Generates continuous live market ticks using Geometric Brownian Motion."""

    def __init__(self, cache: PriceCache, seed: int | None = None) -> None:
        super().__init__(cache)
        self._rng = random.Random(seed)
        self._prices: dict[str, float] = {
            t: cfg.seed_price for t, cfg in TICKER_CONFIG.items()
        }
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        self._backfill()
        self._running = True
        self._task = asyncio.create_task(self._run_loop())

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
        return True

    async def get_history(self, ticker: str, limit: int = 100) -> list[PricePoint]:
        if ticker not in TICKER_UNIVERSE:
            return []
        hist = self.cache.history(ticker)
        return hist[-limit:]

    def _step_all_tickers(self) -> dict[str, float]:
        z_market = self._rng.gauss(0, 1)
        z_tech = self._rng.gauss(0, 1)
        new_prices: dict[str, float] = {}
        for ticker, cfg in TICKER_CONFIG.items():
            z = draw_ticker_shock(self._rng, z_market, z_tech, cfg.loadings)
            price = gbm_step(self._prices[ticker], cfg.mu, cfg.sigma, DT_YEARS, z)
            price = maybe_apply_event(self._rng, price)
            new_prices[ticker] = round(price, 2)
        return new_prices

    async def _run_loop(self) -> None:
        while self._running:
            await asyncio.sleep(TICK_INTERVAL)
            self._tick(now=datetime.now(timezone.utc))

    def _tick(self, now: datetime) -> None:
        new_prices = self._step_all_tickers()
        for ticker, price in new_prices.items():
            prev_price = self._prices[ticker]
            self._prices[ticker] = price
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

    def step(self) -> list[PriceTick]:
        """Perform one discrete step and return published ticks."""
        self._tick(now=datetime.now(timezone.utc))
        return [self.cache.latest(t) for t in TICKER_UNIVERSE if self.cache.latest(t) is not None]

    def backfill_history(self, num_ticks: int = 100) -> None:
        """Backfill history with specified number of ticks."""
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(seconds=TICK_INTERVAL * num_ticks)
        for i in range(max(0, num_ticks - 1)):
            new_prices = self._step_all_tickers()
            ts = start_time + timedelta(seconds=TICK_INTERVAL * i)
            for ticker, price in new_prices.items():
                self._prices[ticker] = price
                self.cache.seed_history_point(ticker, PricePoint(ticker, price, ts))
        for ticker, price in self._prices.items():
            self.cache.update(
                PriceTick(
                    ticker=ticker,
                    price=price,
                    prev_price=price,
                    change=0.0,
                    change_percent=0.0,
                    direction=Direction.FLAT,
                    timestamp=now,
                )
            )

    def _backfill(self) -> None:
        """Synchronously fast-forward 100 ticks before start so history is never empty."""
        self.backfill_history(HISTORY_MAXLEN)


MarketSimulator = SimulatorProvider
