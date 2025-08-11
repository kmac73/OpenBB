"""
Test fixtures for SPX CFD Backtest - Phase 0 Test Suite
Uses REAL market data only - no fake data allowed
"""
import pytest
import pandas as pd
import json
from datetime import datetime, time
from pathlib import Path
import sys

# Add app directory to path for imports when implementation is created
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app"))

@pytest.fixture
def last_5_days_real_data():
    """
    Load actual last 5 days from 5M.txt for comprehensive testing
    Dates: 2024-06-24 through 2024-06-28 (5 complete trading days)
    NO FAKE DATA - Real market data only
    """
    data_file = Path(__file__).parent / "last_5_days_real_data.txt"
    
    data = []
    with open(data_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(',')
                data.append({
                    'date': pd.to_datetime(parts[0]),
                    'open': float(parts[1]),
                    'high': float(parts[2]),
                    'low': float(parts[3]),
                    'close': float(parts[4])
                })
    
    return pd.DataFrame(data)

@pytest.fixture  
def expected_manual_calculations():
    """
    Hand-calculated expected results for last 5 days scenario
    These will be populated during Phase 0 test creation
    TODO: Manual calculation of expected trades, P&L, metrics
    """
    # This will be populated with hand-calculated values
    # NO SYNTHETIC DATA - these must be manually calculated
    expected_file = Path(__file__).parent / "expected_results" / "last_5_days_metrics.json"
    
    if expected_file.exists():
        with open(expected_file, 'r') as f:
            return json.load(f)
    else:
        # Placeholder structure for initial test creation
        return {
            'expected_trades': [],  # To be calculated manually
            'expected_total_trades': 0,  # To be calculated manually
            'expected_winning_trades': 0,  # To be calculated manually
            'expected_losing_trades': 0,  # To be calculated manually
            'expected_total_long_trades': 0,  # To be calculated manually
            'expected_total_short_trades': 0,  # To be calculated manually
            'expected_win_rate': 0.0,  # To be calculated manually
            'expected_total_pnl': 0.0,  # To be calculated manually
            'expected_gross_pnl': 0.0,  # To be calculated manually
            'expected_total_costs': 0.0,  # To be calculated manually
            'expected_avg_win': 0.0,  # To be calculated manually
            'expected_avg_loss': 0.0,  # To be calculated manually
            'expected_max_drawdown': 0.0,  # To be calculated manually
            'expected_avg_drawdown': 0.0,  # To be calculated manually
            'expected_total_return': 0.0,  # To be calculated manually
            'expected_final_equity': 10000.0,  # Starting equity
            'expected_profit_factor': 0.0,  # To be calculated manually
            'expected_cost_ratio': 0.0,  # To be calculated manually
            'expected_shortest_trade_minutes': 0,  # To be calculated manually
            'expected_longest_trade_minutes': 0,  # To be calculated manually
            'expected_avg_trade_duration_minutes': 0,  # To be calculated manually
            'expected_sharpe_ratio': 0.0,  # To be calculated manually
            'expected_value_at_risk': 0.0,  # To be calculated manually
            'note': 'These values must be manually calculated from real data analysis'
        }

@pytest.fixture
def cfd_test_parameters():
    """Standard CFD configuration for testing - based on CFD_Calculator.html defaults"""
    return {
        'account_balance': 10000.0,  # $10,000 starting balance
        'risk_pct': 2.0,  # 2% account risk per trade
        'transaction_cost': 5.0,  # $5 round-trip cost per CFD
        'stop_loss_distance': 50.0,  # $50 stop-loss distance
        'risk_reward_ratio': 2.0,  # 2:1 risk/reward ratio
        'trailing_stop_pct': 2.0,  # 2% trailing stop
        'margin_rate': 5.0,  # 5% margin rate
        'risk_free_rate': 3.0,  # 3% risk-free rate for Sharpe
        'frequency': '5M',  # 5-minute data frequency
        'start_date': '2024-06-24',  # Test period start
        'end_date': '2024-06-28'  # Test period end
    }

@pytest.fixture
def trading_hours_constraints():
    """Trading hours rules for testing"""
    return {
        'market_open': time(9, 30),  # 09:30 market open
        'entry_cutoff': time(15, 30),  # 15:30 last entry time
        'force_close': time(16, 0),  # 16:00 force close time
        'market_close_data': time(16, 5)  # Data may continue to 16:05
    }

@pytest.fixture
def sample_debug_output_format():
    """
    Expected debug output format for validation
    Max 5 trades/day expected, console output limited
    """
    return [
        "2024-06-24 10:15:00 - ENTRY: LONG @5464.05 [2bps trigger: +2.1bps]",
        "2024-06-24 10:45:00 - EXIT: LONG 5464.05->5474.57, P&L: +$105.20 [PROFIT_TARGET]",
        "2024-06-24 11:30:00 - ENTRY: SHORT @5474.57 [2bps trigger: -2.0bps]", 
        "2024-06-24 14:20:00 - EXIT: SHORT 5474.57->5465.23, P&L: +$93.40 [TRAILING_STOP]",
        "2024-06-24 16:00:00 - DAY_CLOSE: 2 trades, Gross P&L: +$198.60, Net P&L: +$188.60",
        "... [Additional trades logged to file only]"  # When limit exceeded
    ]

@pytest.fixture  
def opening_price_reset_scenarios():
    """
    Test scenarios for opening price reset logic based on real data patterns
    """
    return [
        {
            'scenario': 'new_trading_day_reset',
            'previous_timestamp': pd.to_datetime('2024-06-24 16:05:00'),
            'current_timestamp': pd.to_datetime('2024-06-25 09:30:00'),
            'new_open_price': 5459.58,  # Real open price from data
            'expected_reset': True,
            'description': 'Opening price should reset to first open of new trading day'
        },
        {
            'scenario': 'trade_exit_reset',
            'exit_price': 5470.25,
            'expected_new_opening_price': 5470.25,
            'description': 'Opening price should reset to exit price after trade closure'
        }
    ]

@pytest.fixture
def two_bps_trigger_scenarios():
    """
    Test scenarios for 2bps trigger logic using real price movements
    """
    return [
        {
            'opening_price': 5464.05,  # Real opening price from data
            'current_price': 5465.14281,  # +2.0bps exactly
            'expected_signal': 'LONG',
            'bps_change': 2.0
        },
        {
            'opening_price': 5464.05,
            'current_price': 5462.95719,  # -2.0bps exactly  
            'expected_signal': 'SHORT',
            'bps_change': -2.0
        },
        {
            'opening_price': 5464.05,
            'current_price': 5465.05,  # +1.8bps - below threshold
            'expected_signal': None,
            'bps_change': 1.8
        }
    ]

@pytest.fixture
def performance_timing_baseline():
    """Baseline timing expectations for performance measurement"""
    return {
        'max_acceptable_time_seconds': 10,  # 10 seconds for 5 days of 5M data
        'expected_data_points': 400,  # Lines in our test data
        'expected_trades_range': (5, 25),  # Expected 5-25 trades over 5 days
        'memory_limit_mb': 100  # 100MB memory limit for test
    }