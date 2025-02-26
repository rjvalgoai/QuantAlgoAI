from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from datetime import datetime
from .models import TradeRequest, TradeResponse, PositionResponse
from core.trading_engine import TradingEngine
from core.auth import get_current_user
from core.logger import logger

router = APIRouter()
trading_engine = TradingEngine()

@router.post("/trade", response_model=TradeResponse)
async def place_trade(
    trade: TradeRequest,
    current_user = Depends(get_current_user)
):
    """Place a new trade"""
    try:
        result = await trading_engine.execute_trade(trade.dict())
        return TradeResponse(**result)
    except Exception as e:
        logger.error(f"Trade execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(current_user = Depends(get_current_user)):
    """Get current positions"""
    try:
        positions = await trading_engine.get_positions()
        return [PositionResponse(**pos) for pos in positions]
    except Exception as e:
        logger.error(f"Position fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/option-chain/{symbol}")
async def get_option_chain(
    symbol: str,
    current_user = Depends(get_current_user)
):
    """Get option chain analysis"""
    try:
        return await trading_engine.get_option_chain(symbol)
    except Exception as e:
        logger.error(f"Option chain analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 