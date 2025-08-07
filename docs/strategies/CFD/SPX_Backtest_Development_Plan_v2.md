# SPX CFD Backtest Application - Development Plan v2.0

## Overview
This document outlines the revised development plan for creating a comprehensive SPX (S&P 500) historical backtest application for trading Long/Short Contracts for Difference (CFDs) using Test-Driven Development (TDD) methodology and Streamlit as the frontend framework.

## Key Changes from v1.0
- **TDD Approach**: Write tests before code implementation
- **2 basis point trigger**: Entry signals based on +/- 2bps price movement from opening price
- **Daily P&L tracking**: End-of-day summary with charting
- **Command-line debugging**: Real-time trade output during development
- **Simplified PDF reporting**: Summary statistics and charts only
- **Risk-free rate parameter**: Configurable input for Sharpe ratio (default 3%)
- **Multiple VaR horizons**: 1, 3, and 5-day Value at Risk calculations
- **Enhanced metrics**: Additional tracking for long/short trades and average drawdown

## Application Architecture

### Core Components
1. **Streamlit Frontend Application**
   - Location: `OpenBB/app/SPX_CFD_Backtest.py`
   - Framework: Streamlit with sidebar parameter controls
   - Visualization: Plotly charts for performance metrics
   - Export: PDF report generation capability

2. **CFD Trading Engine**
   - Location: `OpenBB/app/common/cfd_engine.py`
   - Responsibilities: 2bps trigger logic, position management, P&L calculations
   - Integration: Uses existing `market_data.py` via `from_file` static method

3. **Backtest Results Analysis**
   - Location: `OpenBB/app/common/backtest_analyzer.py`
   - Responsibilities: Performance metrics calculation, daily P&L tracking, reporting

4. **PDF Report Generator**
   - Location: `OpenBB/app/common/pdf_generator.py`
   - Dependencies: ReportLab (already installed in OpenBB-env)
   - Content: Summary statistics and embedded charts only

## Test-Driven Development Strategy

### Testing Framework Setup
- **Framework**: pytest (already installed in OpenBB-env)
- **Location**: `OpenBB/test_framework/SPX_CFD/`
- **Best Practices**: Following guidelines from `docs/TDD/Python_Unit_Testing_Best_Practices.pdf`

### Test Structure
```
test_framework/SPX_CFD/
├── test_cfd_engine.py              # Core trading logic tests
├── test_backtest_analyzer.py       # Performance metrics tests  
├── test_market_data_integration.py # Data access tests
├── test_pdf_generator.py           # Report generation tests
├── test_integration.py             # End-to-end backtest tests
├── conftest.py                     # Shared fixtures
└── fixtures/                       # Test data files
    ├── sample_5M_data.txt          # Small sample for testing
    └── expected_results.json       # Known good results
```

## Development Phases

### Phase 1: TDD Foundation & Core Logic (Week 1)
**Priority: High - Write Tests First**

#### 1.1 Test Setup and Data Fixtures
- **File**: `test_framework/SPX_CFD/conftest.py`
- Create pytest fixtures for:
  - Sample market data (small 5M dataset)
  - Mock CFD parameters
  - Expected calculation results
- **Test Principles**: Fast, independent, deterministic tests

#### 1.2 CFD Engine Core Logic Tests
- **File**: `test_framework/SPX_CFD/test_cfd_engine.py`
- **Tests to Write First**:
  ```python
  def test_2bps_long_entry_trigger()
  def test_2bps_short_entry_trigger()
  def test_position_sizing_calculation()
  def test_stop_loss_logic()
  def test_profit_target_calculation()
  def test_trailing_stop_logic()
  def test_end_of_day_closure()
  def test_opening_price_reset()
  ```

#### 1.3 Implement CFD Trading Engine
- **File**: `app/common/cfd_engine.py`
- **Classes**:
  ```python
  class CFDPosition:
      # Represents single position state
      
  class CFDTradingEngine:
      def __init__(self, account_balance, risk_pct, ...)
      def process_tick(self, timestamp, ohlc_data)
      def check_entry_signals(self, current_price)  # ±2bps logic
      def enter_trade(self, direction, price)
      def update_position(self, current_price, high, low)
      def check_exit_conditions(self, current_price, timestamp)
      def close_position(self, exit_price, reason)
  ```

