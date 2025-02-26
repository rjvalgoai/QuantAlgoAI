import requests
import pandas as pd
import numpy as np
from scipy.stats import norm
from typing import Dict, List, Optional
import math
from trading.analysis.greeks_calculator import GreeksCalculator
from datetime import datetime, date

class OptionChainAnalyzer:
    def __init__(self, symbol="NIFTY", expiry=None):
        """Initialize with the index symbol and expiry date."""
        self.symbol = symbol
        self.expiry = expiry or self._get_nearest_expiry()
        self.url = f"https://www.nseindia.com/api/option-chain-indices?symbol={self.symbol}"
        self.spot_price = None
        self.chain_data = None
        self.greeks_calculator = GreeksCalculator()

    def fetch_option_chain(self):
        """
        Fetch live option chain data from NSE.
        :return: DataFrame with option chain data
        """
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept-Language": "en-US,en;q=0.5"
        }
        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)  # Initiate session
        response = session.get(self.url, headers=headers)
        data = response.json()

        option_data = []
        for record in data["records"]["data"]:
            if "CE" in record and "PE" in record:
                option_data.append({
                    "strikePrice": record["CE"]["strikePrice"],
                    "CE_OI": record["CE"]["openInterest"],
                    "PE_OI": record["PE"]["openInterest"],
                    "CE_LTP": record["CE"]["lastPrice"],
                    "PE_LTP": record["PE"]["lastPrice"],
                    "CE_Volume": record["CE"]["totalTradedVolume"],
                    "PE_Volume": record["PE"]["totalTradedVolume"]
                })
        
        return pd.DataFrame(option_data).sort_values("strikePrice")

    def analyze_oi_trend(self, df):
        """
        Analyze Open Interest (OI) to determine market sentiment.
        :param df: DataFrame with option chain data
        :return: DataFrame with OI trends
        """
        df["OI_Ratio"] = df["CE_OI"] / (df["PE_OI"] + 1)  # Prevent divide by zero
        df["Signal"] = np.where(df["OI_Ratio"] > 1.2, "Bearish", "Bullish")  # Simple OI signal
        return df

    def calculate_greeks(self, df, interest_rate=0.05, volatility=0.2, expiry_days=30):
        """
        Calculate option Greeks (Delta, Gamma, Vega) for strike prices.
        :param df: DataFrame with option data
        :param interest_rate: Risk-free rate
        :param volatility: Implied volatility
        :param expiry_days: Days to expiration
        :return: DataFrame with Greek values
        """
        df["d1"] = (np.log(df["strikePrice"] / df["strikePrice"].mean()) +
                    (interest_rate + (volatility**2) / 2) * expiry_days) / (volatility * np.sqrt(expiry_days))
        df["d2"] = df["d1"] - volatility * np.sqrt(expiry_days)

        df["Delta"] = norm.cdf(df["d1"])
        df["Gamma"] = norm.pdf(df["d1"]) / (df["strikePrice"] * volatility * np.sqrt(expiry_days))
        df["Vega"] = df["strikePrice"] * norm.pdf(df["d1"]) * np.sqrt(expiry_days)

        return df

    def round_nearest(self, x: float, base: int = 50) -> int:
        """Round to nearest base (default 50)"""
        return int(base * round(float(x)/base))
        
    def get_nearest_strikes(self, spot_price: float, num_strikes: int = 5) -> List[float]:
        """Get n strikes above and below spot price"""
        base = 100 if spot_price > 20000 else 50  # Use 100 for BANKNIFTY, 50 for NIFTY
        atm_strike = self.round_nearest(spot_price, base)
        strikes = []
        
        for i in range(-num_strikes, num_strikes + 1):
            strikes.append(atm_strike + (i * base))
            
        return sorted(strikes)

    def analyze_chain(self, chain_data: dict, spot_price: float) -> dict:
        """Analyze option chain data with Greeks"""
        try:
            df = pd.DataFrame(chain_data['data'])
            
            # Add required columns
            df['Underlying'] = spot_price
            df['Last Price'] = df.apply(lambda x: x['ce']['ltp'] if 'ce' in x else x['pe']['ltp'], axis=1)
            df['Expiry'] = pd.to_datetime(chain_data['expiry_date']).date()
            
            # Calculate Greeks
            df['IV'] = df.apply(lambda row: self.greeks_calculator.calculate_iv(row), axis=1)
            df['Delta'] = df.apply(lambda row: self.greeks_calculator.calculate_delta(row), axis=1)
            df['Gamma'] = df.apply(lambda row: self.greeks_calculator.calculate_gamma(row), axis=1)
            df['Theta'] = df.apply(lambda row: self.greeks_calculator.calculate_theta(row), axis=1)
            df['Vega'] = df.apply(lambda row: self.greeks_calculator.calculate_vega(row), axis=1)
            
            # Basic analysis
            analysis = {
                'symbol': self.symbol,
                'spot_price': spot_price,
                'expiry_date': chain_data['expiry_date'],
                'pcr': self._calculate_pcr(df),
                'max_pain': self._calculate_max_pain(df),
                'iv_skew': self._calculate_iv_skew(df),
                'greeks_data': df[['strike_price', 'IV', 'Delta', 'Gamma', 'Theta', 'Vega']].to_dict('records')
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing option chain: {e}")
            return None
            
    def _calculate_pcr(self, df):
        """Calculate Put-Call Ratio"""
        total_ce_oi = df['ce'].apply(lambda x: x.get('oi', 0)).sum()
        total_pe_oi = df['pe'].apply(lambda x: x.get('oi', 0)).sum()
        return total_pe_oi / total_ce_oi if total_ce_oi > 0 else 0
        
    def _calculate_max_pain(self, df):
        """Calculate Max Pain point"""
        # Implementation here...
        pass
        
    def _calculate_iv_skew(self, df):
        """Calculate IV Skew"""
        # Implementation here...
        pass

    def get_trading_signals(self, analysis: Dict) -> Dict:
        """Generate trading signals based on analysis"""
        signals = {
            'bias': 'NEUTRAL',
            'strength': 0,
            'suggested_trades': []
        }
        
        try:
            # Determine bias based on PCR
            if analysis['pcr'] > 1.5:
                signals['bias'] = 'BULLISH'
                signals['strength'] = min((analysis['pcr'] - 1.5) * 2, 1) * 100
            elif analysis['pcr'] < 0.7:
                signals['bias'] = 'BEARISH'
                signals['strength'] = min((0.7 - analysis['pcr']) * 2, 1) * 100
                
            # Generate trade suggestions
            if signals['bias'] == 'BULLISH' and signals['strength'] > 50:
                signals['suggested_trades'].append({
                    'type': 'BUY',
                    'instrument': 'CALL',
                    'strike': min(s for s in analysis['resistance_levels'] if s > analysis['spot_price']),
                    'reason': 'High Put-Call ratio indicating bullish sentiment'
                })
            elif signals['bias'] == 'BEARISH' and signals['strength'] > 50:
                signals['suggested_trades'].append({
                    'type': 'BUY',
                    'instrument': 'PUT',
                    'strike': max(s for s in analysis['support_levels'] if s < analysis['spot_price']),
                    'reason': 'Low Put-Call ratio indicating bearish sentiment'
                })
                
            return signals
            
        except Exception as e:
            print(f"Error generating trading signals: {str(e)}")
            return signals

# Example Usage
if __name__ == "__main__":
    analyzer = OptionChainAnalyzer(symbol="NIFTY", expiry="2024-02-29")
    df = analyzer.fetch_option_chain()
    df = analyzer.analyze_oi_trend(df)
    df = analyzer.calculate_greeks(df)
    
    print(df.head())
