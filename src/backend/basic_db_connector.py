from .interface import (
    DatabaseConnectionError,
    DatabaseQueryError,
    DatabaseOperations
)

from PySide6.QtCore import QObject, QTimer, Signal

# (Code from the previous response: Imports, Exceptions, DatabaseOperations,
#  SQLiteConnector, MySQLConnector - assuming they are already defined above)

# --- Main BasicDBConnector (Continued) ---
class BasicDBConnector(QObject):
    """Generic helper that delegates all operations to a ``DatabaseOperations`` implementation."""

    def __init__(self, db_operator: DatabaseOperations | None = None):
        """Initialise the connector with a concrete ``DatabaseOperations`` instance.

        Parameters
        ----------
        db_operator : DatabaseOperations | None
            Concrete implementation used to perform DB operations. Must be an
            instance of a class implementing :class:`DatabaseOperations` (e.g.
            ``SQLiteInterface`` or ``MySQLInterface``).

        Raises
        ------
        RuntimeError
            If ``db_operator`` is omitted or ``None`` to provide a clearer
            error than a missing-argument ``TypeError``.
        TypeError
            If ``db_operator`` is not an instance of ``DatabaseOperations``.
        """

        QObject.__init__(self) # No super() to avoid MRO issues with multiple inheritance
        
        if db_operator is None:
            raise RuntimeError(
                "BasicDBConnector wurde ohne 'db_operator' initialisiert. "
                "Übergeben Sie eine Instanz einer DatabaseOperations-Implementierung, "
                "z. B. SQLiteInterface(database='pfad/zur.db') oder "
                "MySQLInterface(host='localhost', user='...', password='...')."
            )
        if not isinstance(db_operator, DatabaseOperations):
            raise TypeError(
                "db_operator muss eine Instanz einer DatabaseOperations-Implementierung sein."
            )
        self.operator = db_operator
        self.conn = None
        # Store the class name for easier logging/messaging
        self.db_type_name = type(db_operator).__name__.replace("Connector", "")


    def connect_to_db(self, database_override: str = None):
        """Connect to the database via the provided operator."""
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


    def disconnect_from_db(self):
        """Close the database connection using the operator."""
        if self.conn:
            # Delegate disconnection to the specific operator
            print(f"Trenne Verbindung via {type(self.operator).__name__}...")
            self.operator.disconnect_db(self.conn)
            self.conn = None # Set to None regardless of disconnect success/failure
        else:
            print("Keine aktive Datenbankverbindung zum Trennen vorhanden.")

    def __enter__(self):
        """Enable use as a context manager."""
        if not self.conn:
             self.connect() # connect() raises error on failure
        return self

    def __exit__(self, *_exc):
        """Leave the context manager and close the connection."""
        self.disconnect()
        return False # Propagate exceptions from the with block

    def database_exists(self, db_name: str) -> bool:
        """Check whether ``db_name`` exists via the operator."""
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



    def list_databases(self, prefix: str | None = None) -> list[str]:
        """Return databases available for this connector.

        Parameters
        ----------
        prefix : str | None, optional
            Filter databases starting with this prefix.

        Returns
        -------
        list[str]
            Names of available databases.

        Raises
        ------
        DatabaseConnectionError
            If the listing fails.
        """
        try:
            info = f" mit Präfix '{prefix}'" if prefix else ""
            print(f"Liste Datenbanken{info} via {type(self.operator).__name__}...")
            return self.operator.list_databases(prefix)
        except (DatabaseConnectionError, ImportError, ValueError) as e:
            print(f"Fehler beim Auflisten der DBs ({self.db_type_name}): {e}")
            raise
        except Exception as e:
            print(f"Unerwarteter Fehler beim Auflisten der DBs ({self.db_type_name}): {e}")
            raise DatabaseConnectionError(
                f"Unerwarteter Fehler beim Auflisten der Datenbanken ({self.db_type_name}): {e}"
            ) from e

    def create_database(self, new_db_name: str):
        """Create a new database via the operator."""
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
        """Execute an SQL query via the operator using ``%s`` placeholders."""
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
        """Insert a new record using ``%s`` placeholders."""
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
        """Update records using ``%s`` placeholders in ``where_clause``."""
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
        """Delete records using ``%s`` placeholders in ``where_clause``."""
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
        """Run a SELECT query and return the results."""
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
        """Convenience wrapper returning all rows from ``table``."""
        # Quote table name
        query = f"SELECT * FROM `{table}`"
        # Reuse the more generic select method, uses %s implicitly (as there are no params)
        return self.select(query, fetch='all')


