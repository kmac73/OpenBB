#!/usr/bin/env python3
"""
OpenBB Test Framework Generator - Documentation Generator
Generates comprehensive test plan documentation and README files.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class DocumentationGenerator:
    """Generates documentation files for the test framework."""
    
    def __init__(self):
        self.analysis = {}
        self.framework_dir = None
        self.framework_name = ""
        self.requirements_doc = ""
    
    def generate_documentation(self, analysis_file: Path, framework_dir: Path, framework_name: str, requirements_doc: str):
        """Generate all documentation files."""
        with open(analysis_file) as f:
            self.analysis = json.load(f)
        
        self.framework_dir = framework_dir
        self.framework_name = framework_name
        self.requirements_doc = requirements_doc
        
        print(f"📚 Generating documentation for {framework_name}")
        
        self._generate_test_plan()
        self._generate_readme()
        
        print("✅ Documentation generated")
    
    def _generate_test_plan(self):
        """Generate comprehensive test plan document."""
        test_plan_content = f"""# {self.framework_name} Testing Framework

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Source Document:** {self.requirements_doc}  
**Strategy Type:** {self.analysis.get('strategy_type', 'general').title()}

## Overview

This document outlines the comprehensive testing strategy for the {self.framework_name} trading strategy implementation. The test suite is designed to validate all critical components of the strategy including data management, parameter validation, trading logic, risk management, and user interface components.

## Test Categories Summary

"""
        
        # Generate test categories overview
        categories = self.analysis.get("test_categories", {})
        total_tests = sum(cat.get("tests", 0) for cat in categories.values())
        
        test_plan_content += f"**Total Test Cases:** {total_tests}\n\n"
        
        # Category breakdown table
        test_plan_content += "| Category | Tests | Priority | Description |\n"
        test_plan_content += "|----------|-------|----------|-------------|\n"
        
        for category, info in categories.items():
            category_name = category.replace('_', ' ').title()
            test_count = info.get('tests', 0)
            priority = info.get('priority', 'medium').upper()
            description = info.get('description', 'No description available')
            test_plan_content += f"| {category_name} | {test_count} | {priority} | {description} |\n"
        
        test_plan_content += "\n"
        
        # Strategy Analysis Section
        test_plan_content += "## Strategy Analysis\n\n"
        
        if self.analysis.get("parameters"):
            test_plan_content += "### Parameters Identified\n\n"
            for param_name, param_info in self.analysis["parameters"].items():
                param_type = param_info.get("type", "unknown")
                param_desc = param_info.get("description", "No description")
                default_val = param_info.get("default_value", "Not specified")
                test_plan_content += f"- **{param_name}** ({param_type}): {param_desc}\n"
                if default_val != "Not specified":
                    test_plan_content += f"  - Default: {default_val}\n"
            test_plan_content += "\n"
        
        if self.analysis.get("trading_logic", {}).get("entry_conditions"):
            test_plan_content += "### Entry Conditions\n\n"
            for condition in self.analysis["trading_logic"]["entry_conditions"]:
                test_plan_content += f"- {condition.strip()}\n"
            test_plan_content += "\n"
        
        if self.analysis.get("trading_logic", {}).get("exit_conditions"):
            test_plan_content += "### Exit Conditions\n\n"
            for condition in self.analysis["trading_logic"]["exit_conditions"]:
                test_plan_content += f"- {condition.strip()}\n"
            test_plan_content += "\n"
        
        # Detailed Test Categories
        test_plan_content += "## Detailed Test Categories\n\n"
        
        for category, info in categories.items():
            category_name = category.replace('_', ' ').title()
            test_plan_content += f"### {category_name}\n\n"
            test_plan_content += f"**Test Count:** {info.get('tests', 0)}  \n"
            test_plan_content += f"**Priority:** {info.get('priority', 'medium').upper()}  \n"
            test_plan_content += f"**Description:** {info.get('description', 'No description available')}\n\n"
            
            # Add category-specific details
            if category == "data_management":
                test_plan_content += """**Test Areas:**
