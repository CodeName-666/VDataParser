

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStatusBar, QLabel, QHBoxLayout, QWidget, QSizePolicy, QSpacerItem
from PySide6.QtCore import QTimer





class StatusBar(QStatusBar):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("statusbar")
        self.setSizeGripEnabled(False)
        self.horizontalLayout = QHBoxLayout(self)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.info_label = QLabel(self)
        self.info_label.setObjectName(u"label")

        self.horizontalLayout.addWidget(self.info_label)

        self.horizontalSpacer = QSpacerItem(214, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.connection_label = QLabel(self)
        self.connection_label.setObjectName(u"label_2")

        self.horizontalLayout.addWidget(self.connection_label)

        self.status_led = QLabel(self)
        self.status_led.setObjectName(u"label_3")

        self.horizontalLayout.addWidget(self.status_led)

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