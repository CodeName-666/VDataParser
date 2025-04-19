import sys
from pathlib import Path
from PySide6.QtCore import QFile, Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTreeWidgetItem,
    QTableWidgetItem,
    QListWidget,
    QListWidgetItem,
    QWidget,
    QVBoxLayout,
    QLabel
)
from PySide6.QtUiTools import QUiLoader

# Erlaube den Import aus übergeordneten Verzeichnissen
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.data import BaseData


class UserListItemWidget(QWidget):
    """
    Benutzerdefiniertes Widget für die flache Listenansicht.
    Es zeigt oben die Benutzerinformationen und darunter alle zugeordneten Stammnummern.
    Beispiel:
        Klaus (klaus@example.com)
        Stammnummern: -1, -44
    """
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        info = user_data["info"]
        # Anzeige der Benutzerinformationen
        user_label = QLabel(f'{info.vorname} {info.nachname} ({info.email})')
        layout.addWidget(user_label)
        # Anzeige der zugeordneten Stammnummern, durch Komma getrennt
        stamm_numbers = ", ".join([stamm["stnr"] for stamm in user_data["stamms"]])
        stamm_label = QLabel(f"Stammnummern: {stamm_numbers}")
        layout.addWidget(stamm_label)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._setup_paths()
        self.load_ui()
        self.setup_data()
        self.setup_signals()
        self.setup_views()

    def _setup_paths(self):
        # Ermöglicht den Import von Modulen aus übergeordneten Verzeichnissen
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    def load_ui(self):
        """Lädt die .ui-Datei und setzt das zentrale Widget."""
        ui_file = QFile("src/test_code/main_window.ui")
        if not ui_file.open(QFile.ReadOnly):
            print("Kann die UI-Datei nicht öffnen")
            sys.exit(-1)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()
        self.setCentralWidget(self.ui.centralwidget)
        self.setWindowTitle("FlohmarktManager")

    def setup_data(self):
        """
        Lädt die JSON-Daten und aggregiert die Informationen:
         - Es wird ein Dictionary erstellt, in dem die Stammnummer-Tabellen anhand ihres Namens gespeichert werden.
         - Die Verkäufer (aus der 'verkaeufer'-Liste) werden anhand ihrer E-Mail gruppiert.
         - Anschließend werden die Stammnummern den Verkäufern zugeordnet, wenn der Stammnummer-Name mit einer der Verkäufer‑IDs (als String) übereinstimmt.
        """
        self.data = BaseData("src/test_code/export.json")
        # Erstellen eines Dictionaries, in dem der Schlüssel die Stammnummer (main_number.name) und der Wert die Einträge ist.
        self.stnr_tables = {}
        for main_number in self.data.get_main_number_list():
            key = main_number.name  # Es existiert kein main_number.id!
            self.stnr_tables[key] = main_number.data

        # Aggregierung der Verkäufer anhand ihrer E-Mail.
        # Dabei werden alle in der Spalte "id" auftretenden Werte gesammelt.
        self.users = {}
        for seller in self.data.get_seller_list():
            key = seller.email
            if key not in self.users:
                # Konvertiere seller.id zu String, um Vergleiche konsistent durchzuführen.
                self.users[key] = {"info": seller, "ids": [str(seller.id)], "stamms": []}
            else:
                if str(seller.id) not in self.users[key]["ids"]:
                    self.users[key]["ids"].append(str(seller.id))

        # Ordne jedem Benutzer die zugehörigen Stammnummern zu.
        for main_number in self.data.get_main_number_list():
            stnr = main_number.name  # Hier wird main_number.name genutzt
            for user in self.users.values():
                # Vergleiche den Stammnummernamen (als String) mit den IDs des Verkäufers.
                if stnr in [str(x) for x in user["ids"]]:
                    user["stamms"].append({
                        "stnr": stnr,
                        "entries": main_number.data
                    })

    def setup_signals(self):
        """Verbindet UI-Elemente (Buttons, Tree-Widget etc.) mit den entsprechenden Methoden."""
        self.ui.treeUsers.itemClicked.connect(self.user_item_clicked)
        self.ui.btnToggleView.clicked.connect(self.toggle_view)

    def setup_views(self):
        """Initialisiert die Ansichten: Die Baumansicht wird initial gefüllt, zusätzlich wird eine
           flache Listenansicht (mit benutzerdefinierten Widgets) erzeugt, die initial versteckt ist."""
        self.populate_user_tree()
        self.listUsers = QListWidget()
        self.ui.verticalLayoutLeft.addWidget(self.listUsers)
        self.listUsers.hide()
        self.listUsers.itemClicked.connect(self.user_list_item_clicked)

    def populate_user_tree(self):
        """
        Füllt das QTreeWidget (aggregierte Baumansicht) mit den Benutzern.
        Unter jedem Benutzer werden die zugeordneten Stammnummern als untergeordnete Knoten angezeigt.
        Beispiel:
            Klaus (klaus@example.com)
                -1
                -44
        """
        self.ui.treeUsers.clear()
        for user in self.users.values():
            info = user["info"]
            user_text = f'{info.vorname} {info.nachname} ({info.email})'
            user_item = QTreeWidgetItem([user_text])
            for stamm in user["stamms"]:
                child = QTreeWidgetItem([stamm["stnr"]])
                user_item.addChild(child)
            self.ui.treeUsers.addTopLevelItem(user_item)

    def populate_user_list(self):
        """
        Füllt das QListWidget (flache Listenansicht) mit aggregierten Benutzereinträgen.
        Unter jedem Listeneintrag (einem Benutzer) wird eine Liste aller zugeordneten Stammnummern angezeigt.
        """
        self.listUsers.clear()
        for user in self.users.values():
            item = QListWidgetItem()
            widget = UserListItemWidget(user)
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.UserRole, user)
            self.listUsers.addItem(item)
            self.listUsers.setItemWidget(item, widget)

    def toggle_view(self):
        """Schaltet zwischen der Baumansicht und der Listenansicht um."""
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
          - Wird bei Klick auf einen Stammnummer-Knoten (Kind) nur die zugehörige Stammnummer-Tabelle geladen.
          - Wird der Benutzerknoten (Elternknoten) geklickt, werden alle zugehörigen Einträge der Stammnummern zusammengefasst.
        """
        if item.parent() is not None:
            # Stammnummer-Kindelement wurde geklickt
            stnr = item.text(0)
            entries = None
            for user in self.users.values():
                for stamm in user["stamms"]:
                    if stamm["stnr"] == stnr:
                        entries = stamm["entries"]
                        break
                if entries is not None:
                    break
        else:
            # Benutzerknoten wurde geklickt – aggregiere alle Einträge der zugehörigen Stammnummern.
            user_text = item.text(0)
            entries = []
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
          - Es werden alle zugehörigen Einträge (über alle Stammnummern) des aggregierten Benutzers geladen.
        """
        user = item.data(Qt.UserRole)
        entries = []
        for stamm in user["stamms"]:
            entries.extend(stamm["entries"])
        self.populate_entry_table(entries)

    def populate_entry_table(self, entries):
        """
        Befüllt das QTableWidget (im rechten Bereich) mit den Detail-Einträgen aus der
        jeweiligen Stammnummer-Tabelle.
        """
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
