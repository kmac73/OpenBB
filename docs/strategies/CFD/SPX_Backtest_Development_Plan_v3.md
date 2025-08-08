# SPX CFD Backtest Application - Development Plan v3.0

## Overview
This document outlines the final development plan for creating a comprehensive SPX (S&P 500) historical backtest application for trading Long/Short Contracts for Difference (CFDs) using Test-Driven Development (TDD) methodology and Streamlit as the frontend framework.

## Key Requirements from v2 Updates

### Critical Implementation Notes
- **No Fake Data**: Never create synthetic data to make tests pass - use real market data samples
- **Comment System**: Use structured comments for future features/changes as specified
- **Debug Output**: Command-line debugging without breaking application flow
- **Opening Price Logic**: Reset to first open price of each trading day AND to exit price after each trade
- **Market Hours**: Trades can open 09:30-15:30, must close by 16:00
- **VaR**: Daily P&L returns, parametric method, 95% confidence 1-day horizon only

### Comment Structure for Future Development
```python
# TODO: Phase 3 - [Feature Description]
# TODO: Future Change - [Enhancement Description] 
# TODO: Compute Performance - [Optimization Description]
```

## Application Architecture

### Core Components
1. **Streamlit Frontend Application**
   - Location: `OpenBB/app/SPX_CFD_Backtest.py`
   - Framework: Streamlit with sidebar parameter controls and Run button
   - Visualization: Plotly charts for performance metrics
   - Export: PDF report generation capability

2. **CFD Trading Engine**
   - Location: `OpenBB/app/common/cfd_engine.py`
   - Responsibilities: 2bps trigger logic, daily reset, position management
   - Integration: Uses existing `market_data.py.from_file()` static method

3. **Backtest Results Analysis**
   - Location: `OpenBB/app/common/backtest_analyzer.py`
   - Responsibilities: 22 performance metrics, daily P&L tracking, VaR calculation

4. **PDF Report Generator**
   - Location: `OpenBB/app/common/pdf_generator.py`
   - Dependencies: ReportLab (already installed in OpenBB-env)
   - Content: All inputs used + results with embedded charts

## Test-Driven Development Strategy

### Testing Framework Setup
- **Framework**: pytest (already installed in OpenBB-env)
- **Location**: `OpenBB/test_framework/SPX_CFD/`
- **Data Source**: Use actual historical data samples from `market_data/historical/SPX/`

### Test Structure
```
test_framework/SPX_CFD/
├── test_cfd_engine.py              # Core trading logic tests
├── test_backtest_analyzer.py       # Performance metrics tests  
├── test_market_data_integration.py # Data access tests
├── test_pdf_generator.py           # Report generation tests
├── test_integration.py             # End-to-end backtest tests
├── conftest.py                     # Shared fixtures using real data
└── fixtures/                       # Reference files (not fake data)
    └── expected_calculations.json  # Hand-calculated expected results
```

## Development Phases

### Phase 1: TDD Foundation & Core Logic (Week 1)
**Priority: High - Write Tests First**

#### 1.1 Test Setup and Real Data Fixtures
- **File**: `test_framework/SPX_CFD/conftest.py`
- Create pytest fixtures using real market data:
  ```python
  @pytest.fixture
  def real_market_sample():
      """Load actual 1-day sample from 5M.txt for testing"""
      # Use actual data from 2008-01-02 for consistent testing
      return market_data.from_file(['SPX'], '2008-01-02', '2008-01-02', '5M')
  
  @pytest.fixture  
  def expected_calculations():
      """Hand-calculated expected results for validation"""
      # Load pre-calculated expected values for known scenarios
      return json.load('fixtures/expected_calculations.json')
  ```

#### 1.2 CFD Engine Core Logic Tests
- **File**: `test_framework/SPX_CFD/test_cfd_engine.py`
- **Tests to Write First**:
  ```python
  def test_opening_price_set_to_first_open_of_day()
  def test_opening_price_reset_to_exit_price_after_trade()
  def test_opening_price_reset_at_start_of_new_day()
  def test_2bps_long_entry_trigger_using_close_price()
  def test_2bps_short_entry_trigger_using_close_price()
  def test_no_trade_entry_after_1530()
  def test_force_close_position_at_1600()
  def test_position_sizing_with_standard_floats()
  def test_daily_pnl_aggregation_and_reset()
  def test_no_active_trades_at_end_of_day()
  def test_no_active_trades_at_start_of_day()
  ```

