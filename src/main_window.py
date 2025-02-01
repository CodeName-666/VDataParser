import sys
import json
from PySide6.QtCore import QFile
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QTableWidgetItem
from PySide6.QtUiTools import QUiLoader

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Laden der .ui-Datei
        ui_file = QFile("main_window.ui")
        if not ui_file.open(QFile.ReadOnly):
            print("Kann die UI-Datei nicht öffnen")
            sys.exit(-1)
        loader = QUiLoader()
        self.ui = loader.load(ui_file, self)
        ui_file.close()

        self.setCentralWidget(self.ui.centralwidget)
        self.setWindowTitle("Test")

        # Beispielhafte JSON-Daten – hier müssten Sie Ihre MySQL-Daten importieren!
        # (Üblicherweise laden Sie die Daten aus einer Datei oder direkt aus der DB.)
        with open("export.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)

        # Erstellen Sie ein Dictionary für die Benutzer.
        # Gruppierung erfolgt hier z.B. über die E-Mail-Adresse, sodass Duplikate (gleiche E-Mail) zusammengeführt werden.
        # Zusätzlich speichern wir alle zugehörigen IDs (aus der Spalte "id") für jeden Benutzer.
        self.users = {}  # Schlüssel: E-Mail, Wert: { "info": erste Benutzerdaten, "ids": [alle IDs], "stamms": [] }
        for table in self.data:
            if table.get("type") == "table" and table.get("name") == "verkaeufer":
                for user in table.get("data", []):
                    key = user["email"]
                    if key not in self.users:
                        self.users[key] = {"info": user, "ids": [user["id"]], "stamms": []}
                    else:
                        # Füge weitere IDs hinzu, falls der Benutzer bereits existiert
                        if user["id"] not in self.users[key]["ids"]:
                            self.users[key]["ids"].append(user["id"])

        # Jetzt werden die stnr-Tabellen (stnr1 ... stnr7) den Benutzern zugeordnet.
        # Es wird davon ausgegangen, dass der Tabellenname "stnrX" über X mit der ID des Benutzers korrespondiert.
        for table in self.data:
            if table.get("type") == "table" and table.get("name", "").startswith("stnr"):
                # Extrahieren Sie aus dem Tabellennamen die Nummer (z.B. "1" aus "stnr1")
                stnr_num = table["name"][4:]
                # Durchlaufen Sie alle Benutzer; wenn die Stammnummer in der ID-Liste enthalten ist, ordnen Sie sie zu.
                for user in self.users.values():
                    if stnr_num in user["ids"]:
                        user["stamms"].append({
                            "stnr": table["name"],
                            "entries": table.get("data", [])
                        })
                        # Falls Sie mehrere stnr-Tabellen pro Benutzer erwarten, löschen Sie hier nicht weiter.
                        # (Bei eindeutiger Zuordnung könnte man z.B. auch ein "break" setzen.)
        
        # Füllen Sie das QTreeWidget mit den Benutzern und deren zugehörigen Stammnummern
        self.populate_user_tree()

        # Verbinden Sie Signale
        self.ui.btnToggleView.clicked.connect(self.toggle_view)
        self.ui.treeUsers.itemClicked.connect(self.user_item_clicked)

    def populate_user_tree(self):
        """Befüllt das QTreeWidget mit den Benutzern und ihren zugehörigen Stammnummern."""
        self.ui.treeUsers.clear()
        for key, user in self.users.items():
            # Erzeugen eines Baum-Knotens für den Benutzer
            user_text = f'{user["info"]["vorname"]} {user["info"]["nachname"]} ({user["info"]["email"]})'
            user_item = QTreeWidgetItem([user_text])
            # Füge als untergeordneten Knoten alle zugehörigen Stammnummern hinzu
            for stamm in user["stamms"]:
                child = QTreeWidgetItem([stamm["stnr"]])
                user_item.addChild(child)
            self.ui.treeUsers.addTopLevelItem(user_item)

    def toggle_view(self):
        """Umschalten zwischen Baum- und Listenansicht.
        In einer Listenansicht könnten Sie beispielsweise alle Benutzereinträge (inkl. Duplikaten) untereinander anzeigen.
        Hier nur als Beispiel – die konkrete Umsetzung liegt bei Ihnen."""
        print("Toggle-Button wurde gedrückt. Implementieren Sie hier die Umschaltung der Ansicht.")
        # Beispiel: Sie könnten hier den QTreeWidget komplett leeren und stattdessen eine QTableWidget-Liste füllen.

    def user_item_clicked(self, item, column):
        """
        Wenn ein Benutzer- oder Stammnummer-Knoten geklickt wird,
        sollen im rechten Bereich die entsprechenden Einträge in der Tabelle angezeigt werden.
        """
        # Falls der geklickte Knoten ein Kind ist (also eine Stammnummer)
        if item.parent() is not None:
            stnr_name = item.text(0)
            entries = None
            # Suchen Sie den entsprechenden Eintrag in den Benutzerdaten
            for user in self.users.values():
                for stamm in user["stamms"]:
                    if stamm["stnr"] == stnr_name:
                        entries = stamm["entries"]
                        break
                if entries is not None:
                    break
        else:
            # Es wurde ein Benutzerknoten geklickt.
            # Sie könnten hier alle Einträge des Benutzers (aller zugehörigen Stammnummern) zusammenfassen.
            entries = []
            # Zum Vergleich erstellen wir den Text, wie er im Baum angezeigt wird.
            user_text = item.text(0)
            for user in self.users.values():
                info_text = f'{user["info"]["vorname"]} {user["info"]["nachname"]} ({user["info"]["email"]})'
                if info_text == user_text:
                    for stamm in user["stamms"]:
                        entries.extend(stamm["entries"])
                    break

        # Füllen Sie die Tabelle auf der rechten Seite mit den gefundenen Einträgen
        self.populate_entry_table(entries)

    def populate_entry_table(self, entries):
        """Befüllt das QTableWidget mit den Detail-Einträgen."""
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
            # Beispiel: Datum (hier verwenden wir created_at)
            self.ui.tableEntries.setItem(row, 4, QTableWidgetItem(entry.get("created_at", "")))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
