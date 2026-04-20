import sys
import time
import pandas as pd
import numpy as np
import multiprocessing
from multiprocessing import Process, Queue
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                             QWidget, QLabel, QProgressBar, QDialog, QTextEdit)
from PyQt5.QtCore import QThread, pyqtSignal, Qt

# --- 1. THE HEAVY MATH (Process Level) ---
# This function MUST be outside any class for Multiprocessing to pick it up.
def heavy_data_crunch(queue, size):
    """Simulates a heavy statistical calculation in a separate process."""
    # Generate 1 million rows of data
    df = pd.DataFrame(
        np.random.randn(size, 4), 
        columns=['Alpha', 'Beta', 'Gamma', 'Delta']
    )
    
    # Perform heavy statistical summary
    stats = df.describe().to_string()
    
    # Simulate a 3-second 'thought' process
    time.sleep(3) 
    
    # Push the result into the communication queue
    queue.put(stats)

# --- 2. THE BRIDGE (Thread Level) ---
class AnalysisWorker(QThread):
    """Monitors the Process so the Main UI stays 100% responsive."""
    result_ready = pyqtSignal(str)

    def __init__(self, size):
        super().__init__()
        self.size = size

    def run(self):
        # Setup the inter-process communication
        result_queue = Queue()
        
        # Spawn the separate OS Process
        p = Process(target=heavy_data_crunch, args=(result_queue, self.size))
        p.start()
        
        # This line blocks the WORKER THREAD, but NOT the MAIN UI THREAD
        data = result_queue.get() 
        p.join()
        
        # Send data back to the UI
        self.result_ready.emit(data)

# --- 3. THE SECONDARY WINDOW ---
class StatsWindow(QDialog):
    """A popup window to display the statistical results."""
    def __init__(self, data):
        super().__init__()
        self.setWindowTitle("Detailed Analysis Report")
        self.resize(500, 400)
        
        layout = QVBoxLayout()
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setPlainText(data)
        # Use Monospace font for better table alignment
        self.text_area.setStyleSheet("font-family: 'Courier New'; font-size: 10pt;")
        
        layout.addWidget(self.text_area)
        self.setLayout(layout)

# --- 4. THE MAIN APPLICATION WINDOW ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt5 Multi-Process Analyzer")
        self.resize(400, 250)

        # UI Setup
        self.label = QLabel("Ready for Analysis")
        self.label.setAlignment(Qt.AlignCenter)
        self.btn = QPushButton("Start 1-Million Row Process")
        self.progress = QProgressBar()
        self.progress.hide()

        central_layout = QVBoxLayout()
        central_layout.addStretch()
        central_layout.addWidget(self.label)
        central_layout.addWidget(self.progress)
        central_layout.addWidget(self.btn)
        central_layout.addStretch()

        container = QWidget()
        container.setLayout(central_layout)
        self.setCentralWidget(container)

        self.btn.clicked.connect(self.launch_analysis)

    def launch_analysis(self):
        self.btn.setEnabled(False)
        self.progress.show()
        self.progress.setRange(0, 0) # Pulse animation
        self.label.setText("Calculating in separate process...\n(You can still move this window!)")

        # Create and start the thread-process bridge
        self.worker = AnalysisWorker(size=1000000)
        self.worker.result_ready.connect(self.handle_results)
        self.worker.start()

    def handle_results(self, result_text):
        self.btn.setEnabled(True)
        self.progress.hide()
        self.label.setText("Analysis Complete.")

        # Instantiate and show the second window
        # We save it to 'self' so the garbage collector doesn't kill it
        self.report_window = StatsWindow(result_text)
        self.report_window.show()

# --- 5. THE RUNTIME (Windows Safe) ---
if __name__ == "__main__":
    # REQUIRED: This prevents Windows from spawning infinite copies of the app
    multiprocessing.freeze_support()
    
    app = QApplication(sys.argv)
    
    # High-DPI Scaling Config
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
    main_win = MainWindow()
    main_win.show()
    
    sys.exit(app.exec_())