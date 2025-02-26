from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import uuid
from dataclasses import dataclass
from core.logger import logger
from trading.brokers.angel_one import AngelOneAPI

class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

@dataclass
class Order:
    symbol: str
    quantity: int
    side: str  # BUY/SELL
    order_type: str  # MARKET/LIMIT
    price: Optional[float] = None
    status: str = "PENDING"
    order_id: Optional[str] = None
    timestamp: datetime = datetime.utcnow()

class OrderManager:
    def __init__(self, broker=None):
        self.broker = broker or AngelOneAPI()
        self.active_orders: Dict[str, Order] = {}
        self.filled_orders: Dict[str, Order] = {}
        self.orders = {}
    
    async def place_order(self, order: Order) -> Optional[str]:
        """Place order with broker"""
        try:
            order_params = {
                "symbol": order.symbol,
                "qty": order.quantity,
                "side": order.side,
                "type": order.order_type,
                "price": order.price
            }
            
            order_id = await self.broker.place_order(**order_params)
            if order_id:
                order.order_id = order_id
                order.status = "OPEN"
                self.active_orders[order_id] = order
                logger.info(f"Order placed successfully: {order_id}")
                return order_id
                
            return None
            
        except Exception as e:
            logger.error(f"Order placement failed: {e}")
            return None
    
    async def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order"""
        try:
            if order_id not in self.active_orders:
                return False
                
            success = await self.broker.cancel_order(order_id)
            if success:
                order = self.active_orders.pop(order_id)
                order.status = "CANCELLED"
                logger.info(f"Order cancelled: {order_id}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Order cancellation failed: {e}")
            return False
    
    def get_order(self, order_id: str) -> Optional[Order]:
        return self.active_orders.get(order_id)
    
    def get_active_orders(self, symbol: str) -> List[Order]:
        return [order for order in self.active_orders.values() if order.symbol == symbol]

    async def handle_order_update(self, update: Dict):
        """Handle order status updates"""
        try:
            order_id = update["order_id"]
            new_status = update["status"]
            
            if order_id in self.active_orders:
                order = self.active_orders[order_id]
                order.status = new_status
                
                if new_status == "FILLED":
                    self.active_orders.pop(order_id)
                    self.filled_orders[order_id] = order
                    
                logger.info(f"Order {order_id} status updated to {new_status}")
                
        except Exception as e:
            logger.error(f"Error handling order update: {e}") 