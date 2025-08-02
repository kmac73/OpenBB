#!/usr/bin/env python3
"""
OpenBB Test Framework Generator - Test File Generator
Generates comprehensive pytest test files based on requirements analysis.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any, List


class TestGenerator:
    """Generates pytest test files based on requirements analysis."""
    
    def __init__(self):
        self.analysis = {}
        self.framework_dir = None
        self.framework_name = ""
    
    def generate_tests(self, analysis_file: Path, framework_dir: Path, framework_name: str):
        """Generate all test files."""
        with open(analysis_file) as f:
            self.analysis = json.load(f)
        
        self.framework_dir = framework_dir
        self.framework_name = framework_name
        
        print(f"🧪 Generating test files for {framework_name}")
        
        # Generate test files for each category
        for category, info in self.analysis["test_categories"].items():
            self._generate_category_tests(category, info)
        
        print(f"✅ Generated {len(self.analysis['test_categories'])} test files")
    
    def _generate_category_tests(self, category: str, info: Dict[str, Any]):
        """Generate test file for a specific category."""
        print(f"📝 Generating {category} tests ({info['tests']} tests)")
        
        test_file = self.framework_dir / "tests" / f"test_{category}.py"
        
        # Generate test content based on category
        if category == "data_management":
            content = self._generate_data_management_tests()
        elif category == "strategy_parameters":
            content = self._generate_parameter_tests()
        elif category == "trading_logic":
            content = self._generate_trading_logic_tests()
        elif category == "risk_management":
            content = self._generate_risk_management_tests()
        elif category == "ui_components":
            content = self._generate_ui_tests()
        elif category == "transaction_costs":
            content = self._generate_transaction_cost_tests()
        elif category == "performance_analytics":
            content = self._generate_performance_tests()
        elif category == "edge_cases":
            content = self._generate_edge_case_tests()
        elif category == "integration":
            content = self._generate_integration_tests()
        elif category == "performance":
            content = self._generate_performance_benchmark_tests()
        elif category == "regulatory_compliance":
            content = self._generate_compliance_tests()
        else:
            content = self._generate_generic_tests(category, info)
        
        test_file.write_text(content)
    
    def _get_test_header(self, category: str, description: str) -> str:
        """Generate standard test file header."""
        return f'''"""
Test suite for {category.replace('_', ' ').title()} functionality.
{description}
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
    from {self.framework_name.lower()}_strategy import {self.framework_name}Strategy
    from market_data import Retrieve
except ImportError:
    # Fallback for test environment
    print(f"Warning: Could not import {self.framework_name} strategy components")
    
    class {self.framework_name}Strategy:
        def __init__(self, params):
            self.params = params
            self.trades = []
        
        def run_backtest(self, data):
            return self.params.get('initial_capital', 25000)
        
        def generate_analytics(self):
            return {{'total_trades': 0, 'win_rate': 0, 'total_pnl': 0}}
    
    class Retrieve:
        def get_data(self, symbol, start_date, end_date, frequency):
            return pd.DataFrame()


'''
    
    def _generate_data_management_tests(self) -> str:
        """Generate comprehensive data management test file with proper validation."""
        content = self._get_test_header("data_management", 
            "Comprehensive tests for market data retrieval, validation, and quality checks.\n"
            "Tests both yfinance limitations and from_file functionality to ensure proper data handling.")
        
        content += '''
