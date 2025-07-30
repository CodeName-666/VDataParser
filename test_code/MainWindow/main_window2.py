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

sys.path.insert(0, Path(__file__).parent.parent.parent.__str__())  # NOQA: E402 pylint: disable=[C0413]
from src.data import BaseData


class UserListItemWidget(QWidget):
    """
    Benutzerdefiniertes Widget für die flache Listenansicht.
    Es zeigt oben die Benutzerinformationen und darunter alle zugeordneten Stammnummern.
    """
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        # Benutzerinformationen
        info = user_data["info"]
        user_label = QLabel(f'{info.vorname} {info.nachname} ({info.email})')
        layout.addWidget(user_label)
        # Stammnummern als durch Kommas getrennte Liste
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
        # Ermöglicht das Importieren von Modulen aus übergeordneten Verzeichnissen
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
        self.setWindowTitle("self.ui.windowTitle()")

    def setup_data(self):
        """
        Initialisiert die Daten, erstellt die Stammnummer-Tabellen und aggregiert die Benutzer.
        Hierbei wird das Attribut 'name' der MainNumberDataClass verwendet, da 'id' nicht existiert.
        """
        self.data = BaseData("src/test_code/export.json")
        # Erzeugen eines Dictionary zur schnellen Zuordnung der Stammnummer-Tabellen mit Schlüsseln main_number.name
        self.stnr_tables = {
            main_number.name: main_number.data 
            for main_number in self.data.get_main_number_as_list()
        }

        # Aggregierung der Benutzer aus der 'verkaeufer'-Tabelle anhand der E-Mail
        self.users = {}
        for user in self.data.get_seller_as_list():
            key = user.email
            if key not in self.users:
                # Hier gehen wir davon aus, dass user.id und main_number.name übereinstimmen
                self.users[key] = {"info": user, "ids": [str(user.id)], "stamms": []}
            else:
                if str(user.id) not in self.users[key]["ids"]:
                    self.users[key]["ids"].append(str(user.id))

        # Zuordnung der Stammnummer-Tabellen zu den Benutzern
        for main_number in self.data.get_main_number_as_list():
            stnr_name = main_number.name
            for user in self.users.values():
                # Anstatt main_number.id verwenden wir main_number.name
                if main_number.name in user["ids"]:
                    user["stamms"].append({
                        "stnr": stnr_name,
                        "entries": main_number.data
                    })

    def setup_signals(self):
        """Verbindet UI-Elemente mit den entsprechenden Methoden."""
        self.ui.treeUsers.itemClicked.connect(self.user_item_clicked)
        self.ui.btnToggleView.clicked.connect(self.toggle_view)

    def setup_views(self):
        """Initialisiert die verschiedenen Ansichten (Baum- und Listenansicht)."""
        self.populate_user_tree()
        self.listUsers = QListWidget()
        self.ui.verticalLayoutLeft.addWidget(self.listUsers)
        self.listUsers.hide()
        self.listUsers.itemClicked.connect(self.user_list_item_clicked)

    def populate_user_tree(self):
        """Füllt das QTreeWidget (aggregierte Ansicht) mit den Benutzern und ihren Stammnummern."""
        self.ui.treeUsers.clear()
        for key, user in self.users.items():
            user_text = f'{user["info"].vorname} {user["info"].nachname} ({user["info"].email})'
            user_item = QTreeWidgetItem([user_text])
            for stamm in user["stamms"]:
                child = QTreeWidgetItem([stamm["stnr"]])
                user_item.addChild(child)
            self.ui.treeUsers.addTopLevelItem(user_item)

    def populate_user_list(self):
        """
        Füllt das QListWidget (flache Listenansicht) mit aggregierten Benutzereinträgen.
        Unter jedem Benutzer wird eine Liste (als Label) aller zugeordneten Stammnummern angezeigt.
        """
        self.listUsers.clear()
        for key, user in self.users.items():
            item = QListWidgetItem()
            widget = UserListItemWidget(user)
            item.setSizeHint(widget.sizeHint())
            item.setData(Qt.UserRole, user)
            self.listUsers.addItem(item)
            self.listUsers.setItemWidget(item, widget)

    def toggle_view(self):
        """Schaltet zwischen Baum- und Listenansicht um."""
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
        Reagiert auf Klicks in der Baumansicht:
        - Bei einem Kindelement (Stammnummer) werden nur die zugehörigen Einträge geladen.
        - Beim Benutzerknoten werden alle zugehörigen Einträge zusammengefasst.
        """
        if item.parent() is not None:
            stnr_name = item.text(0)
            entries = next(
                (stamm["entries"] for user in self.users.values() for stamm in user["stamms"] if stamm["stnr"] == stnr_name),
                None
            )
        else:
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
        Beim Klick in der Listenansicht:
        Es werden alle zugehörigen Einträge (über alle Stammnummern) des aggregierten Benutzers geladen.
        """
        user = item.data(Qt.UserRole)
        entries = []
        for stamm in user["stamms"]:
            entries.extend(stamm["entries"])
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
