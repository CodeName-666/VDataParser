

"""MySQL implementation of :class:`DatabaseOperations`."""

from .common_interface import (
    DatabaseConnectionError,
    DatabaseQueryError,
    DatabaseOperations
    )

# --- MySQL Connector Import ---
import importlib


# --- MySQL Availability Check ---
try:
    mysql_connector_lib = importlib.import_module('mysql.connector')
    _ = mysql_connector_lib.errorcode # Check integrity
    MYSQL_AVAILABLE = True
    print("mysql-connector-python wurde erfolgreich gefunden.")
except ImportError:
    mysql_connector_lib = None
    MYSQL_AVAILABLE = False
    print("WARNUNG: mysql-connector-python nicht gefunden. MySQL-Funktionalität ist deaktiviert.")
except AttributeError:
    mysql_connector_lib = None
    MYSQL_AVAILABLE = False
    print("WARNUNG: mysql.connector Modul gefunden, aber es scheint unvollständig. MySQL-Funktionalität ist deaktiviert.")


# --- Concrete MySQL Implementation ---
class MySQLInterface(DatabaseOperations):
    """Concrete :class:`DatabaseOperations` for MySQL databases."""

    def __init__(self, **kwargs):
        """Initialise the interface and verify the ``mysql-connector`` package."""
        super().__init__(kwargs)
        if not MYSQL_AVAILABLE:
            raise ImportError(
                "MySQLInterface requires a functional 'mysql-connector-python' installation."
            )
        if not self.params.get("user"):
            # Password might be optional depending on MySQL setup
            print("WARNING: MySQL 'user' parameter not provided.")


    def get_placeholder_style(self) -> str:
        """Return the placeholder style used by MySQL."""
        return "%s"

    def get_db_specific_error_types(self) -> tuple:
        """Return the tuple of MySQL error classes."""
        return (mysql_connector_lib.Error,) if mysql_connector_lib else tuple()

    def connect_db(self, database_override: str = None):
        """Create a connection to the configured MySQL server."""
        db_to_connect = database_override or self.params.get("database")  # Can be None

        connect_args = {
            "host": self.params.get("host", "localhost"),
            "user": self.params.get("user"),
            "password": self.params.get("password"),
            "port": self.params.get("port", 3306),
            "database": db_to_connect  # Pass None if not specified
        }
        print(f"Versuche Verbindung zu MySQL ({connect_args['host']}, DB: {db_to_connect or 'Server'})...")

        try:
            conn = mysql_connector_lib.connect(**connect_args)
            if not conn.is_connected():
                 raise DatabaseConnectionError("MySQL connection failed after connect call (is_connected() is False).")
            print(f"MySQL-Verbindung {'zu ' + db_to_connect if db_to_connect else 'zum Server'} erfolgreich hergestellt.")
            return conn
        except mysql_connector_lib.Error as e:
            raise DatabaseConnectionError(f"Fehler beim Verbinden (MySQL): {e}") from e
        except Exception as e: # Catch other potential errors like TypeError if args are wrong
             raise DatabaseConnectionError(f"Unerwarteter Fehler beim MySQL Verbindungsaufbau: {e}") from e

    def disconnect_db(self, conn):
        """Close an existing MySQL connection."""
        if conn and conn.is_connected():
            try:
                conn.close()
                print("Verbindung zur MySQL-Datenbank wurde getrennt.")
            except mysql_connector_lib.Error as e:
                 print(f"Fehler beim Trennen der MySQL-Verbindung: {e}")
            except Exception as e: # Catch other potential errors
                 print(f"Unerwarteter Fehler beim Trennen der MySQL-Verbindung: {e}")


    def execute_db_query(self, conn, query: str, params: tuple = None, fetch: str = None):
        """Execute ``query`` and optionally fetch results."""
        if not conn or not conn.is_connected():
             raise DatabaseConnectionError("Keine aktive MySQL-Verbindung für Query.")

        # MySQL uses %s directly, no adaptation needed here.
        # Using the original query for execution and error messages.

        cursor = None
        is_modifying_query = False
        try:
            # buffered=True can sometimes help avoid "Unread result found" errors
            # dictionary=True returns results as dicts instead of tuples (optional change)
            cursor = conn.cursor(buffered=True)
            print(f"Executing Query (MYSQL): {query} | Params: {params}")

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            query_upper_stripped = query.strip().upper()
            is_modifying_query = not (query_upper_stripped.startswith("SELECT") or query_upper_stripped.startswith("SHOW"))

            if is_modifying_query:
                conn.commit()
                print("Änderungen committed (MySQL).")

            result_data = None
            if fetch == 'one':
                result_data = cursor.fetchone()
            elif fetch == 'all':
                result_data = cursor.fetchall()
            elif fetch == 'cursor':
                 print("WARNUNG: MYSQL-Cursor wird zurückgegeben; Schließen liegt in der Verantwortung des Aufrufers.")
                 # Don't close the cursor, return it (caller must close)
                 return cursor # EARLY RETURN
            else: # Default for INSERT/UPDATE/DELETE etc.
                 result_data = {
                    "rowcount": cursor.rowcount,
                    "lastrowid": getattr(cursor, 'lastrowid', None)
                 }
            return result_data
        except mysql_connector_lib.Error as e:
             db_error_type = f"{type(e).__name__} (MYSQL)"
             print(f"{db_error_type} bei der Ausführung der Abfrage: {e}")
             if is_modifying_query:
                 try:
                     conn.rollback()
                     print("Rollback durchgeführt wegen Fehler (MySQL).")
                 except Exception as rb_e:
                     print(f"Fehler beim Rollback nach MySQL Query-Fehler: {rb_e}")
             raise DatabaseQueryError(f"Fehler bei SQL-Ausführung ({db_error_type}): {e}\nQuery: {query}\nParams: {params}") from e
        finally:
             if cursor is not None and fetch != 'cursor': # Close only if not returned
                 try:
                     cursor.close()
                 except Exception as final_close_e:
                     print(f"Warnung: Fehler beim Schließen des MySQL Cursors im Finally-Block: {final_close_e}")


    def check_database_exists(self, db_name: str) -> bool:
        """Return ``True`` if ``db_name`` exists on the server."""
        temp_conn = None
        cursor = None
        try:
            print(f"Prüfe Existenz der MySQL DB '{db_name}'...")
            # Connect without specifying a database
            temp_conn = mysql_connector_lib.connect(
                host=self.params.get("host", "localhost"),
                user=self.params.get("user"),
                password=self.params.get("password"),
                port=self.params.get("port", 3306)
                # No 'database' argument here
            )
            cursor = temp_conn.cursor()
            query = "SHOW DATABASES LIKE %s"
            cursor.execute(query, (db_name,))
            result = cursor.fetchone()
            exists = result is not None
            print(f"MySQL-Datenbank '{db_name}' existiert: {exists}")
            return exists
        except mysql_connector_lib.Error as e:
            print(f"Fehler beim Überprüfen der MySQL-Datenbank '{db_name}': {e}")
            if hasattr(e, 'errno') and e.errno == mysql_connector_lib.errorcode.ER_ACCESS_DENIED_ERROR:
                print("Zugriff verweigert - Annahme: Existenz kann nicht bestätigt werden.")
                return False # Or re-raise depending on desired behavior
            raise DatabaseConnectionError(f"Konnte Existenz der MySQL DB '{db_name}' nicht prüfen: {e}") from e
        finally:
            if cursor:
                try: cursor.close()
                except Exception as cur_e: print(f"Warnung: Fehler beim Schließen des MySQL-Prüf-Cursors: {cur_e}")
            if temp_conn and temp_conn.is_connected():
                try: temp_conn.close()
                except Exception as conn_e: print(f"Warnung: Fehler beim Schließen der temp. MySQL-Verbindung: {conn_e}")

    def create_db(self, new_db_name: str):
        """Create ``new_db_name`` if it does not already exist."""
        # Check existence first using the method above
        if self.check_database_exists(new_db_name):
             print(f"MySQL-Datenbank '{new_db_name}' existiert bereits.")
             return

        temp_conn = None
        cursor = None
        try:
            print(f"Versuche MySQL-Datenbank '{new_db_name}' zu erstellen...")
            # Connect without DB
            temp_conn = mysql_connector_lib.connect(
                host=self.params.get("host", "localhost"),
                user=self.params.get("user"),
                password=self.params.get("password"),
                port=self.params.get("port", 3306)
            )
            cursor = temp_conn.cursor()
            # Use backticks for safety
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{new_db_name}`")
            # CREATE DATABASE might be implicitly committed, commit() is safe
            temp_conn.commit()
            print(f"MySQL-Datenbank '{new_db_name}' erfolgreich erstellt oder existierte bereits.")
        except mysql_connector_lib.Error as e:
             raise DatabaseQueryError(f"Fehler beim Erstellen der MySQL-Datenbank '{new_db_name}': {e}") from e
        finally:
            if cursor:
                try: cursor.close()
                except Exception as cur_e: print(f"Warnung: Fehler beim Schließen des MySQL-Create-Cursors: {cur_e}")
            if temp_conn and temp_conn.is_connected():
                try: temp_conn.close()
                except Exception as conn_e: print(f"Warnung: Fehler beim Schließen der temp. MySQL-Verbindung: {conn_e}")

    def list_databases(self, prefix: str | None = None) -> list[str]:
        """Return a list of databases available on the server.

        Parameters
        ----------
        prefix : str | None, optional
            Filter databases starting with this prefix.

        Returns
        -------
        list[str]
            Names of the available databases.

        Raises
        ------
        DatabaseConnectionError
            If listing the databases fails.
        """

        temp_conn = None
        cursor = None
        try:
            info = f" mit Präfix '{prefix}'" if prefix else ""
            print(f"Liste MySQL-Datenbanken{info}...")
            temp_conn = mysql_connector_lib.connect(
                host=self.params.get("host", "localhost"),
                user=self.params.get("user"),
                password=self.params.get("password"),
                port=self.params.get("port", 3306),
            )
            cursor = temp_conn.cursor()
            if prefix:
                query = "SHOW DATABASES LIKE %s"
                cursor.execute(query, (prefix + '%',))
            else:
                cursor.execute("SHOW DATABASES")
            result = cursor.fetchall()
            databases = [row[0] for row in result]
            print(f"Gefundene MySQL-Datenbanken: {databases}")
            return databases
        except mysql_connector_lib.Error as e:
            raise DatabaseConnectionError(
                f"Fehler beim Abrufen der MySQL-Datenbanken: {e}"
            ) from e
        except Exception as e:
            raise DatabaseConnectionError(
                f"Unerwarteter Fehler beim Abrufen der MySQL-Datenbanken: {e}"
            ) from e
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception as cur_e:
                    print(
                        f"Warnung: Fehler beim Schließen des MySQL-List-Cursors: {cur_e}"
                    )
            if temp_conn and temp_conn.is_connected():
                try:
                    temp_conn.close()
                except Exception as conn_e:
                    print(
                        f"Warnung: Fehler beim Schließen der temp. MySQL-Verbindung: {conn_e}"
                    )
