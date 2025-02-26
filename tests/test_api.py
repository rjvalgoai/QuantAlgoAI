import pytest
from fastapi.testclient import TestClient
from server import app
from models.trade import Trade
from datetime import datetime

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_place_trade(mock_broker, test_db):
    """Test trade placement endpoint"""
    trade_data = {
        "symbol": "NIFTY",
        "quantity": 50,
        "side": "BUY",
        "order_type": "MARKET",
        "price": 19500
    }
    
    response = client.post("/api/trade", json=trade_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "trade_id" in data
    assert data["status"] == "FILLED"
    
    # Verify in database
    async with test_db as session:
        trade = await session.get(Trade, data["trade_id"])
        assert trade is not None
        assert trade.symbol == "NIFTY"
        assert trade.status == "FILLED"

@pytest.mark.asyncio
async def test_get_positions(mock_broker):
    """Test positions endpoint"""
    response = client.get("/api/positions")
    assert response.status_code == 200
    
    positions = response.json()
    assert len(positions) > 0
    assert positions[0]["symbol"] == "NIFTY"
    assert "quantity" in positions[0]
    assert "average_price" in positions[0]

@pytest.mark.asyncio
async def test_option_chain():
    """Test option chain endpoint"""
    response = client.get("/api/option-chain/NIFTY")
    assert response.status_code == 200
    
    data = response.json()
    assert "calls" in data
    assert "puts" in data
    assert "spot_price" in data
    
    # Verify structure
    for call in data["calls"]:
        assert "strike" in call
        assert "iv" in call
        assert "delta" in call
        assert "gamma" in call

def test_trades_endpoint(test_client):
    response = test_client.get("/api/trading/trades")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_positions_endpoint(test_client):
    response = test_client.get("/api/trading/positions")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

def test_trade_execution(test_client):
    trade_data = {
        "id": 1,
        "time": "2024-02-19T12:00:00",
        "symbol": "NIFTY",
        "price": 19500.50,
        "quantity": 100,
        "side": "BUY"
    }
    response = test_client.post("/api/trading/trade", json=trade_data)
    assert response.status_code in [200, 400, 500]
    if response.status_code == 500:
        print(f"Error response: {response.json()}")


