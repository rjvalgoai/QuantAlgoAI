import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import socketio
import json
from datetime import datetime
import time
from decimal import Decimal
from core.logger import logger

class Position:
    def __init__(self, symbol, entry_price, quantity, position_type):
        self.symbol = symbol
        self.entry_price = Decimal(str(entry_price))
        self.quantity = quantity
        self.position_type = position_type  # 'LONG' or 'SHORT'
        self.stop_loss = None
        self.take_profit = None
        self.entry_time = datetime.now()
        self.pnl = Decimal('0.0')
        
    def update_pnl(self, current_price):
        current_price = Decimal(str(current_price))
        if self.position_type == 'LONG':
            self.pnl = (current_price - self.entry_price) * self.quantity
        else:  # SHORT
            self.pnl = (self.entry_price - current_price) * self.quantity
            
    def __str__(self):
        return (f"{self.position_type} {self.quantity} {self.symbol} @ {self.entry_price:.2f} "
                f"(P&L: {self.pnl:.2f})")

class RiskManager:
    def __init__(self):
        self.max_position_size = 100  # Maximum lots
        self.max_risk_per_trade = Decimal('5000')  # Maximum risk in INR
        self.max_daily_loss = Decimal('15000')  # Maximum daily loss
        self.daily_loss = Decimal('0')
        
    def calculate_position_size(self, price, stop_loss):
        risk_per_unit = abs(Decimal(str(price)) - Decimal(str(stop_loss)))
        if risk_per_unit == 0:
            return 0
        
        size = int(self.max_risk_per_trade / risk_per_unit)
        return min(size, self.max_position_size)
        
    def can_take_trade(self, risk_amount):
        return (self.daily_loss + risk_amount) <= self.max_daily_loss

