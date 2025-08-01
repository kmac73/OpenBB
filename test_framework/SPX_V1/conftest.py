"""
Global pytest configuration and fixtures for SPX_V1 testing framework.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
from unittest.mock import Mock, MagicMock
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Test configuration
TEST_DATA_DIR = Path(__file__).parent / "fixtures" / "data"
TEST_RESULTS_DIR = Path(__file__).parent / "results"

# Ensure directories exist
TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="session")
def test_config():
    """Test configuration parameters."""
    return {
        "test_data_dir": TEST_DATA_DIR,
        "test_results_dir": TEST_RESULTS_DIR,
        "default_timeout": 30,
        "performance_threshold": {
            "backtest_time": 30.0,  # seconds
            "memory_usage": 2.0,    # GB
            "ui_load_time": 5.0     # seconds
        }
    }


@pytest.fixture
def sample_strategy_params():
    """Standard strategy parameters for testing."""
    return {
        'threshold': 15.0
    }


@pytest.fixture
def mock_market_data():
    """Generate mock OHLCV market data for testing."""
    def _generate_data(
        start_date="2023-01-01", 
        end_date="2023-01-31", 
        frequency="5M",
        trend="random"
    ):
        # Generate datetime index
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        if frequency in ["1M", "5M", "15M", "30M", "1H"]:
            # Trading hours: 9:30 AM to 4:00 PM
            dates = pd.date_range(start, end, freq='D')
            
            if frequency == "1M":
                freq_str = '1T'
            elif frequency == "5M":
                freq_str = '5T'
            elif frequency == "15M":
                freq_str = '15T'
            elif frequency == "30M":
                freq_str = '30T'
            elif frequency == "1H":
                freq_str = '1H'
            
            times = pd.date_range('09:30', '16:00', freq=freq_str).time
            
            datetime_index = []
            for date in dates:
                if date.weekday() < 5:  # Monday to Friday
                    for time_val in times:
                        datetime_index.append(pd.Timestamp.combine(date.date(), time_val))
            
            datetime_index = pd.DatetimeIndex(datetime_index)
        else:
            datetime_index = pd.date_range(start, end, freq='D')
        
        n_periods = len(datetime_index)
        
        # Generate price data based on trend and strategy type
        if "cfd" == "cfd":
            base_price = 4500.0  # S&P 500 level
        elif "cfd" == "forex":
            base_price = 1.1000  # EUR/USD level
        elif "cfd" == "crypto":
            base_price = 50000.0  # BTC level
        else:
            base_price = 100.0   # Generic price level
        
        if trend == "uptrend":
            trend_component = np.linspace(0, base_price * 0.1, n_periods)
        elif trend == "downtrend":
            trend_component = np.linspace(0, -base_price * 0.1, n_periods)
        elif trend == "sideways":
            trend_component = np.sin(np.linspace(0, 4*np.pi, n_periods)) * base_price * 0.02
        else:  # random
            trend_component = np.cumsum(np.random.normal(0, base_price * 0.001, n_periods))
        
        # Generate OHLCV data
        close_prices = base_price + trend_component + np.random.normal(0, base_price * 0.002, n_periods)
        
        # Ensure realistic OHLC relationships
        opens = close_prices + np.random.normal(0, base_price * 0.001, n_periods)
        
        highs = np.maximum(opens, close_prices) + np.abs(np.random.normal(0, base_price * 0.003, n_periods))
        lows = np.minimum(opens, close_prices) - np.abs(np.random.normal(0, base_price * 0.003, n_periods))
        
        # Ensure High >= max(Open, Close) and Low <= min(Open, Close)
        highs = np.maximum(highs, np.maximum(opens, close_prices))
        lows = np.minimum(lows, np.minimum(opens, close_prices))
        
        volume = np.random.randint(500000, 2000000, n_periods)
        
        data = pd.DataFrame({
            'Open': opens,
            'High': highs,
            'Low': lows,
            'Close': close_prices,
            'Volume': volume
        }, index=datetime_index)
        
        return data
    
    return _generate_data


@pytest.fixture
def mock_retrieve_class():
    """Mock market data Retrieve class."""
    mock = MagicMock()
    
    def mock_get_data(symbol, start_date, end_date, frequency="5M"):
        # Return sample data
        dates = pd.date_range(start_date, end_date, freq='5T')
        n = len(dates)
        
        data = pd.DataFrame({
            'Open': 100 + np.random.normal(0, 2, n),
            'High': 102 + np.random.normal(0, 2, n),
            'Low': 98 + np.random.normal(0, 2, n),
            'Close': 100 + np.random.normal(0, 2, n),
            'Volume': np.random.randint(500000, 1500000, n)
        }, index=dates)
        
        return data
    
    mock.get_data = mock_get_data
    return mock


@pytest.fixture
def sample_trades_data():
    """Sample trades data for analytics testing."""
    trades = []
    base_time = datetime(2023, 1, 1, 10, 0)
    
    for i in range(10):
        entry_time = base_time + timedelta(days=i, hours=1)
        exit_time = entry_time + timedelta(hours=2)
        
        # Mix of winning and losing trades
        is_winner = i % 3 != 0  # 2/3 winners, 1/3 losers
        direction = 'LONG' if i % 2 == 0 else 'SHORT'
        
        if is_winner:
            gross_pnl = np.random.uniform(100, 500)
        else:
            gross_pnl = np.random.uniform(-200, -50)
        
        trade = {
            'entry_time': entry_time,
            'exit_time': exit_time,
            'direction': direction,
            'entry_price': 100 + np.random.normal(0, 5),
            'exit_price': 100 + np.random.normal(0, 5),
            'size': 25,
            'gross_pnl': gross_pnl,
            'transaction_cost': 26.0,
            'net_pnl': gross_pnl - 26.0,
            'exit_reason': 'Profit Target' if is_winner else 'Stop Loss',
            'duration': timedelta(hours=2),
            'duration_minutes': 120
        }
        trades.append(trade)
    
    return trades


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components for UI testing."""
    class MockStreamlit:
        def __init__(self):
            self.sidebar = Mock()
            self.columns = Mock(return_value=[Mock(), Mock(), Mock(), Mock()])
            self.success = Mock()
            self.error = Mock()
            self.warning = Mock()
            self.info = Mock()
            self.spinner = Mock()
            self.progress = Mock()
            self.plotly_chart = Mock()
            self.dataframe = Mock()
            self.table = Mock()
            self.metric = Mock()
            self.markdown = Mock()
            self.title = Mock()
            self.header = Mock()
            self.subheader = Mock()
            self.text_input = Mock()
            self.selectbox = Mock()
            self.slider = Mock()
            self.button = Mock(return_value=False)
            self.file_uploader = Mock(return_value=None)
            self.download_button = Mock()
            
            # Sidebar mocks
            self.sidebar.header = Mock()
            self.sidebar.subheader = Mock()
            self.sidebar.selectbox = Mock()
            self.sidebar.slider = Mock()
            self.sidebar.text_input = Mock()
            self.sidebar.button = Mock(return_value=False)
            self.sidebar.file_uploader = Mock(return_value=None)
            self.sidebar.success = Mock()
            self.sidebar.error = Mock()
            self.sidebar.warning = Mock()
            self.sidebar.info = Mock()
            self.sidebar.json = Mock()
    
    return MockStreamlit()


