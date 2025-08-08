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



17. - ### Strategy Logic Questions

      1. **Opening Price Definition**: When you say "Opening Price starts with the first date in the historical date range and the first open price", should this be:

         - The very first open price in the entire backtest period? It starts with the first open price of the start date that the user sets in the start date - end date variables 
         - Reset to the first open price of each trading day? Yes (remember, all trades should have been closed from the previous day, you should have a test at the end of day there are no active trades AND start of next day NO active trades)
         - The current interpretation is it's the first price, then reset to exit price after each trade. I don't understand. Does the above answers help? 

      2. **Intraday vs Multi-day Backtests**: 

         - Does the opening price reset each trading day?

         - Or does it only reset when a trade is closed?

           The 2bps trigger logic seems designed for intraday trading, but how should it behave across multiple days? 2bps is designed for intraday logic. Everything resets on the next day open

      3. **Current Market Price Timing**: Should the 2bps comparison use:

         - The close price of each bar (current implementation assumption)?

         - The real-time tick price during the bar?

         - Both high and low to check for trigger hits?

           Use the tick close price for item 3. questions

      ### Technical Implementation Questions

      4. **Basis Point Calculation Precision**: For financial accuracy, should we use:

         - Standard Python floats? Yes

         - Python Decimal for exact precision? No

         - Round to specific decimal places? No

           I may change  this in the future but use Standard Python floats. Add comment for future change 

      5. **Market Hours Enforcement**: Should trades be:

         - Prevented from opening after a certain time (e.g., 15:45)? 15:30
         - Allowed to open until 15:59 but forced to close at 16:00? Allowed to open until 15:30 and force close at 16:00 regardless of price target logic. 16:00 close of position is number one priority in all trade exit logic
         - Current assumption: trades can open anytime, must close by 16:00 Can open from 09:30 to 15:30. 

      6. **Data Gap Handling**: For holidays/weekends in the data:

         - Skip the missing days entirely? Yes
         - Carry forward the last price? Yyes
         - Log gaps for debugging? Yes

      ### Performance Metrics Questions

      7. **VaR Calculation Method**: For Value at Risk at 1, 3, 5 days:

         - Should this be calculated on daily P&L returns? We start with daily, then analyze compute performance. 
         - Rolling window VaR or historical simulation? Ideally rolling window, but default to historical simulation where rolling window not possible. Add comment for future change 
         - Parametric (normal distribution) or historical method? Parametric

      8. **Drawdown Calculation Frequency**: Should drawdown be measured:

         - Only at end-of-day equity levels? 

         - Continuously throughout the day on each trade?

         - Both methods for comparison?

           Both for comparison would be useful but if we need to improve compute, use end-of-day equity levels. Add comment for future change 

      9. **Sharpe Ratio Time Period**: For the configurable risk-free rate:

         - Should it be annualized automatically?

         - Convert daily returns to annual for Sharpe calculation?

         - What frequency should the risk-free rate represent? 3M

           This need further research. Can you apply market norms if available? Add comment for future change 

      ### User Interface Questions

      10. **Debug Output Control**: For the command-line debugging:

          - Should this be a checkbox option in Streamlit? Yes

          - Only active in development environment? Yes

          - How verbose should the output be? I need to see the level of verbose to make that decision

             Add comment for future change for all Debug Output

      11. **Progress Indication**: During backtest execution:

          - Progress bar based on date range processed? Phase 3

          - Number of trades executed? Phase 3

          - Percentage of data processed? Phase 3

             Add comment for Phase 3 change for all Progress Indication

      12. **Date Range Validation**: Should the system:

          - Auto-detect available date ranges from the data file? yes, based on the frequency selected so check start/end dates in 5M.txt

          - Warn users if selected range extends beyond available data? UI error

          - Provide recommended date ranges for testing? Phase 3

             Add comment for Phase 3 change for all Date Range Validation

      ### Reporting Questions

      13. **Daily P&L Chart Granularity**: The end-of-day P&L chart should show:

          - Gross P&L only? Gross + Net, 

          - Both gross and net P&L lines?

          - Cumulative P&L or daily P&L bars?

            Gross and Net, we have a round trip transaction cost variable for net. Start with Cumulative.  Add comment for potential future change

      14. **Chart Time Axes**: For the various charts:

          - Should weekend gaps be shown or compressed?
          - Display only trading days?
          - How to handle holiday gaps?
            Phase one only trading days in historical files (example 5M.txt). Add comment for potential future change