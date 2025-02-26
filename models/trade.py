from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class TradeRequest(BaseModel):
    symbol: str
    quantity: float
    price: float
    side: str  # "buy" or "sell"
    order_type: str = "market"  # default to market order
    time_in_force: str = "gtc"  # good till cancelled
    
class TradeResponse(BaseModel):
    trade_id: str
    status: str
    executed_price: Optional[float] = None
    executed_quantity: Optional[float] = None
    timestamp: datetime = datetime.utcnow()
    details: Optional[Dict] = None 