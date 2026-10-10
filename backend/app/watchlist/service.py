from __future__ import annotations

import uuid
from datetime import datetime, timezone

from ..db.connection import get_db
from ..market.cache import PriceCache
from ..market.types import TICKER_UNIVERSE


def get_watchlist(cache: PriceCache, user_id: str = "default") -> list[dict]:
    """Retrieve user watchlist items with live market prices and metrics."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT ticker FROM watchlist WHERE user_id = ? ORDER BY added_at ASC",
            (user_id,),
        ).fetchall()

    items = []
    for r in rows:
        ticker = r["ticker"]
        tick = cache.latest(ticker)
        if tick:
            items.append({
                "ticker": ticker,
                "price": tick.price,
                "prev_price": tick.prev_price,
                "change_percent": tick.change_percent,
                "direction": tick.direction,
            })
        else:
            items.append({
                "ticker": ticker,
                "price": None,
                "prev_price": None,
                "change_percent": None,
                "direction": "flat",
            })
    return items


def add_to_watchlist(ticker: str, cache: PriceCache, user_id: str = "default") -> list[dict]:
    """Add a ticker to the user watchlist (must be in the 10-ticker universe)."""
    clean_ticker = ticker.strip().upper()
    if clean_ticker not in TICKER_UNIVERSE:
        raise ValueError(f"Ticker '{clean_ticker}' is not supported. Supported universe: {', '.join(TICKER_UNIVERSE)}")

    now_iso = datetime.now(timezone.utc).isoformat()
    with get_db() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO watchlist (id, user_id, ticker, added_at) VALUES (?, ?, ?, ?)",
            (str(uuid.uuid4()), user_id, clean_ticker, now_iso),
        )

    return get_watchlist(cache, user_id=user_id)


def remove_from_watchlist(ticker: str, user_id: str = "default") -> None:
    """Remove a ticker from the user watchlist."""
    clean_ticker = ticker.strip().upper()
    with get_db() as conn:
        conn.execute(
            "DELETE FROM watchlist WHERE user_id = ? AND ticker = ?",
            (user_id, clean_ticker),
        )
