import pandas as pd
import numpy as np

from datetime import datetime, timedelta
from typing import Optional
import random

import matplotlib.pyplot as plt

from optlib.gbs import american, black_scholes

import PyQt5.QtWidgets as qtw
import pyqtgraph as pg

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
        self.dates_range = self.generate_dates()

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
        print(self.expirations)
        
        # Create an ImageItem
        self.img_item = pg.ImageItem()
        
        self.add_plot() # adds plot to 
        #self.plot.addItem(self.img_item)

        # Set image data
        self.img_item.setImage(self.data)

        # Customize the colormap
        cmap = pg.colormap.get('viridis')  # Choose a colormap
        self.img_item.setLookupTable(cmap.getLookupTable(0.0, 1.0, 256), update=True)
        self.img_item.setLevels([np.min(self.data), np.max(self.data)])

        self.add_color_bar(cmap)

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
        print(dates_range)
        return dates_range
    
    def generate_data(self):
        '''
        Generates data for heatmap using attributes of the class.
        '''

        values = np.zeros((len(self.dates_range), len(self.prices)))

        print(self.div_yields)
        for option, div_yield, position in zip(self.options, self.div_yields, self.positions):
            opt_type = option['Description'][-1].lower()
            k = option['Strike']
            iv = option['Volatility']/100 if option['Volatility'] < 200 else 2

            for j, price in enumerate(self.prices):
                for i, date in enumerate(self.dates_range):
                    dte = (len(self.dates_range)-(i+1))/365
                    if dte > 0:
                        print(opt_type, price, k, dte, self.r_f, div_yield, iv, self.r_f - div_yield)
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
        date_positions = np.arange(len(self.dates_range))  # get indeces of dates, e.g. [0, 1, 2, 3, 4]
        print(date_positions)
        ticks = [ (pos+0.5, date) for pos, date in zip(date_positions, self.dates_range) ]
        print(ticks)

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
    

