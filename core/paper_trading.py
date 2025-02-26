import random
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from .trading_engine import TradingEngine
from .risk_manager import RiskManager
from models.trade import Trade
from core.logger import logger
from dataclasses import dataclass

@dataclass
class PaperTrade:
    entry_price: float
    quantity: int
    trade_type: str  # BUY or SELL
    option_symbol: str
    strike: float
    option_type: str  # CE or PE
    entry_time: datetime
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    pnl: float = 0
    status: str = "OPEN"
    exit_reason: Optional[str] = None
    trailing_sl: Optional[float] = None
    target1: Optional[float] = None
    target2: Optional[float] = None

class PaperTrading:
    def __init__(self, initial_balance=100000):
        self.balance = initial_balance
        self.positions = 0

    def place_order(self, tradingsymbol, qty, transaction_type, price):
        """Executes simulated trades."""
        if transaction_type == "BUY":
            if self.balance >= price * qty:
                self.balance -= price * qty
                self.positions += qty
                print(f"📈 Bought {qty} of {tradingsymbol} at {price}")
            else:
                print("❌ Insufficient Balance")
        elif transaction_type == "SELL":
            if self.positions >= qty:
                self.balance += price * qty
                self.positions -= qty
                print(f"📉 Sold {qty} of {tradingsymbol} at {price}")
            else:
                print("❌ No Holdings to Sell")

    def check_balance(self):
        """Returns simulated account balance."""
        return self.balance

class PaperTradingSystem:
    """Paper trading simulation system"""
    
    def __init__(self, initial_capital: float = 1000000):
        self.trading_engine = TradingEngine()
        self.risk_manager = RiskManager()
        self.capital = initial_capital
        self.positions: Dict[str, Dict] = {}
        self.trades: List[Trade] = []
        self.active = False
        self.paper_trading_engine = PaperTradingEngine()
        
    async def start(self):
        """Start paper trading"""
        try:
            self.active = True
            logger.info("Paper trading system started")
            
            while self.active:
                await self._process_market_data()
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Paper trading system error: {e}")
            self.active = False
            
    async def stop(self):
        """Stop paper trading"""
        self.active = False
        logger.info("Paper trading system stopped")
        
    async def _process_market_data(self):
        """Process incoming market data"""
        try:
            # Get latest market data
            market_data = await self.trading_engine.get_market_data()
            
            # Generate signals
            signals = await self.trading_engine.generate_signals(market_data)
            
            # Execute paper trades
            for signal in signals:
                await self._execute_paper_trade(signal)
                
            # Update positions
            await self._update_positions(market_data)
            
        except Exception as e:
            logger.error(f"Market data processing failed: {e}")

    async def _execute_paper_trade(self, signal: Dict):
        """Execute a paper trade based on a trading signal"""
        try:
            # Process the signal
            result = self.paper_trading_engine.process_signal(signal, signal['spot_price'])
            
            if result:
                print(result)
            
        except Exception as e:
            logger.error(f"Paper trade execution failed: {e}")

    def _update_positions(self, market_data: Dict):
        """Update positions based on market data"""
        # Implementation needed
        pass

class PaperTradingEngine:
    def __init__(self):
        self.trades: List[PaperTrade] = []
        self.active_trades: List[PaperTrade] = []
        
    def process_signal(self, signal: Dict, spot_price: float, lot_size: int = 1) -> Optional[str]:
        """Process trading signal and execute paper trade"""
        try:
            # Calculate position size
            quantity = lot_size * signal.get('quantity', 1)
            
            # Create new paper trade
            trade = PaperTrade(
                entry_price=spot_price,
                quantity=quantity,
                trade_type=signal['action'],
                option_symbol=signal.get('option_symbol', ''),
                strike=signal.get('strike', spot_price),
                option_type='CE' if signal['action'] == 'BUY' else 'PE',
                entry_time=datetime.now()
            )
            
            # Set risk levels
            self._set_risk_levels(trade)
            
            self.trades.append(trade)
            self.active_trades.append(trade)
            
            return f"Entered {trade.trade_type} position at {trade.entry_price}"
            
        except Exception as e:
            logger.error(f"Paper trade execution failed: {e}")
            return None
            
    def _set_risk_levels(self, trade: PaperTrade):
        """Set stop loss and target levels"""
        sl_percent = 0.02
        target1_percent = 0.03
        target2_percent = 0.05
        
        if trade.trade_type == "BUY":
            trade.trailing_sl = trade.entry_price * (1 - sl_percent)
            trade.target1 = trade.entry_price * (1 + target1_percent)
            trade.target2 = trade.entry_price * (1 + target2_percent)
        else:
            trade.trailing_sl = trade.entry_price * (1 + sl_percent)
            trade.target1 = trade.entry_price * (1 - target1_percent)
            trade.target2 = trade.entry_price * (1 - target2_percent)

# Example Usage
if __name__ == "__main__":
    paper_trader = PaperTrading()
    paper_trader.place_order("NIFTY25FEBCE", qty=1, transaction_type="BUY", price=random.randint(17000, 18000))
    print(f"💰 Current Balance: {paper_trader.check_balance()}")
