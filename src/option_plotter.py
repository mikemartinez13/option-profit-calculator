# from PyQt5 import QtWidgets as qtw
# from vis import payoff 
# import src.custom_components as comp
# from src.custom_components import configure_button
# from PyQt5.QtWebEngineWidgets import QWebEngineView
# import matplotlib.pyplot as plt
# import sys

# # class OptionProfitCalculator(comp.WindowWithFigureAbove):
# #     def __init__(self, 
# #                  fig: plt.Figure,
# #                  title: str = "Option Profit Calculator"
# #                  ):
# #         super().__init__(fig, title)

# #         self.engine = plots.OptionPayoffPlot()
        
# #         self.configure_calculator()

# #         return 
    
# #     # Let's say I'm calculating combined payoff for a certain investment strategy. I want to be able to create buttons that allow 
    
# #     def configure_calculator(self) -> None:
# #         '''
# #         Adds customs widgets/buttons to the option profit calculator window.
# #         '''
# #         self.setGeometry(150, 150, 600, 400)
        
# #         # Add widgets specific to strategy building
# #         self.label = qtw.QLabel("Build your trading strategy here.")
# #         self.my_layout.addWidget(self.label)
        
# #         # Add buttons to build strategies
# #         self.add_button = qtw.QPushButton()
# #         configure_button(self.add_button, 
# #                          text='Add Option',
# #                          command=self.add_option)
        
# #         self.reset_button = qtw.QPushButton()
# #         configure_button(self.reset_button,
# #                          text='Reset to Empty',
# #                          command=self.reset)
        
# #         self.my_layout.addWidget(self.build_button)

# #         return

# #     def add_option(self):
# #         # Implement logic to add an option
# #         self.engine.add_option()
# #         qtw.QMessageBox.information(self, "Option", "Option Added Successfully!")
# #         return
    
# #     def reset(self):
# #         # Implement logic to reset the strategy
# #         qtw.QMessageBox.information(self, "Reset", "Strategy Reset Successfully!")
# #         return
    
# #     def build_strategy(self):
# #         # Implement strategy building logic
# #         qtw.QMessageBox.information(self, "Strategy", "Strategy Built Successfully!")



# class OptionProfitCalculator(qtw.QWidget):
#     def __init__(self, title: str = "Option Profit Calculator"):
#         super().__init__()
#         self.setWindowTitle(title)
#         self.setGeometry(150, 150, 800, 600)

#         # Initialize the payoff engine
#         self.engine = payoff.OptionPayoffPlot()

#         # Set up the layout
#         self.main_layout = qtw.QVBoxLayout()
#         self.setLayout(self.main_layout)

#         # Add widgets specific to strategy building
#         self.label = qtw.QLabel("Build your trading strategy here.")
#         self.main_layout.addWidget(self.label)

#         # Add buttons to build strategies
#         button_layout = qtw.QHBoxLayout()

#         self.add_button = qtw.QPushButton('Add Option')
#         self.add_button.clicked.connect(self.add_option)
#         button_layout.addWidget(self.add_button)

#         self.reset_button = qtw.QPushButton('Reset to Empty')
#         self.reset_button.clicked.connect(self.reset)
#         button_layout.addWidget(self.reset_button)

#         self.main_layout.addLayout(button_layout)

#         # Add the Plotly graph via QWebEngineView
#         self.web_view = QWebEngineView()
#         self.update_plot()
#         self.main_layout.addWidget(self.web_view)

#     def update_plot(self):
#         '''
#         Updates the Plotly graph in the QWebEngineView.
#         '''
#         html = self.engine.get_html()
#         self.web_view.setHtml(html)

#     def add_option(self, option,opt_type,buy,s0):
#         # Example: Add a long call option. Replace with actual option data as needed.
#         # For a dynamic application, you would gather these details from user input.

#         self.engine.add_option(option, opt_type, buy, s0)
#         self.update_plot()

#         #qtw.QMessageBox.information(self, "Option", "Option Added Successfully!")

#     def reset(self):
#         self.engine.reset_data()
#         self.update_plot()

#         qtw.QMessageBox.information(self, "Reset", "Strategy Reset Successfully!")
