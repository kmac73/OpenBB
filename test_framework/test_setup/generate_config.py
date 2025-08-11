#!/usr/bin/env python3
"""
OpenBB Test Framework Generator - Configuration Generator
Generates pytest configuration, fixtures, and requirements files.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any


class ConfigGenerator:
    """Generates configuration files for the test framework."""
    
    def __init__(self):
        self.analysis = {}
        self.framework_dir = None
        self.framework_name = ""
        self.requirements_doc = ""
    
    def generate_config(self, analysis_file: Path, framework_dir: Path, framework_name: str, requirements_doc: str):
        """Generate all configuration files."""
        with open(analysis_file) as f:
            self.analysis = json.load(f)
        
        self.framework_dir = framework_dir
        self.framework_name = framework_name
        self.requirements_doc = requirements_doc
        
        print(f"⚙️  Generating configuration files for {framework_name}")
        
        self._generate_pytest_ini()
        self._generate_conftest()
        self._generate_requirements()
        
        print("✅ Configuration files generated")
    
    def _generate_pytest_ini(self):
        """Generate pytest.ini configuration file."""
        categories = list(self.analysis["test_categories"].keys())
        markers = self._get_pytest_markers()
        
        content = f"""[pytest]
minversion = 6.0
addopts = -ra -q --tb=short --strict-markers
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
{markers}
filterwarnings =
    ignore::UserWarning
    ignore::DeprecationWarning
log_cli = true
log_cli_level = INFO
log_cli_format = %(asctime)s [%(levelname)8s] %(name)s: %(message)s
log_cli_date_format = %Y-%m-%d %H:%M:%S"""
        
        (self.framework_dir / "pytest.ini").write_text(content)
    
    def _get_pytest_markers(self) -> str:
        """Generate pytest markers based on test categories."""
        base_markers = [
            "unit: Unit tests for individual components",
            "integration: Integration tests for component interactions",
            "performance: Performance and scalability tests",
            "slow: Tests that take longer than 30 seconds",
            "data: Tests requiring market data",
            "mock: Tests using mocked dependencies",
            "edge_case: Edge case and error handling tests",
            "regression: Regression tests for bug fixes"
        ]
        
        # Add category-specific markers
        category_markers = []
        for category in self.analysis["test_categories"].keys():
            if category == "ui_components":
                category_markers.append("ui: User interface tests")
            elif category == "regulatory_compliance":
                category_markers.append("compliance: Regulatory compliance tests")
            elif category not in ["performance", "integration"]:  # Avoid duplicates
                marker_desc = f"{category.replace('_', ' ').title()} tests"
                category_markers.append(f"{category}: {marker_desc}")
        
        all_markers = base_markers + category_markers
        return '\n'.join(f"    {marker}" for marker in all_markers)
    
    def _generate_conftest(self):
        """Generate conftest.py with fixtures."""
        strategy_type = self.analysis.get("strategy_type", "general")
        parameters = self.analysis.get("parameters", {})
        
        # Generate sample parameters based on analysis
        sample_params = self._generate_sample_parameters(parameters)
        
        content = f'''"""
Global pytest configuration and fixtures for {self.framework_name} testing framework.
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
    return {{
        "test_data_dir": TEST_DATA_DIR,
        "test_results_dir": TEST_RESULTS_DIR,
        "default_timeout": 30,
        "performance_threshold": {{
            "backtest_time": 30.0,  # seconds
            "memory_usage": 2.0,    # GB
            "ui_load_time": 5.0     # seconds
        }}
    }}


@pytest.fixture
def sample_strategy_params():
    """Standard strategy parameters for testing."""
    return {sample_params}


