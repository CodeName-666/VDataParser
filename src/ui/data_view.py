# DataView.py
from PySide6.QtWidgets import QWidget, QApplication
from generated import DataViewUi  # Annahme: In __init__.py wurde der UI-Code als DataViewUi bereitgestellt.
import sys

class DataView(QWidget, DataViewUi):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Aufbau der UI (erstellt alle Widgets und Layouts)
        self.setupUi(self)
        # Zusätzliche Initialisierungen (Signal-Slot-Verbindungen etc.)
        self._setup_signals()

    def _setup_signals(self):
        """Verbindet die UI-Elemente mit der Funktionalität."""
        self.btnToggleView.clicked.connect(self._toggle_view)
        # Hier können weitere Signal-Slot-Verbindungen erfolgen.

    def _toggle_view(self):
        """
        Schaltet zwischen der Baumansicht (treeUsers) und der Tabellenansicht (tableEntries) um.
        Dies ist nur ein Beispiel – je nach Anforderung kann die Funktionalität natürlich erweitert werden.
        """
        if self.treeUsers.isVisible():
            self.treeUsers.hide()
            self.tableEntries.show()
        else:
            self.treeUsers.show()
            self.tableEntries.hide()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DataView()
    window.show()
    sys.exit(app.exec())