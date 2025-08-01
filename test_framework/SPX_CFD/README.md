# SPX CFD Testing Framework

## Overview

Comprehensive testing framework for the SPX CFD intraday momentum strategy, implementing 200+ test cases across 11 categories following Python unit testing best practices.

## Features

- **🧪 Comprehensive Test Coverage**: 200+ tests across all strategy components
- **📊 Real-time Test Reporting**: Live test execution with timestamped results
- **🎯 Category-based Testing**: Run specific test categories (data, parameters, UI, etc.)
- **📈 Performance Analytics**: Built-in performance and scalability testing
- **🖥️ UI Component Testing**: Full Streamlit interface testing with mocking
- **📄 Automated Reporting**: JSON and text-based test result reports
- **🔄 CI/CD Ready**: Integration with continuous integration pipelines

## Test Categories

1. **Data Management** (15 tests) - Market data retrieval and validation
2. **Strategy Parameters** (12 tests) - Parameter validation and relationships  
3. **Trading Logic** (16 tests) - Entry/exit signals and session management
4. **Risk Management** (10 tests) - Position sizing and risk controls
5. **Transaction Costs** (8 tests) - Cost calculations and impact analysis
6. **Performance Analytics** (10 tests) - Trade analytics and portfolio metrics
7. **Edge Cases** (15 tests) - Error handling and market anomalies
8. **Integration** (8 tests) - End-to-end and component integration
9. **Performance** (8 tests) - Execution speed and scalability
10. **Regulatory Compliance** (8 tests) - Trading rules and risk disclosure
11. **User Interface** (94 tests) - Streamlit components and interactions

## Installation

1. **Clone and navigate to the testing framework:**
   ```bash
   cd OpenBB/test_framework/SPX_CFD
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python -m pytest --version
   ```

## Usage

### Basic Test Execution

```bash
# Run all tests
python run_tests.py

# Run with verbose output
python run_tests.py --verbose

# Run with coverage report
python run_tests.py --coverage
```

### Category-specific Testing

```bash
# Run data management tests only
python run_tests.py --category data

# Run UI tests only  
python run_tests.py --category ui

# Run parameter validation tests
python run_tests.py --category parameters
```

### Marker-based Testing

```bash
# Run only unit tests
python run_tests.py --markers unit

# Run integration tests (excluding slow tests)
python run_tests.py --markers "integration and not slow"

# Run UI tests only
python run_tests.py --markers ui

# Run performance tests
python run_tests.py --markers performance
```

### Advanced Options

```bash
# Generate HTML coverage report
python run_tests.py --coverage --verbose

# Run specific test file
python -m pytest tests/test_data_management.py -v

# Run single test function
python -m pytest tests/test_data_management.py::TestMarketDataRetrieval::test_market_data_provider_connection -v

# Generate report from last run
python run_tests.py --report-only
```

## Test Output Format

The framework provides real-time test execution feedback:

```
================================================================================
🧪 SPX CFD TESTING FRAMEWORK
================================================================================
Timestamp: 2025-01-25 14:30:15
Test Directory: /path/to/test_framework/SPX_CFD
Results File: /path/to/results/test_result_20250125_143015.txt
================================================================================

🚀 Starting test execution at 14:30:15

[14:30:16] Executing test: test_market_data_provider_connection
[14:30:16] test_market_data_provider_connection: PASS ✅

[14:30:17] Executing test: test_data_frequency_mapping
[14:30:17] test_data_frequency_mapping: PASS ✅

[14:30:18] Executing test: test_parameter_validation
[14:30:18] test_parameter_validation: PASS ✅

================================================================================
📊 TEST EXECUTION SUMMARY
================================================================================
Start Time: 2025-01-25 14:30:15
End Time: 2025-01-25 14:32:45
Duration: 0:02:30

Total Tests: 150
✅ Passed: 147
❌ Failed: 2
⏭️ Skipped: 1

Success Rate: 98.0%
🎉 OVERALL RESULT: SOME TESTS FAILED

📁 Detailed results saved to: results/test_result_20250125_143015.txt
📄 JSON results saved to: results/test_result_20250125_143015.json
================================================================================
```

## Directory Structure

