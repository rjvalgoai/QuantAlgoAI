import pandas as pd
import numpy as np
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)

class OptionChainAnalyzer:
    def __init__(self):
        self.current_chain = None
        self.spot_price = None
        
    def analyze_chain(self, market_data: Dict, spot_price: float) -> Dict:
        """Analyze option chain for trading opportunities"""
        try:
            self.spot_price = spot_price
            
            # Skip max_pain calculation if no strike data
            analysis = {
                'pcr': self._calculate_pcr(),
                'iv_skew': self._calculate_iv_skew(),
                'support_resistance': self._find_support_resistance(),
                'trading_signals': self._generate_signals()
            }
            
            # Only add max_pain if we have strike data
            if 'strike' in self.current_chain.columns:
                analysis['max_pain'] = self._calculate_max_pain()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Option chain analysis failed: {e}")
            return {}
        
    def _calculate_pcr(self) -> float:
        """Calculate Put-Call Ratio"""
        try:
            total_put_oi = self.current_chain['put_oi'].sum()
            total_call_oi = self.current_chain['call_oi'].sum()
            return total_put_oi / total_call_oi if total_call_oi > 0 else 1.0
        except (KeyError, ZeroDivisionError):
            logger.warning("Unable to calculate PCR, using default value")
            return 1.0  # Neutral PCR as default
        
    def _calculate_max_pain(self) -> float:
        """Calculate Max Pain Point"""
        strikes = self.current_chain['strike'].unique()
        
        pain_values = []
        for strike in strikes:
            # Calculate total pain at each strike
            call_pain = self._calculate_option_pain('call', strike)
            put_pain = self._calculate_option_pain('put', strike)
            total_pain = call_pain + put_pain
            pain_values.append((strike, total_pain))
            
        # Strike price with minimum pain
        max_pain = min(pain_values, key=lambda x: x[1])[0]
        return max_pain
        
    def _generate_signals(self) -> List[Dict]:
        """Generate trading signals"""
        signals = []
        
        # PCR based signals
        pcr = self._calculate_pcr()
        if pcr > 1.5:
            signals.append({
                'type': 'BULLISH',
                'strategy': 'PCR_HIGH',
                'confidence': min(pcr/2, 0.9)
            })
        elif pcr < 0.5:
            signals.append({
                'type': 'BEARISH',
                'strategy': 'PCR_LOW',
                'confidence': min(1-pcr, 0.9)
            })
            
        # IV Skew based signals
        iv_skew = self._calculate_iv_skew()
        if iv_skew > 0.2:
            signals.append({
                'type': 'BEARISH',
                'strategy': 'HIGH_PUT_SKEW',
                'confidence': min(iv_skew, 0.9)
            })
            
        return signals 

    def calculate_technical_indicators(self, prices: pd.Series) -> Dict:
        """Calculate technical indicators"""
        try:
            # Calculate RSI
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            # Calculate MACD
            exp1 = prices.ewm(span=12, adjust=False).mean()
            exp2 = prices.ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            
            return {
                'rsi': rsi.iloc[-1],
                'macd': macd.iloc[-1],
                'signal': signal.iloc[-1],
                'macd_hist': (macd - signal).iloc[-1]
            }
        except Exception as e:
            logger.error(f"Technical indicator calculation failed: {e}")
            return {} 