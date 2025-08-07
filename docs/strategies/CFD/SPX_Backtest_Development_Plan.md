# SPX CFD Backtest Application - Development Plan

## Overview
This document outlines the development plan for creating a comprehensive SPX (S&P 500) historical backtest application for trading Long/Short Contracts for Difference (CFDs) using Streamlit as the frontend framework.

## Application Architecture

### Core Components
1. **Streamlit Frontend Application**
   - Location: `OpenBB/app/SPX_CFD_Backtest.py`
   - Framework: Streamlit with sidebar parameter controls
   - Visualization: Plotly charts for performance metrics
   - Export: PDF report generation capability

2. **CFD Trading Engine**
   - Location: `OpenBB/app/common/cfd_engine.py`
   - Responsibilities: Trade execution logic, position sizing, P&L calculations
   - Integration: Uses existing `market_data.py` for historical data access

3. **Backtest Results Analysis**
   - Location: `OpenBB/app/common/backtest_analyzer.py`
   - Responsibilities: Performance metrics calculation, drawdown analysis, reporting

4. **PDF Report Generator**
   - Location: `OpenBB/app/common/pdf_generator.py`
   - Dependencies: ReportLab or similar PDF library
   - Content: Input parameters, performance metrics, charts

## Development Phases

### Phase 1: Core Infrastructure (Week 1)
**Priority: High**

#### 1.1 CFD Trading Engine Development
- **File**: `app/common/cfd_engine.py`
- **Classes**:
  - `CFDPosition`: Represents a single CFD position (long/short)
  - `CFDTradingEngine`: Manages position lifecycle, entry/exit logic
- **Key Methods**:
  - `calculate_position_size()`: Based on account balance and risk percentage
  - `enter_trade()`: Long or short entry logic with stop-loss and profit targets
  - `update_position()`: Real-time P&L and trailing stop calculations
  - `exit_trade()`: Position closing logic with final P&L calculation

#### 1.2 Integration with Market Data
- Extend `market_data.py` usage for historical data access
- Support for all required frequencies (1M, 5M, 30M, 1H, 1D)
- Data validation and time-range filtering
- Market hours enforcement (09:30-16:00 EST)

#### 1.3 Basic Streamlit Framework
- **File**: `app/SPX_CFD_Backtest.py`
- Sidebar parameter controls (without Run button initially)
- Basic layout structure for results display
- Connection to CFD trading engine

### Phase 2: Trading Logic Implementation (Week 2)
**Priority: High**

#### 2.1 Position Management System
- **Long Trade Logic**:
  - Entry: Market price above opening price threshold
  - Stop-loss: Below entry price by risk amount
  - Profit target: Above entry by risk/reward ratio
  - Trailing stop: Dynamic stop based on highest price reached

- **Short Trade Logic**:
  - Entry: Market price below opening price threshold  
  - Stop-loss: Above entry price by risk amount
  - Profit target: Below entry by risk/reward ratio
  - Trailing stop: Dynamic stop based on lowest price reached

#### 2.2 Trade Execution Rules
- Only one active trade at a time
- Mandatory trade closure by 16:00 EST (no overnight positions)
- Next trade entry using previous exit price as new opening price
- Continuous monitoring throughout market hours

#### 2.3 Performance Metrics Calculation
- **File**: `app/common/backtest_analyzer.py`
- **Metrics Implementation**:
  - Basic metrics: total_trades, winning_trades, losing_trades, win_rate
  - P&L metrics: total_pnl, gross_pnl, total_costs, avg_win, avg_loss
  - Risk metrics: max_drawdown, sharpe_ratio, value_at_risk (VaR)
  - Return metrics: total_return, final_equity, profit_factor, cost_ratio
  - Time metrics: shortest/longest/average trade duration

### Phase 3: User Interface Enhancement (Week 3)
**Priority: Medium**

#### 3.1 Streamlit Sidebar Parameters
**Input Categories**:

1. **Account Settings**:
   - Account Balance ($): Default 10,000
   - Account Risk per Trade (%): Default 2%
   - Round Trip Transaction Cost ($): Default 5.00

2. **Historical Data Settings**:
   - Start Date: Date picker
   - End Date: Date picker  
   - Data Frequency: Dropdown (1M, 5M, 30M, 1H, 1D)

3. **Trade Parameters**:
   - Initial Stop-Loss Distance ($): Default 50
   - Risk/Reward Ratio: Default 2.0
   - Trailing Stop Percentage (%): Default 2%
   - Margin Rate (%): Default 5%

4. **Strategy Settings**:
   - Long Trade Entry Trigger: Price movement conditions
   - Short Trade Entry Trigger: Price movement conditions
   - Position Sizing Method: Fixed risk vs. other methods

#### 3.2 Results Display Interface
- **Real-time Results Table**: Key performance metrics
- **Trade Log**: Chronological list of all trades with details
- **Performance Charts**: 
  - Equity curve over time
  - Drawdown chart
  - Monthly returns heatmap
  - Win/Loss distribution

