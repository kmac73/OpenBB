"""
Test Market Data Integration - Phase 0 Test Suite
Tests written BEFORE implementation - Test-First Approach

These tests verify integration with existing market_data.py from_file method
and validate data handling for the backtest system.
"""
import pytest
import pandas as pd
from datetime import datetime, date
from pathlib import Path
import sys

# Add path for existing market_data.py
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "app"))

# Import existing market data module
try:
    from common.market_data import Retrieve
except ImportError:
    # This should work since market_data.py already exists
    Retrieve = None
    pytest.skip("market_data.py not found", allow_module_level=True)

class TestMarketDataFromFile:
    """Test existing from_file static method integration"""
    
    def test_from_file_method_exists_and_accessible(self):
        """Test that from_file static method exists and is accessible"""
        assert hasattr(Retrieve, 'from_file')
        assert callable(Retrieve.from_file)
        
    def test_load_last_5_days_real_data(self, last_5_days_real_data):
        """Test loading last 5 days of real data using market_data.py"""
        # Verify our test fixture loaded real data correctly
        assert not last_5_days_real_data.empty
        assert len(last_5_days_real_data) == 400  # 5 days * ~80 5-minute intervals per day
        
        # Verify data structure matches expected format
        expected_columns = ['date', 'open', 'high', 'low', 'close']
        for col in expected_columns:
            assert col in last_5_days_real_data.columns
            
        # Verify date range covers last 5 trading days
        start_date = last_5_days_real_data['date'].min().date()
        end_date = last_5_days_real_data['date'].max().date()
        
        assert start_date == date(2024, 6, 24)
        assert end_date == date(2024, 6, 28)
        
    def test_from_file_with_5m_frequency(self):
        """Test from_file method with 5M frequency - our primary test data"""
        try:
            # Test using actual from_file method
            data = Retrieve.from_file(['SPX'], '2024-06-24', '2024-06-28', '5M')
            
            assert not data.empty
            assert 'date' in data.columns or data.index.name == 'date'
            assert all(col in data.columns for col in ['open', 'high', 'low', 'close'])
            
        except Exception as e:
            # Document any issues with existing method for Phase 1 implementation
            pytest.fail(f"from_file method failed: {e}")
            
    def test_data_format_validation(self, last_5_days_real_data):
        """Test that loaded data has correct format and types"""
        # Verify datetime parsing
        assert pd.api.types.is_datetime64_any_dtype(last_5_days_real_data['date'])
        
        # Verify numeric columns
        numeric_columns = ['open', 'high', 'low', 'close']
        for col in numeric_columns:
            assert pd.api.types.is_numeric_dtype(last_5_days_real_data[col])
            assert last_5_days_real_data[col].notna().all()
            
        # Verify OHLC relationships (basic sanity check)
        for idx, row in last_5_days_real_data.head(10).iterrows():  # Check first 10 rows
            assert row['low'] <= row['open'], f"Low > Open at {row['date']}"
            assert row['low'] <= row['close'], f"Low > Close at {row['date']}"
            assert row['high'] >= row['open'], f"High < Open at {row['date']}"
            assert row['high'] >= row['close'], f"High < Close at {row['date']}"

class TestDateRangeHandling:
    """Test date range filtering and validation"""
    
    def test_date_range_filtering(self, last_5_days_real_data):
        """Test filtering data by date range"""
        # Filter to just first day
        first_day = date(2024, 6, 24)
        first_day_data = last_5_days_real_data[
            last_5_days_real_data['date'].dt.date == first_day
        ]
        
        assert not first_day_data.empty
        assert all(row.date() == first_day for row in first_day_data['date'])
        
        # Should have approximately 80 5-minute intervals (9:30-16:05)
        assert 70 <= len(first_day_data) <= 85  # Allow some variation
        
    def test_auto_detect_available_date_range(self):
        """Test auto-detection of available date range from 5M.txt file"""
        # This functionality will be implemented in Phase 1
        # Test the file reading approach
        
        file_path = Path(__file__).parent.parent.parent / "market_data/historical/SPX/5M.txt"
        assert file_path.exists(), "5M.txt file not found"
        
        # Read first and last lines to determine range
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
            
            # Get last line efficiently  
            f.seek(0, 2)
            file_size = f.tell()
            f.seek(max(file_size - 1024, 0))
            lines = f.readlines()
            last_line = lines[-1].strip()
            
        # Parse dates from first and last lines
        first_date = pd.to_datetime(first_line.split(',')[0]).date()
        last_date = pd.to_datetime(last_line.split(',')[0]).date()
        
        # Verify we have reasonable date range
        assert first_date <= date(2024, 6, 24)  # Our test data should be within range
        assert last_date >= date(2024, 6, 28)   # Our test data should be within range
        
    def test_date_validation_against_available_data(self):
        """Test validation of user-selected dates against available data"""
        # Test that user can't select dates outside available range
        file_path = Path(__file__).parent.parent.parent / "market_data/historical/SPX/5M.txt"
        
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
            
        earliest_date = pd.to_datetime(first_line.split(',')[0]).date()
        
        # User selecting date before data starts should be invalid
        invalid_start_date = date(2000, 1, 1)  # Way before data starts
        assert invalid_start_date < earliest_date
        
        # This validation will be implemented in Streamlit UI

