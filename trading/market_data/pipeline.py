from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from core.logger import logger

class MarketDataPipeline:
    """Market data preprocessing and feature engineering pipeline"""
    
    def __init__(self):
        self.technical_indicators = {
            "RSI": self._calculate_rsi,
            "MACD": self._calculate_macd,
            "Bollinger": self._calculate_bollinger,
            "ATR": self._calculate_atr
        }
        
    async def process_market_data(self, data: Dict) -> Dict:
        """Process incoming market data"""
        try:
            # Convert to DataFrame for easier processing
            df = pd.DataFrame([data])
            
            # Add technical indicators
            for indicator, func in self.technical_indicators.items():
                df = func(df)
                
            # Add derived features
            df = self._add_derived_features(df)
            
            # Clean and validate
            df = self._clean_data(df)
            
            return df.iloc[0].to_dict()
            
        except Exception as e:
            logger.error(f"Market data processing failed: {e}")
            return data

    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Relative Strength Index"""
        try:
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            return df
        except Exception as e:
            logger.error(f"RSI calculation failed: {e}")
            df['RSI'] = np.nan
            return df

    def _calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD"""
        try:
            exp1 = df['close'].ewm(span=12, adjust=False).mean()
            exp2 = df['close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            return df
        except Exception as e:
            logger.error(f"MACD calculation failed: {e}")
            df['MACD'] = np.nan
            df['Signal_Line'] = np.nan
            return df

    def _calculate_bollinger(self, df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        try:
            df['MA20'] = df['close'].rolling(window=period).mean()
            df['20dSTD'] = df['close'].rolling(window=period).std()
            df['Upper_Band'] = df['MA20'] + (df['20dSTD'] * 2)
            df['Lower_Band'] = df['MA20'] - (df['20dSTD'] * 2)
            return df
        except Exception as e:
            logger.error(f"Bollinger Bands calculation failed: {e}")
            return df

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """Calculate Average True Range"""
        try:
            high_low = df['high'] - df['low']
            high_close = np.abs(df['high'] - df['close'].shift())
            low_close = np.abs(df['low'] - df['close'].shift())
            
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = np.max(ranges, axis=1)
            
            df['ATR'] = true_range.rolling(period).mean()
            return df
        except Exception as e:
            logger.error(f"ATR calculation failed: {e}")
            df['ATR'] = np.nan
            return df

    def _add_derived_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add derived features"""
        try:
            # Price momentum
            df['Price_Momentum'] = df['close'].pct_change()
            
            # Volatility
            df['Volatility'] = df['close'].rolling(window=20).std()
            
            # Volume momentum
            df['Volume_Momentum'] = df['volume'].pct_change()
            
            return df
        except Exception as e:
            logger.error(f"Derived features calculation failed: {e}")
            return df

    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate data"""
        try:
            # Remove duplicates
            df = df.drop_duplicates()
            
            # Handle missing values
            df = df.fillna(method='ffill')
            
            # Remove outliers
            for col in ['close', 'volume']:
                if col in df.columns:
                    mean = df[col].mean()
                    std = df[col].std()
                    df[col] = df[col].clip(mean - 3*std, mean + 3*std)
                    
            return df
        except Exception as e:
            logger.error(f"Data cleaning failed: {e}")
            return df 