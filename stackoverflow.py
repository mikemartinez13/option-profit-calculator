from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QTimer
from plotly.graph_objects import Figure, Scatter, Bar
import plotly
import numpy as np
import random


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        # Initialize plot data
        self.x = np.linspace(0, 10, 100)  # 100 points between 0 and 10
        self.current_plot_type = 'scatter'  # Start with scatter plot

        # Create the initial Plotly figure
        self.fig = Figure()

        # Add initial scatter plot
        scatter = Scatter(x=self.x, y=np.sin(self.x),
                          mode='lines+markers',
                          name='Sine Wave',
                          line=dict(color='blue', width=2),
                          marker=dict(size=6, color='red'))
        self.fig.add_trace(scatter)

        # Customize initial layout
        self.fig.update_layout(title='Initial Scatter Plot',
                               xaxis_title='X-axis',
                               yaxis_title='Y-axis',
                               plot_bgcolor='white')

        # Generate initial HTML for the plot
        self.html = self.generate_html()

        # Create an instance of QWebEngineView and set the initial HTML
        self.plot_widget = QWebEngineView()
        self.plot_widget.setHtml(self.html)

        # Set the QWebEngineView instance as the central widget
        self.setCentralWidget(self.plot_widget)

        # Set up a QTimer for periodic updates (e.g., every 2 seconds)
        self.timer = QTimer()
        self.timer.setInterval(2000)  # Update every 2000 milliseconds (2 seconds)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def generate_html(self):
        """
        Generates the HTML string for the current Plotly figure.
        """
        html = '<html><body>'
        html += plotly.offline.plot(self.fig, output_type='div', include_plotlyjs='cdn')
        html += '</body></html>'
        return html

    def update_plot(self):
        """
        Updates the Plotly figure with new data and refreshes the HTML content.
        Implements drastic changes for visibility.
        """
        # Clear existing traces
        self.fig.data = []

        # Randomly choose a plot type for variety
        plot_types = ['scatter', 'bar', 'scatter', 'bar']  # More likely to switch types
        self.current_plot_type = random.choice(plot_types)

        if self.current_plot_type == 'scatter':
            # Generate new data: e.g., cosine wave with random amplitude and frequency
            amplitude = random.uniform(0.5, 2.0)
            frequency = random.uniform(0.5, 2.0)
            phase = random.uniform(0, np.pi)
            y_new = amplitude * np.cos(frequency * self.x + phase)

            # Create a scatter plot with new data and different styles
            scatter = Scatter(x=self.x, y=y_new,
                              mode='lines',
                              name='Cosine Wave',
                              line=dict(color=self.random_color(), width=random.randint(2, 5)),
                              marker=dict(size=random.randint(5, 10),
                                          color=self.random_color()))
            self.fig.add_trace(scatter)

            # Update layout with a new title and background color
            self.fig.update_layout(title='Updated Scatter Plot: Cosine Wave',
                                   plot_bgcolor=self.random_color())

        elif self.current_plot_type == 'bar':
            # Generate random bar heights
            y_new = np.random.randint(1, 20, size=self.x.shape)

            # Create a bar chart with new data and different styles
            bar = Bar(x=self.x, y=y_new,
                      name='Random Bars',
                      marker=dict(color=self.random_color()))
            self.fig.add_trace(bar)

            # Update layout with a new title and background color
            self.fig.update_layout(title='Updated Bar Chart: Random Data',
                                   plot_bgcolor=self.random_color())

        # Optionally, add more plot types for greater variety

        # Regenerate the HTML with the updated figure
        updated_html = self.generate_html()

        # Update the QWebEngineView with the new HTML
        self.plot_widget.setHtml(updated_html)

    def random_color(self):
        """
        Generates a random color in hexadecimal format.
        """
        return f'#{random.randint(0, 0xFFFFFF):06x}'


if __name__ == '__main__':
    app = QApplication([])
    window = MainWindow()
    window.resize(800, 600)  # Optional: Set a default window size
    window.show()
    app.exec_()
