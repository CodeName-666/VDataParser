from PySide6.QtWidgets import QApplication, QDialog, QFileDialog

from .base_ui import BaseUi
from .generated import OutputWindowUi


class OutputWindow(BaseUi):


    def __init__(self, parent: QDialog | None = None) -> None:
        super().__init__(parent)

        # ────────────────────────── UI aufbauen ───────────────────────────
        self.ui = OutputWindowUi()
        self.ui.setupUi(self)