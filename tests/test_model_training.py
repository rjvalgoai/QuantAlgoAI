import pytest
import pandas as pd
from backend.ai_strategy import model_training  # Update the import path
from sklearn.ensemble import RandomForestClassifier

def test_train_model(mocker):
    data = pd.DataFrame({
        'feature1': [1, 2, 3, 4, 5],
        'feature2': [5, 4, 3, 2, 1],
        'target': [0, 1, 0, 1, 0]
    })
    
    mocker.patch('ai_strategy.data_preprocessing.preprocess_data', return_value=data)
    mocker.patch('ai_strategy.feature_engineering.engineer_features', return_value=data)
    mocker.patch('joblib.dump')
    
    model_training.train_model(data)
    
    assert model_training.RandomForestClassifier.fit.called
    assert model_training.joblib.dump.called