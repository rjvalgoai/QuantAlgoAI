from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from database.models import Position
from typing import List
from pydantic import BaseModel

router = APIRouter()

class PositionResponse(BaseModel):
    id: int
    symbol: str
    quantity: int
    average_price: float
    current_price: float | None
    unrealized_pnl: float
    realized_pnl: float
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[PositionResponse])
async def get_positions(db: Session = Depends(get_db)):
    positions = db.query(Position).all()
    return positions 