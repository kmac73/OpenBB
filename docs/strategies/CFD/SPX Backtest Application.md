**SPX Historical Backtest Application**

This document describes creating a backtest of trading Long/Short Contracts for Difference (CFDs) which generates a set of analysis results from the time period executed.

**Technical Requirements**

**Relevant directory structure**

- OpenBB (base directory)

- OpenBB/app (Streamlit directory)

- OpenBB/docs/strategies/CFD (directory for this document and documents referenced)

- OpenBB/app/common (Location of market_data.py to be used to access historical market data)

- OpenBB/logs (location to write log files - timestamp each log file to separate them for debugging purposes)

- OpenBB/market_data/historical/SPX (Location of different frequencies of market data)

**Application Framework**

- Conda environment OpenBB-env is used for development and package management, These packages are already installed in OpenBB-env: streamlit plotly pandas numpy reportlab fpdf2 openpyxl pytest

- Python - Programming Language
- Use @staticmethod  def from_file in common/market_data.py for historical data access
- Streamlit   - app framework
- Plotly - for graphs
- PDF generator required

**Test Driven Development Approach**

- Follow best practices in: OpenBB/docs/TDD/Python_Unit_Testing_Best_Practices.pdf
- Write tests **before** writing code
- Save tests and associated test results and documentation in OpenBB/test_framework/SPX_CFD

**Input Requirements**

- Use Streamlit sidebar functionality to present parameters to the user. Include a “Run” button to submit the run. Do not attempt to calculate the run when the application first loads.
- Refer to requirements in CFD Trade Mechanics Long vs. Short.md and  CFD_Calculator.html for inputs and formulas. These need to be extended to run for a period of time defined in historical dates. 
- Historical dates to run this strategy need to be included
- Frequency of historical data must be entered. Frequencies are:
  - 1M
  - 5M
  - 30M
  - 1H
  - 1D
- These resolve to OpenBB/market_data/historical/SPX/<frequency_input>.txt
  - Example: OpenBB/market_data/historical/SPX/5M.txt

The data structure is comma separated:

YYYY-MM-DD HH:MM:SS,Open,High,Low,Close

2008-01-02 09:30:00,1467.97,1470.14,1467.97,1470.05

2008-01-02 09:35:00,1470.17,1470.17,1467.88,1469.49

 

**Entering a Trade**

- The  initial "Opening Price" starts with the first date in the historical  date range and the first open price in that sequence. Example - Opening Price (\$) would be set to 1467.97:
  - 2008-01-02      09:30:00,1467.97,1470.14,1467.97,1470.05
- The  variable Current Market Price (\$)  is set to the close price in the market  data file. 
  - Example Current Market Price (\$)  would be set to 1470.05 for:
  - 2008-01-02      09:30:00,1467.97,1470.14,1467.97,1470.05
- The  variable Current Market Price (\$) ticks at the frequency level set: 1M,5M,30M1H,1D
- The price change is tracked in the variable Current Market Price (\$). 
  - When this increases from Opening Price (\$) by 2bps (basis points) enter the trade LONG (record LONG in the logging)
  - When the price decreases from Opening Price (\$) by 2bps (basis points) enter the trade SHORT (record SHORT in the logging)
- When Final Exit Price is triggered, per trade results are recorded. Opening Price is reset to Final Exit Price ($) values and parameters are recalculated to determine entry into the next trade. 
  - This starts the measurement +/- 2bps into a LONG or SHORT trade again
- The market data must be monitored to enter either a long or a short trade. Only 1 trade can be active at a time.
- Trades can only last within 09:30AM-16:00 hours within a single day. All trades must be closed by 16:00. No overnight trades allowed.
- A CLOSE entry should be done at each end of day summing the gross and net P&L (this should be charted in the results)
- The following result metrics must be calculated and logged per trade and used     to generate result totals for the report:
  - total_trades
  - winning_trades
  - losing_trades
  - total_long_trades
  - total_short_trades
  - win_rate
  - total_pnl
  - gross_pnl
  - total_costs
  - avg_win
  - avg_loss
  - max_drawdown
  - avg_drawdown
  - total_return
  - final_equity
  - profit_factor
  - cost_ratio
  - shortest_trade_minutes
  - longest_trade_minutes
  - avg_trade_duration_minutes
  - sharpe_ratio
  - value_at_risk(VaR) - 95% at 1 day
