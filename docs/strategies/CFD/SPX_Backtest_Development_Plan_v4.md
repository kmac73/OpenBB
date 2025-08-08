# SPX CFD Backtest Application - Development Plan v4.0 (Final)

## Overview
This document outlines the final development plan for creating a comprehensive SPX (S&P 500) historical backtest application for trading Long/Short Contracts for Difference (CFDs) using Test-Driven Development (TDD) methodology. This version incorporates all clarifications and follows a **test-first approach** where we run the complete test suite and generate reports before implementing any code.

## Key Requirements - Final Clarifications

### Critical Implementation Requirements
- **No Fake Data**: Never create synthetic data to make tests pass - use real market data only
- **Test-First Approach**: Run complete test suite first, generate test report, then implement code
- **Comment System**: Structured comments for future features using standardized format
- **Real Data Reset Logic**: Opening price determined by date changes in backtest files
- **Limited Debug Output**: Max 5 trades/day expected, limit console output
- **Jupyter-style Error Handling**: Display last 5 debug log lines with error in Streamlit

### Opening Price Reset Logic (Final)
Based on your example from 5M.txt:
```
2008-01-02 16:05:00,1447.17,1447.17,1447.16,1447.16
2008-01-03 09:30:00,1447.55,1452.13,1447.55,1452.13
```
- Opening price resets to first open price when date changes (1447.55 in example)
- Trading logic stops at 16:00 regardless of data file continuation
- Also resets to exit price after each completed trade

### Comment Structure for Future Development
```python
# TODO: FUTURE_CHANGE - [Description] 
# TODO: PHASE_3 - [Feature Description]
# TODO: PRODUCTION_DECISION - [Choice needed for production]
# TODO: MARKET_DATA_PROVIDER - [Enhancement for from_provider method]
# TODO: PERFORMANCE_OPTIMIZATION - [Phase 2 optimization]
```

## Development Phases

### Phase 0: Test Suite Creation and Execution (Week 1)
**Priority: Critical - Test-First Approach**

#### 0.1 Create Complete Test Suite (Without Implementation)
- **Objective**: Write all tests first, run them (they will fail), generate test report
- **Location**: `OpenBB/test_framework/SPX_CFD/`
- **Data Source**: Last 5 days from actual `market_data/historical/SPX/5M.txt`

#### 0.2 Test Data Preparation
- **File**: `test_framework/SPX_CFD/conftest.py`
```python
@pytest.fixture
def last_5_days_real_data():
    """Load actual last 5 days from 5M.txt for comprehensive testing"""
    # Read 5M.txt, extract last 5 trading days
    # No fake data - use actual historical data
    file_path = "../../market_data/historical/SPX/5M.txt"
    
    # Extract last 5 complete trading days
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # Parse and return last 5 days of actual data
    return parse_last_5_trading_days(lines)

@pytest.fixture
def expected_manual_calculations():
    """Hand-calculated expected results for last 5 days scenario"""
    # TODO: Manual calculation of expected trades, P&L, metrics
    # This will be populated during Phase 0 test creation
    return {
        'expected_trades': [],  # To be calculated manually
        'expected_pnl': 0,      # To be calculated manually  
        'expected_metrics': {}  # To be calculated manually
    }
```

#### 0.3 Complete Test Suite Structure
```
test_framework/SPX_CFD/
├── test_cfd_engine.py              # All trading logic tests
├── test_backtest_analyzer.py       # All 22 metrics tests
├── test_market_data_integration.py # Data handling tests
├── test_pdf_generator.py           # Report generation tests
├── test_integration.py             # End-to-end tests with real data
├── conftest.py                     # Real data fixtures
├── test_sample_debug_output.py     # Generate sample debug format
└── expected_results/               # Manual calculations
    ├── last_5_days_trades.json     # Expected trades from manual calc
    └── last_5_days_metrics.json    # Expected metrics from manual calc
```

