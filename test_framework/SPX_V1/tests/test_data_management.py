"""
Test suite for Data Management functionality.
Tests market data retrieval, validation, and quality checks.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, time, timedelta
import sys
from pathlib import Path

# Import strategy components (adjust as needed)
try:
    from spx_v1_strategy import SPX_V1Strategy
    from market_data import Retrieve
except ImportError:
    # Fallback for test environment
    print(f"Warning: Could not import {self.framework_name} strategy components")
    
    class SPX_V1Strategy:
        def __init__(self, params):
            self.params = params
            self.trades = []
        
        def run_backtest(self, data):
            return self.params.get('initial_capital', 25000)
        
        def generate_analytics(self):
            return {'total_trades': 0, 'win_rate': 0, 'total_pnl': 0}
    
    class Retrieve:
        def get_data(self, symbol, start_date, end_date, frequency):
            return pd.DataFrame()



class TestMarketDataRetrieval:
    """Test suite for Market Data Retrieval."""
    
    @pytest.mark.unit
    @pytest.mark.data
    def test_market_data_provider_connection(self, test_logger):
        """Verify connection to market data providers."""
        test_logger.start_test("test_market_data_provider_connection")
        
        try:
            retriever = Retrieve()
            assert retriever is not None
            assert hasattr(retriever, 'get_data')
            
            test_logger.end_test("test_market_data_provider_connection", "PASS")
        except Exception as e:
            test_logger.end_test("test_market_data_provider_connection", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    @pytest.mark.data
    def test_data_frequency_mapping(self, test_logger, mock_retrieve_class):
        """Test frequency parameter mapping."""
        test_logger.start_test("test_data_frequency_mapping")
        
        try:
            valid_frequencies = ["1M", "5M", "30M", "1H", "1D"]
            
            for freq in valid_frequencies:
                data = mock_retrieve_class.get_data("TEST", "2023-01-01", "2023-01-02", freq)
                assert isinstance(data, pd.DataFrame)
                assert all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
            
            test_logger.end_test("test_data_frequency_mapping", "PASS")
        except Exception as e:
            test_logger.end_test("test_data_frequency_mapping", "FAIL", str(e))
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
            
            # Check index is datetime
            assert isinstance(data.index, pd.DatetimeIndex)
            
            test_logger.end_test("test_data_format_consistency", "PASS")
        except Exception as e:
            test_logger.end_test("test_data_format_consistency", "FAIL", str(e))
            raise


class TestDataQuality:
    """Test suite for Data Quality validation."""
    
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
            
            test_logger.end_test("test_data_logical_consistency", "PASS")
        except Exception as e:
            test_logger.end_test("test_data_logical_consistency", "FAIL", str(e))
            raise
