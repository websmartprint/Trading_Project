import datetime as dt
from data.api import get_historical_data
from data.data_loader import load_or_fetch_data
import pandas as pd

def rs_calc(data):
    sum_up = 0
    sum_down = 0

    length = len(data)

    prev = data[0]

    for datum in data[1:]:
        if datum > prev:
            sum_up += (datum - prev)
        elif datum < prev:
            sum_down += (prev - datum)
        prev = datum

    # Avoid divide-by-zero
    avg_up = sum_up / length
    avg_down = sum_down / length

    return avg_up / avg_down


def calc_simple_rsi(data):
    return 100 - (100/(1+rs_calc(data)))

def simple_rsi_detector(stock, date, simulation: bool):
    window = 30
    days_past = 1

    cutoff_high = 70
    cutoff_low = 30

    #yesterday = date - dt.timedelta(days = 1)

    historical_data = load_or_fetch_data(stock, date, window+days_past)#get_historical_data(stock, date, window+days_past)

    rsi_today = calc_simple_rsi(historical_data[:window-1])

    rsi_yestderday = calc_simple_rsi(historical_data[1:window+days_past-1])

    if rsi_yestderday > cutoff_high and rsi_today <= cutoff_high:
        return "sell"
    elif rsi_yestderday < cutoff_low and rsi_today >= cutoff_low:
        return "buy"

    return "hold"