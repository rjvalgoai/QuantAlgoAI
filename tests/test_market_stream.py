import socketio
import time
import sys
import json

class MarketDataTester:
    def __init__(self):
        self.sio = socketio.Client()
        self.received_data = False
        
    def start(self):
        print("🚀 Starting Market Data Test...")
        
        @self.sio.event
        def connect():
            print("✅ Connected to server")
            # Request market data explicitly
            self.sio.emit('request_market_data', {'symbols': ['NIFTY', 'BANKNIFTY']})
            print("📊 Requested market data")
            
        @self.sio.event
        def disconnect():
            print("❌ Disconnected from server")
            
        @self.sio.on('market_update')
        def on_market_data(data):
            print(f"\n📈 Received market update:")
            print(json.dumps(data, indent=2))
            self.received_data = True
            
        try:
            self.sio.connect('http://localhost:5000')
            print("Waiting for market data...")
            
            # Wait for up to 10 seconds for data
            timeout = time.time() + 10
            while not self.received_data and time.time() < timeout:
                time.sleep(1)
                
            if not self.received_data:
                print("⚠️ No market data received within timeout")
            
            self.sio.disconnect()
            
        except Exception as e:
            print(f"❌ Error: {e}")
            
if __name__ == "__main__":
    tester = MarketDataTester()
    tester.start() 