```
SPX_CFD/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── pytest.ini                  # Pytest configuration
├── conftest.py                  # Global fixtures and configuration
├── run_tests.py                 # Command line test runner
├── SPX_CFD_testing.md          # Comprehensive test plan
├── tests/                       # Test modules
│   ├── __init__.py
│   ├── test_data_management.py
│   ├── test_strategy_parameters.py
│   ├── test_trading_logic.py
│   ├── test_risk_management.py
│   ├── test_transaction_costs.py
│   ├── test_performance_analytics.py
│   ├── test_edge_cases.py
│   ├── test_integration.py
│   ├── test_performance.py
│   ├── test_regulatory_compliance.py
│   └── test_ui_components.py
├── fixtures/                    # Test data and fixtures
│   └── data/
├── mocks/                       # Mock objects and utilities
├── utils/                       # Testing utilities
├── results/                     # Test execution results
│   ├── test_result_*.txt       # Timestamped result files
│   ├── test_result_*.json      # JSON result data
│   └── coverage/               # Coverage reports
└── htmlcov/                    # HTML coverage reports
```

## Test Development Guidelines

### Writing New Tests

1. **Follow naming conventions**: `test_<functionality_being_tested>`
2. **Use appropriate markers**: `@pytest.mark.unit`, `@pytest.mark.integration`, etc.
3. **Include test logging**: Use the `test_logger` fixture for consistent output
4. **Mock external dependencies**: Use provided mock fixtures
5. **Assert meaningful conditions**: Test both positive and negative cases

### Example Test Structure

```python
@pytest.mark.unit
@pytest.mark.mock
def test_example_functionality(self, test_logger, sample_strategy_params):
    """Test description following best practices."""
    test_logger.start_test("test_example_functionality")
    
    try:
        # Arrange
        input_data = sample_strategy_params
        expected_result = "expected_value"
        
        # Act
        actual_result = function_under_test(input_data)
        
        # Assert
        assert actual_result == expected_result
        assert isinstance(actual_result, str)
        
        test_logger.end_test("test_example_functionality", "PASS")
    except Exception as e:
        test_logger.end_test("test_example_functionality", "FAIL", str(e))
        raise
```

### Available Fixtures

- `test_config`: Test configuration parameters
- `sample_strategy_params`: Standard strategy parameters
- `mock_market_data`: Generate mock OHLCV data
- `mock_retrieve_class`: Mock market data retrieval
- `sample_trades_data`: Sample trade results
- `mock_streamlit`: Mock Streamlit UI components
- `mock_plotly`: Mock Plotly chart components
- `test_logger`: Test execution logger

## CI/CD Integration

### GitHub Actions Example

```yaml
name: SPX CFD Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        cd test_framework/SPX_CFD
        pip install -r requirements.txt
    - name: Run tests
      run: |
        cd test_framework/SPX_CFD
        python run_tests.py --coverage
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

## Performance Benchmarks

The framework includes performance testing with the following targets:

- **Backtest Execution**: < 30 seconds for 1-year daily data
- **Memory Usage**: < 2GB for typical datasets  
- **Test Suite Completion**: < 10 minutes for full suite
- **UI Load Time**: < 5 seconds for initial page load

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the strategy modules are in Python path
2. **Missing Dependencies**: Run `pip install -r requirements.txt`
3. **Permission Errors**: Check file permissions for results directory
4. **Memory Issues**: Use `--markers "not slow"` to skip resource-intensive tests

### Debug Mode

```bash
# Run with maximum verbosity
python run_tests.py --verbose --markers "unit" -s

# Run single failing test
python -m pytest tests/test_data_management.py::TestMarketDataRetrieval::test_failing_test -v -s

# Generate detailed coverage report
python run_tests.py --coverage --verbose
```

## Contributing

1. **Add new test categories** in `tests/` directory
2. **Update test plan** in `SPX_CFD_testing.md`
3. **Follow coding standards** with black, flake8, mypy
4. **Add appropriate markers** and documentation
5. **Test your tests** before committing

## Results and Reporting

Test results are saved in multiple formats:

- **Text Reports**: `results/test_result_YYYYMMDD_HHMMSS.txt`
- **JSON Data**: `results/test_result_YYYYMMDD_HHMMSS.json`
- **HTML Coverage**: `htmlcov/index.html`
- **XML Results**: `pytest_results.xml` (for CI/CD)

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review test execution logs in `results/` directory  
3. Run tests with `--verbose` flag for detailed output
4. Consult the comprehensive test plan in `SPX_CFD_testing.md`

---

**Framework Version**: 1.0.0  
**Last Updated**: January 2025  
**Compatible with**: Python 3.8+, Pytest 7.0+, Streamlit 1.28+