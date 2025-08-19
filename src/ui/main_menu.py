
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget
from .generated import MainMenuUi
from .base_ui import BaseUi


class MainMenu(BaseUi):
    """Front page menu of the application."""

    on_exit_button_clicked: Signal = None
    on_open_export_button_clicked: Signal = None
    on_open_market_button_clicked: Signal = None
    on_new_market_button_clicked: Signal = None

    def __init__(self, parent: QWidget | None = None) -> None:
        """Instantiate and set up the UI.

        Parameters
        ----------
        parent:
            Optional parent widget used for Qt ownership.
        """
        super().__init__(parent)
        self.ui = MainMenuUi()
        self.setup_ui()

    def setup_ui(self) -> None:
        """Populate widgets and connect signals."""
        self.ui.setupUi(self)
        self.setup_signals()

    def setup_signals(self) -> None:
        """Expose signals from the embedded UI widgets."""
        self.on_exit_button_clicked = self.ui.exitButton.clicked
        self.on_open_export_button_clicked = self.ui.exportButton.clicked
        self.on_open_market_button_clicked = self.ui.loadButton.clicked
        # New market button
        if hasattr(self.ui, "newButton"):
            self.on_new_market_button_clicked = self.ui.newButton.clicked
