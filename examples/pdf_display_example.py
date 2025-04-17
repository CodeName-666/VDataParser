
import sys
import os
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication
)
from PySide6.QtCore import Qt, Signal

sys.path.insert(0, Path(__file__).parent.parent.__str__())
from src.ui.pdf_display import PdfDisplay

# --- Entry Point ---
if __name__ == '__main__':
    # Set attribute for high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # --- Setup Main Window ---
    # Decide if PdfDisplay is the main window or a widget within one
    # Assuming BaseUi is QWidget and we need a QMainWindow container
    # from PySide6.QtWidgets import QMainWindow
    # window = QMainWindow()
    # pdf_display_widget = PdfDisplay()
    # window.setCentralWidget(pdf_display_widget)
    # window.setWindowTitle("PDF Editor") # Set title on main window
    # window.resize(1200, 800) # Set initial size
    # window.show()

    # --- OR If BaseUi IS the main window (e.g., inherits QMainWindow) ---
    window = PdfDisplay()
    window.setWindowTitle("PDF Editor") # Title might be set in load_pdf/load_state
    window.resize(1200, 800)
    window.show()
    # ---

    sys.exit(app.exec())