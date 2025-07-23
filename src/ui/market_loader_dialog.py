"""market_loader_dialog.py
Dialog zum Laden eines Marktes, basierend auf dem *kompilierten* Qt‑Designer‑Code
(`market_loader_dialog_ui.py`, erzeugt z. B. mit `pyuic6`).

Vorteil: Keine XML‑Datei muss zur Laufzeit eingelesen werden – alles ist bereits
in Python gegossen.  Du kannst natürlich weiterhin im Designer arbeiten und bei
Änderungen einfach neu generieren lassen.
"""
from PySide6.QtWidgets import QApplication, QDialog, QFileDialog

from .base_ui import BaseUi
from .generated import MarketLoaderUi


class MarketLoaderDialog(QDialog):
    """Dialog, der zwei Lade‑Varianten bietet:

    * **JSON‑Projektdatei** (Pfad auswählen)
    * **Direkte MySQL‑Verbindung** (Host / Port / DB / User / Passwort)
    """

    def __init__(self, parent: QDialog | None = None) -> None:
        super().__init__(parent)

        # ────────────────────────── UI aufbauen ───────────────────────────
        self.ui = MarketLoaderUi()
        self.ui.setupUi(self)

        # ────────────────────────── Signale verbinden ─────────────────────
        self.ui.jsonRadio.toggled.connect(self._update_mode)
        self.ui.browseJsonBtn.clicked.connect(self._browse_json)
        self.ui.okBtn.clicked.connect(self.accept)
        self.ui.cancelBtn.clicked.connect(self.reject)

        # ────────────────────────── Initialer Zustand ─────────────────────
        self._update_mode()

    # ────────────────────────── Helferfunktionen ─────────────────────────
    def _browse_json(self) -> None:
        """Dateiauswahl‑Dialog für Projektdateien."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Projektdatei wählen", "", "Projektdateien (*.project)"
        )
        if path:
            self.ui.jsonPathEdit.setText(path)

    def _update_mode(self) -> None:
        """Aktiviert/Deaktiviert Eingabefelder je nach gewählter Option."""
        json_active = self.ui.jsonRadio.isChecked()

        # JSON‑Felder
        self.ui.jsonPathEdit.setEnabled(json_active)
        self.ui.browseJsonBtn.setEnabled(json_active)

        # MySQL‑Felder
        for w in (
            self.ui.hostEdit,
            self.ui.portEdit,
            self.ui.dbEdit,
            self.ui.userEdit,
            self.ui.pwEdit,
        ):
            w.setEnabled(not json_active)

    # ────────────────────────── Öffentliche API ──────────────────────────
    def get_result(self) -> dict:
        """Liest die aktuell eingegebenen Daten aus und liefert sie strukturiert."""
        if self.ui.jsonRadio.isChecked():
            return {
                "mode": "json",
                "path": self.ui.jsonPathEdit.text().strip(),
            }
        return {
            "mode": "mysql",
            "host": self.ui.hostEdit.text().strip(),
            "port": int(self.ui.portEdit.text() or 3306),
            "database": self.ui.dbEdit.text().strip(),
            "user": self.ui.userEdit.text().strip(),
            "password": self.ui.pwEdit.text(),
        }
