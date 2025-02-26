import pytest
from datetime import datetime, timedelta
from core.trading_engine import TradingEngine
from ai_strategy.ensemble_model import EnsembleStrategy
from core.backtesting import BacktestEngine

@pytest.mark.integration
async def test_complete_trading_cycle(mock_broker, test_db, sample_market_data):
    """Test complete trading cycle"""
    # Initialize components
    engine = TradingEngine(broker=mock_broker)
    strategy = EnsembleStrategy("test_ensemble")
    
    # Generate and execute signal
    signal = await strategy.generate_signal(sample_market_data)
    assert signal is not None
    
    success = await engine.execute_trade(signal)
    assert success is True
    
    # Verify position
    positions = await engine.get_positions()
    assert len(positions) > 0
    assert positions[0]["symbol"] == signal.symbol
    
    # Test position update
    updated_data = sample_market_data.copy()
    updated_data["last_price"] += 100  # Price increase
    
    await engine.update_positions(updated_data)
    positions = await engine.get_positions()
    assert positions[0]["unrealized_pnl"] > 0

@pytest.mark.integration
async def test_backtest_strategy():
    """Test strategy backtesting"""
    engine = BacktestEngine()
    strategy = EnsembleStrategy("backtest_ensemble")
    
    # Create test data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Run backtest
    results = await engine.run_backtest(
        strategy=strategy,
        start_date=start_date,
        end_date=end_date,
        initial_capital=1000000
    )
    
    assert results is not None
    assert "metrics" in results
    assert "trades" in results
    assert "portfolio_value" in results
    
    # Verify metrics
    metrics = results["metrics"]
    assert "sharpe_ratio" in metrics
    assert "max_drawdown" in metrics
    assert "win_rate" in metrics 