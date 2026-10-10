import pytest
from app.chat.actions import parse_llm_json_response, execute_llm_actions, persist_chat_turn
from app.chat.context import get_chat_history
from app.chat.llm import process_chat_message
from app.db.connection import init_db
from app.market.cache import PriceCache
from app.market.types import PriceTick
from app.portfolio.valuation import get_portfolio


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
            price=200.0,
            prev_price=200.0,
            change=0.0,
            change_percent=0.0,
            direction="flat",
            timestamp="2026-01-01T00:00:00Z",
        )
    )
    return c


def test_parse_llm_json_response_with_fences():
    text = """```json
{
  "message": "I recommend taking a 5 share position in AAPL.",
  "trades": [{"ticker": "AAPL", "side": "buy", "quantity": 5}],
  "watchlist_changes": []
}
```"""
    parsed = parse_llm_json_response(text)
    assert parsed["message"] == "I recommend taking a 5 share position in AAPL."
    assert len(parsed["trades"]) == 1
    assert parsed["trades"][0]["ticker"] == "AAPL"


def test_parse_llm_json_plain():
    text = '{"message": "Hello", "trades": [], "watchlist_changes": []}'
    parsed = parse_llm_json_response(text)
    assert parsed["message"] == "Hello"


def test_execute_llm_actions(cache):
    parsed = {
        "message": "Buying 2 AAPL",
        "trades": [{"ticker": "AAPL", "side": "buy", "quantity": 2.0}],
        "watchlist_changes": [{"ticker": "NFLX", "action": "remove"}],
    }
    actions = execute_llm_actions(cache, parsed)
    assert len(actions) == 2
    assert actions[0]["type"] == "trade"
    assert actions[0]["success"] is True
    assert actions[1]["type"] == "watchlist"
    assert actions[1]["success"] is True

    # Portfolio cash should be 10000 - (2 * 200) = 9600
    p = get_portfolio(cache)
    assert p["cash_balance"] == 9600.0


@pytest.mark.asyncio
async def test_mock_chat_flow(cache, monkeypatch):
    monkeypatch.setenv("LLM_MOCK", "true")
    res = await process_chat_message("buy 5 shares of AAPL", cache)
    assert res["role"] == "assistant"
    assert res["actions"] is not None
    assert len(res["actions"]) == 1
    assert res["actions"][0]["type"] == "trade"
    assert res["actions"][0]["success"] is True

    history = get_chat_history()
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"
