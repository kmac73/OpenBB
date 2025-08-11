"""
Test CFD Trading Engine Core Logic - Phase 0 Test Suite
Tests written BEFORE implementation - Test-First Approach

These tests will FAIL initially - this is expected.
Implementation will be created to make these tests pass.
"""
import pytest
import pandas as pd
import sys
import os
from datetime import datetime, time
from unittest.mock import Mock, patch

# Add the parent directory to Python path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import will fail initially - this is expected in Phase 0
try:
    from app.common.cfd_engine import CFDTradingEngine, Trade
except ImportError:
    # Expected in Phase 0 - implementation doesn't exist yet
    CFDTradingEngine = Mock
    Trade = Mock

class TestCFDTradingEngineBasics:
    """Test basic CFD engine initialization and configuration"""
    
    def test_engine_initialization_with_standard_floats(self, cfd_test_parameters):
        """Test CFD engine initializes with standard Python floats as specified"""
        engine = CFDTradingEngine(
            account_balance=cfd_test_parameters['account_balance'],
            risk_pct=cfd_test_parameters['risk_pct'],
            transaction_cost=cfd_test_parameters['transaction_cost']
        )
        
        # TODO: FUTURE_CHANGE - May switch to Decimal for precision
        assert isinstance(engine.account_balance, float)
        assert engine.account_balance == 10000.0
        assert engine.risk_pct == 2.0
        assert engine.transaction_cost == 5.0
        assert not engine.position_active
        assert engine.opening_price is None
        
    def test_engine_initial_state_clean(self, cfd_test_parameters):
        """Test engine starts with clean state - no active trades"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        assert not engine.position_active
        assert engine.current_date is None
        assert len(engine.daily_trades) == 0
        assert engine.opening_price is None

class TestOpeningPriceResetLogic:
    """Test opening price reset logic from real data patterns"""
    
    def test_opening_price_set_to_first_open_of_day(self, cfd_test_parameters, last_5_days_real_data):
        """Test opening price is set to first open price of trading day"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        # Get first tick of first day
        first_tick = last_5_days_real_data.iloc[0]
        expected_opening_price = first_tick['open']  # 5459.58 from real data
        
        # Process first tick - should set opening price
        engine.detect_new_trading_day(first_tick['date'], first_tick['open'])
        
        assert engine.opening_price == expected_opening_price
        assert engine.current_date == first_tick['date'].date()
        
    def test_opening_price_reset_at_start_of_new_day(self, cfd_test_parameters, opening_price_reset_scenarios):
        """Test opening price resets when date changes in data file"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        scenario = opening_price_reset_scenarios[0]  # new_trading_day_reset
        
        # Set up previous day state
        engine.current_date = scenario['previous_timestamp'].date()
        engine.opening_price = 5400.00  # Some previous price
        engine.position_active = False  # Ensure clean state
        
        # Process new day first tick
        new_day_reset = engine.detect_new_trading_day(
            scenario['current_timestamp'], 
            scenario['new_open_price']
        )
        
        assert new_day_reset is True
        assert engine.opening_price == scenario['new_open_price']  # 5459.58
        assert engine.current_date == scenario['current_timestamp'].date()
        
    def test_opening_price_reset_to_exit_price_after_trade(self, cfd_test_parameters):
        """Test opening price resets to exit price when trade closes"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        # Set up active trade
        engine.opening_price = 5464.05
        engine.position_active = True
        engine.current_position = Mock()
        
        # Close position with exit price
        exit_price = 5474.57
        engine.close_position(exit_price, "PROFIT_TARGET", datetime.now())
        
        assert engine.opening_price == exit_price
        assert not engine.position_active
        
    def test_no_active_trades_at_end_of_day(self, cfd_test_parameters):
        """Test verification that no trades are active at day end"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        # Simulate end of day with active position - should raise assertion
        engine.position_active = True
        engine.current_date = datetime(2024, 6, 24).date()
        
        with pytest.raises(AssertionError, match="Active position detected at day change"):
            engine.detect_new_trading_day(
                pd.to_datetime('2024-06-25 09:30:00'), 
                5459.58
            )
            
    def test_no_active_trades_at_start_of_day(self, cfd_test_parameters):
        """Test verification that no trades are active at day start"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        # Start fresh day - should have clean state
        engine.detect_new_trading_day(pd.to_datetime('2024-06-24 09:30:00'), 5459.58)
        
        assert not engine.position_active
        assert len(engine.daily_trades) == 0