- Market data provider connection validation
- Data frequency mapping and validation
- OHLCV data format consistency checks
- Data completeness verification (no missing values)
- Data logical consistency (High >= Low, etc.)
- Date range and symbol validation
- Data quality metrics and thresholds
- Error handling for data retrieval failures
- Connection timeout and retry logic
- Data caching and refresh mechanisms

"""
            elif category == "strategy_parameters":
                test_plan_content += """**Test Areas:**
- Parameter type validation and constraints
- Required parameter presence checks
- Parameter value range validation
- Parameter relationship consistency
- Default value application
- Invalid parameter handling
- Parameter serialization/deserialization
- Configuration file parsing
- Dynamic parameter updates
- Parameter validation error messages

"""
            elif category == "trading_logic":
                test_plan_content += """**Test Areas:**
- Entry signal generation and validation
- Exit signal generation and validation
- Position sizing calculations
- Trading session management
- Signal timing and synchronization
- Multiple timeframe coordination
- Signal strength measurement
- Trade execution logic
- Order management and tracking
- Strategy state management

"""
            elif category == "risk_management":
                test_plan_content += """**Test Areas:**
- Position size limits enforcement
- Maximum drawdown controls
- Stop loss implementation
- Risk per trade calculations
- Portfolio exposure limits
- Leverage constraint validation
- Risk monitoring and alerts
- Emergency position closure
- Risk metric calculations
- Correlation risk management

"""
            elif category == "ui_components":
                test_plan_content += """**Test Areas:**
- Parameter input widgets (sliders, inputs, selectors)
- Real-time data display components
- Chart rendering and updates
- Interactive chart controls
- Strategy performance metrics display
- Trade history tables
- Portfolio overview components
- Alert and notification systems
- Export functionality (CSV, PDF)
- Responsive design validation

"""
        
        # Testing Framework Details
        test_plan_content += """## Testing Framework Details

### Test Organization
- **Unit Tests:** Individual component testing with mocks
- **Integration Tests:** Component interaction testing
- **UI Tests:** User interface component validation
- **Performance Tests:** Speed and scalability validation
- **Regression Tests:** Bug fix verification

### Test Execution
```bash
# Run all tests
python run_tests.py

# Run specific category
python run_tests.py --category data

# Run with coverage
python run_tests.py --coverage

# Run specific markers
python run_tests.py --markers "unit and not slow"
```

### Test Markers
- `unit`: Unit tests for individual components
- `integration`: Integration tests for component interactions  
- `ui`: User interface tests
- `performance`: Performance and scalability tests
- `slow`: Tests that take longer than 30 seconds
- `data`: Tests requiring market data
- `mock`: Tests using mocked dependencies
- `edge_case`: Edge case and error handling tests
- `regression`: Regression tests for bug fixes

### Mock Data
The framework includes comprehensive mock data generators for:
- OHLCV market data with configurable trends
- Trade execution results
- UI component interactions
- External API responses
- Error conditions and edge cases

### Performance Targets
"""
        
        if self.analysis.get("performance_targets"):
            perf = self.analysis["performance_targets"]
            if perf.get("return_targets"):
                test_plan_content += f"- **Return Targets:** {', '.join(perf['return_targets'])}%\n"
            if perf.get("win_rate_targets"):
                test_plan_content += f"- **Win Rate Targets:** {', '.join(perf['win_rate_targets'])}%\n"
            if perf.get("execution_speed"):
                test_plan_content += f"- **Execution Speed:** {', '.join(perf['execution_speed'])}\n"
        else:
            test_plan_content += """- **Backtest Execution:** < 30 seconds
- **Memory Usage:** < 2GB
- **UI Load Time:** < 5 seconds
"""
        
        test_plan_content += """