#### 3.3 Run Button Implementation
- Validation of all input parameters
- Progress bar for backtest execution
- Error handling and user feedback
- Results caching for large datasets

### Phase 4: Visualization and Reporting (Week 4)
**Priority: Medium**

#### 4.1 Plotly Chart Integration
**Chart Types**:
1. **Equity Curve**: Line chart showing account value over time
2. **Price Action with Trades**: Candlestick chart with entry/exit markers
3. **Drawdown Analysis**: Area chart showing drawdown periods
4. **Performance Distribution**: Histogram of trade returns
5. **Rolling Metrics**: Moving averages of key performance indicators

#### 4.2 PDF Report Generation
- **File**: `app/common/pdf_generator.py`
- **Report Sections**:
  1. Executive Summary: Key performance metrics
  2. Input Parameters: All user-selected settings
  3. Trade Analysis: Detailed trade log with statistics
  4. Performance Charts: All visualizations from Streamlit app
  5. Risk Analysis: Drawdown, VaR, and risk-adjusted returns

#### 4.3 Export Functionality
- PDF download button in Streamlit interface
- CSV export for trade log data
- JSON export for backtest parameters and results

### Phase 5: Testing and Optimization (Week 5)
**Priority: High**

#### 5.1 Unit Testing
- **File**: `tests/test_cfd_engine.py`
- Test all CFD calculation formulas against known values
- Validate position sizing and risk management logic
- Test market hours enforcement and trade closure

#### 5.2 Integration Testing
- **File**: `tests/test_backtest_integration.py`
- End-to-end backtest execution with sample data
- Validate results consistency across different time periods
- Test with various parameter combinations

#### 5.3 Performance Optimization
- Optimize data loading for large historical datasets
- Implement progress tracking for long-running backtests
- Memory usage optimization for extended time periods
- Caching strategies for repeated calculations

## Technical Implementation Details

### Data Flow Architecture
```
Historical Data Files → market_data.py → CFDTradingEngine → BacktestAnalyzer → Streamlit UI → PDF Generator
```

### Key Formulas Implementation

#### Long Trade Calculations
```python
# Position Sizing
risk_per_trade = account_balance * (account_risk_pct / 100)
risk_per_contract = opening_price - stop_loss_price
position_size = risk_per_trade / risk_per_contract

# P&L Calculation
gross_pnl = (exit_price - entry_price) * position_size
net_pnl = gross_pnl - (transaction_cost * position_size)
```

#### Short Trade Calculations
```python
# Position Sizing (same as long)
risk_per_contract = stop_loss_price - opening_price
position_size = risk_per_trade / risk_per_contract

# P&L Calculation
gross_pnl = (entry_price - exit_price) * position_size  
net_pnl = gross_pnl - (transaction_cost * position_size)
```

### Performance Metrics Formulas
```python
# Risk Metrics
win_rate = winning_trades / total_trades * 100
profit_factor = total_winning_amount / abs(total_losing_amount)
sharpe_ratio = (average_return - risk_free_rate) / std_dev_returns
max_drawdown = max(peak_value - current_value) / peak_value * 100

# Return Metrics  
total_return = (final_equity - initial_equity) / initial_equity * 100
return_on_margin = net_profit / margin_required * 100
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
│   ├── SPX Backtest Application.md      # Original requirements
│   ├── CFD Trade Mechanics Long vs. Short.md  # Trade logic reference
│   ├── CFD_Calculator.html              # Interactive calculator reference
│   └── SPX_Backtest_Development_Plan.md # This document
├── logs/
│   └── backtest_YYYYMMDD_HHMMSS.log    # Timestamped log files
├── market_data/historical/SPX/
│   ├── 1M.txt                          # Minute data
│   ├── 5M.txt                          # 5-minute data  
│   ├── 30M.txt                         # 30-minute data
│   ├── 1H.txt                          # Hourly data
│   └── 1D.txt                          # Daily data
└── tests/
    ├── test_cfd_engine.py              # Unit tests for trading engine
    ├── test_backtest_analyzer.py       # Unit tests for analysis
    └── test_integration.py             # End-to-end integration tests
```

## Dependencies

### Python Packages Required
```
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.0.0
numpy>=1.24.0
reportlab>=4.0.0  # For PDF generation
fpdf2>=2.7.0      # Alternative PDF library
openpyxl>=3.1.0   # For Excel export
pytest>=7.4.0     # For testing
```

### Installation Command
```bash
pip install streamlit plotly pandas numpy reportlab fpdf2 openpyxl pytest
```

## Quality Assurance

### Testing Strategy
1. **Unit Tests**: Individual component testing with mocked data
2. **Integration Tests**: Full backtest execution with historical data samples
3. **Performance Tests**: Large dataset handling and memory usage
4. **User Acceptance Tests**: Manual testing of all UI components

### Code Quality Standards
- PEP 8 compliance for Python code formatting
- Comprehensive docstrings for all classes and methods
- Type hints for function parameters and returns
- Error handling with user-friendly messages
- Logging for debugging and audit trail

## Risk Considerations