#### 1.3 Implement CFD Trading Engine
- **File**: `app/common/cfd_engine.py`
- **Key Classes and Methods**:
  ```python
  class CFDTradingEngine:
      def __init__(self, account_balance, risk_pct, transaction_cost, ...):
          # TODO: Future Change - May switch to Decimal for precision
          self.use_standard_floats = True
          
      def start_new_trading_day(self, date, first_open_price):
          """Reset opening price to first open of day"""
          # Verify no active trades from previous day
          assert not self.position_active, "Trades must be closed from previous day"
          self.opening_price = first_open_price
          self.daily_trades = []
          
      def process_market_tick(self, timestamp, ohlc_data):
          """Process each tick - use close price for 2bps logic"""
          current_price = ohlc_data['close']  # Use close price as specified
          
          # Check market hours for new entries (09:30-15:30)
          if self.can_open_new_trade(timestamp):
              signal = self.check_2bps_trigger(current_price)
              if signal and not self.position_active:
                  self.enter_trade(signal, current_price, timestamp)
                  
          # Update existing position
          if self.position_active:
              self.update_position(current_price, ohlc_data, timestamp)
              
          # Force close at 16:00 - highest priority
          if self.is_market_close_time(timestamp) and self.position_active:
              self.close_position(current_price, "END_OF_DAY_FORCE_CLOSE")
              
      def check_2bps_trigger(self, current_price):
          """2bps trigger logic using standard Python floats"""
          # TODO: Future Change - May need Decimal precision for production
          price_change_bps = ((current_price - self.opening_price) / self.opening_price) * 10000
          
          if price_change_bps >= 2.0:
              return "LONG"
          elif price_change_bps <= -2.0:
              return "SHORT"
          return None
          
      def close_position(self, exit_price, reason):
          """Close position and reset opening price to exit price"""
          # Record trade results
          self.record_trade_result(exit_price, reason)
          
          # Reset opening price to exit price for next trade
          self.opening_price = exit_price
          self.position_active = False
          
      def can_open_new_trade(self, timestamp):
          """Check if new trades allowed (09:30-15:30)"""
          time_part = timestamp.time()
          return time(9, 30) <= time_part <= time(15, 30)
          
      def end_of_day_summary(self):
          """Calculate daily P&L for charting"""
          daily_gross_pnl = sum(trade.gross_pnl for trade in self.daily_trades)
          daily_net_pnl = sum(trade.net_pnl for trade in self.daily_trades)
          
          # TODO: Compute Performance - May optimize if needed
          return {
              'date': self.current_date,
              'daily_gross_pnl': daily_gross_pnl,
              'daily_net_pnl': daily_net_pnl,
              'trades_count': len(self.daily_trades),
              'cumulative_pnl': self.total_pnl
          }
  ```

#### 1.4 Market Data Integration Tests
- **File**: `test_framework/SPX_CFD/test_market_data_integration.py`
- Test `market_data.py.from_file()` with actual data files
- Verify data structure and time filtering
- Test date range validation against actual file contents

### Phase 2: Performance Analysis & Enhanced Logic (Week 2)
**Priority: High**

#### 2.1 Performance Metrics Tests (All 22 Metrics)
- **File**: `test_framework/SPX_CFD/test_backtest_analyzer.py`
- **Tests using real data scenarios**:
  ```python
  def test_total_trades_count_with_real_data()
  def test_long_short_trade_breakdown()
  def test_win_rate_calculation()
  def test_pnl_calculations_gross_and_net()
  def test_drawdown_both_methods()  # End-of-day and continuous
  def test_var_calculation_parametric_method()  # 95% confidence, 1-day
  def test_sharpe_ratio_with_3m_rate()
  def test_trade_duration_metrics()
  def test_cost_ratio_and_profit_factor()
  ```

