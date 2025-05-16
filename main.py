#   Main of stock bot
#
#   Author: Daniel Popa
#
#   May 5, 2025
#
#  Runs the stock bot.
#
#   To run a simulation replace start_date, stock, and cycles (number of days) with the desired values
#   For decision alg use the decison making algorithm you want to use for buying and selling stocks from the strategies package
#
#   Be aware for very long time periods (a year or more), there can be issue with the volume of api calls

from simulation import simdays
from strategies.moving_average import simple_moving_average_decider
from strategies.rsi import simple_rsi_detector
import datetime as dt
import numpy as np

if __name__ == "__main__":

    start_date = dt.datetime(2017, 1, 1, tzinfo=dt.timezone.utc)
    stock = "TSLA"
    cycles = 50
    budget_given = 100000
    #decision_alg = simple_moving_average_decider
    decision_alg = simple_rsi_detector

    returns = np.zeros(0)
    
    returns = np.append(returns, simdays(
        budget=budget_given,
        stock=stock,
        start_date=start_date,
        cycles=cycles,
        decision_function=decision_alg,
        print_days=False
    )
    )

    print(returns)
