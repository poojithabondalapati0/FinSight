from fastapi.testclient import TestClient

from app.main import app


def test_health_and_research():
    with TestClient(app) as c:
        assert c.get("/health").json() == {"status": "ok"}
        r = c.post("/research", json={"ticker": "AAPL"})
        assert r.status_code == 200
        body = r.json()
        assert body["report"]["ticker"] == "AAPL"
        assert "not financial advice" in body["report"]["disclaimer"].lower()


def test_invalid_ticker_is_422():
    with TestClient(app) as c:
        r = c.post("/research", json={"ticker": "bad ticker!"})
        assert r.status_code == 422
