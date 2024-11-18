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

def make_heatmap(contract, ticker, strategy, stock_price:float, exp, stock_range: Optional[tuple] = None):
    '''
    Calculates options profit for dates up to expiry as a heatmap. Returns a plt.axes object. 
    '''
    # dates_range = generate_dates(exp)
    
    # STRATEGIES = {
    #     'Long Call': Long_Call,
    #     'Long Put': Long_Put
    # }
    
    # strike = contract['Strike']
    # if stock_range == None:
    #     upper = stock_price * 1.05
    #     lower = stock_price * 0.95
    # else:
    #     upper = stock_range[0] 
    #     lower = stock_range[1]

    # stock_range = np.linspace(lower,upper,25)
    # stock_range = np.round(stock_range,decimals=2)
    # stock_range = stock_range[::-1]
    # stock_range.tostring()

    # fig, ax = plt.subplots(figsize=(8,5))
    
    # heatmap_data = pd.DataFrame(index=stock_range, columns=dates_range)

    # for price in stock_range:
    #     for i,date in enumerate(dates_range):
    #         # Dummy calculation example: square of the price value
    #         dte = (len(dates_range)-(i+1))/365
    #         if dte == 0:
    #             dte = (1/365)
    #         value = STRATEGIES[strategy](price,ticker,dte)
    #         heatmap_data.at[price,date] = float(value)
    #         #print(type(heatmap_data.at[price,date])) # all floats as of here


    # heatmap_data = heatmap_data.astype(float)
    # #heatmap_data.astype(float)
    
    # ax = sns.heatmap(heatmap_data,annot=True,fmt='.2f',linewidth=0.5,annot_kws={'size':4.5},cmap='RdYlGn')
    # # painting strike price line. 

    # strike = contract['Strike']
    # ymin, ymax = ax.get_ylim()

    # for i, n in enumerate(range(len(heatmap_data.index),-1,-1)):
    #     next = heatmap_data.index[n-1]
    #     if float(n) <= strike <= float(next):
    #         plt.axhline(y=(ymin - i),color = 'black',linewidth=2)
    #         break
    
    # # making final changes to the plot
    # ax.xaxis.tick_top()
    # plt.xticks(rotation=45)
    # return fig, ax
    pass

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

    return np.linspace(lower, upper, num=1000).round(2)

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
                  'scat', 
                  'xdata', 
                  'ydata', 
                  'colors')

    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 6), dpi = 100)

        self.xdata = get_stock_prices(100)  # Empty array for x data
        self.ydata = np.zeros_like(self.xdata)  # Empty array for y data
        
        self.colors = [] # Empty list for colors
        self.scat = self.ax.scatter(self.xdata,self.ydata, color = self.colors, s=1)

        self.ax.set_xlim([0, 100])
        self.ax.set_ylim([-50, 50])

        self.ax.axhline(0, color='black', lw=0.5)
        self.ax.grid(True, linestyle='--', alpha=0.7)

        self.fig.tight_layout()
        self.ax.set_xlabel('Stock Price at Expiration ($)')
        self.ax.set_ylabel('Profit ($)')
        self.ax.set_title('Strategy Payoff Diagram')

        self.ax.set_aspect('equal', adjustable='box')

        # self.check_directories()
        return
    
    def add_option(self, option: dict, opt_type:str, buy: bool, s0: float) -> None:
        '''
        Adds an option's payoff to the plot
        '''

        self.xdata = get_stock_prices(s0)

        if opt_type == 'call':
            if buy:
                payoff_series = long_call(self.xdata, option['Strike'], option['Ask'])
            else:
                payoff_series = short_call(self.xdata, option['Strike'], option['Ask'])
        elif opt_type == 'put':
            if buy:
                payoff_series = long_put(self.xdata, option['Strike'], option['Ask'])
            else:
                payoff_series = short_put(self.xdata, option['Strike'], option['Ask'])

        self.ydata += payoff_series

        self.colors = ['green' if profit >= 0 else 'red' for profit in self.ydata]
        self.scat.set_offsets(np.column_stack((self.xdata, self.ydata))) # set offsets only works with (N, 2) size
        self.scat.set_color(self.colors)

        self.ax.set_xlim([min(self.xdata)-1,
                          max(self.xdata)+1
                          ])
        
        x_range = max(self.xdata) - min(self.xdata)

        self.ax.set_ylim([-x_range/2,
                          x_range/2
                          ])

        # self.ax.set_ylim([min(self.ydata)-1,
        #                   max(self.ydata)+1
        #                   ])
        self.ax.set_aspect('equal', adjustable='box')

        self.fig.canvas.draw_idle()
        
        return
    
    def reset_data(self) -> None:
        self.xdata = get_stock_prices(100)  # Empty array for x data
        self.ydata = np.zeros_like(self.xdata)  # Empty array for y data

        self.colors = [] # Empty list for colors
        self.scat.set_offsets(np.column_stack((self.xdata, self.ydata)))
        self.scat.set_color(self.colors)

        self.ax.set_xlim([0, 100])
        self.ax.set_ylim([-50, 50])
        
        self.ax.set_aspect('equal', adjustable='box')

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