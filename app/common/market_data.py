# File: market_data.py

import pandas as pd
from openbb import obb
from pathlib import Path
import re 
import io 

class Retrieve:
    """A class to retrieve financial market data."""

    @staticmethod
    def from_provider(symbols: list, start_date: str, end_date: str, frequency: str = "1D") -> pd.DataFrame:
        """Fetches historical price data for a list of symbols from a provider."""
        dataframes = []
        print(f"📊 Fetching {frequency} historical data from provider...")

        # Map frequency to yfinance interval
        interval_map = {
            "1M": "1m",
            "5M": "5m", 
            "30M": "30m",
            "1H": "1h",
            "1D": "1d"
        }
        
        yf_interval = interval_map.get(frequency, "1d")

        for symbol in symbols:
            try:
                # The f"^{symbol}" format is specific to Yahoo Finance for indices
                data = obb.equity.price.historical(
                    symbol=f"^{symbol}",
                    start_date=start_date,
                    end_date=end_date,
                    interval=yf_interval,
                    provider="yfinance"
                ).to_df()

                data = data.reset_index()
                data['Symbol'] = symbol
                dataframes.append(data)
                print(f"✓ Fetched {len(data)} {frequency} records for {symbol}")

            except Exception as e:
                print(f"❌ Failed to fetch {frequency} data for {symbol}: {e}")
                # Try without interval parameter as fallback
                try:
                    print(f"🔄 Retrying {symbol} without interval parameter...")
                    data = obb.equity.price.historical(
                        symbol=f"^{symbol}",
                        start_date=start_date,
                        end_date=end_date,
                        provider="yfinance"
                    ).to_df()
                    
                    data = data.reset_index()
                    data['Symbol'] = symbol
                    dataframes.append(data)
                    print(f"✓ Fetched {len(data)} daily records for {symbol} (fallback)")
                    
                except Exception as e2:
                    print(f"❌ Both attempts failed for {symbol}: {e2}")

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
            # Use absolute path from project root to ensure tests work
            project_root = Path(__file__).parent.parent.parent
            filepath = project_root / "market_data" / "historical" / symbol / f"{freq}.txt"
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
    
    def get_data(self, symbol: str, start_date: str, end_date: str, frequency: str = "1D") -> pd.DataFrame:
        """
        Main method to retrieve market data - prioritizes files for intraday data
        Expected by CFD strategy implementations
        """
        # For intraday frequencies, try files first (where the good data is)
        if frequency in ["1M", "5M", "30M", "1H"]:
            try:
                # Try file data first for intraday frequencies
                print(f"🔄 Attempting to load {symbol} {frequency} data from files...")
                data = self.from_file([symbol], start_date, end_date, frequency)
                
                if not data.empty:
                    # Convert to expected format
                    data = data.rename(columns={
                        'date': 'Date',
                        'open': 'Open',
                        'high': 'High', 
                        'low': 'Low',
                        'close': 'Close'
                    })
                    
                    # Add volume if missing
                    if 'Volume' not in data.columns:
                        data['Volume'] = 1000000  # Default volume
                    
                    # Set date as index
                    if 'Date' in data.columns:
                        data['Date'] = pd.to_datetime(data['Date'])
                        data.set_index('Date', inplace=True)
                    
                    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                    print(f"✅ Successfully loaded {len(data)} records from files")
                    return data[required_cols]
                    
            except Exception as e:
                print(f"⚠️  File loading failed: {e}")
        
        # For daily data or if files failed, try provider
        try:
            print(f"🔄 Attempting to fetch {symbol} {frequency} data from provider...")
            data = self.from_provider([symbol], start_date, end_date, frequency)
            
            if not data.empty:
                # Convert to expected format for CFD strategies
                data = data.rename(columns={
                    'date': 'Date',
                    'open': 'Open', 
                    'high': 'High',
                    'low': 'Low',
                    'close': 'Close',
                    'volume': 'Volume'
                })
                
                # Set date as index
                if 'Date' in data.columns:
                    data['Date'] = pd.to_datetime(data['Date'])
                    data.set_index('Date', inplace=True)
                
                # Ensure required columns exist
                required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
                for col in required_cols:
                    if col not in data.columns:
                        if col == 'Volume':
                            data[col] = 1000000  # Default volume
                        else:
                            data[col] = data.get('Close', 0)  # Use close price as fallback
                
                print(f"✅ Successfully retrieved {len(data)} records from provider")
                return data[required_cols]
            
        except Exception as e:
            print(f"⚠️  Provider fetch failed: {e}")
        
        # If all methods fail, raise an error - don't mask issues with synthetic data
        error_msg = f"❌ All data sources failed for {symbol} ({frequency}) from {start_date} to {end_date}"
        print(error_msg)
        raise ValueError(error_msg)
