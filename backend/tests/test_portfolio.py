import os
import pytest
from app.db.connection import init_db
from app.market.cache import PriceCache
from app.market.types import PriceTick
from app.portfolio.trades import execute_trade
from app.portfolio.valuation import get_portfolio, get_portfolio_history
from app.portfolio.snapshots import record_snapshot


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_finally.db"
    monkeypatch.setenv("FINALLY_DB_PATH", str(test_db))
    # Reset connection module DB_PATH
    import app.db.connection as db_conn
    monkeypatch.setattr(db_conn, "DB_PATH", test_db)
    init_db()
    yield test_db


@pytest.fixture
def populated_cache():
    cache = PriceCache(history_limit=10)
    for ticker, price in [("AAPL", 200.0), ("MSFT", 400.0), ("TSLA", 250.0)]:
        cache.update(
            PriceTick(
                ticker=ticker,
                price=price,
                prev_price=price,
                change=0.0,
                change_percent=0.0,
                direction="flat",
                timestamp="2026-01-01T00:00:00Z",
            )
        )
    return cache


def test_initial_portfolio_valuation(populated_cache):
    portfolio = get_portfolio(populated_cache)
    assert portfolio["cash_balance"] == 10000.0
    assert portfolio["positions"] == []
    assert portfolio["total_value"] == 10000.0
    assert portfolio["total_pnl"] == 0.0


def test_execute_buy_trade(populated_cache):
    # Buy 10 AAPL @ 200 = 2000 cash spent
    result = execute_trade(populated_cache, "AAPL", 10.0, "buy")
    assert result["ticker"] == "AAPL"
    assert result["side"] == "buy"
    assert result["quantity"] == 10.0
    assert result["price"] == 200.0
    assert result["cash_balance"] == 8000.0

    portfolio = get_portfolio(populated_cache)
    assert portfolio["cash_balance"] == 8000.0
    assert len(portfolio["positions"]) == 1
    pos = portfolio["positions"][0]
    assert pos["ticker"] == "AAPL"
    assert pos["quantity"] == 10.0
    assert pos["avg_cost"] == 200.0
    assert pos["unrealized_pnl"] == 0.0
    assert portfolio["total_value"] == 10000.0


def test_insufficient_cash_rejected(populated_cache):
    # Try to buy 100 AAPL @ 200 = 20000 (exceeds 10000)
    with pytest.raises(ValueError, match="Insufficient funds"):
        execute_trade(populated_cache, "AAPL", 100.0, "buy")


def test_short_selling_rejected(populated_cache):
    # Try to sell without holding any shares
    with pytest.raises(ValueError, match="Insufficient shares"):
        execute_trade(populated_cache, "AAPL", 5.0, "sell")


def test_execute_sell_trade(populated_cache):
    # Buy 10 AAPL @ 200
    execute_trade(populated_cache, "AAPL", 10.0, "buy")

    # Update AAPL price to 220
    populated_cache.update(
        PriceTick(
            ticker="AAPL",
            price=220.0,
            prev_price=200.0,
            change=20.0,
            change_percent=10.0,
            direction="up",
            timestamp="2026-01-01T00:01:00Z",
        )
    )

    # Sell 5 AAPL @ 220 = 1100 cash received -> 8000 + 1100 = 9100
    sell_res = execute_trade(populated_cache, "AAPL", 5.0, "sell")
    assert sell_res["cash_balance"] == 9100.0

    # Remaining 5 shares @ 220 = 1100, cost 1000, unrealized pnl = +100
    portfolio = get_portfolio(populated_cache)
    assert portfolio["cash_balance"] == 9100.0
    assert len(portfolio["positions"]) == 1
    pos = portfolio["positions"][0]
    assert pos["quantity"] == 5.0
    assert pos["unrealized_pnl"] == 100.0
    assert portfolio["total_value"] == 10200.0

    # Sell remaining 5 shares -> row must be deleted
    execute_trade(populated_cache, "AAPL", 5.0, "sell")
    portfolio_empty = get_portfolio(populated_cache)
    assert len(portfolio_empty["positions"]) == 0
    assert portfolio_empty["cash_balance"] == 10200.0


def test_snapshot_recording(populated_cache):
    record_snapshot(populated_cache)
    history = get_portfolio_history()
    assert len(history) >= 2  # Seeded initial + test record
    assert history[-1]["total_value"] == 10000.0
