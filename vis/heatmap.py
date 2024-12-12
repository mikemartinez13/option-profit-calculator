import pandas as pd
import numpy as np

from datetime import datetime, timedelta
from typing import Optional
import random

import matplotlib.pyplot as plt
import seaborn as sns

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

class Heatmap:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(8,5))
        