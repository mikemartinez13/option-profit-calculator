import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Optional

def convert_dates(dates: list):
    '''
    Converts list of dates returned by 
    '''
    converted_dates = []
    for date_str in dates:
        # Convert the date string to a datetime object
        date_obj = datetime.strptime(date_str, '%B %d, %Y')
        # Convert the datetime object to the desired format
        converted_date = date_obj.strftime('%Y-%m-%d')
        converted_dates.append(converted_date)

    return converted_dates



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
            #print(type(heatmap_data.at[price,date])) # all floats as of here


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

# Functions to graph possible payoff of options strategies

def long_call(S, K, Price):
    P = np.maximum(S-K, 0) - Price
    return P

def short_call(S, K, Price):
    return -1.0 * long_call(S, K, Price)

def long_put(S, K, Price):
    P = np.maximum(K-S, 0) - Price
    return P

def short_put(S, K, Price):
     return -1.0 * long_put(S, K, Price)

def get_stock_prices(s0):
    '''
    s0: current stock price
    '''
    lower = s0 * (1 - 0.5) 
    upper = s0 * (1 + 0.5)

    return np.arange(lower, upper+0.1, 0.1).round(2)

def plot_payoff(stock_series, payoff_series):

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['green' if profit >= 0 else 'red' for profit in payoff_series]

    scatter = ax.scatter(stock_series, payoff_series, color=colors, s = 1)
    ax.axhline(0, color='black', lw=0.5)
    ax.set_xlabel('Stock Price at Expiration ($)')
    ax.set_ylabel('Profit ($)')

    # Set title
    ax.set_title('Option Profit Diagram')
    
    ax.grid(True, linestyle='--', alpha=0.7)

    # Tight layout for better spacing
    fig.tight_layout()

    return fig

class OptionPayoffPlot:
    '''
    Class to plot payoff of options strategies.

    Contains, fig, ax, and scat objects.
    '''
    __slots__ = ('fig', 
                 'ax', 
                 'scat'
                 )
    
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 6), dpi = 100)

        self.xdata = np.array([])  # Empty array for x data
        self.ydata = np.array([])  # Empty array for y data
        
        self.colors = [] # Empty list for colors
        self.scat = self.ax.scatter(self.xdata,self.ydata, color = self.colors, s=1)

        self.ax.set_xlim([0, 100])
        self.ax.set_ylim([-100, 100])

        self.ax.axhline(0, color='black', lw=0.5)
        self.ax.grid(True, linestyle='--', alpha=0.7)

        self.fig.tight_layout()
        self.ax.set_xlabel('Stock Price at Expiration ($)')
        self.ax.set_ylabel('Profit ($)')
        self.ax.set_title('Strategy Payoff Diagram')

        # self.check_directories()
        return
    
    def add_option(self, option) -> None:
        '''
        Adds an option's payoff to the plot
        '''
        self.xdata = np.concatenate((self.xdata, stock_series))
        self.ydata = np.concatenate((self.ydata, payoff_series))

        self.colors = ['green' if profit >= 0 else 'red' for profit in payoff_series]
        self.scat.set_offsets(np.column_stack(self.xdata, self.ydata)) # set offsets only works with (N, 2) size

        self.ax.set_xlim([min(self.xdata)-1,
                          max(self.xdata)+1
                          ])
        self.ax.set_ylim([min(self.ydata)-1,
                          max(self.ydata)+1
                          ])

        return
    
    def reset_data(self) -> None:
        self.xdata = np.array([])
        self.ydata = np.array([])

        self.scat.set_offsets(np.column_stack(self.xdata, self.ydata))

        self.ax.set_xlim([0, 100])
        self.ax.set_ylim([-100, 100])

        return

    # def save_plot(self, file_name: str) -> None:
    #     '''
    #     Save the currently displayed figure as a .png file.
    #     '''
    #     if file_name != '':
    #         print(f'Saving: {file_name}.png')
    #         self.fig.savefig(f'{file_name}.png', bbox_inches='tight')
    #     return


if __name__ == '__main__':
    S_current = 418
    S = get_stock_prices(S_current)
    P1 = long_call(S, 400, 130)
    fig = plot_payoff(S, P1)
    plt.savefig('long_call.png')