
from .basic_db_connector import BasicDBConnector
import json

# Erweiterte Klasse zum Exportieren, Aktualisieren und Modifizieren von JSON-Daten
class AdvancedDBManager(BasicDBConnector):
    def export_to_custom_json(self, output_file: str):
        """
        Exportiert die komplette Datenbank in ein JSON-Format, das dem in deinem Export-Beispiel entspricht.
        Das erzeugte JSON besteht aus einer Liste, die einen Header, einen Datenbank-Eintrag und für jede Tabelle
        ein Objekt mit Name, Datenbank und Inhalt enthält.
        """
        export_data = []
        # Header hinzufügen
        header = {
            "type": "header",
            "version": "5.2.1",
            "comment": "Export to JSON plugin for PHPMyAdmin"
        }
        export_data.append(header)
        # Datenbank-Information hinzufügen
        db_name = self.params.get("database", "unknown")
        export_data.append({"type": "database", "name": db_name})
        # Tabellen aus der Datenbank ermitteln
        tables = []
        if self.db_type == "mysql":
            cursor = self.conn.cursor()
            cursor.execute("SHOW TABLES")
            results = cursor.fetchall()
            tables = [row[0] for row in results]
            cursor.close()
        elif self.db_type == "sqlite":
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            results = cursor.fetchall()
            tables = [row["name"] for row in results]  # dank row_factory als sqlite3.Row
            cursor.close()
        else:
            raise ValueError("Unsupported DB-Typ für Export")
        
        # Für jede Tabelle deren Inhalt abfragen und hinzufügen
        for table_name in tables:
            cursor = None
            if self.db_type == "mysql":
                cursor = self.conn.cursor(dictionary=True)
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                cursor.close()
            elif self.db_type == "sqlite":
                cursor = self.conn.cursor()
                cursor.execute(f"SELECT * FROM {table_name}")
                # Konvertiere sqlite3.Row-Objekte in Dicts
                rows = [dict(row) for row in cursor.fetchall()]
                cursor.close()
            export_data.append({
                "type": "table",
                "name": table_name,
                "database": db_name,
                "data": rows
            })
        # Speichern in die Output-Datei
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=4)
            print(f"Database export erfolgreich nach '{output_file}' geschrieben.")
        except Exception as e:
            print("Fehler beim Speichern des Exports:", e)

    def update_from_custom_json(self, json_file: str):
        """
        Liest den JSON-Export ein und aktualisiert die Datenbank.
        Für jede Tabelle im Export werden alle vorhandenen Einträge gelöscht und
        anschließend aus dem Export die neuen Zeilen eingefügt.
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Iteriere über alle Objekte, die als Typ "table" markiert sind
            for item in data:
                if item.get("type") == "table":
                    table = item.get("name")
                    rows = item.get("data", [])
                    # Vorhandene Daten in der Tabelle löschen
                    self.execute_query(f"DELETE FROM {table}")
                    # Wenn Datensätze vorhanden sind: Einfügen
                    for row in rows:
                        keys = list(row.keys())
                        columns = ", ".join(keys)
                        placeholder = "%s" if self.db_type == "mysql" else "?"
                        placeholders = ", ".join([placeholder] * len(keys))
                        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                        values = tuple(row[k] for k in keys)
                        self.execute_query(sql, values)
            print("Datenbank erfolgreich anhand des JSON Exports aktualisiert.")
        except Exception as e:
            print("Fehler beim Aktualisieren der Datenbank aus JSON:", e)

    def modify_export_data(self, json_file: str, modification_func):
        """
        Lädt den JSON-Export, wendet eine Modifikationsfunktion auf die Daten an und speichert den modifizierten Export.
        :param json_file: Pfad zur JSON-Exportdatei
        :param modification_func: Funktion, die eine Liste von Dictionaries (Export-Daten) entgegennimmt und die
                                  modifizierte Liste zurückgibt.
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            modified_data = modification_func(data)
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(modified_data, f, ensure_ascii=False, indent=4)
            print("Modifizierter Export wurde erfolgreich gespeichert.")
        except Exception as e:
            print("Fehler beim Modifizieren des JSON Exports:", e)



# Beispielhafte Nutzung der AdvancedDBManager-Klasse
if __name__ == "__main__":
    # Beispiel: Verwendung mit einer SQLite-Datenbank
    manager = AdvancedDBManager("sqlite", database="example.db")
    manager.connect()
    
    # Beispiel: Erstelle (falls noch nicht vorhanden) eine Beispiel-Tabelle
    create_table_query = """
    CREATE TABLE IF NOT EXISTS personen (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        alter INTEGER,
        created_at TEXT,
        updated_at TEXT
    )
    """
    manager.execute_query(create_table_query)
    
    # Ein Beispiel-Datensatz einfügen
    manager.insert("personen", {
        "name": "Max Mustermann",
        "alter": 30,
        "created_at": "2023-11-15 12:00:00",
        "updated_at": "2023-11-15 12:00:00"
    })
    
    # Exportiere die komplette Datenbank in eine JSON-Datei
    manager.export_to_custom_json("export.json")
    
    # Beispiel: Modifikation des Exports
    # Definiere eine Funktion, die den Export z. B. um einen zusätzlichen Kommentar ergänzt.
    def add_comment(data):
        # Gehe durch die Liste und füge im Header einen zusätzlichen Kommentar hinzu
        for entry in data:
            if entry.get("type") == "header":
                entry["additional_comment"] = "Dies wurde modifiziert."
        return data
    
    # Modifiziere die JSON-Datei
    manager.modify_export_data("export.json", add_comment)
    
    # Beispiel: Aktualisiere die Datenbank aus einem (modifizierten) Export
    # (Hinweis: Diese Funktion löscht in jeder Tabelle vorhandene Einträge und fügt die Exportdaten ein.)
    # manager.update_from_custom_json("export.json")
    
    manager.disconnect()