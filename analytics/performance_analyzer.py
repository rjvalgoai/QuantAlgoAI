from typing import Dict, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    total_pnl: float = 0.0
    win_rate: float = 0.0
    profit_factor: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    avg_trade: float = 0.0
    num_trades: int = 0
    best_trade: float = 0.0
    worst_trade: float = 0.0
    avg_holding_time: float = 0.0

class PerformanceAnalyzer:
    def __init__(self):
        self.trades_df = pd.DataFrame()
        self.daily_pnl = pd.Series()
        self.metrics = PerformanceMetrics()
        
    def add_trade(self, trade: Dict):
        """Add trade to analysis"""
        self.trades_df = pd.concat([
            self.trades_df,
            pd.DataFrame([trade])
        ])
        self._update_metrics()
        
    def _update_metrics(self):
        """Update performance metrics"""
        if not self.trades_df.empty:
            # Daily P&L
            self.daily_pnl = self.trades_df.groupby(
                pd.to_datetime(self.trades_df['exit_time']).dt.date
            )['pnl'].sum()
            
            # Basic metrics
            self.metrics.total_pnl = self.trades_df['pnl'].sum()
            self.metrics.num_trades = len(self.trades_df)
            
            # Win rate
            winning_trades = self.trades_df[self.trades_df['pnl'] > 0]
            self.metrics.win_rate = len(winning_trades) / self.metrics.num_trades
            
            # Profit factor
            gross_profit = winning_trades['pnl'].sum()
            gross_loss = self.trades_df[self.trades_df['pnl'] < 0]['pnl'].sum()
            self.metrics.profit_factor = abs(gross_profit / gross_loss) if gross_loss != 0 else float('inf')
            
            # Trade statistics
            self.metrics.avg_trade = self.trades_df['pnl'].mean()
            self.metrics.best_trade = self.trades_df['pnl'].max()
            self.metrics.worst_trade = self.trades_df['pnl'].min()
            
            # Advanced metrics
            self.metrics.sharpe_ratio = self._calculate_sharpe()
            self.metrics.max_drawdown = self._calculate_drawdown()
            
    def _calculate_sharpe(self, risk_free_rate: float = 0.05) -> float:
        """Calculate Sharpe Ratio"""
        if len(self.daily_pnl) > 1:
            returns = self.daily_pnl.pct_change().dropna()
            excess_returns = returns - (risk_free_rate / 252)
            return np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        return 0.0
        
    def _calculate_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        if len(self.daily_pnl) > 0:
            cumulative = self.daily_pnl.cumsum()
            running_max = cumulative.expanding().max()
            drawdown = (cumulative - running_max) / running_max
            return abs(drawdown.min())
        return 0.0
        
    def get_summary(self) -> Dict:
        """Get performance summary"""
        return {
            'Total P&L': f"₹{self.metrics.total_pnl:,.2f}",
            'Win Rate': f"{self.metrics.win_rate*100:.1f}%",
            'Profit Factor': f"{self.metrics.profit_factor:.2f}",
            'Sharpe Ratio': f"{self.metrics.sharpe_ratio:.2f}",
            'Max Drawdown': f"{self.metrics.max_drawdown*100:.1f}%",
            'Number of Trades': self.metrics.num_trades,
            'Average Trade': f"₹{self.metrics.avg_trade:,.2f}",
            'Best Trade': f"₹{self.metrics.best_trade:,.2f}",
            'Worst Trade': f"₹{self.metrics.worst_trade:,.2f}"
        } 