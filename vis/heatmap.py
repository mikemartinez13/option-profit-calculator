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
    def __init__(self, options, expirations, interest_rate, div_yields, positions, stock_price, cost):
        super().__init__()

        # Necessary financial data
        self.options = options
        self.expirations = expirations
        self.r_f = interest_rate 
        self.div_yields = div_yields
        self.positions = positions
        self.s0 = stock_price
        self.cost = cost

        print(len(self.options))
        print(self.div_yields)
        print(self.positions)

        self.num_prices = 20
        # controls how many stock prices are displayed on the heatmap

        self.prices, self.price_indices = self.get_price_range(self.num_prices)
        self.date_range, self.date_indices = self.generate_dates()

        # Figure configurations
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Future Value Heatmap")

        self.x_min, self.x_max = min(self.date_indices), max(self.date_indices) + 1
        self.y_min, self.y_max = min(self.price_indices)-0.5, max(self.price_indices)+0.5

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
        
        self.plot = self.configure_plot() # adds plot to 
        #self.plot.addItem(self.img_item)

        # Set image data
        self.img_item.setImage(self.data)

        # Customize the colormap
        cmap = self.get_colormap()  # Choose a colormap
        self.img_item.setLookupTable(cmap.getLookupTable(0.0, 1.0, self.data.size), update=True)
        self.img_item.setLevels([np.min(self.data), np.max(self.data)])

        self.img_item.setPos(self.x_min, self.y_min)

        self.view_box = self.plot.getViewBox()

        self.set_zoom_limits()

        # Add annotations to the heatmap
        self.add_annotations()
        return

    def get_price_range(self, num_steps):
        self.lower = self.s0 * (1 - 0.1)
        self.upper = self.s0 * (1 + 0.1)

        price_range = np.round(np.linspace(self.lower, self.upper, num=num_steps), 2)
        price_positions = np.arange(len(price_range)) # get indices of prices

        return price_range, price_positions
    
    def generate_dates(self):
        date_range = []
        exp = max(self.expirations)

        for i in range(0, exp+1):
            date_range.append((datetime.today() + timedelta(days=i)).strftime('%Y-%m-%d'))

        date_indices = np.arange(len(date_range)) # get indices of dates, e.g. [0, 1, 2, 3, 4]

        return date_range, date_indices
    
    def generate_data(self):
        '''
        Generates data for heatmap using attributes of the class.
        '''

        values = np.zeros((len(self.date_range), len(self.prices)))
        exp = datetime.strptime(max(self.date_range), '%Y-%m-%d').replace(hour=16, minute=0, second=0) # set time to 4pm for market close

        for option, div_yield, position in zip(self.options, self.div_yields, self.positions):
            opt_type = option['Description'][-1].lower()
            print(opt_type)
            k = option['Strike']
            iv = option['Volatility']/100 if option['Volatility'] < 200 else 2

            print('dates:',self.date_range)
            for i, date in enumerate(self.date_range):
                dt = datetime.strptime(date, '%Y-%m-%d').replace(hour=12, minute=0, second=0) # set time to 4pm for market close
                dte = (exp - dt).total_seconds()/(365*86400)
                print("today",datetime.today(), "dte:",dte*365)
                for j, price in enumerate(self.prices):
                    if dte > 0.001:
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
    
    def configure_plot(self):
        
        xticks = [ (pos+0.5, date) for pos, date in zip(self.date_indices, self.date_range) ]
        yticks = [ (pos, str(price)) for pos, price in enumerate(self.prices) ]

        # Create a custom AxisItem
        xaxis = pg.AxisItem('bottom')
        xaxis.setTicks([xticks])

        yaxis = pg.AxisItem('left')
        yaxis.setTicks([yticks])

        #axis.setLabel(rotation=45)

        plot = self.graph_widget.addPlot(axisItems={'bottom': xaxis, 'left': yaxis})
    
        # Re-add the ImageItem to the new plot
        plot.addItem(self.img_item)

        plot.setLabel('left', 'Stock Price ($)')
        plot.setLabel('bottom', 'Date')
        plot.setTitle("Option Strategy Value Over Time")

        return plot
    

    def add_annotations(self):
        """
        Adds text annotations to each cell of the heatmap.
        """
        for i in self.date_indices:
            for j in self.price_indices:
                # Calculate the center position of each cell
                # x = self.x_min + (j + 0.5) * (self.x_max - self.x_min) / len(self.prices)
                # y = self.y_min + (i + 0.5) * (self.y_max - self.y_min) / len(self.date_range)
                
                # Retrieve the value to annotate
                value = self.data[i, j]
                formatted_value = f"{value:.2f}"
                
                # Create a TextItem
                text = pg.TextItem(text=formatted_value, anchor=(0.5, 0.5), color='black', border=None)
                
                # Set position and add
                text.setPos(i+0.5, j)
                self.plot.addItem(text)

    
    def get_colormap(self):
        """
        Returns a colormap for the heatmap.
        """
        positions = [0.0, 0.5, 1.0]  # Red at 0.0, White at 0.5, Green at 1.0
        colors = [
            (255, 0, 0),     # Red
            (255, 255, 255), # White
            (0, 255, 0)      # Green
        ]
        
        # Create the custom colormap
        cmap = pg.ColorMap(pos=positions, color=colors)
        return cmap

    
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
    

