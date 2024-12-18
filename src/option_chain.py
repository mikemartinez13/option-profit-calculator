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
    QGridLayout,
    QLineEdit,
    QLabel
)
from PyQt5.QtCore import QModelIndex
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


from src.custom_components import configure_button
from utils.data_utils import SchwabData, DummyData
from vis.payoff import OptionPayoffPlot
from vis.heatmap import Heatmap

import pandas as pd
import traceback
from src.custom_components import PandasModel

from typing import Optional

class OptionChainWindow(qtw.QWidget):
    '''
    A window that contains multiple tabs, each representing an expiration date.
    Each tab contains a table displaying the options chain for that expiration date.


    ### Attributes:
    - engine: SchwabData: The data engine to retrieve options chain data.
    - display: OptionPayoffPlot: The plot to display the option strategy.
    - heatmap: QPushButton: Button to show the future payoff heatmap.
    - ticker: str: The ticker symbol for the stock.
    - total_cost: float: The total cost of all options in the strategy.
    - show_calls: bool: Toggle state for calls/puts.
    - table_views: list[dict]: List of dictionaries containing table views and data for each expiration date.
    - options: list[dict]: List of dictionaries containing option data.
    - expirations: list[int]: List of days to expiration for each option.
    - div_yields: list[float]: List of dividend yields for each option.
    - positions: list[str]: List of positions for each option.
    - current_option: dict: The current option selected by the user.
    - type: str: The type of option selected (call or put).
    - calls_data: dict: Dictionary containing calls data.
    - puts_data: dict: Dictionary containing puts data.
    - interest_rate: float: The risk-free interest rate.

    ### Methods: 
    - configure_left_layout: Configures the left layout of the window.
    - configure_figure: Configures the right layout of the window.
    - show_no_data_message: Displays a message indicating that no data is loaded.
    - initialize_labels: Initializes QLabel widgets for displaying descriptive statistics.
    - update_stock_labels: Updates the labels with the given stock data.
    - update_option_labels: Updates the labels with new options data.
    - add_tab: Adds a new tab for a given expiration date with its options chain table.
    - retrieve_option: Slot to handle click events on the table view.
    - toggle_calls_puts: Toggles the displayed options between calls and puts.
    - get_ticker_data: Get the options chain data for the given ticker and add tabs for each expiration date.
    - add_long: Adds a long option to the plot.
    - add_short: Adds a short option to the plot.
    - reset_plot: Resets the plot.
    - show_heatmap: Shows the future payoff heatmap.

    '''
    def __init__(self, demo = False, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Options Chains by Expiration Date")
        self.setGeometry(200, 200, 1600, 600)

        self.demo = demo
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
        self.tabs.setStyleSheet("""
            QTabBar::tab {
                background: #2E3440;      
                color: #D8DEE9;          
                padding: 10px;
                border: 1px solid #4C566A; 
                border-bottom: none;      
                border-radius: 5px 5px 0 0; 
            }

            QTabBar::tab:selected {
                background: #81A1C1;      
                color: #ECEFF4;           
            }
        """)
        main_layout.addWidget(self.tabs, stretch = 3)

        self.configure_figure(main_layout)

        self.show_no_data_message()


        # initialize data

        self.options = []
        self.expirations = []
        self.div_yields = []
        self.positions = []

        return

    def configure_left_layout(self, layout: QVBoxLayout) -> None:
        '''
        Configure the left layout of the window. Includes the input fields for the ticker and the buttons, labels for stock price, 
        option greeks, and a toggle button to switch between calls and puts.

        ### Parameters:
        - layout: QVBoxLayout: The layout to add the left layout to.
        '''
        left_layout = qtw.QVBoxLayout()
        left_layout.setContentsMargins(20, 50, 20, 20)

        # Add a toggle button to view either calls or puts
        self.toggle_button = QPushButton()

        configure_button(self.toggle_button, 
                         text="Toggle Calls/Puts",
                         command=self.toggle_calls_puts
                         )
        

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

        stock_info = QGridLayout()
        stock_info.setVerticalSpacing(2)

        option_info = QGridLayout()
        option_info.setVerticalSpacing(2)

        self.stock_labels = {}
        self.option_labels = {}
        self.initialize_labels(stock_info, option_info)
        # Add to the left layout
        left_layout.addLayout(ticker_layout)
        left_layout.addWidget(self.enter_ticker)
        left_layout.addLayout(stock_info)
        left_layout.addLayout(option_info)
        left_layout.addWidget(self.toggle_button)
        

        layout.addLayout(left_layout, stretch = 0)

        return 

    def configure_figure(self, layout: QVBoxLayout) -> None:
        '''
        Configures the right layout of the window. Includes the figure for the option payoff plot, buttons to add long and short options,
        a button to reset the plot, and a button to show the future payoff heatmap. The future payoff heatmap connects to the Heatmap class.
        
        ### Parameters:
        - layout: QVBoxLayout: The layout to add to.
        '''

        right_layout = qtw.QVBoxLayout()

        right_layout.addWidget(self.display)
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

    def show_no_data_message(self) -> None:
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

    def initialize_labels(self, stocklayout: QGridLayout, optionlayout: QGridLayout) -> None:
        '''
        Initializes QLabel widgets for displaying descriptive statistics and adds them to the top layout.
        
        ### Parameters:
        - stocklayout: QGridLayout: The layout to add the ticker and stock price labels to.
        - optionlayout: QGridLayout: The layout to add the option greeks labels to. Only for option info.

        '''
        # Define the labels you want to display
        title_names = ["Stock Ticker","Current Price"]

        for i, name in enumerate(title_names):
            # Create value label
            value = QLabel("N/A")
            value.setStyleSheet("font-size: 30px; color: white; padding: 1px;")
            value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # Add to the grid layout
            stocklayout.addWidget(value, i // 2, (i % 2) * 2)

            self.stock_labels[name] = value

        label_names = [
            "Delta",
            "Gamma",
            "Theta",
            "Vega",
            "Rho",
            "Implied Volatility"]
        
        # Set font for labels
        title_font = QFont("Arial", 12, QFont.Bold)
        value_font = QFont("Arial", 12)
        
        for i, name in enumerate(label_names):
            # Create title label
            title = QLabel(f"{name}:")
            title.setMinimumWidth(100)
            title.setFont(title_font)
            title.setStyleSheet('''font-family: Arial;
                                font-size: 18px; 
                                color: white; 
                                padding: 1px;''')
            title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Create value label
            value = QLabel("N/A")
            title.setMinimumWidth(100)
            value.setFont(value_font)
            value.setStyleSheet("color: white;")
            value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
             
            # Add to the grid layout
            optionlayout.addWidget(title, i // 2, (i % 2) * 2)
            optionlayout.addWidget(value, i // 2, (i % 2) * 2 + 1)
            
            # Store the label in the dictionary for easy access
            self.option_labels[name] = value

        return

    def update_stock_labels(self, stock_data: dict) -> None:
        '''
        Updates the labels with the given data.
        
        ### Parameters:
        - stock_data: dict: Dictionary containing stock data.
        
        ### Returns:
        - None
        '''
        # Update stock labels
        for name, value in stock_data.items():
            self.stock_labels[name].setText(str(value))

        return

    def update_option_labels(self, option_data: dict, option_type: Optional[str] = None) -> None:
        '''
        Updates the labels with new options data. Dependent on what kind of option is being added (long or short).
        
        ### Parameters:
        - option_data: dict: Dictionary containing option data.
        - option_type: str: 'long' or 'short'
        
        ### Returns:
        - None
        '''
        # Update stock labels
        for name, value in option_data.items():
            if self.option_labels[name].text() == 'N/A' or value == 'N/A':
                self.option_labels[name].setText(str(value))
            else:
                if option_type == 'long':
                    curr_val = float(self.option_labels[name].text())
                    self.option_labels[name].setText(f"{curr_val+value:.2f}")
                else:
                    curr_val = float(self.option_labels[name].text())
                    self.option_labels[name].setText(f"{curr_val-value:.2f}")
            
        return

    def add_tab(self, expiration_date: str, calls_df: pd.DataFrame, puts_df: pd.DataFrame) -> None:
        '''
        Adds a new tab for a given expiration date with its options chain table. Each tab is a TableView widget.
        Used to display the options chain data for a given expiration date.

        ### Parameters:
            - expiration_date (str): The expiration date label for the tab.
            - df (pd.DataFrame): The options chain data to display in the table.
            - The data inserted into the table is originally in the form of 'exp_date': pd.DataFrame
        '''
        # Create a new QWidget for the tab
        tab = qtw.QWidget()
        tab_layout = qtw.QVBoxLayout()
        tab.setLayout(tab_layout)

        # Create the table view
        table_view = QTableView()

        # Set the style for the table. 
        table_view.setStyleSheet("""
            QTableView {
                background-color: #000000; 
                color: white;              
                gridline-color: #444444;   
                selection-background-color: #555555; 
            }

            QHeaderView::section {
                background-color: #333333; 
                color: white;              
                padding: 4px;              
                border: 1px solid #555555; 
                font-weight: bold;         
            }

            QHeaderView::section {
                border: none;
            }
        """)
        table_view.setEditTriggers(qtw.QAbstractItemView.NoEditTriggers)  # Make table read-only
        table_view.setSelectionBehavior(qtw.QAbstractItemView.SelectRows)
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

    def retrieve_option(self, index: QModelIndex) -> None:
        '''
        Slot to handle click events on the table view. Turns on the buttons to add long and short options to the plot.
        Instantiates the current_option attribute with the data of the selected option. Also sets the text of the option_description label.

        ### Parameters:
        - index (QModelIndex): The index of the clicked cell.
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

    def toggle_calls_puts(self) -> None:
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
        
        return

    def get_ticker_data(self) -> None:
        '''
        Get the options chain data for the given ticker and add tabs for each expiration date. Uses the SchwabData class to get the data from Schwab Developer.
        Adds vertical lines to the plot for the current price of the stock. Instantiates calls_data and puts_data attributes. Clears existing tabs,
        and adds new ones for the new options chain.
        '''

        if self.ticker and self.ticker_input.text().upper() != self.ticker: # if we have a different ticker than already exists
            reply = QMessageBox.warning(
                self,
                "Warning",
                "If you change the ticker, you're strategy plot will be reset! Proceed?",   
                QMessageBox.Ok | QMessageBox.Cancel,
                QMessageBox.Cancel
            )
            if reply == QMessageBox.Cancel:
                return
            else:
                self.display.remove_vlines()
                self.reset_plot()

        # Get the ticker from the input field
        self.ticker = self.ticker_input.text().upper()
        
        try:
            data, r_f = self.engine.get_options_chain_dict(self.ticker)
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
        self.interest_rate = r_f/100

        # Clear existing tabs
        self.tabs.clear()
        self.table_views.clear()

        # Add tabs for calls and puts based on ticker
        expiration_dates = self.calls_data.keys()

        for expdate in expiration_dates:
            self.add_tab(expdate, self.calls_data[expdate], self.puts_data[expdate])

        self.ticker_input.clear()

        self.display.add_vline(self.engine.get_price(self.ticker), name="Current Price")
        
        stock_data = {
            "Stock Ticker": self.ticker,
            "Current Price": self.engine.get_price(self.ticker)
        }
        self.update_stock_labels(stock_data)

        return

    def add_long(self) -> None:
        '''
        Adds a long option to the plot. Updates the plot with the new option. Stores the new option and its attributes 
        as an attribute of the class, and also updates the labels accordingly. 
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

        options_data = {
            "Delta": self.current_option['Delta'],
            "Gamma": self.current_option['Gamma'],
            "Theta": self.current_option['Theta'],
            "Vega": self.current_option['Vega'],
            "Rho": self.current_option['Rho'],
            "Implied Volatility": self.current_option['Volatility']
        }
        self.update_option_labels(options_data,'long')

        return

    def add_short(self) -> None:
        '''
        Adds a short option to the plot. Updates the plot with the new option. Stores the new option and its attributes 
        as an attribute of the class, and also updates the labels accordingly. 
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

        options_data = {
            "Delta": self.current_option['Delta'],
            "Gamma": self.current_option['Gamma'],
            "Theta": self.current_option['Theta'],
            "Vega": self.current_option['Vega'],
            "Rho": self.current_option['Rho'],
            "Implied Volatility": self.current_option['Volatility']
        }
        self.update_option_labels(options_data,'short')

        return
    
    def reset_plot(self) -> None:
        '''
        Resets the plot. Clears all stored options and their attributes. Updates the labels accordingly. 
        Also turns off buttons to prevent errors with empty data
        '''
        self.display.reset_data()
        self.option_description.setText("No option selected.")
        
        option_data = {
            "Delta": "N/A",
            "Gamma": "N/A",
            "Theta": "N/A",
            "Vega": "N/A",
            "Rho": "N/A",
            "Implied Volatility": "N/A"
        }
        self.update_option_labels(option_data)

        # self.current_option = None
        self.options.clear()
        self.expirations.clear()
        self.div_yields.clear()
        self.positions.clear()
        self.total_cost = 0
        
        self.long_button.setEnabled(False)
        self.short_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.heatmap.setEnabled(False)

    def show_heatmap(self) -> None:
        '''
        Shows the future payoff heatmap. Checks if the necessary data is loaded before showing the heatmap.
        Instantiates a heatmap object and passes in stored data from all the options the user added to their strategy. 
        '''
        if not hasattr(self, 'interest_rate') or not self.options:
            QMessageBox.warning(
                self,
                "No Options Data",
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
                        self.total_cost,
                        self.demo
                        )
        self.heatmap.setStyleSheet('''
                    QWidget { 
                    font-family: Arial;
                    font-size: 16px;
                    color: white;
                    background: #17212e;
                    }

                    QPushButton {
                    /* background-color: #614393; */
                    background-color: #2c405a;
                    padding: 8px;
                    border-radius: 5px 5px 0 0;
                    }

                    QPushButton:hover {
                    background-color: #8e64d4;
                    }
                    
                    ''')
        self.heatmap.show()