#### 0.4 Test Creation Priority Order
1. **Basic Data Handling Tests** - Ensure we can load real data
2. **Opening Price Reset Tests** - Test date change detection and reset logic
3. **2bps Trigger Tests** - Entry signal detection with real price movements
4. **Market Hours Tests** - Entry/exit time enforcement
5. **Position Management Tests** - Trade lifecycle management
6. **Performance Metrics Tests** - All 22 metrics with expected values
7. **Error Handling Tests** - Graceful failure scenarios
8. **Integration Tests** - Complete 5-day backtest execution

#### 0.5 Generate Initial Test Report
```bash
# Run complete test suite (will fail initially)
pytest test_framework/SPX_CFD/ --verbose --tb=short --html=reports/initial_test_report.html

# Generate coverage report (will show 0% initially)
pytest test_framework/SPX_CFD/ --cov=app/common --cov-report=html --cov-report=term

# Create test execution summary
python generate_test_summary.py > reports/test_execution_summary.md
```

This report will include:
- All failing tests (expected initially)
- Sample debug output format
- Performance timing baseline
- Manual calculation validation requirements

### Phase 1: Core Implementation Based on Test Requirements (Week 2)
**Priority: High - Implement to Pass Tests**

#### 1.1 CFD Trading Engine Implementation
- **File**: `app/common/cfd_engine.py`
- **Implement only what's needed to pass tests**

```python
class CFDTradingEngine:
    def __init__(self, account_balance, risk_pct, transaction_cost, **kwargs):
        # TODO: FUTURE_CHANGE - May switch to Decimal for precision
        self.account_balance = account_balance
        self.risk_pct = risk_pct
        self.transaction_cost = transaction_cost
        
        # State tracking
        self.opening_price = None
        self.position_active = False
        self.current_date = None
        self.daily_trades = []
        
    def detect_new_trading_day(self, timestamp, open_price):
        """Detect date change from backtest file and reset opening price"""
        new_date = timestamp.date()
        
        if self.current_date is None:
            # First day initialization
            self.current_date = new_date
            self.opening_price = open_price
            return True
            
        elif new_date > self.current_date:
            # Date changed - new trading day detected
            # Verify no active trades from previous day
            assert not self.position_active, f"Active trade found at day change: {self.current_date} -> {new_date}"
            
            # Reset for new day
            self.current_date = new_date
            self.opening_price = open_price
            self.daily_trades = []
            return True
            
        return False
        
    def process_market_tick(self, timestamp, ohlc_data):
        """Process each market tick using close price for 2bps logic"""
        # Check for new trading day first
        if timestamp.time() == time(9, 30, 0):  # Market open
            self.detect_new_trading_day(timestamp, ohlc_data['open'])
        
        current_price = ohlc_data['close']  # Use close price as specified
        
        # Check trading hours and process tick
        if self.is_trading_hours(timestamp):
            # Check for entry signals if no position
            if not self.position_active and self.can_enter_new_trade(timestamp):
                signal = self.check_2bps_trigger(current_price)
                if signal:
                    self.enter_trade(signal, current_price, timestamp)
                    
            # Update existing position
            if self.position_active:
                self.update_position(current_price, ohlc_data, timestamp)
                
        # Force close at 16:00 - highest priority
        if timestamp.time() >= time(16, 0, 0) and self.position_active:
            self.close_position(current_price, "END_OF_DAY_FORCE_CLOSE", timestamp)
            
    def check_2bps_trigger(self, current_price):
        """2bps trigger logic using close price and standard Python floats"""
        if self.opening_price is None:
            return None
            
        # TODO: FUTURE_CHANGE - May need Decimal precision for production
        price_change_bps = ((current_price - self.opening_price) / self.opening_price) * 10000
        
        if price_change_bps >= 2.0:
            return "LONG"
        elif price_change_bps <= -2.0:
            return "SHORT"
        return None
        
    def can_enter_new_trade(self, timestamp):
        """Check if new trades allowed (09:30-15:30)"""
        time_part = timestamp.time()
        return time(9, 30) <= time_part <= time(15, 30)
        
    def close_position(self, exit_price, reason, timestamp):
        """Close position and reset opening price to exit price"""
        # Calculate and record trade results
        trade_result = self.calculate_trade_result(exit_price, reason, timestamp)
        self.daily_trades.append(trade_result)
        
        # Reset opening price to exit price for next trade
        self.opening_price = exit_price
        self.position_active = False
        
        # Debug output (limited as requested)
        if hasattr(self, 'debug_logger'):
            self.debug_logger.log_trade_exit(trade_result)
```