### Reporting
Test results are automatically saved to:
- **Text Report:** `results/test_result_YYYYMMDD_HHMMSS.txt`
- **JSON Report:** `results/test_result_YYYYMMDD_HHMMSS.json`
- **Coverage Report:** `htmlcov/index.html` (when --coverage used)

### Continuous Integration
The test framework is designed to integrate with CI/CD pipelines:
- Exit codes indicate overall test success/failure
- JSON reports can be parsed by CI systems
- Coverage reports can be uploaded to coverage services
- Test timing information for performance monitoring

## Maintenance and Updates

### Adding New Tests
1. Add test functions to appropriate test files in `tests/`
2. Use proper pytest markers for categorization
3. Include test logger calls for execution tracking
4. Update this documentation when adding new categories

### Updating Test Data
- Mock data generators are in `conftest.py`
- Update fixture parameters to match new requirements
- Ensure backwards compatibility with existing tests

### Performance Monitoring
- Monitor test execution times
- Update performance thresholds as needed
- Add benchmarking for critical code paths

---

*This test plan is automatically generated and should be updated when strategy requirements change.*
"""
        
        # Write test plan
        test_plan_file = self.framework_dir / f"{self.framework_name}_testing.md"
        test_plan_file.write_text(test_plan_content)
    
    def _generate_readme(self):
        """Generate README.md file."""
        readme_content = f"""# {self.framework_name} Testing Framework

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

A comprehensive pytest-based testing framework for the {self.framework_name} trading strategy.

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
{self.framework_name}/
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
└── {self.framework_name}_testing.md    # Detailed test plan
```

## Test Categories

"""
        
        # Add test categories summary
        categories = self.analysis.get("test_categories", {})
        total_tests = sum(cat.get("tests", 0) for cat in categories.values())
        
        readme_content += f"**Total Tests:** {total_tests}\n\n"
        
        for category, info in categories.items():
            category_name = category.replace('_', ' ').title()
            test_count = info.get('tests', 0)
            priority = info.get('priority', 'medium')
            description = info.get('description', 'No description available')
            
            readme_content += f"### {category_name} ({test_count} tests)\n"
            readme_content += f"**Priority:** {priority.upper()}  \n"
            readme_content += f"{description}\n\n"
        
        readme_content += f"""## Test Execution Examples

### Basic Usage
```bash
# Run all tests with progress output
python run_tests.py

# Example output:
# ================================================================================
# 🧪 {self.framework_name.upper()} TESTING FRAMEWORK
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
{{
  "framework": "{self.framework_name}",
  "timestamp": "20240131_143022",
  "total_tests": {total_tests},
  "passed": 95,
  "failed": 2,
  "skipped": 1,
  "success_rate": 97.9,
  "test_details": [...]
}}
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

- **Detailed Test Plan:** `{self.framework_name}_testing.md`
- **Strategy Requirements:** `{self.requirements_doc}`
- **API Documentation:** Generated from docstrings
- **Coverage Reports:** `htmlcov/index.html`

## Support

For issues with the testing framework:
1. Check test execution logs in `results/`
2. Verify environment with `./check_environment.sh`
3. Review test plan documentation
4. Check pytest configuration in `pytest.ini`

---

**Framework Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Source Requirements:** {self.requirements_doc}  
**Total Test Coverage:** {total_tests} test cases across {len(categories)} categories
"""
        
        # Write README
        readme_file = self.framework_dir / "README.md"
        readme_file.write_text(readme_content)


def main():
    parser = argparse.ArgumentParser(description="Generate documentation files")
    parser.add_argument("--analysis", required=True, help="Path to analysis JSON file")
    parser.add_argument("--framework-dir", required=True, help="Framework directory path")
    parser.add_argument("--framework-name", required=True, help="Framework name")
    parser.add_argument("--requirements-doc", required=True, help="Requirements document path")
    
    args = parser.parse_args()
    
    generator = DocumentationGenerator()
    generator.generate_documentation(Path(args.analysis), Path(args.framework_dir), args.framework_name, args.requirements_doc)


if __name__ == "__main__":
    main()