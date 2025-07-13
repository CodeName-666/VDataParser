from PySide6.QtCore import QTimer, Slot
from PySide6.QtWidgets import QDialog

from display import OutputInterfaceAbstraction, BasicProgressTracker

from .base_ui import BaseUi
from .generated import OutputWindowUi


class OutputWindow(BaseUi, OutputInterfaceAbstraction):
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

        # References to progress bars
        self.primary_bar = self.ui.progressBar
        self.secondary_bar = self.ui.progressBar_2

        # Optional trackers assigned to the bars
        self._primary_tracker: BasicProgressTracker | None = None
        self._secondary_tracker: BasicProgressTracker | None = None

        # Timer used to poll tracker progress
        self._timer: QTimer | None = None

    # ------------------------------------------------------------------
    def write_message(self, message: str) -> None:
        """Append ``message`` to the output text edit."""
        self.ui.logOutputTextEdit.appendPlainText(message)

    # ------------------------------------------------------------------
    def _ensure_timer(self) -> None:
        """Create and start the update timer if necessary."""
        if self._timer is None:
            self._timer = QTimer(self)
            self._timer.setInterval(100)
            self._timer.timeout.connect(self._update_bars)
            self._timer.start()

    def _update_bars(self) -> None:
        """Update progress bars from assigned trackers."""
        if self._primary_tracker is not None:
            self.primary_bar.setValue(self._primary_tracker.percentage)
        if self._secondary_tracker is not None:
            self._secondary_tracker.setValue(self._secondary_tracker.percentage)
        if (
            (self._primary_tracker is None or self._primary_tracker.percentage >= 100)
            and (self._secondary_tracker is None or self._secondary_tracker.percentage >= 100)
            and self._timer is not None
        ):
            self._timer.stop()

    # ------------------------------------------------------------------
    def set_primary_tracker(self, tracker: BasicProgressTracker) -> None:
        """Assign ``tracker`` to the first progress bar."""
        self._primary_tracker = tracker
        self._ensure_timer()

    def set_secondary_tracker(self, tracker: BasicProgressTracker) -> None:
        """Assign ``tracker`` to the second progress bar."""
        self._secondary_tracker = tracker
        self._ensure_timer()