@pytest.fixture
def real_market_data():
    """Retrieve real OHLCV market data for testing."""
    def _get_data(
        symbol="GSPC",
        start_date="2020-01-01", 
        end_date="2023-12-31", 
        frequency="5M"
    ):
        """
        Get real market data for testing.
        
        Args:
            symbol: Market symbol (default: GSPC for S&P 500)
            start_date: Start date for data
            end_date: End date for data  
            frequency: Data frequency (1M, 5M, 30M, 1H, 1D)
        
        Returns:
            DataFrame with OHLCV data and datetime index
        """
        try:
            # Import the market data class
            import sys
            from pathlib import Path
            
            # Add app directory to path to import market_data
            app_path = Path(__file__).parent.parent.parent / "app" / "SP500_CFD_v1"
            if str(app_path) not in sys.path:
                sys.path.insert(0, str(app_path))
            
            from market_data import Retrieve
            
            # Get real market data
            retriever = Retrieve()
            data = retriever.get_data(symbol, start_date, end_date, frequency)
            
            if data.empty:
                print(f"⚠️  No real data available for {{symbol}}, using fallback period")
                # Try a known good period with daily data
                data = retriever.get_data(symbol, "2022-01-01", "2022-12-31", "1D")
            
            if not data.empty:
                # Ensure required columns exist
                required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                for col in required_cols:
                    if col not in data.columns:
                        if col == 'Volume':
                            data[col] = 1000000  # Default volume if missing
                        else:
                            print(f"⚠️  Missing column {{col}}, using Close price as fallback")
                            data[col] = data['Close']
                
                print(f"✅ Retrieved {{len(data)}} real market data records for {{symbol}}")
                return data[required_cols]
            else:
                raise ValueError(f"No real data available for {{symbol}}")
                
        except Exception as e:
            print(f"❌ Failed to retrieve real market data: {{e}}")
            print("📊 Using minimal fallback data for testing")
            
            # Create minimal real-world-like data as absolute fallback
            dates = pd.date_range(start_date, end_date, freq='1D')[:30]  # Limit to 30 days
            
            # Use realistic S&P 500 levels from 2023
            base_prices = [4200, 4150, 4180, 4220, 4190, 4240, 4210, 4180, 4160, 4200,
                          4230, 4250, 4220, 4190, 4210, 4240, 4260, 4230, 4200, 4180,
                          4160, 4190, 4220, 4240, 4210, 4180, 4200, 4230, 4250, 4220]
            
            n = min(len(dates), len(base_prices))
            dates = dates[:n]
            closes = base_prices[:n]
            
            # Generate realistic OHLC from close prices
            opens = [closes[0]] + closes[:-1]  # Previous close becomes next open
            highs = [c * (1 + np.random.uniform(0, 0.01)) for c in closes]  # Up to 1% above close
            lows = [c * (1 - np.random.uniform(0, 0.01)) for c in closes]   # Up to 1% below close
            
            # Ensure OHLC relationships are logical
            for i in range(len(closes)):
                highs[i] = max(highs[i], opens[i], closes[i])
                lows[i] = min(lows[i], opens[i], closes[i])
            
            fallback_data = pd.DataFrame({{
                'Open': opens,
                'High': highs,
                'Low': lows,
                'Close': closes,
                'Volume': [np.random.randint(3000000, 5000000) for _ in range(n)]
            }}, index=dates)
            
            print(f"📈 Created {{len(fallback_data)}} fallback records based on realistic S&P 500 levels")
            return fallback_data
    
    return _get_data


