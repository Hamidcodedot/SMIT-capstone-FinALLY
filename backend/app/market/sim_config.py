from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FactorLoadings:
    market: float
    sector: float
    idio: float


@dataclass(frozen=True)
class TickerConfig:
    seed_price: float
    mu: float
    sigma: float
    loadings: FactorLoadings


EVENT_PROBABILITY = 0.002
EVENT_MAGNITUDE_RANGE = (0.02, 0.05)

TICKER_CONFIG: dict[str, TickerConfig] = {
    "AAPL": TickerConfig(190.00, 0.08, 0.25, FactorLoadings(0.6, 0.7, 0.39)),
    "GOOGL": TickerConfig(175.00, 0.10, 0.28, FactorLoadings(0.6, 0.7, 0.39)),
    "MSFT": TickerConfig(420.00, 0.09, 0.22, FactorLoadings(0.6, 0.7, 0.39)),
    "AMZN": TickerConfig(185.00, 0.11, 0.30, FactorLoadings(0.55, 0.7, 0.46)),
    "NVDA": TickerConfig(130.00, 0.20, 0.55, FactorLoadings(0.5, 0.75, 0.43)),
    "META": TickerConfig(560.00, 0.12, 0.35, FactorLoadings(0.55, 0.7, 0.46)),
    "NFLX": TickerConfig(700.00, 0.10, 0.32, FactorLoadings(0.5, 0.65, 0.57)),
    "TSLA": TickerConfig(250.00, 0.15, 0.60, FactorLoadings(0.4, 0.3, 0.87)),
    "JPM": TickerConfig(210.00, 0.07, 0.20, FactorLoadings(0.5, 0.0, 0.87)),
    "V": TickerConfig(280.00, 0.08, 0.18, FactorLoadings(0.5, 0.0, 0.87)),
}
