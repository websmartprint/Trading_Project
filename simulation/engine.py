#   Simulation engine for stock bot
#
#   Author: Daniel Popa
#
#   May 5, 2025
#
#  Simulates buys, sells, uses data package to get historical values (DOESNT TAKE INTO ACCOUNT STOCK SPLITS)
#  Also generates a pdf of the results of the simulation
#

import datetime as dt
from data.api import get_historical_datum, get_most_recent_valid_price
from data.data_loader import load_or_fetch_data, load_or_fetch_day
from fpdf import FPDF
import matplotlib.pyplot as plt
import os
import numpy as np

def export_sim_report(stock, prices, net_worth, cycles, filename = "report.pdf"):
    
    #Make plot for stock prices
    price_path = "price_plot.png"
    plt.plot(prices)
    plt.title(f"{stock} Price Over Time")
    plt.xlabel("Day")
    plt.ylabel("Price ($)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(price_path)
    plt.close()

    #make plot for portfolio net worth
    net_val_path = "net_plot.png"
    plt.plot(net_worth)
    plt.title(f"Net Value Over Time (Ballance and Invested)")
    plt.xlabel("Day")
    plt.ylabel("Value ($)")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(net_val_path)
    plt.close()

    #Generate pdf
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size = 12)

    pdf.cell(200, 10, txt=f"{stock} Trading Simulation Report", ln=True, align='C')
    pdf.ln(5)

    #add graphs
    IMG_W = 180
    IMG_H = IMG_W * 2/3   # ≈120

    y_top = 30
    pdf.image(price_path, x=10, y=y_top, w=IMG_W)

    pdf.set_y(y_top + IMG_H + 5)
    pdf.image(net_val_path, x=10, y=pdf.get_y(), w=IMG_W)

    pdf.set_y(pdf.get_y() + IMG_H + 10)

    pdf.cell(200, 10, txt=f"TBD WILL ADD INFO HERE", ln=True)
    pdf.ln(5)

    #Save file
    reports_dir = os.path.join(os.path.dirname(__file__), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    report_path = os.path.join(reports_dir, f"{stock}_report.pdf")
    pdf.output(report_path)

    
    if os.path.exists(report_path):

        print(f"✅ PDF report generated: {filename}")
        os.startfile(report_path)

    else:
        print("file not created")

    # Optionally clean up image
    if os.path.exists(price_path):
        os.remove(price_path)
    if os.path.exists(net_val_path):
        os.remove(net_val_path)


def simdays(budget,stock, start_date, cycles, decision_function, print_days = True):
    date = start_date
    counter = 0
    results = []
    ballance = budget
    invested = 0
    sells = 0
    buys = 0
    price = get_historical_datum(stock, date)

    prices = np.zeros(0)
    net_value =  np.zeros(0)

    day_one_price = get_most_recent_valid_price(stock, date)
    money_spent = 0
    return_from_stock = 0

    print('------------------------------------------')
    print("Running Simulation (LOCAL NOT ALPACA)")
    print(f'For {stock} Stock')
    print(f'Simulation start {start_date}')
    print(f'For {cycles} days and {budget} dollars')

    for i in range(cycles):
        decision = decision_function(stock, date, True)
        results.append((date.date(), decision))
        date += dt.timedelta(days=1)

        price = load_or_fetch_day(stock, date)#get_historical_datum(stock, date)

        #Skip weekend days
        if price is None:
            if print_days:
                print(f"{date.date()}: Market closed or no data.")
            counter +=1
            continue

        if decision == "buy" and ballance >= price:
            ballance = ballance - price
            invested = invested + 1
            money_spent += price
            buys = buys + 1
        
        elif decision == "sell" and invested > 0:
            ballance = ballance + price
            invested = invested - 1
            return_from_stock += price
            sells = sells + 1
        
        elif decision != "hold":
            decision = f"hold (but wanted {decision})"

        if print_days:
            print(f'On {date} ({counter}/{cycles}) made decision {decision}, {stock} price: {price}, Ballance: {ballance}, shares: {invested}')
        else:
            print(f'On {date}, {counter}/{cycles}')
        
        counter = counter + 1

        prices = np.append(prices, price)

        investments = invested * price
        net_value = np.append(net_value, ballance + investments - budget)

    print('------------------------------------------')
    print()
    print(f'For {stock} Stock')
    print(f'Simulation start {start_date}')
    print(f'For {cycles} days and {budget} dollars')
    print(f'Sells: {sells}, Buys: {buys}')
    print(f'Start ballance: {budget}, End Ballance {ballance}')

    #Find value held in shares
    price = get_most_recent_valid_price(stock, date)
    if price is None:
        print("Could not find recent price to value holdings.")
        investments = 0
    else:
        investments = invested * price

    print(f'Hold {invested} shares, valuing: {investments} dollars')
    print(f'Net Gain: {ballance + investments - budget}')

    last_day_price = get_most_recent_valid_price(stock, date)
    portfolio_delta = (return_from_stock+investments)/money_spent
    market_delta = last_day_price/day_one_price
    delta_ratio = portfolio_delta/market_delta
    beat_market = delta_ratio > 1

    #print(f'If only held, gain would be: {buys*last_day_price - buys*day_one_price}')
    print(f'Portfolio increase: {portfolio_delta}, Market increase: {market_delta}')
    print(f'Performance to market: {delta_ratio}, Beat Market: {beat_market}')

    export_sim_report(stock, prices, net_value, cycles)

    return ballance + investments - budget