"""Dialog to select a database from a list."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog

from .generated import DatabaseSelectionDialogUi


class DatabaseSelectionDialog(QDialog):
    """Present a list of database names and return the chosen one.

    Parameters
    ----------
    databases:
        Names of available databases shown in the list.
    parent:
        Optional parent widget.
    """

    def __init__(self, databases: list[str], parent: QDialog | None = None) -> None:
        super().__init__(parent)

        self.ui = DatabaseSelectionDialogUi()
        self.ui.setupUi(self)
        self.ui.databaseList.addItems(databases)
        if databases:
            self.ui.databaseList.setCurrentRow(0)

        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def get_selection(self) -> str | None:
        """Return the currently selected database name if dialog accepted.

        Returns
        -------
        str | None
            Selected database name or ``None`` when no selection was made or the dialog was
            cancelled.
        """
        if self.result() != QDialog.DialogCode.Accepted:
            return None
        item = self.ui.databaseList.currentItem()
        return item.text() if item else None
