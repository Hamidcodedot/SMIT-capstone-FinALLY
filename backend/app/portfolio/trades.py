from __future__ import annotations

from datetime import datetime, timezone
import uuid

from ..db.connection import get_db
from ..market.cache import PriceCache
from ..market.sim_config import TICKER_CONFIG
from ..market.types import TICKER_UNIVERSE


class TradeExecutionError(ValueError):
    """Raised when trade fails validation."""
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def execute_trade(
    ticker: Any,
    side: Any,
    quantity: Any,
    cache: Any = None,
    user_id: str = "default",
    **kwargs,
) -> dict:
    """Execute buy or sell atomically within a single SQLite transaction."""
    # Normalize flexible argument order
    raw_args = [ticker, side, quantity, cache]
    resolved_cache = kwargs.get("cache")
    resolved_ticker = kwargs.get("ticker")
    resolved_side = kwargs.get("side")
    resolved_quantity = kwargs.get("quantity")

    for arg in raw_args:
        if arg is None:
            continue
        if isinstance(arg, PriceCache) and resolved_cache is None:
            resolved_cache = arg
        elif isinstance(arg, (int, float)) and not isinstance(arg, bool) and resolved_quantity is None:
            resolved_quantity = float(arg)
        elif isinstance(arg, str):
            clean = arg.strip().lower()
            if clean in ("buy", "sell") and resolved_side is None:
                resolved_side = clean
            elif resolved_ticker is None:
                resolved_ticker = arg.strip().upper()

    if resolved_cache is None:
        raise ValueError("PriceCache instance is required for trade execution")

    cache = resolved_cache
    ticker = str(resolved_ticker or "").strip().upper()
    side = str(resolved_side or "").strip().lower()
    quantity = float(resolved_quantity or 0)

    if ticker not in TICKER_UNIVERSE:
        raise TradeExecutionError(f"Unsupported ticker '{ticker}'. Must be one of {TICKER_UNIVERSE}", 400)

    if quantity <= 0:
        raise TradeExecutionError("Trade quantity must be strictly greater than 0", 400)

    if side not in ("buy", "sell"):
        raise TradeExecutionError("Trade side must be 'buy' or 'sell'", 400)

    # Determine execution price from live cache
    latest_tick = cache.latest(ticker)
    price = latest_tick.price if latest_tick else TICKER_CONFIG[ticker].seed_price
    price = round(price, 2)
    quantity = round(quantity, 4)
    total_amount = round(quantity * price, 2)
    now = datetime.now(timezone.utc).isoformat()

    with get_db() as conn:
        # Fetch current profile
        profile = conn.execute(
            "SELECT cash_balance FROM users_profile WHERE id = ?", (user_id,)
        ).fetchone()
        if not profile:
            raise TradeExecutionError(f"User profile '{user_id}' not found", 404)

        cash_balance = round(float(profile["cash_balance"]), 2)

        # Fetch current position
        pos = conn.execute(
            "SELECT id, quantity, avg_cost FROM positions WHERE user_id = ? AND ticker = ?",
            (user_id, ticker),
        ).fetchone()

        current_qty = round(float(pos["quantity"]), 4) if pos else 0.0
        current_avg_cost = round(float(pos["avg_cost"]), 2) if pos else 0.0

        if side == "buy":
            if cash_balance < total_amount:
                raise TradeExecutionError(
                    f"Insufficient funds: trade requires ${total_amount:,.2f}, available balance is ${cash_balance:,.2f}",
                    400,
                )
            new_cash = round(cash_balance - total_amount, 2)
            new_qty = round(current_qty + quantity, 4)
            new_avg_cost = round(
                ((current_qty * current_avg_cost) + total_amount) / new_qty, 2
            )

            conn.execute(
                "UPDATE users_profile SET cash_balance = ? WHERE id = ?",
                (new_cash, user_id),
            )

            if pos:
                conn.execute(
                    "UPDATE positions SET quantity = ?, avg_cost = ?, updated_at = ? WHERE id = ?",
                    (new_qty, new_avg_cost, now, pos["id"]),
                )
            else:
                conn.execute(
                    "INSERT INTO positions (id, user_id, ticker, quantity, avg_cost, updated_at) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (str(uuid.uuid4()), user_id, ticker, new_qty, new_avg_cost, now),
                )
            resulting_cash = new_cash

        else:  # sell
            if current_qty < quantity:
                raise TradeExecutionError(
                    f"Insufficient shares: owned {current_qty} shares of {ticker}, attempted to sell {quantity}",
                    400,
                )
            new_cash = round(cash_balance + total_amount, 2)
            new_qty = round(current_qty - quantity, 4)

            conn.execute(
                "UPDATE users_profile SET cash_balance = ? WHERE id = ?",
                (new_cash, user_id),
            )

            if new_qty <= 0:
                conn.execute("DELETE FROM positions WHERE id = ?", (pos["id"],))
            else:
                conn.execute(
                    "UPDATE positions SET quantity = ?, updated_at = ? WHERE id = ?",
                    (new_qty, now, pos["id"]),
                )
            resulting_cash = new_cash

        # Insert trade log
        conn.execute(
            "INSERT INTO trades (id, user_id, ticker, side, quantity, price, executed_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (str(uuid.uuid4()), user_id, ticker, side, quantity, price, now),
        )

        # Compute immediate portfolio valuation for snapshot
        all_positions = conn.execute(
            "SELECT ticker, quantity FROM positions WHERE user_id = ?", (user_id,)
        ).fetchall()
        holdings_val = sum(
            float(p["quantity"]) * (cache.latest(p["ticker"]).price if cache.latest(p["ticker"]) else TICKER_CONFIG[p["ticker"]].seed_price)
            for p in all_positions
        )
        total_val = round(resulting_cash + holdings_val, 2)

        conn.execute(
            "INSERT INTO portfolio_snapshots (id, user_id, total_value, recorded_at) VALUES (?, ?, ?, ?)",
            (str(uuid.uuid4()), user_id, total_val, now),
        )

    return {
        "ticker": ticker,
        "side": side,
        "quantity": quantity,
        "price": price,
        "cash_balance": resulting_cash,
    }
