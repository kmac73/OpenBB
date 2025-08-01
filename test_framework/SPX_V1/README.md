# SPX_V1 Testing Framework

**Generated:** 2025-08-01 11:24:02

A comprehensive pytest-based testing framework for the SPX_V1 trading strategy.

## Quick Start

### Prerequisites
- Python 3.8+
- OpenBB-env conda environment (or compatible environment)

### Installation
```bash
# Install testing dependencies
./install_packages.sh

# Verify environment
./check_environment.sh
```

### Running Tests
```bash
# Run all tests
python run_tests.py

# Run specific category
python run_tests.py --category data

# Run with coverage report
python run_tests.py --coverage

# Run verbose with detailed output
python run_tests.py --verbose

# Generate report from previous run
python run_tests.py --report-only
```

## Project Structure

```
SPX_V1/
├── tests/                      # Test files
│   ├── test_data_management.py
│   ├── test_strategy_parameters.py
│   ├── test_trading_logic.py
│   ├── test_risk_management.py
│   ├── test_ui_components.py
│   └── ...
├── fixtures/                   # Test data fixtures
├── mocks/                      # Mock objects and utilities
├── utils/                      # Test utilities
├── results/                    # Test execution results
├── conftest.py                 # Pytest configuration and fixtures
├── pytest.ini                 # Pytest settings
├── requirements.txt            # Testing dependencies
├── run_tests.py               # Command line test runner
├── install_packages.sh        # Dependency installation
├── check_environment.sh       # Environment validation
├── README.md                  # This file
└── SPX_V1_testing.md    # Detailed test plan
```

## Test Categories

**Total Tests:** 188

### Data Management (15 tests)
**Priority:** HIGH  
Market data retrieval, validation, and quality checks

### Strategy Parameters (6 tests)
**Priority:** HIGH  
Parameter validation, relationships, and constraints

### Trading Logic (16 tests)
**Priority:** HIGH  
Entry/exit signals, session management, and signal generation

### Ui Components (94 tests)
**Priority:** MEDIUM  
User interface components and interactions

### Transaction Costs (8 tests)
**Priority:** MEDIUM  
Cost calculations and impact analysis

### Performance Analytics (10 tests)
**Priority:** MEDIUM  
Trade analytics and portfolio metrics

### Edge Cases (15 tests)
**Priority:** MEDIUM  
Error handling and market anomalies

### Integration (8 tests)
**Priority:** HIGH  
End-to-end and component integration testing

### Performance (8 tests)
**Priority:** LOW  
Execution speed and scalability testing

### Regulatory Compliance (8 tests)
**Priority:** MEDIUM  
Trading rules and regulatory compliance

## Test Execution Examples

### Basic Usage
```bash
# Run all tests with progress output
python run_tests.py

# Example output:
# ================================================================================
# 🧪 SPX_V1 TESTING FRAMEWORK
# ================================================================================
# [10:30:15] Executing test: test_market_data_provider_connection
# [10:30:15] test_market_data_provider_connection: PASS ✅
# [10:30:16] Executing test: test_data_format_consistency
# [10:30:16] test_data_format_consistency: PASS ✅
# ...
```

### Category-Specific Testing
```bash
# Test only data management
python run_tests.py --category data

# Test only UI components
python run_tests.py --category ui

# Test only high-priority items
python run_tests.py --markers "high_priority"
```

### Performance Testing
```bash
# Include performance benchmarks
python run_tests.py --markers "performance"

# Run with memory profiling
python run_tests.py --markers "not slow" --coverage
```

## Test Reports

Test results are automatically saved with timestamps:

- **Text Report:** `results/test_result_YYYYMMDD_HHMMSS.txt`
- **JSON Report:** `results/test_result_YYYYMMDD_HHMMSS.json`
- **Coverage Report:** `htmlcov/index.html` (when using --coverage)

### Sample JSON Report Structure
```json
{
  "framework": "SPX_V1",
  "timestamp": "20240131_143022",
  "total_tests": 188,
  "passed": 95,
  "failed": 2,
  "skipped": 1,
  "success_rate": 97.9,
  "test_details": [...]
}
```

## Integration with Development Workflow

### Pre-commit Testing
```bash
# Quick smoke test
python run_tests.py --markers "unit and not slow"

# Full validation
python run_tests.py --coverage
```

### CI/CD Integration
The test runner returns appropriate exit codes:
- `0`: All tests passed
- `1`: Some tests failed or errors occurred

### Performance Monitoring
Monitor test execution times and update performance thresholds:
- Individual test timeouts
- Category-level benchmarks
- Memory usage tracking
- UI responsiveness metrics

## Troubleshooting

### Common Issues

**Missing Dependencies**
```bash
./install_packages.sh
./check_environment.sh
```

**Test Failures**
```bash
# Run with verbose output
python run_tests.py --verbose

# Run specific failing test
python run_tests.py --markers "failing_test_name"
```

**Performance Issues**
```bash
# Skip slow tests
python run_tests.py --markers "not slow"

# Profile memory usage
python run_tests.py --markers "performance"
```

## Extending the Framework

### Adding New Tests
1. Create test file in `tests/` directory
2. Follow naming convention: `test_<category>.py`
3. Use appropriate pytest markers
4. Include test logger for execution tracking

### Custom Fixtures
Add reusable test fixtures to `conftest.py`:
```python
@pytest.fixture
def custom_test_data():
    return generate_custom_data()
```

### Performance Benchmarks
Add benchmark tests using pytest-benchmark:
```python
@pytest.mark.performance
def test_strategy_execution_speed(benchmark):
    result = benchmark(strategy.run_backtest, test_data)
    assert result is not None
```

## Documentation

- **Detailed Test Plan:** `SPX_V1_testing.md`
- **Strategy Requirements:** `docs/strategies/SPX/revised_cfd_strategy.md`
- **API Documentation:** Generated from docstrings
- **Coverage Reports:** `htmlcov/index.html`

## Support

For issues with the testing framework:
1. Check test execution logs in `results/`
2. Verify environment with `./check_environment.sh`
3. Review test plan documentation
4. Check pytest configuration in `pytest.ini`

---

**Framework Generated:** 2025-08-01 11:24:02  
**Source Requirements:** docs/strategies/SPX/revised_cfd_strategy.md  
**Total Test Coverage:** 188 test cases across 10 categories
