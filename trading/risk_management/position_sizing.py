from typing import Dict
import numpy as np

class RiskManager:
    def __init__(self):
        self.max_position_size = 100000  # ₹1 lakh max position
        self.max_loss_per_trade = 2000   # ₹2000 max loss per trade
        self.max_portfolio_risk = 0.02    # 2% max portfolio risk
        
    def calculate_position_size(self, 
                              capital: float,
                              entry_price: float,
                              stop_loss: float,
                              confidence: float = 0.5) -> Dict:
        """Calculate safe position size"""
        
        # Risk per share
        risk_per_share = abs(entry_price - stop_loss)
        
        # Maximum shares based on risk
        max_shares_risk = self.max_loss_per_trade / risk_per_share
        
        # Maximum shares based on capital
        max_shares_capital = self.max_position_size / entry_price
        
        # Adjust based on confidence
        confidence_factor = 0.5 + (confidence * 0.5)  # Scale 0.5 to 1.0
        
        # Take minimum of all constraints
        recommended_shares = min(
            max_shares_risk,
            max_shares_capital
        ) * confidence_factor
        
        return {
            'recommended_shares': int(recommended_shares),
            'max_loss': recommended_shares * risk_per_share,
            'capital_required': recommended_shares * entry_price,
            'risk_percent': (recommended_shares * risk_per_share / capital) * 100
        } 