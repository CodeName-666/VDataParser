from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtWidgets import QStatusBar, QLabel, QWidget, QSizePolicy


class StatusBar(QStatusBar):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusbar") 
        self.setSizeGripEnabled(True)

        # Info-Label für Statusnachrichten
        self.info_label = QLabel()
        self.info_label.setText("")  # Leer initial
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Platzhalter, um Widgets auseinander zu schieben
        self.horizontalSpacer = QWidget()
        self.horizontalSpacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Connection Label und LED
        self.connection_label = QLabel()
        self.connection_label.setText("Disconnected")

        self.status_led = QLabel()
        self.status_led.setFixedSize(12, 12)
        self.status_led.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.set_led_color("red")

        # Widgets zur StatusBar hinzufügen
        self.addWidget(self.info_label)
        self.addWidget(self.horizontalSpacer)
        self.addPermanentWidget(self.connection_label)
        self.addPermanentWidget(self.status_led)

        # Verantwortlich für Datenbank-Status (nur Beispiel)
        QTimer.singleShot(3000, self.set_connected)

        # Queue und Timer für sequentielle Anzeige von Nachrichten
        self._message_queue = []
        self._message_timer = QTimer(self)
        self._message_timer.setSingleShot(True)
        self._message_timer.timeout.connect(self._show_next_message)

    def set_led_color(self, color):
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
        # Beispiel-Nachricht bei Verbindung
        self.post_message("Datenbank verbunden")

    @Slot(str)
    def post_message(self, message: str):
        """
        Slot zum Hinzufügen einer neuen Statusnachricht.
        Nachricht wird in die Queue gestellt und nacheinander 3 Sekunden angezeigt.
        """
        self._message_queue.append(message)
        # Wenn gerade keine Nachricht angezeigt wird, sofort starten
        if not self._message_timer.isActive():
            self._show_next_message()

    def _show_next_message(self):
        if self._message_queue:
            text = self._message_queue.pop(0)
            self.info_label.setText(text)
            # Timer für 3 Sekunden bis zur nächsten Nachricht
            self._message_timer.start(3000)
        else:
            # Alle Nachrichten angezeigt -> Label leeren
            self.info_label.setText("")
