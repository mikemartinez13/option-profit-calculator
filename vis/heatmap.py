import pandas as pd
import numpy as np

from datetime import datetime, timedelta
from typing import Optional
import random

import matplotlib.pyplot as plt

from optlib.gbs import american, black_scholes

import PyQt5.QtWidgets as qtw
import pyqtgraph as pg


class Heatmap(qtw.QWidget):
    def __init__(self, options, expirations, interest_rate, div_yields, positions, stock_price):
        super().__init__()

        # Necessary financial data
        self.options = options
        self.expirations = expirations
        self.r_f = interest_rate 
        self.div_yields = div_yields
        self.positions = positions
        self.s0 = stock_price

        self.prices = self.get_price_range()
        self.dates_range, self.dates_positions = self.generate_dates()

        # Figure configurations
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Future Value Heatmap")

        main_layout = qtw.QHBoxLayout()
        self.setLayout(main_layout)
        
        # Create a GraphicsLayoutWidget
        self.graph_widget = pg.GraphicsLayoutWidget()
        main_layout.addWidget(self.graph_widget)
        
        # Add a plot to the GraphicsLayoutWidget
        
        # Generate sample data for the heatmap
        self.data = self.generate_data()
        
        # Create an ImageItem
        self.img_item = pg.ImageItem()
        
        self.add_plot() # adds plot to 
        #self.plot.addItem(self.img_item)

        self.view_box = self.plot.getViewBox()

        # Set image data
        self.img_item.setImage(self.data)

        # Customize the colormap
        cmap = pg.colormap.get('viridis')  # Choose a colormap
        self.img_item.setLookupTable(cmap.getLookupTable(0.0, 1.0, 256), update=True)
        self.img_item.setLevels([np.min(self.data), np.max(self.data)])

        self.add_color_bar(cmap)

        self.set_zoom_limits()

        return

    def get_price_range(self):
        self.lower = self.s0 * (1 - 0.3)
        self.upper = self.s0 * (1 + 0.3)

        return np.linspace(self.lower, self.upper, num=500).round()
    
    def generate_dates(self):
        dates_range = []
        exp = max(self.expirations)

        for i in range(0, exp+1):
            dates_range.append((datetime.today() + timedelta(days=i)).strftime('%Y-%m-%d'))

        date_positions = np.arange(len(dates_range)) # get indices of dates, e.g. [0, 1, 2, 3, 4]
        return dates_range, date_positions
    
    def generate_data(self):
        '''
        Generates data for heatmap using attributes of the class.
        '''

        values = np.zeros((len(self.dates_range), len(self.prices)))

        for option, div_yield, position in zip(self.options, self.div_yields, self.positions):
            opt_type = option['Description'][-1].lower()
            k = option['Strike']
            iv = option['Volatility']/100 if option['Volatility'] < 200 else 2

            for j, price in enumerate(self.prices):
                for i, date in enumerate(self.dates_range):
                    dte = (len(self.dates_range)-(i+1))/365
                    if dte > 0:
                        val = american(opt_type,
                                         price, 
                                         k, 
                                         dte,
                                         self.r_f,
                                         div_yield, 
                                         iv)[0] # use option pricing library to get American option value
                    else: # if T = 0 or if time has expired, we just take intrinsic value
                        if opt_type == 'c':
                            val = max(price - k, 0)
                        else:
                            val = max(k - price, 0)
                    
                    if position == 'long':
                        values[i, j] += (val * 100)  # 100 shares per contract
                    elif position == 'short':
                        values[i, j] -= (val * 100)

        return values
    
    def add_plot(self):
        
        ticks = [ (pos+0.5, date) for pos, date in zip(self.dates_positions, self.dates_range) ]

        # Create a custom AxisItem
        axis = pg.AxisItem('bottom')
        axis.setTicks([ticks])

        self.plot = self.graph_widget.addPlot(axisItems={'bottom': axis})
    
        # Re-add the ImageItem to the new plot
        self.plot.addItem(self.img_item)

        self.plot.setLabel('left', 'Time to Evaluation (Days)')
        self.plot.setLabel('bottom', 'Date')
        self.plot.setTitle("Option Strategy Future Value Heatmap")

    
    def add_color_bar(self, cmap):
        # Create a color bar
        color_bar = pg.GradientEditorItem()
        color_bar.restoreState({'mode': 'rgb', 'ticks': [(0.0, (0, 0, 255, 255)),
                                                         (0.5, (0, 255, 0, 255)),
                                                         (1.0, (255, 0, 0, 255))]})
        self.graph_widget.nextRow()
        self.graph_widget.addItem(color_bar)
    
        
    def set_zoom_limits(self):
        """
        Sets the minimum and maximum limits for zooming on both X and Y axes.
        Users won't be able to zoom out beyond these limits.
        """
        # Define the desired ranges
        # For example, limit X and Y axes between -10 and 10
        self.x_min, self.x_max = min(self.dates_positions), max(self.dates_positions) + 1
        self.y_min, self.y_max = self.lower, self.upper
        
        # Set the limits on the ViewBox
        self.view_box.setLimits(xMin=self.x_min, xMax=self.x_max, yMin=self.y_min, yMax=self.y_max)
        
        # Optionally, set the initial view range
        self.view_box.setRange(xRange=(self.x_min, self.x_max), yRange=(self.y_min, self.y_max))
        
        # Disable automatic range adjustment
        self.view_box.setAutoVisible(x=False, y=False)
        
        # Connect signals to enforce limits during interactions
        self.view_box.sigRangeChanged.connect(self.on_range_changed)

    def on_range_changed(self):
        """
        Slot to handle range changes and enforce zoom limits.
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
    

