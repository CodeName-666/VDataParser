
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
        self._setup_signals()

    def _propagate_signals(self):
        self.onExitButtonClickted = self.ui.exitButton.clicked

    def _setup_signals(self):
        
        self.onExitButtonClickted.connect(self.worked)

    def worked(self):
        print("Worked")


