# OpenBB Test Framework Generator

**Interactive Test Framework Generation for Trading Strategies**

This directory contains the intelligent test framework generator system that creates comprehensive, pytest-based testing suites for any OpenBB trading strategy. The generator uses a **smart document analysis approach** - it first extracts information from your requirements document, then only asks about gaps or unclear areas. No assumptions are made; all tests are based purely on what you specify.

## 🚀 Quick Start

### Generate a Test Framework (Interactive)

```bash
cd test_framework/test_setup
./build_test_env.sh name:<framework_name> requirements:<requirements_document>
```

**Example:**
```bash
./build_test_env.sh name:SPX_V1 requirements:"docs/strategies/SPX/revised_cfd_strategy.md"
```

**What happens:**
1. **Document Analysis**: Automatically extracts strategy type, data sources, components from your document
2. **Interactive Questions**: Only asks about information not found in the document
3. **Test Generation**: Creates tests based purely on your specifications
4. **No Assumptions**: Unlike generic test frameworks, this makes zero assumptions about your strategy

### Run Generated Tests

```bash
cd ../SPX_V1
python run_tests.py
```

## 📋 Prerequisites

- **Python 3.8+** with OpenBB-env conda environment
- **Strategy requirements document** (Markdown format)
- **OpenBB market data access** (for real data testing)
- **All generator scripts executable** (automatically set during setup)

## 🏗️ What Gets Generated

Each generated test framework includes:

```
YourStrategy/
├── tests/                          # 188+ test cases across 10+ categories
│   ├── test_data_management.py     # Market data validation tests
│   ├── test_strategy_parameters.py # Parameter validation tests
│   ├── test_trading_logic.py       # Entry/exit signal tests
│   ├── test_risk_management.py     # Risk control tests
│   ├── test_ui_components.py       # Streamlit UI tests
│   └── ...                         # Additional category tests
├── fixtures/                       # Test data fixtures
├── results/                        # Test execution results
├── conftest.py                     # Pytest configuration & real data fixtures
├── pytest.ini                     # Pytest settings
├── requirements.txt                # Testing dependencies
├── run_tests.py                   # Command line test runner
├── install_packages.sh            # Dependency installation
├── check_environment.sh           # Environment validation
├── README.md                      # Framework usage guide
├── YourStrategy_testing.md        # Comprehensive test plan
└── test_cases_summary.md          # Human-readable test case descriptions
```

## 📖 Interactive Framework Process

### Phase 1: Smart Document Analysis (Automatic)

The framework **automatically extracts** from your requirements document:

- **Strategy Type**: CFD, forex, crypto, backtesting, live trading, etc.
- **Target Instruments**: S&P 500, forex pairs, crypto symbols, etc.
- **Data Requirements**: Real-time feeds, historical data, broker APIs, etc.
- **System Components**: Trading logic, risk management, UI, order execution, etc.
- **Strategy Description**: Executive summary and key details

**No user input needed** - the system reads and understands your document!

### Phase 2: Gap Analysis (Interactive)

The system **only asks** about information missing from your document:

- Testing priorities (if not specified)
- Specific data sources (if unclear)
- Data frequencies (if not mentioned)
- Test categories for each component found

### Requirements Document Format

Your Markdown document can be in **any format**. The system intelligently extracts information using pattern matching:

**Example: The system automatically detects:**

```markdown
# S&P 500 CFD Strategy

## Executive Summary
This CFD strategy trades S&P 500 using real-time broker feeds...

## Risk Management
- Stop Loss: 4 points below entry
- Position sizing based on 1% account risk
- Maximum leverage: 5:1

## Implementation Requirements
### Broker Selection
- Regulated CFD provider with real-time feeds
- Spreads ≤ 1.0 points during trading hours
```

**What gets extracted automatically:**
- ✅ Strategy Type: "Live Trading Strategy (CFD)"
- ✅ Instruments: "S&P 500, CFD"
- ✅ Data Sources: "broker feeds, real-time"
- ✅ Components: "Risk management, order execution"

**What gets asked:**
- ❓ "What are your main testing goals?" (not in document)
- ❓ "Generate tests for Risk Management? (Found in document)"

