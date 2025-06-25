from PySide6.QtWidgets import QDialog

from .base_ui import BaseUi
from .generated import OutputWindowUi


class OutputWindow(BaseUi):
    """Simple dialog used to present generation results."""

    def __init__(self, parent: QDialog | None = None) -> None:
        """Create widgets and initialise the dialog.

        Parameters
        ----------
        parent:
            Optional parent dialog this window belongs to.
        """
        super().__init__(parent)
        self.ui = OutputWindowUi()
        self.ui.setupUi(self)
