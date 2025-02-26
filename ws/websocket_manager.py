from core.config import settings
from core.logger import logger
import asyncio
from typing import Dict, List
import pyotp
import sys
import os

# Add the smartapi-python directory to Python path
smartapi_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'smartapi-python')
sys.path.append(smartapi_path)

from SmartApi import SmartConnect  # Updated import
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from datetime import datetime, time
import pytz

class WebSocketManager:
    """WebSocket connection manager"""
    
    # Market hours constants
    MARKET_OPEN = time(9, 15)  # 9:15 AM
    MARKET_CLOSE = time(15, 30)  # 3:30 PM
    TRADING_DAYS = [0, 1, 2, 3, 4]  # Monday (0) to Friday (4)
    IST = pytz.timezone('Asia/Kolkata')
    
    # WebSocket Constants
    ROOT_URI = "wss://smartapisocket.angelone.in/smart-stream"
    HEART_BEAT_MESSAGE = "ping"
    HEAR_BEAT_INTERVAL = 30
    MAX_RETRY_ATTEMPT = 3
    
    # Constants
    LTP_MODE = 1
    QUOTE_MODE = 2
    SNAP_QUOTE_MODE = 3
    
    def __init__(self):
        self.websocket = None
        self.connected = False
        self.subscriptions: Dict[str, List[str]] = {}
        self.smart_api = None
        
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        now = datetime.now(self.IST)
        current_time = now.time()
        
        # Check if it's a trading day (Monday to Friday)
        if now.weekday() not in self.TRADING_DAYS:
            logger.info("Market is closed - Weekend")
            return False
            
        # Check if within trading hours
        if not (self.MARKET_OPEN <= current_time <= self.MARKET_CLOSE):
            logger.info("Market is closed - Outside trading hours")
            return False
            
        return True

    async def initialize_smart_api(self):
        """Initialize SmartAPI connection"""
        try:
            # Initialize SmartAPI exactly as in example
            self.smart_api = SmartConnect(settings.ANGEL_ONE_API_KEY)
            
            # Generate TOTP
            totp = pyotp.TOTP(settings.ANGEL_TOTP_KEY).now()
            
            # Generate session
            data = self.smart_api.generateSession(
                settings.ANGEL_ONE_CLIENT_ID,  # username
                settings.ANGEL_ONE_PASSWORD,   # pwd
                totp
            )
            
            if data['status']:
                # Store tokens
                auth_token = data['data']['jwtToken']
                refresh_token = data['data']['refreshToken']
                
                # Get feed token
                feed_token = self.smart_api.getfeedToken()
                
                # Get user profile
                profile = self.smart_api.getProfile(refresh_token)
                logger.info(f"Login successful: {profile['data']['name']}")
                
                return data['data'], feed_token
            else:
                raise Exception(f"Session generation failed: {data['message']}")
            
        except Exception as e:
            logger.error(f"Error initializing SmartAPI: {e}")
            raise
        
    async def connect(self):
        """Initialize and connect the WebSocket"""
        try:
            session, feed_token = await self.initialize_smart_api()
            
            # Initialize WebSocket with correct parameter names
            self.websocket = SmartWebSocketV2(
                auth_token=session['jwtToken'],    # lowercase
                api_key=settings.ANGEL_ONE_API_KEY,
                client_code=settings.ANGEL_ONE_CLIENT_ID,
                feed_token=feed_token
            )
            
            # Set callbacks
            self.websocket.on_open = self.on_open
            self.websocket.on_data = self.on_data
            self.websocket.on_error = self.on_error
            self.websocket.on_close = self.on_close
            
            # Connect if market is open
            if self.is_market_open():
                await asyncio.get_event_loop().run_in_executor(None, self.websocket.connect)
                self.connected = True
                logger.info("WebSocket connected successfully")
            else:
                logger.info("WebSocket connection deferred - Market is closed")
            
        except Exception as e:
            logger.error(f"Error in connect: {e}")
            self.connected = False
            raise
            
    def on_open(self, ws):
        """Handle WebSocket connection open"""
        logger.info("WebSocket connection opened")
        # Resubscribe to any existing subscriptions
        if self.subscriptions:
            self.resubscribe_all()
            
    def on_data(self, ws, message):
        """Handle incoming market data"""
        try:
            logger.debug(f"Received market data: {message}")
            # Process the market data here
            # You can emit this data to connected clients
        except Exception as e:
            logger.error(f"Error processing market data: {e}")
            
    def on_error(self, ws, error):
        """Handle WebSocket errors"""
        logger.error(f"WebSocket error: {error}")
        
    def on_close(self, ws):
        """Handle WebSocket connection close"""
        logger.info("WebSocket connection closed")
        self.connected = False
        
    async def subscribe(self, symbols: List[str], mode: int = None):
        """Subscribe to market data for symbols"""
        try:
            if not self.websocket:
                await self.connect()
                
            if mode is None:
                mode = self.LTP_MODE
                
            # Store subscription for when market opens
            self.subscriptions[mode] = symbols
            
            # Only subscribe if market is open
            if self.is_market_open() and self.connected:
                token_list = [
                    {
                        "exchangeType": self.websocket.NSE_FO,
                        "tokens": symbols
                    }
                ]
                
                self.websocket.subscribe(
                    correlation_id="quantum_algo",
                    mode=mode,
                    token_list=token_list
                )
                logger.info(f"Subscribed to symbols: {symbols}")
            else:
                logger.info(f"Subscription deferred for symbols: {symbols}")
            
        except Exception as e:
            logger.error(f"Error subscribing to market data: {e}")
            raise
            
    def resubscribe_all(self):
        """Resubscribe to all stored subscriptions"""
        try:
            for mode, symbols in self.subscriptions.items():
                self.subscribe(symbols, mode)
        except Exception as e:
            logger.error(f"Error resubscribing: {e}")

websocket_manager = WebSocketManager() 