#### 1.4 Market Data Integration Tests
- **File**: `test_framework/SPX_CFD/test_market_data_integration.py`
- Test `market_data.py.from_file()` integration
- Verify data format handling and time filtering
- Test market hours enforcement (09:30-16:00)

### Phase 2: Performance Analysis & TDD Continuation (Week 2)
**Priority: High**

#### 2.1 Performance Metrics Tests
- **File**: `test_framework/SPX_CFD/test_backtest_analyzer.py`
- **Tests for All 22 Metrics**:
  ```python
  def test_basic_trade_metrics()      # total_trades, winning_trades, etc.
  def test_pnl_calculations()         # total_pnl, gross_pnl, total_costs
  def test_win_loss_averages()        # avg_win, avg_loss, win_rate
  def test_drawdown_calculations()    # max_drawdown, avg_drawdown
  def test_return_metrics()           # total_return, final_equity
  def test_risk_metrics()             # sharpe_ratio, profit_factor
  def test_time_based_metrics()       # trade duration calculations
  def test_var_calculations()         # VaR at 1, 3, 5 day horizons
  def test_long_short_breakdowns()    # total_long_trades, total_short_trades
  def test_daily_pnl_aggregation()    # End-of-day P&L summaries
  ```

#### 2.2 Implement Backtest Analyzer
- **File**: `app/common/backtest_analyzer.py`
- **Classes**:
  ```python
  class BacktestAnalyzer:
      def __init__(self, risk_free_rate=0.03)
      def add_trade(self, trade_result)
      def add_daily_close(self, date, daily_pnl)
      def calculate_all_metrics(self)
      def calculate_sharpe_ratio(self, returns)
      def calculate_var(self, returns, confidence=0.95, horizons=[1,3,5])
      def calculate_drawdowns(self, equity_curve)
      def get_results_summary(self)
  ```

#### 2.3 Entry Signal Logic Implementation
- **2 Basis Points Trigger Logic**:
  ```python
  def check_entry_signals(self, current_price, opening_price):
      price_change_bps = ((current_price - opening_price) / opening_price) * 10000
      
      if price_change_bps >= 2.0 and not self.position_active:
          return "LONG"
      elif price_change_bps <= -2.0 and not self.position_active:
          return "SHORT"
      return None
  ```

### Phase 3: Integration & User Interface (Week 3)
**Priority: Medium**

#### 3.1 Integration Tests
- **File**: `test_framework/SPX_CFD/test_integration.py`
- End-to-end backtest execution tests
- Test with historical data sample (3-month window)
- Validate complete workflow from data input to results

#### 3.2 Streamlit Interface Development
- **File**: `app/SPX_CFD_Backtest.py`
- **Sidebar Parameters** (with defaults from CFD_Calculator.html):
  ```python
  # Account Settings
  account_balance = st.sidebar.number_input("Account Balance ($)", value=10000)
  account_risk_pct = st.sidebar.number_input("Account Risk per Trade (%)", value=2.0)
  transaction_cost = st.sidebar.number_input("Round Trip Cost per CFD ($)", value=5.0)
  
  # Data Settings  
  start_date = st.sidebar.date_input("Start Date", value=date(2008, 1, 2))
  end_date = st.sidebar.date_input("End Date", value=date(2008, 4, 2))  # 3 month default
  frequency = st.sidebar.selectbox("Frequency", ["1M", "5M", "30M", "1H", "1D"], index=1)
  
  # CFD Parameters
  stop_loss_distance = st.sidebar.number_input("Initial Stop-Loss Distance ($)", value=50.0)
  risk_reward_ratio = st.sidebar.number_input("Risk/Reward Ratio", value=2.0)
  trailing_stop_pct = st.sidebar.number_input("Trailing Stop Percentage (%)", value=2.0)
  margin_rate = st.sidebar.number_input("Margin Rate (%)", value=5.0)
  
  # Analysis Settings
  risk_free_rate = st.sidebar.number_input("Risk-Free Rate for Sharpe (%)", value=3.0)
  ```

