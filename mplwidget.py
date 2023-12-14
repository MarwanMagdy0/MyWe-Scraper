from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import seaborn
import matplotlib.dates as mdates
class MplWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        seaborn.set_style("darkgrid")  # Apply seaborn style
        self.figure = Figure(facecolor='#17181d')
        self.canvas = FigureCanvas(self.figure)
        self.axes1 = self.figure.add_subplot(121)
        self.axes2 = self.figure.add_subplot(122)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.setStyleSheet('''
                QWidget {
                    background-color: #17181d;
                    color: #FFFFFF;
                    border:none;
                }

                QToolBar {
                    background-color: #17181d;
                    border: 1px solid #17181d;
                }

                QToolButton {
                    background-color: #ffffff;
                    color: #FFFFFF;
                }

                QToolButton:hover {
                    background-color: #555555;
                }

                QToolButton:pressed {
                    background-color: #777777;
                }
            ''')

        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        font = {'family': 'Arial', 'size': 10, 'color': 'white'}
        for ax in [self.axes1, self.axes2]:
            ax.tick_params(axis='x', labelcolor='white', labelsize=10)
            ax.tick_params(axis='y', labelcolor='white', labelsize=10)
            ax.tick_params(axis='x', rotation=45, labelsize=7)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
