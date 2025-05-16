#   Api handler for stock bot
#
#   Author: Daniel Popa
#
#   May 5, 2025
#
#  Provides data from alpaca for the other services to use. 
# 
#  Currently only takes historical data, but in the future should allow for paper trading with alpaca
#

import yfinance as yf

import pandas as pd
import datetime as dt
import pytz

import alpaca_trade_api.rest as paca_rest
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ALPACA_KEY_FILE = os.path.join(SCRIPT_DIR, "alpaca_key.txt")
ALPACA_SECRET_KEY_FILE = os.path.join(SCRIPT_DIR, "alpaca_secret_key.txt")
ALPACA_BASE_URL_FILE = os.path.join(SCRIPT_DIR, "alpaca_base_url.txt")

def get_key(filename):

    if not os.path.exists(filename):
    #Create file
        with open (filename, "w") as f:
            f.write(f"YOUR API kere for {filename}")
        raise FileNotFoundError(f"{filename} not found, {filename} created, please insert api key")
    
    with open(filename, "r") as api_key_file:
        key = api_key_file.read()
        if not key:
            raise ValueError(f"{filename} exists but no api  key found")
        return key

#ALPACA KEYS
API_KEY = get_key(ALPACA_KEY_FILE)#'PKVMMPZ5Y36A93PKSML8'
SECRET_KEY = get_key(ALPACA_SECRET_KEY_FILE)#'fgk2vqbJzzqIyhufWlIVtAyTlszv3sIMdSfxJQvG'
BASE_URL = get_key(ALPACA_BASE_URL_FILE)#'https://paper-api.alpaca.markets'  # Use paper trading endpoint

#Alpaca api object
paca = paca_rest.REST(API_KEY, SECRET_KEY, base_url=BASE_URL)

# Global Alpaca state
ACCOUNT = paca.get_account()


#Uses the alpaca api to get "range" historical datapoints of "stock" stock 
# from a given date
def get_historical_data(stock, end_date, window):
    start_date = end_date - dt.timedelta(days=window)

    bars = paca.get_bars(
        stock,
        timeframe="1Day",
        start=start_date.isoformat(),
        end=end_date.isoformat()
    ).df

    if bars.empty or "close" not in bars.columns:
        #print(f"No data for {stock} on or before {end_date.date()}")
        return pd.Series([])  # return an empty series

    closes = bars["close"]
    return closes


def get_historical_datum(stock, end_date):
    closes = get_historical_data(stock, end_date, 1)
    if closes.empty:
        return None  # or 0, or skip that day
    return closes.iloc[0]

#Literally taken from chatgpt so solve an error
def get_most_recent_valid_price(stock, date, max_lookback=5):
    for i in range(max_lookback):
        price = get_historical_datum(stock, date - dt.timedelta(days=i))
        if price is not None:
            return price
    return None