#### 3.3 Real-time Debugging Output
- Command-line progress display during backtest execution
- Trade-by-trade logging with LONG/SHORT direction
- Configurable debug level (can be turned off later)

### Phase 4: Visualization & Reporting (Week 4)
**Priority: Medium**

#### 4.1 Plotly Chart Implementation
- **Daily P&L Time Series**: End-of-day gross and net P&L chart
- **Equity Curve**: Account value progression over time
- **Drawdown Analysis**: Peak-to-trough visualization 
- **Performance Distribution**: Histogram of trade returns
- **Monthly Performance Heatmap**: Calendar view of returns

#### 4.2 PDF Report Generation Tests & Implementation
- **File**: `test_framework/SPX_CFD/test_pdf_generator.py`
- Test PDF structure and content
- Validate chart embedding
- Test report generation with various result sets

#### 4.3 PDF Report Structure
```python
class PDFReportGenerator:
    def generate_report(self, backtest_results, parameters):
        # 1. Executive Summary (key metrics)
        # 2. Input Parameters (all settings used)  
        # 3. Performance Summary Table
        # 4. Embedded Charts (equity curve, daily P&L, drawdown)
        # 5. Risk Analysis (VaR, Sharpe, drawdowns)
```

### Phase 5: Testing & Optimization (Week 5)
**Priority: High**

#### 5.1 Comprehensive Test Execution
- Run all test suites with coverage analysis
- Ensure minimum 90% code coverage
- Performance testing with 3-month 5M data
- Validate all 22 performance metrics

#### 5.2 Error Handling Implementation
- Graceful failure with user-friendly Streamlit messages
- Debug logging for invalid trade conditions
- Data validation and gap handling

#### 5.3 Performance Optimization
- Progress indicators for long-running backtests
- Memory usage monitoring
- Optimize data processing for 5M frequency

## Technical Implementation Details

### Entry Signal Logic (2 Basis Points)
```python
class CFDTradingEngine:
    def process_market_tick(self, timestamp, open_price, high, low, close):
        # Use close price as current market price
        current_price = close
        
        if not self.position_active:
            # Check for entry signals
            signal = self.check_entry_signals(current_price)
            if signal:
                self.enter_trade(signal, current_price, timestamp)
        else:
            # Update existing position
            self.update_position(current_price, high, low, timestamp)
            
        # Check for end-of-day closure (16:00)
        if self.is_market_close(timestamp):
            if self.position_active:
                self.close_position(current_price, "END_OF_DAY")
            self.process_daily_close(timestamp, current_price)
            
    def check_entry_signals(self, current_price):
        price_change_bps = ((current_price - self.opening_price) / self.opening_price) * 10000
        
        if price_change_bps >= 2.0:
            return "LONG"
        elif price_change_bps <= -2.0:
            return "SHORT"
        return None
        
    def process_daily_close(self, timestamp, close_price):
        # Calculate daily P&L summary
        # Reset opening price for next trading day
        # Log CLOSE entry with daily totals
        self.opening_price = close_price
```

### Exit Priority Logic
```python
def check_exit_conditions(self, current_price, timestamp):
    # Priority order: End-of-day > Profit Target > Trailing Stop
    
    if self.is_market_close(timestamp):
        return "END_OF_DAY", current_price
        
    if self.direction == "LONG":
        if current_price >= self.profit_target:
            return "PROFIT_TARGET", self.profit_target
        elif self.trailing_stop and current_price <= self.trailing_stop:
            return "TRAILING_STOP", self.trailing_stop
            
    elif self.direction == "SHORT":
        if current_price <= self.profit_target:
            return "PROFIT_TARGET", self.profit_target  
        elif self.trailing_stop and current_price >= self.trailing_stop:
            return "TRAILING_STOP", self.trailing_stop
            
    return None, None
```

