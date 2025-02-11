from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStackedWidget, QWidget






class StackWidget(QStackedWidget):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.widget_list: list[str] = []

   