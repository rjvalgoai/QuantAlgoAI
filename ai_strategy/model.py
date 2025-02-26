import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from .feature_engineering import FeatureEngineer

class AIModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.feature_engineer = FeatureEngineer()
        
    def train(self, data: pd.DataFrame):
        """Train the model"""
        try:
            # Engineer features
            features = self.feature_engineer.calculate_features(data)
            
            # Prepare target
            target = self._prepare_target(data)
            
            # Train model
            self.model.fit(features, target)
            
            return True
        except Exception as e:
            print(f"Training error: {str(e)}")
            return False
            
    def predict(self, data: pd.DataFrame) -> dict:
        """Generate trading signals"""
        try:
            # Calculate features
            features = self.feature_engineer.calculate_features(data)
            
            # Make prediction
            signal = self.model.predict(features.reshape(1, -1))[0]
            prob = self.model.predict_proba(features.reshape(1, -1))[0]
            
            return {
                'signal': 'BUY' if signal == 1 else 'SELL',
                'confidence': float(max(prob)),
                'features': features.tolist()
            }
            
        except Exception as e:
            print(f"Prediction error: {str(e)}")
            return None 