from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from database.models import Trade
from typing import List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class TradeResponse(BaseModel):
    id: int
    symbol: str
    order_type: str
    quantity: int
    price: float
    status: str
    timestamp: datetime
    realized_pnl: float | None
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[TradeResponse])
async def get_trades(db: Session = Depends(get_db)):
    trades = db.query(Trade).all()
    return trades 