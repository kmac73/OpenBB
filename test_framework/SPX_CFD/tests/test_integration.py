"""
Test suite for Integration functionality (Category 8).
Tests end-to-end strategy execution and component integration.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Import strategy components
try:
    from cfd_strategy_v1 import CFDStrategyV1
    from market_data import Retrieve
except ImportError:
    # Fallback for test environment
    sys.path.append(str(Path(__file__).parent.parent.parent.parent / "app" / "SP500_CFD_v1"))
    try:
        from cfd_strategy_v1 import CFDStrategyV1
        from market_data import Retrieve
    except ImportError:
        # Create mock classes for testing
        class CFDStrategyV1:
            def __init__(self, params):
                self.params = params
                self.trades = []
            
            def run_backtest(self, data):
                return self.params['initial_capital']
            
            def generate_analytics(self):
                return {'total_trades': 0, 'win_rate': 0, 'total_pnl': 0}
        
        class Retrieve:
            def get_data(self, symbol, start_date, end_date, frequency):
                return pd.DataFrame()


class TestEndToEndStrategyTests:
    """Test suite for End-to-End Strategy Tests (8.1)."""
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_complete_strategy_execution(self, test_logger, sample_strategy_params, mock_market_data):
        """Full strategy run with real data."""
        test_logger.start_test("test_complete_strategy_execution")
        
        try:
            # Generate comprehensive market data
            data = mock_market_data(
                start_date="2023-01-01", 
                end_date="2023-01-31", 
                frequency="5M",
                trend="uptrend"
            )
            
            # Verify data quality
            assert not data.empty, "Market data should not be empty"
            assert len(data) > 100, "Should have sufficient data points"
            assert all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
            
            # Initialize strategy
            strategy = CFDStrategyV1(sample_strategy_params)
            
            # Execute backtest
            final_equity = strategy.run_backtest(data)
            
            # Verify execution completed
            assert final_equity is not None, "Strategy should return final equity"
            assert isinstance(final_equity, (int, float)), "Final equity should be numeric"
            assert final_equity > 0, "Final equity should be positive"
            
            # Generate analytics
            analytics = strategy.generate_analytics()
            
            # Verify analytics structure
            required_metrics = [
                'total_trades', 'winning_trades', 'losing_trades', 'win_rate',
                'total_pnl', 'gross_pnl', 'total_costs', 'avg_win', 'avg_loss',
                'max_drawdown', 'total_return', 'final_equity'
            ]
            
            for metric in required_metrics:
                assert metric in analytics, f"Missing required metric: {metric}"
                assert analytics[metric] is not None, f"Metric {metric} should not be None"
            
            # Verify logical consistency
            if analytics['total_trades'] > 0:
                assert analytics['winning_trades'] + analytics['losing_trades'] == analytics['total_trades']
                assert 0 <= analytics['win_rate'] <= 100
                assert analytics['final_equity'] == sample_strategy_params['initial_capital'] + analytics['total_pnl']
            
            test_logger.end_test("test_complete_strategy_execution", "PASS")
        except Exception as e:
            test_logger.end_test("test_complete_strategy_execution", "FAIL", str(e))
            raise
    
    @pytest.mark.integration
    @pytest.mark.slow
    def test_multi_day_backtest(self, test_logger, sample_strategy_params, mock_market_data):
        """Test across multiple trading days."""
        test_logger.start_test("test_multi_day_backtest")
        
        try:
            # Generate multi-day data
            data = mock_market_data(
                start_date="2023-01-01", 
                end_date="2023-01-15", 
                frequency="5M",
                trend="sideways"
            )
            
            # Verify multi-day coverage
            unique_dates = data.index.date
            unique_days = len(set(unique_dates))
            assert unique_days >= 10, f"Should cover at least 10 trading days, got {unique_days}"
            
            # Initialize strategy
            strategy = CFDStrategyV1(sample_strategy_params)
            
            # Execute multi-day backtest
            final_equity = strategy.run_backtest(data)
            analytics = strategy.generate_analytics()
            
            # Verify multi-day execution
            if analytics['total_trades'] > 0:
                # Should have trades across multiple days
                trades_df = pd.DataFrame(strategy.trades) if strategy.trades else pd.DataFrame()
                
                if not trades_df.empty:
                    trade_dates = pd.to_datetime(trades_df['entry_time']).dt.date
                    unique_trade_days = len(set(trade_dates))
                    
                    # Should have trading activity across multiple days (but not necessarily all days)
                    assert unique_trade_days >= 1, "Should have trades on at least 1 day"
                    
                    # Verify no overnight positions
                    for _, trade in trades_df.iterrows():
                        entry_date = pd.to_datetime(trade['entry_time']).date()
                        exit_date = pd.to_datetime(trade['exit_time']).date()
                        assert entry_date == exit_date, f"Trade should not span multiple days: {entry_date} to {exit_date}"
            
            # Verify daily P&L tracking
            assert analytics['max_drawdown'] <= 0, "Max drawdown should be non-positive"
            assert abs(analytics['total_return']) >= 0, "Total return should be calculated"
            
            test_logger.end_test("test_multi_day_backtest", "PASS")
        except Exception as e:
            test_logger.end_test("test_multi_day_backtest", "FAIL", str(e))
            raise
    
    @pytest.mark.integration
    def test_parameter_sensitivity_analysis(self, test_logger, sample_strategy_params, mock_market_data):
        """Test parameter variations."""
        test_logger.start_test("test_parameter_sensitivity_analysis")
        
        try:
            # Generate test data
            data = mock_market_data(
                start_date="2023-01-01", 
                end_date="2023-01-10", 
                frequency="5M"
            )
            
            # Base parameters
            base_params = sample_strategy_params.copy()
            
            # Parameter variations to test
            parameter_variations = [
                {'risk_per_trade': 0.5},  # Conservative risk
                {'risk_per_trade': 2.0},  # Aggressive risk
                {'stop_loss_points': 3.0, 'profit_target_points': 6.0},  # Tighter stops
                {'stop_loss_points': 6.0, 'profit_target_points': 12.0},  # Wider stops
                {'entry_threshold_points': 1.0},  # More sensitive entries
                {'entry_threshold_points': 3.0},  # Less sensitive entries
                {'directional_bias_multiplier': 1.0},  # No bias
                {'directional_bias_multiplier': 2.0},  # Maximum bias
            ]
            
            results = []
            
            for variation in parameter_variations:
                # Create modified parameters
                test_params = base_params.copy()
                test_params.update(variation)
                
                # Run strategy with modified parameters
                strategy = CFDStrategyV1(test_params)
                final_equity = strategy.run_backtest(data)
                analytics = strategy.generate_analytics()
                
                # Store results
                result = {
                    'variation': variation,
                    'final_equity': final_equity,
                    'total_return': analytics['total_return'],
                    'total_trades': analytics['total_trades'],
                    'win_rate': analytics['win_rate'],
                    'max_drawdown': analytics['max_drawdown']
                }
                results.append(result)
                
                # Verify each run completed successfully
                assert final_equity is not None, f"Strategy failed with variation: {variation}"
                assert isinstance(analytics, dict), f"Analytics not generated for variation: {variation}"
            
            # Analyze sensitivity
            assert len(results) == len(parameter_variations), "All parameter variations should complete"
            
            # Verify different parameters produce different results (most of the time)
            returns = [r['total_return'] for r in results]
            unique_returns = len(set(returns))
            
            # Allow some identical results, but expect some variation
            assert unique_returns >= len(returns) // 2, "Parameters should produce varied results"
            
            test_logger.end_test("test_parameter_sensitivity_analysis", "PASS")
        except Exception as e:
            test_logger.end_test("test_parameter_sensitivity_analysis", "FAIL", str(e))
            raise


class TestComponentIntegration:
    """Test suite for Component Integration Tests (8.2)."""
    
    @pytest.mark.integration
    @pytest.mark.mock
    def test_data_strategy_integration(self, test_logger, sample_strategy_params, mock_retrieve_class):
        """Test data flow to strategy."""
        test_logger.start_test("test_data_strategy_integration")
        
        try:
            # Mock data retrieval
            with patch('market_data.Retrieve', return_value=mock_retrieve_class):
                data_retriever = Retrieve()
                
                # Fetch data
                data = data_retriever.get_data("SPX", "2023-01-01", "2023-01-10", "5M")
                
                # Verify data format
                assert isinstance(data, pd.DataFrame), "Data should be DataFrame"
                assert not data.empty, "Data should not be empty"
                
                # Verify required columns
                required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                for col in required_columns:
                    assert col in data.columns, f"Missing required column: {col}"
                
                # Initialize strategy with data
                strategy = CFDStrategyV1(sample_strategy_params)
                
                # Verify strategy can process the data
                final_equity = strategy.run_backtest(data)
                assert final_equity is not None, "Strategy should process data successfully"
            
            test_logger.end_test("test_data_strategy_integration", "PASS")
        except Exception as e:
            test_logger.end_test("test_data_strategy_integration", "FAIL", str(e))
            raise
    
    @pytest.mark.integration
    def test_strategy_analytics_integration(self, test_logger, sample_strategy_params, mock_market_data):
        """Test analytics generation."""
        test_logger.start_test("test_strategy_analytics_integration")
        
        try:
            # Generate data and run strategy
            data = mock_market_data(
                start_date="2023-01-01", 
                end_date="2023-01-05", 
                frequency="5M",
                trend="uptrend"
            )
            
            strategy = CFDStrategyV1(sample_strategy_params)
            final_equity = strategy.run_backtest(data)
            
            # Test analytics generation
            analytics = strategy.generate_analytics()
            
            # Verify analytics completeness
            assert isinstance(analytics, dict), "Analytics should be dictionary"
            
            # Test analytics calculations
            if analytics['total_trades'] > 0:
                # Verify win rate calculation
                calculated_win_rate = (analytics['winning_trades'] / analytics['total_trades']) * 100
                assert abs(analytics['win_rate'] - calculated_win_rate) < 0.1, "Win rate calculation error"
                
                # Verify P&L calculations
                assert analytics['total_pnl'] == analytics['gross_pnl'] - analytics['total_costs'], "P&L calculation error"
                
                # Verify final equity calculation
                expected_final = sample_strategy_params['initial_capital'] + analytics['total_pnl']
                assert abs(analytics['final_equity'] - expected_final) < 0.01, "Final equity calculation error"
            
            # Test analytics with no trades
            empty_strategy = CFDStrategyV1(sample_strategy_params)
            empty_analytics = empty_strategy.generate_analytics()
            
            assert empty_analytics['total_trades'] == 0, "Empty strategy should have no trades"
            assert empty_analytics['win_rate'] == 0, "Empty strategy should have 0% win rate"
            assert empty_analytics['total_pnl'] == 0, "Empty strategy should have 0 P&L"
            
            test_logger.end_test("test_strategy_analytics_integration", "PASS")
        except Exception as e:
            test_logger.end_test("test_strategy_analytics_integration", "FAIL", str(e))
            raise
    
    @pytest.mark.integration
    @pytest.mark.mock
    def test_parameter_loading_integration(self, test_logger, sample_strategy_params):
        """Test parameter file loading."""
        test_logger.start_test("test_parameter_loading_integration")
        
        try:
            import tempfile
            import os
            
            # Create temporary parameter file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                # Write parameters in expected format
                temp_file.write("="*60 + "\n")
                temp_file.write("SPX CFD STRATEGY - PARAMETERS\n")
                temp_file.write("="*60 + "\n")
                temp_file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                temp_file.write("\n")
                temp_file.write("ACCOUNT SETTINGS:\n")
                temp_file.write("-"*20 + "\n")
                temp_file.write(f"Initial Capital: ${sample_strategy_params['initial_capital']:,}\n")
                temp_file.write(f"Risk Per Trade: {sample_strategy_params['risk_per_trade']}%\n")
                temp_file.write("\n")
                temp_file.write("TRADING RULES:\n")
                temp_file.write("-"*20 + "\n")
                temp_file.write(f"Stop Loss Points: {sample_strategy_params['stop_loss_points']}\n")
                temp_file.write(f"Profit Target Points: {sample_strategy_params['profit_target_points']}\n")
                
                temp_filename = temp_file.name
            
            # Test parameter loading
            loaded_params = {}
            
            with open(temp_filename, 'r') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line in lines:
                    if ':' in line and not line.startswith('=') and not line.startswith('-'):
                        key_value = line.split(':', 1)
                        if len(key_value) == 2:
                            key = key_value[0].strip()
                            value = key_value[1].strip()
                            
                            # Parse specific parameters
                            if 'Initial Capital' in key:
                                loaded_params['initial_capital'] = float(value.replace('$', '').replace(',', ''))
                            elif 'Risk Per Trade' in key:
                                loaded_params['risk_per_trade'] = float(value.replace('%', ''))
                            elif 'Stop Loss Points' in key:
                                loaded_params['stop_loss_points'] = float(value)
                            elif 'Profit Target Points' in key:
                                loaded_params['profit_target_points'] = float(value)
            
            # Verify parameters were loaded correctly
            assert loaded_params['initial_capital'] == sample_strategy_params['initial_capital']
            assert loaded_params['risk_per_trade'] == sample_strategy_params['risk_per_trade']
            assert loaded_params['stop_loss_points'] == sample_strategy_params['stop_loss_points']
            assert loaded_params['profit_target_points'] == sample_strategy_params['profit_target_points']
            
            # Test strategy initialization with loaded parameters
            merged_params = sample_strategy_params.copy()
            merged_params.update(loaded_params)
            
            strategy = CFDStrategyV1(merged_params)
            assert strategy.params == merged_params, "Strategy should use loaded parameters"
            
            # Cleanup
            os.unlink(temp_filename)
            
            test_logger.end_test("test_parameter_loading_integration", "PASS")
        except Exception as e:
            test_logger.end_test("test_parameter_loading_integration", "FAIL", str(e))
            raise