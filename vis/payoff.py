import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Optional
import random

import plotly.graph_objs as go
import plotly.io as pio
import plotly.offline as offline

import os
import tempfile

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
    lower = s0 * (1 - 5) 
    upper = s0 * (1 + 5)

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

    def __init__(self):

        self.layout = go.Layout(
            xaxis=dict(
                range=[0, 1000],  # Fixed range without allowing panning beyond
                autorange=True,  # Disables auto-ranging
                rangemode='tozero'  # Fixed range without allowing panning beyond
            ),
            yaxis=dict(
                range=[-1000, 1000],
                autorange=True,
                rangemode='tozero'
            )
        )

        self.fig = go.Figure(layout=self.layout)

        self.positive_trace = go.Scatter(
            x=[],
            y=[],
            mode='lines',
            line=dict(color='green'),
            name='Profit >= 0'
        )
        self.negative_trace = go.Scatter(
            x=[],
            y=[],
            mode='lines',
            line=dict(color='red'),
            name='Profit < 0'
        )

        self.fig.add_trace(self.positive_trace)
        self.fig.add_trace(self.negative_trace)

        self.fig.update_layout(
            title='Strategy Payoff Diagram',
            xaxis_title='Stock Price at Expiration ($)',
            yaxis_title='Profit ($)',
            showlegend=True,
            template='plotly',
            hovermode='closest'
        )

        self.html = self.generate_html() # initialize temp file path

        return
    
    def generate_html(self):
        """
        Generates the HTML string for the current Plotly figure.
        """
        html = '<html><body>'
        html += offline.plot(self.fig, output_type='div', include_plotlyjs='cdn')# config=config)
        html += '</body></html>'

        return html

    def add_option(self, option: dict, opt_type:str, buy: bool, s0: float) -> None:
        '''
        Adds an option's payoff to the plot
        '''

        self.xdata = get_stock_prices(s0)

        if opt_type == 'call':
            if buy:
                payoff_series = long_call(self.xdata, option['Strike'], option['Ask'])
                label = 'Long Call'
            else:
                payoff_series = short_call(self.xdata, option['Strike'], option['Ask'])
                label = 'Short Call'
        elif opt_type == 'put':
            if buy:
                payoff_series = long_put(self.xdata, option['Strike'], option['Ask'])
                label = 'Long Put'
            else:
                payoff_series = short_put(self.xdata, option['Strike'], option['Ask'])
                label = 'Short Put'

        if hasattr(self, 'ydata'):
            self.ydata += payoff_series
        else:
            self.ydata = payoff_series

        self.update_traces()
        
        return 
    
    def update_traces(self):
        '''
        Splits the data into positive and negative segments and updates the Plotly traces.
        '''
        # Positive profits
        pos_x, pos_y = [], []
        # Negative profits
        neg_x, neg_y = [], []
        
        for x, y in zip(self.xdata, self.ydata):
            if y >= 0:
                pos_x.append(x)
                pos_y.append(y)
                # To handle transitions, add a point at y=0
                # if neg_x and neg_y and neg_y[-1] < 0:
                #     pos_x.insert(-1, x)
                #     pos_y.insert(-1, 0)
            else:
                neg_x.append(x)
                neg_y.append(y)
                # To handle transitions, add a point at y=0
                # if pos_x and pos_y and pos_y[-1] >= 0:
                #     neg_x.insert(-1, x)
                #     neg_y.insert(-1, 0)
        
        # Update figure and plot
        self.fig.update_traces(x=pos_x, y=pos_y, selector=dict(name='Profit >= 0'))
        self.fig.update_traces(x=neg_x, y=neg_y, selector=dict(name='Profit < 0'))

        #self.fig.update_layout(plot_bgcolor=self.random_color())
        #self.add_continuous_shapes()

        self.html = self.generate_html()

    
        return 
    
    def add_continuous_shapes(self):
        '''
        Adds shape lines to represent the continuation of positive and negative profit lines.
        '''
        # Remove existing shapes to avoid duplication
        self.fig.update_layout(shapes=[])
        
        # Positive Profit Line: Determine the slope based on current data
        if len(self.positive_trace.x) >= 2:
            x_start, y_start = self.positive_trace.x[0], self.positive_trace.y[0]
            x_end, y_end = self.positive_trace.x[-1], self.positive_trace.y[-1]
            slope_pos = (y_end - y_start) / (x_end - x_start) if (x_end - x_start) != 0 else 0
            intercept_pos = y_end - slope_pos * x_end
            
            # Define the line extending beyond the current x range
            shape_pos = dict(
                type='line',
                x0=self.xdata.min(),
                y0=slope_pos * self.xdata.min() + intercept_pos,
                x1=self.xdata.max(),
                y1=slope_pos * self.xdata.max() + intercept_pos,
                line=dict(color='green', dash='dash'),
            )
            self.fig.add_shape(shape_pos)
        
        # Negative Profit Line: Determine the slope based on current data
        if len(self.negative_trace.x) >= 2:
            x_start, y_start = self.negative_trace.x[0], self.negative_trace.y[0]
            x_end, y_end = self.negative_trace.x[-1], self.negative_trace.y[-1]
            slope_neg = (y_end - y_start) / (x_end - x_start) if (x_end - x_start) != 0 else 0
            intercept_neg = y_end - slope_neg * x_end
            
            # Define the line extending beyond the current x range
            shape_neg = dict(
                type='line',
                x0=self.xdata.min(),
                y0=slope_neg * self.xdata.min() + intercept_neg,
                x1=self.xdata.max(),
                y1=slope_neg * self.xdata.max() + intercept_neg,
                line=dict(color='red', dash='dash'),
            )
            self.fig.add_shape(shape_neg)
    
    def random_color(self):
        """
        Generates a random color in hexadecimal format.
        """
        return f'#{random.randint(0, 0xFFFFFF):06x}'
    
    def reset_data(self) -> None:
        '''
        Reset the x and y data arrays to empty.
        '''
        del self.xdata
        del self.ydata

        self.positive_trace.x = []
        self.positive_trace.y = []

        self.negative_trace.x = []
        self.negative_trace.y = []
        
        return




if __name__ == '__main__':
    S_current = 418
    S = get_stock_prices(S_current)
    P1 = long_call(S, 400, 130)
    fig = plot_payoff(S, P1)
    plt.savefig('long_call.png')