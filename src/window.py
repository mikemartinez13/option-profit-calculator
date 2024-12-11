from PyQt5 import QtWidgets as qtw
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
        self.setWindowTitle("Trading Tool Dashboard")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget and layout
        central_widget = qtw.QWidget()
        self.setCentralWidget(central_widget)
        layout = qtw.QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Buttons for navigation
        self.strategy_button = qtw.QPushButton("Build Strategy")
        self.portfolio_button = qtw.QPushButton("View Portfolio")
        # Add more buttons as needed
        
        layout.addWidget(self.strategy_button)
        layout.addWidget(self.portfolio_button)
        # Add more buttons to layout
        
        # Connect buttons to methods
        self.strategy_button.clicked.connect(self.open_strategy_builder)
        #self.portfolio_button.clicked.connect(self.open_portfolio_viewer)
        # Connect more buttons as needed

        # Initialize Strategy Builder window
        self.strategy_builder_window = OptionChainWindow(demo=self.demo)
        
        # self.portfolio_viewer_window = PortfolioViewerWindow()
        # Initialize more feature windows as needed
        
        return

    def open_strategy_builder(self):
        self.strategy_builder_window.show()

    # def open_portfolio_viewer(self):
    #     self.portfolio_viewer_window.show()

if __name__ == '__main__':
    # app = qtw.QApplication([])
    # window = MainWindow()
    # window.show()
    # sys.exit(app.exec_())
    pass
