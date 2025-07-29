import pandas as pd
from datetime import datetime, timedelta
from openbb import obb
from market_data import Retrieve

# Define parameters for the data retrieval
# These are S&P 500 and NASDAQ index tickers for yfinance
my_symbols = ["SPX"]
start_date = "2024-01-01"
end_date = "2024-07-29"

# Call the static method directly from the class
# No need to create an instance like `retriever = Retrieve()`
market_df = Retrieve.from_provider(
    symbols=my_symbols,
    start_date=start_date,
    end_date=end_date
)

market_df
