from typing import Dict, Set, List
import asyncio
import json
from fastapi import WebSocket, WebSocketDisconnect
from core.logger import logger
from trading.market_data.pipeline import MarketDataPipeline
from ai_strategy.ensemble_model import EnsembleStrategy
from datetime import datetime

class WebSocketHandler:
    """WebSocket handler for real-time market data and signals"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.market_data_pipeline = MarketDataPipeline()
        self.strategy = EnsembleStrategy("realtime")
        self.subscriptions: Dict[str, Set[str]] = {}  # symbol -> user_ids
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Handle new WebSocket connection"""
        try:
            await websocket.accept()
            if client_id not in self.active_connections:
                self.active_connections[client_id] = set()
            self.active_connections[client_id].add(websocket)
            logger.info(f"WebSocket client connected: {client_id}")
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            
    async def disconnect(self, websocket: WebSocket, client_id: str):
        """Handle WebSocket disconnection"""
        try:
            self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
            # Remove subscriptions
            for symbol in self.subscriptions:
                self.subscriptions[symbol].discard(client_id)
            logger.info(f"WebSocket client disconnected: {client_id}")
            
        except Exception as e:
            logger.error(f"WebSocket disconnection failed: {e}")
            
    async def subscribe(self, client_id: str, symbols: List[str]):
        """Subscribe to market data for symbols"""
        try:
            for symbol in symbols:
                if symbol not in self.subscriptions:
                    self.subscriptions[symbol] = set()
                self.subscriptions[symbol].add(client_id)
            
        except Exception as e:
            logger.error(f"Subscription failed: {e}")
            
    async def process_market_data(self, data: Dict):
        """Process and broadcast market data"""
        try:
            # Process market data
            processed_data = await self.market_data_pipeline.process_market_data(data)
            
            # Generate trading signals
            signal = await self.strategy.generate_signal(processed_data)
            
            # Prepare message
            message = {
                "type": "market_update",
                "data": processed_data,
                "signal": signal.dict() if signal else None,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Broadcast to subscribed clients
            symbol = data.get("symbol")
            if symbol in self.subscriptions:
                for client_id in self.subscriptions[symbol]:
                    if client_id in self.active_connections:
                        for websocket in self.active_connections[client_id]:
                            await websocket.send_json(message)
                            
        except Exception as e:
            logger.error(f"Market data processing failed: {e}") 