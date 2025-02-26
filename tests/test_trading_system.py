import socketio
import time
import json
from datetime import datetime
import random
import sys
import pytest
from trading.analysis.option_chain import OptionChainAnalyzer
from core.trading_engine import TradingEngine
from models.trade import Trade
from ai_strategy.ensemble_model import EnsembleStrategy
from database.models import Position
from ai_strategy.ml_strategy import MLStrategy
from .conftest import MockModel
import pandas as pd
from unittest.mock import patch

class TradingSystem:
    def __init__(self):
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=5)
        self.orders = []
        self.running = True
        self.setup_socket_events()
        
    def setup_socket_events(self):
        @self.sio.event
        def connect():
            print("🟢 Trading System Connected!")

        @self.sio.event
        def disconnect():
            print("🔴 Trading System Disconnected!")
            self.running = False

        @self.sio.on('market_update')
        def on_market_update(data):
            print(f"\n📊 Market Update: {json.dumps(data, indent=2)}")
            self.process_market_data(data)

        @self.sio.on('order_confirmation')
        def on_order_confirmation(data):
            print(f"✅ Order Confirmed: {json.dumps(data, indent=2)}")
            self.orders.append(data)

    def process_market_data(self, data):
        try:
            if 'NIFTY' in data:
                nifty_price = data['NIFTY']['price']
                
                if nifty_price < 19480:
                    self.place_order('NIFTY', 'BUY', 50, nifty_price)
                elif nifty_price > 19520:
                    self.place_order('NIFTY', 'SELL', 50, nifty_price)
                    
        except Exception as e:
            print(f"❌ Processing Error: {e}")

    def place_order(self, symbol, order_type, quantity, price):
        order = {
            'symbol': symbol,
            'type': order_type,
            'quantity': quantity,
            'price': price,
            'timestamp': datetime.now().isoformat()
        }
        print(f"\n{'🟢' if order_type == 'BUY' else '🔴'} Placing {order_type} Order:")
        print(json.dumps(order, indent=2))
        self.sio.emit('place_order', order)

    def start(self):
        try:
            print("🚀 Starting Trading System...")
            self.sio.connect('http://localhost:5000')
            
            # Add timeout
            timeout = time.time() + 60  # 60 seconds timeout
            while self.running and time.time() < timeout:
                time.sleep(1)
                if not self.sio.connected:
                    print("⚠️ Connection lost, attempting to reconnect...")
                    break
                    
        except Exception as e:
            print(f"❌ Connection error: {e}")
        finally:
            self.sio.disconnect()
            if len(self.orders) > 0:
                print(f"\n📈 Trading Summary:")
                print(f"Total Orders: {len(self.orders)}")
            print("\n👋 Trading System Stopped")
            sys.exit(0)

@pytest.mark.asyncio
async def test_option_chain_analysis(sample_market_data):
    """Test option chain analysis"""
    analyzer = OptionChainAnalyzer()
    
    # Mock the option chain data
    analyzer.current_chain = pd.DataFrame({
        'strike': [19000, 19500, 20000],
        'call_oi': [1000, 2000, 1500],
        'put_oi': [1500, 1800, 1200],
        'call_price': [500, 250, 100],
        'put_price': [100, 250, 500]
    })
    
    analysis = await analyzer.analyze_chain(
        sample_market_data,
        spot_price=sample_market_data['price']
    )
    assert analysis is not None

@pytest.mark.asyncio
async def test_trade_execution(mock_broker, test_db):
    """Test trade execution"""
    engine = TradingEngine(broker=mock_broker)
    
    trade = Trade(
        id=1,
        symbol="NIFTY",
        quantity=50,
        side="BUY",
        price=19500,
        time=datetime.utcnow().isoformat(),
        status="PENDING",
        order_type="MARKET"
    )
    
    success = await engine.execute_trade(trade)
    assert success is True
    
    # Verify trade in database
    async with test_db as session:
        db_trade = await session.get(Trade, trade.id)
        assert db_trade is not None
        assert db_trade.symbol == "NIFTY"
        assert db_trade.status == "FILLED"

@pytest.mark.asyncio
async def test_ml_strategy(sample_market_data):
    """Test ML strategy signal generation"""
    from ai_strategy.feature_engineering import FeatureEngineer
    
    # Mock feature engineering
    def mock_create_features(*args, **kwargs):
        return pd.DataFrame({
            'rsi': [60],
            'macd': [0.5],
            'bollinger': [1.2]
        })
        
    with patch.object(FeatureEngineer, 'create_features', mock_create_features):
        strategy = MLStrategy("test_ml")
        strategy.model = MockModel()
        signal = await strategy.generate_signal(sample_market_data)
        assert signal is not None

@pytest.mark.asyncio
async def test_risk_management(mock_broker):
    """Test risk management system"""
    from core.risk_manager import RiskManager
    
    risk_manager = RiskManager()
    trade = Trade(
        id=1,
        symbol="NIFTY",
        quantity=5000,  # Large quantity
        side="BUY",
        price=19500,
        time=datetime.utcnow().isoformat()
    )
    
    # Should reject overlarge trade
    is_valid = await risk_manager.check_trade(trade)
    assert is_valid is False
    
    # Should accept normal trade
    trade.quantity = 50
    is_valid = await risk_manager.check_trade(trade)
    assert is_valid is True

@pytest.mark.asyncio
async def test_trading_workflow(mock_broker):
    """Test complete trading workflow"""
    engine = TradingEngine(broker=mock_broker)
    strategy = EnsembleStrategy("test_ensemble")
    
    # Mock the ML model in the strategy
    for sub_strategy in strategy.strategies:
        if isinstance(sub_strategy, MLStrategy):
            sub_strategy.model = MockModel()
    
    # Test market data
    market_data = {
        "symbol": "NIFTY",
        "price": 19500,
        "timestamp": "2024-02-20T10:00:00",
        "volume": 100000
    }
    
    signal = await strategy.generate_signal(market_data)
    assert signal is not None

if __name__ == "__main__":
    trading_system = TradingSystem()
    try:
        trading_system.start()
    except KeyboardInterrupt:
        print("\n⚠️ Manual interruption detected")
        trading_system.sio.disconnect()
        sys.exit(0) 
        print("\n⚠️ Manual interruption detected")
        trading_system.sio.disconnect()
        sys.exit(0) 