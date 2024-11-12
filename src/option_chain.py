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
import pandas as pd
from src.custom_components import configure_button
from utils.data_utils import SchwabData

from src.custom_components import PandasModel

class OptionChainWindow(qtw.QWidget):
    '''
    A window that contains multiple tabs, each representing an expiration date.
    Each tab contains a table displaying the options chain for that expiration date.
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options Chains by Expiration Date")
        self.setGeometry(200, 200, 1000, 600)

        self.engine = SchwabData()

        # Toggle state
        self.show_calls = True

        self.table_views = []

        main_layout = qtw.QVBoxLayout()
        self.setLayout(main_layout)

        left_layout = qtw.QVBoxLayout()

        # Add a toggle button to view either calls or puts
        self.toggle_button = QPushButton()

        configure_button(self.toggle_button, 
                         text="Toggle Calls/Puts",
                         command=self.toggle_calls_puts
                         )
        
        left_layout.addWidget(self.toggle_button)

        main_layout.addLayout(left_layout, stretch = 1)

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

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.show_no_data_message()

        # expiration_dates = self.calls_data.keys()

        # for expdate in expiration_dates:
        #     self.add_tab(expdate, self.calls_data[expdate], self.puts_data[expdate])

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

        table_view.doubleClicked.connect(self.retrieve_option)

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
        Slot to handle double-click events on the table view.
        '''
        if not index.isValid():
            return
        
        # Get the current widget (tab)
        current_tab = self.tabs.currentIndex()
        expiration_date = self.tabs.tabBar().tabData(current_tab)
        # if not isinstance(current_tab, OptionTab):
        #     QMessageBox.warning(
        #         self,
        #         "Unknown Tab",
        #         "Active tab does not contain option data.",
        #         QMessageBox.Ok
        #     )
        #     return

        df = self.option_data.get(expiration_date, None)

        if df is None:
            QMessageBox.warning(
                self,
                "No Data",
                f"No data found for expiration date: {expiration_date}",
                QMessageBox.Ok
            )
            return

        row = index.row()

        option_data = df.iloc[row].to_dict()

        print(option_data)

    def toggle_calls_puts(self):
        '''
        Toggles the displayed options between calls and puts.
        '''
        self.show_calls = not self.show_calls

        if self.show_calls:
            self.toggle_button.setText("View Puts")
        else:
            self.toggle_button.setText("View Calls")
        
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

    def get_ticker_data(self):
        ticker = self.ticker_input.text().upper()
        
        try:
            data = self.engine.get_options_chain_dict(ticker)
        except ValueError as e:
            QMessageBox.warning(
                self,
                "Invalid Ticker",
                str(e),
                QMessageBox.Ok
            )
            return

        self.calls_data = data['calls'] # data initialized
        self.puts_data = data['puts']

        # Clear existing tabs
        self.tabs.clear()
        self.table_views.clear()

        # Add tabs for calls and puts based on ticker
        expiration_dates = self.calls_data.keys()

        for expdate in expiration_dates:
            self.add_tab(expdate, self.calls_data[expdate], self.puts_data[expdate])

        self.ticker_input.clear()
