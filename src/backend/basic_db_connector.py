import mysql.connector
import sqlite3
import os

class BasicDBConnector:
    def __init__(self, db_type: str, **kwargs):
        """
        Grundlegender DB-Connector.
        
        :param db_type: "mysql" oder "sqlite"
        :param kwargs: Parameter je nach DB-Typ
            Für MySQL: host, user, password, database
            Für SQLite: database (Dateipfad)
        """
        self.db_type = db_type.lower()
        self.params = kwargs
        self.conn = None

    def connect(self):
        """Stellt die Verbindung zur Datenbank her."""
        if self.db_type == "mysql":
            try:
                self.conn = mysql.connector.connect(
                    host=self.params.get("host", "localhost"),
                    user=self.params.get("user"),
                    password=self.params.get("password"),
                    database=self.params.get("database")
                )
                print("MySQL-Verbindung erfolgreich hergestellt.")
            except Exception as e:
                print("Fehler beim Verbinden mit MySQL:", e)
        elif self.db_type == "sqlite":
            try:
                db_file = self.params.get("database")
                self.conn = sqlite3.connect(db_file)
                print("SQLite-Verbindung erfolgreich hergestellt.")
            except Exception as e:
                print("Fehler beim Verbinden mit SQLite:", e)
        else:
            print("Nicht unterstützter DB-Typ. Bitte 'mysql' oder 'sqlite' verwenden.")

    def disconnect(self):
        """Beendet die Verbindung zur Datenbank."""
        if self.conn:
            self.conn.close()
            self.conn = None
            print("Verbindung zur Datenbank wurde getrennt.")

    def create_database(self, new_db_name: str):
        """
        Erstellt eine neue Datenbank.
        
        Für MySQL: Legt eine neue Datenbank an (falls sie noch nicht existiert).
        Für SQLite: Erzeugt eine neue Datei, falls diese noch nicht existiert.
        """
        if self.db_type == "mysql":
            try:
                cursor = self.conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {new_db_name}")
                self.conn.commit()
                print(f"MySQL-Datenbank '{new_db_name}' wurde erstellt.")
            except Exception as e:
                print("Fehler beim Erstellen der MySQL-Datenbank:", e)
        elif self.db_type == "sqlite":
            try:
                if not os.path.exists(new_db_name):
                    # Bei SQLite wird die Datenbank automatisch erstellt, wenn wir verbinden.
                    self.disconnect()
                    self.conn = sqlite3.connect(new_db_name)
                    print(f"SQLite-Datenbankdatei '{new_db_name}' wurde erstellt.")
                else:
                    print("Die SQLite-Datenbankdatei existiert bereits.")
            except Exception as e:
                print("Fehler beim Erstellen der SQLite-Datenbank:", e)
        else:
            print("Unsupported DB-Typ beim Erstellen der Datenbank.")

    def execute_query(self, query: str, values: tuple = None):
        """
        Führt eine generische SQL-Abfrage aus.
        
        :param query: Die SQL-Abfrage
        :param values: Optionales Tuple für Parameterplatzhalter
        :return: Cursor-Objekt mit dem Ergebnis der Abfrage
        """
        try:
            cursor = self.conn.cursor()
            if values:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            self.conn.commit()
            print("SQL-Abfrage erfolgreich ausgeführt.")
            return cursor
        except Exception as e:
            print("Fehler bei der Ausführung der Abfrage:", e)
            return None

    def insert(self, table: str, data: dict):
        """
        Fügt einen neuen Datensatz in die angegebene Tabelle ein.
        
        :param table: Name der Tabelle
        :param data: Dictionary mit Spaltennamen als Schlüssel und den einzufügenden Werten
        """
        try:
            keys = list(data.keys())
            columns = ", ".join(keys)
            placeholder = "%s" if self.db_type == "mysql" else "?"
            placeholders = ", ".join([placeholder] * len(keys))
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            values = tuple(data[key] for key in keys)
            self.execute_query(query, values)
            print("Eintrag in Tabelle '{}' eingefügt.".format(table))
        except Exception as e:
            print("Fehler beim Einfügen des Eintrags:", e)

    def update(self, table: str, data: dict, where_clause: str = "", where_values: tuple = None):
        """
        Aktualisiert bestehende Datensätze in einer Tabelle.
        
        :param table: Name der Tabelle
        :param data: Dictionary mit den Spalten und den neuen Werten
        :param where_clause: (Optional) SQL-Bedingung ohne das 'WHERE'-Schlüsselwort (z. B. "id = ?")
        :param where_values: (Optional) Tuple mit Werten für die Bedingung
        """
        try:
            # Erstellen der SET-Klausel
            placeholder = "%s" if self.db_type == "mysql" else "?"
            set_clause = ", ".join([f"{col} = {placeholder}" for col in data.keys()])
            query = f"UPDATE {table} SET {set_clause}"
            if where_clause:
                query += f" WHERE {where_clause}"
            values = tuple(data.values())
            if where_values:
                if isinstance(where_values, tuple):
                    values += where_values
                else:
                    values += (where_values,)
            self.execute_query(query, values)
            print("Eintrag in Tabelle '{}' aktualisiert.".format(table))
        except Exception as e:
            print("Fehler beim Aktualisieren des Eintrags:", e)

    def delete(self, table: str, where_clause: str = "", where_values: tuple = None):
        """
        Löscht Datensätze aus einer Tabelle.
        
        :param table: Name der Tabelle
        :param where_clause: (Optional) SQL-Bedingung ohne das 'WHERE'-Schlüsselwort (z. B. "id = ?")
        :param where_values: (Optional) Tuple mit Werten für die Bedingung
        """
        try:
            query = f"DELETE FROM {table}"
            if where_clause:
                query += f" WHERE {where_clause}"
            self.execute_query(query, where_values)
            print("Einträge aus Tabelle '{}' gelöscht.".format(table))
        except Exception as e:
            print("Fehler beim Löschen des Eintrags:", e)

    def select_all(self, table: str):
        """
        Liest alle Datensätze aus einer Tabelle.
        
        :param table: Name der Tabelle
        :return: Liste von Datensätzen (jeder Datensatz als Tuple)
        """
        try:
            query = f"SELECT * FROM {table}"
            cursor = self.execute_query(query)
            rows = cursor.fetchall() if cursor else []
            return rows
        except Exception as e:
            print("Fehler beim Auslesen der Tabelle:", e)
            return []

     # Neue Methode: Prüfen, ob eine Datenbank existiert
    def database_exists(self, db_name: str) -> bool:
        """
        Prüft, ob eine Datenbank existiert.
        Für MySQL wird per Abfrage "SHOW DATABASES LIKE ..." ermittelt,
        für SQLite wird geprüft, ob die Datei existiert.
        
        :param db_name: Name der Datenbank (bei MySQL) oder Dateipfad (bei SQLite)
        :return: True, falls die Datenbank existiert, sonst False.
        """
        if self.db_type == "mysql":
            try:
                # Wir setzen voraus, dass self.conn bereits eine Verbindung zur MySQL-Instanz hat.
                cursor = self.conn.cursor()
                query = "SHOW DATABASES LIKE %s"
                cursor.execute(query, (db_name,))
                result = cursor.fetchone()
                cursor.close()
                exists = result is not None
                print(f"Datenbank '{db_name}' existiert: {exists}")
                return exists
            except Exception as e:
                print("Fehler beim Überprüfen der Datenbank in MySQL:", e)
                return False
        elif self.db_type == "sqlite":
            # Bei SQLite entspricht der Datenbankname dem Dateipfad.
            exists = os.path.exists(db_name)
            print(f"SQLite-Datenbankdatei '{db_name}' existiert: {exists}")
            return exists
        else:
            print("Unsupported DB-Typ für die Existenzprüfung.")
            return False