### Technical Risks
1. **Large Dataset Performance**: Intraday data files may be very large
   - **Mitigation**: Implement chunked processing and progress indicators
2. **Memory Usage**: Extended backtests may consume significant RAM
   - **Mitigation**: Use generators and streaming data processing
3. **Data Quality**: Historical data gaps or errors
   - **Mitigation**: Data validation and gap handling logic

### Business Logic Risks  
1. **Trading Hours Enforcement**: Ensuring all trades close by 16:00
   - **Mitigation**: Strict time-based validation in trading engine
2. **Position Sizing Edge Cases**: Division by zero or negative values
   - **Mitigation**: Input validation and error handling
3. **Market Data Timing**: Ensuring proper sequencing of price updates
   - **Mitigation**: Timestamp-based ordering and validation

## Success Criteria

### Functional Requirements Met
- [ ] Loads historical data from specified frequency files
- [ ] Executes long and short CFD trades with proper position sizing
- [ ] Calculates all 20+ performance metrics accurately
- [ ] Enforces trading hours (09:30-16:00) and daily position closure
- [ ] Generates comprehensive PDF reports
- [ ] Provides interactive Streamlit interface with sidebar controls

### Performance Requirements Met
- [ ] Processes full-day 1-minute data (390 data points) in under 10 seconds
- [ ] Handles multi-day backtests without memory issues
- [ ] Updates UI responsively during backtest execution
- [ ] Generates PDF reports in under 30 seconds

### User Experience Requirements Met
- [ ] Intuitive parameter input interface
- [ ] Clear error messages for invalid inputs
- [ ] Progress indication for long-running operations
- [ ] Professional-quality charts and reports
- [ ] Export capabilities for further analysis

## Questions and Clarifications Needed

### Strategy Logic Questions

1. **Trade Entry Triggers**: The document mentions monitoring market data to enter long or short trades but doesn't specify the exact conditions. What are the specific price movement or technical indicators that trigger trade entries?

2. **Opening Price Reset Logic**: When a trade exits and "Opening Price is reset to Final Exit Price", does this mean:
   - The next trade immediately looks for entry signals at this new price level?
   - There's a waiting period before the next trade can be entered?
   - Are there any filters to prevent immediate re-entry?

3. **Trade Direction Selection**: How is the decision made between entering a long vs. short trade? Is it:
   - Based on momentum direction?
   - User-specified preference?
   - Market condition algorithms?
   - Both long and short opportunities evaluated simultaneously?

4. **Market Data Frequency for Decisions**: Should trade entry/exit decisions be made:
   - On every data point (tick-by-tick for 1M data)?
   - On bar closes only?
   - Using real-time vs. end-of-bar pricing?

### Technical Implementation Questions

5. **Risk Management Priority**: When multiple exit conditions are met simultaneously (profit target, trailing stop, end-of-day), what is the priority order?

6. **Partial Position Management**: Are partial position closures allowed, or must entire positions be closed at once?

7. **Slippage and Execution**: Should the backtest assume:
   - Perfect execution at exact prices?
   - Realistic slippage modeling?
   - Bid/ask spread considerations?

8. **Data Validation**: How should the system handle:
   - Data gaps in historical files?
   - Inconsistent pricing (high < low, etc.)?
   - Missing market hours data?

### Performance Metrics Questions

9. **Sharpe Ratio Calculation**: What risk-free rate should be used for Sharpe ratio calculation?

10. **Value at Risk (VaR)**: What confidence level and time horizon should be used for VaR calculation (e.g., 95% confidence, 1-day horizon)?

11. **Drawdown Measurement**: Should max drawdown be calculated as:
    - Peak-to-trough in dollar terms?
    - Peak-to-trough as percentage of account balance?
    - Measured on a trade-by-trade basis or continuously?

### User Interface Questions

12. **Parameter Validation**: What are the acceptable ranges for input parameters (e.g., minimum/maximum account balance, risk percentages)?

13. **Historical Date Limits**: Are there minimum or maximum date ranges that should be enforced?

14. **Real-time Feedback**: Should the application show trade-by-trade progress during backtest execution, or only final results?

### Reporting Questions

15. **PDF Content Detail**: Should the PDF report include:
    - Every individual trade with entry/exit details?
    - Only summary statistics?
    - Chart images embedded?
    - Raw data appendices?

16. **Chart Time Granularity**: For visualization purposes, should charts show:
    - All data points (could be overwhelming for 1M data)?
    - Sampled/aggregated data for readability?
    - Multiple time frame views?

### Integration Questions

17. **Logging Requirements**: What level of detail is needed in the timestamped log files?
    - Trade-level events only?
    - Every price update?
    - Debug information?
    - Performance metrics?

18. **Error Recovery**: How should the system handle:
    - Mid-backtest failures?
    - Invalid trade conditions?
    - Memory limitations with large datasets?

19. **Extensions and Modularity**: Should the system be designed to:
    - Support other asset classes beyond SPX?
    - Allow custom trading strategies?
    - Support different CFD broker specifications?

These questions should be addressed before beginning development to ensure the application meets all requirements and handles edge cases appropriately.