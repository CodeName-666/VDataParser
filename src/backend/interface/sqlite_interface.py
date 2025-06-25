import sqlite3
"""SQLite implementation of :class:`DatabaseOperations`."""

import os


from .common_interface import (
    DatabaseConnectionError,
    DatabaseQueryError,
    DatabaseOperations
    )



class SQLiteInterface(DatabaseOperations):
    """Concrete :class:`DatabaseOperations` for SQLite databases."""

    def __init__(self, **kwargs):
        """Initialise the interface and check required ``database`` parameter."""
        super().__init__(kwargs)
        if not self.params.get("database"):
             raise ValueError("SQLiteInterface requires a 'database' file path.")
        self._db_path_template = self.params["database"]

    def get_placeholder_style(self) -> str:
        """Return the SQLite placeholder style."""
        return "?"

    def get_db_specific_error_types(self) -> tuple:
        """Return the tuple of SQLite error classes."""
        return (sqlite3.Error,)

    def connect_db(self, database_override: str = None):
        """Open a SQLite connection to the given or configured file."""
        db_to_connect = database_override or self._db_path_template
        if not db_to_connect:
             raise ValueError("Kein Dateipfad für SQLite-Verbindung angegeben.")

        # Ensure the directory exists
        db_dir = os.path.dirname(db_to_connect)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                print(f"Verzeichnis '{db_dir}' für SQLite-Datenbank erstellt.")
            except OSError as e:
                raise DatabaseConnectionError(f"Konnte Verzeichnis für SQLite DB nicht erstellen: {e}") from e

        print(f"Versuche Verbindung zu SQLite ('{db_to_connect}')...")
        try:
            conn = sqlite3.connect(db_to_connect)
            # Check usability
            try:
                with conn.cursor() as cursor:
                    cursor.execute("PRAGMA quick_check;")
            except sqlite3.Error as e:
                conn.close()
                raise DatabaseConnectionError(f"SQLite connection established but seems unusable: {e}") from e
            print(f"SQLite-Verbindung zu '{db_to_connect}' erfolgreich hergestellt.")
            return conn
        except sqlite3.Error as e:
            raise DatabaseConnectionError(f"Fehler beim Verbinden (SQLite): {e}") from e

    def disconnect_db(self, conn):
        """Close the SQLite connection if open."""
        if conn:
            try:
                conn.close()
                print("Verbindung zur SQLite-Datenbank wurde getrennt.")
            except sqlite3.Error as e:
                 print(f"Fehler beim Trennen der SQLite-Verbindung: {e}")

    def execute_db_query(self, conn, query: str, params: tuple = None, fetch: str = None):
        """Execute ``query`` on ``conn`` and optionally fetch results."""
        if not conn:
             raise DatabaseConnectionError("No active SQLite connection for query.")

        # Adapt placeholder style for SQLite
        internal_query = query.replace('%s', '?')
        original_query_for_error = query # Keep original for error messages

        cursor = None
        is_modifying_query = False
        try:
            cursor = conn.cursor()
            print(f"Executing Query (SQLITE): {internal_query} | Params: {params}")

            if params:
                cursor.execute(internal_query, params)
            else:
                cursor.execute(internal_query)

            query_upper_stripped = internal_query.strip().upper()
            is_modifying_query = not (query_upper_stripped.startswith("SELECT") or query_upper_stripped.startswith("PRAGMA"))

            if is_modifying_query:
                conn.commit()
                print("Änderungen committed (SQLite).")

            result_data = None
            if fetch == 'one':
                result_data = cursor.fetchone()
            elif fetch == 'all':
                result_data = cursor.fetchall()
            elif fetch == 'cursor':
                 print("WARNUNG: SQLITE-Cursor wird zurückgegeben; Schließen liegt in der Verantwortung des Aufrufers.")
                 return cursor # EARLY RETURN
            else:
                result_data = {
                    "rowcount": cursor.rowcount,
                    "lastrowid": getattr(cursor, 'lastrowid', None)
                 }
            return result_data
        except sqlite3.Error as e:
             db_error_type = f"{type(e).__name__} (SQLITE)"
             print(f"{db_error_type} bei der Ausführung der Abfrage: {e}")
             if is_modifying_query:
                 try:
                     conn.rollback()
                     print("Rollback durchgeführt wegen Fehler (SQLite).")
                 except Exception as rb_e:
                     print(f"Fehler beim Rollback nach SQLite Query-Fehler: {rb_e}")
             raise DatabaseQueryError(f"Fehler bei SQL-Ausführung ({db_error_type}): {e}\nQuery: {original_query_for_error}\nParams: {params}") from e
        finally:
             if cursor is not None and fetch != 'cursor': # Close only if not returned
                 try:
                     cursor.close()
                 except Exception as final_close_e:
                     print(f"Warnung: Fehler beim Schließen des SQLite Cursors im Finally-Block: {final_close_e}")

    def check_database_exists(self, db_name: str) -> bool:
        """Return ``True`` if the SQLite file exists."""
        exists = os.path.exists(db_name)
        print(f"SQLite-Datenbankdatei '{db_name}' existiert: {exists}")
        return exists

    def create_db(self, new_db_name: str):
        """Create a new SQLite database file if needed."""
        if not new_db_name:
             raise ValueError("Dateipfad (new_db_name) für SQLite muss angegeben werden.")
        if os.path.exists(new_db_name):
             print(f"SQLite-Datenbankdatei '{new_db_name}' existiert bereits.")
             return

        # Ensure directory exists
        db_dir = os.path.dirname(new_db_name)
        if db_dir and not os.path.exists(db_dir):
            try:
                os.makedirs(db_dir, exist_ok=True)
                print(f"Verzeichnis '{db_dir}' für SQLite-Datenbank erstellt.")
            except OSError as e:
                raise DatabaseConnectionError(f"Konnte Verzeichnis für SQLite DB nicht erstellen: {e}") from e

        print(f"Versuche SQLite-Datenbankdatei '{new_db_name}' zu erstellen...")
        temp_conn = None
        try:
            temp_conn = sqlite3.connect(new_db_name) # Creates file
            # Verify writability
            try:
                 with temp_conn.cursor() as cur:
                     cur.execute("CREATE TABLE IF NOT EXISTS __verify_create__ (id INTEGER);")
                     cur.execute("DROP TABLE IF EXISTS __verify_create__;")
                 temp_conn.commit()
            except sqlite3.Error as check_e:
                 raise DatabaseConnectionError(f"Konnte SQLite-DB erstellen, aber sie ist nicht beschreibbar: {check_e}") from check_e
            print(f"SQLite-Datenbankdatei '{new_db_name}' erfolgreich erstellt und geprüft.")
        except sqlite3.Error as e:
            raise DatabaseConnectionError(f"Fehler beim Erstellen der SQLite-Datenbankdatei '{new_db_name}': {e}") from e
        finally:
            if temp_conn:
                try:
                    temp_conn.close()
                except sqlite3.Error as close_e:
                    print(f"Warnung: Fehler beim Schließen der temporären SQLite Verbindung: {close_e}")