#### 2.2 Implement Backtest Analyzer
- **File**: `app/common/backtest_analyzer.py`
- **Enhanced Implementation**:
  ```python
  class BacktestAnalyzer:
      def __init__(self, risk_free_rate=0.03):  # 3% default as specified
          # TODO: Future Change - Research market norms for Sharpe calculation
          self.risk_free_rate = risk_free_rate
          
      def calculate_all_metrics(self, trades, daily_summaries, equity_curve):
          """Calculate all 22 required metrics"""
          return {
              # Basic counts
              'total_trades': len(trades),
              'winning_trades': len([t for t in trades if t.net_pnl > 0]),
              'losing_trades': len([t for t in trades if t.net_pnl < 0]),
              'total_long_trades': len([t for t in trades if t.direction == "LONG"]),
              'total_short_trades': len([t for t in trades if t.direction == "SHORT"]),
              
              # Performance metrics
              'win_rate': self.calculate_win_rate(trades),
              'total_pnl': sum(t.net_pnl for t in trades),
              'gross_pnl': sum(t.gross_pnl for t in trades),
              'total_costs': sum(t.costs for t in trades),
              'avg_win': self.calculate_average_win(trades),
              'avg_loss': self.calculate_average_loss(trades),
              
              # Risk metrics
              'max_drawdown': self.calculate_max_drawdown(equity_curve),
              'avg_drawdown': self.calculate_avg_drawdown(equity_curve),
              'total_return': self.calculate_total_return(equity_curve),
              'final_equity': equity_curve[-1] if equity_curve else 0,
              'profit_factor': self.calculate_profit_factor(trades),
              'cost_ratio': self.calculate_cost_ratio(trades),
              
              # Time metrics
              'shortest_trade_minutes': min((t.duration_minutes for t in trades), default=0),
              'longest_trade_minutes': max((t.duration_minutes for t in trades), default=0),
              'avg_trade_duration_minutes': self.calculate_avg_duration(trades),
              
              # Advanced metrics
              'sharpe_ratio': self.calculate_sharpe_ratio(daily_summaries),
              'value_at_risk': self.calculate_var_95_1day(daily_summaries)
          }
          
      def calculate_drawdown_both_methods(self, trades, equity_curve):
          """Calculate drawdown using both methods for comparison"""
          # TODO: Compute Performance - Use end-of-day only if performance issues
          eod_drawdown = self.calculate_eod_drawdown(equity_curve)
          continuous_drawdown = self.calculate_continuous_drawdown(trades)
          
          return {
              'eod_max_drawdown': eod_drawdown['max'],
              'eod_avg_drawdown': eod_drawdown['avg'],
              'continuous_max_drawdown': continuous_drawdown['max'],
              'continuous_avg_drawdown': continuous_drawdown['avg']
          }
          
      def calculate_var_95_1day(self, daily_pnl_returns):
          """VaR using parametric method, 95% confidence, 1-day horizon"""
          if len(daily_pnl_returns) < 2:
              return 0
              
          # TODO: Future Change - Implement rolling window VaR when possible
          returns = np.array([d['daily_net_pnl'] for d in daily_pnl_returns])
          mean_return = np.mean(returns)
          std_return = np.std(returns)
          
          # Parametric VaR (normal distribution assumption)
          var_95 = mean_return - (1.645 * std_return)  # 95% confidence
          return var_95
  ```

#### 2.3 Data Gap Handling Implementation
```python
def handle_data_gaps(self, data):
    """Handle holidays/weekends in data"""
    # Skip missing days entirely - Yes
    # Carry forward last price - Yes  
    # Log gaps for debugging - Yes
    
    gaps_found = []
    filled_data = data.copy()
    
    for i in range(1, len(data)):
        time_gap = data.iloc[i]['date'] - data.iloc[i-1]['date']
        if time_gap > expected_frequency:
            gaps_found.append({
                'start': data.iloc[i-1]['date'],
                'end': data.iloc[i]['date'],
                'duration': time_gap
            })
            # Carry forward last price
            filled_data.iloc[i] = filled_data.iloc[i-1].copy()
            filled_data.iloc[i]['date'] = data.iloc[i]['date']
            
    if gaps_found:
        logging.info(f"Data gaps handled: {len(gaps_found)} gaps found and filled")
        
    return filled_data, gaps_found
```

