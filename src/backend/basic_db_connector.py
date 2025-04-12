import sqlite3
import os
import importlib  # To handle optional mysql import

# Try to import mysql.connector, but don't fail if it's not installed
try:
    # Attempt to import the specific module needed
    mysql_connector = importlib.import_module('mysql.connector')
    # Additionally, try accessing an attribute to catch potential installation issues beyond simple import
    _ = mysql_connector.errorcode
    MYSQL_AVAILABLE = True
    print("mysql-connector-python wurde erfolgreich gefunden.")
except ImportError:
    mysql_connector = None
    MYSQL_AVAILABLE = False
    print("WARNUNG: mysql-connector-python nicht gefunden. MySQL-Funktionalität ist deaktiviert.")
except AttributeError:
    # Handle cases where mysql.connector exists but might be incomplete/corrupted
    mysql_connector = None
    MYSQL_AVAILABLE = False
    print("WARNUNG: mysql.connector Modul gefunden, aber es scheint unvollständig. MySQL-Funktionalität ist deaktiviert.")


class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors."""
    pass


class DatabaseQueryError(Exception):
    """Custom exception for query execution errors."""
    pass


class BasicDBConnector:
    def __init__(self, db_type: str, **kwargs):
        """
        Grundlegender DB-Connector.

        :param db_type: "mysql" oder "sqlite"
        :param kwargs: Parameter je nach DB-Typ
            Für MySQL: host, user, password, database (optional für connect)
            Für SQLite: database (Dateipfad)
        :raises ValueError: If db_type is unsupported.
        :raises ImportError: If MySQL is requested but 'mysql-connector-python' is not properly installed.
        """
        self.db_type = db_type.lower()
        self.params = kwargs
        self.conn = None
        # No internal cursor attribute needed now, managed per-call

        if self.db_type not in ["mysql", "sqlite"]:
            raise ValueError("Nicht unterstützter DB-Typ. Bitte 'mysql' oder 'sqlite' verwenden.")
        if self.db_type == "mysql" and not MYSQL_AVAILABLE:
            # Raise ImportError earlier if MySQL is explicitly requested but unavailable
            raise ImportError("MySQL wurde angefordert, aber 'mysql-connector-python' ist nicht installiert oder fehlerhaft.")

    def connect(self, database_override: str = None):
        """
        Stellt die Verbindung zur Datenbank her.

        :param database_override: Optional database name/file to connect to,
                                   overriding the one in __init__. Useful for
                                   operations like creating a database.
        :raises DatabaseConnectionError: If connection fails.
        """
        if self.conn:
            # Avoid reconnecting if already connected, maybe log instead of print?
            print(f"Bereits verbunden ({self.db_type}).")
            return

        db_to_connect = database_override

        try:
            if self.db_type == "mysql":
                if not MYSQL_AVAILABLE: # Double check, though __init__ should catch it
                    raise ImportError("MySQL nicht verfügbar.")

                if not db_to_connect:
                     db_to_connect = self.params.get("database") # Use init param if no override

                print(f"Versuche Verbindung zu MySQL ({self.params.get('host', 'localhost')}, DB: {db_to_connect or 'Server'})...")
                self.conn = mysql_connector.connect(
                    host=self.params.get("host", "localhost"),
                    user=self.params.get("user"),
                    password=self.params.get("password"),
                    database=db_to_connect # Can be None initially
                )
                # Check connection status explicitly for MySQL
                if not self.conn.is_connected():
                     # This case might be rare if connect() didn't raise an error, but good practice
                     raise DatabaseConnectionError("MySQL connection failed after connect call (is_connected() is False).")
                print(f"MySQL-Verbindung {'zu ' + db_to_connect if db_to_connect else 'zum Server'} erfolgreich hergestellt.")

            elif self.db_type == "sqlite":
                if not db_to_connect:
                    db_to_connect = self.params.get("database")
                if not db_to_connect:
                     raise ValueError("Für SQLite muss ein 'database'-Parameter (Dateipfad) angegeben werden.")

                # Ensure the directory exists for the SQLite file
                db_dir = os.path.dirname(db_to_connect)
                if db_dir and not os.path.exists(db_dir):
                    try:
                        os.makedirs(db_dir, exist_ok=True)
                        print(f"Verzeichnis '{db_dir}' für SQLite-Datenbank erstellt.")
                    except OSError as e:
                        raise DatabaseConnectionError(f"Konnte Verzeichnis für SQLite DB nicht erstellen: {e}") from e

                print(f"Versuche Verbindung zu SQLite ('{db_to_connect}')...")
                self.conn = sqlite3.connect(db_to_connect)
                # Check if connection is truly usable (e.g., execute a simple PRAGMA)
                try:
                    with self.conn.cursor() as cursor: # sqlite3 connection object *does* support context management
                         cursor.execute("PRAGMA quick_check;")
                except sqlite3.Error as e:
                    self.conn.close() # Close unusable connection
                    self.conn = None
                    raise DatabaseConnectionError(f"SQLite connection established but seems unusable: {e}") from e

                print(f"SQLite-Verbindung zu '{db_to_connect}' erfolgreich hergestellt.")

        # Catch specific DB errors first if available
        except (mysql_connector.Error if MYSQL_AVAILABLE else tuple(), sqlite3.Error) as e:
            self.conn = None # Ensure connection is None on failure
            raise DatabaseConnectionError(f"Fehler beim Verbinden ({self.db_type}): {e}") from e
        # Catch other potential issues like ValueError or unexpected errors
        except (ValueError, ImportError, Exception) as e:
            self.conn = None
            raise DatabaseConnectionError(f"Fehler beim Verbindungsaufbau ({self.db_type}): {e}") from e


    def disconnect(self):
        """Beendet die Verbindung zur Datenbank."""
        if self.conn:
            db_type_msg = self.db_type # Store type before conn is potentially None
            try:
                self.conn.close()
                self.conn = None
                print(f"Verbindung zur {db_type_msg.upper()}-Datenbank wurde getrennt.")
            except (mysql_connector.Error if MYSQL_AVAILABLE else Exception, sqlite3.Error) as e:
                 print(f"Fehler beim Trennen der {db_type_msg.upper()}-Verbindung: {e}")
                 # Even if close fails, set conn to None to reflect intent
                 self.conn = None
        else:
            print("Keine aktive Datenbankverbindung zum Trennen vorhanden.")

    def __enter__(self):
        """Ermöglicht die Nutzung mit 'with'-Statement (stellt Verbindung her)."""
        if not self.conn:
             self.connect() # connect() raises error on failure
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ermöglicht die Nutzung mit 'with'-Statement (trennt Verbindung)."""
        self.disconnect()
        # Optional: return False to propagate exceptions occurring within the 'with' block
        return False

    def database_exists(self, db_name: str) -> bool:
        """
        Prüft, ob eine Datenbank existiert. Verwendet manuelle Cursor-Verwaltung.

        :param db_name: Name der Datenbank (bei MySQL) oder Dateipfad (bei SQLite)
        :return: True, falls die Datenbank existiert, sonst False.
        :raises DatabaseConnectionError: If unable to check (e.g., MySQL server down).
        :raises ValueError: If db_type is unsupported.
        """
        if self.db_type == "mysql":
            if not MYSQL_AVAILABLE:
                raise ImportError("MySQL nicht verfügbar für Existenzprüfung.")

            temp_conn = None
            cursor = None
            try:
                print(f"Prüfe Existenz der MySQL DB '{db_name}'...")
                # Connect without specifying a database initially
                temp_conn = mysql_connector.connect(
                    host=self.params.get("host", "localhost"),
                    user=self.params.get("user"),
                    password=self.params.get("password")
                )
                cursor = temp_conn.cursor() # Manually create cursor
                query = "SHOW DATABASES LIKE %s"
                cursor.execute(query, (db_name,))
                result = cursor.fetchone()
                exists = result is not None
                print(f"MySQL-Datenbank '{db_name}' existiert: {exists}")
                return exists
            except mysql_connector.Error as e:
                print(f"Fehler beim Überprüfen der MySQL-Datenbank '{db_name}': {e}")
                if hasattr(e, 'errno') and e.errno == mysql_connector.errorcode.ER_ACCESS_DENIED_ERROR:
                    print("Zugriff verweigert - Annahme: Existenz kann nicht bestätigt werden.")
                    return False # Or re-raise depending on desired behavior
                # Re-raise as a connection error if check failed due to connection issues
                raise DatabaseConnectionError(f"Konnte Existenz der MySQL DB '{db_name}' nicht prüfen: {e}") from e
            finally:
                # Ensure cursor is closed
                if cursor:
                    try: cursor.close()
                    except Exception as cur_e: print(f"Warnung: Fehler beim Schließen des MySQL-Prüf-Cursors: {cur_e}")
                # Ensure connection is closed
                if temp_conn and temp_conn.is_connected():
                    try: temp_conn.close()
                    except Exception as conn_e: print(f"Warnung: Fehler beim Schließen der temp. MySQL-Verbindung: {conn_e}")
                # print(f"Temporäre MySQL-Verbindung für Prüfung von '{db_name}' geschlossen.") # Optional Debug

        elif self.db_type == "sqlite":
            # SQLite check remains simple file existence
            exists = os.path.exists(db_name)
            print(f"SQLite-Datenbankdatei '{db_name}' existiert: {exists}")
            return exists
        else:
             raise ValueError("Unsupported DB-Typ für Existenzprüfung.")


    def create_database(self, new_db_name: str):
        """
        Erstellt eine neue Datenbank (MySQL) oder stellt sicher, dass die Datei existiert (SQLite).
        Verwendet manuelle Cursor-Verwaltung für MySQL.

        :param new_db_name: Name der zu erstellenden Datenbank/Datei.
        :raises DatabaseConnectionError: If unable to connect to create the database.
        :raises DatabaseQueryError: If the CREATE DATABASE statement fails (e.g., permissions).
        :raises ValueError: If database name is missing for SQLite or db_type is unsupported.
        :raises ImportError: If MySQL is requested but unavailable.
        """
        if self.db_type == "mysql":
            if not MYSQL_AVAILABLE:
                raise ImportError("MySQL nicht verfügbar zum Erstellen der Datenbank.")

            # Check existence first using the corrected method
            if self.database_exists(new_db_name):
                 print(f"MySQL-Datenbank '{new_db_name}' existiert bereits.")
                 return

            temp_conn = None
            cursor = None
            try:
                print(f"Versuche MySQL-Datenbank '{new_db_name}' zu erstellen...")
                temp_conn = mysql_connector.connect(
                    host=self.params.get("host", "localhost"),
                    user=self.params.get("user"),
                    password=self.params.get("password")
                )
                cursor = temp_conn.cursor() # Manual cursor
                # Use backticks for safety, especially if name could have special chars
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{new_db_name}`")
                # CREATE DATABASE might be implicitly committed, commit() is safe but possibly redundant
                temp_conn.commit()
                print(f"MySQL-Datenbank '{new_db_name}' erfolgreich erstellt oder existierte bereits.")

            except mysql_connector.Error as e:
                 raise DatabaseQueryError(f"Fehler beim Erstellen der MySQL-Datenbank '{new_db_name}': {e}") from e
            finally:
                # Ensure cursor is closed
                if cursor:
                    try: cursor.close()
                    except Exception as cur_e: print(f"Warnung: Fehler beim Schließen des MySQL-Create-Cursors: {cur_e}")
                # Ensure connection is closed
                if temp_conn and temp_conn.is_connected():
                    try: temp_conn.close()
                    except Exception as conn_e: print(f"Warnung: Fehler beim Schließen der temp. MySQL-Verbindung: {conn_e}")
                # print(f"Temporäre MySQL-Verbindung zum Erstellen von '{new_db_name}' geschlossen.") # Optional Debug

        elif self.db_type == "sqlite":
             if not new_db_name:
                 raise ValueError("Dateipfad (new_db_name) für SQLite muss angegeben werden.")
             if os.path.exists(new_db_name):
                 print(f"SQLite-Datenbankdatei '{new_db_name}' existiert bereits.")
                 return

             # Ensure directory exists first
             db_dir = os.path.dirname(new_db_name)
             if db_dir and not os.path.exists(db_dir):
                 try:
                     os.makedirs(db_dir, exist_ok=True)
                     print(f"Verzeichnis '{db_dir}' für SQLite-Datenbank erstellt.")
                 except OSError as e:
                     raise DatabaseConnectionError(f"Konnte Verzeichnis für SQLite DB nicht erstellen: {e}") from e

             print(f"Versuche SQLite-Datenbankdatei '{new_db_name}' zu erstellen...")
             try:
                 # Connecting automatically creates the file
                 temp_conn = sqlite3.connect(new_db_name)
                 # Optional: Perform a quick check to ensure writability
                 try:
                     with temp_conn.cursor() as cur:
                         cur.execute("CREATE TABLE IF NOT EXISTS __verify_create__ (id INTEGER);")
                         cur.execute("DROP TABLE IF EXISTS __verify_create__;")
                     temp_conn.commit()
                 except sqlite3.Error as check_e:
                     temp_conn.close() # Close if unusable
                     os.remove(new_db_name) # Attempt cleanup
                     raise DatabaseConnectionError(f"Konnte SQLite-DB erstellen, aber sie ist nicht beschreibbar: {check_e}") from check_e
                 temp_conn.close() # Close immediately, we just wanted to create it
                 print(f"SQLite-Datenbankdatei '{new_db_name}' erfolgreich erstellt und geprüft.")
             except sqlite3.Error as e:
                 raise DatabaseConnectionError(f"Fehler beim Erstellen der SQLite-Datenbankdatei '{new_db_name}': {e}") from e
        else:
             raise ValueError("Unsupported DB-Typ beim Erstellen der Datenbank.")


    def execute_query(self, query: str, params: tuple = None, fetch: str = None):
        """
        Führt eine SQL-Abfrage aus und verwaltet den Cursor manuell für beide DB-Typen.

        :param query: Die SQL-Abfrage (mit %s Platzhaltern).
        :param params: Optionales Tuple mit Werten für die Platzhalter.
        :param fetch: Art des Datenabrufs: None (default, für INSERT/UPDATE/DELETE),
                      'one' (für fetchone), 'all' (für fetchall).
        :return: Ergebnis der Abfrage (None, single row, list of rows) oder cursor attributes
                 like lastrowid/rowcount depending on context (see specific methods).
                 Returns the cursor itself ONLY if fetch is explicitly 'cursor' (use with caution).
        :raises DatabaseConnectionError: If not connected.
        :raises DatabaseQueryError: If query execution fails.
        """
        if not self.conn:
             raise DatabaseConnectionError("Nicht verbunden. Rufen Sie zuerst connect() auf oder verwenden Sie 'with'.")

        # Adapt placeholder style automatically for SQLite
        original_query = query
        if self.db_type == 'sqlite':
            # Basic replacement, assumes %s is not part of literal strings in the query
            query = query.replace('%s', '?')

        cursor = None # Initialize cursor variable outside try
        is_modifying_query = False # Flag to check if rollback makes sense

        try:
            cursor = self.conn.cursor() # Create cursor manually
            print(f"Executing Query ({self.db_type.upper()}): {query} | Params: {params}")

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Check if it looks like a modifying statement (basic check)
            # More robust checks might parse the SQL command more carefully
            query_upper_stripped = query.strip().upper()
            is_modifying_query = not (query_upper_stripped.startswith("SELECT") or query_upper_stripped.startswith("PRAGMA"))

            # Commit changes for modifying queries
            if is_modifying_query:
                self.conn.commit()
                print("Änderungen committed.")

            # Handle fetching results
            result_data = None
            if fetch == 'one':
                result_data = cursor.fetchone()
            elif fetch == 'all':
                result_data = cursor.fetchall()
            elif fetch == 'cursor':
                # WARNING: Caller must manage this cursor if requested!
                 print(f"WARNUNG: {self.db_type.upper()}-Cursor wird zurückgegeben; Schließen liegt in der Verantwortung des Aufrufers.")
                 # Don't close the cursor here, return it directly
                 return cursor # EARLY RETURN
            else: # Default case for INSERT/UPDATE/DELETE
                # Retrieve potentially useful info *before* closing cursor
                result_data = {
                    "rowcount": cursor.rowcount,
                    # lastrowid behavior varies; might be None/0/-1 or raise errors
                    # depending on statement type and DB driver.
                    "lastrowid": getattr(cursor, 'lastrowid', None) # Safely access lastrowid
                 }

            # If we are not returning the cursor itself, we can return the data
            # Cursor will be closed in finally block below
            return result_data

        # Catch specific DB errors first
        except (mysql_connector.Error if MYSQL_AVAILABLE else tuple(), sqlite3.Error) as e:
             db_error_type = f"{type(e).__name__} ({self.db_type.upper()})"
             print(f"{db_error_type} bei der Ausführung der Abfrage: {e}")
             # Attempt rollback only if it was likely a modifying query
             if is_modifying_query:
                 try:
                     self.conn.rollback()
                     print("Rollback durchgeführt wegen Fehler.")
                 except Exception as rb_e:
                     # Log rollback error but proceed with raising original query error
                     print(f"Fehler beim Rollback nach Query-Fehler: {rb_e}")
             # Use original_query in error for clarity
             raise DatabaseQueryError(f"Fehler bei SQL-Ausführung ({db_error_type}): {e}\nQuery: {original_query}\nParams: {params}") from e
        # Catch other potential programming errors
        except Exception as e:
            print(f"Unerwarteter Fehler bei Query-Ausführung: {e}")
            raise DatabaseQueryError(f"Unerwarteter Fehler: {e}\nQuery: {original_query}\nParams: {params}") from e

        finally:
             # Ensure cursor is closed *unless* fetch='cursor' was used (handled by early return)
             if cursor is not None:
                 try:
                     cursor.close()
                     # print(f"{self.db_type.upper()} Cursor geschlossen.") # Optional Debug
                 except Exception as final_close_e:
                     # Log error but don't overshadow original exception if one occurred
                     print(f"Warnung: Fehler beim Schließen des {self.db_type.upper()} Cursors im Finally-Block: {final_close_e}")


    def insert(self, table: str, data: dict) -> int | None:
        """
        Fügt einen neuen Datensatz in die angegebene Tabelle ein.

        :param table: Name der Tabelle.
        :param data: Dictionary mit Spaltennamen als Schlüssel und Werten.
        :return: Die ID des eingefügten Datensatzes (lastrowid) oder None bei Fehlern/wenn nicht zutreffend.
        :raises DatabaseQueryError: If the insert operation fails.
        :raises ValueError: If data dictionary is empty.
        """
        if not data:
            raise ValueError("Keine Daten zum Einfügen angegeben.")

        try:
            keys = list(data.keys())
            # Use backticks/quotes for identifiers for safety (MySQL uses backticks, SQLite allows various)
            # Using backticks generally works for both in simple cases.
            columns = ", ".join(f"`{k}`" for k in keys)
            # Use %s placeholder; execute_query adapts for SQLite
            placeholders = ", ".join(["%s"] * len(keys))
            # Quote table name as well
            query = f"INSERT INTO `{table}` ({columns}) VALUES ({placeholders})"
            values = tuple(data.values()) # Keep original order

            result = self.execute_query(query, values) # fetch=None is default
            inserted_id = result.get("lastrowid") if isinstance(result, dict) else None
            print(f"Eintrag in Tabelle '{table}' eingefügt. Last Insert ID: {inserted_id}")
            # 'lastrowid' might be 0 or None if not applicable/supported, handle gracefully
            return inserted_id
        except (DatabaseQueryError, ValueError) as e: # Catch expected errors
             print(f"Fehler beim Einfügen des Eintrags in '{table}': {e}")
             raise # Re-raise the specific exception
        except Exception as e: # Catch unexpected errors during construction/call
             print(f"Unerwarteter Fehler beim Einfügen in '{table}': {e}")
             raise DatabaseQueryError(f"Unerwarteter Fehler beim Einfügen: {e}") from e


    def update(self, table: str, data: dict, where_clause: str, where_params: tuple) -> int:
        """
        Aktualisiert bestehende Datensätze in einer Tabelle.

        :param table: Name der Tabelle.
        :param data: Dictionary mit den zu aktualisierenden Spalten und Werten.
        :param where_clause: SQL-Bedingung ohne 'WHERE' (z.B., "id = %s AND name = %s").
                             Verwenden Sie %s als Platzhalter.
        :param where_params: Tuple mit Werten für die Platzhalter in where_clause.
        :return: Anzahl der aktualisierten Zeilen (rowcount). Returns 0 if no rows matched.
        :raises DatabaseQueryError: If the update operation fails.
        :raises ValueError: If data or where_clause/where_params are missing or invalid.
        """
        if not data:
             raise ValueError("Keine Daten zum Aktualisieren angegeben.")
        if not where_clause or where_params is None: # Check for None explicitly
             raise ValueError("where_clause und where_params sind für UPDATE erforderlich.")
        if not isinstance(where_params, tuple):
             # Enforce tuple for clarity and consistency with execute_query expecting tuples
             raise ValueError("where_params muss ein Tuple sein.")


        try:
            # Use %s placeholder, execute_query adapts if needed
            # Quote identifiers
            set_clause = ", ".join([f"`{col}` = %s" for col in data.keys()])
            query = f"UPDATE `{table}` SET {set_clause} WHERE {where_clause}"

            # Combine values for SET and WHERE clauses
            update_values = tuple(data.values())
            params = update_values + where_params # where_params is already a tuple

            result = self.execute_query(query, params) # fetch=None is default
            rowcount = result.get("rowcount", 0) if isinstance(result, dict) else 0
            print(f"{rowcount} Eintrag/Einträge in Tabelle '{table}' aktualisiert (basierend auf WHERE).")
            return rowcount
        except (DatabaseQueryError, ValueError) as e:
             print(f"Fehler beim Aktualisieren von Einträgen in '{table}': {e}")
             raise
        except Exception as e:
             print(f"Unerwarteter Fehler beim Aktualisieren in '{table}': {e}")
             raise DatabaseQueryError(f"Unerwarteter Fehler beim Update: {e}") from e


    def delete(self, table: str, where_clause: str, where_params: tuple) -> int:
        """
        Löscht Datensätze aus einer Tabelle basierend auf einer Bedingung.

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
            # Quote table name
            query = f"DELETE FROM `{table}` WHERE {where_clause}"

            result = self.execute_query(query, where_params) # fetch=None is default
            rowcount = result.get("rowcount", 0) if isinstance(result, dict) else 0
            print(f"{rowcount} Eintrag/Einträge aus Tabelle '{table}' gelöscht (basierend auf WHERE).")
            return rowcount
        except (DatabaseQueryError, ValueError) as e:
            print(f"Fehler beim Löschen von Einträgen aus '{table}': {e}")
            raise
        except Exception as e:
            print(f"Unerwarteter Fehler beim Löschen aus '{table}': {e}")
            raise DatabaseQueryError(f"Unerwarteter Fehler beim Delete: {e}") from e

    def select(self, query: str, params: tuple = None, fetch: str = 'all'):
        """
        Führt eine SELECT-Abfrage aus und gibt die Ergebnisse zurück.

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
            results = self.execute_query(query, params, fetch=fetch)
            fetch_msg = "eine Zeile" if fetch == 'one' else "alle Zeilen"
            count_msg = ""
            if fetch == 'one':
                 count_msg = "Eine Zeile gefunden." if results else "Keine Zeile gefunden."
            elif fetch == 'all':
                 count_msg = f"{len(results)} Zeile(n) gefunden."

            print(f"SELECT-Abfrage ausgeführt (Fetch: {fetch_msg}). {count_msg}")
            return results
        except (DatabaseQueryError, ValueError) as e:
            print(f"Fehler beim Ausführen der SELECT-Abfrage: {e}")
            raise
        except Exception as e:
            print(f"Unerwarteter Fehler bei SELECT: {e}")
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
        # Reuse the more generic select method
        return self.select(query, fetch='all')


# --- Beispielhafte Nutzung ---

def sqlite_example():
    print("\n=== Beispiel: SQLite ===")
    db_file = "example_final.db"
    db_dir = "temp_db_files"
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
        # Use 'with' statement for automatic connect/disconnect
        # The connector handles directory creation inside connect()
        with BasicDBConnector("sqlite", database=full_db_path) as db:
            # Tabelle erstellen
            create_table_query = """
            CREATE TABLE IF NOT EXISTS personen (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE, -- Name sollte einzigartig sein
                alter INTEGER CHECK(alter > 0) -- Alter sollte positiv sein
            )
            """
            db.execute_query(create_table_query) # No fetch needed

            # Datensätze einfügen
            inserted_id_1 = db.insert("personen", {"name": "Max Mustermann", "alter": 30})
            inserted_id_2 = db.insert("personen", {"name": "Maria Musterfrau", "alter": 28})
            print(f"Eingefügte IDs: {inserted_id_1}, {inserted_id_2}")

            # Versuch, doppelten Namen einzufügen (sollte fehlschlagen wegen UNIQUE Constraint)
            try:
                 db.insert("personen", {"name": "Max Mustermann", "alter": 35})
            except DatabaseQueryError as e:
                 print(f"\nErwarteter Fehler beim Einfügen eines Duplikats: {e}")

             # Versuch, ungültiges Alter einzufügen (sollte fehlschlagen wegen CHECK Constraint)
            try:
                 db.insert("personen", {"name": "Negativ Alt", "alter": -5})
            except DatabaseQueryError as e:
                 print(f"\nErwarteter Fehler beim Einfügen mit ungültigem Alter: {e}")


            # Alle Datensätze auslesen
            rows = db.select_all("personen")
            print("\nAktueller Inhalt der Tabelle 'personen':")
            for row in rows:
                print(row)

            # Datensatz aktualisieren (Max wird 31) - Korrekte WHERE Parameter als Tupel!
            updated_count = db.update("personen", {"alter": 31}, "name = %s", ("Max Mustermann",))
            print(f"\nAnzahl aktualisierter Zeilen (Max): {updated_count}")

            # Einzelnen Datensatz lesen
            max_data = db.select("SELECT id, name, alter FROM personen WHERE name = %s", ("Max Mustermann",), fetch='one')
            print(f"\nDaten für Max nach Update: {max_data}")

             # Datensatz löschen (Maria löschen) - Korrekte WHERE Parameter als Tupel!
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
                print(f"\nErwarteter Fehler beim Zugriff auf nicht existente Tabelle: {e}")

    except (DatabaseConnectionError, DatabaseQueryError, ValueError, ImportError) as e:
        print(f"\nEin Fehler ist im SQLite-Beispiel aufgetreten: {e}")
    except Exception as e:
        print(f"\nEin unerwarteter Fehler ist im SQLite-Beispiel aufgetreten: {type(e).__name__}: {e}")

    finally:
         # Optional: Keep the directory for inspection
         print(f"\nSQLite Beispiel beendet. Datenbankdatei unter '{full_db_path}' (falls erstellt).")
         # if os.path.exists(db_dir):
         #    shutil.rmtree(db_dir)
         #    print(f"\nVerzeichnis '{db_dir}' zur Bereinigung gelöscht.")


def mysql_example():
    # Beispiel für MySQL (Setze deine Zugangsdaten ein!)
    # WICHTIG: Der Benutzer benötigt Rechte, um Datenbanken zu erstellen und
    #          Tabellen in der Zieldatenbank zu erstellen/lesen/schreiben/löschen.
    print("\n=== Beispiel: MySQL ===")

    # --- *** BENUTZERKONFIGURATION HIER *** ---
    db_config_server = {
        "host": "localhost",        # Oder deine MySQL-Host-IP/Name
        "user": "test",             # Dein MySQL-Benutzer (mit CREATE DB Rechten)
        "password": "exec1234", # Dein MySQL-Passwort
    }
    db_name_to_use = "test_basic_connector_db"
    # --- *** ENDE BENUTZERKONFIGURATION *** ---


    if not MYSQL_AVAILABLE:
        print("MySQL-Beispiel übersprungen: mysql-connector-python nicht installiert oder fehlerhaft.")
        return

    connector_server = None # For initial checks/creation
    connector_db = None     # For operations within the specific DB

    try:
        # 1. Connector zum Server erstellen (ohne DB) für Checks/Erstellung
        connector_server = BasicDBConnector("mysql", **db_config_server)

        # 2. Datenbank erstellen (falls nicht vorhanden)
        # This internally connects/disconnects to the server
        connector_server.create_database(db_name_to_use)

        # 3. Jetzt mit der spezifischen Datenbank verbinden mittels 'with'
        db_config_with_db = db_config_server.copy()
        db_config_with_db["database"] = db_name_to_use

        with BasicDBConnector("mysql", **db_config_with_db) as db: # New instance or reconfigure
            connector_db = db # Keep reference if needed outside 'with', though bad practice

            # Tabelle erstellen (IF NOT EXISTS ist sicher)
            create_table_query = """
            CREATE TABLE IF NOT EXISTS personen (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE, -- Name sollte einzigartig sein
                alter_jahre INT CHECK(alter_jahre > 0) -- Spaltenname geändert, Alter positiv
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
                 db.insert("personen", {"name": "Zu Jung", "alter_jahre": 0})
            except DatabaseQueryError as e:
                 # Note: CHECK constraints might be ignored by older MySQL versions or specific configs
                 print(f"\nFehler (MySQL CHECK - könnte ignoriert werden): {e}")

            # Weiteren Datensatz einfügen
            db.insert("personen", {"name": "Maria Musterfrau", "alter_jahre": 29})


            # Alle Datensätze auslesen
            rows = db.select_all("personen")
            print("\nAktueller Inhalt der Tabelle 'personen':", rows)

            # Datensatz aktualisieren (WHERE Params als Tuple!)
            updated_count = db.update("personen", {"alter_jahre": 32}, "name = %s", ("Max Mustermann",))
            print(f"\nAnzahl aktualisierter Zeilen (Max): {updated_count}")

            # Datensatz löschen (anhand der ID, falls vorhanden - WHERE Params als Tuple!)
            if inserted_id:
                 deleted_count = db.delete("personen", "id = %s", (inserted_id,))
                 print(f"\nAnzahl gelöschter Zeilen (ID {inserted_id}): {deleted_count}")
            else:
                 print("\nKonnte Datensatz (Max) nicht anhand der ID löschen, da keine ID zurückgegeben wurde oder verloren ging.")


    except (DatabaseConnectionError, DatabaseQueryError, ValueError, ImportError) as e:
        print(f"\nEin Fehler ist im MySQL-Beispiel aufgetreten: {type(e).__name__}: {e}")
    except Exception as e:
        # Catch potential specific MySQL errors if needed, or just general unexpected ones
        print(f"\nEin unerwarteter Fehler ist im MySQL-Beispiel aufgetreten: {type(e).__name__}: {e}")

    finally:
        # Optional: Clean up - Drop the test database
        # Vorsicht: Nur in Testumgebungen ausführen!
        print("\nOptional: Versuche MySQL Test-Datenbank zu bereinigen (erfordert DROP-Rechte)")
        cleanup_connector = None
        if MYSQL_AVAILABLE and 'user' in db_config_server: # Ensure config is available
            try:
                # Need connection without specific DB to drop it
                cleanup_connector = BasicDBConnector("mysql", **db_config_server) # Use server config
                # Check existence again before dropping using the instance method
                if cleanup_connector.database_exists(db_name_to_use):
                    # Use execute_query from the *cleanup_connector* instance
                    # Ensure the name is quoted properly
                    cleanup_connector.execute_query(f"DROP DATABASE IF EXISTS `{db_name_to_use}`")
                    print(f"Test-Datenbank '{db_name_to_use}' erfolgreich gelöscht.")
                else:
                    print(f"Test-Datenbank '{db_name_to_use}' wurde nicht gefunden zum Löschen (vielleicht schon gelöscht oder nie erstellt).")

            except (DatabaseConnectionError, DatabaseQueryError, ImportError) as e:
                 print(f"Fehler beim Löschen der Test-Datenbank '{db_name_to_use}': {e}")
            except Exception as e:
                print(f"Unerwarteter Fehler beim Aufräumen der MySQL DB: {type(e).__name__}: {e}")
            finally:
                 # Ensure the cleanup connector is disconnected if it was created
                 if cleanup_connector:
                     cleanup_connector.disconnect()
        else:
            print("MySQL nicht verfügbar oder Konfiguration unvollständig - Bereinigung übersprungen.")
        print("MySQL Beispiel beendet.")


# --- Hauptausführung ---
if __name__ == "__main__":
    #sqlite_example()

    # --- MySQL Beispiel aktivieren ---
    # Ersetze 'your_password' mit deinem echten MySQL-Passwort in der mysql_example Funktion!
    # Stelle sicher, dass ein MySQL-Server unter 'localhost' läuft oder passe den Host an.
    # Der angegebene Benutzer ('root' im Beispiel) muss existieren und Rechte haben.
    mysql_example()
    # --------------------------------
    print("\n=== Alle Beispiele abgeschlossen ===")