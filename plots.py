import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Optional
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, DataReturnMode, JsCode

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



def generate_dates(expiration_date):
    '''
    Helper function for the make_plots function. Generates dates up to expiry, with maximum 20 dates generated. 
    '''
    # Convert the expiration date string to a datetime object
    expiration_date = datetime.strptime(expiration_date, '%Y-%m-%d')
    
    # Initialize an empty list to store previous dates
    dates_generated_list = []

    today = datetime.today()

    
    num_dates = (expiration_date-today).days
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
    
    dates_generated_list.reverse()
    
    return dates_generated_list



def make_heatmap(contract, stock_price:float, exp, stock_range: Optional[tuple] = None):
    '''
    Calculates options profit for dates up to expiry as a heatmap. Returns a plt.axes object. 
    '''
    dates_range = generate_dates(exp)
    
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
        for date in dates_range:
            # Dummy calculation example: square of the price value
            value = price + 10
            heatmap_data.at[price,date] = float(value)
            #print(type(heatmap_data.at[price,date])) # all floats as of here

    heatmap_data = heatmap_data.astype(float)
    #heatmap_data.astype(float)
    
    ax = sns.heatmap(heatmap_data,annot=True,fmt='.2f',linewidth=0.5,annot_kws={'size':4.5},cmap='RdYlGn')
    # painting strike price line. 

    # strike = contract.loc['Strike'] 
    # if lower <= strike <= upper:
    #     print('worked')
    #     ax.hlines(strike, *ax.get_xlim())
    #     ax.axhline(y=strike)
    
    # making final changes to the plot
    ax.xaxis.tick_top()
    plt.xticks(rotation=45)
    return fig, ax

