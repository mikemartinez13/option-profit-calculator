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
        self.num_prices = 20

        self.value_toggle = True
        # controls how many stock prices are displayed on the heatmap

        # Default price range
        self.prices, self.price_indices = self.get_price_range(self.s0 * (1 - 0.1), 
                                                            self.s0 * (1 + 0.1), 
                                                            self.num_prices)
        self.date_range, self.date_indices = self.generate_dates()

        self.x_min, self.x_max = min(self.date_indices), max(self.date_indices) + 1
        self.y_min, self.y_max = min(self.price_indices)-0.5, max(self.price_indices)+0.5

        # Figure configurations
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle("Future Value Heatmap")

        main_layout = qtw.QHBoxLayout()
        self.setLayout(main_layout)

        self.__configure_plot(main_layout)
        right_layout = self.__configure_buttons(main_layout)
        self.__configure_controls(right_layout)
        
        return


    ##############################
    ##### Plotting Functions #####
    ##############################

    
    def __configure_plot(self, layout: qtw.QHBoxLayout):
        '''
        Configure the plot layout.
        '''
        # Create a GraphicsLayoutWidget
        self.graph_widget = pg.GraphicsLayoutWidget()
        layout.addWidget(self.graph_widget)
        
        # Add a plot to the GraphicsLayoutWidget
        
        # Generate sample data for the heatmap
        self.value_matrix, self.profit_matrix = self.generate_data()
        
        # Create an ImageItem
        self.img_item = pg.ImageItem()
        
        self.plot = self.__label_plot(self.img_item) # adds labels to plot
        
        # Initialize annotations
        self.annotations = []
        
        # Set the data for the heatmap
        self.__set_plot_data(self.value_matrix) 

        self.set_zoom_limits()

        return

    def __label_plot(self, img: pg.ImageItem) -> pg.PlotItem:
        
        xticks = [ (pos+0.5, date) for pos, date in zip(self.date_indices, self.date_range) ]
        yticks = [ (pos, str(price)) for pos, price in enumerate(self.prices) ]

        # Create a custom AxisItem
        self.xaxis = pg.AxisItem('bottom')
        self.xaxis.setTicks([xticks])

        self.yaxis = pg.AxisItem('left')
        self.yaxis.setTicks([yticks])

        #axis.setLabel(rotation=45)

        plot = self.graph_widget.addPlot(axisItems={'bottom': self.xaxis, 
                                                    'left': self.yaxis})
    
        # Re-add the ImageItem to the new plot
        plot.addItem(img)

        plot.setLabel('left', 'Stock Price ($)')
        plot.setLabel('bottom', 'Date')
        plot.setTitle("Option Strategy Value Over Time")

        return plot

    def __configure_buttons(self, layout: qtw.QHBoxLayout):
        '''
        Configure the buttons layout.
        '''
        button_layout = qtw.QVBoxLayout()
        layout.addLayout(button_layout)

        # Add a button to reset the view
        profit_button = qtw.QPushButton("Toggle between Value/Profit")
        profit_button.clicked.connect(self.profit_value_toggle)
        button_layout.addWidget(profit_button)

        # # Add a button to save the heatmap
        # save_button = qtw.QPushButton("Save Heatmap")
        # save_button.clicked.connect(self.save_heatmap)
        # button_layout.addWidget(save_button)

        return button_layout

    def __configure_controls(self, layout: qtw.QVBoxLayout):
        '''
        Configure controls for setting stock price ranges, .
        '''
        # Add a slider to control the number of stock prices
        # price_slider = qtw.QSlider()
        # price_slider.setOrientation(qtc.Qt.Horizontal)
        # price_slider.setRange(10, 70)
        # price_slider.setValue(self.num_prices)
        # price_slider.valueChanged.connect(self.update_prices)
        # control_layout.addWidget(price_slider)

        range_label_y = qtw.QLabel("Set Stock Price Range:")
        layout.addWidget(range_label_y)

        # Stock prices min
        y_min_label = qtw.QLabel("Min:")
        self.y_min_input = qtw.QDoubleSpinBox()
        self.y_min_input.setDecimals(2)
        self.y_min_input.setRange(0.01, np.round(self.s0*4))
        self.y_min_input.setValue(min(self.prices))
        self.y_min_input.setSingleStep(0.5)
        self.y_min_input.setKeyboardTracking(False)  # Disable live tracking
        self.y_min_input.editingFinished.connect(self.update_y_range)

        layout.addWidget(y_min_label)
        layout.addWidget(self.y_min_input)

        # Stock prices max
        y_max_label = qtw.QLabel("Max:")
        self.y_max_input = qtw.QDoubleSpinBox()
        self.y_max_input.setDecimals(2)
        self.y_max_input.setRange(0.01, np.round(self.s0*4))
        self.y_max_input.setValue(max(self.prices))
        self.y_max_input.setSingleStep(0.1)
        self.y_max_input.setKeyboardTracking(False) 
        self.y_max_input.editingFinished.connect(self.update_y_range)

        layout.addWidget(y_max_label)
        layout.addWidget(self.y_max_input)

        return
    
    def __set_plot_data(self, data):
        # Set image data
        self.img_item.setImage(data)

        # Customize the colormap
        cmap = self.get_colormap()  # Choose a colormap
        self.img_item.setLookupTable(cmap.getLookupTable(0.0, 1.0, data.size), update=True)
        self.img_item.setLevels([np.min(data), np.max(data)])
        
        # Remove previous annotations if any
        for text_item in self.annotations: 
            self.plot.removeItem(text_item)
        self.annotations.clear()

        self.img_item.setPos(self.x_min, self.y_min)

        self.view_box = self.plot.getViewBox()

        # Add annotations to the heatmap
        self.add_annotations()

        return

    def __update_plot(self):
        '''
        Update the plot with new data.
        '''
        self.value_matrix, self.profit_matrix = self.generate_data()
        
        # Set the data for the heatmap
        if self.value_toggle:
            self.__set_plot_data(self.value_matrix) 
        else:
            self.__set_plot_data(self.profit_matrix)

        return

    def __update_yticks(self):
        '''
        Update the y-axis (stock prices) ticks.
        '''
        yticks = [ (pos, str(price)) for pos, price in enumerate(self.prices) ]
        self.yaxis.setTicks([yticks])

        return


    ##############################
    ####### Data Functions #######
    ##############################


    def get_price_range(self, lower: float, upper: float, num_steps: int) -> tuple[np.array, np.array]:
        '''
        Get a range of stock prices. Also gets the indices of the prices.
        '''
        price_range = np.round(np.linspace(lower, upper, num=num_steps), 2)
        price_positions = np.arange(len(price_range)) # get indices of prices

        return price_range, price_positions
    
    def generate_dates(self):
        '''
        Get a range of dates, limited to 20 dates equally spaced apart. Also gets the indices of the dates.
        '''
        # date_range = []
        # exp = max(self.expirations)

        # for i in range(0, exp+1):
        #     date_range.append((datetime.today() + timedelta(days=i)).strftime('%Y-%m-%d'))

        # date_indices = np.arange(len(date_range)) # get indices of dates, e.g. [0, 1, 2, 3, 4]

        # return date_range, date_indices

        date_range = []
        exp = max(self.expirations)  

        today = datetime.today().date()

        if exp <= 19:
            # If the range is 20 days or fewer, include every date
            for i in range(0, exp + 1):
                current_date = today + timedelta(days=i)
                date_range.append(current_date.strftime('%Y-%m-%d'))
        else:
            # If the range exceeds 20 days, select 20 equally spaced dates
            num_dates = 20  
            step = exp / (num_dates - 1)  

            indices = [int(round(i * step)) for i in range(num_dates)]
            indices = [min(idx, exp) for idx in indices]
            unique_indices = []
            seen = set()
            for idx in indices:
                if idx not in seen:
                    unique_indices.append(idx)
                    seen.add(idx)

            while len(unique_indices) < num_dates:
                unique_indices.append(exp)

            unique_indices = unique_indices[:num_dates]

            # Generate dates based on the unique indices
            for idx in unique_indices:
                current_date = today + timedelta(days=idx)
                date_range.append(current_date.strftime('%Y-%m-%d'))

        # gen corresponding date indices
        date_indices = np.arange(len(date_range)) 
        
        return date_range, date_indices
    
    def generate_data(self):
        '''
        Generates data for heatmap using attributes of the class.
        '''

        values = np.zeros((len(self.date_range), len(self.prices)))

        exp = datetime.strptime(max(self.date_range), '%Y-%m-%d').replace(hour=16, minute=0, second=0) # set time to 4pm for market close

        for option, div_yield, position in zip(self.options, self.div_yields, self.positions):
            opt_type = option['Description'][-1].lower()

            k = option['Strike']
            iv = option['Volatility']/100 if option['Volatility'] < 200 else 2

            for i, date in enumerate(self.date_range):
                if i == 0:
                    dt = datetime.today()
                else:
                    dt = datetime.strptime(date, '%Y-%m-%d').replace(hour=16, minute=0, second=0) # set time to 4pm for market close
                dte = (exp - dt).total_seconds()/(365*86400)
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

        profit = values - self.cost
        return values, profit

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
                if self.value_toggle:
                    value = self.value_matrix[i, j]
                else:
                    value = self.profit_matrix[i, j]

                formatted_value = f"{value:.2f}"
                
                # Create a TextItem
                text = pg.TextItem(text=formatted_value, anchor=(0.5, 0.5), color='black', border=None)
                
                # Set position and add
                text.setPos(i+0.5, j)
                self.plot.addItem(text)

                self.annotations.append(text) # keep track of annotations

    
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

    
    # def add_color_bar(self, cmap):
    #     # Create a color bar
    #     color_bar = pg.GradientEditorItem()
    #     color_bar.restoreState({'mode': 'rgb', 'ticks': [(0.0, (0, 0, 255, 255)),
    #                                                      (0.5, (0, 255, 0, 255)),
    #                                                      (1.0, (255, 0, 0, 255))]})
    #     self.graph_widget.nextRow()
    #     self.graph_widget.addItem(color_bar)
    
        
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
    

    ##############################
    #### Buttons and Controls ####
    ##############################


    def profit_value_toggle(self):
        '''
        Toggle between profit and value.
        '''
        if self.value_toggle:
            self.value_toggle = False
            self.__set_plot_data(self.profit_matrix)
        else:
            self.value_toggle = True
            self.__set_plot_data(self.value_matrix)

    
    def update_y_range(self):
        """
        Updates the Y-axis range based on user input.
        """
        new_min = self.y_min_input.value()
        new_max = self.y_max_input.value()

        if new_min >= new_max:
            # Optionally, show a warning or reset to previous valid values
            qtw.QMessageBox.warning(self, "Invalid Range", "Y-axis min must be less than max.")
            self.y_min_input.blockSignals(True)
            self.y_max_input.blockSignals(True)
            self.y_min_input.setValue(min(self.prices))
            self.y_max_input.setValue(max(self.prices))
            self.y_min_input.blockSignals(False)
            self.y_max_input.blockSignals(False)
        else:
            self.prices, self.price_indices = self.get_price_range(new_min, 
                                                                new_max, 
                                                                self.num_prices)

            self.__update_plot()
            self.__update_yticks()

        return


