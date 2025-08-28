
"""Utility helpers for exporting and updating databases using JSON.

This module now also provides :class:`AdvancedDBManager` which extends
``BasicDBConnector`` with Qt signals to report the state of the database
connection.  The manager emits a ``connecting`` signal before attempting to
open the connection, ``connected`` once the connection has been established and
``disconnected`` if the connection is lost or explicitly closed.  While the
connection is active a timer checks every ten seconds whether the connection is
still alive and automatically retries to reconnect if necessary.
"""

from PySide6.QtCore import QObject, QTimer, Signal

from .basic_db_connector import BasicDBConnector
from .interface import DatabaseOperations
from .interface import SQLiteInterface  # only used in the self-test example
import json


class AdvancedDBManager(BasicDBConnector):
    """Extended database manager with JSON helpers and connection signals."""

    connected = Signal()
    """Emitted when the database connection has been established."""

    disconnected = Signal()
    """Emitted when the connection has been closed or lost."""

    connecting = Signal()
    
    def __init__(self, db_operator: DatabaseOperations):
        """Initialise the manager with a concrete ``DatabaseOperations`` object.

        Parameters
        ----------
        db_operator:
            Implementation of :class:`~backend.interface.DatabaseOperations`
            providing the low level database access.    
        """
        #QObject.__init__(self)
        BasicDBConnector.__init__(self, db_operator)

        # Expose ``params`` and a simplified ``db_type`` attribute for the
        # legacy export helpers below which expect these names to be present.
        self.params = getattr(db_operator, "params", {})
        self.db_type = "mysql" if "mysql" in self.db_type_name.lower() else "sqlite"

        self._connection_timer = QTimer(self)
        self._connection_timer.setInterval(10000)
        self._connection_timer.timeout.connect(self._check_connection)

    # ------------------------------------------------------------------
    # Connection handling
    # ------------------------------------------------------------------
    def connect_to_db(self, database_override: str = None):  # type: ignore[override]
        """Connect to the database and start the health check timer.

        The ``connecting`` signal is emitted before attempting to establish the
        connection.  On success ``connected`` is emitted and a periodic check is
        started to ensure that the connection stays alive.  If the connection
        attempt fails the ``disconnected`` signal is emitted.
        """

        self.connecting.emit()
        try:
            # Note: QObject must be first in the MRO, so using super() would
            # resolve to QObject.connect here. Call the connector explicitly.
            BasicDBConnector.connect_to_db(self, database_override)
        except Exception:
            self.disconnected.emit()
            return False
        self._connection_timer.start()
        self.connected.emit()
        return True

    def disconnect_from_db(self):  # type: ignore[override]
        """Disconnect from the database and stop the health check timer."""

        self._connection_timer.stop()
        # See note in connect(): avoid super() due to QObject in MRO.
        BasicDBConnector.disconnect_from_db(self)
        self.disconnected.emit()

    # ------------------------------------------------------------------
    # Connection monitoring
    # ------------------------------------------------------------------
    def _check_connection(self) -> None:
        """Verify that the connection is still alive and reconnect if needed."""

        if self._is_connection_alive():
            return
        self._connection_timer.stop()
        # ``connect`` emits the appropriate signals
        self.connect_to_db()

    def _is_connection_alive(self) -> bool:
        """Return ``True`` if the database connection appears to be valid."""

        if not self.conn:
            return False
        try:
            # MySQL connections expose ``is_connected``
            if hasattr(self.conn, "is_connected"):
                return bool(self.conn.is_connected())
            cursor = self.conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            return True
        except Exception:
            return False
    
    def export_to_custom_json(self, output_file: str):
        """Export the entire database into a phpMyAdmin compatible JSON file."""
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
        """Load a JSON export and update the database accordingly."""
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
        """Load a JSON export, apply ``modification_func`` and save it back."""
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
    # AdvancedDBManager erwartet ein Objekt, das DatabaseOperations implementiert
    # (z. B. SQLiteInterface oder MySQLInterface), nicht String-Parameter.
    manager = AdvancedDBManager(SQLiteInterface(database="example.db"))
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
