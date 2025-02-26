import pandas as pd
import numpy as np
from typing import Dict, Any, List
import joblib
from .feature_engineering import FeatureEngineer

class ModelInference:
    def __init__(self, model_path: str):
        # Load model data
        model_data = joblib.load(model_path)
        self.model = model_data["model"]
        self.scaler = model_data["scaler"]
        self.feature_names = model_data["feature_names"]
        self.feature_engineer = FeatureEngineer()
        
    def predict(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make predictions on new market data"""
        # Extract features
        features = self.feature_engineer.extract_features(market_data)
        
        # Select relevant features
        X = pd.DataFrame([features])[self.feature_names]
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make prediction
        pred_proba = self.model.predict_proba(X_scaled)[0]
        prediction = self.model.predict(X_scaled)[0]
        
        return {
            "prediction": "BUY" if prediction == 1 else "SELL",
            "confidence": max(pred_proba),
            "probabilities": {
                "SELL": pred_proba[0],
                "BUY": pred_proba[1]
            },
            "timestamp": market_data.get("timestamp"),
            "features_used": self.feature_names
        }
    
    def batch_predict(self, market_data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Make predictions on a batch of market data"""
        return [self.predict(data) for data in market_data_list]

# Example usage
if __name__ == "__main__":
    # Load model and make predictions
    model_path = "models/trading_model.joblib"
    inference = ModelInference(model_path)
    
    # Sample market data
    sample_data = {
        "timestamp": "2024-02-19T12:00:00",
        "symbol": "NIFTY",
        "open": 19500.0,
        "high": 19550.0,
        "low": 19450.0,
        "close": 19525.0,
        "volume": 1000000
    }
    
    # Make prediction
    prediction = inference.predict(sample_data)
    print(f"Prediction: {prediction}")
