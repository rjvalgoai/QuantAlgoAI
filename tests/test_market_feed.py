import socketio
import time
import random
from datetime import datetime

sio = socketio.Client()

def generate_market_data():
    return {
        "NIFTY": {
            "price": round(19500 + random.uniform(-50, 50), 2),
            "change": round(random.uniform(-1, 1), 2),
            "volume": random.randint(1000, 5000),
            "timestamp": datetime.now().isoformat()
        },
        "BANKNIFTY": {
            "price": round(44500 + random.uniform(-100, 100), 2),
            "change": round(random.uniform(-1, 1), 2),
            "volume": random.randint(2000, 8000),
            "timestamp": datetime.now().isoformat()
        }
    }

@sio.event
def connect():
    print("🟢 Market Feed Connected!")
    while True:
        try:
            market_data = generate_market_data()
            print(f"📊 Sending market update: {market_data}")
            sio.emit('market_update', market_data)
            time.sleep(1)  # Update every second
        except Exception as e:
            print(f"❌ Error: {e}")
            break

@sio.event
def disconnect():
    print("🔴 Market Feed Disconnected!")

try:
    sio.connect('http://localhost:5000')
    sio.wait()
except Exception as e:
    print(f"❌ Connection error: {e}") 