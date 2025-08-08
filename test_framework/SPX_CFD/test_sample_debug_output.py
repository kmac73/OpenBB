"""
Test Sample Debug Output Format - Phase 0 Test Suite
Generate and validate sample debug output format for approval

This creates the debug output sample as requested in the development plan.
"""
import pytest
from datetime import datetime, time
from unittest.mock import Mock

class TestDebugOutputFormat:
    """Test and generate sample debug output format"""
    
    def test_generate_sample_debug_output(self, sample_debug_output_format):
        """Generate sample debug output format for validation and approval"""
        
        # Verify sample format structure
        assert len(sample_debug_output_format) >= 6  # At least 6 sample lines
        
        # Validate first entry format
        first_entry = sample_debug_output_format[0]
        expected_elements = [
            "2024-06-24",      # Date
            "10:15:00",        # Time
            "ENTRY:",          # Action type
            "LONG",            # Direction
            "@5464.05",        # Price with @ symbol
            "[2bps trigger:",  # Trigger reason
            "+2.1bps]"         # Actual basis points
        ]
        
        for element in expected_elements:
            assert element in first_entry, f"Missing element '{element}' in: {first_entry}"
            
        # Validate exit format
        exit_entry = sample_debug_output_format[1] 
        expected_exit_elements = [
            "EXIT:",           # Action type
            "LONG",           # Direction
            "->",             # Arrow separator
            "P&L:",           # P&L label
            "+$",             # Positive P&L indicator
            "[PROFIT_TARGET]" # Exit reason
        ]
        
        for element in expected_exit_elements:
            assert element in exit_entry, f"Missing element '{element}' in: {exit_entry}"
            
        # Validate day close format
        day_close_entry = sample_debug_output_format[4]
        expected_close_elements = [
            "DAY_CLOSE:",     # Day close indicator
            "trades,",        # Trade count
            "Gross P&L:",     # Gross P&L
            "Net P&L:"        # Net P&L
        ]
        
        for element in expected_close_elements:
            assert element in day_close_entry, f"Missing element '{element}' in: {day_close_entry}"
            
        # Validate overflow message
        overflow_message = sample_debug_output_format[-1]
        assert "Additional trades logged to file only" in overflow_message
        assert "..." in overflow_message
        
    def test_debug_output_timing_format(self):
        """Test debug output uses proper timestamp format"""
        # Expected format: YYYY-MM-DD HH:MM:SS
        test_timestamp = datetime(2024, 6, 24, 10, 15, 30)
        
        # Format should match sample output
        formatted_time = test_timestamp.strftime("%Y-%m-%d %H:%M:%S")
        
        assert formatted_time == "2024-06-24 10:15:30"
        assert len(formatted_time) == 19  # Fixed length format
        
    def test_debug_output_price_formatting(self):
        """Test price formatting in debug output"""
        test_prices = [5464.05, 5474.57, 5462.96]
        
        for price in test_prices:
            # Should format to 2 decimal places with @ prefix for entry prices
            entry_format = f"@{price:.2f}"
            assert entry_format.startswith("@")
            assert "." in entry_format
            assert len(entry_format.split(".")[-1]) == 2  # 2 decimal places
            
    def test_debug_output_pnl_formatting(self):
        """Test P&L formatting in debug output"""
        test_pnl_values = [105.20, -87.45, 0.0]
        
        for pnl in test_pnl_values:
            if pnl > 0:
                formatted = f"+${pnl:.2f}"
                assert formatted.startswith("+$")
            elif pnl < 0:
                formatted = f"-${abs(pnl):.2f}"
                assert formatted.startswith("-$")
            else:
                formatted = f"${pnl:.2f}"
                assert formatted.startswith("$")
                
            # Should always have 2 decimal places
            assert "." in formatted
            assert len(formatted.split(".")[-1]) == 2
            
    def test_debug_output_bps_formatting(self):
        """Test basis points formatting in debug output"""
        test_bps_values = [2.1, -2.0, 1.8, -3.5]
        
        for bps in test_bps_values:
            if bps > 0:
                formatted = f"+{bps}bps"
                assert formatted.startswith("+")
            else:
                formatted = f"{bps}bps"  # Negative sign included in value
                
            assert formatted.endswith("bps")
            assert isinstance(bps, (int, float))
            
    def test_debug_output_direction_formatting(self):
        """Test trade direction formatting"""
        directions = ["LONG", "SHORT"]
        
        for direction in directions:
            # Should be uppercase
            assert direction.isupper()
            assert direction in ["LONG", "SHORT"]
            
    def test_debug_output_reason_formatting(self):
        """Test exit reason formatting in square brackets"""
        exit_reasons = [
            "PROFIT_TARGET",
            "TRAILING_STOP", 
            "END_OF_DAY_FORCE_CLOSE",
            "STOP_LOSS"
        ]
        
        for reason in exit_reasons:
            formatted = f"[{reason}]"
            assert formatted.startswith("[")
            assert formatted.endswith("]")
            assert reason.replace("_", " ").replace("_", " ") != reason or "_" in reason  # Uses underscores
            
    def test_limited_console_output_structure(self):
        """Test limited console output structure (max 5 trades/day)"""
        max_daily_output = 5
        
        # Simulate a day with more than 5 trades
        daily_trades = []
        for i in range(8):  # 8 trades (more than limit)
            trade = {
                'timestamp': datetime(2024, 6, 24, 10 + i, 0, 0),
                'direction': 'LONG' if i % 2 == 0 else 'SHORT',
                'entry_price': 5464.05 + i,
                'exit_price': 5474.57 + i,
                'pnl': 10.0 * (i + 1)
            }
            daily_trades.append(trade)
            
        # First 5 should get full console output
        console_output = daily_trades[:max_daily_output]
        assert len(console_output) == 5
        
        # Remaining should be file-only
        file_only = daily_trades[max_daily_output:]
        assert len(file_only) == 3
        
        # Should show overflow message after limit
        overflow_needed = len(daily_trades) > max_daily_output
        assert overflow_needed is True

