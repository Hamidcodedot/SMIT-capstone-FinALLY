import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.db.connection import init_db


@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    test_db = tmp_path / "test_finally.db"
    monkeypatch.setenv("FINALLY_DB_PATH", str(test_db))
    import app.db.connection as db_conn
    monkeypatch.setattr(db_conn, "DB_PATH", test_db)
    init_db()
    yield test_db


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Wait for lifespan to enter
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "provider" in data


@pytest.mark.asyncio
async def test_portfolio_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Get initial portfolio
        res = await client.get("/api/portfolio")
        assert res.status_code == 200
        data = res.json()
        assert data["cash_balance"] == 10000.0

        # 2. Buy trade
        trade_res = await client.post("/api/portfolio/trade", json={
            "ticker": "AAPL",
            "quantity": 10.0,
            "side": "buy"
        })
        assert trade_res.status_code == 200
        trade_data = trade_res.json()
        assert trade_data["ticker"] == "AAPL"
        assert trade_data["side"] == "buy"
        assert trade_data["quantity"] == 10.0

        # 3. Portfolio history
        hist_res = await client.get("/api/portfolio/history")
        assert hist_res.status_code == 200
        assert len(hist_res.json()) >= 1


@pytest.mark.asyncio
async def test_watchlist_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Get watchlist
        res = await client.get("/api/watchlist")
        assert res.status_code == 200
        items = res.json()
        assert len(items) == 10

        # 2. Remove MSFT
        del_res = await client.delete("/api/watchlist/MSFT")
        assert del_res.status_code == 204

        # Verify removal
        res2 = await client.get("/api/watchlist")
        assert len(res2.json()) == 9

        # 3. Reject invalid ticker
        bad_add = await client.post("/api/watchlist", json={"ticker": "INVALID"})
        assert bad_add.status_code == 400


@pytest.mark.asyncio
async def test_chat_endpoints(monkeypatch):
    monkeypatch.setenv("LLM_MOCK", "true")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        chat_res = await client.post("/api/chat", json={"content": "buy 2 shares of MSFT"})
        assert chat_res.status_code == 200
        reply = chat_res.json()
        assert reply["role"] == "assistant"

        hist_res = await client.get("/api/chat")
        assert hist_res.status_code == 200
        assert len(hist_res.json()) >= 2
