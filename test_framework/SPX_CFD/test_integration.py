"""
Integration Tests - End-to-End Backtest Execution - Phase 0 Test Suite
Tests written BEFORE implementation - Test-First Approach

These tests validate the complete workflow from data input to results generation
using real market data from the last 5 days.
"""
import pytest
import pandas as pd
import json
from datetime import datetime, time
from pathlib import Path
from unittest.mock import Mock, patch
import sys

# Add app directory for imports when implementation is created
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app"))

# Imports will fail initially - this is expected in Phase 0
try:
    from common.cfd_engine import CFDTradingEngine
    from common.backtest_analyzer import BacktestAnalyzer
    from common.pdf_generator import SPXBacktestPDFGenerator
    from common.debug_logger import LimitedDebugLogger
    from common.error_handler import JupyterStyleErrorHandler
    from common.performance_timer import PerformanceTimer
except ImportError:
    # Expected in Phase 0 - implementation doesn't exist yet
    CFDTradingEngine = Mock
    BacktestAnalyzer = Mock
    SPXBacktestPDFGenerator = Mock
    LimitedDebugLogger = Mock
    JupyterStyleErrorHandler = Mock
    PerformanceTimer = Mock

class TestEndToEndBacktestExecution:
    """Test complete backtest execution with real data"""
    
    def test_full_5_day_backtest_execution(self, last_5_days_real_data, cfd_test_parameters, expected_manual_calculations):
        """Test complete 5-day backtest execution with real market data"""
        # Initialize components
        engine = CFDTradingEngine(**cfd_test_parameters)
        analyzer = BacktestAnalyzer(risk_free_rate=cfd_test_parameters['risk_free_rate'] / 100)
        timer = PerformanceTimer()
        
        # Start performance timing
        timer.start_backtest()
        
        # Execute backtest with real data
        all_trades = []
        daily_summaries = []
        equity_curve = [cfd_test_parameters['account_balance']]
        
        for idx, row in last_5_days_real_data.iterrows():
            # Process each market tick
            engine.process_market_tick(row['date'], {
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close']
            })
            
            # Collect completed trades
            if hasattr(engine, 'daily_trades'):
                for trade in engine.daily_trades:
                    if trade not in all_trades:
                        all_trades.append(trade)
                        
            # Update equity curve
            if all_trades:
                current_equity = cfd_test_parameters['account_balance'] + sum(t.net_pnl for t in all_trades)
                equity_curve.append(current_equity)
                
            # End of day processing
            if row['date'].time() >= time(16, 0):  # Market close
                daily_summary = engine.end_of_day_summary()
                if daily_summary:
                    daily_summaries.append(daily_summary)
        
        # End performance timing
        performance_report = timer.end_backtest()
        
        # Calculate final metrics
        final_metrics = analyzer.calculate_all_metrics(all_trades, daily_summaries, equity_curve)
        
        # Validate results
        assert isinstance(final_metrics, dict)
        assert 'total_trades' in final_metrics
        assert 'win_rate' in final_metrics
        assert 'total_pnl' in final_metrics
        
        # Validate against manual calculations (when available)
        if expected_manual_calculations['expected_total_trades'] > 0:
            # TODO: Add specific validation against hand-calculated values
            # This will be populated during Phase 0 manual calculation process
            pass
            
        # Validate performance
        assert performance_report['total_processing_time_seconds'] < 10  # Should complete in under 10 seconds
        
    def test_opening_price_reset_across_multiple_days(self, last_5_days_real_data, cfd_test_parameters):
        """Test opening price reset logic across 5 trading days"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        opening_prices_by_day = {}
        current_date = None
        
        for idx, row in last_5_days_real_data.iterrows():
            row_date = row['date'].date()
            
            # Detect new trading day
            if current_date is None or row_date != current_date:
                # Should be first tick of new day (9:30 AM)
                if row['date'].time() == time(9, 30):
                    current_date = row_date
                    opening_prices_by_day[row_date] = row['open']
                    
                    # Process new day detection
                    engine.detect_new_trading_day(row['date'], row['open'])
                    
                    # Verify opening price was set
                    assert engine.opening_price == row['open']
                    assert engine.current_date == row_date
                    
        # Should have detected 5 trading days
        assert len(opening_prices_by_day) == 5
        
        # Verify each day's opening price
        expected_dates = [
            datetime(2024, 6, 24).date(),
            datetime(2024, 6, 25).date(), 
            datetime(2024, 6, 26).date(),
            datetime(2024, 6, 27).date(),
            datetime(2024, 6, 28).date()
        ]
        
        for expected_date in expected_dates:
            assert expected_date in opening_prices_by_day
            
    def test_2bps_trigger_detection_with_real_price_movements(self, last_5_days_real_data, cfd_test_parameters):
        """Test 2bps trigger detection using real price movements"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        trigger_events = []
        
        # Process first day to establish opening price
        first_day_data = last_5_days_real_data[
            last_5_days_real_data['date'].dt.date == datetime(2024, 6, 24).date()
        ].sort_values('date')
        
        # Set opening price from first tick
        first_tick = first_day_data.iloc[0]
        engine.opening_price = first_tick['open']
        
        # Check each subsequent tick for trigger events
        for idx, row in first_day_data.iterrows():
            signal = engine.check_2bps_trigger(row['close'])
            
            if signal:
                # Calculate actual basis points for validation
                bps_change = ((row['close'] - engine.opening_price) / engine.opening_price) * 10000
                
                trigger_events.append({
                    'timestamp': row['date'],
                    'signal': signal,
                    'price': row['close'],
                    'opening_price': engine.opening_price,
                    'bps_change': bps_change
                })
                
        # Should have found some trigger events with real data movement
        assert len(trigger_events) > 0, "No 2bps triggers found in real data"
        
        # Validate trigger events
        for event in trigger_events:
            if event['signal'] == 'LONG':
                assert event['bps_change'] >= 2.0
            elif event['signal'] == 'SHORT':
                assert event['bps_change'] <= -2.0
                
    def test_market_hours_enforcement_integration(self, last_5_days_real_data, cfd_test_parameters):
        """Test market hours enforcement across complete dataset"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        entry_attempts = []
        force_closures = []
        
        for idx, row in last_5_days_real_data.iterrows():
            current_time = row['date'].time()
            
            # Test entry window enforcement
            can_enter = engine.can_enter_new_trade(row['date'])
            entry_attempts.append({
                'timestamp': row['date'],
                'time': current_time,
                'can_enter': can_enter
            })
            
            # Test force closure at 4:00 PM
            if current_time == time(16, 0):
                # Simulate active position for force closure test
                engine.position_active = True
                engine.current_position = Mock()
                
                # Should force close position
                engine.process_market_tick(row['date'], {
                    'open': row['open'],
                    'high': row['high'], 
                    'low': row['low'],
                    'close': row['close']
                })
                
                # Verify position was closed
                assert not engine.position_active
                force_closures.append(row['date'])
                
        # Validate entry window enforcement
        for attempt in entry_attempts:
            expected_can_enter = time(9, 30) <= attempt['time'] <= time(15, 30)
            assert attempt['can_enter'] == expected_can_enter, f"Entry enforcement failed at {attempt['timestamp']}"
            
        # Should have 5 force closures (one per trading day)
        assert len(force_closures) == 5

class TestRealDataProcessingWorkflow:
    """Test real data processing workflow and edge cases"""
    
    def test_complete_data_processing_pipeline(self, last_5_days_real_data, cfd_test_parameters):
        """Test complete data processing pipeline with error handling"""
        error_handler = JupyterStyleErrorHandler()
        debug_logger = LimitedDebugLogger(enabled=True, max_daily_trades=5)
        
        try:
            # Initialize engine with debug capabilities
            engine = CFDTradingEngine(**cfd_test_parameters)
            engine.debug_logger = debug_logger
            engine.error_handler = error_handler
            
            processed_ticks = 0
            errors_encountered = []
            
            # Process all ticks with error tracking
            for idx, row in last_5_days_real_data.iterrows():
                try:
                    # Log debug information
                    error_handler.log_debug_line(f"Processing tick {idx}: {row['date']}")
                    
                    # Process tick
                    engine.process_market_tick(row['date'], {
                        'open': row['open'],
                        'high': row['high'],
                        'low': row['low'],
                        'close': row['close']
                    })
                    
                    processed_ticks += 1
                    
                except Exception as e:
                    errors_encountered.append({
                        'tick_index': idx,
                        'timestamp': row['date'],
                        'error': str(e)
                    })
                    
            # Validate processing completed
            assert processed_ticks > 0
            assert processed_ticks == len(last_5_days_real_data)
            
            # Should have minimal or no errors with clean data
            error_rate = len(errors_encountered) / processed_ticks
            assert error_rate < 0.01, f"Too many processing errors: {error_rate:.2%}"
            
        except Exception as e:
            # Test graceful failure handling
            error_handler.handle_graceful_failure(e, streamlit_context=False)
            pytest.fail(f"Data processing pipeline failed: {e}")
            
    def test_daily_pnl_aggregation_across_5_days(self, last_5_days_real_data, cfd_test_parameters):
        """Test daily P&L aggregation across all 5 trading days"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        analyzer = BacktestAnalyzer()
        
        daily_summaries = []
        
        # Group data by trading day
        for date_group, day_data in last_5_days_real_data.groupby(last_5_days_real_data['date'].dt.date):
            day_data = day_data.sort_values('date')
            
            # Reset for new day
            engine.detect_new_trading_day(day_data.iloc[0]['date'], day_data.iloc[0]['open'])
            
            # Process day's data
            for idx, row in day_data.iterrows():
                engine.process_market_tick(row['date'], {
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close']
                })
                
            # End of day summary
            daily_summary = engine.end_of_day_summary()
            if daily_summary:
                daily_summaries.append(daily_summary)
                
        # Should have 5 daily summaries
        assert len(daily_summaries) == 5
        
        # Validate daily summary structure
        for summary in daily_summaries:
            assert 'date' in summary
            assert 'daily_gross_pnl' in summary
            assert 'daily_net_pnl' in summary
            assert 'trades_count' in summary
            
        # Validate that each day has reasonable trade activity
        total_trades_across_days = sum(s['trades_count'] for s in daily_summaries)
        assert total_trades_across_days >= 5, "Expected at least 1 trade per day on average"
        assert total_trades_across_days <= 25, "Expected no more than 5 trades per day on average"
        
    def test_equity_curve_generation(self, last_5_days_real_data, cfd_test_parameters):
        """Test equity curve generation throughout backtest"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        starting_balance = cfd_test_parameters['account_balance']
        equity_curve = [starting_balance]
        equity_timestamps = [last_5_days_real_data.iloc[0]['date']]
        
        cumulative_pnl = 0
        completed_trades = []
        
        # Process data and track equity changes
        for idx, row in last_5_days_real_data.iterrows():
            engine.process_market_tick(row['date'], {
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close']
            })
            
            # Check for completed trades
            if hasattr(engine, 'daily_trades'):
                for trade in engine.daily_trades:
                    if trade not in completed_trades:
                        completed_trades.append(trade)
                        cumulative_pnl += trade.net_pnl
                        
                        # Update equity curve
                        current_equity = starting_balance + cumulative_pnl
                        equity_curve.append(current_equity)
                        equity_timestamps.append(row['date'])
                        
        # Validate equity curve
        assert len(equity_curve) > 1, "Equity curve should show changes from trades"
        assert equity_curve[0] == starting_balance, "Should start with initial balance"
        
        # Final equity should reflect cumulative P&L
        final_equity = equity_curve[-1]
        expected_final = starting_balance + cumulative_pnl
        assert abs(final_equity - expected_final) < 0.01, f"Equity mismatch: {final_equity} != {expected_final}"

class TestPerformanceAndScalability:
    """Test performance with real data volume"""
    
    def test_processing_speed_with_400_data_points(self, last_5_days_real_data, performance_timing_baseline):
        """Test processing speed with 400 real data points"""
        import time
        
        engine = CFDTradingEngine(
            account_balance=10000,
            risk_pct=2.0,
            transaction_cost=5.0
        )
        
        start_time = time.time()
        
        # Process all 400 data points
        for idx, row in last_5_days_real_data.iterrows():
            engine.process_market_tick(row['date'], {
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close']
            })
            
        end_time = time.time()
        total_time = end_time - start_time
        
        # Validate performance expectations
        max_time = performance_timing_baseline['max_acceptable_time_seconds']
        assert total_time < max_time, f"Processing too slow: {total_time:.2f}s > {max_time}s"
        
        # Calculate processing rate
        data_points = len(last_5_days_real_data)
        processing_rate = data_points / total_time
        
        # Should process at reasonable rate (ticks per second)
        assert processing_rate > 50, f"Processing rate too slow: {processing_rate:.1f} ticks/sec"
        
    def test_memory_usage_scalability(self, last_5_days_real_data, performance_timing_baseline):
        """Test memory usage with real data processing"""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory_mb = process.memory_info().rss / 1024 / 1024
        
        # Process data
        engine = CFDTradingEngine(account_balance=10000, risk_pct=2.0, transaction_cost=5.0)
        analyzer = BacktestAnalyzer()
        
        all_trades = []
        daily_summaries = []
        equity_curve = []
        
        for idx, row in last_5_days_real_data.iterrows():
            engine.process_market_tick(row['date'], {
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close']
            })
            
            # Simulate trade and equity tracking
            if hasattr(engine, 'daily_trades') and engine.daily_trades:
                all_trades.extend(engine.daily_trades)
                equity_curve.append(10000 + sum(t.net_pnl for t in all_trades if hasattr(t, 'net_pnl')))
                
        # Calculate final metrics
        if all_trades and equity_curve:
            final_metrics = analyzer.calculate_all_metrics(all_trades, daily_summaries, equity_curve)
            
        # Get final memory usage
        final_memory_mb = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory_mb - initial_memory_mb
        
        # Validate memory usage
        max_memory_increase = performance_timing_baseline['memory_limit_mb']
        assert memory_increase < max_memory_increase, f"Memory usage too high: {memory_increase:.1f}MB increase"

class TestErrorHandlingIntegration:
    """Test error handling in integrated environment"""
    
    def test_graceful_failure_with_jupyter_style_output(self):
        """Test graceful failure handling with Jupyter-style error display"""
        error_handler = JupyterStyleErrorHandler()
        
        # Simulate some debug operations
        debug_operations = [
            "Initializing CFD engine with account balance: $10,000",
            "Loading historical data: 2024-06-24 to 2024-06-28",
            "Processing tick: 2024-06-24 09:30:00",
            "Checking 2bps trigger: current=5464.05, opening=5459.58",
            "ERROR: Division by zero in position sizing calculation"
        ]
        
        for operation in debug_operations[:-1]:
            error_handler.log_debug_line(operation)
            
        # Simulate error
        try:
            raise ValueError("Division by zero in position sizing calculation")
        except Exception as e:
            error_context = error_handler.handle_graceful_failure(e, streamlit_context=False)
            
        # Verify error handling structure
        assert len(error_handler.debug_log_lines) >= 4
        
        # Should contain context from recent operations
        recent_lines = error_handler.debug_log_lines[-4:]
        assert any("Processing tick" in line for line in recent_lines)
        assert any("Checking 2bps trigger" in line for line in recent_lines)
        
    def test_invalid_trade_conditions_handling(self, cfd_test_parameters):
        """Test handling of invalid trade conditions"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        error_handler = JupyterStyleErrorHandler()
        engine.error_handler = error_handler
        
        # Test various invalid conditions
        invalid_conditions = [
            {
                'description': 'Negative position size',
                'test': lambda: engine.calculate_position_size(-50.0),  # Negative stop loss
            },
            {
                'description': 'Entry after market close', 
                'test': lambda: engine.can_enter_new_trade(pd.to_datetime('2024-06-24 16:30:00')),
            },
            {
                'description': 'Active trade at day change',
                'test': lambda: self._test_active_trade_day_change(engine),
            }
        ]
        
        error_count = 0
        
        for condition in invalid_conditions:
            try:
                condition['test']()
            except (AssertionError, ValueError, TypeError) as e:
                error_count += 1
                error_handler.log_debug_line(f"Invalid condition detected: {condition['description']}")
                
        # Should have caught multiple invalid conditions
        assert error_count > 0, "Should have detected invalid trade conditions"
        
    def _test_active_trade_day_change(self, engine):
        """Helper method to test active trade at day change"""
        engine.position_active = True
        engine.current_date = datetime(2024, 6, 24).date()
        
        # This should raise AssertionError
        engine.detect_new_trading_day(
            pd.to_datetime('2024-06-25 09:30:00'), 
            5459.58
        )