### Phase 3: User Interface & Integration (Week 3)
**Priority: Medium**

#### 3.1 Streamlit Interface Development
- **File**: `app/SPX_CFD_Backtest.py`
- **Sidebar with Date Range Validation**:
  ```python
  def setup_sidebar():
      st.sidebar.header("SPX CFD Backtest Parameters")
      
      # Data Settings with auto-detection
      frequency = st.sidebar.selectbox("Frequency", ["1M", "5M", "30M", "1H", "1D"], index=1)
      
      # Auto-detect available date range from selected frequency file
      available_start, available_end = get_available_date_range(frequency)
      
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
      
      # Validate date range
      if start_date >= end_date:
          st.sidebar.error("End date must be after start date")
          return None
          
      if end_date > available_end:
          st.sidebar.error(f"Selected end date exceeds available data: {available_end}")
          return None
          
      # Account Settings
      account_balance = st.sidebar.number_input("Account Balance ($)", value=10000, min_value=1000)
      risk_pct = st.sidebar.number_input("Account Risk per Trade (%)", value=2.0, min_value=0.1, max_value=10.0)
      transaction_cost = st.sidebar.number_input("Round Trip Cost per CFD ($)", value=5.0, min_value=0.0)
      
      # CFD Parameters (from CFD_Calculator.html defaults)
      stop_loss_distance = st.sidebar.number_input("Initial Stop-Loss Distance ($)", value=50.0, min_value=1.0)
      risk_reward_ratio = st.sidebar.number_input("Risk/Reward Ratio", value=2.0, min_value=0.1)
      trailing_stop_pct = st.sidebar.number_input("Trailing Stop Percentage (%)", value=2.0, min_value=0.1)
      margin_rate = st.sidebar.number_input("Margin Rate (%)", value=5.0, min_value=0.1)
      
      # Analysis Settings
      risk_free_rate = st.sidebar.number_input("Risk-Free Rate for Sharpe (%)", value=3.0, min_value=0.0)
      
      # Debug Settings
      debug_output = st.sidebar.checkbox("Enable Debug Output", value=False)
      # TODO: Future Change - Determine optimal verbosity level
      
      # TODO: Phase 3 - Add progress indicators
      # TODO: Phase 3 - Add recommended date ranges for testing
      
      return {
          'frequency': frequency,
          'start_date': start_date,
          'end_date': end_date,
          'account_balance': account_balance,
          'risk_pct': risk_pct,
          'transaction_cost': transaction_cost,
          'stop_loss_distance': stop_loss_distance,
          'risk_reward_ratio': risk_reward_ratio,
          'trailing_stop_pct': trailing_stop_pct,
          'margin_rate': margin_rate,
          'risk_free_rate': risk_free_rate,
          'debug_output': debug_output
      }
  
  def get_available_date_range(frequency):
      """Auto-detect available date ranges from data file"""
      try:
          file_path = f"../market_data/historical/SPX/{frequency}.txt"
          # Read first and last lines to get date range
          with open(file_path, 'r') as f:
              first_line = f.readline().strip()
              last_line = None
              for last_line in f:
                  pass
                  
          start_date = pd.to_datetime(first_line.split(',')[0]).date()
          end_date = pd.to_datetime(last_line.split(',')[0]).date()
          return start_date, end_date
          
      except Exception as e:
          st.error(f"Error reading data file: {e}")
          # Fallback to known range from 5M.txt
          return date(2008, 1, 2), date(2024, 6, 28)
  ```

#### 3.2 Integration Tests & Debug Output
- **File**: `test_framework/SPX_CFD/test_integration.py`
- End-to-end tests using actual historical data
- Validate complete workflow including debug output