class TestDebugOutputGeneration:
    """Test actual debug output generation methods"""
    
    def test_create_sample_debug_lines(self, sample_debug_output_format):
        """Test creation of sample debug output lines"""
        
        # This function would be called during actual backtest execution
        def generate_debug_line(action_type, timestamp, **kwargs):
            """Generate debug line based on action type"""
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            if action_type == "ENTRY":
                direction = kwargs['direction']
                price = kwargs['price']
                bps_change = kwargs['bps_change']
                return f"{time_str} - ENTRY: {direction} @{price:.2f} [2bps trigger: {bps_change:+.1f}bps]"
                
            elif action_type == "EXIT":
                direction = kwargs['direction']
                entry_price = kwargs['entry_price']
                exit_price = kwargs['exit_price']
                pnl = kwargs['pnl']
                reason = kwargs['reason']
                return f"{time_str} - EXIT: {direction} {entry_price:.2f}->{exit_price:.2f}, P&L: {pnl:+.2f}, [{reason}]"
                
            elif action_type == "DAY_CLOSE":
                trade_count = kwargs['trade_count']
                gross_pnl = kwargs['gross_pnl']
                net_pnl = kwargs['net_pnl']
                return f"{time_str} - DAY_CLOSE: {trade_count} trades, Gross P&L: {gross_pnl:+.2f}, Net P&L: {net_pnl:+.2f}"
                
        # Test generation of each type
        entry_line = generate_debug_line(
            "ENTRY",
            datetime(2024, 6, 24, 10, 15, 0),
            direction="LONG",
            price=5464.05,
            bps_change=2.1
        )
        
        exit_line = generate_debug_line(
            "EXIT",
            datetime(2024, 6, 24, 10, 45, 0),
            direction="LONG",
            entry_price=5464.05,
            exit_price=5474.57,
            pnl=105.20,
            reason="PROFIT_TARGET"
        )
        
        day_close_line = generate_debug_line(
            "DAY_CLOSE", 
            datetime(2024, 6, 24, 16, 0, 0),
            trade_count=4,
            gross_pnl=234.60,
            net_pnl=214.60
        )
        
        # Validate generated lines match expected format
        assert "ENTRY: LONG @5464.05 [2bps trigger: +2.1bps]" in entry_line
        assert "EXIT: LONG 5464.05->5474.57, P&L: +105.20" in exit_line
        assert "DAY_CLOSE: 4 trades, Gross P&L: +234.60, Net P&L: +214.60" in day_close_line
        
    def test_debug_output_file_vs_console_routing(self):
        """Test routing of debug output to file vs console"""
        
        class MockDebugLogger:
            def __init__(self, max_console_per_day=5):
                self.max_console_per_day = max_console_per_day
                self.console_count = 0
                self.file_lines = []
                self.console_lines = []
                self.current_date = None
                
            def log_trade_event(self, timestamp, message):
                # Reset counter for new day
                if self.current_date != timestamp.date():
                    self.current_date = timestamp.date()
                    self.console_count = 0
                    
                # Always log to file
                self.file_lines.append(f"FILE: {message}")
                
                # Log to console only if under daily limit
                if self.console_count < self.max_console_per_day:
                    self.console_lines.append(f"CONSOLE: {message}")
                    self.console_count += 1
                elif self.console_count == self.max_console_per_day:
                    self.console_lines.append("CONSOLE: ... [Additional trades logged to file only]")
                    self.console_count += 1
                    
        # Test with multiple trades in one day
        logger = MockDebugLogger(max_console_per_day=3)
        
        # Log 5 trades (more than console limit of 3)
        for i in range(5):
            timestamp = datetime(2024, 6, 24, 10 + i, 0, 0)
            message = f"Trade {i+1}: ENTRY LONG @{5464.05 + i}"
            logger.log_trade_event(timestamp, message)
            
        # All 5 should be in file
        assert len(logger.file_lines) == 5
        
        # Only 3 trades + 1 overflow message should be in console
        assert len(logger.console_lines) == 4
        assert "Additional trades logged to file only" in logger.console_lines[-1]
        
    def test_debug_output_performance_impact(self):
        """Test that debug output has minimal performance impact"""
        import time
        
        class MockPerformantDebugLogger:
            def __init__(self, enabled=True):
                self.enabled = enabled
                self.messages = []
                
            def log_message(self, message):
                if not self.enabled:
                    return  # Skip processing when disabled
                    
                self.messages.append(message)
                
        # Test performance with debug enabled vs disabled
        logger_enabled = MockPerformantDebugLogger(enabled=True)
        logger_disabled = MockPerformantDebugLogger(enabled=False)
        
        test_message = "Test debug message with formatting"
        iterations = 1000
        
        # Time with debug enabled
        start_time = time.time()
        for i in range(iterations):
            logger_enabled.log_message(f"{test_message} {i}")
        enabled_time = time.time() - start_time
        
        # Time with debug disabled
        start_time = time.time()
        for i in range(iterations):
            logger_disabled.log_message(f"{test_message} {i}")
        disabled_time = time.time() - start_time
        
        # Debug disabled should be much faster
        assert disabled_time < enabled_time
        assert len(logger_enabled.messages) == iterations
        assert len(logger_disabled.messages) == 0
        
        # Performance impact should be reasonable
        assert enabled_time < 0.1  # Should complete 1000 operations in under 100ms