### Enhanced Performance Metrics

#### All 22 Required Metrics Implementation:
```python
class PerformanceMetrics:
    def calculate_all_metrics(self, trades, daily_pnl, equity_curve):
        return {
            # Basic Trade Metrics
            'total_trades': len(trades),
            'winning_trades': len([t for t in trades if t.pnl > 0]),
            'losing_trades': len([t for t in trades if t.pnl < 0]),
            'total_long_trades': len([t for t in trades if t.direction == "LONG"]),
            'total_short_trades': len([t for t in trades if t.direction == "SHORT"]),
            'win_rate': self.calculate_win_rate(trades),
            
            # P&L Metrics  
            'total_pnl': sum(t.net_pnl for t in trades),
            'gross_pnl': sum(t.gross_pnl for t in trades),
            'total_costs': sum(t.costs for t in trades),
            'avg_win': self.calculate_average_win(trades),
            'avg_loss': self.calculate_average_loss(trades),
            
            # Risk & Return Metrics
            'max_drawdown': self.calculate_max_drawdown(equity_curve),
            'avg_drawdown': self.calculate_avg_drawdown(equity_curve),
            'total_return': self.calculate_total_return(equity_curve),
            'final_equity': equity_curve[-1],
            'profit_factor': self.calculate_profit_factor(trades),
            'cost_ratio': self.calculate_cost_ratio(trades),
            
            # Time-based Metrics
            'shortest_trade_minutes': min(t.duration_minutes for t in trades),
            'longest_trade_minutes': max(t.duration_minutes for t in trades),
            'avg_trade_duration_minutes': self.calculate_avg_duration(trades),
            
            # Advanced Risk Metrics
            'sharpe_ratio': self.calculate_sharpe_ratio(daily_pnl, self.risk_free_rate),
            'value_at_risk': self.calculate_var(daily_pnl, [1, 3, 5])
        }
```

## File Structure

```
OpenBB/
├── app/
│   ├── SPX_CFD_Backtest.py              # Main Streamlit application
│   └── common/
│       ├── market_data.py               # Existing data access (enhanced)
│       ├── cfd_engine.py                # CFD trading logic (new)
│       ├── backtest_analyzer.py         # Performance analysis (new)
│       └── pdf_generator.py             # Report generation (new)
├── docs/strategies/CFD/
│   ├── SPX Backtest Application.md      # Updated requirements
│   ├── CFD Trade Mechanics Long vs. Short.md  # Trade logic reference
│   ├── CFD_Calculator.html              # Interactive calculator reference
│   ├── SPX_Backtest_Development_Plan.md # Original plan
│   └── SPX_Backtest_Development_Plan_v2.md # This document
├── logs/
│   └── spx_backtest_YYYYMMDD_HHMMSS.log # Timestamped debug logs
├── market_data/historical/SPX/
│   ├── 1M.txt                          # Minute data
│   ├── 5M.txt                          # 5-minute data (primary testing)
│   ├── 30M.txt                         # 30-minute data
│   ├── 1H.txt                          # Hourly data  
│   └── 1D.txt                          # Daily data
└── test_framework/SPX_CFD/             # TDD test suite
    ├── test_cfd_engine.py              # Core logic tests
    ├── test_backtest_analyzer.py       # Metrics tests
    ├── test_market_data_integration.py # Data access tests
    ├── test_pdf_generator.py           # Reporting tests
    ├── test_integration.py             # End-to-end tests
    ├── conftest.py                     # Shared fixtures
    └── fixtures/                       # Test data
        ├── sample_5M_data.txt          # Small dataset for testing
        └── expected_results.json       # Known good results
```

## Dependencies (Already Installed in OpenBB-env)

The following packages are confirmed available:
- `streamlit` - Web application framework
- `plotly` - Interactive charting
- `pandas` - Data manipulation
- `numpy` - Numerical computing
- `reportlab` - PDF generation
- `fpdf2` - Alternative PDF library
- `openpyxl` - Excel export
- `pytest` - Testing framework

