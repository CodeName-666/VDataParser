from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QStatusBar, QWidget, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Statusbar erstellen
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)

        # Links: Info-Label (Plain Text)
        self.info_label = QLabel("Bereit", self)
        self.status.addWidget(self.info_label)

        # Spacer: dehnt sich aus und schiebt folgende Widgets nach rechts
        spacer = QWidget(self)
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.status.addWidget(spacer)

        # Rechts: Verbindungsanzeige
        self.connection_label = QLabel("Verbindung: Inaktiv", self)
        self.status_led = QLabel(self)
        self.status_led.setFixedSize(12, 12)
        self.set_led_color("red")

        # Rechtsbündig hinzufügen
        self.status.addPermanentWidget(self.connection_label)
        self.status.addPermanentWidget(self.status_led)

        # Test: nach 3 Sekunden Verbindung simulieren
        QTimer.singleShot(3000, self.set_connected)

    def set_led_color(self, color: str):
        # Farbliche LED-Darstellung (kleiner Kreis)
        self.status_led.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border-radius: 6px;
                border: 1px solid black;
            }}
        """)

    def set_connected(self):
        self.connection_label.setText("Verbindung: Aktiv")
        self.set_led_color("green")
        self.info_label.setText("Verbindung hergestellt")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(500, 300)
    window.show()
    sys.exit(app.exec())
