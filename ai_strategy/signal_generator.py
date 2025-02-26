from typing import Dict, Optional, List
import pandas as pd
import numpy as np
from core.logger import logger

class SignalGenerator:
    def __init__(self):
        self.indicators = {}
        self.signals = []
        self.min_confidence = 0.7

    async def generate_signals(self, market_data: Dict, 
                             options_data: Optional[Dict] = None) -> List[Dict]:
        """Generate trading signals using multiple strategies"""
        try:
            signals = []
            
            # Technical signals
            tech_signals = self._generate_technical_signals(market_data)
            if tech_signals:
                signals.extend(tech_signals)
            
            # Options signals
            if options_data:
                opt_signals = self._generate_options_signals(options_data)
                if opt_signals:
                    signals.extend(opt_signals)
            
            # ML signals
            ml_signals = await self._generate_ml_signals(market_data)
            if ml_signals:
                signals.extend(ml_signals)
            
            # Filter high confidence signals
            high_conf_signals = [
                s for s in signals 
                if s.get('confidence', 0) >= self.min_confidence
            ]
            
            return high_conf_signals
            
        except Exception as e:
            logger.error(f"Signal generation failed: {e}")
            return []

    def _generate_technical_signals(self, market_data: Dict) -> List[Dict]:
        """Generate signals based on technical analysis"""
        signals = []
        
        try:
            # MA Crossover
            if market_data.get('MA10', 0) > market_data.get('EMA10', 0):
                signals.append({
                    'type': 'TECHNICAL',
                    'action': 'BUY',
                    'strategy': 'MA_CROSS',
                    'confidence': 0.8
                })
            
            # RSI Signals
            rsi = market_data.get('RSI', 50)
            if rsi < 30:
                signals.append({
                    'type': 'TECHNICAL',
                    'action': 'BUY',
                    'strategy': 'RSI_OVERSOLD',
                    'confidence': 0.75
                })
            
            return signals
            
        except Exception as e:
            logger.error(f"Technical signal generation failed: {e}")
            return []

    def _generate_options_signals(self, options_data: Dict) -> List[Dict]:
        """Generate signals based on options data"""
        signals = []
        
        try:
            # PCR based signals
            pcr = options_data.get('pcr', 1.0)
            if pcr > 1.5:
                signals.append({
                    'type': 'OPTIONS',
                    'action': 'BUY',
                    'strategy': 'HIGH_PCR',
                    'confidence': min(pcr/2, 0.9)
                })
            elif pcr < 0.5:
                signals.append({
                    'type': 'OPTIONS',
                    'action': 'SELL',
                    'strategy': 'LOW_PCR',
                    'confidence': min(1-pcr, 0.9)
                })
                
            # IV Skew signals
            iv_skew = options_data.get('iv_skew', 0)
            if abs(iv_skew) > 0.2:
                signals.append({
                    'type': 'OPTIONS',
                    'action': 'BUY' if iv_skew < 0 else 'SELL',
                    'strategy': 'IV_SKEW',
                    'confidence': min(abs(iv_skew), 0.9)
                })
                
            return signals
            
        except Exception as e:
            logger.error(f"Options signal generation failed: {e}")
            return [] 