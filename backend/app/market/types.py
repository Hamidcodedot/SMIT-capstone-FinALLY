from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json


TICKER_UNIVERSE: tuple[str, ...] = (
    "AAPL",
    "GOOGL",
    "MSFT",
    "AMZN",
    "TSLA",
    "NVDA",
    "META",
    "JPM",
    "V",
    "NFLX",
)


class Direction(str, Enum):
    UP = "up"
    DOWN = "down"
    FLAT = "flat"


@dataclass(frozen=True, slots=True)
class PriceTick:
    """One live price update for a single ticker."""
    ticker: str
    price: float
    prev_price: float
    change: float
    change_percent: float
    direction: Direction
    timestamp: datetime

    def to_dict(self) -> dict:
        ts_str = self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp)
        dir_val = self.direction.value if isinstance(self.direction, Direction) else str(self.direction)
        return {
            "ticker": self.ticker,
            "price": self.price,
            "prev_price": self.prev_price,
            "change": self.change,
            "change_percent": self.change_percent,
            "direction": dir_val,
            "timestamp": ts_str,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


@dataclass(frozen=True, slots=True)
class PricePoint:
    """One point in a rolling/backfill history buffer."""
    ticker: str
    price: float
    timestamp: datetime

    def to_dict(self) -> dict:
        ts_str = self.timestamp.isoformat() if isinstance(self.timestamp, datetime) else str(self.timestamp)
        return {
            "ticker": self.ticker,
            "price": self.price,
            "timestamp": ts_str,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
