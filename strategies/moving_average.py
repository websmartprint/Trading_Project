#   Moving average package
#
#   Author: Daniel Popa
#
#   May 5, 2025
#
#  Contains moving average algorithms that can be used to decide whether stocks are bought or sold
#  All fuctions should return a string "buy", "sell", "hold"
#  Decison making fucntion have acess to the data package to get historcal stock data to make their decisons

import datetime as dt
from data.api import get_historical_data
from data.data_loader import load_or_fetch_data
import pandas as pd

def calc_moving_avg(stock, end_date, window):
    series = pd.Series(get_historical_data(stock, end_date, window))
    return series.mean()

def calc_moving_avg(data):
    series = pd.Series(data)
    return series.mean()

def simple_moving_average_decider(stock, date, simulation: bool):
    long_w = 50
    short_w = 20          # old settings

    if not simulation:
        data = get_historical_data(stock, date, long_w*2.2)  # Mult by 2 to account for weekends
    else:
        data = load_or_fetch_data(stock, date, long_w*2.2)

    if len(data) < long_w + 1:
        return "hold"                 # not enough history

    #For testing
    #print(type(data), data.index if isinstance(data, pd.Series) else "no index")

    # most-recent window (today)
    long_today  = data[-long_w:].mean()
    short_today = data[-short_w:].mean()

    # previous window (yesterday)
    long_yest  = data[-(long_w+1):-1].mean()
    short_yest = data[-(short_w+1):-1].mean()

    crossed_up   = short_yest < long_yest and short_today > long_today
    crossed_down = short_yest > long_yest and short_today < long_today

    if crossed_up:
        return "buy"
    if crossed_down:
        return "sell"
    return "hold"
