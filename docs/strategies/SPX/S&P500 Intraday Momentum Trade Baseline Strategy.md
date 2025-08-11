# S&P500 Intraday Momentum Trade Strategy

**Technical Parameters**

1. Use Python, Jupyter Notebooks, Streamlit and Plotly for analysis and reporting

## **Trade Strategy Parameters**

1. Trades can be entered into as LONG or SHORT

\-      LONG trades bet on the rise of the S&P and take profit from S&P price increases

\-      SHORT trades bet on the decrease of the S&P and take profit from S&P price declines

1. Strategy starts at Open (9:30am) and no new positions can be entered after 3pm. All open positions     must by closed before 4pm. No positions can be held overnight. 
2. The baseline price for trading starts on the T-1 (previous day) close 
3. Positions are entered when the S&P500 price hits 2 basis points (bps) from the baseline price. This     can either be a LONG or SHORT position as explained above
4. Baseline resets to the price the position is exited from 
5. Each tick in the direction of the LONG or SHORT equals $100
6. Stop loss is when trade reverts 0.75 bps back to the baseline and the trade exits. The baseline is     set to this new price
7. Profit taking is set to 2bps and the baseline is reset to the exit price
8. Transaction costs to PnL is 0.445

 

## **Strategy Test (Generate Report)**

1. Back test these parameters against S&P historical data provided
2. Record per trade PnL performance
   1. Per trade SHORT/LONG entry and exit
   2. Profit/Loss
   3. Stop out
   4. Transaction Cost
3. Maintain a P&L totals table
   1. Number of trades executed
   2. Number of LONG/SHORT      trades executed
   3. Win Rate
   4. Total transaction cost
   5. Total PnL (profit/loss)
4. Plot performance charts

## **Trade Strategy Optimization (Generate Report)**

1. Find optimal basis point     entry exit ratios for execution keeping in mind reducing transaction costs     (fewer trades)
2. Generate P-Values on probabilities

## **Implementation Status**

### ✅ **Completed Features**

**Interactive Streamlit Application** (`sp500_strategy_app.py`)
- Full web-based dashboard with parameter controls
- Real-time strategy execution and analysis
- Interactive Plotly charts (enhanced from Matplotlib requirement)

**Strategy Implementation**
- ✅ LONG/SHORT position support
- ✅ T-1 baseline price initialization
- ✅ 2 bps entry threshold (configurable)
- ✅ 0.75 bps stop loss (configurable) 
- ✅ 2 bps profit target (configurable)
- ✅ $100 tick value (configurable)
- ✅ $0.445 transaction cost (configurable)
- ✅ Baseline reset to exit price

**Trade Reporting & Analytics**
- ✅ Per-trade PnL tracking with full details
- ✅ Entry/exit price recording
- ✅ Profit/loss calculation
- ✅ Stop-out tracking
- ✅ Transaction cost accounting
- ✅ Exit reason classification (PROFIT_TARGET, STOP_LOSS, CLOSE)

**P&L Summary Dashboard**
- ✅ Total trades executed count
- ✅ LONG/SHORT trade breakdown
- ✅ Win rate calculation
- ✅ Total transaction costs
- ✅ Net P&L reporting
- ✅ Average P&L per trade
- ✅ Profit factor calculation

**Performance Visualization**
- ✅ Cumulative P&L progression chart
- ✅ Trade P&L distribution histogram
- ✅ LONG vs SHORT performance comparison
- ✅ Exit reason breakdown (pie chart)
- ✅ Win/loss analysis by position type
- ✅ Entry vs exit price scatter plot
- ✅ Monthly P&L breakdown
- ✅ Interactive chart dashboard (9+ chart types)

**Advanced Analytics**
- ✅ Statistical significance testing (t-test with p-values)
- ✅ Performance metrics calculation
- ✅ Risk analysis reporting

**Data Export & Management**
- ✅ CSV export functionality for all trade data
- ✅ Historical data integration via `Retrieve.from_file()`
- ✅ Configurable date ranges and frequencies
- ✅ Session state management for performance

**User Experience**
- ✅ Parameter sidebar with real-time updates
- ✅ Manual execution control (no auto-run on startup)
- ✅ Interactive parameter adjustment
- ✅ Comprehensive performance metrics display
- ✅ Professional dashboard layout

### **Usage Instructions**

1. **Launch Application**:
   ```bash
   cd /mnt/c/Users/kevin/git/OpenBB/app
   streamlit run sp500_strategy_app.py
   ```

2. **Configure Parameters**: Use sidebar to adjust strategy parameters
3. **Execute Strategy**: Click "🚀 Run Strategy" button
4. **Review Results**: Analyze performance metrics and interactive charts
5. **Export Data**: Download trade details as CSV file

### **Key Files**
- `app/sp500_strategy_app.py` - Main Streamlit application
- `app/market_data.py` - Data retrieval module  
- `market_data/historical/SPX/5M.txt` - Historical price data
- `notebooks/sp500_strategy_notebook.ipynb` - Original analysis notebook