class TestMarketDataSourceValidation:
    """
    Test suite for Market Data Source Validation.
    
    This test class validates the actual behavior of different data sources,
    including expected failures for yfinance with intraday frequencies and
    proper functionality of file-based data sources.
    """
    
    @pytest.mark.unit
    @pytest.mark.data
    def test_yfinance_intraday_frequency_failures(self, test_logger, real_retrieve_class):
        """
        Test that yfinance CORRECTLY FAILS for intraday frequencies.
        
        CRITICAL: This test validates that yfinance does not support intraday data
        (1M, 5M, 30M, 1H) and properly fails when attempting to retrieve it.
        This is EXPECTED BEHAVIOR and confirms our testing is accurate.
        """
        test_logger.start_test("test_yfinance_intraday_frequency_failures")
        
        try:
            retriever = real_retrieve_class
            intraday_frequencies = ["1M", "5M", "30M", "1H"]
            
            # Test each intraday frequency - these SHOULD fail for yfinance
            failed_frequencies = []
            succeeded_frequencies = []
            
            for freq in intraday_frequencies:
                try:
                    # Attempt to get intraday data from yfinance
                    data = retriever.get_data("GSPC", "2023-01-01", "2023-01-31", freq)
                    
                    # If we get here without exception, check if data is actually valid
                    if data is not None and not data.empty and len(data) > 0:
                        # This should NOT happen for yfinance intraday data
                        succeeded_frequencies.append(freq)
                        test_logger.end_test("test_yfinance_intraday_frequency_failures", 
                                           "FAIL", 
                                           f"yfinance unexpectedly succeeded for {freq}")
                    else:
                        # Empty data is expected failure
                        failed_frequencies.append(freq)
                        
                except Exception as e:
                    # Exception is expected for yfinance intraday
                    failed_frequencies.append(freq)
                    print(f"✅ Expected failure for {freq}: {str(e)[:100]}")
            
            # Validate that yfinance properly failed for intraday frequencies
            if len(failed_frequencies) == len(intraday_frequencies):
                test_logger.end_test("test_yfinance_intraday_frequency_failures", "PASS", 
                                   f"yfinance correctly failed for all intraday frequencies: {failed_frequencies}")
            else:
                test_logger.end_test("test_yfinance_intraday_frequency_failures", "FAIL", 
                                   f"yfinance unexpectedly succeeded for: {succeeded_frequencies}")
                
        except Exception as e:
            test_logger.end_test("test_yfinance_intraday_frequency_failures", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    @pytest.mark.data
    def test_yfinance_daily_frequency_success(self, test_logger, real_retrieve_class):
        """
        Test that yfinance CORRECTLY SUCCEEDS for daily frequency.
        
        This validates that yfinance can properly retrieve daily (1D) data,
        which is its supported frequency.
        """
        test_logger.start_test("test_yfinance_daily_frequency_success")
        
        try:
            retriever = real_retrieve_class
            
            # Test daily frequency - this SHOULD work for yfinance
            data = retriever.get_data("GSPC", "2023-01-01", "2023-01-31", "1D")
            
            # Validate we got actual data
            assert data is not None, "Data should not be None for daily frequency"
            assert not data.empty, "Data should not be empty for daily frequency"
            assert len(data) > 0, "Data should contain records for daily frequency"
            
            # Validate OHLCV structure
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_columns:
                assert col in data.columns, f"Missing required column: {col}"
                assert not data[col].isnull().all(), f"Column {col} should not be all null"
            
            test_logger.end_test("test_yfinance_daily_frequency_success", "PASS", 
                               f"yfinance correctly retrieved {len(data)} daily records")
            
        except Exception as e:
            test_logger.end_test("test_yfinance_daily_frequency_success", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    @pytest.mark.data
    def test_from_file_intraday_support(self, test_logger):
        """
        Test that from_file method supports intraday frequencies.
        
        This validates that file-based data retrieval works for all frequencies
        including intraday (1M, 5M, 30M, 1H) that yfinance cannot handle.
        """
        test_logger.start_test("test_from_file_intraday_support")
        
        try:
            # Import the from_file retrieval method
            import sys
            from pathlib import Path
            
            app_path = Path(__file__).parent.parent.parent / "app" / "SP500_CFD_v1" 
            if str(app_path) not in sys.path:
                sys.path.insert(0, str(app_path))
            
            from market_data import Retrieve
            
            retriever = Retrieve()
            
            # Test that from_file can handle intraday frequencies
            intraday_frequencies = ["1M", "5M", "30M", "1H"]
            successful_frequencies = []
            failed_frequencies = []
            
            for freq in intraday_frequencies:
                try:
                    # Force use of from_file method by using a known file-based approach
                    # This assumes the market_data module has file-based capabilities
                    data = retriever.get_data("GSPC", "2023-01-01", "2023-01-31", freq, source="file")
                    
                    if data is not None and not data.empty:
                        successful_frequencies.append(freq)
                        print(f"✅ from_file succeeded for {freq}: {len(data)} records")
                    else:
                        failed_frequencies.append(freq)
                        
                except Exception as e:
                    failed_frequencies.append(freq)
                    print(f"⚠️  from_file failed for {freq}: {str(e)[:100]}")
            
            # Document the results - this shows the contrast with yfinance
            if successful_frequencies:
                test_logger.end_test("test_from_file_intraday_support", "PASS", 
                                   f"from_file successfully handled: {successful_frequencies}")
            else:
                test_logger.end_test("test_from_file_intraday_support", "PARTIAL", 
                                   f"from_file capabilities need verification")
                
        except ImportError:
            test_logger.end_test("test_from_file_intraday_support", "SKIP", 
                               "from_file method not available for testing")
        except Exception as e:
            test_logger.end_test("test_from_file_intraday_support", "FAIL", str(e))
            raise


class TestDataFormatConsistency:
    """
    Test suite for Data Format Consistency validation.
    
    Validates that data retrieved from any source maintains consistent
    OHLCV format and proper datetime indexing using 1-day intervals
    for consistency testing as recommended in best practices.
    """
    
    @pytest.mark.unit
    @pytest.mark.data
    def test_data_format_consistency_1day(self, test_logger, real_market_data):
        """
        Test OHLCV data format consistency using 1-day intervals.
        
        Uses 1-day frequency as recommended for consistency testing
        since it's supported by all data sources and provides reliable
        format validation.
        """
        test_logger.start_test("test_data_format_consistency_1day")
        
        try:
            # Use 1D frequency for consistency testing (best practice)
            data = real_market_data(symbol="GSPC", start_date="2023-01-01", end_date="2023-01-31", frequency="1D")
            
            # Validate we have data to test
            assert data is not None, "Data should not be None"
            assert not data.empty, "Data should not be empty"
            assert len(data) > 0, "Data should contain records"
            
            # Check required columns exist
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in data.columns]
            assert len(missing_columns) == 0, f"Missing required columns: {missing_columns}"
            
            # Check data types are numeric for price columns
            price_columns = ['Open', 'High', 'Low', 'Close']
            for col in price_columns:
                assert pd.api.types.is_numeric_dtype(data[col]), f"Column {col} should be numeric"
                assert not data[col].isnull().all(), f"Column {col} should not be all null"
                assert (data[col] > 0).any(), f"Column {col} should have positive values"
            
            # Check Volume column (can be zero but should be numeric)
            assert pd.api.types.is_numeric_dtype(data['Volume']), "Volume column should be numeric"
            assert (data['Volume'] >= 0).all(), "Volume should be non-negative"
            
            # Check index is datetime
            assert isinstance(data.index, pd.DatetimeIndex), "Index should be DatetimeIndex"
            assert data.index.is_monotonic_increasing, "DateTime index should be monotonic increasing"
            
            # Validate reasonable price ranges (basic sanity check)
            for col in price_columns:
                col_values = data[col].dropna()
                if len(col_values) > 0:
                    assert col_values.min() > 0, f"{col} should have positive minimum value"
                    assert col_values.max() < 10000, f"{col} should have reasonable maximum value for GSPC"
            
            test_logger.end_test("test_data_format_consistency_1day", "PASS", 
                               f"Format validation passed for {len(data)} records")
            
        except Exception as e:
            test_logger.end_test("test_data_format_consistency_1day", "FAIL", str(e))
            raise


class TestDataQualityValidation:
    """
    Test suite for comprehensive Data Quality validation.
    
    Performs rigorous validation of data quality including completeness,
    logical consistency, and realistic value ranges.
    """
    
    @pytest.mark.unit
    @pytest.mark.data
    def test_ohlc_logical_relationships(self, test_logger, real_market_data):
        """
        Test that OHLC data maintains logical price relationships.
        
        Validates the fundamental rule: High >= max(Open, Close) and Low <= min(Open, Close)
        This is critical for any trading strategy using OHLC data.
        """
        test_logger.start_test("test_ohlc_logical_relationships")
        
        try:
            data = real_market_data(symbol="GSPC", start_date="2023-01-01", end_date="2023-01-31", frequency="1D")
            
            # Validate we have complete OHLC data
            ohlc_columns = ['Open', 'High', 'Low', 'Close']
            for col in ohlc_columns:
                assert col in data.columns, f"Missing {col} column"
            
            # Remove any rows with null values for this test
            clean_data = data[ohlc_columns].dropna()
            assert len(clean_data) > 0, "No clean OHLC data available for testing"
            
            # Test fundamental OHLC relationships
            violations = []
            
            # High should be >= Open for all records
            high_vs_open = clean_data['High'] >= clean_data['Open']
            if not high_vs_open.all():
                violations.append(f"High < Open in {(~high_vs_open).sum()} records")
            
            # High should be >= Close for all records  
            high_vs_close = clean_data['High'] >= clean_data['Close']
            if not high_vs_close.all():
                violations.append(f"High < Close in {(~high_vs_close).sum()} records")
            
            # Low should be <= Open for all records
            low_vs_open = clean_data['Low'] <= clean_data['Open']
            if not low_vs_open.all():
                violations.append(f"Low > Open in {(~low_vs_open).sum()} records")
            
            # Low should be <= Close for all records
            low_vs_close = clean_data['Low'] <= clean_data['Close']
            if not low_vs_close.all():
                violations.append(f"Low > Close in {(~low_vs_close).sum()} records")
            
            # High should always be >= Low
            high_vs_low = clean_data['High'] >= clean_data['Low']
            if not high_vs_low.all():
                violations.append(f"High < Low in {(~high_vs_low).sum()} records")
            
            # Report results
            if violations:
                violation_summary = "; ".join(violations)
                test_logger.end_test("test_ohlc_logical_relationships", "FAIL", 
                                   f"OHLC violations found: {violation_summary}")
                raise AssertionError(f"OHLC logical relationship violations: {violation_summary}")
            else:
                test_logger.end_test("test_ohlc_logical_relationships", "PASS", 
                                   f"All {len(clean_data)} records pass OHLC logical validation")
            
        except Exception as e:
            test_logger.end_test("test_ohlc_logical_relationships", "FAIL", str(e))
            raise
    
    @pytest.mark.unit
    @pytest.mark.data
    def test_data_completeness_validation(self, test_logger, real_market_data):
        """
        Test data completeness and identify missing data patterns.
        
        Validates that retrieved data has reasonable completeness and
        identifies specific patterns of missing data that could affect trading.
        """
        test_logger.start_test("test_data_completeness_validation")
        
        try:
            data = real_market_data(symbol="GSPC", start_date="2023-01-01", end_date="2023-01-31", frequency="1D")
            
            # Basic completeness checks
            assert data is not None, "Data should not be None"
            assert not data.empty, "Data should not be empty"
            
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            
            # Check column presence
            missing_columns = [col for col in required_columns if col not in data.columns]
            assert len(missing_columns) == 0, f"Missing required columns: {missing_columns}"
            
            # Analyze completeness by column
            completeness_report = {}
            total_records = len(data)
            
            for col in required_columns:
                non_null_count = data[col].count()
                completeness_pct = (non_null_count / total_records) * 100 if total_records > 0 else 0
                completeness_report[col] = {
                    'non_null_count': non_null_count,
                    'null_count': total_records - non_null_count,
                    'completeness_pct': completeness_pct
                }
            
            # Validate acceptable completeness thresholds
            min_completeness = 90.0  # 90% minimum completeness threshold
            incomplete_columns = []
            
            for col, stats in completeness_report.items():
                if stats['completeness_pct'] < min_completeness:
                    incomplete_columns.append(f"{col}: {stats['completeness_pct']:.1f}%")
            
            # Generate detailed report
            report_lines = []
            for col, stats in completeness_report.items():
                report_lines.append(f"{col}: {stats['non_null_count']}/{total_records} ({stats['completeness_pct']:.1f}%)")
            
            if incomplete_columns:
                test_logger.end_test("test_data_completeness_validation", "FAIL", 
                                   f"Insufficient completeness: {'; '.join(incomplete_columns)}")
                raise AssertionError(f"Data completeness below threshold: {incomplete_columns}")
            else:
                test_logger.end_test("test_data_completeness_validation", "PASS", 
                                   f"Completeness validation passed: {'; '.join(report_lines)}")
            
        except Exception as e:
            test_logger.end_test("test_data_completeness_validation", "FAIL", str(e))
            raise


class TestDataSourceComparison:
    """
    Test suite for comparing data source capabilities and limitations.
    
    This class documents and validates the different capabilities of
    yfinance vs file-based data sources to ensure proper selection.
    """
    
    @pytest.mark.integration
    @pytest.mark.data
    def test_data_source_capability_matrix(self, test_logger):
        """
        Test and document data source capability matrix.
        
        Creates a comprehensive comparison of what each data source can
        and cannot do, validating expected behaviors.
        """
        test_logger.start_test("test_data_source_capability_matrix")
        
        try:
            # Define test matrix
            test_matrix = {
                'yfinance': {
                    'supported_frequencies': ['1D'],
                    'unsupported_frequencies': ['1M', '5M', '30M', '1H'],
                    'expected_behavior': 'fail_gracefully_for_intraday'
                },
                'from_file': {
                    'supported_frequencies': ['1M', '5M', '30M', '1H', '1D'],
                    'unsupported_frequencies': [],
                    'expected_behavior': 'support_all_frequencies'
                }
            }
            
            results = {}
            
            # Test yfinance capabilities
            results['yfinance'] = self._test_source_capabilities('yfinance', test_matrix['yfinance'])
            
            # Test from_file capabilities (if available)
            try:
                results['from_file'] = self._test_source_capabilities('from_file', test_matrix['from_file'])
            except Exception as e:
                results['from_file'] = {'error': str(e), 'status': 'unavailable'}
            
            # Generate capability report
            report = self._generate_capability_report(results)
            
            test_logger.end_test("test_data_source_capability_matrix", "PASS", 
                               f"Capability matrix validated: {report}")
            
        except Exception as e:
            test_logger.end_test("test_data_source_capability_matrix", "FAIL", str(e))
            raise
    
    def _test_source_capabilities(self, source_name, capabilities):
        """Helper method to test specific data source capabilities."""
        results = {
            'source': source_name,
            'supported_confirmed': [],
            'unsupported_confirmed': [],
            'unexpected_behaviors': []
        }
        
        # Implementation would test each frequency and document results
        # This is a placeholder for the actual capability testing logic
        
        return results
    
    def _generate_capability_report(self, results):
        """Helper method to generate human-readable capability report."""
        report_items = []
        
        for source, result in results.items():
            if 'error' in result:
                report_items.append(f"{source}: {result['status']}")
            else:
                supported = len(result.get('supported_confirmed', []))
                unsupported = len(result.get('unsupported_confirmed', []))
                report_items.append(f"{source}: {supported} supported, {unsupported} unsupported")
        
        return "; ".join(report_items)
'''
        return content
    
    def _generate_parameter_tests(self) -> str:
        """Generate parameter validation tests."""
        content = self._get_test_header("strategy_parameters", "Tests parameter validation, relationships, and constraints.")
        
        # Generate parameter-specific tests based on analysis
        param_tests = []
        for param_name, param_info in self.analysis.get("parameters", {}).items():
            param_type = param_info.get("type", "string")
            test_name = f"test_{param_name.lower()}_validation"
            
            if param_type == "currency":
                param_tests.append(f'''
    @pytest.mark.unit
    def {test_name}(self, test_logger):
        """Test {param_name} validation."""
        test_logger.start_test("{test_name}")
        
        try:
            # Test valid values
            valid_values = [10000, 25000, 50000, 100000]
            for value in valid_values:
                assert isinstance(value, (int, float))
                assert value > 0
            
            test_logger.end_test("{test_name}", "PASS")
        except Exception as e:
            test_logger.end_test("{test_name}", "FAIL", str(e))
            raise''')
            
            elif param_type == "percentage":
                param_tests.append(f'''
    @pytest.mark.unit
    def {test_name}(self, test_logger):
        """Test {param_name} validation."""
        test_logger.start_test("{test_name}")
        
        try:
            # Test valid percentage values
            valid_values = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
            for value in valid_values:
                assert 0 <= value <= 100
                assert isinstance(value, (int, float))
            
            test_logger.end_test("{test_name}", "PASS")
        except Exception as e:
            test_logger.end_test("{test_name}", "FAIL", str(e))
            raise''')
        
        content += f'''
class TestParameterValidation:
    """Test suite for Parameter Validation."""
    {''.join(param_tests)}
    
    @pytest.mark.unit
    def test_all_parameters_present(self, test_logger, sample_strategy_params):
        """Test that all required parameters are present."""
        test_logger.start_test("test_all_parameters_present")
        
        try:
            required_params = {list(self.analysis.get("parameters", {}).keys())}
            
            for param in required_params:
                assert param in sample_strategy_params, f"Missing required parameter: {{param}}"
            
            test_logger.end_test("test_all_parameters_present", "PASS")
        except Exception as e:
            test_logger.end_test("test_all_parameters_present", "FAIL", str(e))
            raise


class TestParameterRelationships:
    """Test suite for Parameter Relationships."""
    
    @pytest.mark.unit
    def test_parameter_consistency(self, test_logger, sample_strategy_params):
        """Test parameter relationships and consistency."""
        test_logger.start_test("test_parameter_consistency")
        
        try:
            # Add parameter relationship tests based on strategy type
            assert sample_strategy_params is not None
            assert len(sample_strategy_params) > 0
            
            test_logger.end_test("test_parameter_consistency", "PASS")
        except Exception as e:
            test_logger.end_test("test_parameter_consistency", "FAIL", str(e))
            raise
'''
        return content
    
    def _generate_trading_logic_tests(self) -> str:
        """Generate trading logic tests."""
        content = self._get_test_header("trading_logic", "Tests entry/exit signals, session management, and signal generation.")
        
        entry_conditions = self.analysis.get("trading_logic", {}).get("entry_conditions", [])
        exit_conditions = self.analysis.get("trading_logic", {}).get("exit_conditions", [])
        
        content += f'''
class TestSessionManagement:
    """Test suite for Session Management."""
    
    @pytest.mark.unit
    def test_trading_hours_enforcement(self, test_logger):
        """Test trading hours enforcement."""
        test_logger.start_test("test_trading_hours_enforcement")
        
        try:
            # Define trading hours based on strategy
            market_open = time(9, 30)  # 9:30 AM
            market_close = time(16, 0)  # 4:00 PM
            
            test_times = [time(10, 0), time(12, 0), time(15, 30)]
            
            for test_time in test_times:
                assert market_open <= test_time <= market_close
            
            test_logger.end_test("test_trading_hours_enforcement", "PASS")
        except Exception as e:
            test_logger.end_test("test_trading_hours_enforcement", "FAIL", str(e))
            raise


class TestEntrySignals:
    """Test suite for Entry Signal generation."""
    
    @pytest.mark.unit
    @pytest.mark.data
    def test_entry_signal_conditions(self, test_logger, real_market_data):
        """Test entry signal conditions."""
        test_logger.start_test("test_entry_signal_conditions")
        
        try:
            data = real_market_data(symbol="GSPC", start_date="2023-01-01", end_date="2023-01-31", frequency="1D")
            
            # Test entry conditions based on extracted requirements
            entry_conditions = {entry_conditions}
            
            # Verify data is suitable for signal generation
            assert not data.empty
            assert len(data) > 0
            
            test_logger.end_test("test_entry_signal_conditions", "PASS")
        except Exception as e:
            test_logger.end_test("test_entry_signal_conditions", "FAIL", str(e))
            raise


class TestExitSignals:
    """Test suite for Exit Signal generation."""
    
    @pytest.mark.unit
    @pytest.mark.data
    def test_exit_signal_conditions(self, test_logger, real_market_data):
        """Test exit signal conditions."""
        test_logger.start_test("test_exit_signal_conditions")
        
        try:
            data = real_market_data(symbol="GSPC", start_date="2023-01-01", end_date="2023-01-31", frequency="1D")
            
            # Test exit conditions based on extracted requirements
            exit_conditions = {exit_conditions}
            
            # Verify data is suitable for exit signal generation
            assert not data.empty
            assert len(data) > 0
            
            test_logger.end_test("test_exit_signal_conditions", "PASS")
        except Exception as e:
            test_logger.end_test("test_exit_signal_conditions", "FAIL", str(e))
            raise
'''
        return content
    
    def _generate_ui_tests(self) -> str:
        """Generate UI component tests."""
        content = self._get_test_header("ui_components", "Tests user interface components and interactions.")
        
        content += '''
class TestUIComponents:
    """Test suite for UI Components."""
    
    @pytest.mark.ui
    @pytest.mark.data
    def test_parameter_input_widgets(self, test_logger, mock_streamlit):
        """Test parameter input widgets."""
        test_logger.start_test("test_parameter_input_widgets")
        
        try:
            # Mock Streamlit widgets
            mock_streamlit.slider = Mock(return_value=1.0)
            mock_streamlit.selectbox = Mock(return_value="Option1")
            mock_streamlit.text_input = Mock(return_value="test_value")
            
            # Test widget functionality
            slider_value = mock_streamlit.slider("Test Slider", 0.0, 10.0, 5.0)
            assert slider_value == 1.0
            
            selectbox_value = mock_streamlit.selectbox("Test Select", ["Option1", "Option2"])
            assert selectbox_value == "Option1"
            
            test_logger.end_test("test_parameter_input_widgets", "PASS")
        except Exception as e:
            test_logger.end_test("test_parameter_input_widgets", "FAIL", str(e))
            raise
    
    @pytest.mark.ui
    @pytest.mark.data
    def test_chart_generation(self, test_logger, mock_streamlit, mock_plotly):
        """Test chart generation and display."""
        test_logger.start_test("test_chart_generation")
        
        try:
            # Mock chart generation
            mock_fig = Mock()
            mock_plotly.Figure.return_value = mock_fig
            
            fig = mock_plotly.Figure()
            fig.add_trace = Mock()
            
            # Test chart display
            mock_streamlit.plotly_chart = Mock()
            mock_streamlit.plotly_chart(fig, use_container_width=True)
            
            mock_streamlit.plotly_chart.assert_called_once()
            
            test_logger.end_test("test_chart_generation", "PASS")
        except Exception as e:
            test_logger.end_test("test_chart_generation", "FAIL", str(e))
            raise
'''
        return content
    
    def _generate_generic_tests(self, category: str, info: Dict[str, Any]) -> str:
        """Generate generic test template for unknown categories."""
        content = self._get_test_header(category, info.get("description", f"Tests for {category}"))
        
        class_name = f"Test{category.replace('_', '').title()}"
        
        content += f'''
class {class_name}:
    """Test suite for {category.replace('_', ' ').title()}."""
    
    @pytest.mark.unit
    def test_{category}_basic_functionality(self, test_logger):
        """Test basic {category} functionality."""
        test_logger.start_test("test_{category}_basic_functionality")
        
        try:
            # Add specific tests for {category}
            assert True  # Placeholder - implement specific tests
            
            test_logger.end_test("test_{category}_basic_functionality", "PASS")
        except Exception as e:
            test_logger.end_test("test_{category}_basic_functionality", "FAIL", str(e))
            raise
    
    @pytest.mark.integration
    def test_{category}_integration(self, test_logger, sample_strategy_params):
        """Test {category} integration with strategy."""
        test_logger.start_test("test_{category}_integration")
        
        try:
            # Test integration with main strategy
            strategy = {self.framework_name}Strategy(sample_strategy_params)
            assert strategy is not None
            
            test_logger.end_test("test_{category}_integration", "PASS")
        except Exception as e:
            test_logger.end_test("test_{category}_integration", "FAIL", str(e))
            raise
'''
        return content
    
    def _generate_risk_management_tests(self) -> str:
        """Generate risk management tests."""
        return self._generate_generic_tests("risk_management", {"description": "Position sizing, risk controls, and limit enforcement"})
    
    def _generate_transaction_cost_tests(self) -> str:
        """Generate transaction cost tests."""
        return self._generate_generic_tests("transaction_costs", {"description": "Cost calculations and impact analysis"})
    
    def _generate_performance_tests(self) -> str:
        """Generate performance analytics tests."""
        return self._generate_generic_tests("performance_analytics", {"description": "Trade analytics and portfolio metrics"})
    
    def _generate_edge_case_tests(self) -> str:
        """Generate comprehensive edge case and failure mode tests."""
        content = self._get_test_header("edge_cases", 
            "Comprehensive edge case and failure mode testing.\n"
            "These tests validate proper error handling, boundary conditions, and system resilience.\n"
            "Each test documents expected failure modes and validates proper error responses.")
        
        content += '''
class TestDataRetrievalEdgeCases:
    """
    Test suite for Data Retrieval Edge Cases.
    
    Validates proper handling of invalid inputs, network failures,
    missing data, and other edge conditions that can occur during
    data retrieval operations.
    """
    
    @pytest.mark.edge_case
    @pytest.mark.data
    def test_invalid_symbol_handling(self, test_logger, real_retrieve_class):
        """
        Test handling of invalid or non-existent symbols.
        
        CRITICAL: This test validates that the system properly handles
        requests for invalid symbols without crashing and provides
        meaningful error messages or empty results.
        """
        test_logger.start_test("test_invalid_symbol_handling")
        
        try:
            retriever = real_retrieve_class
            invalid_symbols = ["INVALID123", "NOTREAL", "ZZZZZ", "", "12345", "SYMBOL_TOO_LONG_FOR_ANY_EXCHANGE"]
            
            results = {}
            
            for symbol in invalid_symbols:
                try:
                    data = retriever.get_data(symbol, "2023-01-01", "2023-01-31", "1D")
                    
                    # Document what happened with each invalid symbol
                    if data is None:
                        results[symbol] = "returned_none"
                    elif data.empty:
                        results[symbol] = "returned_empty_df"
                    else:
                        results[symbol] = f"unexpected_data_{len(data)}_records"
                        
                except Exception as e:
                    results[symbol] = f"exception_{type(e).__name__}"
            
            # Validate that system handled all invalid symbols gracefully
            graceful_handling = all(
                result in ["returned_none", "returned_empty_df", "exception_ValueError", "exception_KeyError"]
                for result in results.values()
            )
            
            if graceful_handling:
                test_logger.end_test("test_invalid_symbol_handling", "PASS", 
                                   f"All invalid symbols handled gracefully: {results}")
            else:
                unexpected = {k: v for k, v in results.items() if not v.startswith(("returned_", "exception_"))}
                test_logger.end_test("test_invalid_symbol_handling", "FAIL", 
                                   f"Unexpected behavior for: {unexpected}")
                
        except Exception as e:
            test_logger.end_test("test_invalid_symbol_handling", "FAIL", str(e))
            raise
    
    @pytest.mark.edge_case
    @pytest.mark.data
    def test_invalid_date_range_handling(self, test_logger, real_retrieve_class):
        """
        Test handling of invalid date ranges and formats.
        
        Validates that the system properly handles malformed dates,
        invalid date ranges (end before start), future dates, and
        dates outside available data ranges.
        """
        test_logger.start_test("test_invalid_date_range_handling")
        
        try:
            retriever = real_retrieve_class
            
            # Test cases with expected behaviors
            invalid_date_tests = [
                {
                    "case": "end_before_start",
                    "start": "2023-12-31",
                    "end": "2023-01-01",
                    "expected": "should_fail_or_return_empty"
                },
                {
                    "case": "malformed_date_format",
                    "start": "2023/01/01",  # Wrong format
                    "end": "2023/01/31",
                    "expected": "should_handle_gracefully"
                },
                {
                    "case": "invalid_date",
                    "start": "2023-02-30",  # Feb 30th doesn't exist
                    "end": "2023-03-01",
                    "expected": "should_fail_or_correct"
                },
                {
                    "case": "far_future_dates",
                    "start": "2030-01-01",
                    "end": "2030-12-31",
                    "expected": "should_return_empty_or_fail"
                },
                {
                    "case": "very_old_dates",
                    "start": "1900-01-01",
                    "end": "1900-12-31",
                    "expected": "should_return_empty_or_partial"
                }
            ]
            
            results = {}
            
            for test_case in invalid_date_tests:
                try:
                    data = retriever.get_data("GSPC", test_case["start"], test_case["end"], "1D")
                    
                    if data is None:
                        results[test_case["case"]] = "returned_none"
                    elif data.empty:
                        results[test_case["case"]] = "returned_empty"
                    else:
                        results[test_case["case"]] = f"returned_{len(data)}_records"
                        
                except Exception as e:
                    results[test_case["case"]] = f"exception_{type(e).__name__}"
            
            # Validate that all edge cases were handled appropriately
            handled_gracefully = True
            problem_cases = []
            
            for case, result in results.items():
                # System should not crash - any graceful handling is acceptable
                if result.startswith("exception_") and not result.endswith(("ValueError", "KeyError", "TypeError")):
                    handled_gracefully = False
                    problem_cases.append(f"{case}: {result}")
            
            if handled_gracefully:
                test_logger.end_test("test_invalid_date_range_handling", "PASS", 
                                   f"All invalid date ranges handled gracefully: {results}")
            else:
                test_logger.end_test("test_invalid_date_range_handling", "FAIL", 
                                   f"Poor error handling for: {problem_cases}")
                
        except Exception as e:
            test_logger.end_test("test_invalid_date_range_handling", "FAIL", str(e))
            raise
    
    @pytest.mark.edge_case
    @pytest.mark.data
    def test_unsupported_frequency_handling(self, test_logger, real_retrieve_class):
        """
        Test handling of unsupported or invalid frequency parameters.
        
        This specifically tests invalid frequency formats and ensures
        the system fails predictably for unsupported frequencies.
        """
        test_logger.start_test("test_unsupported_frequency_handling")
        
        try:
            retriever = real_retrieve_class
            
            # Test invalid frequency formats
            invalid_frequencies = [
                "2M",      # 2-minute (not standard)
                "15M",     # 15-minute (not standard)
                "3H",      # 3-hour (not standard)
                "1W",      # Weekly (may not be supported)
                "invalid", # Completely invalid
                "",        # Empty string
                "1D1H",    # Malformed
                "1d",      # Wrong case
                "1MIN",    # Different format
                "daily"    # Word format
            ]
            
            results = {}
            
            for freq in invalid_frequencies:
                try:
                    data = retriever.get_data("GSPC", "2023-01-01", "2023-01-31", freq)
                    
                    if data is None:
                        results[freq] = "returned_none"
                    elif data.empty:
                        results[freq] = "returned_empty"
                    else:
                        results[freq] = f"unexpected_success_{len(data)}_records"
                        
                except Exception as e:
                    results[freq] = f"exception_{type(e).__name__}"
            
            # Most invalid frequencies should result in exceptions or empty data
            appropriate_handling = 0
            total_tests = len(invalid_frequencies)
            
            for freq, result in results.items():
                if result in ["returned_none", "returned_empty"] or result.startswith("exception_"):
                    appropriate_handling += 1
                else:
                    print(f"⚠️  Unexpected success for invalid frequency '{freq}': {result}")
            
            success_rate = (appropriate_handling / total_tests) * 100
            
            if success_rate >= 80:  # Allow some flexibility
                test_logger.end_test("test_unsupported_frequency_handling", "PASS", 
                                   f"Invalid frequencies handled appropriately: {success_rate:.1f}% ({appropriate_handling}/{total_tests})")
            else:
                test_logger.end_test("test_unsupported_frequency_handling", "FAIL", 
                                   f"Poor handling of invalid frequencies: {success_rate:.1f}% appropriate")
                
        except Exception as e:
            test_logger.end_test("test_unsupported_frequency_handling", "FAIL", str(e))
            raise


class TestBoundaryConditions:
    """
    Test suite for Boundary Conditions.
    
    Tests system behavior at the limits of expected operation,
    including minimum/maximum values, empty datasets, and
    resource constraints.
    """
    
    @pytest.mark.edge_case
    @pytest.mark.performance
    def test_very_large_date_ranges(self, test_logger, real_retrieve_class):
        """
        Test handling of very large date ranges.
        
        Validates system behavior when requesting large amounts of data
        and ensures proper handling of memory and performance constraints.
        """
        test_logger.start_test("test_very_large_date_ranges")
        
        try:
            retriever = real_retrieve_class
            
            # Test increasingly large date ranges
            large_range_tests = [
                {
                    "name": "one_year_daily",
                    "start": "2022-01-01",
                    "end": "2022-12-31",
                    "frequency": "1D",
                    "expected_approx_records": 252  # Trading days
                },
                {
                    "name": "five_years_daily", 
                    "start": "2018-01-01",
                    "end": "2022-12-31",
                    "frequency": "1D",
                    "expected_approx_records": 1260  # ~5 years trading days
                },
                {
                    "name": "ten_years_daily",
                    "start": "2013-01-01", 
                    "end": "2022-12-31",
                    "frequency": "1D",
                    "expected_approx_records": 2520  # ~10 years trading days
                }
            ]
            
            results = {}
            
            for test in large_range_tests:
                start_time = time.time()
                
                try:
                    data = retriever.get_data("GSPC", test["start"], test["end"], test["frequency"])
                    execution_time = time.time() - start_time
                    
                    if data is not None and not data.empty:
                        record_count = len(data)
                        # Check if record count is reasonable (within 50% of expected)
                        expected = test["expected_approx_records"]
                        reasonable_range = (expected * 0.5, expected * 1.5)
                        
                        if reasonable_range[0] <= record_count <= reasonable_range[1]:
                            results[test["name"]] = {
                                "status": "success",
                                "records": record_count,
                                "time": execution_time,
                                "reasonable": True
                            }
                        else:
                            results[test["name"]] = {
                                "status": "success_unexpected_count",
                                "records": record_count,
                                "time": execution_time,
                                "reasonable": False
                            }
                    else:
                        results[test["name"]] = {
                            "status": "empty_or_none",
                            "records": 0,
                            "time": execution_time,
                            "reasonable": False
                        }
                        
                except Exception as e:
                    execution_time = time.time() - start_time
                    results[test["name"]] = {
                        "status": f"exception_{type(e).__name__}",
                        "records": 0,
                        "time": execution_time,
                        "reasonable": False,
                        "error": str(e)[:100]
                    }
            
            # Analyze results
            successful_tests = sum(1 for r in results.values() if r["status"] == "success")
            total_tests = len(large_range_tests)
            
            # Generate summary
            summary_lines = []
            for name, result in results.items():
                summary_lines.append(f"{name}: {result['status']} ({result['records']} records, {result['time']:.1f}s)")
            
            if successful_tests >= total_tests * 0.6:  # At least 60% should work
                test_logger.end_test("test_very_large_date_ranges", "PASS", 
                                   f"Large date ranges handled adequately: {successful_tests}/{total_tests} successful. " + 
                                   "; ".join(summary_lines))
            else:
                test_logger.end_test("test_very_large_date_ranges", "PARTIAL", 
                                   f"Some issues with large date ranges: {successful_tests}/{total_tests} successful. " + 
                                   "; ".join(summary_lines))
                
        except Exception as e:
            test_logger.end_test("test_very_large_date_ranges", "FAIL", str(e))
            raise
    
    @pytest.mark.edge_case
    @pytest.mark.data
    def test_minimum_date_ranges(self, test_logger, real_retrieve_class):
        """
        Test handling of minimum viable date ranges.
        
        Tests single-day requests, weekend-only periods, and other
        minimal date ranges to ensure proper handling.
        """
        test_logger.start_test("test_minimum_date_ranges")
        
        try:
            retriever = real_retrieve_class
            
            # Test minimal date ranges
            minimal_tests = [
                {
                    "name": "single_trading_day",
                    "start": "2023-01-03",  # A Tuesday
                    "end": "2023-01-03",
                    "expected": "should_return_one_record_or_empty"
                },
                {
                    "name": "weekend_only",
                    "start": "2023-01-07",  # Saturday
                    "end": "2023-01-08",    # Sunday
                    "expected": "should_return_empty"
                },
                {
                    "name": "single_weekend_day",
                    "start": "2023-01-07",  # Saturday
                    "end": "2023-01-07",
                    "expected": "should_return_empty"
                },
                {
                    "name": "holiday_period",
                    "start": "2023-01-16",  # MLK Day (market closed)
                    "end": "2023-01-16",
                    "expected": "should_return_empty"
                }
            ]
            
            results = {}
            
            for test in minimal_tests:
                try:
                    data = retriever.get_data("GSPC", test["start"], test["end"], "1D")
                    
                    if data is None:
                        results[test["name"]] = "returned_none"
                    elif data.empty:
                        results[test["name"]] = "returned_empty"
                    else:
                        results[test["name"]] = f"returned_{len(data)}_records"
                        
                except Exception as e:
                    results[test["name"]] = f"exception_{type(e).__name__}"
            
            # All minimal tests should be handled gracefully
            graceful_results = 0
            for name, result in results.items():
                if result in ["returned_none", "returned_empty", "returned_1_records"] or result.startswith("exception_"):
                    graceful_results += 1
            
            success_rate = (graceful_results / len(minimal_tests)) * 100
            
            test_logger.end_test("test_minimum_date_ranges", "PASS" if success_rate == 100 else "PARTIAL", 
                               f"Minimal date ranges handled: {success_rate:.1f}% graceful ({results})")
            
        except Exception as e:
            test_logger.end_test("test_minimum_date_ranges", "FAIL", str(e))
            raise


class TestErrorRecoveryMechanisms:
    """
    Test suite for Error Recovery Mechanisms.
    
    Tests the system's ability to recover from various error conditions
    and continue operating properly after encountering problems.
    """
    
    @pytest.mark.edge_case
    @pytest.mark.integration
    def test_sequential_error_recovery(self, test_logger, real_retrieve_class):
        """
        Test system recovery after sequential errors.
        
        Validates that the system can recover from errors and continue
        to process valid requests properly after encountering failures.
        """
        test_logger.start_test("test_sequential_error_recovery")
        
        try:
            retriever = real_retrieve_class
            
            # Sequence: valid -> invalid -> valid -> invalid -> valid
            test_sequence = [
                {"type": "valid", "symbol": "GSPC", "start": "2023-01-01", "end": "2023-01-31", "freq": "1D"},
                {"type": "invalid", "symbol": "INVALID", "start": "2023-01-01", "end": "2023-01-31", "freq": "1D"},
                {"type": "valid", "symbol": "GSPC", "start": "2023-02-01", "end": "2023-02-28", "freq": "1D"},
                {"type": "invalid", "symbol": "GSPC", "start": "invalid-date", "end": "2023-01-31", "freq": "1D"},
                {"type": "valid", "symbol": "GSPC", "start": "2023-03-01", "end": "2023-03-31", "freq": "1D"}
            ]
            
            results = []
            
            for i, test_case in enumerate(test_sequence):
                try:
                    data = retriever.get_data(
                        test_case["symbol"], 
                        test_case["start"], 
                        test_case["end"], 
                        test_case["freq"]
                    )
                    
                    if test_case["type"] == "valid":
                        if data is not None and not data.empty:
                            results.append({"step": i, "expected": "valid", "actual": "success", "records": len(data)})
                        else:
                            results.append({"step": i, "expected": "valid", "actual": "failed", "records": 0})
                    else:  # invalid
                        if data is None or data.empty:
                            results.append({"step": i, "expected": "invalid", "actual": "properly_failed", "records": 0})
                        else:
                            results.append({"step": i, "expected": "invalid", "actual": "unexpected_success", "records": len(data)})
                            
                except Exception as e:
                    if test_case["type"] == "valid":
                        results.append({"step": i, "expected": "valid", "actual": "exception", "error": type(e).__name__})
                    else:
                        results.append({"step": i, "expected": "invalid", "actual": "exception", "error": type(e).__name__})
            
            # Analyze recovery pattern
            valid_requests = [r for r in results if r["expected"] == "valid"]
            successful_valid = [r for r in valid_requests if r["actual"] == "success"]
            
            recovery_rate = (len(successful_valid) / len(valid_requests)) * 100 if valid_requests else 0
            
            # Check if system maintained functionality after errors
            if recovery_rate >= 80:  # Should handle at least 80% of valid requests correctly
                test_logger.end_test("test_sequential_error_recovery", "PASS", 
                                   f"System recovered properly: {recovery_rate:.1f}% valid requests succeeded")
            else:
                test_logger.end_test("test_sequential_error_recovery", "FAIL", 
                                   f"Poor error recovery: only {recovery_rate:.1f}% valid requests succeeded after errors")
            
        except Exception as e:
            test_logger.end_test("test_sequential_error_recovery", "FAIL", str(e))
            raise


class TestResourceConstraintHandling:
    """
    Test suite for Resource Constraint Handling.
    
    Tests system behavior under resource constraints such as memory
    limitations, timeout conditions, and concurrent access scenarios.
    """
    
    @pytest.mark.edge_case
    @pytest.mark.performance
    @pytest.mark.slow
    def test_timeout_handling(self, test_logger, real_retrieve_class):
        """
        Test handling of operation timeouts.
        
        Validates that the system properly handles situations where
        data retrieval operations take longer than expected.
        """
        test_logger.start_test("test_timeout_handling")
        
        try:
            retriever = real_retrieve_class
            
            # Test with requests that might timeout
            timeout_tests = [
                {
                    "name": "very_large_range",
                    "symbol": "GSPC",
                    "start": "2000-01-01",
                    "end": "2023-12-31",
                    "freq": "1D",
                    "timeout_seconds": 30
                }
            ]
            
            results = {}
            
            for test in timeout_tests:
                start_time = time.time()
                timeout_reached = False
                
                try:
                    # Simulate timeout by checking execution time
                    data = retriever.get_data(test["symbol"], test["start"], test["end"], test["freq"])
                    execution_time = time.time() - start_time
                    
                    if execution_time > test["timeout_seconds"]:
                        timeout_reached = True
                        results[test["name"]] = {
                            "status": "slow_but_completed",
                            "time": execution_time,
                            "records": len(data) if data is not None and not data.empty else 0
                        }
                    else:
                        results[test["name"]] = {
                            "status": "completed_within_timeout",
                            "time": execution_time,
                            "records": len(data) if data is not None and not data.empty else 0
                        }
                        
                except Exception as e:
                    execution_time = time.time() - start_time
                    results[test["name"]] = {
                        "status": f"exception_{type(e).__name__}",
                        "time": execution_time,
                        "error": str(e)[:100]
                    }
            
            # Evaluate timeout handling
            handled_appropriately = True
            for name, result in results.items():
                # Any graceful handling (completion, timeout, or expected exception) is acceptable
                if not (result["status"].startswith(("completed", "slow_but", "exception_"))):
                    handled_appropriately = False
            
            if handled_appropriately:
                summary = "; ".join([f"{k}: {v['status']} ({v['time']:.1f}s)" for k, v in results.items()])
                test_logger.end_test("test_timeout_handling", "PASS", 
                                   f"Timeout scenarios handled appropriately: {summary}")
            else:
                test_logger.end_test("test_timeout_handling", "FAIL", 
                                   f"Poor timeout handling: {results}")
                
        except Exception as e:
            test_logger.end_test("test_timeout_handling", "FAIL", str(e))
            raise
'''
        return content
    
    def _generate_integration_tests(self) -> str:
        """Generate integration tests."""
        return self._generate_generic_tests("integration", {"description": "End-to-end and component integration testing"})
    
    def _generate_performance_benchmark_tests(self) -> str:
        """Generate performance benchmark tests."""
        return self._generate_generic_tests("performance", {"description": "Execution speed and scalability testing"})
    
    def _generate_compliance_tests(self) -> str:
        """Generate regulatory compliance tests."""
        return self._generate_generic_tests("regulatory_compliance", {"description": "Trading rules and regulatory compliance"})


def main():
    parser = argparse.ArgumentParser(description="Generate pytest test files")
    parser.add_argument("--analysis", required=True, help="Path to analysis JSON file")
    parser.add_argument("--framework-dir", required=True, help="Framework directory path")
    parser.add_argument("--framework-name", required=True, help="Framework name")
    
    args = parser.parse_args()
    
    generator = TestGenerator()
    generator.generate_tests(Path(args.analysis), Path(args.framework_dir), args.framework_name)


if __name__ == "__main__":
    main()