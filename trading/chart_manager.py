import pandas as pd
from typing import Dict
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO

class ChartManager:
    def __init__(self):
        self.data = pd.DataFrame()
        self.indicators = {}
        
    def update_data(self, market_data: Dict):
        """Update chart data with new market data"""
        new_data = pd.DataFrame([market_data])
        self.data = pd.concat([self.data, new_data])
        self._calculate_indicators()
        
    def _calculate_indicators(self):
        """Calculate technical indicators"""
        if len(self.data) > 0:
            # Calculate MA
            self.data['MA10'] = self.data['Close'].rolling(10).mean()
            self.data['EMA10'] = self.data['Close'].ewm(span=10).mean()
            
            # Calculate RSI
            delta = self.data['Close'].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = -delta.where(delta < 0, 0).rolling(14).mean()
            rs = gain / loss
            self.data['RSI'] = 100 - (100 / (1 + rs))
            
    def create_chart(self) -> BytesIO:
        """Create chart using matplotlib"""
        plt.figure(figsize=(12, 6))
        
        # Plot price
        plt.plot(self.data.index, self.data['Close'], label='Price')
        plt.plot(self.data.index, self.data['MA10'], label='MA10')
        plt.plot(self.data.index, self.data['EMA10'], label='EMA10')
        
        plt.title('Market Data')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.legend()
        
        # Save to buffer
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        
        return buf 