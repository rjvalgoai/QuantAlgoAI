from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from decimal import Decimal
import logging
from .risk_manager import RiskManager
from .order_manager import OrderManager, Order
from ai_strategy.ml_strategy import MLStrategy
from .logger import logger
from trading.brokers.angel_one import AngelOneAPI
from trading.analysis.option_chain import OptionChainAnalyzer
from models.trade import Trade
from sqlalchemy.ext.asyncio import AsyncSession
from database.service import async_session  # Use async_session instead of engine
import os
from trading.brokers.paper_broker import PaperBroker
from core.config import settings
import pandas as pd

@dataclass
class Trade:
    symbol: str
    quantity: int
    price: float
    side: str  # BUY or SELL
    timestamp: datetime
    status: str = "PENDING"
    order_type: str = "MARKET"  # MARKET, LIMIT, STOP
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    trade_id: Optional[str] = None

class Position:
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.quantity = 0
        self.average_price = 0.0
        self.realized_pnl = 0.0
        self.unrealized_pnl = 0.0

class TradingEngine:
    def __init__(self):
        # Initialize broker based on mode
        if settings.TRADING_MODE == "paper":
            self.broker = PaperBroker()
            logger.info("Starting in paper trading mode")
        else:
            self.broker = AngelOneAPI()
            logger.info("Starting in live trading mode")
            
        self.risk_manager = RiskManager()
        self.order_manager = OrderManager(broker=self.broker)
        self.strategies = {}
        self.analyzer = OptionChainAnalyzer()
        self.active_trades = {}
        self.last_price = None
        # Initialize price history as empty DataFrame with timestamp index
        self.price_history = pd.DataFrame(columns=['price'])
    
    def get_trade(self, trade_id: str):
        """Get a specific trade by ID"""
        return self.trades.get(trade_id)

    def get_trades(self):
        """Get all trades"""
        return list(self.trades.values())

    async def execute_trade(self, trade: Trade) -> bool:
        """Execute a trade with risk checks"""
        try:
            # Check risk limits
            if not await self.risk_manager.check_trade(trade):
                logger.warning(f"Trade {trade.trade_id} rejected by risk manager")
                return False
                
            # Place order
            order_id = await self.order_manager.place_order(trade)
            if not order_id:
                return False
                
            # Store trade
            trade.order_id = order_id
            trade.status = "OPEN"
            trade.timestamp = datetime.utcnow()
            
            async with async_session() as db:
                db.add(trade)
                await db.commit()
                
            self.active_trades[trade.trade_id] = trade
            return True
            
        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return False
    
    def get_position_value(self, symbol: str, current_price: float) -> float:
        position = self.positions.get(symbol)
        if not position:
            return 0.0
        return position["quantity"] * current_price
    
    def calculate_pnl(self, symbol: str, current_price: float) -> Dict[str, float]:
        position = self.positions.get(symbol)
        if not position:
            return {"realized": 0.0, "unrealized": 0.0, "total": 0.0}
        
        unrealized = (current_price - position["average_price"]) * position["quantity"]
        return {
            "realized": position["realized_pnl"],
            "unrealized": unrealized,
            "total": position["realized_pnl"] + unrealized
        }

    def add_strategy(self, symbol: str, strategy: MLStrategy):
        """Add a trading strategy for a symbol"""
        self.strategies[symbol] = strategy
        
    async def process_market_data(self, market_data: Dict[str, Any]):
        """Process new market data and generate signals"""
        symbol = market_data["symbol"]
        if symbol in self.strategies:
            strategy = self.strategies[symbol]
            signal = strategy.update(market_data)
            
            if signal:
                # Execute trade based on signal
                trade = Trade(
                    symbol=symbol,
                    quantity=signal["position_size"],
                    price=signal["price"],
                    side=signal["action"],
                    timestamp=signal["timestamp"]
                )
                await self.execute_trade(trade)

    async def execute_strategy(self):
        try:
            # Get market data
            nifty_chain = self.broker.get_option_chain("NIFTY")
            
            # Analyze for signals
            signals = self.analyzer.analyze_chain(nifty_chain)
            
            # Apply risk management
            for signal in signals:
                position_size = self.risk_manager.calculate_position_size(
                    signal['entry_price'],
                    signal['stop_loss']
                )
                
                if position_size > 0:
                    order = await self.place_trade(
                        symbol=signal['symbol'],
                        quantity=position_size,
                        side=signal['side']
                    )
                    logger.info(f"Order placed: {order}")
                    
        except Exception as e:
            logger.error(f"Strategy execution error: {str(e)}") 

    async def get_positions(self) -> List[Dict]:
        """Get current positions"""
        try:
            positions = await self.order_manager.get_positions()
            return [
                {
                    "symbol": pos.symbol,
                    "quantity": pos.quantity,
                    "avg_price": pos.average_price,
                    "pnl": pos.unrealized_pnl
                }
                for pos in positions
            ]
        except Exception as e:
            logger.error(f"Error getting positions: {e}")
            return [] 

    def calculate_position_size(self, signal: Dict, account_value: float) -> int:
        """Calculate position size based on risk and confidence"""
        try:
            # Base position sizing on account value and risk per trade
            risk_percent = 0.02  # 2% risk per trade
            max_risk = account_value * risk_percent
            
            # Adjust size based on signal confidence
            confidence = signal.get('confidence', 0.5)
            adjusted_size = int(max_risk * confidence)
            
            # Apply position limits
            min_size = 1
            max_size = int(account_value * 0.1)  # Max 10% of account
            
            return max(min_size, min(adjusted_size, max_size))
            
        except Exception as e:
            logger.error(f"Position size calculation failed: {e}")
            return 1  # Default to minimum size 

    async def get_market_data(self, symbol: str = "NIFTY") -> Dict:
        """Get market data from broker"""
        try:
            market_data = await self.broker.get_market_data(symbol)
            if market_data:
                # Update price history using concat instead of append
                new_data = pd.DataFrame(
                    {'price': [market_data['price']]},
                    index=[pd.Timestamp.now()]
                )
                self.price_history = pd.concat([
                    self.price_history, 
                    new_data
                ]).last('1D')
                
                # Add indicators
                self._add_indicators(market_data)
                
                # Update last price
                self.last_price = market_data['price']
                
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return None
            
    def _add_indicators(self, market_data: Dict):
        """Add technical indicators to market data"""
        try:
            if len(self.price_history) > 0:
                # Calculate on price history DataFrame
                prices = self.price_history['price']
                
                # Add basic indicators
                market_data['MA10'] = prices.rolling(10).mean().iloc[-1] if len(prices) >= 10 else prices.mean()
                market_data['EMA10'] = prices.ewm(span=10).mean().iloc[-1] if len(prices) >= 10 else prices.mean()
                
                # Add RSI if enough data
                if len(prices) > 14:
                    delta = prices.diff()
                    gain = delta.where(delta > 0, 0).rolling(14).mean()
                    loss = -delta.where(delta < 0, 0).rolling(14).mean()
                    rs = gain / loss
                    market_data['RSI'] = 100 - (100 / (1 + rs)).iloc[-1]
                
        except Exception as e:
            logger.error(f"Error calculating indicators: {e}") 

    async def generate_signals(self, market_data: Dict) -> List[Dict]:
        """Generate trading signals from market data"""
        try:
            signals = []
            
            # Calculate technical indicators
            if market_data and 'price' in market_data:
                price = market_data['price']
                
                # Simple MA crossover strategy
                if self.last_price and price > self.last_price:
                    signals.append({
                        'action': 'BUY',
                        'strategy': 'MA_CROSS',
                        'confidence': 0.8,
                        'price': price
                    })
                elif self.last_price and price < self.last_price:
                    signals.append({
                        'action': 'SELL',
                        'strategy': 'MA_CROSS', 
                        'confidence': 0.8,
                        'price': price
                    })
                    
                self.last_price = price
                
            return signals
            
        except Exception as e:
            logger.error(f"Signal generation failed: {e}")
            return [] 