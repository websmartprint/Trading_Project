import os
import pandas as pd
import datetime as dt
from data.api import get_historical_data

CACHE_DIR = os.path.join(os.path.dirname(__file__), "stock_data")
os.makedirs(CACHE_DIR, exist_ok=True)

def load_or_fetch_data(symbol: str, end: dt.datetime, window: int):
    filename = os.path.join(CACHE_DIR, f"{symbol}.csv")
    start = end - dt.timedelta(days=window)
    start_2015 = dt.datetime(2015, 1, 1, tzinfo=dt.timezone.utc)

    if os.path.exists(filename):
        df = pd.read_csv(filename, parse_dates=["timestamp"], index_col="timestamp")
    else:
        print(f"No cache found for {symbol}. Downloading from Alpaca...")
        df = get_historical_data(symbol, dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc), 10000)
        df = pd.DataFrame(df)
        df.index.name = "timestamp"
        df.to_csv(filename)
        print(f"✅ Cached {len(df)} data points to {filename}")

    # Filter and return closing prices as a Series (with timestamp index)
    filtered = df.loc[(df.index >= start) & (df.index <= end)]
    return filtered["close"]

def load_or_fetch_day(stock, end_date):
    closes = load_or_fetch_data(stock, end_date, 1)
    if closes.empty:
        return None  # or 0, or skip that day
    return closes.iloc[0]

