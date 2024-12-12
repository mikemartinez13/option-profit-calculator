import sys
from PyQt5 import QtWidgets as qtw

import plotly.graph_objs as go
import plotly.offline as offline
import plotly.io as pio
import plotly.express as px
import tempfile
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import os

class PlotlyTestWindow(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Plotly Test")
        self.setGeometry(100, 100, 800, 600)
        layout = qtw.QVBoxLayout()
        self.setLayout(layout)

        # Create a simple Plotly figure
        fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[4, 5, 6], mode='lines+markers'))
        fig.update_layout(title="Sample Plotly Figure")

        # Convert Plotly figure to HTML
        self.temp_html_file = self.create_temp_plot(fig)
        # html = pio.to_html(fig, full_html=False,include_plotlyjs='inline')
        # print(html)

        # Set up QWebEngineView
        self.web_view = QWebEngineView()
        self.web_view.load(QUrl.fromLocalFile(self.temp_html_file))

        layout.addWidget(self.web_view)

    def create_temp_plot(self, fig):
        """
        Generates a temporary HTML file containing the Plotly figure.

        Parameters:
            fig (plotly.graph_objs.Figure): The Plotly figure to render.

        Returns:
            str: The absolute path to the temporary HTML file.
        """
        # Create a temporary file with a .html suffix
        temp_file = tempfile.NamedTemporaryFile(delete=False, 
                                                suffix='.html', 
                                                mode='w', 
                                                encoding='utf-8',
                                                dir=os.getcwd()
                                                )
        temp_file_path = temp_file.name

        # try:
        # Generate the HTML using plotly.offline.plot
        offline.plot(fig, filename=temp_file_path, auto_open=False)
        #print(f"Temporary Plotly HTML file created at: {temp_file_path}")
        # # except Exception as e:
        # #     print(f"Error generating Plotly HTML: {e}")
        # #     temp_file.close()
        # #     os.unlink(temp_file_path)
        # #     raise e
        # finally:
        temp_file.close()

        return temp_file_path

    def closeEvent(self, event):
        """
        Ensures that the temporary HTML file is deleted when the application is closed.
        """
        try:
            if os.path.exists(self.temp_html_file):
                os.unlink(self.temp_html_file)
                print(f"Temporary Plotly HTML file deleted: {self.temp_html_file}")
        except Exception as e:
            print(f"Error deleting temporary file: {e}")
        event.accept()
    

if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    window = PlotlyTestWindow()
    window.show()
    sys.exit(app.exec_())

# import sys
# import plotly




# def main():
#     '''
#         A simple example of a plotly application
#     '''
#     # Some data
#     x_coords = [1, 2, 3, 5, 6]
#     y_coords = [1, 4.5, 7, 24, 38]

#     trace = dict(x=x_coords, y=y_coords)

#     data = [trace]

#     app = QApplication(sys.argv)
#     view = QWebEngineView()
#     view.load(QUrl(plotly.offline.plot(data, auto_open=False)))
#     view.show()
#     return app.exec_()


# if __name__ == "__main__":
#     from PyQt5.QtWidgets import QApplication
#     from PyQt5.QtCore import QUrl
#     from PyQt5.QtWebEngineWidgets import QWebEngineView
#     main()
