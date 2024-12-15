import sys
from PyQt5 import QtWidgets as qtw, QtCore, QtGui
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QTableView,
    QPushButton,
    QHBoxLayout,
    QMessageBox,
    QLineEdit,
    QLabel
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import pandas as pd
from src.custom_components import configure_button
from utils.data_utils import SchwabData, DummyData
from vis.payoff import OptionPayoffPlot
from vis.heatmap import Heatmap
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

import os
import traceback

from datetime import datetime

import json

from src.custom_components import PandasModel

class OptionChainWindow(qtw.QWidget):
    '''
    A window that contains multiple tabs, each representing an expiration date.
    Each tab contains a table displaying the options chain for that expiration date.
    '''
    def __init__(self, demo = False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options Chains by Expiration Date")
        self.setGeometry(200, 200, 1600, 600)

        if demo:
            self.engine = DummyData()
        else:
            self.engine = SchwabData()
            
        self.display = OptionPayoffPlot()
        self.heatmap = None

        self.ticker = None

        # display values
        self.total_cost = 0

        # Toggle state
        self.show_calls = True

        self.table_views = []

        main_layout = qtw.QHBoxLayout()
        self.setLayout(main_layout)

        self.configure_left_layout(main_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, stretch = 3)

        self.configure_figure(main_layout)

        self.show_no_data_message()


        # initialize data

        self.options = []
        self.expirations = []
        self.div_yields = []
        self.positions = []

        return

    def configure_left_layout(self, layout: QVBoxLayout):
        left_layout = qtw.QVBoxLayout()

        # Add a toggle button to view either calls or puts
        self.toggle_button = QPushButton()

        configure_button(self.toggle_button, 
                         text="Toggle Calls/Puts",
                         command=self.toggle_calls_puts
                         )
        
        left_layout.addWidget(self.toggle_button)

        # Add a ticker input field
        ticker_layout = QHBoxLayout()
        ticker_label = qtw.QLabel("Ticker:")
        self.ticker_input = QLineEdit()
        self.enter_ticker = QPushButton()

        configure_button(self.enter_ticker, 
                         text="Enter",
                         command=self.get_ticker_data
                         )
        
        ticker_layout.addWidget(ticker_label)
        ticker_layout.addWidget(self.ticker_input)

        # Add to the left layout
        left_layout.addLayout(ticker_layout)
        left_layout.addWidget(self.enter_ticker)

        layout.addLayout(left_layout, stretch = 0)

    def configure_figure(self, layout: QVBoxLayout):

        right_layout = qtw.QVBoxLayout()

        self.canvas = QWebEngineView()
        self.canvas.setHtml(self.display.html)
        # self.update_plot()
        #self.canvas.loadFinished.connect(self.on_load_finished)

        self.option_description = QLabel("No option selected.")

        self.long_button = QPushButton()
        self.short_button = QPushButton()
        self.reset_button = QPushButton()
        self.heatmap = QPushButton()

        configure_button(self.long_button,
                            text="Add Long to Plot (Buy)",
                            command=self.add_long
                        )
        configure_button(self.short_button,
                            text="Add Short to Plot (Sell)",
                            command=self.add_short
                        )
        configure_button(self.reset_button,
                            text="Reset Plot",
                            command=self.reset_plot
                        )
        configure_button(self.heatmap, 
                            text="Show Future Payoff",
                            command=self.show_heatmap
                        )
        
        right_layout.addWidget(self.canvas)
        right_layout.addWidget(self.option_description)
        right_layout.addWidget(self.long_button)
        right_layout.addWidget(self.short_button)
        right_layout.addWidget(self.reset_button)
        right_layout.addWidget(self.heatmap)

        self.long_button.setEnabled(False)
        self.short_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.heatmap.setEnabled(False)
        
        layout.addLayout(right_layout, stretch = 2)

    def show_no_data_message(self):
        '''
        Displays a message indicating that no data is loaded.
        '''
        # Create a new QWidget for the tab
        tab = QWidget()
        tab_layout = QVBoxLayout()
        tab.setLayout(tab_layout)

        # Add a label with the message
        message_label = QLabel("Data not loaded.")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 16px; color: #777777;")
        tab_layout.addWidget(message_label)

        # Add the tab to the QTabWidget
        self.tabs.addTab(tab, "No Data")
    
    def update_plot(self):
        
        self.canvas.setHtml(self.display.html)
        return 


    def add_tab(self, expiration_date: str, calls_df: pd.DataFrame, puts_df: pd.DataFrame):
        '''
        Adds a new tab for a given expiration date with its options chain table.

        Parameters:
            expiration_date (str): The expiration date label for the tab.
            df (pd.DataFrame): The options chain data to display in the table.
            The data inserted into the table is originally in the form of 'exp_date': pd.DataFrame
        '''
        # Create a new QWidget for the tab
        tab = qtw.QWidget()
        tab_layout = qtw.QVBoxLayout()
        tab.setLayout(tab_layout)

        # Create the table view
        table_view = QTableView()
        table_view.setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)  # Make table read-only
        table_view.setSelectionBehavior(qtw.QAbstractItemView.SelectRows)
        table_view.setAlternatingRowColors(True)
        table_view.setSortingEnabled(True)  # Enable sorting

        # Create and set the model
        df = calls_df if self.show_calls else puts_df

        model = PandasModel(df)
        table_view.setModel(model)

        # Stretch columns to fit content
        table_view.horizontalHeader().setStretchLastSection(True)
        table_view.horizontalHeader().setSectionResizeMode(qtw.QHeaderView.Stretch)

        table_view.clicked.connect(self.retrieve_option)

        # Add the table to the tab layout
        tab_layout.addWidget(table_view)

        # Add the tab to the QTabWidget
        tab_index = self.tabs.addTab(tab, expiration_date)
        self.tabs.tabBar().setTabData(tab_index, expiration_date) # allows us to retrieve data for a certain tab

        self.table_views.append({
            'table_view': table_view,
            'calls_df': calls_df,
            'puts_df': puts_df,
            'current_model': model
        })

    def retrieve_option(self, index: QModelIndex):
        '''
        Slot to handle click events on the table view.
        '''
        if not index.isValid():
            return
        
        # Get the current widget (tab)
        current_tab = self.tabs.currentIndex()
        expiration_date = self.tabs.tabBar().tabData(current_tab)

        if self.show_calls:
            df = self.calls_data[expiration_date]
        else:
            df = self.puts_data[expiration_date]

        if df is None:
            QMessageBox.warning(
                self,
                "No Data",
                f"No data found for expiration date: {expiration_date}",
                QMessageBox.Ok
            )
            return

        row = index.row()

        self.current_option = df.iloc[row].to_dict() # make attribute so other functions can access

        # Enable buttons 
        self.long_button.setEnabled(True)
        self.short_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        self.heatmap.setEnabled(True)

        # Update option description
        self.type = "call" if self.show_calls else "put"

        self.option_description.setText("{1} {0} at $K={2}$, bid of {3}, ask of {4}, expiring {5}."\
                                        .format(self.type, self.ticker, self.current_option['Strike'], self.current_option['Bid'], self.current_option['Ask'], expiration_date))

        return

    def toggle_calls_puts(self):
        '''
        Toggles the displayed options between calls and puts.
        '''
        self.show_calls = not self.show_calls

        if self.show_calls:
            self.toggle_button.setText("View Puts")
        else:
            self.toggle_button.setText("View Calls")
        
        print("Show calls is",self.show_calls)
        
        for tab_info in self.table_views:
            table_view = tab_info['table_view']
            calls_df = tab_info['calls_df']
            puts_df = tab_info['puts_df']

            # Determine which DataFrame to display
            new_df = calls_df if self.show_calls else puts_df

            # Create a new model and set it to the table view
            new_model = PandasModel(new_df)
            table_view.setModel(new_model)

            # Update the current model reference
            tab_info['current_model'] = new_model
        
        return

    def get_ticker_data(self):

        if self.ticker and self.ticker_input.text().upper() != self.ticker: # if we have a different ticker than already exists
            QMessageBox.warning(
                self,
                "If you change the ticker, you're strategy plot will be reset! Proceed?",   
                QMessageBox.Ok | QMessageBox.Cancel
            )
            if QMessageBox.Cancel:
                return
            else:
                self.reset_plot()
        self.ticker = self.ticker_input.text().upper()
        
        try:
            data, r_f = self.engine.get_options_chain_dict(self.ticker)
        except ValueError as e:
            # QMessageBox.warning(
            #     self,
            #     "Invalid Ticker",
            #     str(e),
            #     QMessageBox.Ok
            # )
            print(traceback.format_exc())
            return 

        self.calls_data = data['calls'] # data initialized
        self.puts_data = data['puts']
        self.interest_rate = r_f/100

        # Clear existing tabs
        self.tabs.clear()
        self.table_views.clear()

        # Add tabs for calls and puts based on ticker
        expiration_dates = self.calls_data.keys()

        for expdate in expiration_dates:
            self.add_tab(expdate, self.calls_data[expdate], self.puts_data[expdate])

        self.ticker_input.clear()

        return

    def add_long(self):
        '''
        Adds a long option to the plot.
        '''
        self.display.add_option(option=self.current_option, 
                                opt_type=self.type, 
                                buy=True, 
                                s0=self.engine.get_price(ticker=self.ticker)
                                )
        self.options.append(self.current_option)
        self.expirations.append(self.current_option['Days to Expiration'])
        self.div_yields.append(self.engine.get_div_yield(self.ticker))
        self.positions.append("long")
        self.total_cost += self.current_option['Ask']*100

        self.update_plot()
        return

    def add_short(self):
        '''
        Adds a short option to the plot.
        '''
        self.display.add_option(option=self.current_option, 
                                opt_type=self.type, 
                                buy=False, 
                                s0=self.engine.get_price(ticker=self.ticker)
                                ) # updates traces and generates new html
        self.options.append(self.current_option)
        self.expirations.append(self.current_option['Days to Expiration'])
        self.div_yields.append(self.engine.get_div_yield(self.ticker))
        self.positions.append("short")
        self.total_cost -= self.current_option['Ask']*100

        self.update_plot() # assigns new html to webengineview
        return
    
    def reset_plot(self):
        '''
        Resets the plot.
        '''
        self.display.reset_data()
        self.option_description.setText("No option selected.")
        
        self.update_plot()

    def show_heatmap(self):
        '''
        Shows the future payoff heatmap.
        '''
        if not hasattr(self, 'interest_rate'):
            QMessageBox.warning(
                self,
                "No Data",
                "Please load data before showing the heatmap.",
                QMessageBox.Ok
            )
            return

        self.heatmap = Heatmap(self.options, 
                        self.expirations,
                        self.interest_rate,
                        self.div_yields, 
                        self.positions,
                        self.engine.get_price(self.ticker),
                        self.total_cost
                        )
        self.heatmap.show()


