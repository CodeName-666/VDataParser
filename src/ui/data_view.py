# DataView.py

import sys
from PySide6.QtWidgets import QWidget, QApplication
from .generated import DataViewUi  # Annahme: In __init__.py wurde der UI-Code als DataViewUi bereitgestellt.
from .base_ui import BaseUi



class DataView(BaseUi):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = DataViewUi()
        # Aufbau der UI (erstellt alle Widgets und Layouts)
        self.ui.setupUi(self)
        # Zusätzliche Initialisierungen (Signal-Slot-Verbindungen etc.)
        self._setup_signals()

    def _setup_signals(self):
        """Verbindet die UI-Elemente mit der Funktionalität."""
        self.ui.btnToggleView.clicked.connect(self._toggle_view)
        # Hier können weitere Signal-Slot-Verbindungen erfolgen.

    def _toggle_view(self):
        """
        Schaltet zwischen der Baumansicht (treeUsers) und der Tabellenansicht (tableEntries) um.
        Dies ist nur ein Beispiel – je nach Anforderung kann die Funktionalität natürlich erweitert werden.
        """
        if self.ui.treeUsers.isVisible():
            self.ui.treeUsers.hide()
            self.ui.tableEntries.show()
        else:
            self.ui.treeUsers.show()
            self.ui.tableEntries.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DataView()
    window.show()
    sys.exit(app.exec())