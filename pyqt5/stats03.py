import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QHBoxLayout, QProgressBar, QLabel)
from PyQt5.QtCore import QThread, pyqtSignal

# --- 1. THE DATA WORKER (QThread) ---
class DataDownloader(QThread):
    # Signal to send the DataFrame back to the Main Thread
    data_ready = pyqtSignal(pd.DataFrame)
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            # URL to a real CSV dataset (Global Fuel Prices 2024-2026)
            url = "https://raw.githubusercontent.com/datasets/gdp/main/data/gdp.csv"
            
            # Heavy operation: Network I/O and Parsing
            df = pd.read_csv(url)
            
            # Filtering data for a cleaner chart (e.g., specific countries)
            countries = ['United States', 'China', 'India', 'Japan', 'Germany']
            filtered_df = df[df['Country Name'].isin(countries)]
            
            # Send result back
            self.data_ready.emit(filtered_df)
        except Exception as e:
            self.error_occurred.emit(str(e))

# --- 2. THE MAIN UI ---
class StatAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Global GDP Statistics Analyzer")
        self.setGeometry(100, 100, 1000, 600)

        # UI Components
        self.status_label = QLabel("Click 'Load' to fetch global data...")
        self.load_btn = QPushButton("Load & Analyze Online Data")
        self.progress = QProgressBar()
        self.progress.hide()

        # Matplotlib Figure
        self.figure, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvas(self.figure)

        # Layout Setup
        layout = QVBoxLayout()
        layout.addWidget(self.status_label)
        layout.addWidget(self.progress)
        layout.addWidget(self.canvas)
        layout.addWidget(self.load_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connect Signal
        self.load_btn.clicked.connect(self.start_download)

    def start_download(self):
        self.load_btn.setEnabled(False)
        self.status_label.setText("Downloading CSV from GitHub...")
        self.progress.show()
        self.progress.setRange(0, 0) # Pulsing "busy" mode

        # Start the worker thread
        self.worker = DataDownloader()
        self.worker.data_ready.connect(self.process_and_plot)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.start()

    def process_and_plot(self, df):
        # We are back in the Main Thread now!
        self.progress.hide()
        self.load_btn.setEnabled(True)
        self.status_label.setText(f"Loaded {len(df)} records.")

        # Update the Matplotlib Chart
        self.ax.clear()
        # Plotting GDP over time for selected countries
        for country, group in df.groupby('Country Name'):
            self.ax.plot(group['Year'], group['Value'], label=country)
        
        self.ax.set_title("GDP Comparison Over Time")
        self.ax.set_xlabel("Year")
        self.ax.set_ylabel("GDP (USD)")
        self.ax.legend()
        self.canvas.draw()

    def handle_error(self, msg):
        self.status_label.setText(f"Error: {msg}")
        self.load_btn.setEnabled(True)
        self.progress.hide()

# --- 3. THE RUNTIME ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StatAnalyzer()
    window.show()
    sys.exit(app.exec_())