### 2. Interactive Generation Process

```bash
./build_test_env.sh name:MyStrategy requirements:"path/to/strategy.md"
```

**Interactive Session Example:**
```
🎯 Smart Requirements Analysis for: MyStrategy
============================================================
First, I'll extract what I can from the requirements document.
Then I'll only ask about gaps or unclear areas.
============================================================

🔍 STEP 1: Extracting information from requirements document...
✅ Strategy Type: Live Trading Strategy (CFD)
✅ Target Instruments: S&P 500, ES, CFD
✅ Needs Data: True
   - Data Types: Real-time price feeds, Broker-specific data
   - Data Sources: trading platform
   - Frequencies: intraday
✅ System Components Found: 7
   - Trading logic/algorithms
   - Risk management systems
   - Order execution systems
   - Performance monitoring
   - Configuration/parameter management
   - User interface
   - External API integrations

❓ STEP 2: Asking about gaps and unclear areas...
Now I'll ask about anything that wasn't clear from the document...

❓ What are your main testing goals for this strategy?
   1. Verify correctness
   2. Performance testing
   3. Error handling
   4. Integration testing
   5. Regression testing
   6. All of the above
   > 6

❓ Which areas are highest priority for testing?
   > Trading logic validation, risk management, order execution

❓ Generate comprehensive tests for Trading logic/algorithms? (Found in document)
   1. Yes - High Priority
   2. Yes - Medium Priority
   3. Yes - Low Priority
   4. Skip
   > 1

✅ Analysis complete. Results saved to analysis file.
📊 Total Estimated Tests: 67
```

**Final Output:**
```
🎉 Test framework 'MyStrategy' generated successfully!
📁 Framework location: test_framework/MyStrategy
📈 Total Estimated Tests: 67 (based on your specifications)
```

### 3. Install Dependencies

```bash
cd ../MyStrategy
./install_packages.sh
```

This installs all required testing packages into your OpenBB-env environment.

### 4. Run Tests

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

## 🔧 Interactive Generator Components

### Core Scripts

| Script | Purpose | How It Works |
|--------|---------|-------------|
| `build_test_env.sh` | Main orchestrator | Runs all generation steps in sequence |
| `analyze_requirements.py` | **Interactive analyzer** | **Phase 1**: Extracts from document<br>**Phase 2**: Asks about gaps |
| `generate_tests_interactive.py` | **Assumption-free test generator** | Creates tests based **purely** on user specifications |
| `generate_config.py` | Configuration generator | Uses user input instead of assumptions |
| `generate_runner.py` | Test runner generator | Creates command-line test runner |
| `generate_docs.py` | Documentation generator | Documents user requirements and assumptions |

### Key Features

| Feature | Old Approach | New Interactive Approach |
|---------|-------------|-------------------------|
| **Data Sources** | ❌ Assumed yfinance | ✅ Extracts from document ("broker feeds", "trading platform") |
| **Strategy Type** | ❌ Generic templates | ✅ Document analysis ("CFD", "live trading", "backtesting") |
| **Test Categories** | ❌ All categories | ✅ Only components found in document + user priorities |
| **Assumptions** | ❌ Undocumented | ✅ All assumptions explicitly confirmed by user |
| **Requirements** | ❌ Ignored documents | ✅ Document-first analysis |

### Template Files

| Template | Purpose | Used For |
|----------|---------|----------|
| `templates/install_packages_template.sh` | Package installer | Dependency setup |
| `templates/check_environment_template.sh` | Environment validator | System verification |

## 📊 Interactive Test Category Generation

**The framework only generates tests for components found in your document:**

### Document Analysis Example (CFD Strategy)
```
✅ System Components Found: 7
   - Trading logic/algorithms        → User priority: High (18 tests)
   - Risk management systems         → User priority: High (15 tests) 
   - Order execution systems         → User priority: High (12 tests)
   - Performance monitoring          → User priority: Medium (8 tests)
   - Configuration/parameter mgmt    → User priority: Medium (6 tests)
   - User interface                  → User priority: Low (4 tests)
   - External API integrations       → User priority: Medium (8 tests)
```

