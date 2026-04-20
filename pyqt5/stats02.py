import sys
import time
import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel

# 1. The Worker Class (The "Kitchen")
class StatsWorker(QThread):
    # This signal sends the result (a string or a dataframe) back to the UI
    finished_signal = pyqtSignal(str)

    def run(self):
        # SIMULATE HEAVY STATS WORK
        # In reality, this would be: df = pd.read_csv(...)
        time.sleep(5) 
        result = "Analysis Complete: Mean = 42.0"
        
        # Send the result back to the main thread
        self.finished_signal.emit(result)

# 2. The UI Class (The "Front Desk")
class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stats Tool")
        
        self.label = QLabel("Waiting for data...")
        self.btn = QPushButton("Start Heavy Analysis")
        self.btn.clicked.connect(self.start_analysis)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_analysis(self):
        self.label.setText("Processing... (Window is still responsive!)")
        self.btn.setEnabled(False) # Prevent double clicking

        # 3. Start the Thread
        self.worker = StatsWorker()
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, result):
        # This runs in the Main Thread when the signal is received
        self.label.setText(result)
        self.btn.setEnabled(True)

app = QApplication(sys.argv)
win = MyApp()
win.show()
sys.exit(app.exec_())