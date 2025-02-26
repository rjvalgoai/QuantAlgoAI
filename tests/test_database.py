import pytest
from datetime import datetime
from database.service import DatabaseService
from models.trade import Trade
from models.position import Position

@pytest.mark.asyncio
async def test_create_trade(test_db):
    """Test trade creation in database"""
    trade_data = {
        "symbol": "NIFTY",
        "quantity": 50,
        "entry_price": 19500,
        "side": "BUY",
        "status": "OPEN",
        "strategy": "test_strategy",
        "entry_time": datetime.utcnow()
    }
    
    # Create trade
    trade = await DatabaseService.create_trade(trade_data)
    assert trade is not None
    assert trade.symbol == "NIFTY"
    assert trade.status == "OPEN"
    
    # Verify in database
    async with test_db as session:
        db_trade = await session.get(Trade, trade.id)
        assert db_trade is not None
        assert db_trade.symbol == trade.symbol

@pytest.mark.asyncio
async def test_update_position(test_db):
    """Test position update in database"""
    position_data = {
        "symbol": "NIFTY",
        "quantity": 50,
        "average_price": 19500
    }
    
    # Create/update position
    position = await DatabaseService.update_position(position_data)
    assert position is not None
    assert position.symbol == "NIFTY"
    
    # Update position
    position_data["quantity"] = 100
    updated_position = await DatabaseService.update_position(position_data)
    assert updated_position.quantity == 100 