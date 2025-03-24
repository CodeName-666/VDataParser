import sys
import json
from PySide6.QtWidgets import QApplication, QWidget, QListWidgetItem
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

class UserInterface(QWidget):
    def __init__(self, json_data, ui_file="src/test_code/user_ui.ui", parent=None):
        super().__init__(parent)
        self.json_data = json_data

        # Laden der UI aus der .ui-Datei
        loader = QUiLoader()
        ui_file_obj = QFile(ui_file)
        if not ui_file_obj.open(QFile.ReadOnly):
            raise RuntimeError(f"Kann die UI-Datei {ui_file} nicht öffnen.")
        self.ui = loader.load(ui_file_obj, self)
        ui_file_obj.close()
        self.setWindowTitle(self.ui.windowTitle())
        
        # Extrahiere alle Benutzer aus der JSON-Datenstruktur
        self.users = self.extract_users(json_data)
        self.aggregated_users = self.get_aggregated_users(self.users)
        self.current_user_list = self.users  # Standard: alle Einträge

        self.setup_connections()
        self.refresh_user_list()
        if self.ui.listWidgetUsers.count() > 0:
            self.ui.listWidgetUsers.setCurrentRow(0)

    def setup_connections(self):
        """Verbindet die UI-Signale mit den entsprechenden Methoden."""
        self.ui.checkboxUnique.toggled.connect(self.refresh_user_list)
        self.ui.listWidgetUsers.currentRowChanged.connect(self.display_user_details)

    def extract_users(self, data):
        """Sucht in der JSON-Datenstruktur nach der 'verkaeufer'-Tabelle und gibt deren Daten zurück."""
        for item in data:
            if item.get("type") == "table" and item.get("name") == "verkaeufer":
                return item.get("data", [])
        return []

    def get_aggregated_users(self, users):
        """
        Gruppiert Benutzer anhand eines Schlüssels (hier: E-Mail) und fasst die IDs zusammen.
        Jeder aggregierte Benutzer enthält dann zusätzlich ein Feld 'ids' mit allen zugehörigen IDs.
        """
        aggregated = {}
        for user in users:
            key = user.get("email", "")
            if key not in aggregated:
                aggregated[key] = {
                    "vorname": user.get("vorname", ""),
                    "nachname": user.get("nachname", ""),
                    "telefon": user.get("telefon", ""),
                    "email": user.get("email", ""),
                    "created_at": user.get("created_at", ""),
                    "updated_at": user.get("updated_at", ""),
                    "ids": [user.get("id", "")]
                }
            else:
                aggregated[key]["ids"].append(user.get("id", ""))
        return list(aggregated.values())

    def refresh_user_list(self):
        """Aktualisiert die ListWidget-Anzeige basierend auf dem Status der Checkbox."""
        self.ui.listWidgetUsers.clear()
        if self.ui.checkboxUnique.isChecked():
            self.current_user_list = self.aggregated_users
            for user in self.current_user_list:
                count_ids = len(user.get("ids", []))
                text = f"{user.get('vorname', '')} {user.get('nachname', '')} ({count_ids})"
                self.ui.listWidgetUsers.addItem(text)
        else:
            self.current_user_list = self.users
            for user in self.current_user_list:
                text = f"{user.get('vorname', '')} {user.get('nachname', '')}"
                self.ui.listWidgetUsers.addItem(text)
        if self.ui.listWidgetUsers.count() > 0:
            self.ui.listWidgetUsers.setCurrentRow(0)
        else:
            self.clear_details()

    def clear_details(self):
        """Leert alle Detailfelder."""
        self.ui.valueVorname.setText("")
        self.ui.valueNachname.setText("")
        self.ui.valueTelefon.setText("")
        self.ui.valueEmail.setText("")
        self.ui.valueCreatedAt.setText("")
        self.ui.valueUpdatedAt.setText("")
        self.ui.valueIDs.setText("")

    def display_user_details(self, index):
        """Aktualisiert die Detailfelder mit den Daten des ausgewählten Benutzers."""
        if index < 0 or index >= len(self.current_user_list):
            return
        user = self.current_user_list[index]
        self.ui.valueVorname.setText(user.get("vorname", ""))
        self.ui.valueNachname.setText(user.get("nachname", ""))
        self.ui.valueTelefon.setText(user.get("telefon", ""))
        self.ui.valueEmail.setText(user.get("email", ""))
        self.ui.valueCreatedAt.setText(user.get("created_at", ""))
        self.ui.valueUpdatedAt.setText(user.get("updated_at", ""))
        if self.ui.checkboxUnique.isChecked():
            # Aggregierter Modus: Alle IDs, durch "|" getrennt
            ids = user.get("ids", [])
            self.ui.valueIDs.setText("|".join(ids))
        else:
            self.ui.valueIDs.setText(user.get("id", ""))

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Laden Sie die JSON-Daten.
    # Option 1: Aus einer Datei (z. B. config.json)
    # with open("config.json", "r", encoding="utf-8") as f:
    #     data = json.load(f)

    # Option 2: Direkt aus einem (längeren) JSON-String (hier als Beispiel mit Platzhalter)

    # Hinweis: Ersetzen Sie in obigem JSON-String den Platzhalter (/* ... */) durch Ihre kompletten Daten oder laden Sie
    # die Daten aus einer externen Datei.
    with open('src/test_code/export.json','r',encoding="utf-8") as file:
        data = json.load(file)

    window = UserInterface(data)
    window.resize(800, 400)
    window.show()
    sys.exit(app.exec())