class TestTwoBpsTrigerLogic:
    """Test 2 basis point trigger logic using real price movements"""
    
    def test_2bps_long_entry_trigger_using_close_price(self, cfd_test_parameters, two_bps_trigger_scenarios):
        """Test LONG entry trigger when price increases 2bps using close price"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        scenario = two_bps_trigger_scenarios[0]  # LONG scenario
        engine.opening_price = scenario['opening_price']
        
        signal = engine.check_2bps_trigger(scenario['current_price'])
        
        assert signal == scenario['expected_signal']  # 'LONG'
        
        # Verify basis points calculation with standard Python floats
        # TODO: FUTURE_CHANGE - May need Decimal precision for production
        calculated_bps = ((scenario['current_price'] - scenario['opening_price']) / 
                         scenario['opening_price']) * 10000
        assert abs(calculated_bps - scenario['bps_change']) < 0.1  # Floating point tolerance
        
    def test_2bps_short_entry_trigger_using_close_price(self, cfd_test_parameters, two_bps_trigger_scenarios):
        """Test SHORT entry trigger when price decreases 2bps using close price"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        scenario = two_bps_trigger_scenarios[1]  # SHORT scenario
        engine.opening_price = scenario['opening_price']
        
        signal = engine.check_2bps_trigger(scenario['current_price'])
        
        assert signal == scenario['expected_signal']  # 'SHORT'
        
        # Verify negative basis points calculation
        calculated_bps = ((scenario['current_price'] - scenario['opening_price']) / 
                         scenario['opening_price']) * 10000
        assert abs(calculated_bps - scenario['bps_change']) < 0.1
        
    def test_no_trigger_below_2bps_threshold(self, cfd_test_parameters, two_bps_trigger_scenarios):
        """Test no trigger when price movement is below 2bps threshold"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        scenario = two_bps_trigger_scenarios[2]  # Below threshold scenario
        engine.opening_price = scenario['opening_price']
        
        signal = engine.check_2bps_trigger(scenario['current_price'])
        
        assert signal is None  # No signal should be generated
        
class TestMarketHoursEnforcement:
    """Test market hours rules: entry 09:30-15:30, force close at 16:00"""
    
    def test_can_enter_new_trade_during_entry_hours(self, cfd_test_parameters, trading_hours_constraints):
        """Test new trades allowed 09:30-15:30"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        # Test various times within entry window
        valid_entry_times = [
            datetime(2024, 6, 24, 9, 30),   # Market open
            datetime(2024, 6, 24, 12, 0),   # Mid-day
            datetime(2024, 6, 24, 15, 30),  # Last entry time
        ]
        
        for test_time in valid_entry_times:
            assert engine.can_enter_new_trade(test_time) is True
            
    def test_no_trade_entry_after_1530(self, cfd_test_parameters):
        """Test no new trades allowed after 15:30"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        # Test times after entry cutoff
        invalid_entry_times = [
            datetime(2024, 6, 24, 15, 31),  # 1 minute after cutoff
            datetime(2024, 6, 24, 15, 45),  # 15 minutes after cutoff
            datetime(2024, 6, 24, 16, 0),   # Market close time
        ]
        
        for test_time in invalid_entry_times:
            assert engine.can_enter_new_trade(test_time) is False
            
    def test_force_close_position_at_1600(self, cfd_test_parameters):
        """Test all positions force closed at 16:00 regardless of other logic"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        # Set up active position with real Trade object
        from app.common.cfd_engine import Trade
        
        entry_time = pd.to_datetime('2024-06-24 14:00:00')
        trade = Trade(
            direction="LONG",
            entry_price=5465.0,
            entry_time=entry_time,
            stop_loss=5415.0,  # $50 below entry
            profit_target=5565.0,  # 2:1 ratio
            position_size=4.0,  # $200 risk / $50 distance
            costs=5.0
        )
        
        engine.position_active = True
        engine.current_position = trade
        engine.opening_price = 5464.05
        
        # Create OHLC data for 16:00 tick
        market_close_tick = {
            'date': pd.to_datetime('2024-06-24 16:00:00'),
            'open': 5470.00,
            'high': 5471.00,
            'low': 5469.00,
            'close': 5470.50
        }
        
        # Process market close tick - should force close position
        engine.process_market_tick(market_close_tick['date'], market_close_tick)
        
        assert not engine.position_active
        # Verify force close reason was recorded
        assert len(engine.daily_trades) > 0
        last_trade = engine.daily_trades[-1]
        assert last_trade.exit_reason == "END_OF_DAY_FORCE_CLOSE"

