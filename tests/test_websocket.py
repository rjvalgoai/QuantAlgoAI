import socketio
import time
import pytest
import json
import asyncio
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
from server import app
from core.logger import logger

sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server!")
    # Test order placement
    sio.emit('place_order', {
        'symbol': 'NIFTY',
        'type': 'BUY',
        'quantity': 50,
        'price': 19500
    })

@sio.event
def disconnect():
    print("Disconnected from server!")

@sio.on('market_update')
def on_market_update(data):
    print(f"Market Update: {data}")

@sio.on('order_confirmation')
def on_order_confirmation(data):
    print(f"Order Confirmation: {data}")

try:
    sio.connect('http://localhost:5000')
    time.sleep(5)  # Wait for responses
    sio.disconnect()
except Exception as e:
    print(f"Connection error: {e}")

@pytest.mark.asyncio
async def test_websocket_connection(test_client):
    """Test WebSocket connection and market data flow"""
    with test_client.websocket_connect("/ws") as websocket:
        # Test connection
        assert websocket.connected
        
        # Send test market data
        test_data = {
            "symbol": "NIFTY",
            "last_price": 19500,
            "timestamp": "2024-02-20T10:00:00"
        }
        
        await websocket.send_json(test_data)
        
        # Receive response
        response = await websocket.receive_json()
        assert response["symbol"] == "NIFTY"
        assert "analysis" in response
        assert "signals" in response

@pytest.mark.asyncio
async def test_market_data_processing():
    """Test market data processing and signal generation"""
    async with TestClient(app) as client:
        with client.websocket_connect("/ws") as websocket:
            # Send multiple market updates
            for price in [19500, 19550, 19600]:
                data = {
                    "symbol": "NIFTY",
                    "last_price": price,
                    "timestamp": "2024-02-20T10:00:00"
                }
                await websocket.send_json(data)
                
                # Verify response
                response = await websocket.receive_json()
                assert response["spot_price"] == price
                assert "analysis" in response
                
                # Check signal generation
                if "signals" in response and response["signals"]:
                    signal = response["signals"][0]
                    assert signal["symbol"] == "NIFTY"
                    assert signal["action"] in ["BUY", "SELL"]
                    assert 0 <= signal["confidence"] <= 1

@pytest.mark.asyncio
async def test_error_handling():
    """Test WebSocket error handling"""
    async with TestClient(app) as client:
        with client.websocket_connect("/ws") as websocket:
            # Send invalid data
            await websocket.send_json({"invalid": "data"})
            
            # Should receive error response
            response = await websocket.receive_json()
            assert "error" in response