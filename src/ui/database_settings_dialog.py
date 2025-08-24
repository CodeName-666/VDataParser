"""Dialog to edit database connection settings."""

from __future__ import annotations

from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
)

from data import MarketConfigHandler


class DatabaseSettingsDialog(QDialog):
    """Collect and return database connection parameters.

    The dialog provides line edits for host, port, database name, user and
    password.  Existing values are taken from :class:`MarketConfigHandler` to
    give the user a starting point.
    """

    def __init__(self, parent: QDialog | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Datenbankeinstellungen")

        self._host_edit = QLineEdit(self)
        self._port_edit = QLineEdit(self)
        self._port_edit.setValidator(QIntValidator(1, 65535, self))
        self._name_edit = QLineEdit(self)
        self._user_edit = QLineEdit(self)
        self._password_edit = QLineEdit(self)
        self._password_edit.setEchoMode(QLineEdit.EchoMode.Password)

        try:
            db_cfg = MarketConfigHandler().get_database()
        except Exception:
            db_cfg = {}
        self._host_edit.setText(db_cfg.get("url", ""))
        self._port_edit.setText(db_cfg.get("port", ""))
        self._name_edit.setText(db_cfg.get("name", ""))
        self._user_edit.setText(db_cfg.get("user", ""))

        form = QFormLayout(self)
        form.addRow("Host", self._host_edit)
        form.addRow("Port", self._port_edit)
        form.addRow("DB-Name", self._name_edit)
        form.addRow("Benutzer", self._user_edit)
        form.addRow("Passwort", self._password_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addWidget(buttons)

    def get_values(self) -> tuple[str, str, str, str, str]:
        """Return entered connection parameters."""
        return (
            self._host_edit.text().strip(),
            self._port_edit.text().strip(),
            self._name_edit.text().strip(),
            self._user_edit.text().strip(),
            self._password_edit.text(),
        )