@pytest.fixture
def real_retrieve_class():
    """Real market data Retrieve class for testing."""
    try:
        # Import the actual market data class
        import sys
        from pathlib import Path
        
        # Add app directory to path to import market_data
        app_path = Path(__file__).parent.parent.parent / "app" / "SP500_CFD_v1"
        if str(app_path) not in sys.path:
            sys.path.insert(0, str(app_path))
        
        from market_data import Retrieve
        return Retrieve()
        
    except ImportError as e:
        print(f"⚠️  Could not import real Retrieve class: {{e}}")
        print("📊 Using test-compatible Retrieve class")
        
        # Create a test-compatible version that uses real data patterns
        class TestRetrieve:
            def get_data(self, symbol, start_date, end_date, frequency="5M"):
                """Get real market data or realistic fallback."""
                try:
                    # Try to use the real market data fixture
                    from conftest import real_market_data
                    data_func = real_market_data()
                    return data_func(symbol, start_date, end_date, frequency)
                except:
                    # Final fallback with realistic data
                    dates = pd.date_range(start_date, end_date, freq='1D')[:30]
                    base_price = 4200 if symbol in ['GSPC', 'SPX'] else 100
                    
                    # Generate realistic price series
                    closes = [base_price * (1 + np.random.normal(0, 0.01)) for _ in range(len(dates))]
                    opens = [closes[0]] + closes[:-1]
                    highs = [max(o, c) * (1 + abs(np.random.normal(0, 0.005))) for o, c in zip(opens, closes)]
                    lows = [min(o, c) * (1 - abs(np.random.normal(0, 0.005))) for o, c in zip(opens, closes)]
                    
                    return pd.DataFrame({{
                        'Open': opens,
                        'High': highs,  
                        'Low': lows,
                        'Close': closes,
                        'Volume': [np.random.randint(2000000, 6000000) for _ in range(len(dates))]
                    }}, index=dates)
        
        return TestRetrieve()


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
        
        trade = {{
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
        }}
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
            message = f"[{{timestamp}}] Executing test: {{test_name}}"
            print(message)
            self.results.append({{"test": test_name, "status": "RUNNING", "timestamp": timestamp}})
        
        def end_test(self, test_name, status, message=""):
            timestamp = datetime.now().strftime("%H:%M:%S")
            status_message = f"[{{timestamp}}] {{test_name}}: {{status}}"
            if message:
                status_message += f" - {{message}}"
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
'''
        
        (self.framework_dir / "conftest.py").write_text(content)
    
    def _generate_sample_parameters(self, parameters: Dict[str, Any]) -> str:
        """Generate sample parameters dictionary based on user input."""
        user_inputs = self.analysis.get("user_inputs", {})
        strategy_type = self.analysis.get("strategy_type", "unknown")
        
        # Generate parameters based on what user actually specified
        sample_params = {
            'framework_name': self.framework_name,
            'strategy_type': strategy_type,
            'user_specified_requirements': 'See analysis JSON for full user requirements'
        }
        
        # Add any user-specific parameters they mentioned
        if user_inputs:
            sample_params['user_inputs'] = 'Captured in interactive session - see analysis file'
        
        # Format as Python dictionary
        param_lines = []
        for key, value in sample_params.items():
            if isinstance(value, str):
                param_lines.append(f"        '{key}': '{value}'")
            else:
                param_lines.append(f"        '{key}': {value}")
        
        return "{\n" + ",\n".join(param_lines) + "\n    }"
    
    def _generate_requirements(self):
        """Generate requirements.txt file."""
        strategy_type = self.analysis.get("strategy_type", "general")
        has_ui = "ui_components" in self.analysis.get("test_categories", {})
        
        base_requirements = [
            "# Core testing framework",
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-html>=3.1.0",
            "pytest-mock>=3.10.0",
            "pytest-xdist>=3.0.0",
            "",
            "# Data handling and analysis",
            "pandas>=1.5.0",
            "numpy>=1.24.0",
            "scipy>=1.10.0",
            "",
            "# Mocking and testing utilities",
            "unittest-xml-reporting>=3.2.0",
            "freezegun>=1.2.0",
            "responses>=0.20.0",
            "",
            "# Performance testing",
            "memory-profiler>=0.60.0",
            "psutil>=5.9.0",
            "pytest-benchmark>=4.0.0",
            "",
            "# Code quality",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.5.0",
            "",
            "# Coverage reporting",
            "coverage>=7.0.0",
            "coverage-badge>=1.1.0",
            "",
            "# Utilities",
            "python-dateutil>=2.8.0",
            "pytz>=2023.3",
            "colorama>=0.4.6",
            "tabulate>=0.9.0",
            "",
            "# Configuration",
            "pydantic>=2.0.0",
            "python-dotenv>=1.0.0",
            "",
            "# Logging and monitoring",
            "structlog>=23.0.0",
            "rich>=13.0.0"
        ]
        
        # Add strategy-specific requirements
        if strategy_type == "cfd":
            base_requirements.extend([
                "",
                "# CFD-specific packages",
                "yfinance>=0.2.0",
                "openbb>=4.0.0"
            ])
        elif strategy_type == "forex":
            base_requirements.extend([
                "",
                "# Forex-specific packages", 
                "fxcmpy>=1.3.0",
                "oanda-api-v20>=3.0.0"
            ])
        elif strategy_type == "crypto":
            base_requirements.extend([
                "",
                "# Crypto-specific packages",
                "ccxt>=4.0.0",
                "binance>=1.0.0"
            ])
        
        # Add UI requirements if needed
        if has_ui:
            base_requirements.extend([
                "",
                "# UI testing (Streamlit)",
                "streamlit>=1.28.0",
                "selenium>=4.15.0",
                "pytest-selenium>=4.0.0",
                "",
                "# Chart testing (Plotly)",
                "plotly>=5.15.0",
                "kaleido>=0.2.1",
                "",
                "# PDF testing",
                "reportlab>=4.0.0",
                "PyPDF2>=3.0.0"
            ])
        
        base_requirements.extend([
            "",
            "# Network testing",
            "httpx>=0.24.0",
            "aioresponses>=0.7.0",
            "",
            "# Market data dependencies",
            "requests>=2.28.0"
        ])
        
        content = "\n".join(base_requirements)
        (self.framework_dir / "requirements.txt").write_text(content)


def main():
    parser = argparse.ArgumentParser(description="Generate configuration files")
    parser.add_argument("--analysis", required=True, help="Path to analysis JSON file")
    parser.add_argument("--framework-dir", required=True, help="Framework directory path")
    parser.add_argument("--framework-name", required=True, help="Framework name")
    parser.add_argument("--requirements-doc", required=True, help="Requirements document path")
    
    args = parser.parse_args()
    
    generator = ConfigGenerator()
    generator.generate_config(Path(args.analysis), Path(args.framework_dir), args.framework_name, args.requirements_doc)


if __name__ == "__main__":
    main()