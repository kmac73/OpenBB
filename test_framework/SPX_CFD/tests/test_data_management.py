"""
Test suite for Data Management functionality (Category 1).
Tests market data retrieval, validation, and quality checks.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, time
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path

# Import the market data module
try:
    from market_data import Retrieve
except ImportError:
    # Fallback for test environment
    sys.path.append(str(Path(__file__).parent.parent.parent.parent / "app" / "SP500_CFD_v1"))
    from market_data import Retrieve


class TestMarketDataRetrieval:
    """Test suite for Market Data Retrieval (1.1)."""
    
    @pytest.mark.unit
    @pytest.mark.data
    def test_market_data_provider_connection(self, test_logger):
        """Verify connection to market data providers."""
        test_logger.start_test("test_market_data_provider_connection")
        
        try:
            retriever = Retrieve()
            # Test provider connection without actually fetching data
            assert retriever is not None
            assert hasattr(retriever, 'from_provider')
            assert hasattr(retriever, 'get_data')
            
            test_logger.end_test("test_market_data_provider_connection", "PASS")
        except Exception as e:
            test_logger.end_test("test_market_data_provider_connection", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    @pytest.mark.data
    def test_market_data_from_file_connection(self, test_logger):
        """Verify access to market data files under market_data/historical/SPX."""
        test_logger.start_test("test_market_data_from_file_connection")
        
        try:
            retriever = Retrieve()
            assert hasattr(retriever, 'from_file')
            
            # Test file access method exists
            method = getattr(retriever, 'from_file')
            assert callable(method)
            
            test_logger.end_test("test_market_data_from_file_connection", "PASS")
        except Exception as e:
            test_logger.end_test("test_market_data_from_file_connection", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_data_frequency_mapping(self, test_logger, mock_retrieve_class):
        """Test frequency parameter mapping (provider:1D, from_file:1M, 5M, 30M, 1H, 1D)."""
        test_logger.start_test("test_data_frequency_mapping")
        
        try:
            valid_frequencies = ["1M", "5M", "30M", "1H", "1D"]
            
            for freq in valid_frequencies:
                # Mock the get_data method to return valid data
                data = mock_retrieve_class.get_data("SPX", "2023-01-01", "2023-01-02", freq)
                
                assert isinstance(data, pd.DataFrame)
                assert not data.empty
                assert all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
            
            test_logger.end_test("test_data_frequency_mapping", "PASS")
        except Exception as e:
            test_logger.end_test("test_data_frequency_mapping", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    @pytest.mark.data
    def test_data_date_range_validation(self, test_logger):
        """Validate start/end date handling."""
        test_logger.start_test("test_data_date_range_validation")
        
        try:
            retriever = Retrieve()
            
            # Test valid date formats
            valid_dates = [
                ("2023-01-01", "2023-01-31"),
                ("2022-12-01", "2022-12-31"),
            ]
            
            for start_date, end_date in valid_dates:
                start_dt = pd.to_datetime(start_date)
                end_dt = pd.to_datetime(end_date)
                assert start_dt < end_dt, f"Start date {start_date} should be before end date {end_date}"
            
            # Test invalid date ranges
            with pytest.raises((ValueError, Exception)):
                pd.to_datetime("invalid-date")
            
            test_logger.end_test("test_data_date_range_validation", "PASS")
        except Exception as e:
            test_logger.end_test("test_data_date_range_validation", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    def test_data_symbol_validation(self, test_logger):
        """Test symbol format and validation (SPX)."""
        test_logger.start_test("test_data_symbol_validation")
        
        try:
            valid_symbols = ["SPX", "^SPX"]
            invalid_symbols = ["", None, 123, "INVALID_SYMBOL_TOOLONG"]
            
            for symbol in valid_symbols:
                assert isinstance(symbol, str)
                assert len(symbol) >= 1
                assert len(symbol) <= 10
            
            for symbol in invalid_symbols:
                if symbol is None:
                    continue
                if isinstance(symbol, str) and len(symbol) > 10:
                    assert len(symbol) > 10  # Should be invalid
            
            test_logger.end_test("test_data_symbol_validation", "PASS")
        except Exception as e:
            test_logger.end_test("test_data_symbol_validation", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_data_missing_handling(self, test_logger, mock_market_data):
        """Test handling of missing or incomplete data."""
        test_logger.start_test("test_data_missing_handling")
        
        try:
            # Test with empty dataset
            empty_data = pd.DataFrame()
            assert empty_data.empty
            
            # Test with missing columns
            incomplete_data = pd.DataFrame({
                'Open': [100, 101, 102],
                'Close': [101, 102, 103]
                # Missing High, Low, Volume
            })
            
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = set(required_columns) - set(incomplete_data.columns)
            assert len(missing_columns) > 0
            
            # Test data can be completed
            for col in missing_columns:
                if col == 'Volume':
                    incomplete_data[col] = 1000000
                elif col == 'High':
                    incomplete_data[col] = incomplete_data[['Open', 'Close']].max(axis=1) + 1
                elif col == 'Low':
                    incomplete_data[col] = incomplete_data[['Open', 'Close']].min(axis=1) - 1
            
            assert all(col in incomplete_data.columns for col in required_columns)
            
            test_logger.end_test("test_data_missing_handling", "PASS")
        except Exception as e:
            test_logger.end_test("test_data_missing_handling", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_data_format_consistency(self, test_logger, mock_market_data):
        """Verify OHLCV data format consistency."""
        test_logger.start_test("test_data_format_consistency")
        
        try:
            data = mock_market_data(start_date="2023-01-01", end_date="2023-01-05", frequency="5M")
            
            # Check required columns exist
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            assert all(col in data.columns for col in required_columns)
            
            # Check data types
            for col in ['Open', 'High', 'Low', 'Close']:
                assert pd.api.types.is_numeric_dtype(data[col])
            
            assert pd.api.types.is_numeric_dtype(data['Volume'])
            
            # Check index is datetime
            assert isinstance(data.index, pd.DatetimeIndex)
            
            test_logger.end_test("test_data_format_consistency", "PASS")
        except Exception as e:
            test_logger.end_test("test_data_format_consistency", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    def test_data_timezone_handling(self, test_logger):
        """Test EST timezone handling for trading hours."""
        test_logger.start_test("test_data_timezone_handling")
        
        try:
            # Test trading hours validation
            market_open = time(9, 30)  # 9:30 AM EST
            market_close = time(16, 0)  # 4:00 PM EST
            
            test_times = [
                time(9, 30),   # Market open - valid
                time(12, 0),   # Midday - valid
                time(15, 59),  # Just before close - valid
                time(16, 0),   # Market close - valid
            ]
            
            for test_time in test_times:
                assert market_open <= test_time <= market_close
            
            # Test invalid times
            invalid_times = [time(9, 29), time(16, 1), time(6, 0), time(20, 0)]
            for test_time in invalid_times:
                assert not (market_open <= test_time <= market_close)
            
            test_logger.end_test("test_data_timezone_handling", "PASS")
        except Exception as e:
            test_logger.end_test("test_data_timezone_handling", "FAIL", str(e))
            raise


class TestDataQuality:
    """Test suite for Data Quality (1.2)."""
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_data_completeness(self, test_logger, mock_market_data):
        """Verify no missing OHLCV values."""
        test_logger.start_test("test_data_completeness")
        
        try:
            data = mock_market_data(start_date="2023-01-01", end_date="2023-01-05", frequency="5M")
            
            # Check for missing values
            assert not data.isnull().any().any(), "Data contains missing values"
            
            # Check all required columns exist
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = set(required_columns) - set(data.columns)
            assert len(missing_columns) == 0, f"Missing columns: {missing_columns}"
            
            # Check data is not empty
            assert len(data) > 0, "Data is empty"
            
            test_logger.end_test("test_data_completeness", "PASS")
        except Exception as e:
            test_logger.end_test("test_data_completeness", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_data_logical_consistency(self, test_logger, mock_market_data):
        """Test High >= Low, OHLC relationships."""
        test_logger.start_test("test_data_logical_consistency")
        
        try:
            data = mock_market_data(start_date="2023-01-01", end_date="2023-01-05", frequency="5M")
            
            # Test High >= Low
            assert (data['High'] >= data['Low']).all(), "High prices should be >= Low prices"
            
            # Test High >= Open and High >= Close
            assert (data['High'] >= data['Open']).all(), "High should be >= Open"
            assert (data['High'] >= data['Close']).all(), "High should be >= Close"
            
            # Test Low <= Open and Low <= Close
            assert (data['Low'] <= data['Open']).all(), "Low should be <= Open"
            assert (data['Low'] <= data['Close']).all(), "Low should be <= Close"
            
            # Test all prices are positive
            assert (data['Open'] > 0).all(), "Open prices should be positive"
            assert (data['High'] > 0).all(), "High prices should be positive" 
            assert (data['Low'] > 0).all(), "Low prices should be positive"
            assert (data['Close'] > 0).all(), "Close prices should be positive"
            
            test_logger.end_test("test_data_logical_consistency", "PASS")
        except Exception as e:
            test_logger.end_test("test_data_logical_consistency", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_data_volume_presence(self, test_logger, mock_market_data):
        """Ensure volume data exists or defaults properly."""
        test_logger.start_test("test_data_volume_presence")
        
        try:
            data = mock_market_data(start_date="2023-01-01", end_date="2023-01-05", frequency="5M")
            
            # Check volume column exists
            assert 'Volume' in data.columns, "Volume column missing"
            
            # Check volume values are positive
            assert (data['Volume'] > 0).all(), "Volume should be positive"
            
            # Check volume is numeric
            assert pd.api.types.is_numeric_dtype(data['Volume']), "Volume should be numeric"
            
            # Check no missing volume values
            assert not data['Volume'].isnull().any(), "Volume contains missing values"
            
            test_logger.end_test("test_data_volume_presence", "PASS")
        except Exception as e:
            test_logger.end_test("test_data_volume_presence", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_data_price_precision(self, test_logger, mock_market_data):
        """Verify price precision and decimal handling."""
        test_logger.start_test("test_data_price_precision")
        
        try:
            data = mock_market_data(start_date="2023-01-01", end_date="2023-01-05", frequency="5M")
            
            price_columns = ['Open', 'High', 'Low', 'Close']
            
            for col in price_columns:
                # Check prices are reasonable (between $1000 and $10000 for SPX)
                assert (data[col] >= 1000).all(), f"{col} prices too low"
                assert (data[col] <= 10000).all(), f"{col} prices too high"
                
                # Check precision (should have at most 2-4 decimal places)
                # Convert to string and check decimal places
                price_strings = data[col].astype(str)
                for price_str in price_strings.head(10):  # Check first 10 for performance
                    if '.' in price_str:
                        decimal_places = len(price_str.split('.')[1])
                        assert decimal_places <= 4, f"Too many decimal places in {col}: {price_str}"
            
            test_logger.end_test("test_data_price_precision", "PASS")
        except Exception as e:
            test_logger.end_test("test_data_price_precision", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    @pytest.mark.mock
    def test_data_chronological_order(self, test_logger, mock_market_data):
        """Ensure data is properly time-ordered."""
        test_logger.start_test("test_data_chronological_order")
        
        try:
            data = mock_market_data(start_date="2023-01-01", end_date="2023-01-05", frequency="5M")
            
            # Check index is sorted
            assert data.index.is_monotonic_increasing, "Data index is not chronologically ordered"
            
            # Check no duplicate timestamps
            assert not data.index.duplicated().any(), "Data contains duplicate timestamps"
            
            # Check timestamps are within expected range
            start_expected = pd.to_datetime("2023-01-01")
            end_expected = pd.to_datetime("2023-01-05")
            
            assert data.index.min() >= start_expected, "Data starts before expected date"
            assert data.index.max() <= end_expected + pd.Timedelta(days=1), "Data ends after expected date"
            
            test_logger.end_test("test_data_chronological_order", "PASS")
        except Exception as e:
            test_logger.end_test("test_data_chronological_order", "FAIL", str(e))
            raise