import sys
import json
from PySide6.QtCore import QFile, Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTreeWidgetItem,
    QTableWidgetItem,
    QListWidget,
    QListWidgetItem
)
from PySide6.QtUiTools import QUiLoader
from src.data import BaseData

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Laden der .ui-Datei
        ui_file = QFile("src/test_code/main_window.ui")
        if not ui_file.open(QFile.ReadOnly):
            print("Kann die UI-Datei nicht öffnen")
            sys.exit(-1)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.setCentralWidget(self.ui.centralwidget)
        self.setWindowTitle("self.ui.windowTitle()")

        # JSON-Daten einlesen (z. B. aus export.json – dies entspricht Ihrem MySQL‑Export)
        self.data = BaseData("src/test_code/export.json")

        # Erzeugen Sie ein Dictionary zur schnellen Zuordnung der stnr‑Tabellen
        # Beispiel: "stnr1": [Einträge aus Tabelle stnr1], etc.
        self.stnr_tables = {}
        for main_number in self.data.get_main_number_list():
            table_name = f"stnr{main_number.id}"
            self.stnr_tables[table_name] = main_number.data

        # Gruppierung der Benutzer aus der "verkaeufer"-Tabelle (aggregierte Ansicht)
        # Hier werden Benutzer anhand ihrer E-Mail zusammengefasst.
        # Dabei werden alle in der Spalte "id" auftretenden Werte (bei Duplikaten) gesammelt.
        self.users = {}  # Schlüssel: E-Mail, Wert: { "info": erste Benutzerdaten, "ids": [alle IDs], "stamms": [] }
        for user in self.data.get_seller_list():
            key = user.email
            if key not in self.users:
                self.users[key] = {"info": user, "ids": [user.id], "stamms": []}
            else:
                if user.id not in self.users[key]["ids"]:
                    self.users[key]["ids"].append(user.id)

        # Ordnen Sie nun zu jedem Benutzer die zugehörigen stnr‑Tabellen zu,
        # wenn der Tabellenname (z. B. "stnr2") mit einer der gesammelten IDs übereinstimmt.
        for main_number in self.data.get_main_number_list():
            stnr_name = f"stnr{main_number.id}"
            for user in self.users.values():
                if str(main_number.id) in user["ids"]:
                    user["stamms"].append({
                        "stnr": stnr_name,
                        "entries": main_number.data
                    })

        # Zunächst wird die Baumansicht (aggregierte Ansicht) gefüllt.
        self.populate_user_tree()

        # Erstellen Sie nun zusätzlich eine flache Listenansicht (QListWidget) und fügen Sie diese in
        # das linke Layout (verticalLayoutLeft) hinzu – diese wird anfangs versteckt.
        self.listUsers = QListWidget()
        self.ui.verticalLayoutLeft.addWidget(self.listUsers)
        self.listUsers.hide()
        self.listUsers.itemClicked.connect(self.user_list_item_clicked)

        # Verbinden Sie den Toggle-Button, um zwischen den beiden Ansichten umzuschalten.
        self.ui.btnToggleView.clicked.connect(self.toggle_view)

        # Verbinden Sie das Klicken in der Baumansicht.
        self.ui.treeUsers.itemClicked.connect(self.user_item_clicked)

    def populate_user_tree(self):
        """Füllt das QTreeWidget (aggregierte Ansicht) mit den Benutzern und ihren zugehörigen stnr‑Tabellen."""
        self.ui.treeUsers.clear()
        for key, user in self.users.items():
            # Anzeige-Text z. B.: "Max Mustermann (max@mustermann.de)"
            user_text = f'{user["info"].vorname} {user["info"].nachname} ({user["info"].email})'
            user_item = QTreeWidgetItem([user_text])
            # Füge untergeordnete Kindelemente hinzu, die die zugehörigen stnr‑Tabellen anzeigen.
            for stamm in user["stamms"]:
                child = QTreeWidgetItem([stamm["stnr"]])
                user_item.addChild(child)
            self.ui.treeUsers.addTopLevelItem(user_item)

    def populate_user_list(self):
        """Füllt das QListWidget (flache Listenansicht) mit allen Benutzereinträgen aus der 'verkaeufer'-Tabelle."""
        self.listUsers.clear()
        flat_users = self.data.get_seller_list()
        for index, user in enumerate(flat_users, start=1):
            # Nummerierung und Anzeige-Text z. B.: "1. Sabrina Willkomm (sabimi@gmail.com)"
            text = f'{index}. {user.vorname} {user.nachname} ({user.email})'
            item = QListWidgetItem(text)
            # Speichern Sie das komplette Benutzer-Dictionary im Item (über UserRole)
            item.setData(Qt.UserRole, user)
            self.listUsers.addItem(item)

    def toggle_view(self):
        """Schaltet zwischen der Baumansicht (aggregiert) und der Listenansicht (flach) um."""
        if self.ui.treeUsers.isVisible():
            # Wechsel zur Listenansicht
            self.ui.treeUsers.hide()
            self.populate_user_list()
            self.listUsers.show()
            self.ui.btnToggleView.setText("Baumansicht")
        else:
            # Wechsel zurück zur Baumansicht
            self.listUsers.hide()
            self.ui.treeUsers.show()
            self.ui.btnToggleView.setText("Listenansicht")

    def user_item_clicked(self, item, column):
        """
        Beim Klick in der Baumansicht:
        - Wird, wenn ein Kindelement (stnr) geklickt wird, nur die zugehörige stnr-Tabelle geladen.
        - Wird der Benutzerknoten geklickt, können alle zugehörigen stnr-Einträge zusammengefasst werden.
        """
        if item.parent() is not None:
            # Es wurde ein stnr-Kindelement angeklickt.
            stnr_name = item.text(0)
            entries = None
            for user in self.users.values():
                for stamm in user["stamms"]:
                    if stamm["stnr"] == stnr_name:
                        entries = stamm["entries"]
                        break
                if entries is not None:
                    break
        else:
            # Es wurde ein Benutzerknoten angeklickt – hier werden alle zugehörigen stnr-Einträge zusammengefasst.
            entries = []
            user_text = item.text(0)
            for user in self.users.values():
                info_text = f'{user["info"].vorname} {user["info"].nachname} ({user["info"].email})'
                if info_text == user_text:
                    for stamm in user["stamms"]:
                        entries.extend(stamm["entries"])
                    break
        self.populate_entry_table(entries)

    def user_list_item_clicked(self, item):
        """
        Beim Klick in der flachen Listenansicht:
        Wird der Benutzer aus dem Item ausgelesen und anhand seiner ID die zugehörige stnr-Tabelle geladen.
        """
        user = item.data(Qt.UserRole)
        target_stnr = f"stnr{user.id}"
        entries = self.stnr_tables.get(target_stnr, [])
        self.populate_entry_table(entries)

    def populate_entry_table(self, entries):
        """Befüllt das QTableWidget im rechten Bereich mit den Detail-Einträgen."""
        self.ui.tableEntries.clearContents()
        if not entries:
            self.ui.tableEntries.setRowCount(0)
            return
        self.ui.tableEntries.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            self.ui.tableEntries.setItem(row, 0, QTableWidgetItem(entry.get("artikelnummer", "")))
            self.ui.tableEntries.setItem(row, 1, QTableWidgetItem(entry.get("beschreibung", "")))
            self.ui.tableEntries.setItem(row, 2, QTableWidgetItem(entry.get("groesse", "")))
            self.ui.tableEntries.setItem(row, 3, QTableWidgetItem(entry.get("preis", "")))
            self.ui.tableEntries.setItem(row, 4, QTableWidgetItem(entry.get("created_at", "")))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