### User Control
**For each component found, you choose:**
- ✅ **Yes - High Priority**: Comprehensive test suite
- ✅ **Yes - Medium Priority**: Core functionality tests
- ✅ **Yes - Low Priority**: Basic validation tests
- ❌ **Skip**: No tests generated

### Result: Tailored Test Suite
- **Total Tests**: Based on your priorities (typically 40-80 tests)
- **Categories**: Only components you actually have
- **Focus**: Your highest priority areas get most tests
- **No Waste**: No tests for components you don't use

## 🎯 Real Market Data Integration

Unlike traditional mock data approaches, this framework uses **real market data** for testing:

### Benefits
- **Authentic Market Conditions**: Tests against actual price gaps, volatility, events
- **Real Edge Cases**: Includes market crashes, holidays, trading halts
- **No Artificial Bias**: Prevents unconsciously favorable mock data
- **Production Confidence**: Real data success ≈ live trading success

### Data Sources (User-Specified)
The framework now generates tests based on **your actual data sources**:

**For CFD Strategies**:
1. **Primary**: Broker API/feeds (as specified in requirements)
2. **Secondary**: Real-time trading platform data
3. **Fallback**: Test-compatible data with realistic market patterns

**For Backtesting Strategies**:
1. **Primary**: yfinance/OpenBB (if specified in requirements)
2. **Secondary**: Historical data files
3. **Fallback**: Realistic market data for testing

**No Assumptions**: Tests are generated only for data sources you actually specify!

### Example Real Data Coverage
```
SPX Data (2020-2023): 1,006 trading days
- Price range: $2,237 to $4,797
- Max daily drop: -12.0% 
- Max daily gain: +9.4%
- High volatility days (>3%): 40 days
- Market regimes: COVID crash, recovery, inflation, AI rally
```

## 🧪 Test Execution Features

### Command Line Runner
- **Real-time logging**: `[timestamp] Executing test: test_name`
- **Progress tracking**: Visual indicators for pass/fail
- **Multiple output formats**: Text, JSON, XML reports
- **Category filtering**: Run specific test groups
- **Marker support**: Filter by test characteristics
- **Coverage reporting**: Code coverage analysis

### Example Output
```
================================================================================
🧪 SPX_V1 TESTING FRAMEWORK
================================================================================
[17:30:51] Executing test: test_market_data_provider_connection
[17:30:51] test_market_data_provider_connection: PASS ✅
[17:31:08] Executing test: test_data_frequency_mapping  
[17:31:37] test_data_frequency_mapping: PASS ✅

Total Tests: 188
✅ Passed: 185
❌ Failed: 2  
⏭️  Skipped: 1
Success Rate: 98.4%
🎉 OVERALL RESULT: TESTS MOSTLY PASSED
```

## 📁 File Structure Details

### Generated Test Files
Each test file follows pytest best practices:

```python
# test_data_management.py
class TestMarketDataRetrieval:
    @pytest.mark.unit
    @pytest.mark.data
    def test_market_data_provider_connection(self, test_logger):
        """Verify connection to market data providers."""
        # Real market data testing logic
        
    @pytest.mark.unit  
    @pytest.mark.data
    def test_data_format_consistency(self, test_logger, real_market_data):
        """Verify OHLCV data format consistency."""
        data = real_market_data(symbol="GSPC", start_date="2023-01-01", end_date="2023-01-31")
        # Validation logic with real data
```

### Configuration Files
- **pytest.ini**: Test runner configuration, markers, warnings
- **conftest.py**: Global fixtures, real market data integration
- **requirements.txt**: All testing dependencies

### Documentation Files
- **README.md**: Framework usage instructions
- **{Strategy}_testing.md**: Comprehensive test plan with 200+ detailed test descriptions
- **test_cases_summary.md**: Human-readable test case table with inputs/outputs

## 🔍 Customization Options

### Adding Custom Tests
1. Create new test file in `tests/` directory
2. Follow naming convention: `test_<category>.py`
3. Use appropriate pytest markers
4. Include test logger for execution tracking