class AdvancedTradingSystem:
    def __init__(self):
        self.sio = socketio.Client()
        self.market_data = {}
        self.positions = {}  # symbol -> Position
        self.orders = []
        self.connected = False
        self.last_trade_time = 0
        self.trade_cooldown = 5
        self.risk_manager = RiskManager()
        self.daily_pnl = Decimal('0')
        
        # Strategy parameters
        self.stop_loss_pct = Decimal('0.005')  # 0.5%
        self.take_profit_pct = Decimal('0.015')  # 1.5%
        
    def start(self):
        logger.info("🚀 Starting Advanced Trading System")
        
        @self.sio.event
        def connect():
            self.connected = True
            logger.info("✅ Connected to server")
            self.sio.emit('request_market_data', {'symbols': ['NIFTY', 'BANKNIFTY']})
        
        @self.sio.event
        def disconnect():
            self.connected = False
            logger.info("❌ Disconnected from server")
        
        @self.sio.on('market_update')
        def on_market_update(data):
            self.market_data = data
            self.update_positions()
            self.check_exit_conditions()
            self.analyze_and_trade()
        
        @self.sio.on('order_confirmation')
        def on_order_confirmation(data):
            self.process_order_confirmation(data)
        
        try:
            self.sio.connect('http://localhost:5000')
            timeout = time.time() + 300  # Run for 5 minutes
            while time.time() < timeout:
                if not self.connected:
                    try:
                        self.sio.connect('http://localhost:5000')
                    except:
                        time.sleep(1)
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("\n⚠️ Trading stopped by user")
        finally:
            self.print_summary()
            if self.sio.connected:
                self.sio.disconnect()

    def update_positions(self):
        """Update P&L for all positions"""
        for symbol, position in self.positions.items():
            current_price = self.get_current_price(symbol)
            if current_price:
                position.update_pnl(current_price)
                
    def check_exit_conditions(self):
        """Check stop-loss and take-profit conditions"""
        for symbol, position in list(self.positions.items()):
            current_price = self.get_current_price(symbol)
            if not current_price:
                continue
                
            if position.position_type == 'LONG':
                if current_price <= position.stop_loss:
                    self.close_position(symbol, 'Stop Loss Hit')
                elif current_price >= position.take_profit:
                    self.close_position(symbol, 'Take Profit Hit')
            else:  # SHORT
                if current_price >= position.stop_loss:
                    self.close_position(symbol, 'Stop Loss Hit')
                elif current_price <= position.take_profit:
                    self.close_position(symbol, 'Take Profit Hit')

    def analyze_and_trade(self):
        """Enhanced trading strategy"""
        try:
            for symbol in ['NIFTY', 'BANKNIFTY']:
                if symbol in self.positions:
                    continue  # Already in position
                    
                current_price = self.get_current_price(symbol)
                if not current_price:
                    continue
                
                # Calculate indicators (simplified example)
                if symbol == 'NIFTY':
                    if current_price < 19480:
                        self.enter_position(symbol, 'LONG', current_price)
                    elif current_price > 19520:
                        self.enter_position(symbol, 'SHORT', current_price)
                
        except Exception as e:
            logger.error(f"Analysis error: {e}")

    def enter_position(self, symbol, position_type, price):
        """Enter new position with risk management"""
        try:
            price = Decimal(str(price))
            stop_loss = price * (1 - self.stop_loss_pct) if position_type == 'LONG' else price * (1 + self.stop_loss_pct)
            take_profit = price * (1 + self.take_profit_pct) if position_type == 'LONG' else price * (1 - self.take_profit_pct)
            
            # Calculate position size based on risk
            quantity = self.risk_manager.calculate_position_size(price, stop_loss)
            if quantity == 0:
                return
            
            # Check if we can take the risk
            risk_amount = abs(price - stop_loss) * quantity
            if not self.risk_manager.can_take_trade(risk_amount):
                logger.warning(f"❌ Cannot take trade: Daily risk limit reached")
                return
            
            # Place the order
            order = {
                'symbol': symbol,
                'type': 'BUY' if position_type == 'LONG' else 'SELL',
                'quantity': quantity,
                'price': float(price),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"\n{'🟢' if position_type == 'LONG' else '🔴'} Opening {position_type} position:")
            logger.info(json.dumps(order, indent=2))
            
            self.sio.emit('place_order', order)
            
            # Create position object
            position = Position(symbol, price, quantity, position_type)
            position.stop_loss = stop_loss
            position.take_profit = take_profit
            self.positions[symbol] = position
            
        except Exception as e:
            logger.error(f"Error entering position: {e}")

    def close_position(self, symbol, reason):
        """Close existing position"""
        try:
            position = self.positions[symbol]
            current_price = self.get_current_price(symbol)
            
            if not current_price:
                return
                
            order = {
                'symbol': symbol,
                'type': 'SELL' if position.position_type == 'LONG' else 'BUY',
                'quantity': position.quantity,
                'price': float(current_price),
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"\n{'🔴' if position.position_type == 'LONG' else '🟢'} Closing position ({reason}):")
            logger.info(json.dumps(order, indent=2))
            
            self.sio.emit('place_order', order)
            
            # Update daily P&L
            position.update_pnl(current_price)
            self.daily_pnl += position.pnl
            self.risk_manager.daily_loss -= position.pnl
            
            # Remove position
            del self.positions[symbol]
            
        except Exception as e:
            logger.error(f"Error closing position: {e}")

    def get_current_price(self, symbol):
        """Get current price for symbol"""
        try:
            return Decimal(str(self.market_data.get(symbol, {}).get('price', 0)))
        except:
            return None

    def process_order_confirmation(self, data):
        """Process order confirmation"""
        self.orders.append(data)
        logger.info(f"\n✅ Order Confirmed:")
        logger.info(json.dumps(data, indent=2))

    def print_summary(self):
        """Print trading session summary"""
        logger.info("\n📊 Trading Session Summary")
        logger.info("=" * 40)
        logger.info(f"Total Orders: {len(self.orders)}")
        logger.info(f"Daily P&L: {self.daily_pnl:.2f}")
        logger.info(f"Open Positions: {len(self.positions)}")
        
        if self.positions:
            logger.info("\nOpen Positions:")
            for symbol, position in self.positions.items():
                logger.info(f"- {position}")
        
        if self.orders:
            logger.info("\nOrder History:")
            for order in self.orders:
                order_type = order['data']['type']
                price = order['data']['price']
                quantity = order['data']['quantity']
                timestamp = order['timestamp']
                emoji = '🟢' if order_type == 'BUY' else '🔴'
                logger.info(f"{emoji} {order_type}: {quantity} @ {price} ({timestamp})")

if __name__ == "__main__":
    trading_system = AdvancedTradingSystem()
    trading_system.start() 