#### 1.2 Market Data Integration Enhancement
- **File**: `app/common/market_data.py` (add comments only)

```python
@staticmethod
def from_provider(symbols: list, start_date: str, end_date: str, frequency: str = "1D") -> pd.DataFrame:
    """Fetches historical price data for a list of symbols from a provider."""
    # TODO: MARKET_DATA_PROVIDER - Add data validation checks here:
    # - Validate that all expected trading hours are present
    # - Handle partial trading days (early closes)  
    # - Validate OHLC relationships (O≤H, O≥L, etc.)
    # - Currently validation only done in from_file method
    
    dataframes = []
    print(f"📊 Fetching {frequency} historical data from provider...")
    # ... existing implementation continues unchanged
```

#### 1.3 Debug Output System (Limited Volume)
```python
class LimitedDebugLogger:
    def __init__(self, enabled=False, max_daily_trades=5):
        self.enabled = enabled
        self.max_daily_trades = max_daily_trades
        self.daily_trade_count = 0
        self.current_date = None
        # TODO: FUTURE_CHANGE - Determine optimal verbosity level
        
    def log_trade_entry(self, direction, price, timestamp):
        if not self.enabled:
            return
            
        # Reset counter for new day
        if timestamp.date() != self.current_date:
            self.current_date = timestamp.date()
            self.daily_trade_count = 0
            
        # Limit output to prevent overwhelming console
        if self.daily_trade_count < self.max_daily_trades:
            msg = f"ENTRY: {direction} @{price:.2f} [{timestamp}]"
            print(msg)  # Console output
            logging.info(msg)  # Log file
            self.daily_trade_count += 1
        elif self.daily_trade_count == self.max_daily_trades:
            print("... [Additional trades logged to file only]")
            self.daily_trade_count += 1
```

### Phase 2: Performance Analysis & Error Handling (Week 3)
**Priority: High**

#### 2.1 Backtest Analyzer Implementation
- **File**: `app/common/backtest_analyzer.py`

