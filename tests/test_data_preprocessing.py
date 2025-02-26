import pytest
import pandas as pd
from ai_strategy import data_preprocessing

def test_load_data():
    data = data_preprocessing.load_data('sample_data.csv')
    assert isinstance(data, pd.DataFrame)

def test_clean_data():
    data = pd.DataFrame({'col1': [1, 2, None], 'col2': [4, None, 6]})
    cleaned_data = data_preprocessing.clean_data(data)
    assert cleaned_data.isnull().sum().sum() == 0

def test_normalize_data():
    data = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
    normalized_data = data_preprocessing.normalize_data(data)
    assert normalized_data.mean().mean() == pytest.approx(0, abs=1e-6)

def test_preprocess_data():
    data = data_preprocessing.preprocess_data('sample_data.csv')
    assert isinstance(data, pd.DataFrame)
    assert data.isnull().sum().sum() == 0