## TDD Best Practices Implementation

### Following Best Practices from `docs/TDD/Python_Unit_Testing_Best_Practices.pdf`:

1. **Tests Should Be Fast**: Use small data samples, mock external dependencies
2. **Tests Should Be Independent**: Each test can run in isolation
3. **Each Test Should Test One Thing**: Single assertion per test method
4. **Tests Should Be Readable**: Descriptive names like `test_2bps_long_entry_trigger`
5. **Tests Should Be Deterministic**: No random data, fixed test scenarios
6. **No Implementation Details**: Test behavior, not internal mechanics
7. **Single Assert Per Test**: One verification point per test
8. **Use Fake Data**: Sample market data files for consistent testing
9. **Setup/Teardown**: Pytest fixtures for clean test environments
10. **Group Related Tests**: Test classes for logical organization

### Test Naming Conventions
```python
def test_when_price_increases_2bps_then_enter_long_trade()
def test_when_price_decreases_2bps_then_enter_short_trade()  
def test_when_profit_target_hit_then_close_position()
def test_when_market_closes_then_force_position_closure()
def test_given_losing_trades_when_calculating_avg_loss_then_return_negative_value()
```

### Fixture Structure
```python
# conftest.py
@pytest.fixture
def sample_market_data():
    """Small 5M dataset for testing (1 day of data)"""
    return pd.DataFrame({
        'date': pd.date_range('2008-01-02 09:30', '2008-01-02 16:00', freq='5T'),
        'open': [1467.97] * 79,  # Sample values
        'high': [1470.00] * 79,
        'low': [1465.00] * 79,
        'close': [1469.00] * 79
    })

@pytest.fixture  
def cfd_parameters():
    """Standard CFD configuration for testing"""
    return {
        'account_balance': 10000,
        'risk_percentage': 2.0,
        'transaction_cost': 5.0,
        'stop_loss_distance': 50.0,
        'risk_reward_ratio': 2.0,
        'trailing_stop_pct': 2.0,
        'margin_rate': 5.0
    }
```

## Quality Assurance

### Testing Strategy
1. **Unit Tests**: Individual component testing (functions, methods)
2. **Integration Tests**: Component interaction testing  
3. **End-to-End Tests**: Full backtest workflow testing
4. **Performance Tests**: 3-month data processing validation
5. **Regression Tests**: Known result verification

### Code Quality Standards
- **PEP 8 Compliance**: Automated formatting checks
- **Type Hints**: Function parameters and returns
- **Docstrings**: Google-style documentation
- **Error Handling**: User-friendly messages
- **Logging**: Debug and audit trail

### Coverage Requirements
- **Minimum 90% Code Coverage**: Measured with pytest-cov
- **Critical Path 100%**: Entry/exit logic, P&L calculations
- **Edge Case Testing**: Market close, data gaps, invalid inputs

## Risk Considerations

### Technical Risks & Mitigations
1. **Data Processing Performance**: 
   - Risk: 5M data may be large for 3+ months
   - Mitigation: Progress indicators, chunked processing if needed

2. **Floating Point Precision**: 
   - Risk: Basis point calculations may have precision issues
   - Mitigation: Use Decimal for financial calculations

3. **Market Hours Logic**: 
   - Risk: Timezone handling and exact market close times
   - Mitigation: Comprehensive tests for time-based logic

4. **Memory Usage**: 
   - Risk: Large datasets consuming too much RAM
   - Mitigation: Stream processing, memory profiling

### Business Logic Risks & Mitigations
1. **2bps Trigger Accuracy**: 
   - Risk: Incorrect basis point calculations
   - Mitigation: Extensive unit tests with known values

2. **Position Reset Logic**: 
   - Risk: Opening price reset errors between trades
   - Mitigation: State machine testing, logging validation

3. **Daily P&L Aggregation**: 
   - Risk: Incorrect daily summaries
   - Mitigation: Manual calculation verification tests

## Success Criteria

