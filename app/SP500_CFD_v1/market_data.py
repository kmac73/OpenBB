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
            filepath = Path(f"../market_data/historical/{symbol}/{freq}.txt")
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
        Main method to retrieve market data - tries provider first, falls back to files
        Expected by CFD strategy implementations
        """
        try:
            # Try provider first (for real-time data)
            print(f"🔄 Attempting to fetch {symbol} data from provider...")
            data = self.from_provider([symbol], start_date, end_date)
            
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
        
        try:
            # Fallback to file data
            print(f"🔄 Attempting to load {symbol} data from files...")
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
        
        # If all methods fail, generate synthetic data for testing
        print(f"⚠️  All data sources failed. Generating synthetic data for testing...")
        return self._generate_synthetic_data(symbol, start_date, end_date, frequency)
    
    def _generate_synthetic_data(self, symbol: str, start_date: str, end_date: str, frequency: str = "5M") -> pd.DataFrame:
        """Generate synthetic market data for testing purposes"""
        import numpy as np
        
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        # Generate time series based on frequency
        if frequency == "5M":
            # Generate 5-minute intervals during trading hours only
            dates = []
            current_date = start_dt
            
            while current_date <= end_dt:
                # Only weekdays
                if current_date.weekday() < 5:
                    # Trading hours: 9:30 AM - 4:00 PM
                    for hour in range(9, 16):
                        for minute in [30, 35, 40, 45, 50, 55] if hour == 9 else [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]:
                            if hour == 15 and minute > 0:  # Stop at 4:00 PM
                                break
                            dt = current_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                            dates.append(dt)
                current_date += pd.Timedelta(days=1)
        else:
            # Daily data
            dates = pd.date_range(start=start_dt, end=end_dt, freq='D')
            # Filter to weekdays only
            dates = dates[dates.weekday < 5]
        
        # Limit data size for performance
        if len(dates) > 2000:
            dates = dates[:2000]
        
        # Generate realistic price data
        np.random.seed(42)  # Reproducible for testing
        base_price = 4500.0 if symbol == "SPX" else 100.0
        
        prices = []
        current_price = base_price
        
        for i, date in enumerate(dates):
            # Random walk with slight upward bias
            price_change = np.random.normal(0.05, 2.0)  # Small upward bias, 2 point volatility
            current_price = max(current_price + price_change, base_price * 0.8)  # Floor at 80% of base
            
            # Generate OHLC
            high = current_price + abs(np.random.normal(0, 1.0))
            low = current_price - abs(np.random.normal(0, 1.0)) 
            volume = int(np.random.lognormal(13, 0.5))  # Realistic volume
            
            prices.append({
                'Open': current_price,
                'High': high,
                'Low': low, 
                'Close': current_price,
                'Volume': volume
            })
        
        data = pd.DataFrame(prices, index=dates)
        print(f"✅ Generated {len(data)} synthetic data points for {symbol}")
        return data