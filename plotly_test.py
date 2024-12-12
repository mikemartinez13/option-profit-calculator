import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import plotly.graph_objs as go
import plotly.io as pio
import datetime

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Plotly Update Test")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)

        self.update_button = QPushButton("Update Plot")
        self.update_button.clicked.connect(self.update_plot)
        layout.addWidget(self.update_button)

        self.counter = 0
        self.update_plot()

    def update_plot(self):
        self.counter += 1
        fig = go.Figure(data=go.Scatter(x=[1, 2, 3], y=[self.counter, self.counter+1, self.counter+2]))
        fig.update_layout(title=f"Plot Update #{self.counter} at {datetime.datetime.now().strftime('%H:%M:%S')}")

        html = pio.to_html(
            fig, 
            full_html=True, 
            include_plotlyjs='inline'
        )

        unique_base_url = QUrl("about:blank#{}".format(datetime.datetime.now().timestamp()))
        self.web_view.setHtml(html, unique_base_url)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())