#### 3.3 Command-Line Debug Implementation
```python
class DebugLogger:
    def __init__(self, enabled=False, streamlit_mode=True):
        self.enabled = enabled
        self.streamlit_mode = streamlit_mode
        # TODO: Future Change - Adjust verbosity levels as needed
        
    def log_trade_entry(self, direction, price, timestamp):
        if self.enabled:
            msg = f"TRADE ENTRY: {direction} at ${price:.2f} on {timestamp}"
            if self.streamlit_mode:
                st.write(msg)  # Non-blocking Streamlit output
            else:
                print(msg)  # Command line output
            logging.info(msg)
            
    def log_trade_exit(self, direction, entry_price, exit_price, pnl, reason, timestamp):
        if self.enabled:
            msg = f"TRADE EXIT: {direction} ${entry_price:.2f} -> ${exit_price:.2f}, P&L: ${pnl:.2f}, Reason: {reason} on {timestamp}"
            if self.streamlit_mode:
                st.write(msg)
            else:
                print(msg)
            logging.info(msg)
```

### Phase 4: Visualization & Reporting (Week 4)
**Priority: Medium**

#### 4.1 Plotly Chart Implementation
```python
def create_daily_pnl_chart(daily_summaries):
    """Create daily P&L chart showing gross and net cumulative P&L"""
    # TODO: Future Change - Add option for daily bars vs cumulative
    
    dates = [d['date'] for d in daily_summaries]
    cumulative_gross = np.cumsum([d['daily_gross_pnl'] for d in daily_summaries])
    cumulative_net = np.cumsum([d['daily_net_pnl'] for d in daily_summaries])
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=cumulative_gross, name="Cumulative Gross P&L"))
    fig.add_trace(go.Scatter(x=dates, y=cumulative_net, name="Cumulative Net P&L"))
    
    fig.update_layout(
        title="Daily P&L Performance",
        xaxis_title="Date",
        yaxis_title="P&L ($)",
        # TODO: Future Change - Handle weekend/holiday gaps
        xaxis=dict(type='date')  # Only show trading days in Phase 1
    )
    
    return fig

def create_drawdown_chart(equity_curve, timestamps):
    """Create drawdown visualization"""
    # TODO: Compute Performance - Show both methods if performance allows
    peak = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - peak) / peak * 100
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=timestamps, y=drawdown, fill='tonegative', name="Drawdown %"))
    fig.update_layout(
        title="Drawdown Analysis",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        yaxis=dict(tickformat='.1%')
    )
    
    return fig
```

#### 4.2 PDF Report Generation
- **File**: `test_framework/SPX_CFD/test_pdf_generator.py`
- Tests for PDF structure and content validation

- **File**: `app/common/pdf_generator.py`
```python
class SPXBacktestPDFGenerator:
    def generate_comprehensive_report(self, parameters, results, charts):
        """Generate PDF with all inputs and results as specified"""
        
        # Section 1: All Input Parameters Used
        self.add_parameters_section(parameters)
        
        # Section 2: Performance Summary (All 22 Metrics)
        self.add_results_summary(results)
        
        # Section 3: Embedded Charts
        self.add_charts_section(charts)
        
        # Section 4: Trade Analysis Details
        self.add_trade_details_section(results['trade_log'])
        
        return self.save_pdf()
```

### Phase 5: Testing & Optimization (Week 5)
**Priority: High**

#### 5.1 Comprehensive Test Execution
```bash
# Run all tests with coverage
pytest test_framework/SPX_CFD/ --cov=app/common --cov-report=html

# Run specific test categories
pytest test_framework/SPX_CFD/test_cfd_engine.py -v
pytest test_framework/SPX_CFD/test_integration.py -v
```

#### 5.2 Performance Validation
- Test with actual 3-month 5M data samples
- Validate all 22 metrics against hand-calculated expectations
- Ensure no fake data used in any test

#### 5.3 Error Handling & Logging
```python
def graceful_failure_handling():
    try:
        # Backtest execution
        pass
    except Exception as e:
        error_msg = f"Backtest failed: {str(e)}"
        st.error(error_msg)
        logging.error(error_msg, exc_info=True)
        
        # Show last successful state for debugging
        if hasattr(self, 'last_successful_state'):
            st.json(self.last_successful_state)
```

