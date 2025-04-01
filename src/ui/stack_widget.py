from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QStackedWidget, QWidget







class StackWidget(QStackedWidget):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.last_index = []


    def backup_last_index(self):
        self.last_index.append(self.currentIndex()) 

    @Slot()
    def restore_last_index(self):
        if len(self.last_index) > 0:
            self.setCurrentIndex(self.last_index.pop())
        else:
            self.setCurrentIndex(0)

    def get_last_index(self):
        return self.last_index[-1] if len(self.last_index) > 0 else 0