from interface import (
    DatabaseConnectionError,
    DatabaseQueryError,
    DatabaseOperations
    )
import os
from interface import SQLiteConnector, MySQLConnector
from interface import MYSQL_AVAILABLE


# (Code from the previous response: Imports, Exceptions, DatabaseOperations,
#  SQLiteConnector, MySQLConnector - assuming they are already defined above)

# --- Main BasicDBConnector (Continued) ---
class BasicDBConnector:
    def __init__(self, db_operator: DatabaseOperations):
        """
        Initialisiert den DB-Connector mit einer spezifischen Implementierung
        der Datenbankoperationen.

        :param db_operator: Eine Instanz einer Klasse, die von DatabaseOperations erbt
                            (z.B. SQLiteConnector, MySQLConnector).
        """
        if not isinstance(db_operator, DatabaseOperations):
            raise TypeError("db_operator muss eine Instanz einer DatabaseOperations-Implementierung sein.")
        self.operator = db_operator
        self.conn = None
        # Store the class name for easier logging/messaging
        self.db_type_name = type(db_operator).__name__.replace("Connector", "")


    def connect(self, database_override: str = None):
        """
        Stellt die Verbindung zur Datenbank her, delegiert an den Operator.

        :param database_override: Optionaler Datenbankname/Datei zum Verbinden.
        :raises DatabaseConnectionError: If connection fails.
        """
        if self.conn:
            print(f"Bereits verbunden ({self.db_type_name}).")
            return
        try:
            # Delegate connection to the specific operator
            self.conn = self.operator.connect_db(database_override)
            print(f"Verbindung erfolgreich hergestellt via {type(self.operator).__name__}.")
        except DatabaseConnectionError:
             self.conn = None # Ensure conn is None on failure
             raise # Re-raise the specific connection error
        except Exception as e:
            self.conn = None
            # Wrap unexpected errors from the operator's connect
            raise DatabaseConnectionError(f"Unerwarteter Fehler beim Verbindungsaufbau ({self.db_type_name}): {e}") from e


    def disconnect(self):
        """Beendet die Verbindung zur Datenbank, delegiert an den Operator."""
        if self.conn:
            # Delegate disconnection to the specific operator
            print(f"Trenne Verbindung via {type(self.operator).__name__}...")
            self.operator.disconnect_db(self.conn)
            self.conn = None # Set to None regardless of disconnect success/failure
        else:
            print("Keine aktive Datenbankverbindung zum Trennen vorhanden.")

    def __enter__(self):
        """Ermöglicht die Nutzung mit 'with'-Statement."""
        if not self.conn:
             self.connect() # connect() raises error on failure
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ermöglicht die Nutzung mit 'with'-Statement."""
        self.disconnect()
        return False # Propagate exceptions from the with block

    def database_exists(self, db_name: str) -> bool:
        """Prüft, ob eine Datenbank existiert, delegiert an den Operator."""
        try:
            # Delegate check to the specific operator
            print(f"Prüfe DB-Existenz '{db_name}' via {type(self.operator).__name__}...")
            return self.operator.check_database_exists(db_name)
        except (DatabaseConnectionError, ImportError, ValueError) as e:
             print(f"Fehler bei Existenzprüfung ({self.db_type_name}): {e}")
             raise # Re-raise known error types
        except Exception as e:
            print(f"Unerwarteter Fehler bei Existenzprüfung ({self.db_type_name}): {e}")
            # Wrap unexpected errors
            raise DatabaseConnectionError(f"Unerwarteter Fehler bei Existenzprüfung ({self.db_type_name}): {e}") from e


    def create_database(self, new_db_name: str):
        """Erstellt eine neue Datenbank, delegiert an den Operator."""
        try:
             # Delegate creation to the specific operator
             print(f"Erstelle DB '{new_db_name}' via {type(self.operator).__name__}...")
             self.operator.create_db(new_db_name)
        except (DatabaseConnectionError, DatabaseQueryError, ImportError, ValueError) as e:
             print(f"Fehler beim Erstellen der DB ({self.db_type_name}): {e}")
             raise # Re-raise known error types
        except Exception as e:
            print(f"Unerwarteter Fehler beim Erstellen der DB ({self.db_type_name}): {e}")
            # Wrap unexpected errors
            raise DatabaseQueryError(f"Unerwarteter Fehler beim Erstellen der DB ({self.db_type_name}): {e}") from e


    def execute_query(self, query: str, params: tuple = None, fetch: str = None):
        """
        Führt eine SQL-Abfrage aus, delegiert an den Operator.
        Verwendet IMMER %s als Platzhalter im Input-Query. Der Operator passt es ggf. an.
        """
        if not self.conn:
             raise DatabaseConnectionError(f"Nicht verbunden ({self.db_type_name}). Rufen Sie zuerst connect() auf oder verwenden Sie 'with'.")

        try:
            # Delegate query execution to the specific operator
            # The operator is responsible for handling placeholders and specific errors
            return self.operator.execute_db_query(self.conn, query, params, fetch)
        except DatabaseQueryError:
            raise # Re-raise directly, operator should have formatted it
        except Exception as e:
            # Catch unexpected errors during delegation
            print(f"Unerwarteter Fehler bei Query-Ausführung ({self.db_type_name}): {e}")
            placeholder_style = self.operator.get_placeholder_style()
            adapted_query = query.replace('%s', placeholder_style) if placeholder_style != '%s' else query
            raise DatabaseQueryError(f"Unerwarteter Fehler ({self.db_type_name}): {e}\nAngepasste Query (intern): {adapted_query}\nParams: {params}") from e


    # --- Convenience Methods (using execute_query) ---
    # Diese Methoden bleiben weitgehend gleich, da sie execute_query verwenden.
    # Sie müssen nur sicherstellen, dass sie %s als Platzhalter verwenden.

    def insert(self, table: str, data: dict) -> int | None:
        """
        Fügt einen neuen Datensatz ein (verwendet %s Platzhalter).
        """
        if not data:
            raise ValueError("Keine Daten zum Einfügen angegeben.")

        try:
            keys = list(data.keys())
            columns = ", ".join(f"`{k}`" for k in keys) # Quote identifiers
            placeholders = ", ".join(["%s"] * len(keys)) # Use %s
            # Quote table name
            query = f"INSERT INTO `{table}` ({columns}) VALUES ({placeholders})"
            values = tuple(data.values())

            result = self.execute_query(query, values, fetch=None) # Use default fetch=None
            inserted_id = result.get("lastrowid") if isinstance(result, dict) else None
            print(f"Eintrag in Tabelle '{table}' eingefügt ({self.db_type_name}). Last Insert ID: {inserted_id}")
            return inserted_id
        except (DatabaseQueryError, ValueError) as e:
             print(f"Fehler beim Einfügen des Eintrags in '{table}' ({self.db_type_name}): {e}")
             raise
        except Exception as e:
             print(f"Unerwarteter Fehler beim Einfügen in '{table}' ({self.db_type_name}): {e}")
             raise DatabaseQueryError(f"Unerwarteter Fehler beim Einfügen: {e}") from e


    def update(self, table: str, data: dict, where_clause: str, where_params: tuple) -> int:
        """
        Aktualisiert Datensätze (verwendet %s Platzhalter in where_clause).
        """
        if not data:
             raise ValueError("Keine Daten zum Aktualisieren angegeben.")
        if not where_clause or where_params is None:
             raise ValueError("where_clause und where_params sind für UPDATE erforderlich.")
        if not isinstance(where_params, tuple):
             raise ValueError("where_params muss ein Tuple sein.")

        try:
            # Quote identifiers, use %s
            set_clause = ", ".join([f"`{col}` = %s" for col in data.keys()])
            # Use %s in where_clause - the user provides it this way
            query = f"UPDATE `{table}` SET {set_clause} WHERE {where_clause}"
            update_values = tuple(data.values())
            params = update_values + where_params

            result = self.execute_query(query, params, fetch=None) # Use default fetch=None
            rowcount = result.get("rowcount", 0) if isinstance(result, dict) else 0
            print(f"{rowcount} Eintrag/Einträge in Tabelle '{table}' aktualisiert ({self.db_type_name}).")
            return rowcount
        except (DatabaseQueryError, ValueError) as e:
             print(f"Fehler beim Aktualisieren von Einträgen in '{table}' ({self.db_type_name}): {e}")
             raise
        except Exception as e:
             print(f"Unerwarteter Fehler beim Aktualisieren in '{table}' ({self.db_type_name}): {e}")
             raise DatabaseQueryError(f"Unerwarteter Fehler beim Update: {e}") from e


    def delete(self, table: str, where_clause: str, where_params: tuple) -> int:
        """
        Löscht Datensätze (verwendet %s Platzhalter in where_clause).

        :param table: Name der Tabelle.
        :param where_clause: SQL-Bedingung ohne 'WHERE' (z.B., "id = %s").
                             Verwenden Sie %s als Platzhalter.
        :param where_params: Tuple mit Werten für die Platzhalter in where_clause.
        :return: Anzahl der gelöschten Zeilen (rowcount). Returns 0 if no rows matched.
        :raises DatabaseQueryError: If the delete operation fails.
        :raises ValueError: If where_clause/where_params are missing or invalid.
        """
        if not where_clause or where_params is None:
             raise ValueError("where_clause und where_params sind für DELETE erforderlich.")
        if not isinstance(where_params, tuple):
             raise ValueError("where_params muss ein Tuple sein.")

        try:
            # Quote table name, use %s in where_clause
            query = f"DELETE FROM `{table}` WHERE {where_clause}"

            result = self.execute_query(query, where_params, fetch=None) # Use default fetch=None
            rowcount = result.get("rowcount", 0) if isinstance(result, dict) else 0
            print(f"{rowcount} Eintrag/Einträge aus Tabelle '{table}' gelöscht ({self.db_type_name}).")
            return rowcount
        except (DatabaseQueryError, ValueError) as e:
            print(f"Fehler beim Löschen von Einträgen aus '{table}' ({self.db_type_name}): {e}")
            raise
        except Exception as e:
            print(f"Unerwarteter Fehler beim Löschen aus '{table}' ({self.db_type_name}): {e}")
            raise DatabaseQueryError(f"Unerwarteter Fehler beim Delete: {e}") from e

    def select(self, query: str, params: tuple = None, fetch: str = 'all'):
        """
        Führt eine SELECT-Abfrage aus und gibt die Ergebnisse zurück
        (verwendet %s Platzhalter).

        :param query: Die vollständige SELECT-SQL-Abfrage (mit %s Platzhaltern).
        :param params: Optionales Tuple mit Werten für die Platzhalter.
        :param fetch: 'one' für eine Zeile, 'all' für alle Zeilen (default).
        :return: Eine einzelne Zeile (als Tuple) oder eine Liste von Zeilen (als Tuples).
                 Returns None if fetch='one' finds no rows. Returns empty list if fetch='all' finds no rows.
        :raises DatabaseQueryError: If the select operation fails.
        :raises ValueError: If query doesn't start with SELECT or fetch mode is invalid.
        """
        if not query.strip().upper().startswith("SELECT"):
             raise ValueError("Diese Methode ist nur für SELECT-Abfragen vorgesehen.")
        if fetch not in ['one', 'all']:
             raise ValueError("Ungültiger fetch-Modus. Nur 'one' oder 'all'.")
        if params is not None and not isinstance(params, tuple):
            raise ValueError("params muss None oder ein Tuple sein.")

        try:
            # Delegate with correct fetch mode
            results = self.execute_query(query, params, fetch=fetch)

            fetch_msg = "eine Zeile" if fetch == 'one' else "alle Zeilen"
            count_msg = ""
            if fetch == 'one':
                 count_msg = "Eine Zeile gefunden." if results else "Keine Zeile gefunden."
            elif fetch == 'all':
                 count_msg = f"{len(results)} Zeile(n) gefunden."

            print(f"SELECT-Abfrage ausgeführt ({self.db_type_name}, Fetch: {fetch_msg}). {count_msg}")
            return results
        except (DatabaseQueryError, ValueError) as e:
            print(f"Fehler beim Ausführen der SELECT-Abfrage ({self.db_type_name}): {e}")
            raise
        except Exception as e:
            print(f"Unerwarteter Fehler bei SELECT ({self.db_type_name}): {e}")
            raise DatabaseQueryError(f"Unerwarteter Fehler bei SELECT: {e}") from e


    def select_all(self, table: str) -> list:
        """
        Liest alle Datensätze aus einer Tabelle (vereinfachte Methode).

        :param table: Name der Tabelle.
        :return: Liste von Datensätzen (jeder Datensatz als Tuple). Leere Liste wenn Tabelle leer.
        :raises DatabaseQueryError: If the select operation fails.
        """
        # Quote table name
        query = f"SELECT * FROM `{table}`"
        # Reuse the more generic select method, uses %s implicitly (as there are no params)
        return self.select(query, fetch='all')


# --- Beispielhafte Nutzung (Angepasst an die neue Struktur) ---

def sqlite_example():
    print("\n=== Beispiel: SQLite (Refactored) ===")
    db_file = "example_refactored.db"
    db_dir = "temp_db_files_refactored"
    full_db_path = os.path.join(db_dir, db_file)

    # Clean up previous run directory
    if os.path.exists(db_dir):
        import shutil
        try:
            shutil.rmtree(db_dir)
            print(f"Altes Verzeichnis '{db_dir}' gelöscht.")
        except OSError as e:
            print(f"Fehler beim Löschen des alten Verzeichnisses '{db_dir}': {e}")

    try:
        # 1. Erstelle den spezifischen Operator
        sqlite_op = SQLiteInterface(database=full_db_path)

        # 2. Erstelle den BasicDBConnector mit dem Operator
        #    Verwende 'with' für automatisches connect/disconnect
        with BasicDBConnector(sqlite_op) as db:
            # Tabelle erstellen (verwende %s Platzhalter - SQLiteConnector passt intern an)
            create_table_query = """
            CREATE TABLE IF NOT EXISTS personen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                alter INTEGER CHECK(alter > 0)
            )
            """
            db.execute_query(create_table_query)

            # Datensätze einfügen
            inserted_id_1 = db.insert("personen", {"name": "Max Mustermann", "alter": 30})
            inserted_id_2 = db.insert("personen", {"name": "Maria Musterfrau", "alter": 28})
            print(f"Eingefügte IDs: {inserted_id_1}, {inserted_id_2}")

            # Versuch, doppelten Namen einzufügen
            try:
                 db.insert("personen", {"name": "Max Mustermann", "alter": 35})
            except DatabaseQueryError as e:
                 print(f"\nErwarteter Fehler beim Einfügen eines Duplikats (SQLite): {e}")

             # Versuch, ungültiges Alter einzufügen
            try:
                 db.insert("personen", {"name": "Negativ Alt", "alter": -5})
            except DatabaseQueryError as e:
                 print(f"\nErwarteter Fehler beim Einfügen mit ungültigem Alter (SQLite): {e}")

            # Alle Datensätze auslesen
            rows = db.select_all("personen")
            print("\nAktueller Inhalt der Tabelle 'personen':")
            for row in rows:
                print(row)

            # Datensatz aktualisieren (Max wird 31) - WHERE mit %s und Tuple!
            updated_count = db.update("personen", {"alter": 31}, "name = %s", ("Max Mustermann",))
            print(f"\nAnzahl aktualisierter Zeilen (Max): {updated_count}")

            # Einzelnen Datensatz lesen - WHERE mit %s und Tuple!
            max_data = db.select("SELECT id, name, alter FROM personen WHERE name = %s", ("Max Mustermann",), fetch='one')
            print(f"\nDaten für Max nach Update: {max_data}")

             # Datensatz löschen (Maria löschen) - WHERE mit %s und Tuple!
            deleted_count = db.delete("personen", "name = %s", ("Maria Musterfrau",))
            print(f"\nAnzahl gelöschter Zeilen (Maria): {deleted_count}")

            # Alle Datensätze erneut auslesen
            rows = db.select_all("personen")
            print("\nEndgültiger Inhalt der Tabelle 'personen':")
            for row in rows:
                print(row)

            # Beispiel für Fehler: Tabelle existiert nicht
            try:
                db.select_all("nicht_existente_tabelle")
            except DatabaseQueryError as e:
                print(f"\nErwarteter Fehler beim Zugriff auf nicht existente Tabelle (SQLite): {e}")

    except (DatabaseConnectionError, DatabaseQueryError, ValueError, ImportError, TypeError) as e:
        print(f"\nEin Fehler ist im SQLite-Beispiel aufgetreten: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"\nEin unerwarteter Fehler ist im SQLite-Beispiel aufgetreten: {type(e).__name__}: {e}")

    finally:
         print(f"\nSQLite Beispiel beendet. Datenbankdatei unter '{full_db_path}' (falls erstellt).")
         # Optional cleanup
         # if os.path.exists(db_dir):
         #    shutil.rmtree(db_dir)
         #    print(f"\nVerzeichnis '{db_dir}' zur Bereinigung gelöscht.")


def mysql_example():
    print("\n=== Beispiel: MySQL (Refactored) ===")

    # --- *** BENUTZERKONFIGURATION HIER *** ---
    db_config_server = {
        "host": "localhost",
        "user": "test",
        "password": "exec1234",
        # Kein 'database' hier für Server-Operationen
    }
    db_name_to_use = "test_basic_connector_refactored_db"
    # --- *** ENDE BENUTZERKONFIGURATION *** ---

    if not MYSQL_AVAILABLE:
        print("MySQL-Beispiel übersprungen: mysql-connector-python nicht installiert oder fehlerhaft.")
        return

    # Verwende separate Operatoren für Server-Tasks und DB-Tasks
    server_operator = None
    db_operator = None
    cleanup_operator = None

    try:
        # 1. Operator und Connector zum Server erstellen für Checks/Erstellung
        server_operator = MySQLInterface(**db_config_server)
        connector_server = BasicDBConnector(server_operator) # Kein 'with' hier, manuelles Management

        # 2. Datenbank erstellen (falls nicht vorhanden) über den Server-Connector
        connector_server.create_database(db_name_to_use)
        # Wichtig: Server-Connector nach Nutzung trennen, wenn nicht mehr gebraucht
        connector_server.disconnect() # Manually disconnect after create

        # 3. Jetzt Operator und Connector für die spezifische Datenbank
        db_config_with_db = db_config_server.copy()
        db_config_with_db["database"] = db_name_to_use
        db_operator = MySQLConnector(**db_config_with_db)

        #    Verwende 'with' für die Arbeit IN der Datenbank
        with BasicDBConnector(db_operator) as db:
            # Tabelle erstellen (IF NOT EXISTS ist sicher) - %s wird direkt verwendet
            create_table_query = """
            CREATE TABLE IF NOT EXISTS personen (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                alter_jahre INT CHECK(alter_jahre > 0)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            db.execute_query(create_table_query)
            print(f"Tabelle 'personen' in '{db_name_to_use}' sichergestellt.")

            # Datensatz einfügen
            inserted_id = db.insert("personen", {"name": "Max Mustermann", "alter_jahre": 30})
            print(f"Eingefügte ID (Max): {inserted_id}")

            # Versuch Duplikat einzufügen
            try:
                 db.insert("personen", {"name": "Max Mustermann", "alter_jahre": 40})
            except DatabaseQueryError as e:
                 print(f"\nErwarteter Fehler (MySQL UNIQUE): {e}")

            # Versuch ungültiges Alter
            try:
                 # MySQL < 8.0.16 ignoriert CHECK Constraints oft standardmäßig
                 db.insert("personen", {"name": "Zu Jung", "alter_jahre": 0})
                 print("\nHinweis: Einfügen mit alter_jahre=0 war erfolgreich (CHECK evtl. ignoriert).")
            except DatabaseQueryError as e:
                 print(f"\nFehler (MySQL CHECK): {e}")

            # Weiteren Datensatz einfügen
            db.insert("personen", {"name": "Maria Musterfrau", "alter_jahre": 29})

            # Alle Datensätze auslesen
            rows = db.select_all("personen")
            print("\nAktueller Inhalt der Tabelle 'personen':", rows)

            # Datensatz aktualisieren (WHERE mit %s und Tuple!)
            updated_count = db.update("personen", {"alter_jahre": 32}, "name = %s", ("Max Mustermann",))
            print(f"\nAnzahl aktualisierter Zeilen (Max): {updated_count}")

            # Datensatz löschen (anhand der ID) - WHERE mit %s und Tuple!
            if inserted_id:
                 deleted_count = db.delete("personen", "id = %s", (inserted_id,))
                 print(f"\nAnzahl gelöschter Zeilen (ID {inserted_id}): {deleted_count}")
            else:
                 print("\nKonnte Datensatz (Max) nicht anhand der ID löschen.")

            rows = db.select_all("personen")
            print("\nEndgültiger Inhalt der Tabelle 'personen':", rows)

    except (DatabaseConnectionError, DatabaseQueryError, ValueError, ImportError, TypeError) as e:
        print(f"\nEin Fehler ist im MySQL-Beispiel aufgetreten: {type(e).__name__}: {e}")
    except Exception as e:
        print(f"\nEin unerwarteter Fehler ist im MySQL-Beispiel aufgetreten: {type(e).__name__}: {e}")

    finally:
        # Cleanup: Drop the test database
        print("\nOptional: Versuche MySQL Test-Datenbank zu bereinigen (erfordert DROP-Rechte)")
        if MYSQL_AVAILABLE and 'user' in db_config_server:
            cleanup_connector = None # Define here to ensure disconnect happens
            try:
                # Use the server configuration (no database specified)
                cleanup_operator = MySQLConnector(**db_config_server)
                cleanup_connector = BasicDBConnector(cleanup_operator)

                # Check existence using the cleanup connector instance
                if cleanup_connector.database_exists(db_name_to_use):
                    # Use execute_query from the *cleanup_connector* instance
                    # Ensure the name is quoted properly
                    cleanup_connector.execute_query(f"DROP DATABASE IF EXISTS `{db_name_to_use}`")
                    print(f"Test-Datenbank '{db_name_to_use}' erfolgreich gelöscht.")
                else:
                    print(f"Test-Datenbank '{db_name_to_use}' nicht gefunden zum Löschen.")

            except (DatabaseConnectionError, DatabaseQueryError, ImportError, ValueError, TypeError) as e:
                 print(f"Fehler beim Löschen der Test-Datenbank '{db_name_to_use}': {e}")
            except Exception as e:
                print(f"Unerwarteter Fehler beim Aufräumen der MySQL DB: {type(e).__name__}: {e}")
            finally:
                 # Ensure the cleanup connector is disconnected if it was created/connected
                 if cleanup_connector:
                     cleanup_connector.disconnect()
        else:
            print("MySQL nicht verfügbar oder Konfiguration unvollständig - Bereinigung übersprungen.")
        print("MySQL Beispiel beendet.")


# --- Hauptausführung ---
if __name__ == "__main__":
    sqlite_example()

    # --- MySQL Beispiel aktivieren ---
    # Stelle sicher, dass die Konfiguration in mysql_example() korrekt ist.
    mysql_example()
    # --------------------------------

    print("\n=== Alle Beispiele abgeschlossen ===")