## File Structure

```
OpenBB/
├── app/
│   ├── SPX_CFD_Backtest.py              # Main Streamlit application
│   └── common/
│       ├── market_data.py               # Existing (use from_file static method)
│       ├── cfd_engine.py                # CFD trading logic with 2bps + daily resets
│       ├── backtest_analyzer.py         # 22 metrics + VaR + drawdown analysis
│       └── pdf_generator.py             # Report with all inputs + results + charts
├── docs/strategies/CFD/
│   ├── SPX_Backtest_Application_v2.md   # Latest requirements
│   └── SPX_Backtest_Development_Plan_v3.md # This document
├── logs/
│   └── spx_backtest_YYYYMMDD_HHMMSS.log # Debug and trade logging
├── market_data/historical/SPX/
│   ├── 5M.txt                          # Primary testing data (2008-01-02 to 2024-06-28)
│   ├── 1M.txt, 30M.txt, 1H.txt, 1D.txt # Other frequencies
└── test_framework/SPX_CFD/             # TDD test suite using real data
    ├── test_cfd_engine.py              # Core logic tests
    ├── test_backtest_analyzer.py       # All 22 metrics tests
    ├── test_market_data_integration.py # Data access validation  
    ├── test_pdf_generator.py           # Report generation tests
    ├── test_integration.py             # End-to-end real data tests
    ├── conftest.py                     # Real data fixtures
    └── fixtures/                       
        └── expected_calculations.json  # Hand-calculated expected results
```

## Critical Implementation Details

### Opening Price Reset Logic
```python
def handle_opening_price_logic(self):
    """
    Opening price resets in two scenarios:
    1. Start of each trading day -> first open price of that day
    2. After each trade closes -> exit price becomes new opening price
    """
    
    # Daily reset (start of new trading day)
    def start_trading_day(self, date, market_data_for_day):
        first_open = market_data_for_day.iloc[0]['open']
        self.opening_price = first_open
        self.verify_no_active_trades()  # Must be clean slate
        
    # Trade-based reset (after trade closure)  
    def close_position(self, exit_price, reason):
        self.record_trade_results(exit_price, reason)
        self.opening_price = exit_price  # Reset for next trade
        self.position_active = False
```

### Market Hours Enforcement (09:30-15:30 Entry, 16:00 Force Close)
```python
def check_market_hours_rules(self, timestamp):
    """
    - Can open trades: 09:30-15:30
    - Must close all trades: 16:00 (highest priority)
    """
    time_part = timestamp.time()
    
    # Entry window
    can_enter = time(9, 30) <= time_part <= time(15, 30)
    
    # Force close time (overrides all other exit logic)
    must_close = time_part >= time(16, 0)
    
    return can_enter, must_close
```

### 2bps Trigger Using Close Price
```python
def check_2bps_trigger(self, current_close_price):
    """Use tick close price for 2bps comparison as specified"""
    # TODO: Future Change - May switch to Decimal for precision
    price_change_bps = ((current_close_price - self.opening_price) / self.opening_price) * 10000
    
    if price_change_bps >= 2.0:
        return "LONG"
    elif price_change_bps <= -2.0:  
        return "SHORT"
    return None
```

### VaR Calculation (Parametric, 95%, 1-day)
```python
def calculate_var_parametric_95_1day(self, daily_pnl_returns):
    """
    VaR using parametric method as specified:
    - Daily P&L returns
    - 95% confidence level  
    - 1-day horizon only (not 3,5 day as originally planned)
    """
    if len(daily_pnl_returns) < 2:
        return 0
        
    # TODO: Future Change - Implement rolling window when possible
    returns = np.array([d['daily_net_pnl'] for d in daily_pnl_returns])
    mean_return = np.mean(returns) 
    std_return = np.std(returns)
    
    # 95% confidence, normal distribution assumption
    var_95_1day = mean_return - (1.645 * std_return)
    return var_95_1day
```

## Remaining Questions for Final Clarification

### Data Processing Questions

