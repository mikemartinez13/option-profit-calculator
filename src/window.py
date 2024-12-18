from PyQt5 import QtWidgets as qtw
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
#from option_plotter import OptionProfitCalculator
from src.option_chain import OptionChainWindow
from utils import data_utils as dat

import sys
#from portfolio_viewer import PortfolioViewerWindow
# Import other feature windows as needed

class MainWindow(qtw.QMainWindow):
    def __init__(self, demo: bool = False):
        super().__init__()

        self.demo = demo
        
        self.configure_main_window()
        
        return

    def configure_main_window(self) -> None:
        '''
        Method to configure the main window of the application. Adds labels, buttons, and connects them to OptionChainWindow. 
        '''
        self.setWindowTitle("Trading Tool Dashboard")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget and layout
        central_widget = qtw.QWidget()
        central_widget.setStyleSheet('''background: #17212e;''')
        self.setCentralWidget(central_widget)
        layout = qtw.QVBoxLayout()
        central_widget.setLayout(layout)

        layout.setContentsMargins(20, 20, 20, 20)  # Adjust padding as needed

        # Title Label
        title_label = qtw.QLabel("Option Profit Calculator")
        title_label.setStyleSheet('''font-family: Arial; color: white;''')
        title_font = title_label.font()
        title_font.setPointSize(30)  # Increase font size
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)

        # Author Label
        author_label = qtw.QLabel("Created by Michael Martinez")  # Replace 'Your Name' with actual name
        author_label.setStyleSheet('''font-family: Arial; color: white;''')
        author_font = author_label.font()
        author_font.setPointSize(14)  # Set a smaller font size for the author
        author_label.setFont(author_font)
        author_label.setAlignment(Qt.AlignCenter)

        description_label = qtw.QLabel(
            "Welcome to the Option Profit Calculator!\n\n"
            "This tool helps you graph custom option strategies for any stock and visualize their potential payoffs in the future.\n\n"
            "Press Build Strategy to get started! For additional support, check out <a href=\"https://github.com/mikemartinez13/option-profit-calculator\">the GitHub</a>."
        )
        description_label.setStyleSheet('''font-family: Arial;
                    font-size: 20px;
                    color: white;
                    background: #17212e;''')
        description_label.setAlignment(Qt.AlignCenter)
        description_label.setWordWrap(True)  # Enable word wrapping for better readability

        description_label.setTextFormat(Qt.RichText)
        description_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        description_label.setOpenExternalLinks(True)

        layout.addWidget(title_label)
        layout.addWidget(author_label)
        layout.addSpacing(20) 
        layout.addWidget(description_label)
        layout.addSpacing(50) 

        # Spacer to add some space between the author and buttons
        layout.addSpacing(50)  # Adjust the spacing as needed

        button_layout = qtw.QVBoxLayout()
        button_layout.addSpacing(30)

        self.strategy_button = qtw.QPushButton("Build Strategy")
        self.strategy_button.setStyleSheet('''font-family: Arial;
                    font-size: 18px;
                    color: white; background-color: #2c405a; border-radius: 5px 5px 0 0;''')
        # Connect buttons to methods
        self.strategy_button.clicked.connect(self.open_strategy_builder)
        button_layout.addWidget(self.strategy_button)

        self.portfolio_button = qtw.QPushButton("View Portfolio")
        self.portfolio_button.setStyleSheet('''font-family: Arial;
                    font-size: 18px;
                    color: white; background-color: #2c405a; border-radius: 5px 5px 0 0;''')
        button_layout.addWidget(self.portfolio_button)



        layout.addWidget(self.strategy_button)
        layout.addWidget(self.portfolio_button)

        # Add button layout
        layout.addLayout(button_layout)


        self.strategy_builder_window = OptionChainWindow(demo=self.demo)
        self.strategy_builder_window.setStyleSheet('''
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
        # self.portfolio_viewer_window = PortfolioViewerWindow()
        
        return

    def open_strategy_builder(self):
        self.strategy_builder_window.show()

        return