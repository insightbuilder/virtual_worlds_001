# Master Notes: PyQt5 Architecture for Statistical Engineering

## 1. The Core Philosophy: The Trinity of a GUI App
A professional PyQt5 application is divided into three distinct layers. Understanding these is the difference between a "script" and a "software product."

### A. The Engine (QApplication)
* **Technical Role:** The `QApplication` is a **Singleton** that manages the GUI control flow and main settings. It initializes the connection between your code and the OS Window Manager (GDI+ on Windows or X11/Wayland on Linux).
* **The Event Loop:** When you call `app.exec_()`, you start an infinite `while` loop. This loop listens for "Events" (mouse clicks, key presses, window paints).
* **The Logic:** You must create the `QApplication` *before* any UI widgets. Without it, the widgets have no "host" to draw pixels.

### B. The Body (QMainWindow)
* **Technical Role:** The framework for the user interface. Unlike a simple `QWidget`, a `QMainWindow` comes with built-in support for a **Menu Bar**, **Toolbars**, **Dock Widgets**, and a **Status Bar**.
* **Central Widget:** Everything in a statistical app (the charts/tables) must be set as the "Central Widget" using `self.setCentralWidget()`.

### C. The Brain (The Logic Layer)
* **Technical Role:** This is where Pandas and Matplotlib live. In a professional setup (like Orange3), this logic is decoupled from the UI classes to allow for automated testing.

---

## 2. Managing Concurrency: Threads vs. Processes
In statistical software, you must never block the "Main Thread" (the UI thread). If the Main Thread waits for a calculation, the window freezes.

### QThread (The Worker)
* **Purpose:** Ideal for I/O bound tasks like downloading a 500MB CSV from GitHub or reading a database.
* **Communication:** Uses **Signals and Slots**.
    * *Worker Signal:* `data_ready = pyqtSignal(pd.DataFrame)`
    * *UI Slot:* `self.worker.data_ready.connect(self.update_chart)`
* **The Golden Rule:** Never touch a GUI widget (like `label.setText`) inside the `run()` method of a `QThread`. It will cause a segmentation fault. Always emit a signal back to the Main Thread.

### QProcess / Multiprocessing
* **Purpose:** Essential for CPU-bound statistical modeling (e.g., Random Forest training).
* **Benefit:** If the calculation hits a "Memory Error" or crashes, the GUI remains alive because the crash happened in a separate OS process.

---

## 3. Layout Management & High-DPI Fixes
PyQt5 uses "Layout Managers" instead of absolute positioning to ensure windows look good when resized.

| Layout | Use Case |
| :--- | :--- |
| **QVBoxLayout** | Stacking elements vertically (e.g., Chart on top, Button on bottom). |
| **QHBoxLayout** | Aligning elements horizontally (e.g., a row of filter buttons). |
| **QGridLayout** | Creating a dashboard of multiple charts. |
| **QStackedWidget** | Creating "Pages" (e.g., moving from a 'Data Upload' page to an 'Analysis' page). |

### The "Magical" High-DPI Setup
Add this to your entry point to fix blurry text on 4K monitors:
```python
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

### Installation

pip install PyQt5 pandas matplotlib

After above completes

pip install PyQtChart
