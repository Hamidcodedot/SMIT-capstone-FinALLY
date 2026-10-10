from __future__ import annotations

from datetime import datetime, timezone
import sqlite3
import uuid

from ..market.types import TICKER_UNIVERSE


def seed_default_data(conn: sqlite3.Connection) -> None:
    """Seed default profile ($10,000) and watchlist (10 tickers) if empty."""
    now = datetime.now(timezone.utc).isoformat()

    # Seed user profile
    cursor = conn.execute("SELECT id FROM users_profile WHERE id = 'default'")
    if not cursor.fetchone():
        conn.execute(
            "INSERT INTO users_profile (id, cash_balance, created_at) VALUES ('default', 10000.0, ?)",
            (now,),
        )
        # Record initial snapshot
        conn.execute(
            "INSERT INTO portfolio_snapshots (id, user_id, total_value, recorded_at) VALUES (?, 'default', 10000.0, ?)",
            (str(uuid.uuid4()), now),
        )

    # Seed watchlist
    for ticker in TICKER_UNIVERSE:
        cur = conn.execute(
            "SELECT id FROM watchlist WHERE user_id = 'default' AND ticker = ?",
            (ticker,),
        )
        if not cur.fetchone():
            conn.execute(
                "INSERT INTO watchlist (id, user_id, ticker, added_at) VALUES (?, 'default', ?, ?)",
                (str(uuid.uuid4()), ticker, now),
            )
