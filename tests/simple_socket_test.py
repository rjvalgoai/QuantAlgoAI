import pytest
import socketio
import time
import sys

def test_socket():
    print("Starting WebSocket test...")
    
    # Create socket client
    sio = socketio.Client()
    
    @sio.event
    def connect():
        print("✅ Connected to WebSocket!")
        # Test message
        sio.emit('message', {'test': 'Hello Server!'})
        print("Message sent to server")
    
    @sio.event
    def connect_error(error):
        print(f"❌ Connection failed: {error}")
    
    @sio.event
    def disconnect():
        print("Disconnected from server")
    
    try:
        print("Attempting to connect...")
        sio.connect('http://localhost:5000', wait=True, wait_timeout=5)
        print("Connection attempt completed")
        
        # Keep alive for a few seconds
        time.sleep(3)
        
        print("Disconnecting...")
        sio.disconnect()
        print("Test completed")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
if __name__ == "__main__":
    test_socket() 