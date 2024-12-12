import os.path
import posixpath
import sys
#from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.offline as offline
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.express as px

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        self.setWindowTitle('PyQt & Plotly')

        # create data frame (or read directly from a csv file)
        self.df = {
            "Date": ["01/02/1965", "01/04/1965", "01/05/1965", "01/08/1965", "01/09/1965"],
            "Latitude": [19.246, 1.8630, -20.579, -59.076, 11.9379],
            "Longitude": [145.616, 127.352, -173.972, -23.557, 126.427],
            "Magnitude": [6.0, 5.8, 6.2, 5.8, 5.1]
            }

        # create figure for the heatmap
        fig = px.density_mapbox(self.df, lat='Latitude', lon='Longitude', z='Magnitude', radius=10, center=dict(lat=0, lon=180), zoom=0, mapbox_style="open-street-map")
        
        # create the html file for the offline map
        # note that we are working offline, so we first generate the html file with heatmaps on, then display it on the Qt GUI
        self.filename = os.path.join(os.getcwd(), 'map.html').replace(os.path.sep, posixpath.sep)
        
        # put the data from the data frame on the html map
        offline.plot(fig, filename=self.filename, auto_open=False)

        self.view = QWebEngineView()
        self.view.load(QUrl.fromLocalFile(self.filename))

        self.setCentralWidget(self.view)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec()