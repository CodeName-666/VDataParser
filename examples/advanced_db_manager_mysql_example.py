"""AdvancedDBManager MySQL-Beispiel.

Dieses Beispiel zeigt, wie der ``AdvancedDBManager`` mit einem MySQL-Server
verwendet wird. Es verbindet sich optional zuerst ohne Datenbank, um eine
Test-Datenbank zu erstellen (falls nicht vorhanden), stellt anschließend die
Verbindung zur Datenbank her, führt einige einfache Operationen aus und trennt
die Verbindung wieder. Die Klasse emittiert Qt-Signale für Verbindungsstatus.

Voraussetzungen:
- Paket ``mysql-connector-python`` installiert.
- Optional: ``PySide6`` (für die Signale/Timer, in diesem Repo bereits genutzt).

Konfiguration via Umgebungsvariablen (mit Standardwerten):
- ``MYSQL_HOST`` (Standard: ``localhost``)
- ``MYSQL_PORT`` (Standard: ``3306``)
- ``MYSQL_USER`` (Standard: ``test``)
- ``MYSQL_PASSWORD`` (Standard: ``exec1234``)
- ``MYSQL_DB`` (Standard: ``advanced_db_manager_demo``)
- ``ADVANCED_DB_DROP_ON_EXIT`` (``1`` zum Aufräumen/Droppen der Test-DB)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Projekt-Wurzel zum PYTHONPATH hinzufügen, damit ``src`` importierbar ist
sys.path.insert(0, Path(__file__).parent.parent.__str__())  # NOQA: E402

from src.backend.advance_db_connector import AdvancedDBManager  # NOQA: E402
from src.backend.basic_db_connector import BasicDBConnector  # NOQA: E402
from src.backend import (  # NOQA: E402
    MySQLInterface,
    DatabaseConnectionError,
    DatabaseQueryError,
    MYSQL_AVAILABLE,
)


def _read_config_from_env() -> dict:
    """Read MySQL connection parameters from environment variables.

    Returns
    -------
    dict
        Dictionary with keys ``host``, ``port``, ``user``, ``password``, ``database``.
    """

    return {
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "port": int(os.environ.get("MYSQL_PORT", "3306")),
        "user": os.environ.get("MYSQL_USER", "test"),
        "password": os.environ.get("MYSQL_PASSWORD", "exec1234"),
        "database": os.environ.get("MYSQL_DB", "advanced_db_manager_demo"),
    }


def main() -> None:
    """Run the AdvancedDBManager demo against a MySQL server."""

    if not MYSQL_AVAILABLE:
        print("MySQL-Beispiel übersprungen: mysql-connector-python nicht installiert/verfügbar.")
        return

    cfg = _read_config_from_env()
    db_name = cfg["database"]

    # 1) Datenbank auf dem Server sicherstellen (ohne DB verbinden)
    server_cfg = {k: v for k, v in cfg.items() if k != "database"}
    server_operator = MySQLInterface(**server_cfg)

    # Für Server-Operationen reicht der BasicDBConnector (kein Qt notwendig)
    server_connector = BasicDBConnector(server_operator)
    try:
        server_connector.create_database(db_name)
    except (DatabaseConnectionError, DatabaseQueryError) as e:
        print(f"Fehler beim Erstellen/Prüfen der DB '{db_name}': {e}")
        return
    finally:
        server_connector.disconnect()

    # 2) AdvancedDBManager für die konkrete Datenbank erstellen
    db_operator = MySQLInterface(**cfg)
    manager = AdvancedDBManager(db_operator)

    # Signale für Demo-Zwecke verbinden
    manager.connecting.connect(lambda: print("[Signal] Connecting…"))
    manager.connected.connect(lambda: print("[Signal] Connected."))
    manager.disconnected.connect(lambda: print("[Signal] Disconnected."))

    try:
        if not manager.connect_to_db():
            print("Verbindung konnte nicht aufgebaut werden.")
            return

        # Tabelle anlegen (id, name, alter_jahre)
        create_sql = """
            CREATE TABLE IF NOT EXISTS personen (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                alter_jahre INT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        manager.execute_query(create_sql)
        print(f"Tabelle 'personen' in '{db_name}' bereit.")

        # Einfügen
        person_id = manager.insert("personen", {"name": "Max Mustermann", "alter_jahre": 30})
        print(f"Eingefügte ID: {person_id}")

        # Auswahl
        rows = manager.select_all("personen")
        print(f"Aktuelle Einträge: {rows}")

        # Update und erneute Auswahl
        manager.update("personen", {"alter_jahre": 31}, "name = %s", ("Max Mustermann",))
        one = manager.select(
            "SELECT id, name, alter_jahre FROM personen WHERE name = %s",
            ("Max Mustermann",),
            fetch="one",
        )
        print(f"Nach Update: {one}")

        # Delete (optional)
        if person_id:
            manager.delete("personen", "id = %s", (person_id,))
            print("Eintrag wieder gelöscht.")

        # Endstand
        print(f"Endgültige Einträge: {manager.select_all('personen')}")

    except (DatabaseConnectionError, DatabaseQueryError, ValueError, TypeError) as e:
        print(f"Fehler im AdvancedDBManager-MySQL-Beispiel: {type(e).__name__}: {e}")
    finally:
        manager.disconnect_from_db()

        # Optionales Aufräumen: Test-DB droppen, falls gewünscht
        if os.environ.get("ADVANCED_DB_DROP_ON_EXIT") == "1":
            try:
                cleanup_operator = MySQLInterface(**server_cfg)
                cleanup_connector = BasicDBConnector(cleanup_operator)
                if cleanup_connector.database_exists(db_name):
                    cleanup_connector.execute_query(f"DROP DATABASE IF EXISTS `{db_name}`")
                    print(f"Test-Datenbank '{db_name}' gelöscht.")
                cleanup_connector.disconnect()
            except Exception as cleanup_error:  # noqa: BLE001 – Beispielcode
                print(f"Aufräumen fehlgeschlagen: {cleanup_error}")


if __name__ == "__main__":
    main()