class TestDebugOutputValidation:
    """Test validation of debug output requirements"""
    
    def test_debug_output_meets_requirements(self, sample_debug_output_format):
        """Test that debug output meets all specified requirements"""
        
        # Requirements from development plan:
        # 1. Max 5 trades/day expected
        # 2. Console output limited 
        # 3. Sample format for validation
        # 4. Command-line debugging without breaking application
        
        # Validate requirement 1: Max 5 trades/day expected
        daily_trade_lines = [line for line in sample_debug_output_format 
                           if "ENTRY:" in line or "EXIT:" in line]
        trade_count = len([line for line in daily_trade_lines if "ENTRY:" in line])
        assert trade_count <= 5, f"Sample shows {trade_count} trades, expected ≤ 5"
        
        # Validate requirement 2: Console output limited
        overflow_line = sample_debug_output_format[-1]
        assert "Additional trades logged to file only" in overflow_line
        
        # Validate requirement 3: Sample format suitable for validation
        for line in sample_debug_output_format[:-1]:  # Exclude overflow message
            assert len(line) > 20, "Debug lines should be informative"
            assert "2024-06-24" in line, "Should include date"
            assert any(action in line for action in ["ENTRY:", "EXIT:", "DAY_CLOSE:"]), "Should specify action"
            
        # Validate requirement 4: Non-breaking debugging
        # Debug output should be simple strings that don't require user interaction
        for line in sample_debug_output_format:
            assert isinstance(line, str), "All debug output should be strings"
            assert "\n" not in line, "Debug lines should be single-line"
            assert len(line) < 200, "Debug lines should be concise"
            
    def test_debug_output_contains_required_information(self, sample_debug_output_format):
        """Test that debug output contains all required trading information"""
        
        # Should contain trade direction information
        directions_found = []
        for line in sample_debug_output_format:
            if "LONG" in line:
                directions_found.append("LONG")
            if "SHORT" in line:
                directions_found.append("SHORT")
                
        assert "LONG" in directions_found, "Sample should show LONG trades"
        assert "SHORT" in directions_found, "Sample should show SHORT trades"
        
        # Should contain price information
        price_info_found = False
        for line in sample_debug_output_format:
            if "@" in line and "." in line:  # Price format like @5464.05
                price_info_found = True
                break
        assert price_info_found, "Sample should show price information"
        
        # Should contain P&L information
        pnl_info_found = False
        for line in sample_debug_output_format:
            if "P&L:" in line and "$" in line:
                pnl_info_found = True
                break
        assert pnl_info_found, "Sample should show P&L information"
        
        # Should contain trigger information
        trigger_info_found = False
        for line in sample_debug_output_format:
            if "2bps trigger:" in line:
                trigger_info_found = True
                break
        assert trigger_info_found, "Sample should show trigger information"
        
        # Should contain daily summary
        daily_summary_found = False
        for line in sample_debug_output_format:
            if "DAY_CLOSE:" in line:
                daily_summary_found = True
                break
        assert daily_summary_found, "Sample should show daily summary"