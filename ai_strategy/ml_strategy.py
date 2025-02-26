from .base_strategy import BaseStrategy, Signal
from .feature_engineering import FeatureEngineer
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import joblib
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from core.logger import logger

class MLStrategy(BaseStrategy):
    def __init__(self, name: str):
        super().__init__(name)
        self.model = RandomForestClassifier(n_estimators=100)
        self.feature_engineer = FeatureEngineer()
        self.min_confidence = 0.7

    async def train_model(self, historical_data: List[Dict]):
        """Train the ML model"""
        try:
            # Prepare features and labels
            features = self.feature_engineer.create_features(historical_data)
            labels = self.feature_engineer.create_labels(historical_data)
            
            # Train model
            self.model.fit(features, labels)
            logger.info(f"Model trained successfully with {len(features)} samples")
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            
    async def generate_signal(self, market_data: Dict) -> Optional[Signal]:
        """Generate trading signals using ML model"""
        try:
            # Create features
            features = self.feature_engineer.create_features(market_data)
            
            # Get model prediction
            prediction = self.model.predict(features)
            proba = self.model.predict_proba(features)
            
            # Convert to numpy if needed
            if not isinstance(prediction, np.ndarray):
                prediction = np.array(prediction)
            if not isinstance(proba, np.ndarray):
                proba = np.array(proba)
            
            # Get first prediction and confidence
            pred = prediction[0]
            confidence = float(proba[0].max())
            
            # Calculate position size based on confidence
            quantity = int(100 * confidence)  # Basic position sizing
            
            return Signal(
                symbol=market_data['symbol'],
                action="BUY" if pred == 1 else "SELL",
                price=market_data['price'],
                quantity=quantity,  # Use calculated quantity
                timestamp=market_data['timestamp'],
                confidence=confidence,
                strategy_name=self.name,
                signal_type="ENTRY",  # Add default signal type
                stop_loss=None,  # Optional stop loss
                target=None  # Optional target
            )
            
        except Exception as e:
            logger.error(f"Signal generation failed: {str(e)}")  # Log full error
            return None
            
    async def validate_signal(self, signal: Signal) -> bool:
        """Validate ML signal"""
        try:
            # Check confidence
            if signal.confidence < self.min_confidence:
                return False
                
            # Check if opposite signal exists
            existing_signal = self.active_signals.get(signal.symbol)
            if existing_signal and existing_signal.action != signal.action:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Signal validation failed: {e}")
            return False
            
    def calculate_stop_loss(self, market_data: Dict, prediction: int) -> float:
        """Calculate stop loss level"""
        try:
            price = market_data['last_price']
            atr = market_data.get('atr', price * 0.02)  # Default 2% if ATR not available
            
            if prediction == 1:  # BUY
                return price - (atr * 2)
            else:  # SELL
                return price + (atr * 2)
                
        except Exception as e:
            logger.error(f"Stop loss calculation failed: {e}")
            return 0.0

    def generate_signals(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        # Extract features
        features = self.feature_engineer.extract_features(market_data)
        
        # Make prediction
        X = pd.DataFrame([features])
        pred_proba = self.model.predict_proba(X)[0]
        confidence = max(pred_proba)
        
        if confidence >= self.min_confidence:
            signal = {
                "timestamp": market_data["timestamp"],
                "symbol": self.symbol,
                "action": "BUY" if pred_proba[1] > pred_proba[0] else "SELL",
                "confidence": confidence,
                "price": market_data["price"]
            }
            return signal
        return None

    def calculate_position_size(self, signal: Dict[str, Any]) -> int:
        """Calculate position size based on confidence and risk"""
        base_size = 100  # Base position size
        confidence_factor = signal["confidence"]
        return int(base_size * confidence_factor) 