import json

class DataManager:
    """Lädt und verarbeitet die Rohdaten aus der JSON-Datei."""
    def __init__(self, json_path):
        self.json_path = json_path
        self.raw_data = []
        self.stnr_tables = {}
        self.users = {}
        self.load_data()
        self.process_data()

    def load_data(self):
        """Lädt die JSON-Daten aus der Datei."""
        with open(self.json_path, "r", encoding="utf-8") as f:
            self.raw_data = json.load(f)

    def process_data(self):
        """Bereitet die Daten für den UI-Gebrauch auf.
        
        - Erstellt ein Dictionary der stnr‑Tabellen.
        - Aggregiert die Benutzer aus der 'verkaeufer'-Tabelle anhand der E-Mail.
        - Ordnet jedem Benutzer die zugehörigen stnr‑Tabellen zu.
        """
        # stnr‑Tabellen ermitteln
        self.stnr_tables = {}
        for table in self.raw_data:
            if table.get("type") == "table" and table.get("name", "").startswith("stnr"):
                self.stnr_tables[table["name"]] = table.get("data", [])
        
        # Benutzer aus der "verkaeufer"-Tabelle aggregieren
        self.users = {}
        for table in self.raw_data:
            if table.get("type") == "table" and table.get("name") == "verkaeufer":
                for user in table.get("data", []):
                    key = user["email"]
                    if key not in self.users:
                        self.users[key] = {"info": user, "ids": [user["id"]], "stamms": []}
                    else:
                        if user["id"] not in self.users[key]["ids"]:
                            self.users[key]["ids"].append(user["id"])
        
        # Zuordnung der stnr‑Tabellen zu den Benutzern
        for table in self.raw_data:
            if table.get("type") == "table" and table.get("name", "").startswith("stnr"):
                stnr_num = table["name"][4:]  # extrahiert die Nummer aus "stnrX"
                for user in self.users.values():
                    if stnr_num in user["ids"]:
                        user["stamms"].append({
                            "stnr": table["name"],
                            "entries": table.get("data", [])
                        })

    def get_users(self):
        """Gibt die aggregierten Benutzer zurück."""
        return self.users

    def get_stnr_tables(self):
        """Gibt die stnr‑Tabellen zurück."""
        return self.stnr_tables

    def get_flat_users(self):
        """Gibt die flache Benutzerliste aus der 'verkaeufer'-Tabelle zurück."""
        for table in self.raw_data:
            if table.get("type") == "table" and table.get("name") == "verkaeufer":
                return table.get("data", [])
        return []
