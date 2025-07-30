from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QStackedWidget, QWidget


class StackWidget(QStackedWidget):
    """QStackedWidget extension that keeps track of navigation history."""

    def __init__(self, parent: QWidget | None = None) -> None:
        """Create a new stack widget.

        Parameters
        ----------
        parent:
            Optional Qt parent widget.
        """
        super().__init__(parent)
        self.last_index: list[int] = []

    def backup_last_index(self) -> None:
        """Store the currently active index on a stack."""
        self.last_index.append(self.currentIndex())

    @Slot()
    def restore_last_index(self) -> None:
        """Restore the previously saved index or fall back to ``0``."""
        if self.last_index:
            self.setCurrentIndex(self.last_index.pop())
        else:
            self.setCurrentIndex(0)

    def get_last_index(self) -> int:
        """Return the last stored index or ``0`` if none available."""
        return self.last_index[-1] if self.last_index else 0
