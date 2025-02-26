from typing import Dict, Optional
import pandas as pd
import numpy as np
from scipy.stats import norm
from datetime import datetime, timedelta
from core.logger import logger

class OptionsAnalyzer:
    def __init__(self):
        self.current_chain = None
        self.spot_price = None
        self.risk_free_rate = 0.05

    def analyze_chain(self, chain_data: pd.DataFrame, spot_price: float) -> Dict:
        """Analyze full options chain"""
        try:
            self.current_chain = chain_data
            self.spot_price = spot_price
            
            analysis = {
                'pcr': self._calculate_pcr(),
                'max_pain': self._calculate_max_pain(),
                'iv_skew': self._calculate_iv_skew(),
                'greeks': self._calculate_greeks(),
                'signals': self._generate_signals()
            }
            
            return analysis
        except Exception as e:
            logger.error(f"Options chain analysis failed: {e}")
            return {}

    def _calculate_greeks(self) -> Dict:
        """Calculate option Greeks"""
        try:
            chain = self.current_chain.copy()
            
            # Calculate time to expiry in years
            expiry = pd.to_datetime(chain['expiry'].iloc[0])
            days_to_expiry = (expiry - datetime.now()).days
            t = days_to_expiry / 365
            
            for idx, row in chain.iterrows():
                S = self.spot_price  # Current spot price
                K = row['strike']    # Strike price
                r = self.risk_free_rate
                σ = row['iv'] / 100  # Implied volatility
                
                d1 = (np.log(S/K) + (r + σ**2/2)*t) / (σ*np.sqrt(t))
                d2 = d1 - σ*np.sqrt(t)
                
                if row['type'] == 'CE':
                    chain.loc[idx, 'delta'] = norm.cdf(d1)
                    chain.loc[idx, 'theta'] = (-S*σ*norm.pdf(d1))/(2*np.sqrt(t))
                else:  # PE
                    chain.loc[idx, 'delta'] = -norm.cdf(-d1)
                    chain.loc[idx, 'theta'] = (-S*σ*norm.pdf(d1))/(2*np.sqrt(t))
                    
                chain.loc[idx, 'gamma'] = norm.pdf(d1)/(S*σ*np.sqrt(t))
                chain.loc[idx, 'vega'] = S*np.sqrt(t)*norm.pdf(d1)
            
            return chain.to_dict('records')
            
        except Exception as e:
            logger.error(f"Greeks calculation failed: {e}")
            return {} 