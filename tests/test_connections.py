import requests
import socketio
import json
from datetime import datetime

def test_rest_api():
    print("\n🔍 Testing REST API Endpoints...")
    
    endpoints = [
        "http://localhost:5000/",
        "http://localhost:5000/health",
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint)
            print(f"✅ {endpoint}: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {str(e)}")

def test_websocket():
    print("\n🔌 Testing WebSocket Connection...")
    
    sio = socketio.Client()
    
    @sio.event
    def connect():
        print("✅ WebSocket Connected!")
        # Test message
        sio.emit('message', {'test': 'Hello Server!'})
    
    @sio.event
    def disconnect():
        print("❌ WebSocket Disconnected!")
    
    @sio.on('*')
    def catch_all(event, data):
        print(f"📨 Received {event}: {json.dumps(data, indent=2)}")
    
    try:
        sio.connect('http://localhost:5000')
        sio.sleep(5)  # Wait for 5 seconds
        sio.disconnect()
    except Exception as e:
        print(f"❌ WebSocket Error: {str(e)}")

def main():
    print("🚀 Starting Connection Tests...")
    print(f"⏰ Time: {datetime.now().isoformat()}")
    
    # Test REST API
    test_rest_api()
    
    # Test WebSocket
    test_websocket()
    
    print("\n✨ Connection Tests Completed!")

if __name__ == "__main__":
    main() 