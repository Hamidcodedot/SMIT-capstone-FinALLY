import pytest
from app.db.connection import init_db
from app.market.cache import PriceCache
from app.market.types import PriceTick, TICKER_UNIVERSE
from app.watchlist.service import add_to_watchlist, get_watchlist, remove_from_watchlist


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_finally.db"
    monkeypatch.setenv("FINALLY_DB_PATH", str(test_db))
    import app.db.connection as db_conn
    monkeypatch.setattr(db_conn, "DB_PATH", test_db)
    init_db()
    yield test_db


@pytest.fixture
def cache():
    c = PriceCache()
    c.update(
        PriceTick(
            ticker="AAPL",
            price=195.0,
            prev_price=190.0,
            change=5.0,
            change_percent=2.63,
            direction="up",
            timestamp="2026-01-01T00:00:00Z",
        )
    )
    return c


def test_watchlist_seeded(cache):
    wl = get_watchlist(cache)
    assert len(wl) == 10
    tickers = [item["ticker"] for item in wl]
    assert "AAPL" in tickers
    aapl_item = next(item for item in wl if item["ticker"] == "AAPL")
    assert aapl_item["price"] == 195.0
    assert aapl_item["direction"] == "up"


def test_remove_and_add_watchlist(cache):
    remove_from_watchlist("AAPL")
    wl = get_watchlist(cache)
    assert len(wl) == 9
    assert "AAPL" not in [i["ticker"] for i in wl]

    # Re-add AAPL
    updated = add_to_watchlist("AAPL", cache)
    assert len(updated) == 10
    assert "AAPL" in [i["ticker"] for i in updated]


def test_add_unsupported_ticker_rejected(cache):
    with pytest.raises(ValueError, match="not supported"):
        add_to_watchlist("DOGE", cache)
