from PyQt5 import QtWidgets as qtw

import sys

class DataDashboard(qtw.QApplication):
    def __init__(self):
        super().__init__([]) # give a QApplication an empty list of arguments, usually wants to accept command line args

        self.engine = RandomDataAnalysis()
        self.display = SimpleScatter()

        self.configure_main_window()

        self.main_window.show()

        sys.exit(self.exec_())

        return
    
    def configure_main_window(self) -> None:
        self.main_window = WindowWithFigureAbove(self.display.fig)

        self.buttons = ButtonBox(nrows=2, ncols=2)
        self.main_window.my_layout.addLayout(self.buttons)

        configure_button(self.buttons.rows[0].items[0], 
                         text='Generate Random Data',
                         command=self.make_random_data
                         )
        
        configure_button(self.buttons.rows[0].items[1],
                         text='Save Figure',
                         command=self.save_figure)
        
        configure_button(self.buttons.rows[1].items[0],
                         text='Load Data',
                         command=self.load_data)
        
        configure_button(self.buttons.rows[1].items[1],
                         text='Save Data',
                         command=self.save_data)
        
        return

    def make_random_data(self) -> None:
        self.engine.make_random_data()
        self.update_plot()

        return

    def update_plot(self):
        self.display.update_scatter(self.engine.get_data())
        self.main_window.canvas.draw()

        return
    
    def load_data(self):
        '''
        Loading a .csv file with data
        '''
        file_name, _ = qtw.QFileDialog.getOpenFileName(self.main_window, 
                                                       'Select a file',
                                                       PATH_DATA
                                                       ) # Belongs to the main window
        if file_name != '':
            self.engine.load_data(file_name)
            self.update_plot()

        return
    
    def save_data(self):
        '''
        Save the current data to a .csv file
        '''
        file_name, _ = qtw.QFileDialog.getSaveFileName(self.main_window,
                                                       'Select a file',
                                                       PATH_DATA
                                                       ) # Belongs to the main window
        self.engine.save_data(file_name)
        
        return

    def save_figure(self) -> None:
        '''
        Save the figure as .png
        '''
        file_name, _ = qtw.QFileDialog.getSaveFileName(self.main_window,
                                                       'Name the file',
                                                       PATH_FIGURES
                                                       )
        self.display.save_plot(file_name)

        return
    
if __name__ == '__main__':
    DataDashboard()