```python
class BacktestAnalyzer:
    def __init__(self, risk_free_rate=0.03):
        # TODO: FUTURE_CHANGE - Research market norms for Sharpe calculation
        self.risk_free_rate = risk_free_rate
        
    def calculate_all_metrics(self, trades, daily_summaries, equity_curve):
        """Calculate all 22 required metrics with real data validation"""
        
        # Validate input data (no fake data allowed)
        assert len(trades) >= 0, "Trade list cannot be None"
        assert all(hasattr(t, 'net_pnl') for t in trades), "All trades must have net_pnl"
        
        metrics = {
            # Basic Trade Counts
            'total_trades': len(trades),
            'winning_trades': len([t for t in trades if t.net_pnl > 0]),
            'losing_trades': len([t for t in trades if t.net_pnl < 0]),
            'total_long_trades': len([t for t in trades if t.direction == "LONG"]),
            'total_short_trades': len([t for t in trades if t.direction == "SHORT"]),
            
            # Performance Ratios
            'win_rate': self.calculate_win_rate(trades),
            'total_pnl': sum(t.net_pnl for t in trades),
            'gross_pnl': sum(t.gross_pnl for t in trades),
            'total_costs': sum(t.costs for t in trades),
            'avg_win': self.calculate_average_win(trades),
            'avg_loss': self.calculate_average_loss(trades),
            
            # Risk Metrics with both methods as requested
            'max_drawdown': self.calculate_drawdown_both_methods(equity_curve, trades)['primary'],
            'avg_drawdown': self.calculate_avg_drawdown(equity_curve),
            'total_return': self.calculate_total_return(equity_curve),
            'final_equity': equity_curve[-1] if equity_curve else 0,
            'profit_factor': self.calculate_profit_factor(trades),
            'cost_ratio': self.calculate_cost_ratio(trades),
            
            # Time-based Metrics
            'shortest_trade_minutes': min((t.duration_minutes for t in trades), default=0),
            'longest_trade_minutes': max((t.duration_minutes for t in trades), default=0),
            'avg_trade_duration_minutes': self.calculate_avg_duration(trades),
            
            # Advanced Risk Metrics
            'sharpe_ratio': self.calculate_sharpe_ratio(daily_summaries),
            'value_at_risk': self.calculate_var_parametric_95_1day(daily_summaries)
        }
        
        return metrics
        
    def calculate_drawdown_both_methods(self, equity_curve, trades):
        """Calculate drawdown using both methods for development comparison"""
        # TODO: PRODUCTION_DECISION - Confirm which method for production code
        
        # Method 1: End-of-day equity levels
        eod_drawdown = self.calculate_eod_drawdown(equity_curve)
        
        # Method 2: Continuous (trade-by-trade)
        # TODO: PERFORMANCE_OPTIMIZATION - Use end-of-day only if performance issues
        continuous_drawdown = self.calculate_continuous_drawdown(trades)
        
        return {
            'primary': eod_drawdown['max'],  # Default to end-of-day
            'eod_method': eod_drawdown,
            'continuous_method': continuous_drawdown,
            'comparison_note': 'Both methods calculated for development validation'
        }
```

#### 2.2 Error Handling (Jupyter Notebook Style)
```python
class JupyterStyleErrorHandler:
    def __init__(self):
        self.debug_log_lines = []
        self.max_stored_lines = 100
        
    def log_debug_line(self, message):
        """Store debug lines for error context"""
        self.debug_log_lines.append(f"{datetime.now()}: {message}")
        if len(self.debug_log_lines) > self.max_stored_lines:
            self.debug_log_lines = self.debug_log_lines[-self.max_stored_lines:]
            
    def handle_graceful_failure(self, error, streamlit_context=True):
        """Display error with last 5 debug lines like Jupyter notebooks"""
        error_msg = f"Backtest execution failed: {str(error)}"
        
        # Get last 5 debug lines for context
        context_lines = self.debug_log_lines[-5:] if len(self.debug_log_lines) >= 5 else self.debug_log_lines
        
        if streamlit_context:
            st.error(error_msg)
            st.write("**Debug Context (Last 5 operations):**")
            for line in context_lines:
                st.code(line)
        else:
            print(f"ERROR: {error_msg}")
            print("Debug Context:")
            for line in context_lines:
                print(f"  {line}")
                
        # Log complete error for debugging
        logging.error(error_msg, exc_info=True)
        for line in context_lines:
            logging.error(f"Context: {line}")
```

#### 2.3 Performance Timing and Measurement
```python
class PerformanceTimer:
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.phase_times = {}
        
    def start_backtest(self):
        """Phase 1: Measure and log processing time"""
        self.start_time = time.time()
        
    def end_backtest(self):
        """Phase 1: Create performance report, Phase 2: Investigate optimization"""
        self.end_time = time.time()
        total_time = self.end_time - self.start_time
        
        # TODO: PERFORMANCE_OPTIMIZATION - Phase 2 investigate optimization if needed
        performance_report = {
            'total_processing_time_seconds': total_time,
            'processing_rate_ticks_per_second': self.calculate_processing_rate(),
            'memory_usage_mb': self.get_memory_usage(),
            'optimization_needed': total_time > 120  # 2 minute threshold
        }
        
        # Log performance metrics
        logging.info(f"Backtest Performance: {performance_report}")
        return performance_report
```

