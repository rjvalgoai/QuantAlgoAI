import pytest
import pandas as pd
from ai_strategy import feature_engineering

def test_add_technical_indicators():
    data = pd.DataFrame({'close': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]})
    data = feature_engineering.add_technical_indicators(data)
    assert 'SMA_20' in data.columns
    assert 'SMA_50' in data.columns

def test_add_option_specific_features():
    data = pd.DataFrame({'close': [1, 2, 3, 4, 5]})
    data = feature_engineering.add_option_specific_features(data)
    assert 'implied_volatility' in data.columns

def test_engineer_features():
    data = pd.DataFrame({'close': [1, 2, 3, 4, 5]})
    data = feature_engineering.engineer_features(data)
    assert 'SMA_20' in data.columns
    assert 'implied_volatility' in data.columns