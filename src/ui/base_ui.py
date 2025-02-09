
from PySide6.QtWidgets import QStackedWidget, QWidget




class BaseUi(QWidget): 


    def __init__(self, parent: QWidget = None):
        super().__init__(parent)

    def setup_ui(self):
        pass

    def propagate_signals(self):
        pass

    def setup_signals(self):
        pass