### Phase 3: User Interface & Integration (Week 4)
**Priority: Medium**

#### 3.1 Streamlit Interface with Auto-Detection
- **File**: `app/SPX_CFD_Backtest.py`

```python
def setup_sidebar_with_validation():
    """Streamlit sidebar with date range auto-detection and validation"""
    st.sidebar.header("SPX CFD Backtest Parameters")
    
    # Data Settings with auto-detection from selected frequency
    frequency = st.sidebar.selectbox("Frequency", ["1M", "5M", "30M", "1H", "1D"], index=1)
    
    # Auto-detect available date range from selected file
    try:
        available_start, available_end = auto_detect_date_range(frequency)
        
        start_date = st.sidebar.date_input(
            "Start Date", 
            value=available_start,
            min_value=available_start,
            max_value=available_end
        )
        
        end_date = st.sidebar.date_input(
            "End Date", 
            value=min(available_start + timedelta(days=90), available_end),  # 3 month default
            min_value=available_start,
            max_value=available_end
        )
        
        # Validate date range with UI error messages
        if start_date >= end_date:
            st.sidebar.error("End date must be after start date")
            return None
            
        if end_date > available_end:
            st.sidebar.error(f"Selected end date exceeds available data: {available_end}")
            return None
            
    except Exception as e:
        st.sidebar.error(f"Error reading data file: {e}")
        return None
    
    # TODO: PHASE_3 - Add progress indicators
    # TODO: PHASE_3 - Add recommended date ranges for testing
    
    # Other parameters remain the same...
    
def auto_detect_date_range(frequency):
    """Auto-detect available date ranges from data file as requested"""
    file_path = f"../market_data/historical/SPX/{frequency}.txt"
    
    try:
        # Read first and last lines efficiently
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
            
            # Seek to end and find last line
            f.seek(0, 2)  # Seek to end
            file_size = f.tell()
            f.seek(max(file_size - 1024, 0))  # Go back up to 1KB
            lines = f.readlines()
            last_line = lines[-1].strip()
            
        start_date = pd.to_datetime(first_line.split(',')[0]).date()
        end_date = pd.to_datetime(last_line.split(',')[0]).date()
        
        return start_date, end_date
        
    except Exception as e:
        logging.error(f"Error auto-detecting date range: {e}")
        # Fallback to known 5M.txt range
        return date(2008, 1, 2), date(2024, 6, 28)
```

#### 3.2 Data Gap Handling Implementation
```python
def handle_data_gaps(data_df):
    """Handle holidays/weekends: skip, carry forward, log"""
    gaps_found = []
    filled_data = data_df.copy()
    
    for i in range(1, len(data_df)):
        current_time = data_df.iloc[i]['date']
        previous_time = data_df.iloc[i-1]['date']
        
        # Detect significant time gaps (> expected frequency)
        expected_gap = determine_expected_gap(current_time, previous_time)
        actual_gap = current_time - previous_time
        
        if actual_gap > expected_gap:
            gap_info = {
                'start_time': previous_time,
                'end_time': current_time,
                'duration_hours': actual_gap.total_seconds() / 3600,
                'gap_type': classify_gap_type(previous_time, current_time)
            }
            gaps_found.append(gap_info)
            
            # Carry forward last price as requested
            filled_data.iloc[i]['open'] = filled_data.iloc[i-1]['close']
            filled_data.iloc[i]['high'] = filled_data.iloc[i-1]['close'] 
            filled_data.iloc[i]['low'] = filled_data.iloc[i-1]['close']
            # Close price remains original from data file
            
    # Log gaps for debugging as requested
    if gaps_found:
        logging.info(f"Data gaps handled: {len(gaps_found)} gaps found")
        for gap in gaps_found:
            logging.info(f"  Gap: {gap['start_time']} to {gap['end_time']} ({gap['gap_type']})")
            
    return filled_data, gaps_found
```

### Phase 4: Visualization & Reporting (Week 5)
**Priority: Medium**