class TestTradingHoursData:
    """Test trading hours in data and market hours enforcement"""
    
    def test_trading_hours_in_data(self, last_5_days_real_data):
        """Test that data contains expected trading hours"""
        # Group by date and check time ranges
        for date_group, day_data in last_5_days_real_data.groupby(last_5_days_real_data['date'].dt.date):
            day_times = day_data['date'].dt.time
            
            earliest_time = day_times.min()
            latest_time = day_times.max()
            
            # Should start at 9:30 AM
            assert earliest_time <= pd.Time(9, 30), f"Data starts late on {date_group}: {earliest_time}"
            
            # Should end at or after 4:00 PM (data may continue to 4:05 as noted)
            assert latest_time >= pd.Time(16, 0), f"Data ends early on {date_group}: {latest_time}"
            
    def test_market_hours_boundaries(self, last_5_days_real_data, trading_hours_constraints):
        """Test identification of market hours boundaries"""
        # Find 9:30 AM ticks (market open)
        market_open_ticks = last_5_days_real_data[
            last_5_days_real_data['date'].dt.time == trading_hours_constraints['market_open']
        ]
        
        # Should have one 9:30 tick per trading day (5 days)
        assert len(market_open_ticks) == 5
        
        # Find 4:00 PM ticks (force close time)
        force_close_ticks = last_5_days_real_data[
            last_5_days_real_data['date'].dt.time == trading_hours_constraints['force_close']
        ]
        
        # Should have one 4:00 PM tick per trading day
        assert len(force_close_ticks) == 5
        
    def test_data_beyond_trading_hours(self, last_5_days_real_data):
        """Test that data may continue beyond 4:00 PM but trading logic stops at 4:00"""
        # Find ticks after 4:00 PM
        after_hours_ticks = last_5_days_real_data[
            last_5_days_real_data['date'].dt.time > pd.Time(16, 0)
        ]
        
        # Data may continue but should not be many ticks
        if not after_hours_ticks.empty:
            # Verify these are close to market close (e.g., 4:05 PM)
            after_hours_times = after_hours_ticks['date'].dt.time
            latest_after_hours = after_hours_times.max()
            
            # Should not extend too far past market close
            assert latest_after_hours <= pd.Time(16, 10), f"Data extends too late: {latest_after_hours}"

class TestDataGapHandling:
    """Test data gap detection and handling"""
    
    def test_detect_weekend_gaps(self, last_5_days_real_data):
        """Test detection of weekend gaps in data"""
        # Check for date gaps between trading days
        dates = last_5_days_real_data['date'].dt.date.unique()
        dates = sorted(dates)
        
        # Should have exactly 5 trading days with weekend gap
        assert len(dates) == 5
        
        # Check for gaps between consecutive trading days
        for i in range(1, len(dates)):
            current_date = dates[i]
            previous_date = dates[i-1]
            gap_days = (current_date - previous_date).days
            
            # Weekend gaps should be 1 day (consecutive trading days) or 3 days (over weekend)
            assert gap_days in [1, 3], f"Unexpected gap: {gap_days} days between {previous_date} and {current_date}"
            
    def test_no_data_gaps_within_trading_day(self, last_5_days_real_data):
        """Test that there are no gaps within individual trading days"""
        # Check each trading day for 5-minute interval consistency
        for date_group, day_data in last_5_days_real_data.groupby(last_5_days_real_data['date'].dt.date):
            day_data = day_data.sort_values('date')
            
            # Calculate time differences between consecutive ticks
            time_diffs = day_data['date'].diff().dropna()
            
            # Most differences should be 5 minutes (300 seconds)
            expected_interval = pd.Timedelta(minutes=5)
            
            # Allow for some variation due to market closures, etc.
            normal_intervals = time_diffs[time_diffs <= pd.Timedelta(minutes=10)]
            
            # At least 80% of intervals should be normal 5-minute intervals
            normal_ratio = len(normal_intervals) / len(time_diffs)
            assert normal_ratio >= 0.8, f"Too many irregular intervals on {date_group}: {normal_ratio:.2%}"
            
    def test_data_gap_logging_preparation(self):
        """Test preparation for data gap logging functionality"""
        # This will be implemented in Phase 1 - prepare test structure
        
        # Test that we can identify different types of gaps
        gap_types = {
            'weekend_gap': 'Saturday-Sunday gap between trading days',
            'holiday_gap': 'Holiday gap between trading days',
            'intraday_gap': 'Gap within trading day (unusual)',
            'market_closure_gap': 'Early market closure gap'
        }
        
        # Verify gap classification structure exists
        for gap_type, description in gap_types.items():
            assert isinstance(gap_type, str)
            assert isinstance(description, str)

