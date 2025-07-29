# File: market_data.py

import pandas as pd
from openbb import obb
from pathlib import Path
import re 
import io 

class Retrieve:
    """A class to retrieve financial market data."""

    @staticmethod
    def from_provider(symbols: list, start_date: str, end_date: str) -> pd.DataFrame:
        """Fetches historical price data for a list of symbols from a provider."""
        dataframes = []
        print("📊 Fetching historical data from provider...")

        for symbol in symbols:
            try:
                # The f"^{symbol}" format is specific to Yahoo Finance for indices
                data = obb.equity.price.historical(
                    symbol=f"^{symbol}",
                    start_date=start_date,
                    end_date=end_date,
                    provider="yfinance"
                ).to_df()

                data = data.reset_index()
                data['Symbol'] = symbol
                dataframes.append(data)
                print(f"✓ Fetched {len(data)} records for {symbol}")

            except Exception as e:
                print(f"❌ Failed to fetch data for {symbol}: {e}")

        # If the list is empty, return an empty DataFrame, NOT None
        if not dataframes:
            print("\n❌ No data was fetched.")
            return pd.DataFrame()

        # Combine, print summary, and return the final DataFrame
        daily_data = pd.concat(dataframes, ignore_index=True)
        print(f"\n📈 Combined provider dataset has {len(daily_data)} total records.")
        return daily_data

    @staticmethod
    def from_file(symbols: list, start_date: str, end_date: str, freq: str) -> pd.DataFrame:
        """
        Retrieves historical data from pre-saved local files, handling cases
        with no headers and concatenated records.
        """
        dataframes = []
        print(f"📂 Loading historical data from files for freq='{freq}'...")

        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)

        for symbol in symbols:
            filepath = Path(f"market_data/historical/{symbol}/{freq}.txt")
            try:
                headers = ['date', 'open', 'high', 'low', 'close']
                raw_text = filepath.read_text()
                processed_text = re.sub(r'(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})', r'\n\1', raw_text).strip()
                string_data = io.StringIO(processed_text)
                data = pd.read_csv(string_data, header=None, names=headers)
                
                data['date'] = pd.to_datetime(data['date'])
                mask = (data['date'] >= start_dt) & (data['date'] <= end_dt)
                filtered_data = data.loc[mask].copy()

                if filtered_data.empty:
                    print(f"✓ No data for {symbol} within the specified date range in {filepath}.")
                    continue
                
                filtered_data['Symbol'] = symbol
                dataframes.append(filtered_data)
                print(f"✓ Loaded {len(filtered_data)} records for {symbol} from {filepath}")

            except FileNotFoundError:
                print(f"❌ File not found for symbol '{symbol}' at: {filepath}")
            except Exception as e:
                print(f"❌ Failed to process file for {symbol}: {e}")

        if not dataframes:
            print("\n❌ No data was loaded from files.")
            return pd.DataFrame()

        combined_data = pd.concat(dataframes, ignore_index=True)
        print(f"\n📈 Combined file dataset has {len(combined_data)} total records.")
        return combined_data