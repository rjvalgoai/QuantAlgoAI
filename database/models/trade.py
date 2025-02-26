from pydantic import BaseModel
from typing import Literal, Optional
from datetime import datetime

class Trade(BaseModel):
    id: int
    symbol: str
    quantity: int
    side: str  # BUY/SELL
    price: float
    time: str
    status: str = "PENDING"
    order_type: str = "MARKET"  # Add default order type
    
    # Add risk management fields
    stop_loss: Optional[float] = None
    target1: Optional[float] = None
    target2: Optional[float] = None
    trailing_sl: Optional[float] = None
    exit_price: Optional[float] = None
    exit_time: Optional[str] = None
    exit_reason: Optional[str] = None
    pnl: Optional[float] = None

    def calculate_risk_levels(self, sl_percent: float = 0.02, 
                            target1_percent: float = 0.03,
                            target2_percent: float = 0.05):
        """Calculate risk management levels"""
        if self.side == "BUY":
            self.stop_loss = self.price * (1 - sl_percent)
            self.target1 = self.price * (1 + target1_percent)
            self.target2 = self.price * (1 + target2_percent)
        else:  # SELL
            self.stop_loss = self.price * (1 + sl_percent)
            self.target1 = self.price * (1 - target1_percent)
            self.target2 = self.price * (1 - target2_percent)
        self.trailing_sl = self.stop_loss

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "time": datetime.utcnow().isoformat(),
                "symbol": "NIFTY",
                "price": 19500.50,
                "quantity": 100,
                "side": "BUY"
            }
        } 