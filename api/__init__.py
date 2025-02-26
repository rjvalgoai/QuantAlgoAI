from fastapi import APIRouter
from ws import SmartWebSocket  # Changed from websocket to ws

# Create the routers
trade_router = APIRouter()
market_router = APIRouter()

# Basic endpoints
@trade_router.get("/status")
async def trade_status():
    return {"status": "Trading system operational"}

@market_router.get("/status")
async def market_status():
    return {"status": "Market data feed operational"}

__all__ = ['SmartWebSocket'] 