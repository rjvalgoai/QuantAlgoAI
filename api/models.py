from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from decimal import Decimal

class TradeRequest(BaseModel):
    """Trade request validation model"""
    symbol: str = Field(..., min_length=1, max_length=10)
    quantity: int = Field(..., gt=0)
    side: str = Field(..., regex="^(BUY|SELL)$")
    order_type: str = Field(..., regex="^(MARKET|LIMIT)$")
    price: Optional[float] = Field(None, gt=0)
    stop_loss: Optional[float] = Field(None, gt=0)
    take_profit: Optional[float] = Field(None, gt=0)
    
    @validator("price")
    def validate_price(cls, v, values):
        if values.get("order_type") == "LIMIT" and v is None:
            raise ValueError("Price is required for LIMIT orders")
        return v

class TradeResponse(BaseModel):
    """Trade response model"""
    trade_id: str
    symbol: str
    quantity: int
    side: str
    price: float
    status: str
    timestamp: datetime
    
class PositionResponse(BaseModel):
    """Position response model"""
    symbol: str
    quantity: int
    average_price: float
    current_price: float
    unrealized_pnl: float
    realized_pnl: float
    last_update: datetime

class OptionChainResponse(BaseModel):
    """Option chain response model"""
    calls: List[Dict]
    puts: List[Dict]
    spot_price: float
    timestamp: datetime 