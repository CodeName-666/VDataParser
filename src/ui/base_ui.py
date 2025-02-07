
from PySide6.QtWidgets import QStackedWidget, QWidget




class BaseUi(QWidget): 


    def __init__(self, parent: QStackedWidget = None):
        super().__init__(parent)