#### 4.1 Chart Implementation with Development Mode Options
```python
def create_daily_pnl_chart(daily_summaries, development_mode=False):
    """Daily P&L chart with gross and net cumulative P&L"""
    # TODO: FUTURE_CHANGE - Add option for daily bars vs cumulative
    
    dates = [d['date'] for d in daily_summaries]
    cumulative_gross = np.cumsum([d['daily_gross_pnl'] for d in daily_summaries])
    cumulative_net = np.cumsum([d['daily_net_pnl'] for d in daily_summaries])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=cumulative_gross, name="Cumulative Gross P&L", line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=dates, y=cumulative_net, name="Cumulative Net P&L", line=dict(color='red')))
    
    fig.update_layout(
        title="Daily P&L Performance (Cumulative)",
        xaxis_title="Date",
        yaxis_title="P&L ($)",
        # TODO: FUTURE_CHANGE - Handle weekend/holiday gaps in chart display
        xaxis=dict(type='date')  # Phase 1: Only trading days as requested
    )
    
    return fig

def create_drawdown_comparison_chart(drawdown_results, development_mode=False):
    """Show both drawdown methods side-by-side in development mode"""
    if development_mode:
        # TODO: PRODUCTION_DECISION - Confirm which method for production
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('End-of-Day Drawdown', 'Continuous Drawdown')
        )
        
        # Add both methods side by side as requested
        # No highlighting needed as specified
        # ... implementation continues
        
    else:
        # Production mode - show primary method only
        fig = create_single_drawdown_chart(drawdown_results['primary'])
        
    return fig
```

#### 4.2 PDF Report Generation
```python
class ComprehensivePDFGenerator:
    def generate_complete_report(self, parameters, results, charts, trades):
        """Generate PDF with all inputs and results as specified"""
        
        pdf = FPDF()
        
        # Page 1: Executive Summary
        self.add_executive_summary_page(pdf, results)
        
        # Page 2-3: All Input Parameters Used (comprehensive)
        self.add_complete_parameters_section(pdf, parameters)
        
        # Page 4-5: All 22 Performance Metrics  
        self.add_comprehensive_metrics_section(pdf, results)
        
        # Page 6-8: Embedded Charts
        self.add_all_charts_section(pdf, charts)
        
        # Page 9+: Additional Analysis (if development mode)
        if parameters.get('development_mode'):
            self.add_development_analysis_section(pdf, results)
            
        return pdf.output(dest='S').encode('latin1')
```

### Phase 5: Final Testing & Validation (Week 6)
**Priority: Critical**

#### 5.1 Test Suite Validation with Real Data
```bash
# Run complete test suite with real data
pytest test_framework/SPX_CFD/ --verbose --tb=long --maxfail=5

# Generate final coverage report  
pytest test_framework/SPX_CFD/ --cov=app/common --cov-report=html --cov-report=term --cov-fail-under=90

# Run integration tests with last 5 days of real data
pytest test_framework/SPX_CFD/test_integration.py -v -s

# Performance validation
python test_performance_with_real_data.py --duration=3months --frequency=5M
```

#### 5.2 Manual Validation Against Expected Results
```python
def validate_against_manual_calculations():
    """Compare automated results against hand-calculated expected values"""
    
    # Load manual calculations from Phase 0
    with open('test_framework/SPX_CFD/expected_results/last_5_days_metrics.json') as f:
        expected = json.load(f)
    
    # Run backtest on same data
    actual = run_backtest_last_5_days()
    
    # Validate key metrics within tolerance
    tolerance = 0.01  # 1% tolerance for floating point
    
    for metric in ['total_trades', 'win_rate', 'total_pnl', 'max_drawdown']:
        expected_value = expected[metric]
        actual_value = actual[metric]
        
        if abs(expected_value - actual_value) > tolerance * abs(expected_value):
            raise ValueError(f"Metric {metric} validation failed: expected {expected_value}, got {actual_value}")
    
    print("✅ All manual validation checks passed")
```

