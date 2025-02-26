from typing import Dict, List
import yfinance as yf
from datetime import datetime
import asyncio
from core.logger import logger
import numpy as np

class PaperBroker:
    def __init__(self):
        self.positions = {}
        self.orders = {}
        self.balance = 1000000  # Start with 10L virtual capital
        
    async def get_market_data(self, symbol: str) -> Dict:
        """Get real market data from yfinance"""
        try:
            # Map symbol to yfinance format
            yf_symbol = "^NSEI" if symbol == "NIFTY" else symbol
            
            ticker = yf.Ticker(yf_symbol)
            data = ticker.history(period="1d", interval="5m")
            
            if len(data) > 0:
                latest = data.iloc[-1]
                return {
                    "symbol": symbol,
                    "price": float(latest["Close"]),
                    "high": float(latest["High"]),
                    "low": float(latest["Low"]), 
                    "volume": int(latest["Volume"]),
                    "timestamp": datetime.now().isoformat()
                }
                
            # Return simulated data if no live data
            return self._get_simulated_data(symbol)
                
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            # Return simulated data as fallback
            return self._get_simulated_data(symbol)
            
    def _get_simulated_data(self, symbol: str) -> Dict:
        """Generate simulated market data"""
        # Add small random change to last price
        if not hasattr(self, 'last_price'):
            self.last_price = 19500.0
        else:
            self.last_price *= (1 + np.random.normal(0, 0.001))
            
        return {
            "symbol": symbol,
            "price": self.last_price,
            "high": self.last_price * 1.002,
            "low": self.last_price * 0.998,
            "volume": 100000,
            "timestamp": datetime.now().isoformat()
        }
            
    async def place_order(self, order: Dict) -> str:
        """Simulate order placement"""
        order_id = f"PAPER_{len(self.orders) + 1}"
        self.orders[order_id] = {
            **order,
            "status": "COMPLETE",
            "filled_price": order["price"],
            "timestamp": datetime.now().isoformat()
        }
        logger.info(f"Paper trade executed: {order}")
        return order_id 