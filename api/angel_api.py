from SmartApi import SmartConnect
import os
from dotenv import load_dotenv

class AngelOneAPI:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('API_KEY')
        self.client_code = os.getenv('CLIENT_CODE')
        self.totp_secret = os.getenv('TOTP_SECRET')
        self.access_token = None
        self.smart_api = SmartConnect(api_key=self.api_key)

    def login(self):
        try:
            data = self.smart_api.generateSession(self.client_code, self.totp_secret)
            self.access_token = data['data']['access_token']
            return True
        except Exception as e:
            print(f"Login error: {e}")
            return False

    def get_symbol_token(self, symbol):
        # Implement symbol token lookup
        return "NIFTY_TOKEN"  # Placeholder

    def place_order(self, order_params):
        try:
            return self.smart_api.placeOrder(order_params)
        except Exception as e:
            print(f"Order placement error: {e}")
            return None 