## File Structure (Final)

```
OpenBB/
├── app/
│   ├── SPX_CFD_Backtest.py              # Main Streamlit application
│   └── common/
│       ├── market_data.py               # Enhanced with provider comments
│       ├── cfd_engine.py                # Complete trading engine
│       ├── backtest_analyzer.py         # All 22 metrics + dual drawdown
│       ├── pdf_generator.py             # Comprehensive PDF reports
│       ├── debug_logger.py              # Limited debug output system
│       ├── error_handler.py             # Jupyter-style error handling
│       └── performance_timer.py         # Performance measurement
├── docs/strategies/CFD/
│   ├── SPX_Backtest_Application_v3.md   # Final requirements
│   └── SPX_Backtest_Development_Plan_v4.md # This document
├── logs/
│   └── spx_backtest_YYYYMMDD_HHMMSS.log # Debug and performance logging
├── market_data/historical/SPX/
│   ├── 5M.txt                          # Primary data source (real data only)
│   └── [other frequencies...]           # 1M.txt, 30M.txt, 1H.txt, 1D.txt
├── test_framework/SPX_CFD/             # Complete test suite
│   ├── test_cfd_engine.py              # Core trading logic tests
│   ├── test_backtest_analyzer.py       # All metrics tests
│   ├── test_market_data_integration.py # Data handling tests
│   ├── test_pdf_generator.py           # Report generation tests
│   ├── test_integration.py             # Real data end-to-end tests
│   ├── test_sample_debug_output.py     # Debug format validation
│   ├── conftest.py                     # Real data fixtures only
│   ├── expected_results/               # Manual calculations
│   │   ├── last_5_days_trades.json     # Hand-calculated expected trades
│   │   └── last_5_days_metrics.json    # Hand-calculated expected metrics
│   └── reports/                        # Test execution reports
│       ├── initial_test_report.html    # Phase 0 test results
│       ├── final_test_report.html      # Phase 5 validation results
│       └── performance_benchmarks.json # Processing time measurements
└── validate_manual_calculations.py     # Manual validation script
```

## Critical Implementation Points (Final)

### 1. Opening Price Reset Detection from Real Data
```python
def detect_date_change_from_data(self, current_timestamp, previous_timestamp):
    """
    Detect new trading day from actual data file timestamps
    Example from 5M.txt:
    2008-01-02 16:05:00  <- Trading stops at 16:00, data may continue
    2008-01-03 09:30:00  <- New day detected, reset opening price
    """
    if previous_timestamp is None:
        return True  # First data point
        
    current_date = current_timestamp.date()
    previous_date = previous_timestamp.date()
    
    # New trading day detected when date changes
    if current_date > previous_date:
        # Verify clean slate (no active trades should exist)
        if self.position_active:
            logging.warning(f"Active position found at date change: {previous_date} -> {current_date}")
            # Force close any remaining position
            self.force_close_position("DATE_CHANGE_CLEANUP")
            
        return True
        
    return False
```

### 2. Limited Debug Output (Max 5 trades/day)
```python
def create_sample_debug_output():
    """
    Generate sample debug format for validation
    Expected volume: <5 trades/day, limit console output
    """
    sample_debug_lines = [
        "2024-01-02 10:15:00 - ENTRY: LONG @4567.89 [2bps trigger: +2.1bps]",
        "2024-01-02 10:45:00 - EXIT: LONG 4567.89->4578.23, P&L: +$103.40 [PROFIT_TARGET]",
        "2024-01-02 11:30:00 - ENTRY: SHORT @4578.23 [2bps trigger: -2.0bps]", 
        "2024-01-02 14:20:00 - EXIT: SHORT 4578.23->4565.11, P&L: +$131.20 [TRAILING_STOP]",
        "2024-01-02 16:00:00 - DAY_CLOSE: 4 trades, Gross P&L: +$234.60, Net P&L: +$214.60",
        "... [Additional trades logged to file only]"  # When limit exceeded
    ]
    
    return sample_debug_lines
```

