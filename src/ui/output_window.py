from PySide6.QtCore import QTimer, QThread, QMetaObject, Qt
from PySide6.QtWidgets import QDialog, QAbstractItemView, QPushButton

from display import (
    OutputInterfaceAbstraction,
    BasicProgressTracker,
    QtOutput,
)

from .generated import OutputWindowUi
from abc import ABCMeta


class _DialogABCMeta(type(QDialog), ABCMeta):
    """Combine Qt's dialog metaclass with :class:`ABCMeta`."""
    pass


class OutputWindow(QDialog, OutputInterfaceAbstraction, metaclass=_DialogABCMeta):
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

        self.close_button = QPushButton("Close", self)
        self.close_button.clicked.connect(self.close)
        self.ui.verticalLayout.addWidget(self.close_button)

        # Output interface implementation for the log list widget
        self._output = QtOutput(self.ui.logOutputList)
        self.ui.logOutputList.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # References to progress bars from the UI
        self.primary_bar = self.ui.progressBar
        self.secondary_bar = self.ui.progressBar_2

        # Optional trackers assigned to the bars
        self._primary_tracker: BasicProgressTracker | None = None
        self._secondary_tracker: BasicProgressTracker | None = None

        # Timer used to poll tracker progress
        self._timer: QTimer | None = None

    # ------------------------------------------------------------------
    def write_message(self, message: str) -> None:
        """Append ``message`` to the output list via :class:`QtOutput`."""
        self._output.write_message(message)

    # ------------------------------------------------------------------
    def _ensure_timer(self) -> None:
        """Create and start the update timer in the GUI thread if needed."""
        if QThread.currentThread() != self.thread():
            QMetaObject.invokeMethod(
                self,
                "_ensure_timer",
                Qt.ConnectionType.QueuedConnection,
            )
            return
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
            self.secondary_bar.setValue(self._secondary_tracker.percentage)
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

