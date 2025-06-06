import argparse
import mysql.connector
import sqlite3
import os
import json
from dataclasses import asdict
from datetime import datetime

# Importiere hier Deine Dataklassen. Es wird angenommen, dass diese aus der Datei 
# data/data_class_definition.py stammen und folgende Klassen enthalten:
# HeaderDataClass, BaseInfoDataClass, MainNumberDataClass, SellerListDataClass, JSONData
from objects.data_class_definition import *

class DatabaseManager:
    def __init__(self, db_type: str, **kwargs):
        """
        Initialisiert den Manager.
        :param db_type: "mysql" oder "sqlite"
        :param kwargs: 
            - Für MySQL: host, user, password, database
            - Für SQLite: database (Dateipfad) und optional directory (für das Auflisten von DB-Dateien)
        """
        self.db_type = db_type.lower()
        self.connection = None
        self.params = kwargs

    def connect(self):
        """Verbindet mit der Datenbank (MySQL oder SQLite)."""
        try:
            if self.db_type == "mysql":
                self.connection = mysql.connector.connect(
                    host=self.params.get("host"),
                    user=self.params.get("user"),
                    password=self.params.get("password"),
                    database=self.params.get("database")
                )
                if self.connection.is_connected():
                    print(f"Erfolgreich mit der MySQL-Datenbank '{self.params.get('database')}' auf {self.params.get('host')} verbunden.")
            elif self.db_type == "sqlite":
                db_path = self.params.get("database")
                self.connection = sqlite3.connect(db_path)
                print(f"Erfolgreich mit der SQLite-Datenbank '{db_path}' verbunden.")
            else:
                raise ValueError("Unsupported db_type. Bitte 'mysql' oder 'sqlite' verwenden.")
        except Exception as err:
            print(f"Fehler beim Verbinden: {err}")

    def disconnect(self):
        """Trennt die Verbindung zur Datenbank."""
        try:
            if self.connection:
                self.connection.close()
                print("Verbindung zur Datenbank wurde getrennt.")
        except Exception as err:
            print(f"Fehler beim Trennen der Verbindung: {err}")

    def list_databases(self, prefix: str) -> list:
        """
        Prüft, welche Datenbanken (oder Dateien bei SQLite) vorhanden sind, anhand eines Präfixes.
        :param prefix: z. B. "<prefix>_db_name"
        :return: Liste der übereinstimmenden Datenbanknamen bzw. Dateinamen (bei SQLite)
        """
        db_list = []
        try:
            if self.db_type == "mysql":
                cursor = self.connection.cursor()
                cursor.execute("SHOW DATABASES")
                results = cursor.fetchall()
                # Bei MySQL liefert SHOW DATABASES eine Liste von Tupeln
                for (db_name,) in results:
                    if db_name.startswith(prefix):
                        db_list.append(db_name)
                cursor.close()
            elif self.db_type == "sqlite":
                # Bei SQLite gehen wir davon aus, dass alle Datenbanken als Dateien im angegebenen Verzeichnis vorliegen.
                directory = self.params.get("directory", os.getcwd())
                for file in os.listdir(directory):
                    if file.endswith(".db") and file.startswith(prefix):
                        db_list.append(file)
            else:
                raise ValueError("Unsupported db_type.")
        except Exception as err:
            print(f"Fehler beim Auflisten der Datenbanken: {err}")
        return db_list

    def export_to_json(self, output_file: str):
        """
        Exportiert die gesamte Datenbank in ein JSON-Format basierend auf den verwendeten Dataclasses.
        :param output_file: Pfad zur Ausgabedatei, z. B. "export.json"
        """
        try:
            main_numbers_list = []
            seller_data_list = None

            if self.db_type == "mysql":
                cursor = self.connection.cursor(dictionary=True)
                # Ermitteln aller Tabellennamen
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                # Der Key für den Tabellennamen ist abhängig vom Datenbanknamen
                table_key = f"Tables_in_{self.params.get('database')}"
                for table in tables:
                    table_name = table[table_key]
                    cursor.execute(f"SELECT * FROM {table_name}")
                    rows = cursor.fetchall()
                    if table_name.lower() == "verkaeufer":
                        seller_data_list = SellerListDataClass(
                            type="table",
                            name=table_name,
                            database=self.params.get("database"),
                            data=rows
                        )
                    else:
                        main_numbers_list.append(MainNumberDataClass(
                            type="table",
                            name=table_name,
                            database=self.params.get("database"),
                            data=rows
                        ))
                cursor.close()

            elif self.db_type == "sqlite":
                self.connection.row_factory = sqlite3.Row
                cursor = self.connection.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                for table in tables:
                    table_name = table["name"]
                    cursor.execute(f"SELECT * FROM {table_name}")
                    # sqlite3.Row-Objekte in normale Dicts umwandeln
                    rows = [dict(row) for row in cursor.fetchall()]
                    if table_name.lower() == "verkaeufer":
                        seller_data_list = SellerListDataClass(
                            type="table",
                            name=table_name,
                            database=self.params.get("database"),
                            data=rows
                        )
                    else:
                        main_numbers_list.append(MainNumberDataClass(
                            type="table",
                            name=table_name,
                            database=self.params.get("database"),
                            data=rows
                        ))
                cursor.close()
            else:
                raise ValueError("Unsupported db_type.")

            # Falls keine Verkäufer-Tabelle vorhanden war, lege einen leeren Datensatz an.
            if seller_data_list is None:
                seller_data_list = SellerListDataClass(
                    type="table",
                    name="verkaeufer",
                    database=self.params.get("database"),
                    data=[]
                )

            # Erstellen der JSON-Datenstruktur
            header = HeaderDataClass(type="header", version="5.2.1", comment="Export to JSON plugin for Python")
            base_info = BaseInfoDataClass(type="database", name=self.params.get("database"))
            json_data = JSONData(
                export_header=header,
                base_info=base_info,
                main_numbers_list=main_numbers_list,
                sellers=seller_data_list
            )

            with open(output_file, 'w', encoding='utf-8') as json_file:
                json.dump(asdict(json_data), json_file, ensure_ascii=False, indent=4)

            print(f"Datenbank erfolgreich exportiert nach '{output_file}'.")
        except Exception as err:
            print(f"Fehler beim Exportieren: {err}")

    def update_from_json(self, json_file: str):
        """
        Aktualisiert die Datenbank anhand neuer JSON-Daten.
        Es wird für jede Tabelle der vorhandene Inhalt gelöscht und die neuen Zeilen werden eingefügt.
        :param json_file: Pfad zur JSON-Datei mit den neuen Daten.
        """
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Wähle den passenden Platzhalter für Parameter (MySQL: %s, SQLite: ?)
            placeholder = "%s" if self.db_type == "mysql" else "?"
            cursor = self.connection.cursor()

            # Update für alle normalen Tabellen (main_numbers_list)
            for table in data.get("main_numbers_list", []):
                table_name = table.get("name")
                rows = table.get("data", [])
                # Vorherige Daten löschen
                cursor.execute(f"DELETE FROM {table_name}")
                # Neue Zeilen einfügen
                for row in rows:
                    keys = list(row.keys())
                    columns = ", ".join(keys)
                    placeholders = ", ".join([placeholder] * len(keys))
                    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                    values = tuple(row[key] for key in keys)
                    cursor.execute(sql, values)

            # Update für die Verkäufer-Tabelle
            sellers_table = data.get("sellers", {})
            table_name = sellers_table.get("name", "verkaeufer")
            rows = sellers_table.get("data", [])
            cursor.execute(f"DELETE FROM {table_name}")
            for row in rows:
                keys = list(row.keys())
                columns = ", ".join(keys)
                placeholders = ", ".join([placeholder] * len(keys))
                sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                values = tuple(row[key] for key in keys)
                cursor.execute(sql, values)

            self.connection.commit()
            cursor.close()
            print("Datenbank erfolgreich anhand der JSON-Daten aktualisiert.")
        except Exception as err:
            print(f"Fehler beim Aktualisieren der Datenbank: {err}")

    def create_database(self, new_db_name: str):
        """
        Erstellt eine neue Datenbank mit vordefinierten Tabellenstrukturen.
        Bei MySQL wird eine neue Datenbank angelegt und Default-Tabellen erstellt.
        Bei SQLite wird eine neue Datenbankdatei erstellt (falls noch nicht vorhanden) und die Standardtabellen werden angelegt.
        :param new_db_name: Name der neuen Datenbank bzw. SQLite-Datei.
        """
        try:
            if self.db_type == "mysql":
                cursor = self.connection.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {new_db_name}")
                cursor.execute(f"USE {new_db_name}")
                # Beispiel: Erstelle Standardtabellen
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS verkaeufer (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(255) NOT NULL
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS artikel (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        description VARCHAR(255)
                    )
                """)
                self.connection.commit()
                cursor.close()
                print(f"Neue MySQL-Datenbank '{new_db_name}' mit Standardtabellen erstellt.")
            elif self.db_type == "sqlite":
                # Bei SQLite erstellt sich die Datenbank beim Connecten, wenn die Datei noch nicht existiert.
                self.disconnect()
                if not os.path.exists(new_db_name):
                    self.connection = sqlite3.connect(new_db_name)
                    cursor = self.connection.cursor()
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS verkaeufer (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL
                        )
                    """)
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS artikel (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            description TEXT
                        )
                    """)
                    self.connection.commit()
                    cursor.close()
                    print(f"Neue SQLite-Datenbank '{new_db_name}' mit Standardtabellen erstellt.")
                else:
                    print("Die SQLite-Datenbankdatei existiert bereits.")
            else:
                raise ValueError("Unsupported db_type.")
        except Exception as err:
            print(f"Fehler beim Erstellen der Datenbank: {err}")

    def delete_database(self, db_name: str):
        """
        Löscht die angegebene Datenbank.
        Bei MySQL wird die Datenbank mit DROP DATABASE entfernt.
        Bei SQLite wird die entsprechende Datei gelöscht.
        :param db_name: Name der Datenbank oder bei SQLite der Dateiname.
        """
        try:
            if self.db_type == "mysql":
                cursor = self.connection.cursor()
                cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")
                self.connection.commit()
                cursor.close()
                print(f"MySQL-Datenbank '{db_name}' wurde gelöscht.")
            elif self.db_type == "sqlite":
                self.disconnect()
                if os.path.exists(db_name):
                    os.remove(db_name)
                    print(f"SQLite-Datenbankdatei '{db_name}' wurde gelöscht.")
                else:
                    print("Die SQLite-Datenbankdatei existiert nicht.")
            else:
                raise ValueError("Unsupported db_type.")
        except Exception as err:
            print(f"Fehler beim Löschen der Datenbank: {err}")


# Beispiel: Nutzung der Klasse über Argumentparsing
def main():
    parser = argparse.ArgumentParser(description="Datenbankmanager: Verbindung, Export, Update, Erstellen und Löschen von MySQL/SQLite-Datenbanken")
    parser.add_argument("--db_type", choices=["mysql", "sqlite"], required=True, help="Datenbanktyp: 'mysql' oder 'sqlite'")
    parser.add_argument("--action", choices=["connect", "list", "export", "update", "disconnect", "create", "delete"], required=True, help="Aktion auswählen")
    
    # Allgemeine Argumente
    parser.add_argument("--database", help="Name der Datenbank (bei MySQL) oder Pfad zur SQLite-Datei")
    parser.add_argument("--host", help="Hostname (nur MySQL)")
    parser.add_argument("--user", help="Benutzername (nur MySQL)")
    parser.add_argument("--password", help="Passwort (nur MySQL)")
    parser.add_argument("--directory", help="Verzeichnis (nur für SQLite zum Auflisten von DB-Dateien)", default=os.getcwd())
    
    # Spezifische Argumente
    parser.add_argument("--prefix", help="Präfix zum Filtern von Datenbanknamen (bei 'list')")
    parser.add_argument("--output", help="Ausgabedatei für JSON (bei 'export')", default="export.json")
    parser.add_argument("--json_file", help="JSON-Datei zum Update (bei 'update')")
    parser.add_argument("--new_db_name", help="Name der neu zu erstellenden Datenbank (bei 'create' bzw. 'delete')")
    
    args = parser.parse_args()

    # Initialisiere den Manager mit den übergebenen Parametern
    params = {}
    if args.database:
        params["database"] = args.database
    if args.host:
        params["host"] = args.host
    if args.user:
        params["user"] = args.user
    if args.password:
        params["password"] = args.password
    if args.directory:
        params["directory"] = args.directory

    manager = DatabaseManager(args.db_type, **params)

    if args.action == "connect":
        manager.connect()
    elif args.action == "list":
        manager.connect()
        if not args.prefix:
            print("Für 'list' muss ein Präfix (--prefix) angegeben werden.")
        else:
            dbs = manager.list_databases(args.prefix)
            print("Gefundene Datenbanken:", dbs)
    elif args.action == "export":
        manager.connect()
        manager.export_to_json(args.output)
    elif args.action == "update":
        if not args.json_file:
            print("Für 'update' muss der Pfad zur JSON-Datei (--json_file) angegeben werden.")
        else:
            manager.connect()
            manager.update_from_json(args.json_file)
    elif args.action == "disconnect":
        manager.disconnect()
    elif args.action == "create":
        if not args.new_db_name:
            print("Für 'create' muss der neue Datenbankname (--new_db_name) angegeben werden.")
        else:
            manager.connect()
            manager.create_database(args.new_db_name)
    elif args.action == "delete":
        if not args.new_db_name:
            print("Für 'delete' muss der Datenbankname (--new_db_name) angegeben werden.")
        else:
            manager.connect()
            manager.delete_database(args.new_db_name)
    else:
        print("Unbekannte Aktion.")


if __name__ == "__main__":
    main()
