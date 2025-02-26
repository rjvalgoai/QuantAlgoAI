import sys
import os
# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import socketio
import json
from datetime import datetime
import time
from core.logger import logger

class TradingFlowTest:
    def __init__(self):
        self.sio = socketio.Client()
        self.market_data = {}
        self.orders = []
        self.connected = False
        self.last_trade_time = 0
        self.trade_cooldown = 5  # Seconds between trades
        
    def start(self):
        logger.info("🚀 Starting Trading Flow Test")
        
        @self.sio.event
        def connect():
            self.connected = True
            logger.info("✅ Connected to server")
            # Request initial market data
            self.sio.emit('request_market_data', {'symbols': ['NIFTY', 'BANKNIFTY']})
        
        @self.sio.event
        def disconnect():
            self.connected = False
            logger.info("❌ Disconnected from server")
        
        @self.sio.on('market_update')
        def on_market_update(data):
            self.market_data = data
            logger.info(f"\n📊 Market Update:")
            logger.info(json.dumps(data, indent=2))
            self.analyze_and_trade()
        
        @self.sio.on('order_confirmation')
        def on_order_confirmation(data):
            self.orders.append(data)
            logger.info(f"\n✅ Order Confirmed:")
            logger.info(json.dumps(data, indent=2))
        
        try:
            logger.info("Connecting to trading server...")
            self.sio.connect('http://localhost:5000')
            
            # Run test for 30 seconds
            timeout = time.time() + 30
            while time.time() < timeout:
                if not self.connected:
                    logger.warning("Reconnecting...")
                    try:
                        self.sio.connect('http://localhost:5000')
                    except:
                        pass
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("\n⚠️ Test stopped by user")
        except Exception as e:
            logger.error(f"❌ Error: {e}")
        finally:
            self.print_summary()
            if self.sio.connected:
                self.sio.disconnect()
    
    def analyze_and_trade(self):
        """Simple trading strategy with more frequent trades"""
        try:
            nifty_data = self.market_data.get('NIFTY', {})
            current_price = nifty_data.get('price')
            current_time = time.time()
            
            if not current_price:
                return
                
            # Check if enough time has passed since last trade
            if current_time - self.last_trade_time < self.trade_cooldown:
                return
                
            # Trading rules
            if current_price < 19480:  # Buy condition
                self.place_order('NIFTY', 'BUY', 50, current_price)
                self.last_trade_time = current_time
                logger.info(f"🟢 Buy Signal: Price {current_price} < 19480")
                
            elif current_price > 19520:  # Sell condition
                self.place_order('NIFTY', 'SELL', 50, current_price)
                self.last_trade_time = current_time
                logger.info(f"🔴 Sell Signal: Price {current_price} > 19520")
                
        except Exception as e:
            logger.error(f"Analysis error: {e}")
    
    def place_order(self, symbol, order_type, quantity, price):
        order = {
            'symbol': symbol,
            'type': order_type,
            'quantity': quantity,
            'price': price,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"\n{'🟢' if order_type == 'BUY' else '🔴'} Placing {order_type} Order at {price}:")
        logger.info(json.dumps(order, indent=2))
        
        self.sio.emit('place_order', order)
    
    def print_summary(self):
        logger.info("\n📈 Trading Summary")
        logger.info(f"Total Orders: {len(self.orders)}")
        
        if self.orders:
            logger.info("\nOrder History:")
            for order in self.orders:
                order_type = order['data']['type']
                price = order['data']['price']
                quantity = order['data']['quantity']
                timestamp = order['timestamp']
                emoji = '🟢' if order_type == 'BUY' else '🔴'
                logger.info(f"{emoji} {order_type}: {quantity} @ {price} ({timestamp})")
        
        if self.market_data:
            logger.info("\nLast Market Price:")
            nifty_price = self.market_data.get('NIFTY', {}).get('price')
            logger.info(f"NIFTY: {nifty_price}")

if __name__ == "__main__":
    test = TradingFlowTest()
    test.start() 