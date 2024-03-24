import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

from typing import Optional

from Math import Long_Call, Long_Put

def transcribe_option(option_string):
    '''
    Takes an option code (e.g. AAPL071222C00122500) and outputs as plain text (e.g. )
    '''
    t = 0
    for i, char in enumerate(option_string):
        if char.isdigit():
            t = i
            break
    ticker_symbol = option_string[:t]
    expiry_date = option_string[t:t+7]  # YYMMDD
    strike_price = int(option_string[-8:])  # First five digits represent whole number
    strike_price_decimal = int(option_string[-3:])  # Last three digits represent decimals
    strike_price /= 1000  # Convert decimal part to proper fraction
    option_type = "Call" if option_string[t+6] == 'C' else "Put"

    month_names = {
        "01": "January", "02": "February", "03": "March", "04": "April",
        "05": "May", "06": "June", "07": "July", "08": "August",
        "09": "September", "10": "October", "11": "November", "12": "December"
    }
    month = month_names[expiry_date[2:4]]
    # Convert YYMMDD to a readable date format
    expiry_date_readable = f"20{expiry_date[:2]} {month} {expiry_date[4:6]}"
    
    return f"{expiry_date_readable} ${strike_price:.3f} {option_type} on {ticker_symbol}"
    

def generate_dates(expiration_date):
    # Convert the expiration date string to a datetime object
    date_obj = datetime.strptime(expiration_date, '%B %d, %Y')
    expiration_date = datetime.strftime(date_obj, '%Y-%m-%d')
    expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d')
    # Initialize an empty list to store previous dates
    dates_generated_list = []

    today = datetime.today()

    print(today)
    num_dates = (expiration_date-today).days + 1
    print(num_dates)
    # Calculating max number of dates to be generated
    max_dates = 20
    step_size = max(1, num_dates // max_dates)

    dates_generated = [expiration_date - timedelta(days=i) for i in range(0, num_dates, step_size)]
    # Generate previous dates
    # for i in range(num_dates):
    #     previous_date = expiration_date - timedelta(days=i+1)
    #     previous_dates_list.append(previous_date.strftime('%Y-%m-%d'))
    for n in dates_generated:
        print(n)
    [dates_generated_list.append(n.strftime('%Y-%m-%d')) for n in dates_generated]
    # previous_dates_list.reverse()
    dates_generated_list.reverse()
    # previous_dates_list = previous_dates_list.reverse()
    return dates_generated_list

def make_heatmap(contract, ticker, strategy, stock_price:float, exp, stock_range: Optional[tuple] = None):
    '''
    Calculates options profit for dates up to expiry as a heatmap. Returns a plt.axes object. 
    '''
    dates_range = generate_dates(exp)
    
    STRATEGIES = {
        'Long Call': Long_Call,
        'Long Put': Long_Put
    }
    
    strike = contract['Strike']
    if stock_range == None:
        upper = stock_price * 1.05
        lower = stock_price * 0.95
    else:
        upper = stock_range[0] 
        lower = stock_range[1]

    stock_range = np.linspace(lower,upper,25)
    stock_range = np.round(stock_range,decimals=2)
    stock_range = stock_range[::-1]
    stock_range.tostring()

    fig, ax = plt.subplots(figsize=(8,5))
    
    heatmap_data = pd.DataFrame(index=stock_range, columns=dates_range)

    for price in stock_range:
        for i,date in enumerate(dates_range):
            # Dummy calculation example: square of the price value
            dte = (len(dates_range)-(i+1))/365
            if dte == 0:
                dte = (1/365)
            value = STRATEGIES[strategy](price,ticker,dte)
            heatmap_data.at[price,date] = float(value)

    heatmap_data = heatmap_data.astype(float)
    #heatmap_data.astype(float)
    
    ax = sns.heatmap(heatmap_data,annot=True,fmt='.2f',linewidth=0.5,annot_kws={'size':4.5},cmap='RdYlGn')
    # painting strike price line. 

    strike = contract['Strike']
    ymin, ymax = ax.get_ylim()

    for i, n in enumerate(range(len(heatmap_data.index),-1,-1)):
        next = heatmap_data.index[n-1]
        if float(n) <= strike <= float(next):
            plt.axhline(y=(ymin - i),color = 'black',linewidth=2)
            break
    
    # making final changes to the plot
    ax.xaxis.tick_top()
    plt.xticks(rotation=45)
    return fig, ax