import sys
from pathlib import Path	
from PySide6.QtCore import QFile, Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTreeWidgetItem, QTableWidgetItem, QListWidget, QListWidgetItem
)
from PySide6.QtUiTools import QUiLoader

sys.path.insert(0, Path(__file__).parent.parent.parent.parent.__str__())  # NOQA: E402 pylint: disable=[C0413]

from data.data_manager import DataManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_ui()

        # Initialisiere den DataManager (der von BaseData erbt)
        self.data_manager = DataManager("src/test_code/export.json")
        # Aggregierte Verkäufer (users) und stnr‑Tabellen aus dem DataManager abrufen
        self.users = self.data_manager.get_aggregated_users()
        self.stnr_tables = self.data_manager.get_main_number_tables()

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
        """Initialisiert die Ansichten (Baum- und Listenansicht)."""
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
        """
        Befüllt die Baumansicht mit aggregierten Verkäufern und ihren zugehörigen
        MainNumber-Tabellen (stnr‑Tabellen). Jeder Verkäufer wird über seine E‑Mail
        aggregiert und als Knoten dargestellt.
        """
        self.ui.treeUsers.clear()
        for email, user in self.users.items():
            user_text = f'{user["info"].vorname} {user["info"].nachname} ({user["info"].email})'
            user_item = QTreeWidgetItem([user_text])
            # Füge als untergeordnete Elemente die zugehörigen MainNumber-Tabellen hinzu.
            for main_number in user["stamms"]:
                child = QTreeWidgetItem([main_number.name])
                user_item.addChild(child)
            self.ui.treeUsers.addTopLevelItem(user_item)

    def populate_user_list(self):
        """
        Befüllt die flache Listenansicht mit allen Verkäufern aus der
        SellerListDataClass (databaseseitig gespeichert in data_manager.sellers.data).
        """
        self.listUsers.clear()
        flat_users = self.data_manager.sellers.data
        for index, seller in enumerate(flat_users, start=1):
            text = f'{index}. {seller.vorname} {seller.nachname} ({seller.email})'
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, seller)
            self.listUsers.addItem(item)

    def toggle_view(self):
        """Wechselt zwischen der Baumansicht (aggregiert) und der Listenansicht (flach)."""
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
        Reagiert auf Klicks in der Baumansicht.
        - Wird ein Kindknoten (stnr‑Tabelle) angeklickt, werden nur dessen Artikel angezeigt.
        - Wird ein Verkäuferknoten angeklickt, werden alle zugehörigen Artikel (aus allen stnr‑Tabellen)
          zusammengefasst.
        """
        if item.parent() is not None:
            # Kindelement (stnr‑Tabelle) wurde angeklickt.
            stnr_name = item.text(0)
            entries = None
            for user in self.users.values():
                for main_number in user["stamms"]:
                    if main_number.name == stnr_name:
                        entries = main_number.data
                        break
                if entries is not None:
                    break
        else:
            # Verkäuferknoten wurde angeklickt: Alle zugehörigen Artikel zusammenfassen.
            entries = []
            user_text = item.text(0)
            for user in self.users.values():
                info_text = f'{user["info"].vorname} {user["info"].nachname} ({user["info"].email})'
                if info_text == user_text:
                    for main_number in user["stamms"]:
                        entries.extend(main_number.data)
                    break
        self.populate_entry_table(entries)

    def user_list_item_clicked(self, item):
        """
        Reagiert auf Klicks in der flachen Listenansicht:
        Anhand der Verkäufer-ID wird die zugehörige stnr‑Tabelle ermittelt und
        deren Artikel angezeigt.
        """
        seller = item.data(Qt.UserRole)
        target_stnr = "stnr" + seller.id
        main_number = self.stnr_tables.get(target_stnr)
        entries = main_number.data if main_number else []
        self.populate_entry_table(entries)

    def populate_entry_table(self, entries):
        """
        Befüllt das Tabellen-Widget mit den Detail-Artikeln.
        Dabei wird auf die Artikelattribute (aus ArticleDataClass) über Attribute zugegriffen.
        """
        self.ui.tableEntries.clearContents()
        if not entries:
            self.ui.tableEntries.setRowCount(0)
            return
        self.ui.tableEntries.setRowCount(len(entries))
        for row, entry in enumerate(entries):
            self.ui.tableEntries.setItem(row, 0, QTableWidgetItem(getattr(entry, "artikelnummer", "")))
            self.ui.tableEntries.setItem(row, 1, QTableWidgetItem(getattr(entry, "beschreibung", "")))
            self.ui.tableEntries.setItem(row, 2, QTableWidgetItem(getattr(entry, "groesse", "")))
            self.ui.tableEntries.setItem(row, 3, QTableWidgetItem(getattr(entry, "preis", "")))
            self.ui.tableEntries.setItem(row, 4, QTableWidgetItem(getattr(entry, "created_at", "")))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
