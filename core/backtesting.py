from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from .trading_engine import TradingEngine
from .risk_manager import RiskManager
from ai_strategy.base_strategy import BaseStrategy
from models.trade import Trade
from core.logger import logger

class BacktestEngine:
    """Backtesting engine for strategy evaluation"""
    
    def __init__(self):
        self.trading_engine = TradingEngine()
        self.risk_manager = RiskManager()
        self.trades: List[Trade] = []
        self.positions: Dict[str, Dict] = {}
        self.portfolio_value: List[float] = []
        self.metrics: Dict = {}
        
    async def run_backtest(self, 
                          strategy: BaseStrategy,
                          historical_data: pd.DataFrame,
                          initial_capital: float = 1000000,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> Dict:
        """Run backtest for a strategy"""
        try:
            self.capital = initial_capital
            self.portfolio_value = [initial_capital]
            
            # Filter data by date range
            data = self._filter_data(historical_data, start_date, end_date)
            
            # Run simulation
            for index, row in data.iterrows():
                # Generate signals
                signal = await strategy.generate_signal(row.to_dict())
                if signal:
                    # Execute trade
                    trade = await self._execute_backtest_trade(signal)
                    if trade:
                        self.trades.append(trade)
                        
                # Update positions
                self._update_positions(row['close'])
                
                # Track portfolio value
                self.portfolio_value.append(
                    self._calculate_portfolio_value(row['close'])
                )
                
            # Calculate metrics
            self.metrics = self._calculate_metrics()
            
            return {
                "metrics": self.metrics,
                "trades": self.trades,
                "portfolio_value": self.portfolio_value
            }
            
        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            return {}
            
    def _calculate_metrics(self) -> Dict:
        """Calculate backtest performance metrics"""
        try:
            returns = pd.Series(self.portfolio_value).pct_change().dropna()
            
            return {
                "total_return": (self.portfolio_value[-1] / self.portfolio_value[0]) - 1,
                "sharpe_ratio": self._calculate_sharpe_ratio(returns),
                "max_drawdown": self._calculate_max_drawdown(),
                "win_rate": self._calculate_win_rate(),
                "profit_factor": self._calculate_profit_factor(),
                "total_trades": len(self.trades)
            }
            
        except Exception as e:
            logger.error(f"Metrics calculation failed: {e}")
            return {}

    def _calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe Ratio"""
        try:
            excess_returns = returns - risk_free_rate/252  # Daily risk-free rate
            return np.sqrt(252) * excess_returns.mean() / returns.std()
        except Exception as e:
            logger.error(f"Sharpe ratio calculation failed: {e}")
            return 0.0

    def _calculate_max_drawdown(self) -> float:
        """Calculate Maximum Drawdown"""
        try:
            portfolio_values = pd.Series(self.portfolio_value)
            rolling_max = portfolio_values.expanding().max()
            drawdowns = portfolio_values / rolling_max - 1
            return drawdowns.min()
        except Exception as e:
            logger.error(f"Max drawdown calculation failed: {e}")
            return 0.0

    def _calculate_win_rate(self) -> float:
        """Calculate Win Rate"""
        try:
            if not self.trades:
                return 0.0
            winning_trades = sum(1 for trade in self.trades if trade.pnl > 0)
            return winning_trades / len(self.trades)
        except Exception as e:
            logger.error(f"Win rate calculation failed: {e}")
            return 0.0

    def _calculate_profit_factor(self) -> float:
        """Calculate Profit Factor"""
        try:
            gross_profit = sum(trade.pnl for trade in self.trades if trade.pnl > 0)
            gross_loss = abs(sum(trade.pnl for trade in self.trades if trade.pnl < 0))
            return gross_profit / gross_loss if gross_loss != 0 else 0.0
        except Exception as e:
            logger.error(f"Profit factor calculation failed: {e}")
            return 0.0

    async def _execute_backtest_trade(self, signal) -> Optional[Trade]:
        """Execute trade in backtest"""
        try:
            # Check risk limits
            if not await self.risk_manager.check_trade(signal):
                return None

            # Calculate trade details
            entry_price = signal.price
            quantity = signal.quantity
            
            # Create trade record
            trade = Trade(
                symbol=signal.symbol,
                side=signal.action,
                quantity=quantity,
                entry_price=entry_price,
                timestamp=signal.timestamp,
                strategy=signal.strategy_name
            )

            # Update positions
            if signal.action == "BUY":
                self.capital -= entry_price * quantity
                self._update_position(signal.symbol, quantity, entry_price)
            else:
                self.capital += entry_price * quantity
                self._update_position(signal.symbol, -quantity, entry_price)

            return trade

        except Exception as e:
            logger.error(f"Trade execution failed: {e}")
            return None

    def _update_position(self, symbol: str, quantity: int, price: float):
        """Update position for a symbol"""
        try:
            if symbol not in self.positions:
                self.positions[symbol] = {
                    "quantity": 0,
                    "average_price": 0.0
                }

            position = self.positions[symbol]
            old_quantity = position["quantity"]
            new_quantity = old_quantity + quantity

            if new_quantity != 0:
                # Update average price
                old_value = old_quantity * position["average_price"]
                trade_value = quantity * price
                position["average_price"] = (old_value + trade_value) / new_quantity

            position["quantity"] = new_quantity

        except Exception as e:
            logger.error(f"Position update failed: {e}")

    def _calculate_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate current portfolio value"""
        try:
            position_value = sum(
                pos["quantity"] * current_prices[symbol]
                for symbol, pos in self.positions.items()
            )
            return self.capital + position_value
        except Exception as e:
            logger.error(f"Portfolio value calculation failed: {e}")
            return self.capital