### 3. Jupyter-Style Error Display in Streamlit
```python
def demonstrate_error_handling():
    """Show how errors will be displayed like Jupyter notebooks"""
    try:
        # Backtest execution
        engine.run_backtest()
    except Exception as e:
        # Display last 5 debug operations + error
        st.error("Backtest execution failed")
        st.write("**Last 5 operations:**")
        
        debug_context = [
            "Processing tick: 2024-01-02 14:45:00",
            "Checking 2bps trigger: current=4567.89, opening=4565.23",
            "Trigger detected: LONG entry signal (+2.1 bps)",
            "Calculating position size: risk=$200, distance=$2.66",
            "ERROR: Division by zero in position sizing calculation"
        ]
        
        for i, line in enumerate(debug_context, 1):
            st.code(f"{i}. {line}")
            
        # Show actual error
        st.code(f"Error: {str(e)}")
```

### 4. Performance Measurement and Reporting
```python
def generate_performance_report(processing_time, data_points, trades_executed):
    """
    Phase 1: Measure and log performance
    Phase 2: Investigate optimization if needed
    """
    report = {
        'processing_time_seconds': processing_time,
        'data_points_processed': data_points,
        'trades_executed': trades_executed,
        'processing_rate_ticks_per_second': data_points / processing_time,
        'avg_time_per_trade_ms': (processing_time * 1000) / max(trades_executed, 1),
        'memory_usage_mb': get_current_memory_usage(),
        'optimization_recommendations': []
    }
    
    # TODO: PERFORMANCE_OPTIMIZATION - Phase 2 investigation
    if processing_time > 120:  # 2 minute threshold for 3-month data
        report['optimization_recommendations'].extend([
            'Consider data chunking for large datasets',
            'Implement vectorized calculations where possible',
            'Add progress indicators for user feedback'
        ])
    
    return report
```

## Success Criteria (Final Validation)

### Functional Requirements ✅
- [ ] Loads real market data from `market_data/historical/SPX/5M.txt` (last 5 days for testing)
- [ ] Detects new trading days from date changes in data file
- [ ] Implements ±2bps entry trigger using close prices
- [ ] Resets opening price to first open of day AND to exit price after trades
- [ ] Enforces trading hours 09:30-15:30 (entry) and 16:00 (force close)
- [ ] Calculates all 22 performance metrics accurately
- [ ] Generates dual drawdown calculations (development mode)
- [ ] Creates comprehensive PDF reports with all inputs + results
- [ ] Handles data gaps (skip, carry forward, log)
- [ ] Provides limited debug output (max 5 trades/day displayed)
- [ ] Auto-detects date ranges from selected frequency files
- [ ] Shows Jupyter-style error handling in Streamlit

### Testing Requirements ✅
- [ ] Test suite created and executed BEFORE implementation
- [ ] 90%+ code coverage with real data tests only
- [ ] Manual validation against hand-calculated expected results
- [ ] No fake data used anywhere in test suite
- [ ] Performance benchmarks measured and reported
- [ ] All tests pass with actual historical data

### Performance Requirements ✅
- [ ] Phase 1: Measures and logs processing time for optimization planning
- [ ] Handles last 5 days of 5M data efficiently (baseline measurement)
- [ ] Graceful error handling with context display
- [ ] Memory usage monitoring and reporting

## Final Notes

This development plan represents the complete, final specification incorporating all clarifications. The key differentiator is the **test-first approach** where the complete test suite is created and executed before any implementation code is written. This ensures:

1. **Real Data Validation**: All tests use actual market data from historical files
2. **Manual Calculation Verification**: Expected results are hand-calculated, not generated
3. **Performance Baseline**: Processing times are measured from the start
4. **Error Pattern Discovery**: Running tests first reveals potential implementation challenges

The structured comment system allows for easy future enhancement identification, and the limited debug output prevents console overwhelming while maintaining comprehensive logging for debugging purposes.