- Chart  result metrics
- Generate PDF file with all inputs used in backtest and all results with charts



### Technical Implementation Questions

5. **Risk Management Priority**: When multiple exit conditions are met simultaneously (profit target, trailing stop, end-of-day), what is the priority order?

   ​	1. End-of-day

   ​	2. profit target

   ​	3. trailing stop

6. **Partial Position Management**: Are partial position closures allowed, or must entire positions be closed at once?

   ​	Only one trade can be live at one time.

7. **Slippage and Execution**: Should the backtest assume:

   - Perfect execution at exact prices? Yes

   - Realistic slippage modeling? No

   - Bid/ask spread considerations? 

     This should be captured in the transaction cost variable which is configurable in "Round Trip Cost per CFD (\$)" so it can be modeled.

   

8. **Data Validation**: How should the system handle:

   - Data gaps in historical files?

   - Inconsistent pricing (high < low, etc.)?

   - Missing market hours data?

     The data has been cleansed and is accurate. Gaps would only be from holidays and can be skipped.

### Performance Metrics Questions

9. **Sharpe Ratio Calculation**: What risk-free rate should be used for Sharpe ratio calculation? Make this a configurable input variable defaulting to 3%

10. **Value at Risk (VaR)**: What confidence level and time horizon should be used for VaR calculation (e.g., 95% confidence, 1-day horizon)? 95% at 1,3,5 day horizons

11. **Drawdown Measurement**: Should max drawdown be calculated as:

    - Peak-to-trough in dollar terms?

    - Peak-to-trough as percentage of account balance?

    - Measured on a trade-by-trade basis or continuously?

      Use Peak-to-trough as percentage of account balance and be sure to highlight in losses even if the overall backtest P&L looks positive. I don't know how to show that yet but we can iterate.

### User Interface Questions

12. **Parameter Validation**: What are the acceptable ranges for input parameters (e.g., minimum/maximum account balance, risk percentages)?

    For the first iteration, use defaults found in CFD_Calculator.html where applicable. Price variables may need to be read from the beginning of the historical data file to start the backtest

13. **Historical Date Limits**: Are there minimum or maximum date ranges that should be enforced?

    Read the start date, end date of the file and set that for limits. using 5M.txt historical file 

    - Start: 2008-01-02
    - End: 2024-06-28

14. **Real-time Feedback**: Should the application show trade-by-trade progress during backtest execution, or only final results?

    To start, show trade by trade which can be outputted to command line screen instead of streamlit unless that is easy to do. This will be turned off in the future and is for debugging purposes now. Length of the back test with be around 3 month windows to test the logic, not years worth of prices.

### Reporting Questions

15. **PDF Content Detail**: Should the PDF report include:

    - Every individual trade with entry/exit details? No
    - Only summary statistics? Yes
    - Chart images embedded? Yes
    - Raw data appendices? Set up the option but start with No

16. **Chart Time Granularity**: For visualization purposes, should charts show:

    - All data points (could be overwhelming for 1M data)? 

      Charts should show the summary statistics only. The only long time series chart request is: A CLOSE entry should be done at each end of day summing the gross and net P&L of the day (this should be charted in the results as a time series)

    - Sampled/aggregated data for readability? Yes

    - Multiple time frame views? No

### Integration Questions

17. **Logging Requirements**: What level of detail is needed in the timestamped log files?

    - Trade-level events only? Yes including LONG/SHORT direction
    - Every price update? No
    - Debug information? Yes
    - Performance metrics? Only P&L metrics

18. **Error Recovery**: How should the system handle:

    - Mid-backtest failures? 

      "Fail elegantly" with a streamlit message stating error occurred with last debug message

    - Invalid trade conditions? 

      Fail with debug message that captures the invalid conditions (this can be basic information for development to figure out, not fancy intelligent logging)

    - Memory limitations with large datasets?

    - For now, just let it run even if it takes a long time. Investigate chunking of data or other alternatives in Phase 2 development. Phase 1 will only be running on average 3 months worth of data at a time.

19. **Extensions and Modularity**: Should the system be designed to:

    - Support other asset classes beyond SPX?

    - Allow custom trading strategies?

    - Support different CFD broker specifications?

      These are all phase three items. Let's get the SPX backtest working correctly first.