import pytest
import sys
import os
# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import socketio
from datetime import datetime
import json
from core.logger import logger
from config import settings

class SystemTester:
    def __init__(self):
        self.sio = socketio.AsyncClient()
        self.test_results = {}
        self.server_url = f"http://localhost:{settings.API_PORT}"
        logger.info(f"Initializing system tester with server URL: {self.server_url}")

    async def connect(self):
        try:
            await self.sio.connect(self.server_url)
            self.test_results['websocket_connection'] = True
            logger.info("✅ WebSocket connection successful")
        except Exception as e:
            self.test_results['websocket_connection'] = False
            logger.error(f"❌ WebSocket connection failed: {str(e)}")

    async def test_market_data(self):
        try:
            logger.info("Testing market data subscription...")
            await self.sio.emit('subscribe_market_data', ['NIFTY', 'BANKNIFTY'])
            
            data = await self.sio.wait_for('market_update', timeout=5)
            logger.info(f"Received market data: {json.dumps(data, indent=2)}")
            
            self.test_results['market_data'] = bool(data)
        except Exception as e:
            self.test_results['market_data'] = False
            logger.error(f"❌ Market data test failed: {str(e)}")

    async def test_order_placement(self):
        try:
            logger.info("Testing order placement...")
            order = {
                'symbol': 'NIFTY',
                'type': 'BUY',
                'quantity': 50,
                'price': 19500.50
            }
            await self.sio.emit('place_order', order)
            
            confirmation = await self.sio.wait_for('order_confirmation', timeout=5)
            logger.info(f"Order confirmation received: {json.dumps(confirmation, indent=2)}")
            
            self.test_results['order_placement'] = confirmation.get('status') == 'EXECUTED'
        except Exception as e:
            self.test_results['order_placement'] = False
            logger.error(f"❌ Order placement test failed: {str(e)}")

    async def run_tests(self):
        logger.info("🚀 Starting system tests...")
        
        await self.connect()
        
        if self.test_results.get('websocket_connection'):
            await self.test_market_data()
            await self.test_order_placement()
        
        await self.sio.disconnect()
        
        logger.info("\n" + "=" * 40)
        logger.info("Test Results:")
        for test, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            logger.info(f"{test}: {status}")
        logger.info("=" * 40)

if __name__ == "__main__":
    tester = SystemTester()
    asyncio.run(tester.run_tests()) 