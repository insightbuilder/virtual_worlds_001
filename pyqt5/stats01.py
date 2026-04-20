import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class StatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Statistical Analysis Tool")
        
        # 1. Setup UI Layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)

        # 2. Setup the Plotting Canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # 3. Add an Action Button
        self.btn = QPushButton("Generate Random Stats")
        self.btn.clicked.connect(self.update_chart) # The Signal/Slot magic
        layout.addWidget(self.btn)

    def update_chart(self):
        # 4. Generate some mock data with Pandas
        data = pd.Series([1, 3, 2, 4, 3, 5])
        
        # 5. Clear and Redraw
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        data.plot(kind='bar', ax=ax, title="Statistical Distribution")
        self.canvas.draw()

app = QApplication(sys.argv)
window = StatApp()
window.show()
sys.exit(app.exec_())