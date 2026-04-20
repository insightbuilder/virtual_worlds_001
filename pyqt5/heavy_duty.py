import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QProgressBar, QLabel, QLineEdit)
from PyQt5.QtCore import QThread, pyqtSignal

# --- 1. THE ENGINE (Data Worker) ---
class GDPWorker(QThread):
    finished = pyqtSignal(pd.DataFrame)
    error = pyqtSignal(str)

    def run(self):
        try:
            # Verified Raw URL for World Bank GDP Data
            url = "https://raw.githubusercontent.com/datasets/gdp/main/data/gdp.csv"
            
            # Heavier Operation: Load & Basic Cleaning
            df = pd.read_csv(url)
            df['Year'] = pd.to_numeric(df['Year'])
            df['Value'] = pd.to_numeric(df['Value'])
            
            self.finished.emit(df)
        except Exception as e:
            self.error.emit(str(e))

# --- 2. THE UI (Dashboard) ---
class StatsApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Global Economic Analyzer (PyQt5 + Pandas)")
        self.resize(900, 700)
        
        self.full_data = None # Store the master DataFrame here

        # Widgets
        self.status = QLabel("Ready to load dataset...")
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Enter country (e.g. India, United States)...")
        self.search_box.setEnabled(False)
        
        self.btn_load = QPushButton("Fetch Online Data")
        self.progress = QProgressBar()
        self.progress.hide()

        # Matplotlib Setup
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.status)
        layout.addWidget(self.search_box)
        layout.addWidget(self.canvas)
        layout.addWidget(self.progress)
        layout.addWidget(self.btn_load)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Signals
        self.btn_load.clicked.connect(self.run_worker)
        self.search_box.textChanged.connect(self.update_plot)

    def run_worker(self):
        self.btn_load.setEnabled(False)
        self.progress.show()
        self.progress.setRange(0, 0) # Infinite pulse
        self.status.setText("Downloading heavy CSV...")

        self.worker = GDPWorker()
        self.worker.finished.connect(self.on_data_loaded)
        self.worker.error.connect(lambda e: self.status.setText(f"Error: {e}"))
        self.worker.start()

    def on_data_loaded(self, df):
        self.full_data = df
        self.progress.hide()
        self.btn_load.hide()
        self.search_box.setEnabled(True)
        self.status.setText(f"Loaded {len(df)} rows. Search for a country above.")
        self.update_plot()

    def update_plot(self):
        if self.full_data is None: return
        
        query = self.search_box.text().strip()
        # Using .loc for label-based filtering
        # This is high-speed filtering even with 13k rows
        filtered = self.full_data.loc[self.full_data['Country Name'].str.contains(query, case=False, na=False)]

        self.ax.clear()
        if not filtered.empty:
            # Group by Country and Plot
            for name, group in filtered.groupby('Country Name'):
                self.ax.plot(group['Year'], group['Value'], label=name)
            
            self.ax.set_title(f"GDP Trend: {query if query else 'All'}")
            self.ax.legend(loc='upper left', fontsize='small', ncol=2)
            self.ax.set_ylabel("GDP (USD)")
        
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StatsApp()
    window.show()
    sys.exit(app.exec_())