1. **Opening Price Reset Timing**: When processing intraday data, should the opening price reset occur:
   
   - Immediately at the first tick of a new trading day?
   
   - Or only when the first trade opportunity is evaluated?
   
   - Current interpretation: Reset immediately when new day starts
   
     The back test file should determine the reset, here is an example of date change from 5M.txt but all frequency files have same model. Note sometimes the historical file will go beyond 16:00 but the trading logic always ends at 16:00
   
     2008-01-02 16:05:00,1447.17,1447.17,1447.16,1447.16
     2008-01-03 09:30:00,1447.55,1452.13,1447.55,1452.13
   
2. **Weekend/Holiday Data Handling**: When the data file has gaps:
   - Should we detect weekend gaps vs holiday gaps differently?
   
   - Or treat all gaps the same way (skip, carry forward, log)?
   
     skip, carry forward, log
   
3. **Market Data Validation**: For the 5M.txt file data integrity:
   - Should we validate that all expected trading hours are present?
   
   - How should we handle partial trading days (early closes)?
   
   - Should we validate OHLC relationships (O≤H, O≥L, etc.)?
   
     No, this has been done already for the from_file method. Insert comment for future to do these checks in from_provider method in market_data.py:
   
         @staticmethod
         def from_provider(symbols: list, start_date: str, end_date: str, frequency: str = "1D") -> pd.DataFrame:
             """Fetches historical price data for a list of symbols from a provider."""
             dataframes = []
             print(f"📊 Fetching {frequency} historical data from provider...")

### Performance & Scalability Questions  

4. **Memory Management**: For processing 3+ months of 5M data:
   
   - Should we implement data chunking from the start?
   
   - Or wait to see if memory issues arise with full datasets?
   
   - Current plan: Load all data, optimize later if needed
   
     Current plan is correct, do not initiate a back test until the user clicks the run button. For early command line versions (if required), ask for date range.
   
5. **Debug Output Volume**: For the command-line debugging:
   - How many trades per day are typically expected with 2bps triggers? Less than 5, 
   - Should we limit debug output to avoid overwhelming the console? yes
   - Would you like sample debug output format before implementation? Create a sample in the test results. We will run the test suite first and create a report before we begin the implementation code. This will be a good place to validate any unsure options.

### Metrics Calculation Questions

6. **Drawdown Comparison**: You mentioned "both methods for comparison" for drawdowns:
   
   - Should both values be displayed in the UI side-by-side?
   
   - Or should one method be primary with the other as a debug/validation metric?
   
   - How should differences between methods be highlighted?
   
     In development mode, display them side by side, no highlighting needed. Add comment, confirm which option for production code
   
7. **Daily P&L Aggregation**: For the end-of-day summaries:
   - Should intraday unrealized P&L be tracked separately from realized P&L?
   
   - Or only track realized P&L from completed trades?
   
   - Current interpretation: Only realized P&L from completed trades
   
     There should be no open trades at end of day which has already been stated above so this should be realized P&L on the current day's completed trades.

### Testing & Validation Questions

8. **Real Data Test Scenarios**: For creating the expected_calculations.json:
   - Would you prefer to manually validate a simple 1-2 day scenario first?
   
   - Or should we start with a full week of data for more comprehensive testing?

   - Should we include boundary conditions (market open/close times)?
   
     Take the last 5 days from the historical frequency file (5M.txt for example)
   
9. **Error Condition Testing**: For graceful failure scenarios:
   - What are the most critical error conditions to test?
   
   - Should we simulate data corruption/missing files?

   - How detailed should error messages be for end users?
   
     I don't know yet. Display in logs and in streamlit the last 5 lines of the debug log with the actual last line being the error. Jupyter Notebooks is a good error handling model to use if possible.
   
10. **Performance Benchmarks**: For acceptable processing times:
    
    - What's the maximum acceptable time for a 3-month 5M backtest?
    
    - Should we measure and report processing speed to users?
    
    - At what point should we implement performance optimizations?
    
      Phase 1, measure length and create a report log. Phase 2 investigate optimization.

These final clarifications will ensure the implementation exactly matches your requirements and handles all edge cases appropriately.