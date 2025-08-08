**SPX Historical Backtest Application**

This document describes creating a backtest of trading Long/Short Contracts for Difference (CFDs) which generates a set of analysis results from the time period executed.

**V2 Change Comments**

- **Command-line debugging**: Real-time trade output during development
  - This should only be debug output to the command line (and log), not break in the middle of the application process

- **Do Not Create Fake Data to allow a test to pass** (Claude has done this in the past)
- When I answer questions below and I want to see some results before deciding how to proceed, insert comment in that section of code with my comments so we can refer back to it in future phases.
- Create a structured why to find functionality where I've said Add comment... so we can find those features in the future.

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

     Use skip, carry forward, log

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

   - Would you like sample debug output format before implementation? 

     Create a sample in the test results. We will run the test suite first and create a report before we begin the implementation code. This will be a good place to validate any unsure options.

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