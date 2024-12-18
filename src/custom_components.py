#from src.globals import *

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtCore
from typing import Callable
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
import pandas as pd
from PyQt5.QtCore import Qt


class WindowWithVerticalSlots(qtw.QWidget):
    '''
    A window with a title and an empty
    vertical container (QVBoxLayout).
    
    Intended use is to inherit and add
    additional customization
    '''
    def __init__(self, title: str):
        super().__init__()
        
        # Make a title for the window
        self.setWindowTitle(title)
        
        # Create an empty vertical layout container
        self.my_layout = qtw.QVBoxLayout(self)
        return
    

class WindowWithFigureAbove(WindowWithVerticalSlots):
    '''
    A window with vertical layout and matplotlib figure on top. 
    '''
    def __init__(self, 
                 fig: plt.Figure, 
                 title: str = 'Window with a Figure'):
        super().__init__(title=title)

        # Create a canvas for the figure
        self.canvas = FigureCanvasQTAgg(fig)
        self.my_layout.addWidget(self.canvas)

        return 
    

class ButtonRow(qtw.QHBoxLayout):
    '''
    A horizontal row of buttons. Names must be provided for each.
    '''
    def __init__(self, 
                 names: list[str]
                 ):
        super().__init__()

        self.items = []
        for name in names: 
            self.items.append(qtw.QPushButton(name))
            self.addWidget(self.items[-1])
        return 
    

class ButtonBox(qtw.QVBoxLayout):
    '''
    A vertical container of ButtonRow objects.

        nrows: How many rows of buttons
        ncols: How many buttons in each row
    '''
    def __init__(self, 
                 nrows: int,
                 ncols: int):
        super().__init__()

        self.rows = []
        for _ in range(nrows):
            names = [f'Button {i}' for i in range(ncols)]
            self.rows.append(ButtonRow(names))
            self.addLayout(self.rows[-1]) # last one we just made
        
        return

def configure_button(button: qtw.QPushButton,
                     text:str, 
                     command: Callable) -> None:
    button.setText(text)
    button.clicked.connect(command)
    # Gives button text and gives it a function when clicked.
    
    return


class PandasModel(QtCore.QAbstractTableModel):
    '''
    Custom class to display pandas dataframes in PyQt5. Inherits from QAbstractTableModel.
    Directly ported from this StackOverflow post https://stackoverflow.com/questions/44603119/how-to-display-a-pandas-data-frame-with-pyqt5-pyside2, 
    aided by ChatGPT to update outdated methods. 
    '''
    def __init__(self, data: pd.DataFrame, parent=None):
        super().__init__(parent)
        self._data = data.copy()

    def rowCount(self, parent=None) -> int:
        '''
        Returns the number of rows in the dataframe.
        '''
        return self._data.shape[0]

    def columnCount(self, parent=None) -> int:
        '''
        Returns the number of columns in the dataframe.
        '''
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole): # role for why the data is requested
        if not index.isValid():
            return None

        if role == Qt.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

        elif role == Qt.TextAlignmentRole: # centers the data in each cell
            return Qt.AlignCenter

        return 
    
    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable # allows users to select and view data

    def headerData(self, section, orientation, role=Qt.DisplayRole): # displays names of columns and rows
        '''
        Displays the headers of the table
        '''
        if role != Qt.DisplayRole:
            return 

        if orientation == Qt.Horizontal:
            try:
                return str(self._data.columns[section])
            except (IndexError, ):
                return 
        elif orientation == Qt.Vertical:
            return str(self._data.index[section])
        
        return
    
    def sort(self, column, order):
        '''
        Sorts the data by the column and order specified.
        '''
        colname = self._data.columns[column]
        self.layoutAboutToBeChanged.emit()
        self._data.sort_values(colname, ascending=order == Qt.AscendingOrder, inplace=True)
        self._data.reset_index(drop=True, inplace=True)
        self.layoutChanged.emit()

    def update_data(self, data: pd.DataFrame):
        '''
        Updates the data displayed in the table.
        '''
        self.beginResetModel()
        self._data = data.copy()
        self.endResetModel()