from SmartApi import SmartConnect
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
import pyotp
from time import sleep
import base64
import requests

load_dotenv()

class AngelOneAPI:
    def __init__(self):
        self.api_key = os.getenv("ANGEL_API_KEY", "lB9qx6Rm")
        self.client_code = os.getenv("ANGEL_CLIENT_CODE", "R182159")
        self.password = os.getenv("ANGEL_PASSWORD", "1010")
        self.totp_key = os.getenv("ANGEL_TOTP_KEY", "NRXMU4SVMHCEW3H2KQ65IZKDGI")
        
        try:
            # Initialize Smart API
            self.smart_api = SmartConnect(api_key=self.api_key)
            
            # Process TOTP key
            # Try different key formats
            totp_keys = [
                self.totp_key,  # Original key
                self.totp_key.upper(),  # Uppercase
                self.totp_key.replace(" ", ""),  # Remove spaces
                base64.b32encode(self.totp_key.encode()).decode(),  # Base32 encoded
            ]
            
            # Try to login with retry mechanism
            max_retries = 3
            retry_delay = 2  # seconds
            success = False
            
            for key in totp_keys:
                if success:
                    break
                    
                print(f"Trying TOTP key format: {key}")
                totp = pyotp.TOTP(key)
                
                for attempt in range(max_retries):
                    try:
                        # Generate fresh TOTP
                        current_totp = totp.now()
                        print(f"Generated TOTP: {current_totp}")  # For debugging
                        
                        # Generate session
                        data = self.smart_api.generateSession(
                            self.client_code,
                            self.password,
                            current_totp
                        )
                        
                        # If successful, break the loop
                        if data.get('status'):
                            self.session = data
                            print("Successfully logged in to Angel One!")
                            success = True
                            break
                        else:
                            print(f"Login failed: {data.get('message', 'Unknown error')}")
                            
                    except Exception as e:
                        print(f"Login attempt {attempt + 1} failed with key {key}: {str(e)}")
                        if attempt < max_retries - 1:  # if not the last attempt
                            sleep(retry_delay)  # wait before retrying
                        
            if not success:
                raise Exception("Failed to connect to Angel One after trying all TOTP formats")
                        
        except Exception as e:
            print(f"Error initializing Angel One API: {str(e)}")
            raise

    def get_option_chain(self, symbol: str, expiry_date: str = None):
        """Get option chain data from NSE"""
        try:
            # URLs for fetching Data
            url_oc = "https://www.nseindia.com/option-chain"
            url_map = {
                'BANKNIFTY': 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY',
                'NIFTY': 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
            }
            
            # Headers to mimic browser
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                'accept-language': 'en,gu;q=0.9,hi;q=0.8',
                'accept-encoding': 'gzip, deflate, br'
            }

            session = requests.Session()
            
            # Get cookies first
            session.get(url_oc, headers=headers, timeout=5)
            
            # Get option chain data
            url = url_map.get(symbol.upper())
            if not url:
                raise ValueError(f"Symbol {symbol} not supported. Use NIFTY or BANKNIFTY")
            
            response = session.get(url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Process the data
                processed_data = []
                current_expiry = data["records"]["expiryDates"][0] if not expiry_date else expiry_date
                
                for item in data['records']['data']:
                    if item["expiryDate"] == current_expiry:
                        processed_data.append({
                            'strike_price': item['strikePrice'],
                            'expiry_date': item['expiryDate'],
                            'ce': {
                                'oi': item.get('CE', {}).get('openInterest', 0),
                                'volume': item.get('CE', {}).get('totalTradedVolume', 0),
                                'ltp': item.get('CE', {}).get('lastPrice', 0)
                            },
                            'pe': {
                                'oi': item.get('PE', {}).get('openInterest', 0),
                                'volume': item.get('PE', {}).get('totalTradedVolume', 0),
                                'ltp': item.get('PE', {}).get('lastPrice', 0)
                            }
                        })
                
                return {
                    'symbol': symbol,
                    'expiry_date': current_expiry,
                    'data': processed_data
                }
                
            else:
                print(f"Error fetching option chain: Status code {response.status_code}")
                return None
            
        except Exception as e:
            print(f"Error fetching option chain: {str(e)}")
            return None

    def place_order(self, symbol: str, qty: int, side: str):
        try:
            # Add rate limiting delay
            sleep(0.5)  # 500ms delay between API calls
            
            # Your order placement logic here
            orderparams = {
                "variety": "NORMAL",
                "tradingsymbol": symbol,
                "symboltoken": self._get_token(symbol),
                "transactiontype": side,
                "exchange": "NSE",
                "ordertype": "MARKET",
                "producttype": "INTRADAY",
                "duration": "DAY",
                "quantity": qty
            }
            
            order_id = self.smart_api.placeOrder(orderparams)
            return order_id
            
        except Exception as e:
            print(f"Error placing order: {str(e)}")
            return None

    def _get_token(self, symbol: str) -> str:
        # Implement token lookup logic
        # This is a placeholder - you need to implement proper token lookup
        return "SYMBOL_TOKEN"
        
    def _get_nearest_expiry(self, symbol):
        """Get nearest expiry date"""
        # Implement expiry date logic
        pass
        
    def _process_option_chain(self, data):
        """Process option chain response"""
        try:
            df = pd.DataFrame(data['data'])
            # Add any additional processing you need
            return df
        except Exception as e:
            print(f"Error processing option chain: {str(e)}")
            return None

    def get_spot_price(self, symbol: str) -> float:
        """Get live spot price for the symbol"""
        try:
            # Use Angel One API to get spot price
            # This is a placeholder - implement actual spot price fetching
            ltp_params = {
                "exchange": "NSE",
                "tradingsymbol": symbol,
                "symboltoken": self._get_token(symbol)
            }
            response = self.smart_api.ltpData(ltp_params)
            if response and response.get('data'):
                return float(response['data']['ltp'])
            return 0
        except Exception as e:
            print(f"Error getting spot price: {str(e)}")
            return 0 