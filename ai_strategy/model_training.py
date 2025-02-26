import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import joblib
from typing import Tuple, Dict, List
from .feature_engineering import FeatureEngineer
from .ml_strategy import MLStrategy
from .quantum_model import QuantumStrategy
from .ensemble_model import EnsembleStrategy
from core.logger import logger

class ModelTrainer:
    """Training and evaluation system for trading models"""
    
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.ml_strategy = MLStrategy("ml_training")
        self.quantum_strategy = QuantumStrategy("quantum_training")
        self.ensemble_strategy = EnsembleStrategy("ensemble_training")
        
    async def train_models(self, historical_data: List[Dict]) -> Dict:
        """Train all models"""
        try:
            # Prepare features and labels
            features = self.feature_engineer.create_features(historical_data)
            labels = self.feature_engineer.create_labels(historical_data)
            
            # Split data
            train_data, test_data = self._split_data(features, labels)
            
            # Train individual models
            ml_metrics = await self._train_and_evaluate_ml(train_data, test_data)
            quantum_metrics = await self._train_and_evaluate_quantum(train_data, test_data)
            
            # Train ensemble
            ensemble_metrics = await self._train_and_evaluate_ensemble(
                train_data, test_data, ml_metrics, quantum_metrics)
                
            return {
                "ml_metrics": ml_metrics,
                "quantum_metrics": quantum_metrics,
                "ensemble_metrics": ensemble_metrics
            }
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return {}
            
    def _split_data(self, features: pd.DataFrame, 
                    labels: np.ndarray) -> Tuple[Dict, Dict]:
        """Split data for training and testing"""
        try:
            tscv = TimeSeriesSplit(n_splits=5)
            for train_idx, test_idx in tscv.split(features):
                train_data = {
                    "features": features.iloc[train_idx],
                    "labels": labels[train_idx]
                }
                test_data = {
                    "features": features.iloc[test_idx],
                    "labels": labels[test_idx]
                }
            return train_data, test_data
            
        except Exception as e:
            logger.error(f"Data splitting failed: {e}")
            return {}, {}
            
    async def _train_and_evaluate_ml(self, train_data: Dict, 
                                    test_data: Dict) -> Dict:
        """Train and evaluate ML strategy"""
        try:
            # Train
            await self.ml_strategy.train_model(train_data["features"])
            
            # Predict
            predictions = []
            for _, row in test_data["features"].iterrows():
                signal = await self.ml_strategy.generate_signal(row.to_dict())
                if signal:
                    predictions.append(1 if signal.action == "BUY" else 0)
                else:
                    predictions.append(0)
                    
            # Calculate metrics
            return {
                "accuracy": accuracy_score(test_data["labels"], predictions),
                "precision": precision_score(test_data["labels"], predictions),
                "recall": recall_score(test_data["labels"], predictions)
            }
            
        except Exception as e:
            logger.error(f"ML evaluation failed: {e}")
            return {}
    
    def prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for training"""
        # Generate features
        features_df = self.feature_engineer.calculate_technical_features(data)
        
        # Generate labels (1 for price increase, 0 for decrease)
        features_df['target'] = (features_df['close'].shift(-1) > features_df['close']).astype(int)
        
        # Drop NaN values
        features_df = features_df.dropna()
        
        # Separate features and target
        X = features_df[self.feature_engineer.feature_names]
        y = features_df['target']
        
        return X, y
    
    def train(self, data: pd.DataFrame) -> Dict[str, float]:
        """Train the model and return metrics"""
        X, y = self.prepare_data(data)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Cross validation score
        cv_scores = cross_val_score(
            self.model, X_train_scaled, y_train, 
            cv=5, scoring='accuracy'
        )
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Calculate metrics
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        # Feature importance
        feature_importance = dict(zip(
            self.feature_engineer.feature_names,
            self.model.feature_importances_
        ))
        
        return {
            "train_accuracy": train_score,
            "test_accuracy": test_score,
            "cv_scores_mean": cv_scores.mean(),
            "cv_scores_std": cv_scores.std(),
            "feature_importance": feature_importance
        }
    
    def save_model(self, path: str):
        """Save model and scaler"""
        model_data = {
            "model": self.model,
            "scaler": self.scaler,
            "feature_names": self.feature_engineer.feature_names
        }
        joblib.dump(model_data, path)

# Example Usage
if __name__ == "__main__":
    sample_data = pd.DataFrame({
        "date": pd.date_range(start="2024-01-01", periods=100),
        "close": np.random.randint(17000, 18000, 100),
        "volume": np.random.randint(100000, 200000, 100),
        "upper_band": np.random.randint(17500, 18500, 100),
        "lower_band": np.random.randint(16500, 17500, 100),
        "MACD": np.random.randn(100),
        "MACD_signal": np.random.randn(100),
        "delta": np.random.rand(100),
        "gamma": np.random.rand(100),
        "vega": np.random.rand(100)
    })

    trainer = ModelTrainer()
    metrics = trainer.train(sample_data)
    trainer.save_model("BTC_model.pkl")
    print(f"✅ Model trained with metrics: {metrics}")
