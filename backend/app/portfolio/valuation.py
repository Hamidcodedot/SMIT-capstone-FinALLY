from __future__ import annotations

from ..db.connection import get_db
from ..market.cache import PriceCache
from ..market.sim_config import TICKER_CONFIG


def get_portfolio(cache: PriceCache, user_id: str = "default") -> dict:
    """Calculate current live portfolio valuation including open positions and unrealized P&L."""
    with get_db() as conn:
        profile = conn.execute(
            "SELECT cash_balance FROM users_profile WHERE id = ?", (user_id,)
        ).fetchone()
        cash_balance = round(float(profile["cash_balance"]), 2) if profile else 10000.0

        pos_rows = conn.execute(
            "SELECT ticker, quantity, avg_cost FROM positions WHERE user_id = ? ORDER BY ticker ASC",
            (user_id,),
        ).fetchall()

    positions_list = []
    total_holdings_value = 0.0
    total_pnl = 0.0

    for r in pos_rows:
        ticker = r["ticker"]
        qty = round(float(r["quantity"]), 4)
        avg_cost = round(float(r["avg_cost"]), 2)

        latest_tick = cache.latest(ticker)
        current_price = latest_tick.price if latest_tick else TICKER_CONFIG.get(ticker, type("", (), {"seed_price": 100.0})).seed_price
        current_price = round(current_price, 2)

        mkt_val = round(qty * current_price, 2)
        unrealized = round((current_price - avg_cost) * qty, 2)
        pct = round(((current_price - avg_cost) / avg_cost * 100) if avg_cost > 0 else 0.0, 2)

        total_holdings_value += mkt_val
        total_pnl += unrealized

        positions_list.append({
            "ticker": ticker,
            "quantity": qty,
            "avg_cost": avg_cost,
            "current_price": current_price,
            "unrealized_pnl": unrealized,
            "pnl_percent": pct,
        })

    total_value = round(cash_balance + total_holdings_value, 2)
    total_pnl = round(total_pnl, 2)

    return {
        "cash_balance": cash_balance,
        "positions": positions_list,
        "total_value": total_value,
        "total_pnl": total_pnl,
    }


def get_portfolio_history(user_id: str = "default", limit: int = 100) -> list[dict]:
    """Retrieve historical snapshots of portfolio valuation for the P&L chart."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT total_value, recorded_at FROM portfolio_snapshots "
            "WHERE user_id = ? ORDER BY recorded_at ASC LIMIT ?",
            (user_id, limit),
        ).fetchall()

    return [
        {"total_value": round(float(r["total_value"]), 2), "recorded_at": r["recorded_at"]}
        for r in rows
    ]
