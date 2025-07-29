# OpenBB Streamlit Applications

This directory contains all Streamlit web applications for the OpenBB platform.

## Available Applications

### 📈 S&P 500 Intraday Momentum Strategy (`sp500_strategy_app.py`)

Interactive web dashboard for backtesting and analyzing the S&P 500 intraday momentum trading strategy.

**Features:**
- Real-time parameter adjustment
- Interactive performance charts
- Comprehensive trade analysis
- CSV data export
- Statistical significance testing

**Launch:**
```bash
cd /mnt/c/Users/kevin/git/OpenBB/app
streamlit run sp500_strategy_app.py
```

**Requirements:**
- `market_data.py` - Data retrieval module
- `../market_data/historical/` - Historical price data directory

## Usage Instructions

1. **Navigate to app directory:**
   ```bash
   cd /mnt/c/Users/kevin/git/OpenBB/app
   ```

2. **Launch any Streamlit app:**
   ```bash
   streamlit run [app_name].py
   ```

3. **Access via browser:**
   - Local: `http://localhost:8501`
   - Network: Check terminal output for network URLs

## Development

When creating new Streamlit applications:

1. Place all `.py` files in this `/app` directory
2. Update this README with app descriptions
3. Ensure proper relative imports for shared modules
4. Test locally before deployment

## Directory Structure

```
app/
├── README.md                 # This file
├── sp500_strategy_app.py    # S&P 500 strategy dashboard
├── market_data.py           # Data retrieval module
└── [future_app].py          # Additional Streamlit apps
```