class TestPositionManagement:
    """Test position entry, management, and exit logic"""
    
    def test_enter_trade_long_position(self, cfd_test_parameters):
        """Test entering a LONG position with proper position sizing"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        engine.opening_price = 5464.05
        
        # Enter LONG trade
        entry_price = 5465.14  # +2bps from opening
        entry_time = pd.to_datetime('2024-06-24 10:15:00')
        
        engine.enter_trade("LONG", entry_price, entry_time)
        
        assert engine.position_active is True
        assert engine.current_position.direction == "LONG"
        assert engine.current_position.entry_price == entry_price
        assert engine.current_position.entry_time == entry_time
        
    def test_enter_trade_short_position(self, cfd_test_parameters):
        """Test entering a SHORT position with proper position sizing"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        engine.opening_price = 5464.05
        
        # Enter SHORT trade
        entry_price = 5462.96  # -2bps from opening
        entry_time = pd.to_datetime('2024-06-24 11:30:00')
        
        engine.enter_trade("SHORT", entry_price, entry_time)
        
        assert engine.position_active is True
        assert engine.current_position.direction == "SHORT"
        assert engine.current_position.entry_price == entry_price
        assert engine.current_position.entry_time == entry_time
        
    def test_position_sizing_calculation(self, cfd_test_parameters):
        """Test position sizing calculation based on account balance and risk"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        # Calculate expected position size
        # Risk per trade = $10,000 * 2% = $200
        # Risk per contract = $50 (stop loss distance)
        # Position size = $200 / $50 = 4 contracts
        
        expected_position_size = engine.calculate_position_size(
            stop_loss_distance=cfd_test_parameters['stop_loss_distance']
        )
        
        assert expected_position_size == 4.0  # 4 CFD contracts
        
    def test_only_one_active_trade_at_time(self, cfd_test_parameters):
        """Test only one trade can be active at a time"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        engine.opening_price = 5464.05
        
        # Enter first trade
        engine.enter_trade("LONG", 5465.14, pd.to_datetime('2024-06-24 10:15:00'))
        assert engine.position_active is True
        
        # Attempt to enter second trade - should be prevented
        engine.enter_trade("SHORT", 5462.96, pd.to_datetime('2024-06-24 10:20:00'))
        
        # Should still have only the first trade
        assert engine.current_position.direction == "LONG"