### Functional Requirements ✅
- [ ] Loads 5M historical data from `market_data/historical/SPX/5M.txt`
- [ ] Implements ±2bps entry trigger logic correctly
- [ ] Executes long and short CFD trades with proper position sizing
- [ ] Enforces trading hours (09:30-16:00) and daily position closure
- [ ] Calculates all 22 performance metrics accurately
- [ ] Generates daily P&L time series with charting
- [ ] Creates PDF reports with summary statistics and charts
- [ ] Provides real-time command-line debugging output

### Performance Requirements ✅
- [ ] Processes 3-month 5M data in under 2 minutes
- [ ] Handles full trading day (390 data points) efficiently
- [ ] Updates UI responsively during backtest execution
- [ ] Generates PDF reports in under 30 seconds

### Testing Requirements ✅
- [ ] 90%+ code coverage across all modules
- [ ] All tests pass consistently (deterministic)
- [ ] TDD approach: tests written before implementation
- [ ] Integration tests validate end-to-end workflow
- [ ] Performance tests confirm acceptable processing times

## Remaining Questions for Clarification

### Strategy Logic Questions

1. **Opening Price Definition**: When you say "Opening Price starts with the first date in the historical date range and the first open price", should this be:
   - The very first open price in the entire backtest period?
   - Reset to the first open price of each trading day?
   - The current interpretation is it's the first price, then reset to exit price after each trade

2. **Intraday vs Multi-day Backtests**: The 2bps trigger logic seems designed for intraday trading, but how should it behave across multiple days?
   - Does the opening price reset each trading day?
   - Or does it only reset when a trade is closed?

3. **Current Market Price Timing**: Should the 2bps comparison use:
   - The close price of each bar (current implementation assumption)?
   - The real-time tick price during the bar?
   - Both high and low to check for trigger hits?

### Technical Implementation Questions

4. **Basis Point Calculation Precision**: For financial accuracy, should we use:
   - Standard Python floats?
   - Python Decimal for exact precision?
   - Round to specific decimal places?

5. **Market Hours Enforcement**: Should trades be:
   - Prevented from opening after a certain time (e.g., 15:45)?
   - Allowed to open until 15:59 but forced to close at 16:00?
   - Current assumption: trades can open anytime, must close by 16:00

6. **Data Gap Handling**: For holidays/weekends in the data:
   - Skip the missing days entirely?
   - Carry forward the last price?
   - Log gaps for debugging?

### Performance Metrics Questions

7. **VaR Calculation Method**: For Value at Risk at 1, 3, 5 days:
   - Should this be calculated on daily P&L returns?
   - Rolling window VaR or historical simulation?
   - Parametric (normal distribution) or historical method?

8. **Drawdown Calculation Frequency**: Should drawdown be measured:
   - Only at end-of-day equity levels?
   - Continuously throughout the day on each trade?
   - Both methods for comparison?

9. **Sharpe Ratio Time Period**: For the configurable risk-free rate:
   - Should it be annualized automatically?
   - Convert daily returns to annual for Sharpe calculation?
   - What frequency should the risk-free rate represent?

### User Interface Questions

10. **Debug Output Control**: For the command-line debugging:
    - Should this be a checkbox option in Streamlit?
    - Only active in development environment?
    - How verbose should the output be?

11. **Progress Indication**: During backtest execution:
    - Progress bar based on date range processed?
    - Number of trades executed?
    - Percentage of data processed?

12. **Date Range Validation**: Should the system:
    - Auto-detect available date ranges from the data file?
    - Warn users if selected range extends beyond available data?
    - Provide recommended date ranges for testing?

### Reporting Questions

13. **Daily P&L Chart Granularity**: The end-of-day P&L chart should show:
    - Gross P&L only?
    - Both gross and net P&L lines?
    - Cumulative P&L or daily P&L bars?

14. **Chart Time Axes**: For the various charts:
    - Should weekend gaps be shown or compressed?
    - Display only trading days?
    - How to handle holiday gaps?

These questions will help ensure the final implementation meets your exact requirements and handles edge cases appropriately.