### Modifying Test Categories
Edit `analyze_requirements.py` to:
- Add new category detection patterns
- Modify test count allocations
- Update category priorities

### Extending Real Data Sources
Modify `generate_config.py` to:
- Add new data providers
- Include additional symbols
- Support new frequencies

## 🚨 Troubleshooting

### Interactive Session Issues

**EOF Error During Interactive Session**
```
EOFError: EOF when reading a line
```
**Solution**: Run in interactive terminal, not from IDE or script
```bash
# Run from actual terminal
terminal$ ./build_test_env.sh name:MyStrategy requirements:"path/to/doc.md"
```

**Document Not Found**
```bash
# Verify document path (relative to OpenBB root)
ls -la "docs/strategies/SPX/revised_cfd_strategy.md"

# Check current directory
pwd  # Should be in test_framework/test_setup
```

**No Components Extracted**
```
✅ System Components Found: 0
```
**Solution**: Add keywords to your document that the system recognizes:
- Trading logic: "entry", "exit", "signal", "algorithm"
- Risk management: "risk", "stop loss", "position size"
- UI: "streamlit", "dashboard", "interface", "web"
- Order execution: "order", "execution", "broker", "trade"

**Tests Fail to Collect**
```bash
# Verify pytest configuration
cat pytest.ini

# Check Python path setup
python -c "import sys; print('\n'.join(sys.path))"
```

**Real Data Connection Issues**
```bash
# Test market data access
python -c "
import sys
sys.path.insert(0, '../app/SP500_CFD_v1')
from market_data import Retrieve
r = Retrieve()
data = r.get_data('GSPC', '2023-01-01', '2023-01-31', '1D')
print(f'Retrieved {len(data)} records')
"
```

**Missing Dependencies**
```bash
# Install testing packages
./install_packages.sh

# Verify environment
./check_environment.sh
```

## 📈 Best Practices

### Writing Effective Requirements Documents

**For Better Document Analysis:**
- **Use Keywords**: Include "CFD", "live trading", "backtesting", "real-time", "broker"
- **Be Specific**: "S&P 500 CFD" vs. "equity trading"
- **Mention Components**: "risk management", "order execution", "user interface"
- **Data Sources**: "broker API", "yfinance", "real-time feeds", "historical data"

**Example Good Document Sections:**
```markdown
## Strategy Type
This is a live CFD trading strategy for S&P 500 futures.

## Data Requirements  
Strategy uses real-time broker feeds via trading platform API.

## System Components
- Trading logic for entry/exit signals
- Risk management with stop losses
- Order execution via broker API
- Performance monitoring dashboard
```

**The system will extract:**
- ✅ Strategy Type: "Live Trading Strategy (CFD)"
- ✅ Instruments: "S&P 500, CFD, futures"
- ✅ Data: "real-time broker feeds, trading platform API"
- ✅ Components: 4 components found

### Test Execution
- **Run frequently**: Execute tests during strategy development
- **Use categories**: Focus on relevant test groups during debugging
- **Monitor performance**: Track test execution times
- **Review failures**: Investigate failed tests thoroughly

### Framework Maintenance
- **Update regularly**: Regenerate framework when requirements change
- **Add custom tests**: Include strategy-specific test scenarios
- **Monitor real data**: Ensure data sources remain accessible
- **Document changes**: Track modifications for team awareness

## 🔗 Integration with Development Workflow

### Pre-commit Testing
```bash
# Quick validation
python run_tests.py --markers "unit and not slow"

# Full validation  
python run_tests.py --coverage
```

### CI/CD Integration
The test runner returns appropriate exit codes:
- `0`: All tests passed
- `1`: Some tests failed or errors occurred

### Performance Monitoring
- Individual test timeouts
- Category-level benchmarks  
- Memory usage tracking
- UI responsiveness metrics

---

## 📞 Support

For issues with the test framework generator:
1. Check test execution logs in `results/`
2. Verify environment with `./check_environment.sh`
3. Review requirements document format
4. Check generator script permissions and paths

**Generated Frameworks:** Each framework is self-contained with its own README and documentation for framework-specific usage instructions.