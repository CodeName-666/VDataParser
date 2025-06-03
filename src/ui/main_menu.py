
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget
from .generated import MainMenuUi
from .base_ui import BaseUi

class MainMenu(BaseUi):


    on_exit_button_clicked: Signal = None
    on_open_export_button_clicked: Signal = None
    on_open_market_button_clicked: Signal = None

    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = MainMenuUi()
        self.setup_ui()
            
    def setup_ui(self): 
        self.ui.setupUi(self)
        self.setup_signals()


    def setup_signals(self):        
        self.on_exit_button_clicked: Signal = self.ui.exitButton.clicked
        self.on_open_export_button_clicked: Signal = self.ui.exportButton.clicked
        self.on_open_market_button_clicked: Signal = self.ui.loadButton.clicked
        



