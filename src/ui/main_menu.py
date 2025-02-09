
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget
from .generated import MainMenuUi
from .base_ui import BaseUi

class MainMenu(BaseUi):


    onExitButtonClickted: Signal = None

    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = MainMenuUi()
        self.ui.setupUi(self)
        self.propagate_signals()
        self.setup_signals()
       
    def propagate_signals(self):
        self.on_exit_button_clicked = self.ui.exitButton.clicked

    def setup_signals(self):        
        self.on_exit_button_clicked.connect(self.worked)

    def worked(self):
        print("Worked")


