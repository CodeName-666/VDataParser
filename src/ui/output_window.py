from PySide6.QtWidgets import QDialog, QProgressBar, QWidget
from PySide6.QtCore import QTimer
from abc import ABCMeta

from display import OutputInterfaceAbstraction, BasicProgressTracker


class _WidgetABCMeta(type(QWidget), ABCMeta):
    """Combine Qt's widget metaclass with :class:`ABCMeta`."""
    pass

from .base_ui import BaseUi
from .generated import OutputWindowUi


class OutputWindow(BaseUi, OutputInterfaceAbstraction, metaclass=_WidgetABCMeta):
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
        self.progress_bar_1: QProgressBar = self.ui.progressBar
        self.progress_bar_2: QProgressBar = self.ui.progressBar_2
        self._tracker1: BasicProgressTracker | None = None
        self._tracker2: BasicProgressTracker | None = None
        self._timer: QTimer | None = None

    # ---------------------------------------------------------------
    # OutputInterfaceAbstraction implementation
    # ---------------------------------------------------------------
    def write_message(self, message: str) -> None:
        """Append ``message`` to the log output widget."""
        self.ui.logOutputTextEdit.appendPlainText(message)

    # ---------------------------------------------------------------
    # Progress handling
    # ---------------------------------------------------------------
    def _ensure_timer(self) -> None:
        """Create and start the update timer if necessary."""
        if self._timer is None:
            self._timer = QTimer(self)
            self._timer.setInterval(100)
            self._timer.timeout.connect(self._update_bars)
            self._timer.start()

    def _update_bars(self) -> None:
        """Update progress bars from assigned trackers."""
        if self._tracker1 is not None:
            self.progress_bar_1.setValue(self._tracker1.percentage)
        if self._tracker2 is not None:
            self.progress_bar_2.setValue(self._tracker2.percentage)
        if (
            (self._tracker1 is None or self._tracker1.percentage >= 100)
            and (self._tracker2 is None or self._tracker2.percentage >= 100)
            and self._timer is not None
        ):
            self._timer.stop()

    def set_primary_tracker(self, tracker: BasicProgressTracker) -> None:
        """Assign ``tracker`` to the first progress bar and start updates."""
        self._tracker1 = tracker
        self._ensure_timer()

    def set_secondary_tracker(self, tracker: BasicProgressTracker) -> None:
        """Assign ``tracker`` to the second progress bar and start updates."""
        self._tracker2 = tracker
        self._ensure_timer()
