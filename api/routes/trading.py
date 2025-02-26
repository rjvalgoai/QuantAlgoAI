from fastapi import APIRouter, Depends, HTTPException, WebSocket
from typing import List, Dict, Optional
from datetime import datetime
from core.auth import get_current_user
from core.exceptions import TradingException
from models.trade import TradeRequest, TradeResponse
from services.trading_service import TradingService
from core.logger import logger

router = APIRouter()
trading_service = TradingService()

@router.post("/trade", response_model=TradeResponse)
async def place_trade(
    trade: TradeRequest,
    current_user = Depends(get_current_user)
):
    """Place a new trade"""
    try:
        result = await trading_service.execute_trade(trade.dict(), current_user)
        return TradeResponse(**result)
    except TradingException as e:
        logger.error(f"Trade execution failed: {e.message}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/positions")
async def get_positions(current_user = Depends(get_current_user)):
    """Get current positions"""
    try:
        return await trading_service.get_positions(current_user)
    except TradingException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/orders")
async def get_orders(
    status: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Get orders with optional status filter"""
    try:
        return await trading_service.get_orders(current_user, status)
    except TradingException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/orders/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    current_user = Depends(get_current_user)
):
    """Cancel an existing order"""
    try:
        return await trading_service.cancel_order(order_id, current_user)
    except TradingException as e:
        raise HTTPException(status_code=400, detail=str(e)) 