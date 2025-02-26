from datetime import datetime
import asyncio
import random
from core.logger import logger
from trading.brokers.angel_one import AngelOneAPI
from trading.analysis.option_chain import OptionChainAnalyzer

class MarketDataHandler:
    def __init__(self, sio):
        self.sio = sio
        self.running = False
        self.broker = AngelOneAPI()
        self.analyzer = OptionChainAnalyzer()
        self.symbols = {
            'NIFTY': {'last': 19500.0},
            'BANKNIFTY': {'last': 45600.0}
        }
        self.logger = logger  # Use the common logger
    
    async def start(self):
        """Start market data streaming"""
        self.running = True
        while self.running:
            try:
                # Get option chain data
                nifty_chain = self.broker.get_option_chain("NIFTY")
                banknifty_chain = self.broker.get_option_chain("BANKNIFTY")
                
                # Analyze chains
                nifty_analysis = self.analyzer.analyze_chain(nifty_chain)
                banknifty_analysis = self.analyzer.analyze_chain(banknifty_chain)
                
                # Emit data to clients
                await self.sio.emit('market_data', {
                    'timestamp': datetime.now().isoformat(),
                    'nifty': nifty_analysis,
                    'banknifty': banknifty_analysis
                })
                
            except Exception as e:
                logger.error(f"Error in market data handler: {str(e)}")
                
            await asyncio.sleep(1)  # Update every second
            
    def stop(self):
        """Stop market data streaming"""
        self.running = False 