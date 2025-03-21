import sys
from pathlib import Path
from PySide6.QtCore import QFile, Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTreeWidgetItem, QTableWidgetItem, QListWidget, QListWidgetItem
)
from PySide6.QtUiTools import QUiLoader

sys.path.insert(0, Path(__file__).parent.parent.parent.parent.__str__())  # NOQA: E402 pylint: disable=[C0413]
from src.test_code.MainWindow.data_manager import DataManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()
        
        # Initialisiere den Data Manager
        self.data_manager = DataManager("src/test_code/export.json")
        self.users = self.data_manager.get_users()
        self.stnr_tables = self.data_manager.get_stnr_tables()

        self.setup_views()
        self.setup_connections()

    def load_ui(self):
        """Lädt die UI-Datei und richtet das zentrale Widget ein."""
        ui_file = QFile("src/test_code/MainWindow/main_window.ui")
        if not ui_file.open(QFile.ReadOnly):
            print("Kann die UI-Datei nicht öffnen")
            sys.exit(-1)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setCentralWidget(self.ui.centralwidget)
        self.setWindowTitle("Meine Anwendung")

    def setup_views(self):
        """Initialisiert die Views (Baum- und Listenansicht)."""
        self.populate_user_tree()
        self.listUsers = QListWidget()
        self.ui.verticalLayoutLeft.addWidget(self.listUsers)
        self.listUsers.hide()

    def setup_connections(self):
        """Verbindet UI-Elemente mit ihren Event-Handlern."""
        self.ui.btnToggleView.clicked.connect(self.toggle_view)
        self.ui.treeUsers.itemClicked.connect(self.user_item_clicked)
        self.listUsers.itemClicked.connect(self.user_list_item_clicked)

    def populate_user_tree(self):
        """Befüllt die Baumansicht mit aggregierten Benutzerinformationen."""
        self.ui.treeUsers.clear()
        for key, user in self.users.items():
            user_text = f'{user["info"]["vorname"]} {user["info"]["nachname"]} ({user["info"]["email"]})'
            user_item = QTreeWidgetItem([user_text])
            for stamm in user["stamms"]:
                child = QTreeWidgetItem([stamm["stnr"]])
                user_item.addChild(child)
            self.ui.treeUsers.addTopLevelItem(user_item)

    def populate_user_list(self):
        """Befüllt die Listenansicht mit flachen Benutzerinformationen."""
        self.listUsers.clear()
        flat_users = self.data_manager.get_flat_users()
        for index, user in enumerate(flat_users, start=1):
            text = f'{index}. {user["vorname"]} {user["nachname"]} ({user["email"]})'
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, user)
            self.listUsers.addItem(item)

    def toggle_view(self):
        """Wechselt zwischen Baum- und Listenansicht."""
        if self.ui.treeUsers.isVisible():
            self.ui.treeUsers.hide()
            self.populate_user_list()
            self.listUsers.show()
            self.ui.btnToggleView.setText("Baumansicht")
        else:
            self.listUsers.hide()
            self.ui.treeUsers.show()
            self.ui.btnToggleView.setText("Listenansicht")

    def user_item_clicked(self, item, column):
        """
        Handler für Klicks in der Baumansicht.
        
        - Bei Klick auf ein Kind (stnr) wird nur die zugehörige Tabelle geladen.
        - Bei Klick auf einen Benutzerknoten werden alle zugehörigen stnr‑Einträge zusammengefasst.
        """
        if item.parent() is not None:
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
            entries = []
            user_text = item.text(0)
            for user in self.users.values():
                info_text = f'{user["info"]["vorname"]} {user["info"]["nachname"]} ({user["info"]["email"]})'
                if info_text == user_text:
                    for stamm in user["stamms"]:
                        entries.extend(stamm["entries"])
                    break
        self.populate_entry_table(entries)

    def user_list_item_clicked(self, item):
        """
        Handler für Klicks in der Listenansicht.
        
        Hier wird anhand der Benutzer-ID die zugehörige stnr‑Tabelle ermittelt.
        """
        user = item.data(Qt.UserRole)
        target_stnr = "stnr" + user["id"]
        entries = self.stnr_tables.get(target_stnr, [])
        self.populate_entry_table(entries)

    def populate_entry_table(self, entries):
        """Befüllt das Tabellen-Widget mit den Detail-Einträgen."""
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