class TestManualCalculationValidation:
    """Test framework for validating against manual calculations"""
    
    def test_manual_calculation_framework_setup(self, expected_manual_calculations):
        """Test that manual calculation framework is properly set up"""
        # Verify expected calculation structure exists
        required_fields = [
            'expected_total_trades',
            'expected_winning_trades', 
            'expected_losing_trades',
            'expected_total_long_trades',
            'expected_total_short_trades',
            'expected_win_rate',
            'expected_total_pnl',
            'expected_gross_pnl',
            'expected_total_costs',
            'expected_max_drawdown',
            'expected_sharpe_ratio',
            'expected_value_at_risk'
        ]
        
        for field in required_fields:
            assert field in expected_manual_calculations, f"Missing expected field: {field}"
            
        # Verify placeholder structure
        assert 'note' in expected_manual_calculations
        assert 'manually calculated' in expected_manual_calculations['note']
        
    def test_placeholder_for_manual_validation(self, last_5_days_real_data, expected_manual_calculations):
        """Placeholder test for manual validation - to be completed during Phase 0"""
        # TODO: This test will be completed with actual manual calculations
        # during Phase 0 test creation process
        
        # For now, document the validation approach:
        validation_approach = {
            'step_1': 'Manually analyze first day of real data (2024-06-24)',
            'step_2': 'Hand-calculate expected trades based on 2bps trigger logic',
            'step_3': 'Calculate expected P&L, win rate, and other metrics',
            'step_4': 'Compare automated results against manual calculations',
            'step_5': 'Ensure tolerance levels account for floating-point precision'
        }
        
        # Verify approach is documented
        for step, description in validation_approach.items():
            assert isinstance(description, str)
            assert len(description) > 10
            
        # Actual validation will be implemented once manual calculations are complete
        # Example structure:
        # if expected_manual_calculations['expected_total_trades'] > 0:
        #     automated_results = run_full_backtest(last_5_days_real_data)
        #     assert abs(automated_results['total_trades'] - expected_manual_calculations['expected_total_trades']) == 0
        
    def test_real_data_analysis_preparation(self, last_5_days_real_data):
        """Prepare data analysis for manual calculations"""
        # Extract key information needed for manual calculations
        analysis_data = {
            'total_data_points': len(last_5_days_real_data),
            'trading_days': last_5_days_real_data['date'].dt.date.nunique(),
            'date_range': {
                'start': last_5_days_real_data['date'].min(),
                'end': last_5_days_real_data['date'].max()
            },
            'price_ranges': {
                'min_price': last_5_days_real_data['close'].min(),
                'max_price': last_5_days_real_data['close'].max(),
                'price_volatility': last_5_days_real_data['close'].std()
            },
            'daily_opening_prices': {}
        }
        
        # Extract opening prices for each day
        for date_group, day_data in last_5_days_real_data.groupby(last_5_days_real_data['date'].dt.date):
            first_tick = day_data.sort_values('date').iloc[0]
            analysis_data['daily_opening_prices'][str(date_group)] = first_tick['open']
            
        # Save analysis data for manual calculation reference
        analysis_file = Path(__file__).parent / "expected_results" / "real_data_analysis.json"
        analysis_file.parent.mkdir(exist_ok=True)
        
        with open(analysis_file, 'w') as f:
            json.dump(analysis_data, f, indent=2, default=str)
            
        # Validate analysis data structure
        assert analysis_data['trading_days'] == 5
        assert analysis_data['total_data_points'] == 400
        assert len(analysis_data['daily_opening_prices']) == 5