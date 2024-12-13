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

        self.xdata = np.array([])
        self.ydata = np.array([])

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

        if self.ydata.size > 0:
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
            else:
                neg_x.append(x)
                neg_y.append(y)
        
        # Update figure and plot
        self.fig.update_traces(x=pos_x, y=pos_y, selector=dict(name='Profit >= 0'))
        self.fig.update_traces(x=neg_x, y=neg_y, selector=dict(name='Profit < 0'))

        self.html = self.generate_html()

        return 
    
    def reset_data(self) -> None:
        '''
        Reset the x and y data arrays to empty.
        '''
        self.xdata = np.array([])
        self.ydata = np.array([])

        self.fig.update_traces(x=[], y=[], selector=dict(name='Profit >= 0'))
        self.fig.update_traces(x=[], y=[], selector=dict(name='Profit < 0'))
        
        self.html = self.generate_html()

        return


if __name__ == '__main__':
    S_current = 418
    S = get_stock_prices(S_current)
    P1 = long_call(S, 400, 130)
    fig = plot_payoff(S, P1)
    plt.savefig('long_call.png')