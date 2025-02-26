import pennylane as qml
import numpy as np
from typing import List, Dict
import torch
from transformers import AutoModelForSequenceClassification
from datetime import datetime

class OptionsQuantumModel:
    def __init__(self, n_qubits: int = 8):  # Increased qubits for more features
        self.dev = qml.device("default.qubit", wires=n_qubits)
        
        @qml.qnode(self.dev)
        def quantum_circuit(inputs, weights):
            # Encode option-specific features
            for i in range(n_qubits):
                qml.RY(inputs[i], wires=i)
                qml.RZ(inputs[i], wires=i)
            
            # Multi-level entanglement for complex patterns
            for layer in range(2):
                for i in range(n_qubits-1):
                    qml.CNOT(wires=[i, i+1])
                    qml.CRZ(weights[layer][i], wires=[i, i+1])
            
            return [qml.expval(qml.PauliZ(i)) for i in range(n_qubits)]
            
        self.quantum_circuit = quantum_circuit
        self.sentiment_model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        
    def predict_option_trade(self, market_data: Dict, vix: float, pcr: float) -> Dict:
        """Generate option trading signals with strike selection"""
        try:
            # Prepare quantum features
            quantum_features = self._prepare_option_features(
                market_data['spot'],
                market_data['iv'],
                vix,
                pcr,
                market_data['theta'],
                market_data['delta'],
                market_data['gamma'],
                market_data['time_to_expiry']
            )
            
            # Get quantum prediction
            signal = self._quantum_process(quantum_features)
            
            # Select optimal strike and expiry
            trade_params = self._select_option_params(market_data, signal)
            
            return {
                'action': trade_params['action'],
                'symbol': trade_params['symbol'],
                'strike': trade_params['strike'],
                'expiry': trade_params['expiry'],
                'confidence': trade_params['confidence'],
                'stop_loss': trade_params['stop_loss'],
                'target': trade_params['target'],
                'option_type': trade_params['option_type']
            }
            
        except Exception as e:
            print(f"Options quantum prediction error: {str(e)}")
            return None
            
    def _prepare_option_features(self, spot, iv, vix, pcr, theta, delta, gamma, tte):
        """Prepare option-specific features for quantum processing"""
        features = np.array([
            spot/10000,  # Normalized spot price
            iv,          # Implied volatility
            vix/100,     # VIX
            pcr,         # Put-Call ratio
            theta,       # Theta
            delta,       # Delta
            gamma*100,   # Gamma
            tte/30      # Time to expiry in months
        ])
        return features
        
    def _select_option_params(self, market_data: Dict, quantum_signal: np.ndarray) -> Dict:
        """Select optimal option parameters based on quantum signal"""
        spot_price = market_data['spot']
        
        # Determine if bullish or bearish
        is_bullish = np.mean(quantum_signal) > 0.6  # Higher threshold for confidence
        
        # Select strike price based on delta
        if is_bullish:
            optimal_delta = 0.7  # ITM for higher probability
            option_type = 'CE'
        else:
            optimal_delta = -0.7  # ITM for higher probability
            option_type = 'PE'
            
        # Find closest strike
        strikes = market_data['option_chain']['strikes']
        deltas = market_data['option_chain']['deltas']
        optimal_strike_idx = np.argmin(np.abs(deltas - optimal_delta))
        selected_strike = strikes[optimal_strike_idx]
        
        # Calculate stop loss and target
        entry_price = market_data['option_chain']['premiums'][optimal_strike_idx]
        stop_loss = entry_price * 0.7  # 30% stop loss
        target = entry_price * 1.5     # 1.5:1 reward-risk ratio
        
        # Select expiry (prefer 15-30 days)
        expiry = self._select_optimal_expiry(market_data['expiry_dates'])
        
        symbol = f"NIFTY{expiry.strftime('%d%b%y').upper()}{selected_strike}{option_type}"
        
        return {
            'action': 'BUY' if is_bullish else 'SELL',
            'symbol': symbol,
            'strike': selected_strike,
            'expiry': expiry,
            'confidence': abs(np.mean(quantum_signal)),
            'stop_loss': stop_loss,
            'target': target,
            'option_type': option_type
        }
        
    def _select_optimal_expiry(self, expiry_dates: List[datetime]) -> datetime:
        """Select optimal expiry date (15-30 days)"""
        today = datetime.now()
        days_to_expiry = [(expiry - today).days for expiry in expiry_dates]
        optimal_idx = np.argmin(np.abs(np.array(days_to_expiry) - 20))  # Target 20 days
        return expiry_dates[optimal_idx] 