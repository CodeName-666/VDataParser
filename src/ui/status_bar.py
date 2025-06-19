

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStatusBar, QLabel, QHBoxLayout, QWidget, QSizePolicy, QSpacerItem, QSizePolicy
from PySide6.QtCore import QTimer





class StatusBar(QStatusBar):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusbar")
        self.setSizeGripEnabled(True)


        self.info_label = QLabel()
        self.info_label.setText(u"Bereit")

        self.horizontalSpacer = QWidget()
        self.horizontalSpacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.connection_label = QLabel()
        self.connection_label.setText(u"Disconnected")

        self.status_led = QLabel()
        self.status_led.setFixedSize(12, 12)
        self.status_led.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.set_led_color("red")
        
        self.addWidget(self.info_label)
        self.addWidget(self.horizontalSpacer)
        self.addPermanentWidget(self.connection_label) 
        self.addPermanentWidget(self.status_led)
        
        QTimer.singleShot(3000, self.set_connected) 



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
        self.info_label.setText("Datenbank verbunden")