# --- Beispielhafte Nutzung (Angepasst an die neue Struktur) ---

import os
import sys
from pathlib import Path

sys.path.insert(0, Path(__file__).parent.parent.__str__())
from src.backend.basic_db_connector import BasicDBConnector
from src.backend import SQLiteInterface
from src.backend import MySQLInterface
from src.backend import DatabaseConnectionError, DatabaseQueryError, MYSQL_AVAILABLE






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
        db_operator = MySQLInterface(**db_config_with_db)

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
                cleanup_operator = MySQLInterface(**db_config_server)
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