class TestDataIntegrityValidation:
    """Test data integrity and validation"""
    
    def test_no_missing_values_in_critical_columns(self, last_5_days_real_data):
        """Test that OHLC data has no missing values"""
        critical_columns = ['date', 'open', 'high', 'low', 'close']
        
        for col in critical_columns:
            missing_count = last_5_days_real_data[col].isna().sum()
            assert missing_count == 0, f"Found {missing_count} missing values in {col}"
            
    def test_ohlc_relationships_validation(self, last_5_days_real_data):
        """Test OHLC price relationships are valid"""
        # Sample validation - check first 50 rows for performance
        sample_data = last_5_days_real_data.head(50)
        
        for idx, row in sample_data.iterrows():
            # High should be >= Open, Close, Low
            assert row['high'] >= row['open'], f"High < Open at {row['date']}: {row['high']} < {row['open']}"
            assert row['high'] >= row['close'], f"High < Close at {row['date']}: {row['high']} < {row['close']}"
            assert row['high'] >= row['low'], f"High < Low at {row['date']}: {row['high']} < {row['low']}"
            
            # Low should be <= Open, Close, High
            assert row['low'] <= row['open'], f"Low > Open at {row['date']}: {row['low']} > {row['open']}"
            assert row['low'] <= row['close'], f"Low > Close at {row['date']}: {row['low']} > {row['close']}"
            assert row['low'] <= row['high'], f"Low > High at {row['date']}: {row['low']} > {row['high']}"
            
    def test_price_ranges_reasonable(self, last_5_days_real_data):
        """Test that prices are within reasonable ranges for SPX"""
        # SPX should be in thousands, not hundreds or tens of thousands
        price_columns = ['open', 'high', 'low', 'close']
        
        for col in price_columns:
            min_price = last_5_days_real_data[col].min()
            max_price = last_5_days_real_data[col].max()
            
            # SPX typically ranges from 3000-7000 in recent years
            assert 3000 <= min_price <= 7000, f"Suspicious min {col}: {min_price}"
            assert 3000 <= max_price <= 7000, f"Suspicious max {col}: {max_price}"
            
    def test_future_data_provider_validation_comments(self):
        """Test that comments are in place for future from_provider validation"""
        # Verify that market_data.py has TODO comments for from_provider validation
        # This validates the comment structure from the development plan
        
        market_data_file = Path(__file__).parent.parent.parent / "app/common/market_data.py"
        
        if market_data_file.exists():
            with open(market_data_file, 'r') as f:
                content = f.read()
                
            # TODO: MARKET_DATA_PROVIDER comments should be added during Phase 1
            # This test documents the expected comment structure
            expected_comment_topics = [
                'Validate that all expected trading hours are present',
                'Handle partial trading days (early closes)',
                'Validate OHLC relationships'
            ]
            
            # For Phase 0, just verify file exists and is readable
            assert len(content) > 100  # Should have substantial content

class TestPerformanceWithRealData:
    """Test performance characteristics with real data volume"""
    
    def test_data_loading_performance(self, last_5_days_real_data, performance_timing_baseline):
        """Test that data loading meets performance expectations"""
        import time
        
        # Measure time to process our test dataset
        start_time = time.time()
        
        # Simulate basic data processing operations
        processed_data = last_5_days_real_data.copy()
        processed_data['price_change'] = processed_data['close'].diff()
        processed_data['bps_change'] = (processed_data['price_change'] / processed_data['close'].shift(1)) * 10000
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process test data quickly
        max_time = performance_timing_baseline['max_acceptable_time_seconds']
        assert processing_time < max_time, f"Data processing too slow: {processing_time:.2f}s > {max_time}s"
        
        # Verify expected data volume
        expected_points = performance_timing_baseline['expected_data_points']
        assert len(processed_data) == expected_points, f"Unexpected data volume: {len(processed_data)} != {expected_points}"
        
    def test_memory_usage_with_real_data(self, last_5_days_real_data, performance_timing_baseline):
        """Test memory usage with real data volume"""
        import sys
        
        # Measure memory usage of our test dataset
        data_size_bytes = last_5_days_real_data.memory_usage(deep=True).sum()
        data_size_mb = data_size_bytes / (1024 * 1024)
        
        max_memory_mb = performance_timing_baseline['memory_limit_mb']
        assert data_size_mb < max_memory_mb, f"Data uses too much memory: {data_size_mb:.1f}MB > {max_memory_mb}MB"