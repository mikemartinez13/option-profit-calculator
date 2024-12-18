import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from typing import Optional

import pyqtgraph as pg
from PyQt5 import QtWidgets as qtw

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
    P = np.maximum(S-K, 0) - (Price)
    return P*100

def short_call(S, K, Price):
    return -1.0 * long_call(S, K, Price)

def long_put(S, K, Price):
    P = np.maximum(K-S, 0) - (Price)
    return P*100

def short_put(S, K, Price):
     return -1.0 * long_put(S, K, Price)

def get_stock_prices(s0,K):
    '''
    s0: current stock price
    '''
    lower = min(s0 * 0.05, K * 0.05)
    upper = max(s0 * 6, K * 6)

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


class OptionPayoffPlot(qtw.QWidget):
    '''
    Class to plot payoff of options strategies.
    Designed to be used with PyQt5 and set to a main layout on a larger window. 
    Takes no parameters. 

    ### Methods:
    - add_vline: Add a vertical line to the plot
    - remove_vlines: Remove all vertical lines from the plot
    - add_option: Add an option to the plot
    - reset_data: Reset the plot to empty
    - update_traces: Update the plot with the current data. Designed to be called after add_option.

    ### Attributes:
    - xdata: array of x-axis (stock price) data
    - ydata: array of y-axis (option value) data
    - plot_widget: PyQtGraph PlotWidget object
    - positive_curve: PyQtGraph curve for positive profits
    - negative_curve: PyQtGraph curve for negative profits
    - lines: list of vertical lines on the plot


    '''

    def __init__(self):
        super().__init__()

        self.xdata = np.array([])
        self.ydata = np.array([])

        # Create a vertical layout
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)
        
        # Create a PyQtGraph PlotWidget
        self.plot_widget = pg.PlotWidget()
        layout.addWidget(self.plot_widget)
        
        # Create two separate curves for positive and negative profits
        self.positive_curve = self.plot_widget.plot(pen=pg.mkPen(color='g', width=2), name='Profit >= 0')
        self.negative_curve = self.plot_widget.plot(pen=pg.mkPen(color='r', width=2), name='Profit < 0')

        self.__customize_plot(self.plot_widget)
        
        self.lines = []
        
        # Set initial ranges
        # self.plot_widget.setXRange(0, 1000)
        # self.plot_widget.setYRange(-1000, 1000)

        self.view_box = self.plot_widget.getPlotItem().getViewBox()
        self.x_min, self.x_max, self.y_min, self.y_max = self.__set_plot_range(self.view_box)

        return

    def __customize_plot(self, plot_widget: pg.PlotWidget) -> None:
        """
        Returns None. 
        Customizes the appearance of the PlotWidget.
        - plot_widget: the PlotWidget object to customize
        """
        # Set the background color
        plot_widget.setBackground('k')
        
        # Show grid lines
        plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Set axis labels and title
        plot_widget.setLabel('left', 'Profit ($)', color='w', size=14)
        plot_widget.setLabel('bottom', 'Stock Price at Expiration ($)', color='w', size=14)
        plot_widget.setTitle('Strategy Payoff Diagram', color='w', size='14pt')
        
        # Customize the appearance of the axes
        plot_widget.getPlotItem().getAxis('left').setTextPen(pg.mkPen(color='w'))
        plot_widget.getPlotItem().getAxis('bottom').setTextPen(pg.mkPen(color='w'))
        plot_widget.getPlotItem().getAxis('left').setTickPen(pg.mkPen(color='w'))
        plot_widget.getPlotItem().getAxis('bottom').setTickPen(pg.mkPen(color='w'))

        # Add a legend
        self.plot_widget.addLegend()
    
    def __set_plot_range(self, view_box: pg.ViewBox, stock_price=None) -> tuple[float, float, float, float]:
        """
        Sets the minimum and maximum limits for zooming on both X and Y axes and returns the limits for X and Y axes.
        If stock_price is not provided, default limits of 0 < x < 1000 and -50000 < y < 50000 are used. 
        Modifies the ViewBox object to enforce these limits.
        - view_box: the ViewBox object to modify
        - stock_price: the current stock price (default None)
        """
        # Adjusting min and maxes based on s0
        view_box.setAspectLocked(True, ratio = 100)

        x_min = 0
        if not stock_price:
            x_max = 1000
            y_min = -500*100
            y_max = 500*100
        else:
            x_max = stock_price * 6
            y_min = -stock_price * 3 * 100
            y_max = stock_price * 3 * 100

        # Set the limits on the ViewBox
        view_box.setLimits(xMin=x_min, xMax=x_max, yMin=y_min, yMax=y_max)
        
        # Set the initial view range
        if not stock_price:
            self.plot_widget.setXRange(0, 1000)
        else:
            self.plot_widget.setXRange(stock_price*(1-0.2), stock_price*(1+0.2))
        #view_box.setRange(xRange=(self.s0*(1-0.2), self.s0*(1+0.2)), yRange=(-self.y_min, self.y_max))
        
        # Disable automatic range adjustment
        view_box.setAutoVisible(x=False, y=False)
        
        # Connect signals to enforce limits during interactions
        view_box.sigRangeChanged.connect(self.__on_range_changed)

        return x_min, x_max, y_min, y_max

    def __on_range_changed(self):
        """
        Slot to handle range changes and enforce zoom limits. Returns None.
        """
        # Get the current range
        view_range = self.view_box.viewRange()
        x_range, y_range = view_range
        
        # Initialize flags to check if limits are exceeded
        needs_update = False
        new_x_range = list(x_range)
        new_y_range = list(y_range)
        
        # Check and adjust X-axis
        if new_x_range[0] < self.x_min:
            new_x_range[0] = self.x_min
            needs_update = True
        if new_x_range[1] > self.x_max:
            new_x_range[1] = self.x_max
            needs_update = True
        
        # Check and adjust Y-axis
        if new_y_range[0] < self.y_min:
            new_y_range[0] = self.y_min
            needs_update = True
        if new_y_range[1] > self.y_max:
            new_y_range[1] = self.y_max
            needs_update = True
        
        # If limits are exceeded, update the view range
        if needs_update:
            self.view_box.blockSignals(True)  # Prevent recursive calls
            self.view_box.setXRange(new_x_range[0], new_x_range[1], padding=0)
            self.view_box.setYRange(new_y_range[0], new_y_range[1], padding=0)
            self.view_box.blockSignals(False)

    def add_vline(self, x:float, name:str) -> None:
        '''
        Adds vertical lines to plot at x. Gives a name to the line.
        - x: x-coordinate of the vertical line
        - name: name of the vertical line to appear in the legend
        '''
        line = self.plot_widget.plot([x, x], [self.y_min, self.y_max], 
                                     pen=pg.mkPen(color='w', width=2), 
                                     name=name)
        
        self.lines.append(line) # to avoid garbage collection
        
        return
    
    def remove_vlines(self) -> None:
        for line in self.lines:
            self.plot_widget.removeItem(line)
        self.lines.clear()
        
        return

    def add_option(self, option: dict, opt_type:str, buy: bool, s0: float) -> None:
        '''
        Adds an option's payoff to the plot
        '''

        self.xdata = get_stock_prices(s0, option['Strike'])
        self.s0 = s0

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
        self.__set_plot_range(self.view_box, s0)
        
        return 
    
    def update_traces(self):
        '''
        Splits the data into positive and negative segments and updates the Plotly traces.
        '''
        pos_mask = self.ydata >= 0
        neg_mask = self.ydata < 0
        
        pos_x = self.xdata[pos_mask]
        pos_y = self.ydata[pos_mask]
        
        neg_x = self.xdata[neg_mask]
        neg_y = self.ydata[neg_mask]
        
        # Update the curves
        self.positive_curve.setData(pos_x, pos_y)
        self.negative_curve.setData(neg_x, neg_y)

        return 
    
    def reset_data(self) -> None:
        '''
        Reset the x and y data arrays to empty.
        '''
        self.xdata = np.array([])
        self.ydata = np.array([])

        # self.fig.update_traces(x=[], y=[], selector=dict(name='Profit >= 0'))
        # self.fig.update_traces(x=[], y=[], selector=dict(name='Profit < 0'))
        
        # self.html = self.generate_html()

        self.positive_curve.setData([], [])
        self.negative_curve.setData([], [])

        self.__set_plot_range(self.view_box)

        return