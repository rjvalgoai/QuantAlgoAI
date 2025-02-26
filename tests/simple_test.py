import requests
import sys
import os

def test_server():
    print("Starting simple server test...")
    
    try:
        # Test basic endpoint
        response = requests.get('http://localhost:5000')
        print(f"Server response: {response.status_code}")
        print(f"Response data: {response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Server is not running!")
        print("Please start the server first with: python server.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    test_server() 