# Beispielhafte Nutzung der BasicDBConnector-Klasse
if __name__ == "__main__":
    # Beispiel für SQLite:
    print("=== Beispiel: SQLite ===")
    sqlite_connector = BasicDBConnector("sqlite", database="example.db")
    sqlite_connector.connect()
    
    # Tabelle erstellen (falls sie nicht existiert)
    create_table_query = """
    CREATE TABLE IF NOT EXISTS personen (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        alter INTEGER
    )
    """
    sqlite_connector.execute_query(create_table_query)
    
    # Datensatz einfügen
    sqlite_connector.insert("personen", {"name": "Max Mustermann", "alter": 30})
    
    # Alle Datensätze auslesen
    rows = sqlite_connector.select_all("personen")
    print("Aktueller Inhalt der Tabelle 'personen':", rows)
    
    # Datensatz aktualisieren
    sqlite_connector.update("personen", {"alter": 31}, "name = ?", ("Max Mustermann",))
    
    # Datensatz löschen (Beispiel: Löschen des Datensatzes mit id = 1)
    sqlite_connector.delete("personen", "id = ?", (1,))
    
    # Verbindung trennen
    sqlite_connector.disconnect()
    
    # Beispiel für MySQL (auskommentiert – benötige entsprechende MySQL-Zugangsdaten):
    # print("=== Beispiel: MySQL ===")
    # mysql_connector = BasicDBConnector(
    #     "mysql",
    #     host="localhost",
    #     user="dein_benutzer",
    #     password="dein_passwort",
    #     database="testdb"
    # )
    # mysql_connector.connect()
    # mysql_connector.execute_query("""
    #     CREATE TABLE IF NOT EXISTS personen (
    #         id INT AUTO_INCREMENT PRIMARY KEY,
    #         name VARCHAR(255) NOT NULL,
    #         alter INT
    #     )
    # """)
    # mysql_connector.insert("personen", {"name": "Max Mustermann", "alter": 30})
    # rows = mysql_connector.select_all("personen")
    # print("Aktueller Inhalt der Tabelle 'personen':", rows)
    # mysql_connector.disconnect()
