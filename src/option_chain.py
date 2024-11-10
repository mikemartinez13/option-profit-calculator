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
    QMessageBox
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
import pandas as pd

from custom_components import PandasModel

class OptionChainWindow(qtw.QWidget):
    '''
    A window that contains multiple tabs, each representing an expiration date.
    Each tab contains a table displaying the options chain for that expiration date.
    '''
    def __init__(self, options_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options Chains by Expiration Date")
        self.setGeometry(200, 200, 1000, 600)

        main_layout = qtw.QVBoxLayout()
        self.setLayout(main_layout)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        for expiration_date, df in options_data.items():
            self.add_expiration_tab(expiration_date, df)

    def add_expiration_tab(self, expiration_date: str, df: pd.DataFrame):
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
        model = PandasModel(df)
        table_view.setModel(model)

        # Stretch columns to fit content
        table_view.horizontalHeader().setStretchLastSection(True)
        table_view.horizontalHeader().setSectionResizeMode(qtw.QHeaderView.Stretch)

        # Add the table to the tab layout
        tab_layout.addWidget(table_view)

        # Add the tab to the QTabWidget
        self.tabs.addTab(tab, expiration_date)