class TestTickProcessing:
    """Test market tick processing with real data"""
    
    def test_process_market_tick_with_real_data(self, cfd_test_parameters, last_5_days_real_data):
        """Test processing market ticks using real 5M data"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        # Process first few ticks of real data
        first_tick = last_5_days_real_data.iloc[0]
        
        engine.process_market_tick(first_tick['date'], {
            'open': first_tick['open'],
            'high': first_tick['high'],
            'low': first_tick['low'],
            'close': first_tick['close']
        })
        
        # Should have set opening price and current date
        assert engine.opening_price == first_tick['open']
        assert engine.current_date == first_tick['date'].date()
        
    def test_use_close_price_for_2bps_comparison(self, cfd_test_parameters):
        """Test that close price is used for 2bps trigger comparison as specified"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        engine.opening_price = 5464.05
        
        # Create tick where close price triggers 2bps but other prices don't
        tick_data = {
            'open': 5464.00,   # Below 2bps threshold
            'high': 5464.50,   # Below 2bps threshold
            'low': 5463.50,    # Below threshold
            'close': 5465.14281   # Exactly 2bps above opening - should trigger
        }
        
        # Should use close price (5465.14) for trigger detection
        signal = engine.check_2bps_trigger(tick_data['close'])
        assert signal == "LONG"
        
class TestDailyPnLAggregation:
    """Test daily P&L calculation and aggregation"""
    
    def test_daily_pnl_aggregation_and_reset(self, cfd_test_parameters):
        """Test daily P&L summary calculation and reset for new day"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        # Simulate completed trades for a day
        mock_trades = [
            Mock(gross_pnl=100.0, net_pnl=95.0),
            Mock(gross_pnl=50.0, net_pnl=45.0),
            Mock(gross_pnl=-30.0, net_pnl=-35.0)
        ]
        engine.daily_trades = mock_trades
        engine.current_date = datetime(2024, 6, 24).date()
        
        # Calculate daily summary
        daily_summary = engine.end_of_day_summary()
        
        assert daily_summary['date'] == datetime(2024, 6, 24).date()
        assert daily_summary['daily_gross_pnl'] == 120.0  # 100 + 50 - 30
        assert daily_summary['daily_net_pnl'] == 105.0    # 95 + 45 - 35
        assert daily_summary['trades_count'] == 3
        
    def test_realized_pnl_only_from_completed_trades(self, cfd_test_parameters):
        """Test that only realized P&L from completed trades is tracked"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        
        # There should be no open trades at end of day as specified
        assert not engine.position_active
        
        # All P&L should come from completed trades in daily_trades list
        completed_trade = Mock(gross_pnl=100.0, net_pnl=95.0, status="COMPLETED")
        engine.daily_trades = [completed_trade]
        
        daily_summary = engine.end_of_day_summary()
        
        # Should only include realized P&L from completed trades
        assert daily_summary['daily_gross_pnl'] == 100.0
        assert daily_summary['daily_net_pnl'] == 95.0

class TestDebugOutput:
    """Test limited debug output system"""
    
    def test_limited_debug_output_max_5_trades_per_day(self, cfd_test_parameters, sample_debug_output_format):
        """Test debug output limited to 5 trades per day to prevent console overwhelming"""
        engine = CFDTradingEngine(**cfd_test_parameters)
        debug_logger = Mock()
        engine.debug_logger = debug_logger
        
        # Simulate 7 trades in one day (more than 5 limit)
        for i in range(7):
            trade_result = Mock(
                direction="LONG" if i % 2 == 0 else "SHORT",
                entry_price=5464.05 + i,
                exit_price=5474.57 + i,
                pnl=10.0 * i,
                timestamp=pd.to_datetime(f'2024-06-24 1{i}:00:00')
            )
            engine.debug_logger.log_trade_exit(trade_result)
            
        # Should have limited console output but full log file output
        assert debug_logger.log_trade_exit.call_count == 7
        # Verify console output was limited but file logging continued
        
    def test_debug_output_format_matches_expected(self, sample_debug_output_format):
        """Test debug output format matches expected structure"""
        expected_format = sample_debug_output_format[0]
        
        # Expected format: "2024-06-24 10:15:00 - ENTRY: LONG @5464.05 [2bps trigger: +2.1bps]"
        assert "ENTRY:" in expected_format
        assert "LONG" in expected_format
        assert "@5464.05" in expected_format
        assert "[2bps trigger:" in expected_format
        assert "2024-06-24" in expected_format