#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Beispiel einer PySide6 UI zur Konfiguration der Flohmarkt‑Parameter.
Die UI ermöglicht es, entweder einen Verkaufsmarkt anzupassen oder einen neuen zu erstellen.
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QSpinBox, QDateTimeEdit, QCheckBox, QPushButton, QLabel,
    QRadioButton, QGroupBox
)
from PySide6.QtCore import QDateTime, Qt

class MarketConfigDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Markt-Konfiguration")
        self.resize(450, 500)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout(self)

        # Überschrift
        title_label = QLabel("<h2>Markt-Konfiguration</h2>")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Modus-Auswahl: Markt anpassen oder neu erstellen
        mode_groupbox = QGroupBox("Modus")
        mode_layout = QHBoxLayout()
        self.radio_edit = QRadioButton("Verkaufsmarkt anpassen")
        self.radio_new = QRadioButton("Neuen Verkaufsmarkt erstellen")
        # Standardmäßig neuen Markt erstellen
        self.radio_new.setChecked(True)
        mode_layout.addWidget(self.radio_edit)
        mode_layout.addWidget(self.radio_new)
        mode_groupbox.setLayout(mode_layout)
        main_layout.addWidget(mode_groupbox)

        # Formular für die Parameter
        form_layout = QFormLayout()

        # MAX_STAMMNUMMERN (Ganzzahl)
        self.spin_max_stammnummer = QSpinBox()
        self.spin_max_stammnummer.setRange(1, 10000)
        self.spin_max_stammnummer.setValue(250)
        form_layout.addRow("Max. Stammnummern:", self.spin_max_stammnummer)

        # MAX_ARTIKEL (Ganzzahl)
        self.spin_max_artikel = QSpinBox()
        self.spin_max_artikel.setRange(1, 1000)
        self.spin_max_artikel.setValue(40)
        form_layout.addRow("Max. Artikel:", self.spin_max_artikel)

        # FLOHMARKT_DATUM (Datum & Zeit)
        self.date_edit_flohmarkt = QDateTimeEdit()
        self.date_edit_flohmarkt.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        # Datum aus dem String "March 15, 2025 12:00:00" parsen
        dt = QDateTime.fromString("March 15, 2025 12:00:00", "MMMM d, yyyy HH:mm:ss")
        if not dt.isValid():
            dt = QDateTime.currentDateTime()
        self.date_edit_flohmarkt.setDateTime(dt)
        form_layout.addRow("Flohmarkt Datum:", self.date_edit_flohmarkt)

        # FLOHMARKT (Text)
        self.line_flohmarkt = QLineEdit("Sept. 24")
        form_layout.addRow("Flohmarkt:", self.line_flohmarkt)

        # FLOHMARKTNUMMER (Ganzzahl)
        self.spin_flohmarkt_nummer = QSpinBox()
        self.spin_flohmarkt_nummer.setRange(1, 100)
        self.spin_flohmarkt_nummer.setValue(5)
        form_layout.addRow("Flohmarkt Nummer:", self.spin_flohmarkt_nummer)

        # PW_LENGTH (Ganzzahl)
        self.spin_pw_length = QSpinBox()
        self.spin_pw_length.setRange(1, 50)
        self.spin_pw_length.setValue(10)
        form_layout.addRow("Passwortlänge:", self.spin_pw_length)

        # TABELLE_PREFIX (Text)
        self.line_tabelle_prefix = QLineEdit("stnr")
        form_layout.addRow("Tabellen-Prefix:", self.line_tabelle_prefix)

        # TABELLE_VERKAEUFER (Text)
        self.line_tabelle_verkaeufer = QLineEdit("verkaeufer")
        form_layout.addRow("Tabelle Verkäufer:", self.line_tabelle_verkaeufer)

        # MAXIDPERUSER (Ganzzahl)
        self.spin_max_id_per_user = QSpinBox()
        self.spin_max_id_per_user.setRange(1, 100)
        self.spin_max_id_per_user.setValue(8)
        form_layout.addRow("Max. ID pro User:", self.spin_max_id_per_user)

        # LOGIN_DISABLE (Boolesch)
        self.checkbox_login_disable = QCheckBox("Login deaktivieren")
        self.checkbox_login_disable.setChecked(False)
        form_layout.addRow(self.checkbox_login_disable)

        main_layout.addLayout(form_layout)

        # Buttons: Speichern und Abbrechen
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.button_save = QPushButton("Speichern")
        self.button_cancel = QPushButton("Abbrechen")
        button_layout.addWidget(self.button_save)
        button_layout.addWidget(self.button_cancel)
        main_layout.addLayout(button_layout)

        # Signal-Verbindungen
        self.button_cancel.clicked.connect(self.reject)
        self.button_save.clicked.connect(self.accept)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = MarketConfigDialog()
    if dialog.exec():
        # Bei Bestätigung können hier die Werte weiterverarbeitet werden.
        modus = "Anpassen" if dialog.radio_edit.isChecked() else "Neu erstellen"
        print("Modus:", modus)
        print("Max. Stammnummern:", dialog.spin_max_stammnummer.value())
        print("Max. Artikel:", dialog.spin_max_artikel.value())
        print("Flohmarkt Datum:", dialog.date_edit_flohmarkt.dateTime().toString("yyyy-MM-dd HH:mm:ss"))
        print("Flohmarkt:", dialog.line_flohmarkt.text())
        print("Flohmarkt Nummer:", dialog.spin_flohmarkt_nummer.value())
        print("Passwortlänge:", dialog.spin_pw_length.value())
        print("Tabellen-Prefix:", dialog.line_tabelle_prefix.text())
        print("Tabelle Verkäufer:", dialog.line_tabelle_verkaeufer.text())
        print("Max. ID pro User:", dialog.spin_max_id_per_user.value())
        print("Login deaktivieren:", dialog.checkbox_login_disable.isChecked())
    sys.exit(0)
