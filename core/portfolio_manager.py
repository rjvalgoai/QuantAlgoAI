from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
import pandas as pd

@dataclass
class PortfolioMetrics:
    total_pnl: float = 0
    win_rate: float = 0
    avg_win: float = 0
    avg_loss: float = 0
    sharpe_ratio: float = 0
    max_drawdown: float = 0

class PortfolioManager:
    def __init__(self):
        self.positions = {}
        self.trades_history = []
        self.daily_pnl = pd.Series()
        
    def update_position(self, trade: Dict):
        """Update portfolio position"""
        symbol = trade['symbol']
        if symbol not in self.positions:
            self.positions[symbol] = {
                'quantity': 0,
                'avg_price': 0,
                'unrealized_pnl': 0
            }
            
        pos = self.positions[symbol]
        if trade['side'] == 'BUY':
            pos['quantity'] += trade['quantity']
            pos['avg_price'] = (pos['avg_price'] * pos['quantity'] + 
                              trade['price'] * trade['quantity']) / pos['quantity']
        else:
            realized_pnl = (trade['price'] - pos['avg_price']) * trade['quantity']
            pos['quantity'] -= trade['quantity']
            self.trades_history.append({
                'time': datetime.now(),
                'symbol': symbol,
                'pnl': realized_pnl
            })
            
    def calculate_metrics(self) -> PortfolioMetrics:
        """Calculate portfolio performance metrics"""
        metrics = PortfolioMetrics()
        
        if self.trades_history:
            pnls = [t['pnl'] for t in self.trades_history]
            metrics.total_pnl = sum(pnls)
            
            winning_trades = [p for p in pnls if p > 0]
            losing_trades = [p for p in pnls if p < 0]
            
            metrics.win_rate = len(winning_trades) / len(pnls)
            metrics.avg_win = sum(winning_trades) / len(winning_trades) if winning_trades else 0
            metrics.avg_loss = sum(losing_trades) / len(losing_trades) if losing_trades else 0
            
        return metrics 