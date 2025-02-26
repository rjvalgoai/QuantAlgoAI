from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import numpy as np
import pandas as pd
from dataclasses import dataclass
from datetime import datetime
from core.logger import logger

@dataclass
class Signal:
    symbol: str
    action: str  # BUY/SELL
    price: float
    quantity: int
    timestamp: str  # Change to str to match market_data
    confidence: float
    strategy_name: str
    signal_type: str = "ENTRY"  # Add default
    stop_loss: Optional[float] = None
    target: Optional[float] = None

class BaseStrategy(ABC):
    """Base class for all trading strategies"""
    def __init__(self, name: str):
        self.name = name
        self.active_signals: Dict[str, Signal] = {}
        self.historical_signals: Dict[str, Signal] = {}
        
    @abstractmethod
    async def generate_signal(self, market_data: Dict) -> Optional[Signal]:
        """Generate trading signals from market data"""
        pass
        
    async def validate_signal(self, signal: Signal) -> bool:
        """Base validation - can be overridden"""
        return True
        
    async def process_market_data(self, market_data: Dict) -> Optional[Signal]:
        """Process market data and generate signals"""
        try:
            # Generate signal
            signal = await self.generate_signal(market_data)
            if not signal:
                return None
                
            # Validate signal
            if not await self.validate_signal(signal):
                logger.info(f"Signal validation failed: {signal}")
                return None
                
            # Store signal
            self.active_signals[signal.symbol] = signal
            logger.info(f"New signal generated: {signal}")
            return signal
            
        except Exception as e:
            logger.error(f"Error processing market data: {e}")
            return None

    def update(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update strategy with new market data and generate signals"""
        signal = self.generate_signals(market_data)
        if signal:
            position_size = self.calculate_position_size(signal)
            signal.update({"position_size": position_size})
            self.signals.append(signal)
        return signal 