@pytest.fixture
def mock_plotly():
    """Mock Plotly components for chart testing."""
    class MockPlotly:
        def __init__(self):
            self.Figure = Mock()
            self.Scatter = Mock()
            self.Candlestick = Mock()
            self.Bar = Mock()
            
        def make_subplots(self, **kwargs):
            return Mock()
    
    return MockPlotly()


@pytest.fixture
def test_logger():
    """Test result logger for command line output."""
    class TestLogger:
        def __init__(self):
            self.results = []
            self.current_test = None
        
        def start_test(self, test_name):
            self.current_test = test_name
            timestamp = datetime.now().strftime("%H:%M:%S")
            message = f"[{timestamp}] Executing test: {test_name}"
            print(message)
            self.results.append({"test": test_name, "status": "RUNNING", "timestamp": timestamp})
        
        def end_test(self, test_name, status, message=""):
            timestamp = datetime.now().strftime("%H:%M:%S")
            status_message = f"[{timestamp}] {test_name}: {status}"
            if message:
                status_message += f" - {message}"
            print(status_message)
            
            # Update results
            for result in self.results:
                if result["test"] == test_name and result["status"] == "RUNNING":
                    result["status"] = status
                    result["end_timestamp"] = timestamp
                    result["message"] = message
                    break
        
        def get_results(self):
            return self.results
    
    return TestLogger()


# Pytest configuration hooks
def pytest_configure(config):
    """Pytest configuration hook."""
    pass


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Add slow marker to tests with 'slow' in name
        if "slow" in item.name:
            item.add_marker(pytest.mark.slow)
        
        # Add category markers based on file names
        test_file = str(item.fspath)
        if "ui" in test_file:
            item.add_marker(pytest.mark.ui)
        elif "performance" in test_file:
            item.add_marker(pytest.mark.performance)
        elif "integration" in test_file:
            item.add_marker(pytest.mark.integration)
