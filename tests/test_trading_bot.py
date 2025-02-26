import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import socketio
import json
from datetime import datetime
import time
from core.logger import logger

class TradingBot:
    def __init__(self):
        print("Initializing Trading Bot...")  # Debug print
        self.sio = socketio.Client(reconnection=True, reconnection_delay=1)
        self.positions = {}
        self.orders = []
        self.last_price = None
        self.running = True
        self.connected = False
        
    def start(self):
        print("Starting Trading Bot...")  # Debug print
        
        @self.sio.event
        def connect():
            print("Socket Connected!")  # Debug print
            self.connected = True
            self.sio.emit('request_market_data', {'symbols': ['NIFTY', 'BANKNIFTY']})

        @self.sio.event
        def connect_error(data):
            print(f"Connection Error: {data}")  # Debug print

        @self.sio.event
        def disconnect():
            print("Socket Disconnected!")  # Debug print
            self.connected = False

        @self.sio.on('market_update')
        def on_market_update(data):
            print(f"Received market update: {data}")  # Debug print
            try:
                nifty_data = data.get('NIFTY', {})
                current_price = nifty_data.get('price')
                
                logger.info(f"📊 NIFTY: {current_price}")
                
                if current_price and self.last_price:
                    self.analyze_price_movement(current_price)
                
                self.last_price = current_price
                
            except Exception as e:
                logger.error(f"❌ Error processing market data: {e}")

        @self.sio.on('order_confirmation')
        def on_order_confirmation(data):
            logger.info(f"✅ Order Confirmed: {json.dumps(data, indent=2)}")
            self.orders.append(data)
            
        try:
            print("Attempting to connect to server...")  # Debug print
            self.sio.connect('http://localhost:5000', wait_timeout=10)
            
            print("Connection attempt completed")  # Debug print
            
            # Keep bot running with heartbeat
            start_time = time.time()
            while self.running:
                if not self.connected:
                    print("Not connected, attempting reconnection...")  # Debug print
                    try:
                        self.sio.connect('http://localhost:5000', wait_timeout=10)
                    except Exception as e:
                        print(f"Reconnection error: {e}")
                
                # Request market data periodically
                if self.connected:
                    self.sio.emit('request_market_data', {'symbols': ['NIFTY', 'BANKNIFTY']})
                
                # Print heartbeat every 30 seconds
                if time.time() - start_time > 30:
                    logger.info("💓 Bot is alive...")
                    start_time = time.time()
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("Bot stopped by user")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.print_summary()
            if self.sio.connected:
                self.sio.disconnect()
            print("Bot shutdown complete")

    def analyze_price_movement(self, current_price):
        """Simple trading strategy"""
        if not self.last_price:
            return
            
        price_change = current_price - self.last_price
        
        if abs(price_change) >= 10:  # Minimum price movement threshold
            if price_change > 0:
                self.place_order("NIFTY", "BUY", 50, current_price)
            else:
                self.place_order("NIFTY", "SELL", 50, current_price)

    def place_order(self, symbol, order_type, quantity, price):
        order = {
            'symbol': symbol,
            'type': order_type,
            'quantity': quantity,
            'price': price,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"\n{'🟢' if order_type == 'BUY' else '🔴'} Placing {order_type} Order:")
        logger.info(json.dumps(order, indent=2))
        
        self.sio.emit('place_order', order)

    def print_summary(self):
        logger.info("\n📈 Trading Summary")
        logger.info(f"Total Orders: {len(self.orders)}")
        if self.orders:
            logger.info("\nLast 5 Orders:")
            for order in self.orders[-5:]:
                logger.info(json.dumps(order, indent=2))

if __name__ == "__main__":
    print("Starting main...")  # Debug print
    bot = TradingBot()
    bot.start() 