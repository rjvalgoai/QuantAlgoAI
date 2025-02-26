import numpy as np
from typing import Dict, List

class MarketAnalyzer:
    def __init__(self):
        self.price_history: Dict[str, List[float]] = {}
    
    def update_price(self, symbol: str, price: float):
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        self.price_history[symbol].append(price)
    
    def calculate_vwap(self, symbol: str) -> float:
        prices = self.price_history.get(symbol, [])
        if not prices:
            return 0
        return np.mean(prices) 