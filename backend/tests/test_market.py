import pytest
from app.market.types import TICKER_UNIVERSE, PriceTick, PricePoint
from app.market.cache import PriceCache
from app.market.sim_config import TICKER_CONFIG
from app.market.simulator import MarketSimulator


def test_ticker_universe_complete():
    assert len(TICKER_UNIVERSE) == 10
    expected = {"AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META", "JPM", "V", "NFLX"}
    assert set(TICKER_UNIVERSE) == expected


def test_price_cache_operations():
    cache = PriceCache(history_limit=5)
    tick1 = PriceTick(
        ticker="AAPL",
        price=150.0,
        prev_price=149.0,
        change=1.0,
        change_percent=0.67,
        direction="up",
        timestamp="2026-01-01T00:00:00Z",
    )
    cache.update(tick1)

    assert cache.latest("AAPL") == tick1
    history = cache.get_history("AAPL")
    assert len(history) == 1
    assert history[0].price == 150.0


def test_simulator_backfill_and_step():
    cache = PriceCache(history_limit=100)
    sim = MarketSimulator(cache)

    sim.backfill_history(num_ticks=50)

    for ticker in TICKER_UNIVERSE:
        history = cache.get_history(ticker)
        assert len(history) == 50
        latest = cache.latest(ticker)
        assert latest is not None
        assert latest.price > 0

    # Step simulation once
    ticks = sim.step()
    assert len(ticks) == 10
    for tick in ticks:
        assert tick.ticker in TICKER_UNIVERSE
        assert tick.price > 0
        assert tick.direction in ("up", "down", "flat")
