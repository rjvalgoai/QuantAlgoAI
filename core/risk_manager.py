from typing import Dict, Optional, List
import numpy as np
from datetime import datetime, timedelta
from core.exceptions import RiskLimitError
from database.service import DatabaseService
from core.logger import logger

# Move Trade type hint to function level to avoid circular import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.trade import Trade

class RiskManager:
    """Risk management system"""
    
    def __init__(self):
        self.db = DatabaseService()
        self.risk_limits = {
            "max_position_size": 1000000,  # Max position size in base currency
            "max_daily_loss": 50000,       # Max daily loss
            "max_trade_size": 100000,      # Max single trade size
            "max_leverage": 5,             # Max leverage
            "min_margin": 0.2,             # Minimum margin requirement
            "max_concentration": 0.3,       # Max concentration in single asset
            "max_drawdown": 0.15           # Max drawdown threshold
        }
        self.max_position_size = 1000  # Maximum position size
        self.max_trade_value = 1000000  # Maximum trade value in rupees
        
    async def validate_trade(self, trade_data: Dict, user: Dict) -> bool:
        """Validate trade against risk limits"""
        try:
            # Get current positions and account info
            positions = await self.db.get_positions(user["id"])
            account = await self.db.get_account(user["id"])
            
            # Calculate trade value
            trade_value = trade_data["quantity"] * trade_data["price"]
            
            # Check trade size limit
            if trade_value > self.risk_limits["max_trade_size"]:
                raise RiskLimitError("Trade size exceeds limit")
                
            # Check position size limit
            total_exposure = sum(p["quantity"] * p["current_price"] for p in positions)
            if total_exposure + trade_value > self.risk_limits["max_position_size"]:
                raise RiskLimitError("Position size would exceed limit")
                
            # Check concentration limit
            symbol_exposure = sum(
                p["quantity"] * p["current_price"] 
                for p in positions 
                if p["symbol"] == trade_data["symbol"]
            )
            total_equity = account["balance"] + sum(p["unrealized_pnl"] for p in positions)
            concentration = (symbol_exposure + trade_value) / total_equity
            if concentration > self.risk_limits["max_concentration"]:
                raise RiskLimitError("Asset concentration would exceed limit")
                
            # Check daily loss limit
            daily_pnl = await self._calculate_daily_pnl(user["id"])
            if daily_pnl < -self.risk_limits["max_daily_loss"]:
                raise RiskLimitError("Daily loss limit reached")
                
            # Check drawdown
            drawdown = await self._calculate_drawdown(user["id"])
            if drawdown > self.risk_limits["max_drawdown"]:
                raise RiskLimitError("Drawdown limit reached")
                
            return True
            
        except RiskLimitError:
            raise
        except Exception as e:
            logger.error(f"Trade validation failed: {e}")
            return False
            
    async def _calculate_daily_pnl(self, user_id: str) -> float:
        """Calculate daily P&L"""
        try:
            today = datetime.utcnow().date()
            trades = await self.db.get_trades_by_date(user_id, today)
            
            realized_pnl = sum(t["pnl"] for t in trades if t["pnl"] is not None)
            positions = await self.db.get_positions(user_id)
            unrealized_pnl = sum(p["unrealized_pnl"] for p in positions)
            
            return realized_pnl + unrealized_pnl
            
        except Exception as e:
            logger.error(f"Daily P&L calculation failed: {e}")
            return 0.0
            
    async def _calculate_drawdown(self, user_id: str) -> float:
        """Calculate current drawdown"""
        try:
            # Get historical equity curve
            equity_history = await self.db.get_equity_history(user_id)
            if not equity_history:
                return 0.0
                
            equity_values = [e["equity"] for e in equity_history]
            peak = max(equity_values)
            current = equity_values[-1]
            
            return (peak - current) / peak if peak > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Drawdown calculation failed: {e}")
            return 0.0

    async def check_trade(self, trade: "Trade") -> bool:
        """Check if trade meets risk criteria"""
        try:
            # Check position size
            if trade.quantity > self.max_position_size:
                logger.warning(f"Trade quantity {trade.quantity} exceeds max size {self.max_position_size}")
                return False
                
            # Check trade value
            trade_value = trade.quantity * trade.price
            if trade_value > self.max_trade_value:
                logger.warning(f"Trade value {trade_value} exceeds max value {self.max_trade_value}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Risk check failed: {e}")
            return False 