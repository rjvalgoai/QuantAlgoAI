import pandas as pd
import numpy as np

class DataPreprocessor:
    def __init__(self, data):
        """
        Initialize with raw market data.
        :param data: DataFrame with raw market price data
        """
        self.data = data

    def clean_data(self):
        """Remove NaNs, handle missing values, and normalize data."""
        self.data.dropna(inplace=True)
        self.data['returns'] = self.data['close'].pct_change().fillna(0)
        return self.data

    def add_moving_averages(self, short_window=9, long_window=21):
        """Add short and long moving averages."""
        self.data['SMA_9'] = self.data['close'].rolling(window=short_window).mean()
        self.data['SMA_21'] = self.data['close'].rolling(window=long_window).mean()
        return self.data

    def add_rsi(self, period=14):
        """Calculate and add RSI (Relative Strength Index)."""
        delta = self.data['close'].diff(1)
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        return self.data

    def add_volatility(self, window=10):
        """Calculate rolling volatility."""
        self.data['volatility'] = self.data['returns'].rolling(window=window).std()
        return self.data

    def preprocess(self):
        """Run all preprocessing steps."""
        self.clean_data()
        self.add_moving_averages()
        self.add_rsi()
        self.add_volatility()
        return self.data

# Example Usage
if __name__ == "__main__":
    sample_data = pd.DataFrame({
        "close": np.random.randint(17000, 18000, 100)
    })
    preprocessor = DataPreprocessor(sample_data)
    processed_data = preprocessor.preprocess()
    print(processed_data.tail())
