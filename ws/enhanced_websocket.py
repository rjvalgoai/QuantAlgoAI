import asyncio
import ssl
import json
from typing import Optional, Dict, Any
from websocket import WebSocketApp
from core.logger import logger
import os
from backend.database.websocket_service import WebSocketDBService

class EnhancedSmartWebSocket(SmartWebSocketV2):
    """Enhanced WebSocket with quantum debugging and better error handling"""
    
    def __init__(self, auth_token, api_key, client_code, feed_token):
        super().__init__(auth_token, api_key, client_code, feed_token)
        self.reconnect_delay = 1  # Start with 1 second delay
        self.health_metrics = {
            "connection_stability": 1.0,
            "data_coherence": 1.0,
            "latency": 0
        }
        # Create DB service but don't initialize yet
        self.db = WebSocketDBService(
            f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
            f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        )

    async def initialize(self):
        """Async initialization method"""
        await self.db.init_pool()
        return self

    @classmethod
    async def create(cls, auth_token, api_key, client_code, feed_token):
        """Factory method to create and initialize instance"""
        instance = cls(auth_token, api_key, client_code, feed_token)
        await instance.initialize()
        return instance

    async def connect_with_retry(self):
        """Connect with exponential backoff"""
        while True:
            try:
                if await self.connect():
                    self.reconnect_delay = 1  # Reset on successful connection
                    return True
            except Exception as e:
                logger.error(f"Connection failed: {e}")
                await asyncio.sleep(self.reconnect_delay)
                self.reconnect_delay = min(self.reconnect_delay * 2, 60)  # Cap at 60 seconds

    def _on_data(self, wsapp, data, data_type, continue_flag):
        """Enhanced data handler with health monitoring"""
        try:
            # Update health metrics
            self.health_metrics["connection_stability"] = 1.0
            
            if data_type == 2:  # Binary data
                parsed_data = self._parse_binary_data(data)
                self._analyze_data_coherence(parsed_data)
                self.on_data(wsapp, parsed_data)
            else:
                self.on_data(wsapp, data)
                
        except Exception as e:
            logger.error(f"Data handling error: {e}")
            self.health_metrics["connection_stability"] *= 0.9  # Degrade health score

    def _analyze_data_coherence(self, data: Dict[str, Any]):
        """Analyze market data coherence"""
        try:
            if "last_traded_price" in data and "average_traded_price" in data:
                # Check price coherence
                price_diff = abs(data["last_traded_price"] - data["average_traded_price"])
                price_coherence = 1.0 / (1.0 + price_diff/data["last_traded_price"])
                
                # Update coherence metric
                self.health_metrics["data_coherence"] = (
                    0.8 * self.health_metrics["data_coherence"] + 
                    0.2 * price_coherence
                )
        except Exception as e:
            logger.error(f"Coherence analysis error: {e}")

    def get_health_report(self) -> Dict[str, float]:
        """Get current health metrics"""
        return {
            "connection_health": self.health_metrics["connection_stability"],
            "data_quality": self.health_metrics["data_coherence"],
            "system_latency": self.health_metrics["latency"]
        } 