from typing import Dict, List, Optional
from datetime import datetime
import numpy as np
from .base_strategy import BaseStrategy, Signal
from .ml_strategy import MLStrategy
from .quantum_model import QuantumStrategy
from core.logger import logger

class EnsembleStrategy(BaseStrategy):
    """Ensemble strategy combining ML and Quantum approaches"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.strategies = [
            MLStrategy("ml_strategy"),
            # Add other strategies
        ]
        
    async def validate_signal(self, signal: Signal) -> bool:
        """Implement abstract method"""
        return True  # Basic validation
        
    async def generate_signal(self, market_data: Dict) -> Optional[Signal]:
        """Generate ensemble signal"""
        try:
            signals = []
            for strategy in self.strategies:
                signal = await strategy.generate_signal(market_data)
                if signal:
                    signals.append(signal)
                    
            if not signals:
                return None
                
            # Simple majority voting
            buy_signals = len([s for s in signals if s.action == "BUY"])
            sell_signals = len([s for s in signals if s.action == "SELL"])
            
            action = "BUY" if buy_signals > sell_signals else "SELL"
            avg_confidence = sum(s.confidence for s in signals) / len(signals)
            
            return Signal(
                symbol=market_data['symbol'],
                action=action,
                price=market_data['price'],
                quantity=self.calculate_position_size(market_data),
                timestamp=market_data['timestamp'],
                confidence=avg_confidence,
                strategy_name=self.name
            )
            
        except Exception as e:
            logger.error(f"Ensemble signal generation failed: {e}")
            return None
            
    def _combine_signals(self, ml_signal: Optional[Signal], 
                        quantum_signal: Optional[Signal], 
                        market_data: Dict) -> Optional[Signal]:
        """Combine signals using weighted voting"""
        try:
            signals = []
            if ml_signal:
                signals.append((ml_signal, self.weights["ml"]))
            if quantum_signal:
                signals.append((quantum_signal, self.weights["quantum"]))
                
            if not signals:
                return None
                
            # Calculate weighted action
            buy_weight = sum(w for s, w in signals if s.action == "BUY")
            sell_weight = sum(w for s, w in signals if s.action == "SELL")
            
            # Calculate weighted confidence
            total_confidence = sum(s.confidence * w for s, w in signals)
            avg_confidence = total_confidence / sum(w for _, w in signals)
            
            # Generate ensemble signal
            return Signal(
                symbol=market_data['symbol'],
                action="BUY" if buy_weight > sell_weight else "SELL",
                price=market_data['last_price'],
                quantity=self._calculate_ensemble_position_size(signals),
                timestamp=datetime.now(),
                confidence=avg_confidence,
                strategy_name=self.name,
                signal_type="ENTRY",
                stop_loss=self._calculate_ensemble_stop_loss(signals, market_data)
            )
            
        except Exception as e:
            logger.error(f"Signal combination failed: {e}")
            return None
            
    def _calculate_ensemble_position_size(self, signals: List[tuple]) -> int:
        """Calculate weighted position size"""
        try:
            total_size = sum(s.quantity * w for s, w in signals)
            return int(total_size / sum(w for _, w in signals))
        except Exception as e:
            logger.error(f"Position size calculation failed: {e}")
            return 0
            
    def _calculate_ensemble_stop_loss(self, signals: List[tuple], 
                                    market_data: Dict) -> float:
        """Calculate weighted stop loss"""
        try:
            valid_stops = [(s.stop_loss, w) for s, w in signals if s.stop_loss]
            if not valid_stops:
                return market_data['last_price'] * 0.98  # Default 2% stop loss
                
            return sum(stop * w for stop, w in valid_stops) / sum(w for _, w in valid_stops)
        except Exception as e:
            logger.error(f"Stop loss calculation failed: {e}")
            return 0.0 