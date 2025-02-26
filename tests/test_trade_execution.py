import socketio
import time
import json
from datetime import datetime

sio = socketio.Client()
orders = []

def place_order(symbol, order_type, quantity, price):
    order = {
        'symbol': symbol,
        'type': order_type,
        'quantity': quantity,
        'price': price,
        'timestamp': datetime.now().isoformat()
    }
    sio.emit('place_order', order)
    return order

@sio.event
def connect():
    print("🟢 Trade Execution Connected!")

@sio.event
def disconnect():
    print("🔴 Trade Execution Disconnected!")

@sio.on('market_update')
def on_market_update(data):
    try:
        nifty_price = data['NIFTY']['price']
        banknifty_price = data['BANKNIFTY']['price']
        
        # Simple trading logic
        if nifty_price < 19480:  # Buy condition
            order = place_order('NIFTY', 'BUY', 50, nifty_price)
            print(f"🟢 BUY Order: {json.dumps(order, indent=2)}")
            
        elif nifty_price > 19520:  # Sell condition
            order = place_order('NIFTY', 'SELL', 50, nifty_price)
            print(f"🔴 SELL Order: {json.dumps(order, indent=2)}")

    except Exception as e:
        print(f"❌ Error processing market update: {e}")

@sio.on('order_confirmation')
def on_order_confirmation(data):
    print(f"✅ Order Confirmed: {json.dumps(data, indent=2)}")
    orders.append(data)

try:
    sio.connect('http://localhost:5000')
    sio.wait()
except Exception as e:
    print(f"❌ Connection error: {e}")
finally:
    if len(orders) > 0:
        print(f"\n📊 Trading Summary:")
        print(f"Total Orders: {len(orders)}") 