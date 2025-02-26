from typing import Dict, List
import numpy as np
from .options_quantum_model import OptionsQuantumModel
from .classical_model import ClassicalModel
from .feature_engineering import FeatureEngineer

class OptionsEnsemble:
    def __init__(self):
        self.quantum_model = OptionsQuantumModel()
        self.classical_model = ClassicalModel()
        self.feature_engineer = FeatureEngineer()
        self.min_confidence = 0.8  # 80% minimum confidence threshold
        
    async def generate_option_signal(self, market_data: Dict) -> Dict:
        """Generate high-probability option trading signals"""
        try:
            # Get market conditions
            vix = market_data['vix']
            pcr = market_data['put_call_ratio']
            
            # Get quantum signal
            quantum_signal = self.quantum_model.predict_option_trade(
                market_data, vix, pcr
            )
            
            # Get classical signal
            features = self.feature_engineer.calculate_features(market_data)
            classical_signal = self.classical_model.predict(features)
            
            # Only generate signal if both models agree with high confidence
            if (quantum_signal['confidence'] > self.min_confidence and 
                classical_signal['confidence'] > self.min_confidence and
                quantum_signal['action'] == classical_signal['action']):
                
                return {
                    'signal': quantum_signal['action'],
                    'symbol': quantum_signal['symbol'],
                    'strike': quantum_signal['strike'],
                    'expiry': quantum_signal['expiry'],
                    'confidence': min(quantum_signal['confidence'], 
                                   classical_signal['confidence']),
                    'stop_loss': quantum_signal['stop_loss'],
                    'target': quantum_signal['target'],
                    'option_type': quantum_signal['option_type'],
                    'entry_range': f"{market_data['spot']}±0.2%",
                    'time_stamp': market_data['timestamp'],
                    'market_status': self._get_market_status(market_data)
                }
            
            return None  # No signal if confidence is low
            
        except Exception as e:
            print(f"Options ensemble error: {str(e)}")
            return None
            
    def _get_market_status(self, market_data: Dict) -> Dict:
        """Get current market conditions"""
        return {
            'trend': 'BULLISH' if market_data['sma_20'] > market_data['sma_50'] else 'BEARISH',
            'volatility': 'HIGH' if market_data['vix'] > 20 else 'LOW',
            'put_call_ratio': market_data['put_call_ratio'],
            'india_vix': market_data['vix']
        } 