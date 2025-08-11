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
        self._generate_test_cases_summary()
        
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
    
    def _generate_test_cases_summary(self):
        """Generate human-readable test cases summary."""
        summary_content = f"""# {self.framework_name} Test Cases Summary

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Framework:** {self.framework_name}  
**Strategy Type:** {self.analysis.get('strategy_type', 'general').title()}

This document provides a human-readable summary of all test cases in the {self.framework_name} testing framework, organized by category with detailed descriptions of inputs, expected outputs, and test objectives.

## Overview

"""
        
        categories = self.analysis.get("test_categories", {})
        total_tests = sum(cat.get("tests", 0) for cat in categories.values())
        
        summary_content += f"**Total Test Cases:** {total_tests}  \n"
        summary_content += f"**Test Categories:** {len(categories)}  \n"
        summary_content += f"**Strategy Parameters:** {len(self.analysis.get('parameters', {}))}  \n\n"
        
        # Generate detailed test case descriptions for each category
        for category, info in categories.items():
            category_name = category.replace('_', ' ').title()
            summary_content += f"## {category_name}\n\n"
            summary_content += f"**Category:** {category}  \n"
            summary_content += f"**Test Count:** {info.get('tests', 0)}  \n"
            summary_content += f"**Priority:** {info.get('priority', 'medium').upper()}  \n"
            summary_content += f"**Description:** {info.get('description', 'No description available')}  \n\n"
            
            # Generate specific test case descriptions based on category
            if category == "data_management":
                summary_content += self._get_data_management_test_cases()
            elif category == "strategy_parameters":
                summary_content += self._get_parameter_test_cases()
            elif category == "trading_logic":
                summary_content += self._get_trading_logic_test_cases()
            elif category == "risk_management":
                summary_content += self._get_risk_management_test_cases()
            elif category == "ui_components":
                summary_content += self._get_ui_test_cases()
            elif category == "transaction_costs":
                summary_content += self._get_transaction_cost_test_cases()
            elif category == "performance_analytics":
                summary_content += self._get_performance_analytics_test_cases()
            elif category == "edge_cases":
                summary_content += self._get_edge_case_test_cases()
            elif category == "integration":
                summary_content += self._get_integration_test_cases()
            elif category == "performance":
                summary_content += self._get_performance_benchmark_test_cases()
            elif category == "regulatory_compliance":
                summary_content += self._get_compliance_test_cases()
            else:
                summary_content += self._get_generic_test_cases(category, info)
            
            summary_content += "\n---\n\n"
        
        # Write summary file
        summary_file = self.framework_dir / "test_cases_summary.md"
        summary_file.write_text(summary_content)
    
    def _get_data_management_test_cases(self):
        """Generate data management test case descriptions."""
        return """### Test Cases

| Test Name | Input | Expected Output | Success Criteria |
|-----------|-------|-----------------|-------------------|
| **test_market_data_provider_connection** | None | Retrieve class instance | ✅ Connection established, get_data method available |
| **test_data_frequency_mapping** | Frequencies: 1M, 5M, 30M, 1H, 1D | OHLCV DataFrame for each frequency | ✅ All frequencies return valid data with required columns |
| **test_data_format_consistency** | Symbol: GSPC, Date range: 2023-01-01 to 2023-01-31 | Properly formatted DataFrame | ✅ Required columns present, numeric data types, datetime index |
| **test_data_completeness** | Real market data for specified period | Complete dataset without gaps | ✅ No missing values, all required columns populated |
| **test_data_logical_consistency** | OHLCV data with price relationships | Validated price data | ✅ High ≥ Low, High ≥ Open/Close, Low ≤ Open/Close |

**Real Data Integration:**
- Uses actual S&P 500 data from OpenBB/yfinance
- Tests against 1,000+ real trading days
- Includes market crashes, volatility spikes, and normal conditions
- Validates data quality for production trading

"""
    
    def _get_parameter_test_cases(self):
        """Generate parameter validation test case descriptions."""
        parameters = self.analysis.get("parameters", {})
        
        content = """### Test Cases

| Test Name | Input | Expected Output | Success Criteria |
|-----------|-------|-----------------|-------------------|
"""
        
        # Add parameter-specific tests
        for param_name, param_info in parameters.items():
            param_type = param_info.get("type", "string")
            if param_type == "currency":
                content += f"| **test_{param_name.lower()}_validation** | Values: [10000, 25000, 50000, 100000] | Validation results | ✅ All positive numeric values accepted |\n"
            elif param_type == "percentage":
                content += f"| **test_{param_name.lower()}_validation** | Values: [0.5, 1.0, 1.5, 2.0, 2.5, 3.0] | Validation results | ✅ All values within 0-100% range |\n"
            else:
                content += f"| **test_{param_name.lower()}_validation** | Various {param_type} values | Validation results | ✅ Type and constraint validation passed |\n"
        
        content += """| **test_all_parameters_present** | Strategy parameter dictionary | Parameter presence check | ✅ All required parameters exist in configuration |
| **test_parameter_consistency** | Full parameter set | Consistency validation | ✅ Parameter relationships and constraints satisfied |

**Parameter Coverage:**
"""
        
        for param_name, param_info in parameters.items():
            param_desc = param_info.get("description", "No description")
            default_val = param_info.get("default_value", "Not specified")
            content += f"- **{param_name}**: {param_desc} (Default: {default_val})\n"
        
        return content + "\n"
    
    def _get_trading_logic_test_cases(self):
        """Generate trading logic test case descriptions."""
        entry_conditions = self.analysis.get("trading_logic", {}).get("entry_conditions", [])
        exit_conditions = self.analysis.get("trading_logic", {}).get("exit_conditions", [])
        
        content = """### Test Cases

| Test Name | Input | Expected Output | Success Criteria |
|-----------|-------|-----------------|-------------------|
| **test_trading_hours_enforcement** | Various times: 10:00, 12:00, 15:30 | Time validation | ✅ All times within market hours (9:30 AM - 4:00 PM) |
| **test_entry_signal_conditions** | Real S&P 500 data (2023-01-01 to 2023-01-31) | Signal generation validation | ✅ Entry logic processes real market data correctly |
| **test_exit_signal_conditions** | Real S&P 500 data with positions | Exit signal validation | ✅ Exit logic triggers appropriately on real data |
| **test_position_sizing_logic** | Account balance, risk parameters | Position size calculations | ✅ Proper position sizing based on account and risk rules |
| **test_signal_timing_accuracy** | Tick-by-tick data sequences | Signal timing validation | ✅ Signals generated at correct market moments |

**Trading Logic Coverage:**
"""
        
        if entry_conditions:
            content += "**Entry Conditions Tested:**\n"
            for condition in entry_conditions[:5]:  # Limit to first 5
                content += f"- {condition.strip()}\n"
        
        if exit_conditions:
            content += "\n**Exit Conditions Tested:**\n"
            for condition in exit_conditions[:5]:  # Limit to first 5
                content += f"- {condition.strip()}\n"
        
        content += """
**Real Market Scenarios:**
- Tests against actual S&P 500 intraday patterns
- Validates signal generation during high volatility periods
- Ensures proper handling of market gaps and news events

"""
        return content
    
    def _get_ui_test_cases(self):
        """Generate UI component test case descriptions."""
        return """### Test Cases

| Test Name | Input | Expected Output | Success Criteria |
|-----------|-------|-----------------|-------------------|
| **test_parameter_input_widgets** | Streamlit slider, selectbox, text_input | Widget functionality | ✅ All input widgets respond correctly to user interaction |
| **test_chart_generation** | Market data, Plotly figure | Chart display | ✅ Charts render properly with correct data visualization |
| **test_real_time_data_display** | Live market data feed | Updated UI components | ✅ UI updates reflect real-time data changes |
| **test_strategy_metrics_display** | Performance statistics | Metrics dashboard | ✅ All key metrics displayed accurately and updated |
| **test_trade_history_table** | Trade execution records | Formatted data table | ✅ Trade history shows complete and accurate information |
| **test_interactive_controls** | User button/slider interactions | UI state changes | ✅ Interactive elements modify strategy behavior correctly |
| **test_export_functionality** | Generated reports/data | Download triggers | ✅ Export functions create proper CSV/PDF files |
| **test_responsive_design** | Various screen sizes | Layout adaptation | ✅ UI remains functional across different screen sizes |

**UI Framework Integration:**
- **Streamlit Components**: Sliders, buttons, selectboxes, file uploaders
- **Chart Libraries**: Plotly for candlestick charts, performance graphs
- **Data Display**: Real-time tables, metrics dashboards
- **Export Features**: CSV downloads, PDF report generation

**User Experience Testing:**
- Validates intuitive parameter adjustment workflows
- Tests error message display and user guidance
- Ensures responsive design across devices
- Verifies accessibility compliance

"""
    
    def _get_risk_management_test_cases(self):
        """Generate risk management test case descriptions."""
        risk_controls = self.analysis.get("risk_management", {}).get("risk_controls", [])
        
        content = """### Test Cases

| Test Name | Input | Expected Output | Success Criteria |
|-----------|-------|-----------------|-------------------|
| **test_position_size_limits** | Account size, risk percentage | Position size calculation | ✅ Position size never exceeds maximum risk limits |
| **test_stop_loss_enforcement** | Trade positions, price movements | Stop loss triggers | ✅ Stop losses execute at correct price levels |
| **test_maximum_drawdown_controls** | Portfolio performance history | Drawdown monitoring | ✅ Trading halts when maximum drawdown reached |
| **test_risk_per_trade_validation** | Individual trade parameters | Risk calculation | ✅ Each trade risk stays within specified limits |
| **test_leverage_constraint_enforcement** | Margin requirements, position sizes | Leverage validation | ✅ Leverage never exceeds regulatory/internal limits |
| **test_correlation_risk_monitoring** | Multiple positions, correlation matrix | Portfolio risk assessment | ✅ Correlation limits enforced across positions |
| **test_emergency_position_closure** | Risk threshold breaches | Automatic closure triggers | ✅ Emergency procedures execute correctly |

**Risk Management Coverage:**
"""
        
        if risk_controls:
            content += "**Risk Controls Tested:**\n"
            for control in risk_controls[:7]:  # Limit to first 7
                content += f"- {control.strip()}\n"
        
        leverage_limits = self.analysis.get("risk_management", {}).get("leverage_constraints", [])
        if leverage_limits:
            content += f"\n**Leverage Limits:** {', '.join(leverage_limits)}:1\n"
        
        drawdown_limits = self.analysis.get("risk_management", {}).get("drawdown_limits", [])
        if drawdown_limits:
            content += f"**Drawdown Limits:** {', '.join(drawdown_limits)}%\n"
        
        content += """
**Real Market Risk Testing:**
- Tests risk controls against actual market crash scenarios (2020 COVID, 2022 inflation)
- Validates stop loss execution during high volatility periods
- Ensures position sizing remains appropriate during extreme market conditions

"""
        return content
    
    def _get_transaction_cost_test_cases(self):
        """Generate transaction cost test case descriptions."""
        return """### Test Cases

| Test Name | Input | Expected Output | Success Criteria |
|-----------|-------|-----------------|-------------------|
| **test_spread_cost_calculation** | Bid-ask spreads, position sizes | Cost calculations | ✅ Spread costs calculated accurately for all position sizes |
| **test_commission_fee_application** | Trade executions, broker rates | Fee calculations | ✅ Commission fees applied correctly per trade |
| **test_slippage_impact_modeling** | Market conditions, order sizes | Slippage estimates | ✅ Slippage impact modeled realistically for different conditions |
| **test_overnight_funding_costs** | Held positions, funding rates | Funding calculations | ✅ Overnight costs calculated correctly for CFD positions |
| **test_currency_conversion_costs** | Multi-currency trades | Conversion fees | ✅ FX conversion costs included in total trade cost |
| **test_total_cost_impact_analysis** | Complete trade scenarios | Net P&L calculations | ✅ All costs properly netted against gross profits |

**Cost Components Tested:**
- **Spread Costs**: Bid-ask spread impact on entry/exit
- **Commission Fees**: Broker charges per trade
- **Slippage**: Market impact and execution delays
- **Funding Costs**: Overnight CFD position charges
- **Currency Costs**: FX conversion fees for international assets

**Real Cost Validation:**
- Uses actual broker cost structures
- Tests against historical spread data
- Validates cost impact during different market conditions

"""
    
    def _get_performance_analytics_test_cases(self):
        """Generate performance analytics test case descriptions."""
        return """### Test Cases

| Test Name | Input | Expected Output | Success Criteria |
|-----------|-------|-----------------|-------------------|
| **test_trade_pnl_calculations** | Trade execution data | P&L metrics | ✅ Gross and net P&L calculated correctly for all trades |
| **test_win_rate_statistics** | Trade outcomes history | Win rate percentage | ✅ Win rate accurately reflects successful vs. total trades |
| **test_risk_adjusted_returns** | Returns, volatility data | Sharpe ratio, Sortino ratio | ✅ Risk-adjusted metrics calculated using proper formulas |
| **test_drawdown_analysis** | Equity curve data | Maximum drawdown metrics | ✅ Drawdown calculations identify peak-to-trough declines |
| **test_trade_duration_analysis** | Entry/exit timestamps | Duration statistics | ✅ Average, median, min/max trade durations calculated |
| **test_portfolio_correlation_metrics** | Multi-strategy returns | Correlation analysis | ✅ Portfolio diversification metrics computed correctly |
| **test_benchmark_comparison** | Strategy vs. S&P 500 returns | Relative performance | ✅ Alpha, beta, and tracking error calculated accurately |

**Analytics Coverage:**
- **Return Metrics**: Total return, annualized return, excess return
- **Risk Metrics**: Volatility, VaR, maximum drawdown, downside deviation
- **Ratio Analysis**: Sharpe, Sortino, Calmar, information ratios
- **Trade Analytics**: Win rate, average win/loss, profit factor
- **Timing Analysis**: Trade duration, holding periods, turnover

**Real Performance Validation:**
- Tests calculations against known benchmark results
- Uses actual S&P 500 data for comparison metrics
- Validates performance during different market regimes

"""
    
    def _get_edge_case_test_cases(self):
        """Generate edge case test case descriptions."""
        return """### Test Cases

| Test Name | Input | Expected Output | Success Criteria |
|-----------|-------|-----------------|-------------------|
| **test_market_gap_handling** | Price data with overnight gaps | Gap processing | ✅ Strategy handles price gaps without errors or incorrect signals |
| **test_extreme_volatility_response** | High VIX periods (>30) | Volatility adaptation | ✅ Strategy adjusts appropriately to extreme market conditions |
| **test_low_liquidity_scenarios** | Thin volume periods | Liquidity handling | ✅ Strategy recognizes and adapts to low liquidity conditions |
| **test_data_feed_interruptions** | Missing/delayed data | Error handling | ✅ Graceful degradation when data feeds fail |
| **test_holiday_market_conditions** | Holiday trading data | Special condition handling | ✅ Strategy adapts to shortened/unusual trading sessions |
| **test_circuit_breaker_events** | Market halt scenarios | Trading suspension response | ✅ Strategy stops appropriately during market halts |
| **test_flash_crash_scenarios** | Rapid price movements | Extreme event handling | ✅ Risk controls activate during flash crash conditions |
| **test_earnings_announcement_impacts** | High volatility around earnings | Event handling | ✅ Strategy manages increased volatility around scheduled events |

**Edge Case Categories:**
- **Market Structure Events**: Circuit breakers, trading halts, settlement days
- **Data Quality Issues**: Missing ticks, delayed feeds, incorrect prices
- **Extreme Market Conditions**: Flash crashes, limit moves, unprecedented volatility
- **Technical Failures**: Connection losses, system outages, order routing failures
- **Regulatory Events**: New rules, margin changes, trading restrictions

**Real Edge Case Testing:**
- Uses actual historical events (2010 Flash Crash, 2020 COVID crash)
- Tests against real market halt and circuit breaker data
- Validates behavior during actual earnings seasons and FOMC meetings

"""
    
    def _get_integration_test_cases(self):
        """Generate integration test case descriptions."""
        return """### Test Cases

| Test Name | Input | Expected Output | Success Criteria |
|-----------|-------|-----------------|-------------------|
| **test_end_to_end_strategy_execution** | Complete market session | Full strategy run | ✅ Strategy executes from market open to close without errors |
| **test_data_to_signals_pipeline** | Real market data stream | Trading signals | ✅ Data flows correctly through analysis to signal generation |
| **test_signals_to_execution_integration** | Generated signals | Trade executions | ✅ Signals translate properly to actual trade orders |
| **test_risk_management_integration** | Live positions, market moves | Risk control actions | ✅ Risk management integrates seamlessly with trading logic |
| **test_ui_to_strategy_communication** | UI parameter changes | Strategy updates | ✅ UI changes immediately reflect in strategy behavior |
| **test_multi_timeframe_coordination** | Multiple data frequencies | Coordinated analysis | ✅ Different timeframes work together correctly |
| **test_cross_component_error_handling** | Simulated component failures | Error propagation | ✅ Errors handled gracefully across all components |

**Integration Scope:**
- **Data Pipeline**: Market data → Processing → Analysis → Signals
- **Execution Chain**: Signals → Risk checks → Order generation → Execution
- **UI Integration**: User interface ↔ Strategy parameters ↔ Display updates
- **Risk Integration**: All components respect risk management rules
- **Error Handling**: Failures in one component don't crash others

**System-Level Validation:**
- Tests complete trading day simulation
- Validates component interaction under stress
- Ensures data consistency across all system parts

"""
    
    def _get_performance_benchmark_test_cases(self):
        """Generate performance benchmark test case descriptions."""
        return """### Test Cases

| Test Name | Input | Expected Output | Success Criteria |
|-----------|-------|-----------------|-------------------|
| **test_backtest_execution_speed** | 1 year of daily data | Execution time | ✅ Backtest completes in < 30 seconds |
| **test_memory_usage_efficiency** | Full dataset processing | Memory consumption | ✅ Memory usage stays < 2GB during execution |
| **test_real_time_processing_latency** | Live data feeds | Processing delays | ✅ Signal generation latency < 100ms |
| **test_concurrent_strategy_performance** | Multiple strategy instances | Parallel execution | ✅ Multiple strategies run without interference |
| **test_large_dataset_scalability** | 10+ years of intraday data | Scalability metrics | ✅ Performance degrades gracefully with data size |
| **test_ui_responsiveness_benchmarks** | Complex chart rendering | UI update times | ✅ UI updates complete within 5 seconds |

**Performance Targets:**
- **Execution Speed**: Backtests complete quickly for iterative development
- **Memory Efficiency**: Handles large datasets without memory issues
- **Real-time Performance**: Low latency for live trading applications
- **Scalability**: Performance remains acceptable as data grows
- **UI Responsiveness**: Interface stays responsive during heavy computation

**Benchmark Validation:**
- Compares against industry-standard performance metrics
- Tests on realistic dataset sizes for production trading
- Validates performance across different hardware configurations

"""
    
    def _get_compliance_test_cases(self):
        """Generate regulatory compliance test case descriptions."""
        return """### Test Cases

| Test Name | Input | Expected Output | Success Criteria |
|-----------|-------|-----------------|-------------------|
| **test_position_limit_compliance** | Large position requests | Position validation | ✅ Positions never exceed regulatory limits |
| **test_leverage_ratio_enforcement** | High leverage scenarios | Leverage validation | ✅ Leverage stays within regulatory boundaries |
| **test_risk_disclosure_requirements** | Strategy documentation | Disclosure validation | ✅ All required risk warnings present |
| **test_trade_reporting_accuracy** | Trade executions | Reporting validation | ✅ All trades reported with required accuracy |
| **test_margin_requirement_compliance** | Margin calculations | Regulatory validation | ✅ Margin requirements meet regulatory standards |
| **test_client_suitability_checks** | Client profiles, strategy risk | Suitability validation | ✅ Strategy appropriate for client risk profiles |

**Regulatory Framework Coverage:**
- **SEC Regulations**: US securities law compliance
- **CFTC Rules**: Commodity and derivatives regulations  
- **Risk Management Rules**: Basel III, Dodd-Frank requirements
- **Reporting Standards**: Trade reporting and record keeping
- **Client Protection**: Suitability and disclosure requirements

**Compliance Validation:**
- Tests against current regulatory requirements
- Validates proper risk disclosure documentation
- Ensures audit trail completeness and accuracy

"""
    
    def _get_generic_test_cases(self, category: str, info: dict):
        """Generate generic test case descriptions for unknown categories."""
        category_name = category.replace('_', ' ').title()
        
        return f"""### Test Cases

| Test Name | Input | Expected Output | Success Criteria |
|-----------|-------|-----------------|-------------------|
| **test_{category}_basic_functionality** | Standard test inputs | Basic operation validation | ✅ Core {category_name.lower()} functionality works correctly |
| **test_{category}_integration** | Integration with strategy components | Component interaction | ✅ {category_name} integrates properly with main strategy |
| **test_{category}_error_handling** | Invalid inputs, error conditions | Error management | ✅ Proper error handling and recovery mechanisms |
| **test_{category}_performance** | Performance benchmarking inputs | Execution metrics | ✅ {category_name} performance meets requirements |

**Category Description:**
{info.get('description', f'Tests for {category_name} functionality')}

**Coverage Areas:**
- Basic functionality validation
- Integration with other strategy components
- Error handling and edge cases
- Performance and scalability testing

"""


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