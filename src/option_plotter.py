from PyQt5 import QtWidgets as qtw
from vis import plots 
import src.custom_components as comp
from src.custom_components import configure_button
import matplotlib.pyplot as plt

class OptionProfitCalculator(comp.WindowWithFigureAbove):
    def __init__(self, 
                 fig: plt.Figure,
                 title: str = "Option Profit Calculator"
                 ):
        super().__init__(fig, title)

        self.engine = plots.OptionPayoffPlot()
        
        self.configure_calculator()

        return 
    
    # Let's say I'm calculating combined payoff for a certain investment strategy. I want to be able to create buttons that allow 
    
    def configure_calculator(self) -> None:
        '''
        Adds customs widgets/buttons to the option profit calculator window.
        '''
        self.setGeometry(150, 150, 600, 400)
        
        # Add widgets specific to strategy building
        self.label = qtw.QLabel("Build your trading strategy here.")
        self.my_layout.addWidget(self.label)
        
        # Add buttons to build strategies
        self.add_button = qtw.QPushButton()
        configure_button(self.add_button, 
                         text='Add Option',
                         command=self.add_option)
        
        self.reset_button = qtw.QPushButton()
        configure_button(self.reset_button,
                         text='Reset to Empty',
                         command=self.reset)
        
        self.my_layout.addWidget(self.build_button)

        return

    def add_option(self):
        # Implement logic to add an option
        self.engine.add_option()
        qtw.QMessageBox.information(self, "Option", "Option Added Successfully!")
        return
    
    def reset(self):
        # Implement logic to reset the strategy
        qtw.QMessageBox.information(self, "Reset", "Strategy Reset Successfully!")
        return
    
    def build_strategy(self):
        # Implement strategy building logic
        qtw.QMessageBox.information(self, "Strategy", "Strategy Built Successfully!")
