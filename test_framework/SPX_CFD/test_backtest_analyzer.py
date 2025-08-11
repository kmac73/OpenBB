"""
Test Backtest Analyzer - All 22 Performance Metrics - Phase 0 Test Suite
Tests written BEFORE implementation - Test-First Approach

These tests will FAIL initially - this is expected.
Implementation will be created to make these tests pass.
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os
from unittest.mock import Mock
from datetime import datetime

# Add the parent directory to Python path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import will fail initially - this is expected in Phase 0
try:
    from app.common.backtest_analyzer import BacktestAnalyzer, PerformanceMetrics
except ImportError:
    # Expected in Phase 0 - implementation doesn't exist yet
    BacktestAnalyzer = Mock
    PerformanceMetrics = Mock

class TestBacktestAnalyzerInitialization:
    """Test analyzer initialization and basic setup"""
    
    def test_analyzer_initialization_with_risk_free_rate(self):
        """Test analyzer initializes with 3% default risk-free rate"""
        analyzer = BacktestAnalyzer()
        
        # TODO: FUTURE_CHANGE - Research market norms for Sharpe calculation
        assert analyzer.risk_free_rate == 0.03  # 3% default as specified
        
    def test_analyzer_custom_risk_free_rate(self):
        """Test analyzer accepts custom risk-free rate"""
        custom_rate = 0.025  # 2.5%
        analyzer = BacktestAnalyzer(risk_free_rate=custom_rate)
        
        assert analyzer.risk_free_rate == custom_rate

class TestBasicTradeMetrics:
    """Test basic trade counting and classification metrics"""
    
    def test_total_trades_count_with_real_data(self, expected_manual_calculations):
        """Test total trades calculation with real trade data"""
        analyzer = BacktestAnalyzer()
        
        # Mock trades based on expected manual calculations
        # TODO: Replace with actual calculated values during Phase 0
        mock_trades = []
        expected_count = expected_manual_calculations['expected_total_trades']
        
        for i in range(expected_count):
            mock_trades.append(Mock(
                direction="LONG" if i % 2 == 0 else "SHORT",
                net_pnl=10.0 if i % 3 == 0 else -5.0,  # Mix of wins and losses
                gross_pnl=15.0 if i % 3 == 0 else -5.0,
                costs=5.0,
                duration_minutes=30 + i * 10
            ))
        
        metrics = analyzer.calculate_all_metrics(mock_trades, [], [])
        
        assert metrics['total_trades'] == expected_count
        
    def test_long_short_trade_breakdown(self, expected_manual_calculations):
        """Test breakdown of long vs short trades"""
        analyzer = BacktestAnalyzer()
        
        # Create mixed long/short trades
        trades = [
            Mock(direction="LONG", net_pnl=10.0, gross_pnl=15.0, costs=5.0, duration_minutes=30),
            Mock(direction="LONG", net_pnl=5.0, gross_pnl=10.0, costs=5.0, duration_minutes=25),
            Mock(direction="SHORT", net_pnl=-8.0, gross_pnl=-3.0, costs=5.0, duration_minutes=45),
            Mock(direction="SHORT", net_pnl=12.0, gross_pnl=17.0, costs=5.0, duration_minutes=35),
        ]
        
        metrics = analyzer.calculate_all_metrics(trades, [], [])
        
        assert metrics['total_long_trades'] == 2
        assert metrics['total_short_trades'] == 2
        assert metrics['total_trades'] == 4
        
    def test_winning_losing_trades_classification(self):
        """Test classification of winning vs losing trades"""
        analyzer = BacktestAnalyzer()
        
        trades = [
            Mock(direction="LONG", net_pnl=10.0, gross_pnl=15.0, costs=5.0, duration_minutes=30),   # Win
            Mock(direction="LONG", net_pnl=-8.0, gross_pnl=-3.0, costs=5.0, duration_minutes=25),  # Loss
            Mock(direction="SHORT", net_pnl=5.0, gross_pnl=10.0, costs=5.0, duration_minutes=45),  # Win
            Mock(direction="SHORT", net_pnl=-12.0, gross_pnl=-7.0, costs=5.0, duration_minutes=35), # Loss
            Mock(direction="LONG", net_pnl=0.0, gross_pnl=5.0, costs=5.0, duration_minutes=20),     # Breakeven (not win)
        ]
        
        metrics = analyzer.calculate_all_metrics(trades, [], [])
        
        assert metrics['winning_trades'] == 2  # Only net_pnl > 0
        assert metrics['losing_trades'] == 3   # net_pnl <= 0
        
    def test_win_rate_calculation(self):
        """Test win rate percentage calculation"""
        analyzer = BacktestAnalyzer()
        
        trades = [
            Mock(direction="LONG", net_pnl=10.0, gross_pnl=15.0, costs=5.0, duration_minutes=30),   # Win
            Mock(direction="LONG", net_pnl=5.0, gross_pnl=10.0, costs=5.0, duration_minutes=25),   # Win
            Mock(direction="SHORT", net_pnl=-8.0, gross_pnl=-3.0, costs=5.0, duration_minutes=45), # Loss
            Mock(direction="SHORT", net_pnl=-12.0, gross_pnl=-7.0, costs=5.0, duration_minutes=35) # Loss
        ]
        
        metrics = analyzer.calculate_all_metrics(trades, [], [])
        
        expected_win_rate = (2 / 4) * 100  # 50%
        assert metrics['win_rate'] == expected_win_rate

class TestPnLCalculations:
    """Test P&L calculations - gross, net, costs"""
    
    def test_pnl_calculations_gross_and_net(self):
        """Test total P&L calculations for gross and net"""
        analyzer = BacktestAnalyzer()
        
        trades = [
            Mock(direction="LONG", net_pnl=95.0, gross_pnl=100.0, costs=5.0, duration_minutes=30),
            Mock(direction="SHORT", net_pnl=45.0, gross_pnl=50.0, costs=5.0, duration_minutes=25),
            Mock(direction="LONG", net_pnl=-35.0, gross_pnl=-30.0, costs=5.0, duration_minutes=45),
        ]
        
        metrics = analyzer.calculate_all_metrics(trades, [], [])
        
        assert metrics['total_pnl'] == 105.0     # 95 + 45 - 35 (net)
        assert metrics['gross_pnl'] == 120.0     # 100 + 50 - 30 (gross)
        assert metrics['total_costs'] == 15.0    # 5 + 5 + 5
        
    def test_win_loss_averages(self):
        """Test average win and average loss calculations"""
        analyzer = BacktestAnalyzer()
        
        trades = [
            Mock(direction="LONG", net_pnl=100.0, gross_pnl=105.0, costs=5.0, duration_minutes=30),  # Win
            Mock(direction="SHORT", net_pnl=50.0, gross_pnl=55.0, costs=5.0, duration_minutes=25),   # Win
            Mock(direction="LONG", net_pnl=-30.0, gross_pnl=-25.0, costs=5.0, duration_minutes=45),  # Loss
            Mock(direction="SHORT", net_pnl=-20.0, gross_pnl=-15.0, costs=5.0, duration_minutes=35)  # Loss
        ]
        
        metrics = analyzer.calculate_all_metrics(trades, [], [])
        
        # Average win: (100 + 50) / 2 = 75.0
        # Average loss: -(30 + 20) / 2 = -25.0 (negative)
        assert metrics['avg_win'] == 75.0
        assert metrics['avg_loss'] == -25.0
        
    def test_profit_factor_calculation(self):
        """Test profit factor calculation: total wins / abs(total losses)"""
        analyzer = BacktestAnalyzer()
        
        trades = [
            Mock(direction="LONG", net_pnl=100.0, gross_pnl=105.0, costs=5.0, duration_minutes=30),  # Win
            Mock(direction="SHORT", net_pnl=50.0, gross_pnl=55.0, costs=5.0, duration_minutes=25),   # Win
            Mock(direction="LONG", net_pnl=-30.0, gross_pnl=-25.0, costs=5.0, duration_minutes=45),  # Loss
            Mock(direction="SHORT", net_pnl=-20.0, gross_pnl=-15.0, costs=5.0, duration_minutes=35)  # Loss
        ]
        
        metrics = analyzer.calculate_all_metrics(trades, [], [])
        
        # Profit factor = total wins / abs(total losses) = 150 / 50 = 3.0
        assert metrics['profit_factor'] == 3.0
        
    def test_cost_ratio_calculation(self):
        """Test cost ratio calculation: total costs / gross profits"""
        analyzer = BacktestAnalyzer()
        
        trades = [
            Mock(direction="LONG", net_pnl=95.0, gross_pnl=100.0, costs=5.0, duration_minutes=30),
            Mock(direction="SHORT", net_pnl=45.0, gross_pnl=50.0, costs=5.0, duration_minutes=25),
        ]
        
        metrics = analyzer.calculate_all_metrics(trades, [], [])
        
        # Cost ratio = total costs / gross profits = 10 / 150 = 0.0667
        expected_cost_ratio = 10.0 / 150.0
        assert abs(metrics['cost_ratio'] - expected_cost_ratio) < 0.0001

class TestDrawdownCalculations:
    """Test drawdown calculations - both methods for comparison"""
    
    def test_drawdown_both_methods(self):
        """Test drawdown calculation using both end-of-day and continuous methods"""
        analyzer = BacktestAnalyzer()
        
        # Mock equity curve with drawdowns
        equity_curve = [10000, 10100, 10050, 9900, 9950, 10200, 10150]  # Peak at 10200, trough at 9900
        trades = [
            Mock(net_pnl=100, timestamp=datetime(2024, 6, 24, 10, 0)),
            Mock(net_pnl=-50, timestamp=datetime(2024, 6, 24, 11, 0)),
            Mock(net_pnl=-150, timestamp=datetime(2024, 6, 24, 12, 0)),  # Drawdown here
            Mock(net_pnl=50, timestamp=datetime(2024, 6, 24, 13, 0)),
            Mock(net_pnl=250, timestamp=datetime(2024, 6, 24, 14, 0)),
            Mock(net_pnl=-50, timestamp=datetime(2024, 6, 24, 15, 0))
        ]
        
        drawdown_result = analyzer.calculate_drawdown_both_methods(equity_curve, trades)
        
        # TODO: PRODUCTION_DECISION - Confirm which method for production code
        assert 'eod_method' in drawdown_result
        assert 'continuous_method' in drawdown_result
        assert 'primary' in drawdown_result
        assert drawdown_result['comparison_note'] == 'Both methods calculated for development validation'
        
    def test_max_drawdown_percentage_calculation(self):
        """Test max drawdown as percentage of account balance"""
        analyzer = BacktestAnalyzer()
        
        # Equity curve: start at 10000, peak at 11000, trough at 9500
        equity_curve = [10000, 10500, 11000, 10200, 9500, 9800, 10500]
        
        max_dd = analyzer.calculate_max_drawdown(equity_curve)
        
        # Max drawdown = (11000 - 9500) / 11000 = 13.64%
        expected_max_dd = (11000 - 9500) / 11000 * 100
        assert abs(max_dd - expected_max_dd) < 0.01
        
    def test_avg_drawdown_calculation(self):
        """Test average drawdown calculation"""
        analyzer = BacktestAnalyzer()
        
        equity_curve = [10000, 9900, 9800, 9900, 10000, 9950, 9850, 9950, 10100]
        
        avg_dd = analyzer.calculate_avg_drawdown(equity_curve)
        
        # Should calculate average of all drawdown periods
        assert avg_dd > 0  # Should be positive percentage
        assert isinstance(avg_dd, (int, float))

class TestTimeBasedMetrics:
    """Test trade duration and time-based metrics"""
    
    def test_trade_duration_metrics(self):
        """Test shortest, longest, and average trade duration calculations"""
        analyzer = BacktestAnalyzer()
        
        trades = [
            Mock(direction="LONG", net_pnl=10.0, gross_pnl=15.0, costs=5.0, duration_minutes=15),   # Shortest
            Mock(direction="SHORT", net_pnl=5.0, gross_pnl=10.0, costs=5.0, duration_minutes=45),   # Longest
            Mock(direction="LONG", net_pnl=-8.0, gross_pnl=-3.0, costs=5.0, duration_minutes=30),
            Mock(direction="SHORT", net_pnl=12.0, gross_pnl=17.0, costs=5.0, duration_minutes=25)
        ]
        
        metrics = analyzer.calculate_all_metrics(trades, [], [])
        
        assert metrics['shortest_trade_minutes'] == 15
        assert metrics['longest_trade_minutes'] == 45
        assert metrics['avg_trade_duration_minutes'] == (15 + 45 + 30 + 25) / 4  # 28.75
        
    def test_empty_trades_duration_handling(self):
        """Test duration metrics with empty trades list"""
        analyzer = BacktestAnalyzer()
        
        trades = []
        metrics = analyzer.calculate_all_metrics(trades, [], [])
        
        assert metrics['shortest_trade_minutes'] == 0
        assert metrics['longest_trade_minutes'] == 0
        assert metrics['avg_trade_duration_minutes'] == 0

class TestReturnMetrics:
    """Test return and equity calculations"""
    
    def test_total_return_calculation(self):
        """Test total return percentage calculation"""
        analyzer = BacktestAnalyzer()
        
        # Starting equity 10000, ending equity 11500
        equity_curve = [10000, 10200, 10800, 11200, 11500]
        
        total_return = analyzer.calculate_total_return(equity_curve)
        
        # Total return = (11500 - 10000) / 10000 * 100 = 15%
        expected_return = (11500 - 10000) / 10000 * 100
        assert abs(total_return - expected_return) < 0.01
        
    def test_final_equity_tracking(self):
        """Test final equity value tracking"""
        analyzer = BacktestAnalyzer()
        
        equity_curve = [10000, 10200, 10800, 11200, 11500]
        trades = []
        
        metrics = analyzer.calculate_all_metrics(trades, [], equity_curve)
        
        assert metrics['final_equity'] == 11500
        
    def test_empty_equity_curve_handling(self):
        """Test handling of empty equity curve"""
        analyzer = BacktestAnalyzer()
        
        equity_curve = []
        trades = []
        
        metrics = analyzer.calculate_all_metrics(trades, [], equity_curve)
        
        assert metrics['final_equity'] == 0
        assert metrics['total_return'] == 0

class TestVaRCalculation:
    """Test Value at Risk calculation - parametric method, 95%, 1-day"""
    
    def test_var_parametric_95_1day(self):
        """Test VaR using parametric method, 95% confidence, 1-day horizon"""
        analyzer = BacktestAnalyzer()
        
        # Mock daily P&L returns
        daily_summaries = [
            {'date': datetime(2024, 6, 24).date(), 'daily_net_pnl': 100.0},
            {'date': datetime(2024, 6, 25).date(), 'daily_net_pnl': -50.0},
            {'date': datetime(2024, 6, 26).date(), 'daily_net_pnl': 75.0},
            {'date': datetime(2024, 6, 27).date(), 'daily_net_pnl': -25.0},
            {'date': datetime(2024, 6, 28).date(), 'daily_net_pnl': 25.0}
        ]
        
        var_result = analyzer.calculate_var_parametric_95_1day(daily_summaries)
        
        # Should return VaR value using normal distribution assumption
        assert isinstance(var_result, (int, float))
        assert var_result < 0  # VaR should typically be negative (potential loss)
        
    def test_var_insufficient_data(self):
        """Test VaR calculation with insufficient data points"""
        analyzer = BacktestAnalyzer()
        
        # Only 1 data point - insufficient for VaR
        daily_summaries = [
            {'date': datetime(2024, 6, 24).date(), 'daily_net_pnl': 100.0}
        ]
        
        var_result = analyzer.calculate_var_parametric_95_1day(daily_summaries)
        
        assert var_result == 0  # Should return 0 for insufficient data
        
    def test_var_normal_distribution_assumption(self):
        """Test VaR calculation uses normal distribution (parametric method)"""
        analyzer = BacktestAnalyzer()
        
        # Create normally distributed daily returns
        np.random.seed(42)  # For reproducible tests
        daily_returns = np.random.normal(10, 20, 30)  # Mean=10, Std=20, 30 days
        
        daily_summaries = [
            {'date': datetime(2024, 6, i+1).date(), 'daily_net_pnl': ret}
            for i, ret in enumerate(daily_returns[:30])
        ]
        
        var_result = analyzer.calculate_var_parametric_95_1day(daily_summaries)
        
        # Verify calculation: VaR = mean - (1.645 * std) for 95% confidence
        mean_return = np.mean(daily_returns)
        std_return = np.std(daily_returns)
        expected_var = mean_return - (1.645 * std_return)
        
        assert abs(var_result - expected_var) < 0.1  # Allow small floating point differences

class TestSharpeRatioCalculation:
    """Test Sharpe ratio calculation with configurable risk-free rate"""
    
    def test_sharpe_ratio_with_3m_rate(self):
        """Test Sharpe ratio calculation with 3% risk-free rate (3M treasury)"""
        analyzer = BacktestAnalyzer(risk_free_rate=0.03)  # 3% as specified
        
        # Mock daily summaries with varying returns
        daily_summaries = [
            {'date': datetime(2024, 6, 24).date(), 'daily_net_pnl': 100.0},
            {'date': datetime(2024, 6, 25).date(), 'daily_net_pnl': -50.0},
            {'date': datetime(2024, 6, 26).date(), 'daily_net_pnl': 75.0},
            {'date': datetime(2024, 6, 27).date(), 'daily_net_pnl': -25.0},
            {'date': datetime(2024, 6, 28).date(), 'daily_net_pnl': 25.0}
        ]
        
        sharpe = analyzer.calculate_sharpe_ratio(daily_summaries)
        
        # Should calculate: (average return - risk free rate) / std dev of returns
        assert isinstance(sharpe, (int, float))
        # TODO: FUTURE_CHANGE - Research market norms for annualization
        
    def test_sharpe_ratio_zero_std_dev(self):
        """Test Sharpe ratio with zero standard deviation (constant returns)"""
        analyzer = BacktestAnalyzer(risk_free_rate=0.03)
        
        # All returns are the same - zero standard deviation
        daily_summaries = [
            {'date': datetime(2024, 6, 24).date(), 'daily_net_pnl': 50.0},
            {'date': datetime(2024, 6, 25).date(), 'daily_net_pnl': 50.0},
            {'date': datetime(2024, 6, 26).date(), 'daily_net_pnl': 50.0}
        ]
        
        sharpe = analyzer.calculate_sharpe_ratio(daily_summaries)
        
        # Should handle division by zero gracefully
        assert sharpe == 0 or sharpe == float('inf')  # Depends on implementation approach

class TestMetricsIntegration:
    """Test integration of all 22 metrics calculation"""
    
    def test_calculate_all_22_metrics_integration(self, expected_manual_calculations):
        """Test calculation of all 22 required metrics together"""
        analyzer = BacktestAnalyzer()
        
        # Create comprehensive test data
        trades = [
            Mock(direction="LONG", net_pnl=100.0, gross_pnl=105.0, costs=5.0, duration_minutes=30),
            Mock(direction="SHORT", net_pnl=-50.0, gross_pnl=-45.0, costs=5.0, duration_minutes=25),
            Mock(direction="LONG", net_pnl=75.0, gross_pnl=80.0, costs=5.0, duration_minutes=45),
            Mock(direction="SHORT", net_pnl=-25.0, gross_pnl=-20.0, costs=5.0, duration_minutes=35)
        ]
        
        daily_summaries = [
            {'date': datetime(2024, 6, 24).date(), 'daily_net_pnl': 50.0},
            {'date': datetime(2024, 6, 25).date(), 'daily_net_pnl': -25.0},
            {'date': datetime(2024, 6, 26).date(), 'daily_net_pnl': 75.0}
        ]
        
        equity_curve = [10000, 10050, 10025, 10100]
        
        metrics = analyzer.calculate_all_metrics(trades, daily_summaries, equity_curve)
        
        # Verify all 22 metrics are present
        expected_metrics = [
            'total_trades', 'winning_trades', 'losing_trades', 'total_long_trades', 
            'total_short_trades', 'win_rate', 'total_pnl', 'gross_pnl', 'total_costs',
            'avg_win', 'avg_loss', 'max_drawdown', 'avg_drawdown', 'total_return',
            'final_equity', 'profit_factor', 'cost_ratio', 'shortest_trade_minutes',
            'longest_trade_minutes', 'avg_trade_duration_minutes', 'sharpe_ratio',
            'value_at_risk'
        ]
        
        for metric in expected_metrics:
            assert metric in metrics, f"Missing metric: {metric}"
            assert metrics[metric] is not None, f"Metric {metric} is None"
            
    def test_real_data_validation_against_manual_calculations(self, expected_manual_calculations):
        """Test that calculated metrics match hand-calculated expected values"""
        analyzer = BacktestAnalyzer()
        
        # TODO: This test will be populated with actual manual calculations
        # during Phase 0 test creation process
        
        # For now, verify the structure exists for validation
        assert 'expected_total_trades' in expected_manual_calculations
        assert 'expected_win_rate' in expected_manual_calculations
        assert 'expected_total_pnl' in expected_manual_calculations
        assert 'note' in expected_manual_calculations
        
        # Actual validation will be added after manual calculations are complete
        # Example structure:
        # calculated_metrics = analyzer.calculate_all_metrics(real_trades, real_daily_summaries, real_equity_curve)
        # assert abs(calculated_metrics['total_pnl'] - expected_manual_calculations['expected_total_pnl']) < 0.01

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_empty_trades_list_handling(self):
        """Test analyzer handles empty trades list gracefully"""
        analyzer = BacktestAnalyzer()
        
        trades = []
        daily_summaries = []
        equity_curve = []
        
        metrics = analyzer.calculate_all_metrics(trades, daily_summaries, equity_curve)
        
        assert metrics['total_trades'] == 0
        assert metrics['winning_trades'] == 0
        assert metrics['losing_trades'] == 0
        assert metrics['win_rate'] == 0
        
    def test_no_fake_data_validation(self):
        """Test that no synthetic data is created to make tests pass"""
        analyzer = BacktestAnalyzer()
        
        # This test ensures we never create fake data
        # All test data must be based on real market data or manual calculations
        trades = []  # Empty trades - should not be artificially populated
        
        metrics = analyzer.calculate_all_metrics(trades, [], [])
        
        # Verify realistic empty results, not fake positive results
        assert metrics['total_trades'] == 0
        assert metrics['total_pnl'] == 0
        assert metrics['profit_factor'] == 0  # Should handle division by zero